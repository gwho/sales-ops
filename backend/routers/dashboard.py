"""GET /api/dashboard -- session-scoped latest saved workflow results.

See docs/adr/0007-session-scoped-workflow-result-persistence.md's "Read
path" section. Absent X-Session-Id -> all three fields null (no DB query
attempted -- a brand-new visitor has nothing to look up). Malformed header
-> 400, via the same get_session_id dependency the write path uses. A
genuine database failure -> 503, distinct from the normal "nothing saved
yet" 200-all-null case.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.repositories.workflow_results import (
    DashboardLatestResults,
    WorkflowResultsRepository,
    get_workflow_results_repository,
)
from backend.session import get_session_id

router = APIRouter(prefix="/api", tags=["dashboard"])

_EMPTY_RESULTS: DashboardLatestResults = {
    "order_validation": None,
    "inventory_allocation": None,
    "payment_aging": None,
}


@router.get("/dashboard")
def get_dashboard(
    session_id: Annotated[uuid.UUID | None, Depends(get_session_id)],
    repo: Annotated[WorkflowResultsRepository, Depends(get_workflow_results_repository)],
) -> DashboardLatestResults:
    if session_id is None:
        return _EMPTY_RESULTS

    results = repo.get_latest(session_id)
    if results == "unavailable":
        raise HTTPException(
            status_code=503,
            detail="The dashboard database is temporarily unavailable. Please reload in a moment.",
        )
    return results
