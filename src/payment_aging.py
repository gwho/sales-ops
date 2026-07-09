"""Payment aging rules and aging output (Phase 5 — sales_admin_automation_toolkit_specs/03_demo_payment_aging.md).

Implements PA-001 through PA-007. None of these rules carry a version label,
so all are in scope per the Scope Gate (context/build-plan.md, CONTEXT.md).
"""

from __future__ import annotations

from datetime import date
from typing import TypedDict

import pandas as pd

from src.contracts import (
    DraftMessageRow,
    PaymentAgingRow,
    PaymentAgingSummary,
    PaymentDataIssueRow,
)
from src.excel_io import load_excel, validate_required_columns

INVOICES_REQUIRED_COLUMNS = [
    "invoice_id",
    "customer_name",
    "invoice_date",
    "due_date",
    "invoice_amount",
]

# PA-004 — aging buckets, in display order. Every key is always present in
# PaymentAgingSummary.aging_bucket_counts, even when a bucket has zero rows.
_AGING_BUCKET_ORDER = ["Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+ Days"]

# PA-005 — the "None" priority shares Paid's suggested action; the spec's
# suggested-actions table (section 7) has no distinct text for a not-yet-due,
# not-paid invoice.
_SUGGESTED_ACTION = {
    "High": "Call or email customer urgently",
    "Medium": "Send payment reminder this week",
    "Low": "Include in regular follow-up list",
    "Watch": "Monitor before due date",
    "None": "No action required",
}


class PaymentAgingResult(TypedDict):
    summary: PaymentAgingSummary
    aging_rows: list[PaymentAgingRow]
    data_issues: list[PaymentDataIssueRow]
    draft_messages: list[DraftMessageRow]


