"""POST /api/payments/aging, POST /api/payments/aging/report.

`as_of_date` is a required form field -- the live UI always sends an explicit
value (CONTEXT.md's As-of Date decision); the Python function's own
`as_of_date=None` fallback stays for direct/test callers only. Stateless per
docs/adr/0006.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from backend.uploads import read_xlsx_upload
from src.payment_aging import PaymentAgingResult, calculate_payment_aging, load_invoices
from src.report_export import export_payment_aging_report

router = APIRouter(prefix="/api/payments", tags=["payments"])

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


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
    invoices_file: Annotated[UploadFile, File()],
    as_of_date: Annotated[str, Form()],
) -> PaymentAgingResult:
    invoices_df = read_xlsx_upload(invoices_file, "invoices file", load_invoices)
    parsed_date = _parse_as_of_date(as_of_date)
    return calculate_payment_aging(invoices_df, as_of_date=parsed_date)


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
