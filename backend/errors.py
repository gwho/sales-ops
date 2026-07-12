"""Shared FastAPI exception handlers.

Keeps every failure response in the uniform {"detail": "<business-readable
message>"} shape (CONTEXT.md's Business Error, docs/adr/0006). HTTPExceptions
raised elsewhere (backend/uploads.py, the routers) already produce this shape
via FastAPI's default handler -- the two handlers registered here cover the
two cases that would otherwise break the contract: FastAPI's own list-shaped
validation errors, and truly unexpected exceptions that must never leak a
traceback to the client.
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

_VALIDATION_MESSAGE = (
    "Please upload the required files and complete the required fields before submitting."
)
_GENERIC_MESSAGE = "Something went wrong processing this request. Please try again."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": _VALIDATION_MESSAGE},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": _GENERIC_MESSAGE},
        )
