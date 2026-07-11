"""POST /api/orders/validate, POST /api/orders/validate/report.

Stateless per docs/adr/0006: each request re-parses uploaded files and calls
the tested `validate_orders` module directly; nothing is retained server-side
after the response.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, Response, UploadFile

from backend.uploads import read_xlsx_upload
from src.order_validation import (
    OrderValidationResult,
    load_orders,
    load_product_master,
    validate_orders,
)
from src.report_export import export_order_validation_report

router = APIRouter(prefix="/api/orders", tags=["orders"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/validate")
def validate_orders_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
) -> OrderValidationResult:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    return validate_orders(orders_df, product_master_df)


@router.post("/validate/report")
def validate_orders_report_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
) -> Response:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    result = validate_orders(orders_df, product_master_df)
    workbook_bytes, manifest = export_order_validation_report(
        result, original_orders_df=orders_df, generated_at=datetime.now()
    )
    return Response(
        content=workbook_bytes,
        media_type=_XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{manifest["file_name"]}"',
            "X-Report-Id": manifest["report_id"],
            "X-Generated-At": manifest["generated_at"],
        },
    )
