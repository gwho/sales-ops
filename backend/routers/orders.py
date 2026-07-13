"""POST /api/orders/validate, POST /api/orders/validate/report.

Stateless per docs/adr/0006: each request re-parses uploaded files and calls
the tested `validate_orders` module directly; nothing is retained server-side
after the response, except a best-effort Saved Workflow Result on
POST /validate when a valid X-Session-Id is supplied -- see
docs/adr/0007-session-scoped-workflow-result-persistence.md. Report export
stays entirely unaffected by ADR 0007 and never persists.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, File, Response, UploadFile

from backend.persistence import persist_workflow_result
from backend.repositories.workflow_results import (
    WorkflowResultsRepository,
    get_workflow_results_repository,
)
from backend.session import get_session_id
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
_WORKFLOW_TYPE = "order_validation"


def _load_and_validate(
    orders_file: UploadFile, product_master_file: UploadFile
) -> tuple[OrderValidationResult, pd.DataFrame]:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    return validate_orders(orders_df, product_master_df), orders_df


@router.post("/validate")
def validate_orders_endpoint(
    response: Response,
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
    session_id: Annotated[uuid.UUID | None, Depends(get_session_id)],
    repo: Annotated[WorkflowResultsRepository, Depends(get_workflow_results_repository)],
) -> OrderValidationResult:
    result, _orders_df = _load_and_validate(orders_file, product_master_file)
    persist_workflow_result(response, repo, session_id, _WORKFLOW_TYPE, result)
    return result


@router.post("/validate/report")
def validate_orders_report_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
) -> Response:
    result, orders_df = _load_and_validate(orders_file, product_master_file)
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
