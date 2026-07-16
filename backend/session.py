"""FastAPI dependency for parsing the X-Session-Id header.

See docs/adr/0007-session-scoped-workflow-result-persistence.md's "Session
identity" section. This is the single place X-Session-Id is parsed --
both the write-path workflow endpoints and GET /api/dashboard depend on it,
so "malformed" means exactly one thing everywhere.
"""

from __future__ import annotations

import uuid

from fastapi import Header, HTTPException


def get_session_id(x_session_id: str | None = Header(default=None)) -> uuid.UUID | None:
    """Returns None if the header is absent (standalone API use).

    Raises 400 if present but not a parseable UUID -- including an empty
    string, which the frontend must never send (it should omit the header
    entirely instead). Accepts any RFC4122 UUID version, not narrowed to
    v4, so this isn't brittle to exactly how the frontend generates it.

    Always returns the parsed uuid.UUID object, never the raw string --
    every query binds this object directly, so normalization happens once
    here and Postgres's native UUID column type canonicalizes again.
    """
    if x_session_id is None:
        return None
    try:
        return uuid.UUID(x_session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400, detail="Malformed X-Session-Id header."
        ) from exc
