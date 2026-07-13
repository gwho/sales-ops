"""FastAPI app entrypoint (Phase 10, extended in Phase 12).

Thin orchestration over the tested Python business modules -- see
docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md for the
stateless architecture this API follows, and
docs/adr/0007-session-scoped-workflow-result-persistence.md for the
best-effort Postgres persistence layered on top of it. See
context/library-docs.md's "Future FastAPI" section for the full endpoint
list and conventions.

Run: uv run fastapi dev backend/main.py
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import close_pool, open_pool
from backend.errors import register_exception_handlers
from backend.routers import dashboard, health, inventory, orders, payments, templates

_DEFAULT_CORS_ORIGINS = "http://localhost:3000"


def _cors_origins() -> list[str]:
    """CORS_ALLOWED_ORIGINS, comma-separated, trimmed, empty entries dropped --
    so a trailing comma or stray whitespace in the env value never produces a
    blank/invalid origin."""
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", _DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # open_pool() migrates then opens the pool, or returns None (persistence
    # disabled) if DATABASE_URL is unset -- see backend/db.py and ADR 0007.
    app.state.db_pool = open_pool()
    try:
        yield
    finally:
        close_pool(app.state.db_pool)


app = FastAPI(title="Sales Admin Automation Toolkit API", lifespan=lifespan)
# Safe default so app.state.db_pool always exists even for a TestClient(app)
# instance that's never entered as a context manager (this project's existing
# backend test convention) and therefore never runs the lifespan hook above --
# same "no pool configured" meaning as an unset DATABASE_URL.
app.state.db_pool = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At", "X-Persisted"],
)

register_exception_handlers(app)

app.include_router(orders.router)
app.include_router(inventory.router)
app.include_router(payments.router)
app.include_router(templates.router)
app.include_router(health.router)
app.include_router(dashboard.router)
