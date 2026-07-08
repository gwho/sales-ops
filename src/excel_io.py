"""Excel loading and required-column validation shared across business modules."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


class MissingColumnsError(Exception):
    """Business-readable error for an uploaded file missing required columns."""

    def __init__(self, file_label: str, missing_columns: list[str]) -> None:
        self.file_label = file_label
        self.missing_columns = missing_columns
        column_list = ", ".join(missing_columns)
        message = (
            f"The uploaded {file_label} is missing required columns: {column_list}. "
            "Please check the sample template."
        )
        super().__init__(message)


def load_excel(file, sheet_name: int | str = 0) -> pd.DataFrame:
    """Load an Excel file (path or file-like object) into a DataFrame."""
    return pd.read_excel(file, sheet_name=sheet_name)


def validate_required_columns(
    df: pd.DataFrame, required_columns: Iterable[str], file_label: str
) -> None:
    """Raise MissingColumnsError if any required column is absent from df."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise MissingColumnsError(file_label, missing)
