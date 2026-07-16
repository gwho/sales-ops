"""Workflow Results Store repository -- the Postgres persistence layer for
Saved Workflow Results.

See docs/adr/0007-session-scoped-workflow-result-persistence.md. Exposed as
a FastAPI dependency (get_workflow_results_repository), not called as bare
module functions, so route-orchestration tests can override it via
app.dependency_overrides instead of monkeypatching a module global.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, TypedDict

from fastapi import Request
from psycopg_pool import ConnectionPool

from src.contracts import CONTRACT_SCHEMA_VERSIONS

logger = logging.getLogger(__name__)

WorkflowType = Literal["order_validation", "inventory_allocation", "payment_aging"]

# Connection-acquire and per-statement timeouts, so a hanging DB call can
# never stall an already-successful (write path) or otherwise-completable
# (read path) response.
_ACQUIRE_TIMEOUT_SECONDS = 3.0
_STATEMENT_TIMEOUT_SQL = "SET LOCAL statement_timeout = '3000ms'"

_DEFAULT_TTL_DAYS = 30


class DashboardLatestResults(TypedDict):
    order_validation: dict | None
    inventory_allocation: dict | None
    payment_aging: dict | None


def _ttl() -> timedelta:
    # Read at call-time, not import-time, so tests can override via env.
    days = int(os.environ.get("WORKFLOW_RESULT_TTL_DAYS", str(_DEFAULT_TTL_DAYS)))
    return timedelta(days=days)


def _is_usable(workflow_type: str, schema_version: int, saved_at: datetime) -> bool:
    """One shared predicate for both staleness reasons (see ADR 0007's Read
    path) -- a row failing either check is indistinguishable from a missing
    row to the caller."""
    if schema_version != CONTRACT_SCHEMA_VERSIONS[workflow_type]:
        return False
    if datetime.now(timezone.utc) - saved_at > _ttl():
        return False
    return True


class WorkflowResultsRepository:
    """Thin wrapper around a (possibly None) connection pool.

    A None pool means DATABASE_URL was unset at startup -- persistence is
    intentionally disabled for this run, not an error (see backend/db.py).
    """

    def __init__(self, pool: ConnectionPool | None) -> None:
        self._pool = pool

    def save(
        self,
        session_id: uuid.UUID,
        workflow_type: WorkflowType,
        result: dict,
        schema_version: int,
    ) -> bool:
        """Best-effort save. Never raises -- returns False on any failure
        (missing pool, connection issue, non-finite JSON values, etc.) so
        the caller can report X-Persisted: false without failing the
        request that already computed a valid result."""
        if self._pool is None:
            return False

        try:
            payload = json.dumps(result, allow_nan=False)
        except ValueError:
            logger.exception(
                "Result for session %s / %s contains non-finite values "
                "(NaN/Infinity) -- refusing to persist.",
                session_id,
                workflow_type,
            )
            return False

        try:
            with self._pool.connection(timeout=_ACQUIRE_TIMEOUT_SECONDS) as conn:
                with conn.cursor() as cur:
                    cur.execute(_STATEMENT_TIMEOUT_SQL)
                    cur.execute(
                        """
                        INSERT INTO workflow_results
                            (session_id, workflow_type, result, result_schema_version, saved_at)
                        VALUES (%s, %s, %s::jsonb, %s, now())
                        ON CONFLICT (session_id, workflow_type) DO UPDATE
                        SET result = EXCLUDED.result,
                            result_schema_version = EXCLUDED.result_schema_version,
                            saved_at = now()
                        """,
                        (str(session_id), workflow_type, payload, schema_version),
                    )
            return True
        except Exception:
            logger.exception(
                "Failed to save workflow result for session %s / %s",
                session_id,
                workflow_type,
            )
            return False

    def get_latest(
        self, session_id: uuid.UUID
    ) -> DashboardLatestResults | Literal["unavailable"]:
        """Fetches at most 3 rows for this session and applies the shared
        usability predicate in Python (see module docstring / ADR 0007) --
        never a SQL WHERE on schema version or TTL, since the current
        schema version is Python-side data.

        Returns the sentinel "unavailable" -- distinct from a normal
        all-null envelope -- only when the query genuinely fails (a real
        outage), so the router can tell "nothing saved yet" (200) apart
        from "the database is down" (503). A None pool (DATABASE_URL
        unset) is the former, not the latter."""
        envelope: DashboardLatestResults = {
            "order_validation": None,
            "inventory_allocation": None,
            "payment_aging": None,
        }
        if self._pool is None:
            return envelope

        try:
            with self._pool.connection(timeout=_ACQUIRE_TIMEOUT_SECONDS) as conn:
                with conn.cursor() as cur:
                    cur.execute(_STATEMENT_TIMEOUT_SQL)
                    cur.execute(
                        """
                        SELECT workflow_type, result, result_schema_version, saved_at
                        FROM workflow_results
                        WHERE session_id = %s
                        """,
                        (str(session_id),),
                    )
                    rows = cur.fetchall()
        except Exception:
            logger.exception("Failed to read workflow results for session %s", session_id)
            return "unavailable"

        for workflow_type, result, schema_version, saved_at in rows:
            if _is_usable(workflow_type, schema_version, saved_at):
                envelope[workflow_type] = result
        return envelope


def get_workflow_results_repository(request: Request) -> WorkflowResultsRepository:
    return WorkflowResultsRepository(request.app.state.db_pool)
