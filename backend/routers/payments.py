"""POST /api/payments/aging, POST /api/payments/aging/report.

`as_of_date` is a required form field -- the live UI always sends an explicit
value (CONTEXT.md's As-of Date decision); the Python function's own
`as_of_date=None` fallback stays for direct/test callers only. Stateless per
docs/adr/0006, except a best-effort Saved Workflow Result on POST /aging
when a valid X-Session-Id is supplied -- see
docs/adr/0007-session-scoped-workflow-result-persistence.md. Note the saved
result is a snapshot as of the caller's chosen `as_of_date`, not "today" --
its aging buckets do not advance as real time passes.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile

from backend.persistence import persist_workflow_result
from backend.repositories.workflow_results import (
    WorkflowResultsRepository,
    get_workflow_results_repository,
)
from backend.session import get_session_id
from backend.uploads import read_xlsx_upload
from src.payment_aging import PaymentAgingResult, calculate_payment_aging, load_invoices
from src.report_export import export_payment_aging_report

router = APIRouter(prefix="/api/payments", tags=["payments"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
_WORKFLOW_TYPE = "payment_aging"


def _parse_as_of_date(as_of_date: str) -> date:
    try:
        return date.fromisoformat(as_of_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid as-of date (YYYY-MM-DD) and try again.",
        ) from exc


@router.post("/aging")
def calculate_payment_aging_endpoint(
    response: Response,
    invoices_file: Annotated[UploadFile, File()],
    as_of_date: Annotated[str, Form()],
    session_id: Annotated[uuid.UUID | None, Depends(get_session_id)],
    repo: Annotated[WorkflowResultsRepository, Depends(get_workflow_results_repository)],
) -> PaymentAgingResult:
    invoices_df = read_xlsx_upload(invoices_file, "invoices file", load_invoices)
    parsed_date = _parse_as_of_date(as_of_date)
    result = calculate_payment_aging(invoices_df, as_of_date=parsed_date)
    persist_workflow_result(response, repo, session_id, _WORKFLOW_TYPE, result)
    return result


@router.post("/aging/report")
def calculate_payment_aging_report_endpoint(
    invoices_file: Annotated[UploadFile, File()],
    as_of_date: Annotated[str, Form()],
) -> Response:
    invoices_df = read_xlsx_upload(invoices_file, "invoices file", load_invoices)
    parsed_date = _parse_as_of_date(as_of_date)
    result = calculate_payment_aging(invoices_df, as_of_date=parsed_date)
    workbook_bytes, manifest = export_payment_aging_report(result, generated_at=datetime.now())
    return Response(
        content=workbook_bytes,
        media_type=_XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{manifest["file_name"]}"',
            "X-Report-Id": manifest["report_id"],
            "X-Generated-At": manifest["generated_at"],
        },
    )
