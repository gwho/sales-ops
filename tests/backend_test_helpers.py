"""Shared fixtures for backend/ FastAPI tests -- not a test file itself (no test_ prefix)."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"
XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def upload_file(filename: str, fh: BinaryIO) -> tuple[str, BinaryIO, str]:
    """Shape a real sample_data/*.xlsx file for TestClient's `files=` multipart param."""
    return (filename, fh, XLSX_MEDIA_TYPE)
