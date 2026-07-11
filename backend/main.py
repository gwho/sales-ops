"""FastAPI app entrypoint (Phase 10).

Thin orchestration over the tested Python business modules -- see
docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md for the
stateless architecture this API follows, and context/library-docs.md's
"Future FastAPI" section for the full endpoint list and conventions.

Run: uv run fastapi dev backend/main.py
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.errors import register_exception_handlers
from backend.routers import inventory, orders, payments, templates

app = FastAPI(title="Sales Admin Automation Toolkit API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At"],
)

register_exception_handlers(app)

app.include_router(orders.router)
app.include_router(inventory.router)
app.include_router(payments.router)
app.include_router(templates.router)
