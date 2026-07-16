"""Repository/SQL integration tests against the real Neon `test` branch.

Marked @pytest.mark.db per test -- skipped (not failed) when
TEST_DATABASE_URL is unset, so `uv run pytest` stays fully hermetic on a
fresh clone. Never targets `dev` or `main`: TEST_DATABASE_URL is a separate
env var from DATABASE_URL specifically so a misconfigured environment can't
point this at either by accident. See
docs/adr/0007-session-scoped-workflow-result-persistence.md.

Isolation: each test uses a freshly generated session_id (so tests can
never collide with each other) and deletes its own rows in a `finally`
block, rather than wrapping calls in a transaction that's rolled back.
WorkflowResultsRepository.save()/get_latest() each borrow a pool
connection per call and commit on clean exit (by design -- a real save
must actually persist), so there's no single externally-wrappable
transaction around a repository call the way there would be around raw
SQL. The migration/advisory-lock test below manages its own transaction
directly and doesn't need this cleanup pattern.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone

import psycopg
import pytest

import backend.db as db_module
from backend.db import close_pool, open_pool, run_migrations
from backend.repositories.workflow_results import WorkflowResultsRepository
from src.contracts import CONTRACT_SCHEMA_VERSIONS


def _test_database_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set -- skipping Neon-backed repository tests.")
    return url


@pytest.fixture
def pool(monkeypatch: pytest.MonkeyPatch):
    url = _test_database_url()
    # Reuse the real migration/pool-open path against the test branch --
    # exercises the actual startup code, not a parallel test-only path.
    monkeypatch.setenv("DATABASE_URL", url)
    opened = open_pool()
    assert opened is not None
    yield opened
    close_pool(opened)


@pytest.fixture
def repo(pool):
    return WorkflowResultsRepository(pool)


def _cleanup(pool, session_id: uuid.UUID) -> None:
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM workflow_results WHERE session_id = %s", (str(session_id),))


@pytest.mark.db
def test_save_then_get_latest_round_trips(pool, repo):
    session_id = uuid.uuid4()
    try:
        result = {"summary": {"total_orders": 5}, "valid_orders": [], "errors": []}
        assert (
            repo.save(session_id, "order_validation", result, CONTRACT_SCHEMA_VERSIONS["order_validation"])
            is True
        )

        envelope = repo.get_latest(session_id)
        assert envelope["order_validation"] == result
        assert envelope["inventory_allocation"] is None
        assert envelope["payment_aging"] is None
    finally:
        _cleanup(pool, session_id)


@pytest.mark.db
def test_upsert_latest_wins_and_advances_saved_at(pool, repo):
    session_id = uuid.uuid4()
    try:
        repo.save(
            session_id,
            "payment_aging",
            {"summary": {"total_invoices": 1}},
            CONTRACT_SCHEMA_VERSIONS["payment_aging"],
        )
        with pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT saved_at FROM workflow_results WHERE session_id = %s AND workflow_type = %s",
                (str(session_id), "payment_aging"),
            )
            (first_saved_at,) = cur.fetchone()

        repo.save(
            session_id,
            "payment_aging",
            {"summary": {"total_invoices": 99}},
            CONTRACT_SCHEMA_VERSIONS["payment_aging"],
        )
        envelope = repo.get_latest(session_id)
        assert envelope["payment_aging"]["summary"]["total_invoices"] == 99

        with pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT saved_at FROM workflow_results WHERE session_id = %s AND workflow_type = %s",
                (str(session_id), "payment_aging"),
            )
            rows = cur.fetchall()
            assert len(rows) == 1  # upsert, not a second row
            assert rows[0][0] > first_saved_at  # saved_at advanced on the update branch
    finally:
        _cleanup(pool, session_id)


@pytest.mark.db
def test_json_nan_guard_fails_save_not_silently(pool, repo):
    session_id = uuid.uuid4()
    try:
        result = {"summary": {"total_orders": float("nan")}}
        saved = repo.save(
            session_id, "order_validation", result, CONTRACT_SCHEMA_VERSIONS["order_validation"]
        )
        assert saved is False

        envelope = repo.get_latest(session_id)
        assert envelope["order_validation"] is None
    finally:
        _cleanup(pool, session_id)


@pytest.mark.db
def test_result_schema_version_mismatch_resolves_to_null(pool, repo):
    session_id = uuid.uuid4()
    try:
        repo.save(session_id, "inventory_allocation", {"summary": {}}, 999)
        envelope = repo.get_latest(session_id)
        assert envelope["inventory_allocation"] is None
    finally:
        _cleanup(pool, session_id)


@pytest.mark.db
def test_ttl_expired_result_resolves_to_null(pool, repo):
    session_id = uuid.uuid4()
    try:
        repo.save(session_id, "payment_aging", {"summary": {}}, CONTRACT_SCHEMA_VERSIONS["payment_aging"])
        # Force the row's saved_at into the past directly via SQL -- there's
        # no public API for backdating a save; this is the one place a test
        # reaches past the repository's own interface.
        with pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE workflow_results SET saved_at = %s WHERE session_id = %s AND workflow_type = %s",
                (datetime.now(timezone.utc) - timedelta(days=31), str(session_id), "payment_aging"),
            )

        envelope = repo.get_latest(session_id)
        assert envelope["payment_aging"] is None
    finally:
        _cleanup(pool, session_id)


def test_missing_pool_returns_false_and_empty_envelope():
    """No DB required -- runs on every clone, not just when TEST_DATABASE_URL is set."""
    repo = WorkflowResultsRepository(pool=None)
    session_id = uuid.uuid4()
    assert repo.save(session_id, "order_validation", {"summary": {}}, 1) is False
    assert repo.get_latest(session_id) == {
        "order_validation": None,
        "inventory_allocation": None,
        "payment_aging": None,
    }


# --- Migration runner ---------------------------------------------------


@pytest.mark.db
def test_migrations_are_idempotent(pool):
    # `pool` fixture already applied migrations once via open_pool(); running
    # again against the same database should be a no-op, not an error.
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        run_migrations(conn)


@pytest.mark.db
def test_migration_checksum_mismatch_fails_startup(pool, tmp_path, monkeypatch: pytest.MonkeyPatch):
    # `pool` fixture already recorded a legitimate schema_migrations entry
    # for 0001_create_workflow_results. Point the runner at a tampered file
    # under the same version name and confirm it refuses to proceed.
    fake_dir = tmp_path / "migrations"
    fake_dir.mkdir()
    (fake_dir / "0001_create_workflow_results.sql").write_text("-- tampered\n")
    monkeypatch.setattr(db_module, "MIGRATIONS_DIR", fake_dir)

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with pytest.raises(RuntimeError, match="checksum mismatch"):
            run_migrations(conn)
