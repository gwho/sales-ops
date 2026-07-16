"""POST /api/inventory/allocate, POST /api/inventory/allocate/report.

Runs the full chain internally -- orders + product master through
`validate_orders` first, then the resulting valid orders through
`allocate_inventory` with the inventory file -- because `allocate_inventory`
requires already-valid orders, and that's what the UI workflow means by
"allocate." Stateless per docs/adr/0006, except a best-effort Saved Workflow
Result on POST /allocate when a valid X-Session-Id is supplied -- see
docs/adr/0007-session-scoped-workflow-result-persistence.md. Only the
inventory_allocation result is persisted, never the internal validation
byproduct (ADR 0007's "Write path" section) -- the caller never invoked or
even received an order-validation workflow in this request.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile

from backend.persistence import persist_workflow_result
from backend.repositories.workflow_results import (
    WorkflowResultsRepository,
    get_workflow_results_repository,
)
from backend.session import get_session_id
from backend.uploads import read_xlsx_upload
from src.excel_io import MissingColumnsError
from src.inventory_allocation import (
    InvalidInventoryDataError,
    InvalidOrderDataError,
    InventoryAllocationResult,
    allocate_inventory,
    load_inventory,
)
from src.order_validation import load_orders, load_product_master, validate_orders
from src.report_export import export_inventory_allocation_report

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_WORKFLOW_TYPE = "inventory_allocation"


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
    try:
        return allocate_inventory(valid_orders_df, inventory_df)
    except (MissingColumnsError, InvalidOrderDataError, InvalidInventoryDataError) as exc:
        # Zero valid orders (or otherwise malformed valid-order/inventory data)
        # is a business/input failure, not a server failure -- allocate_inventory
        # raises these for exactly that reason, so they map to 400, not the
        # generic 500 an uncaught exception would produce.
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/allocate")
def allocate_inventory_endpoint(
    response: Response,
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
    inventory_file: Annotated[UploadFile, File()],
    session_id: Annotated[uuid.UUID | None, Depends(get_session_id)],
    repo: Annotated[WorkflowResultsRepository, Depends(get_workflow_results_repository)],
) -> InventoryAllocationResult:
    result = _run_allocation(orders_file, product_master_file, inventory_file)
    persist_workflow_result(response, repo, session_id, _WORKFLOW_TYPE, result)
    return result


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
