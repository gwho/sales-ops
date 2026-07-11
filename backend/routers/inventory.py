"""POST /api/inventory/allocate, POST /api/inventory/allocate/report.

Runs the full chain internally -- orders + product master through
`validate_orders` first, then the resulting valid orders through
`allocate_inventory` with the inventory file -- because `allocate_inventory`
requires already-valid orders, and that's what the UI workflow means by
"allocate." Stateless per docs/adr/0006.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, Response, UploadFile

from backend.uploads import read_xlsx_upload
from src.inventory_allocation import InventoryAllocationResult, allocate_inventory, load_inventory
from src.order_validation import load_orders, load_product_master, validate_orders
from src.report_export import export_inventory_allocation_report

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _run_allocation(
    orders_file: UploadFile, product_master_file: UploadFile, inventory_file: UploadFile
) -> InventoryAllocationResult:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    inventory_df = read_xlsx_upload(inventory_file, "inventory file", load_inventory)

    validation_result = validate_orders(orders_df, product_master_df)
    valid_orders_df = pd.DataFrame(validation_result["valid_orders"])
    return allocate_inventory(valid_orders_df, inventory_df)


@router.post("/allocate")
def allocate_inventory_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
    inventory_file: Annotated[UploadFile, File()],
) -> InventoryAllocationResult:
    return _run_allocation(orders_file, product_master_file, inventory_file)


@router.post("/allocate/report")
def allocate_inventory_report_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
    inventory_file: Annotated[UploadFile, File()],
) -> Response:
    result = _run_allocation(orders_file, product_master_file, inventory_file)
    workbook_bytes, manifest = export_inventory_allocation_report(
        result, generated_at=datetime.now()
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
