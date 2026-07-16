"""Shared write-path glue for the three workflow routers.

Sets X-Persisted per docs/adr/0007-session-scoped-workflow-result-persistence.md.
Defensively catches any repository failure so a regression in the
repository's own best-effort guarantee can never turn a successful workflow
computation into a failed request -- the route layer doesn't just trust
that guarantee, it enforces it too.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import Response

from backend.repositories.workflow_results import WorkflowResultsRepository, WorkflowType
from src.contracts import CONTRACT_SCHEMA_VERSIONS

logger = logging.getLogger(__name__)


def persist_workflow_result(
    response: Response,
    repo: WorkflowResultsRepository,
    session_id: uuid.UUID | None,
    workflow_type: WorkflowType,
    result: dict,
) -> None:
    """Sets X-Persisted on `response`.

    "skipped" if no session was supplied; "true"/"false" if one was, based
    on whether the save succeeded. Never raises -- a repository exception is
    treated the same as a returned False.
    """
    if session_id is None:
        response.headers["X-Persisted"] = "skipped"
        return

    try:
        saved = repo.save(
            session_id, workflow_type, result, CONTRACT_SCHEMA_VERSIONS[workflow_type]
        )
    except Exception:
        logger.exception(
            "Repository raised while saving %s for session %s", workflow_type, session_id
        )
        saved = False

    response.headers["X-Persisted"] = "true" if saved else "false"
