"""Postgres connection pool and migration runner for the Workflow Results Store.

See docs/adr/0007-session-scoped-workflow-result-persistence.md for the full
design. DATABASE_URL is read at call-time (inside open_pool), never captured
at import time, so tests that set/unset it via monkeypatch or a plain env
var behave predictably.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path

import psycopg
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

# Arbitrary, fixed key for this app's migration-batch advisory lock. Only
# needs to be unique enough not to collide with some other advisory lock
# usage sharing the same database, which nothing else here does.
_MIGRATION_LOCK_KEY = 725_814_001

# Bounded retry for the initial admin connection, to absorb ordinary Neon
# free-tier cold-start latency without treating it as a hard failure. Kept
# well under Render's service start/health-check timeout so a slow cold
# start reads as "still booting," not a failed deploy.
_CONNECT_RETRY_ATTEMPTS = 5
_CONNECT_RETRY_BACKOFF_SECONDS = 2.5


def _connect_with_retry(database_url: str) -> psycopg.Connection:
    """Connects with a short bounded retry.

    A database still unreachable after this window is a genuine failure --
    fail-closed startup is correct at that point (see ADR 0007's "DATABASE_URL
    set but unreachable at boot" case).
    """
    last_error: psycopg.OperationalError | None = None
    for attempt in range(1, _CONNECT_RETRY_ATTEMPTS + 1):
        try:
            return psycopg.connect(database_url)
        except psycopg.OperationalError as exc:
            last_error = exc
            if attempt < _CONNECT_RETRY_ATTEMPTS:
                logger.warning(
                    "Database connection attempt %d/%d failed, retrying: %s",
                    attempt,
                    _CONNECT_RETRY_ATTEMPTS,
                    exc,
                )
                time.sleep(_CONNECT_RETRY_BACKOFF_SECONDS)
    assert last_error is not None
    raise last_error


def _checksum(sql_text: str) -> str:
    return hashlib.sha256(sql_text.encode("utf-8")).hexdigest()


def _migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def run_migrations(conn: psycopg.Connection) -> None:
    """Applies every pending migration file in one transaction.

    schema_migrations is owned by this runner, never by a migration file --
    it is created here, not by any 00XX_*.sql file, keeping migration
    bookkeeping separate from application schema. Raises (rolling back the
    whole batch) if an already-applied file's checksum has changed, or if
    any pending file fails to apply.
    """
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(%s)", (_MIGRATION_LOCK_KEY,))
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            cur.execute("SELECT version, checksum FROM schema_migrations")
            applied = {version: checksum for version, checksum in cur.fetchall()}

            for path in _migration_files():
                version = path.stem
                sql_text = path.read_text()
                checksum = _checksum(sql_text)

                if version in applied:
                    if applied[version] != checksum:
                        raise RuntimeError(
                            f"Migration {version} has changed since it was applied "
                            "(checksum mismatch) -- refusing to continue startup."
                        )
                    continue

                cur.execute(sql_text)
                cur.execute(
                    "INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)",
                    (version, checksum),
                )
                logger.info("Applied migration %s", version)


def open_pool() -> ConnectionPool | None:
    """Runs migrations and opens the serving connection pool.

    Returns None -- skipping migrations entirely -- if DATABASE_URL is
    unset. Persistence is then intentionally disabled for this run, not
    treated as an error; this is what keeps the app (and TestClient-driven
    tests that exercise this same lifespan hook) hermetic on a fresh clone
    with zero configuration. Production must set DATABASE_URL regardless.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.info("DATABASE_URL is not set -- persistence disabled for this run.")
        return None

    admin_conn = _connect_with_retry(database_url)
    try:
        run_migrations(admin_conn)
    finally:
        admin_conn.close()

    # Deliberately small pool, appropriate for Render's free-tier service.
    return ConnectionPool(database_url, min_size=1, max_size=3, open=True)


def close_pool(pool: ConnectionPool | None) -> None:
    if pool is not None:
        pool.close()
