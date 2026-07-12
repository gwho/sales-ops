"""FastAPI app entrypoint (Phase 10).

Thin orchestration over the tested Python business modules -- see
docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md for the
stateless architecture this API follows, and context/library-docs.md's
"Future FastAPI" section for the full endpoint list and conventions.

Run: uv run fastapi dev backend/main.py
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.errors import register_exception_handlers
from backend.routers import health, inventory, orders, payments, templates

_DEFAULT_CORS_ORIGINS = "http://localhost:3000"


def _cors_origins() -> list[str]:
    """CORS_ALLOWED_ORIGINS, comma-separated, trimmed, empty entries dropped --
    so a trailing comma or stray whitespace in the env value never produces a
    blank/invalid origin."""
    raw = os.environ.get("CORS_ALLOWED_ORIGINS", _DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="Sales Admin Automation Toolkit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At"],
)

register_exception_handlers(app)

app.include_router(orders.router)
app.include_router(inventory.router)
app.include_router(payments.router)
app.include_router(templates.router)
app.include_router(health.router)
