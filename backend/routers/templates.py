"""GET /api/templates/{template_name} -- allowlisted Sample File downloads.

Serves the existing committed sample_data/*.xlsx workbooks as-is (CONTEXT.md's
Sample File term) -- no clean/minimal template generator, no raw filesystem
path access. sample_customers.xlsx is intentionally excluded: it's
reference-only and unused by any live workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Path as ApiPath
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/templates", tags=["templates"])

_SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"

TEMPLATE_FILES: dict[str, Path] = {
    "orders": _SAMPLE_DATA_DIR / "sample_orders.xlsx",
    "product-master": _SAMPLE_DATA_DIR / "sample_product_master.xlsx",
    "inventory": _SAMPLE_DATA_DIR / "sample_inventory.xlsx",
    "invoices": _SAMPLE_DATA_DIR / "sample_invoices.xlsx",
}

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/{template_name}")
def download_template(template_name: Annotated[str, ApiPath()]) -> FileResponse:
    path = TEMPLATE_FILES.get(template_name)
    if path is None:
        raise HTTPException(status_code=400, detail="The requested sample file is not available.")
    return FileResponse(path, media_type=_XLSX_MEDIA_TYPE, filename=path.name)
