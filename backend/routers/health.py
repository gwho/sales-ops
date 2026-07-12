"""GET /health -- minimal liveness check.

Deliberately no database query (Phase 11 scope). If a deployment health check
ever needs to verify the Demo Reporting Database specifically, that's a Phase
11.1 concern to add then, not now.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
