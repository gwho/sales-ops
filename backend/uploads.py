"""Shared upload validation for the FastAPI layer.

Enforces the "Uploaded File" contract (CONTEXT.md): .xlsx extension is
mandatory, content-type is advisory only (not gated), and a corrupt or
unreadable workbook is a 400, not a 500 -- it is user input failure, not
server failure. `src/excel_io.py` and the business modules stay framework-free;
this module is the only place that converts their exceptions into HTTPException.
"""

from __future__ import annotations

from typing import Callable

import pandas as pd
from fastapi import HTTPException, UploadFile

from src.excel_io import MissingColumnsError


def read_xlsx_upload(
    file: UploadFile, label: str, loader: Callable[[object], pd.DataFrame]
) -> pd.DataFrame:
    """Validate an uploaded file's type, then load it via a business module's load_* helper.

    `loader` is one of load_orders/load_product_master/load_inventory/load_invoices --
    required-column lists stay owned by their business module, not duplicated here.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400, detail=f"Please upload the required {label} and try again."
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail=f"Please upload a .xlsx Excel file for {label}.")

    try:
        return loader(file.file)
    except MissingColumnsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                f"The uploaded {label} could not be read as a valid .xlsx workbook. "
                "Please use the sample file and try again."
            ),
        ) from exc