def load_invoices(file) -> pd.DataFrame:
    """Load invoices.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVOICES_REQUIRED_COLUMNS, "invoices file")
    return df


def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _to_trimmed_str(value: object) -> str:
    return str(value).strip()


def _parse_date(value: object) -> pd.Timestamp | None:
    """Return a normalized Timestamp, or None if value cannot be parsed as a date (including blank)."""
    if isinstance(value, pd.Timestamp):
        return value
    try:
        parsed = pd.to_datetime(value)
    except (ValueError, TypeError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _parse_amount(value: object) -> float | None:
    """Return a float amount, or None if the value is blank, non-numeric, or a bool."""
    if _is_blank(value) or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def _build_data_issue(
    invoice_id_value: object, customer_name_value: object, error_code: str, error_message: str
) -> PaymentDataIssueRow:
    issue: PaymentDataIssueRow = {
        "error_code": error_code,
        "error_message": error_message,
        "severity": "Error",
    }
    if not _is_blank(invoice_id_value):
        issue["invoice_id"] = _to_trimmed_str(invoice_id_value)
    if not _is_blank(customer_name_value):
        issue["customer_name"] = _to_trimmed_str(customer_name_value)
    return issue


def _aging_bucket(days_overdue: int) -> str:
    """PA-004 — aging bucket from a signed days_overdue value."""
    if days_overdue <= 0:
        return "Current"
    if days_overdue <= 30:
        return "1-30 Days"
    if days_overdue <= 60:
        return "31-60 Days"
    if days_overdue <= 90:
        return "61-90 Days"
    return "90+ Days"


def _follow_up_priority(outstanding_amount: float, days_overdue: int) -> str:
    """PA-005 — evaluated in order: Paid, then High (can override bucket), Medium, Low, Watch, None."""
    if outstanding_amount <= 0:
        return "None"
    if days_overdue > 60 or outstanding_amount >= 50000:
        return "High"
    if 31 <= days_overdue <= 60:
        return "Medium"
    if 1 <= days_overdue <= 30:
        return "Low"
    if -7 <= days_overdue <= 0:
        return "Watch"
    return "None"


def _format_amount(amount: float, currency_value: object) -> str:
    if not _is_blank(currency_value):
        return f"{_to_trimmed_str(currency_value)} {amount:,.2f}"
    return f"{amount:,.2f}"


def _build_draft_message(
    invoice_id: str, customer_name: str, outstanding_amount: float, days_overdue: int, currency_value: object
) -> DraftMessageRow:
    formatted_amount = _format_amount(outstanding_amount, currency_value)
    message_text = (
        f"Dear {customer_name},\n\n"
        f"Hope you are well. We would like to follow up on invoice {invoice_id}, "
        f"with an outstanding amount of {formatted_amount}, which is currently "
        f"{days_overdue} days overdue.\n\n"
        "Please let us know the expected payment status or if any further information "
        "is required from our side.\n\nThank you."
    )
    return {
        "invoice_id": invoice_id,
        "customer_name": customer_name,
        "outstanding_amount": outstanding_amount,
        "days_overdue": days_overdue,
        "message_text": message_text,
    }


def _build_summary(total_invoices: int, aging_rows: list[PaymentAgingRow]) -> PaymentAgingSummary:
    aging_bucket_counts = {bucket: 0 for bucket in _AGING_BUCKET_ORDER}
    total_outstanding_amount = 0.0
    overdue_amount = 0.0
    high_priority_count = 0

    for row in aging_rows:
        aging_bucket_counts[row["aging_bucket"]] += 1
        total_outstanding_amount += row["outstanding_amount"]
        if row["days_overdue"] > 0:
            overdue_amount += row["outstanding_amount"]
        if row["follow_up_priority"] == "High":
            high_priority_count += 1

    return {
        "total_invoices": total_invoices,
        "total_outstanding_amount": total_outstanding_amount,
        "overdue_amount": overdue_amount,
        "high_priority_count": high_priority_count,
        "aging_bucket_counts": aging_bucket_counts,
    }


def calculate_payment_aging(invoices_df: pd.DataFrame, as_of_date: date | None = None) -> PaymentAgingResult:
    """Compute aging, data issues, and draft reminders for every invoice row."""
    effective_date = as_of_date or date.today()

    aging_rows: list[PaymentAgingRow] = []
    data_issues: list[PaymentDataIssueRow] = []
    draft_messages: list[DraftMessageRow] = []

    for _, row in invoices_df.iterrows():
        invoice_id_value = row.get("invoice_id")
        customer_name_value = row.get("customer_name")

        due_date_parsed = _parse_date(row.get("due_date"))
        invoice_amount = _parse_amount(row.get("invoice_amount"))

        # PA-006 / PA-007 — evaluated independently; a row can have both issues.
        row_issues: list[PaymentDataIssueRow] = []
        if due_date_parsed is None:
            row_issues.append(
                _build_data_issue(invoice_id_value, customer_name_value, "PA-006", "Due date is missing.")
            )
        if invoice_amount is None or invoice_amount < 0:
            row_issues.append(
                _build_data_issue(
                    invoice_id_value, customer_name_value, "PA-007", "Invoice amount is missing or invalid."
                )
            )

        if row_issues:
            data_issues.extend(row_issues)
            continue

        invoice_id = _to_trimmed_str(invoice_id_value) if not _is_blank(invoice_id_value) else ""
        customer_name = _to_trimmed_str(customer_name_value) if not _is_blank(customer_name_value) else ""
        invoice_date_parsed = _parse_date(row.get("invoice_date"))

        # PA-001 — paid_amount is optional; missing/non-numeric/negative all default to 0.
        paid_amount_parsed = _parse_amount(row.get("paid_amount"))
        paid_amount = paid_amount_parsed if paid_amount_parsed is not None and paid_amount_parsed >= 0 else 0.0

        # PA-001/PA-002 — outstanding amount can't be sensibly negative; overpayment clamps to 0.
        outstanding_amount = max(invoice_amount - paid_amount, 0.0)
        # PA-003 — signed day count; positive when overdue, negative when due in the future.
        days_overdue = (effective_date - due_date_parsed.date()).days

        aging_bucket = _aging_bucket(days_overdue)
        follow_up_priority = _follow_up_priority(outstanding_amount, days_overdue)
        suggested_action = _SUGGESTED_ACTION[follow_up_priority]

        aging_row: PaymentAgingRow = {
            "invoice_id": invoice_id,
            "customer_name": customer_name,
            "invoice_date": invoice_date_parsed.date().isoformat() if invoice_date_parsed is not None else "",
            "due_date": due_date_parsed.date().isoformat(),
            "invoice_amount": invoice_amount,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding_amount,
            "days_overdue": days_overdue,
            "aging_bucket": aging_bucket,
            "follow_up_priority": follow_up_priority,
            "suggested_action": suggested_action,
        }
        aging_rows.append(aging_row)

        # Draft reminders only for invoices that are actually overdue with an active follow-up.
        if outstanding_amount > 0 and days_overdue > 0 and follow_up_priority in ("High", "Medium", "Low"):
            draft_messages.append(
                _build_draft_message(
                    invoice_id, customer_name, outstanding_amount, days_overdue, row.get("currency")
                )
            )

    summary = _build_summary(len(invoices_df), aging_rows)

    return {
        "summary": summary,
        "aging_rows": aging_rows,
        "data_issues": data_issues,
        "draft_messages": draft_messages,
    }
