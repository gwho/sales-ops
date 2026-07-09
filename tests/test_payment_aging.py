"""Tests for src/payment_aging.py — every PA-001..PA-007 rule from
sales_admin_automation_toolkit_specs/03_demo_payment_aging.md, plus the edge
cases resolved during the Phase 5 /architect session."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import pytest

from src.excel_io import MissingColumnsError
from src.payment_aging import INVOICES_REQUIRED_COLUMNS, calculate_payment_aging, load_invoices

AS_OF = date(2026, 7, 9)


def _invoice_row(**overrides) -> dict:
    row = {
        "invoice_id": "INV-2026-100",
        "customer_name": "Test Customer Ltd",
        "invoice_date": date(2026, 6, 1),
        "due_date": date(2026, 7, 1),
        "invoice_amount": 10000.0,
        "paid_amount": 0.0,
        "currency": "HKD",
        "payment_status": "Unpaid",
        "sales_owner": "Jesse",
        "remarks": "",
    }
    row.update(overrides)
    return row


def _invoices_df(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows))


def _due(days_overdue: int) -> date:
    """due_date that puts the invoice exactly `days_overdue` days overdue as of AS_OF."""
    return AS_OF - timedelta(days=days_overdue)


# --- Spec section 12 test cases -------------------------------------------


def test_fully_paid_invoice_marked_paid_no_follow_up():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=1000.0, paid_amount=1000.0, due_date=_due(20))),
        as_of_date=AS_OF,
    )
    row = result["aging_rows"][0]
    assert row["outstanding_amount"] == 0.0
    assert row["follow_up_priority"] == "None"
    assert row["suggested_action"] == "No action required"
    assert result["draft_messages"] == []


def test_missing_paid_amount_treated_as_zero():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=5000.0, paid_amount=None)), as_of_date=AS_OF
    )
    row = result["aging_rows"][0]
    assert row["paid_amount"] == 0.0
    assert row["outstanding_amount"] == 5000.0


def test_current_invoice_future_due_date_is_current_bucket():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=_due(-30))), as_of_date=AS_OF
    )
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "Current"
    assert row["follow_up_priority"] == "None"


def test_20_days_overdue_is_1_30_days_low_priority():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(20))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["days_overdue"] == 20
    assert row["aging_bucket"] == "1-30 Days"
    assert row["follow_up_priority"] == "Low"
    assert row["suggested_action"] == "Include in regular follow-up list"


def test_45_days_overdue_is_31_60_days_medium_priority():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(45))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "31-60 Days"
    assert row["follow_up_priority"] == "Medium"
    assert row["suggested_action"] == "Send payment reminder this week"


def test_75_days_overdue_is_61_90_days_but_high_priority():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(75))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "61-90 Days"
    assert row["follow_up_priority"] == "High"
    assert row["suggested_action"] == "Call or email customer urgently"


def test_100_days_overdue_is_90_plus_days_high_priority():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(100))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "90+ Days"
    assert row["follow_up_priority"] == "High"


def test_large_outstanding_amount_forces_high_priority_at_low_day_count():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=_due(5), invoice_amount=60000.0)), as_of_date=AS_OF
    )
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "1-30 Days"
    assert row["follow_up_priority"] == "High"


def test_missing_due_date_flagged_as_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_id="INV-2026-200", due_date=None)), as_of_date=AS_OF
    )
    assert result["aging_rows"] == []
    assert len(result["data_issues"]) == 1
    issue = result["data_issues"][0]
    assert issue["error_code"] == "PA-006"
    assert issue["invoice_id"] == "INV-2026-200"
    assert issue["severity"] == "Error"
    assert result["summary"]["total_invoices"] == 1


def test_negative_invoice_amount_flagged_as_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=-500.0)), as_of_date=AS_OF
    )
    assert result["aging_rows"] == []
    assert result["data_issues"][0]["error_code"] == "PA-007"


# --- Resolved edge cases ---------------------------------------------------


def test_overpayment_clamps_outstanding_to_zero():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=100.0, paid_amount=150.0, due_date=_due(20))),
        as_of_date=AS_OF,
    )
    row = result["aging_rows"][0]
    assert row["outstanding_amount"] == 0.0
    assert row["follow_up_priority"] == "None"
    assert row["suggested_action"] == "No action required"
    assert result["draft_messages"] == []


def test_non_numeric_invoice_amount_flagged_as_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount="not-a-number")), as_of_date=AS_OF
    )
    assert result["aging_rows"] == []
    assert result["data_issues"][0]["error_code"] == "PA-007"


def test_invalid_paid_amount_degrades_to_zero_no_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=1000.0, paid_amount="abc")), as_of_date=AS_OF
    )
    assert result["data_issues"] == []
    row = result["aging_rows"][0]
    assert row["paid_amount"] == 0.0
    assert row["outstanding_amount"] == 1000.0


def test_negative_paid_amount_degrades_to_zero_no_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=1000.0, paid_amount=-50.0)), as_of_date=AS_OF
    )
    assert result["data_issues"] == []
    assert result["aging_rows"][0]["paid_amount"] == 0.0


def test_row_with_missing_due_date_and_invalid_amount_produces_two_data_issues():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=None, invoice_amount=-10.0)), as_of_date=AS_OF
    )
    assert result["aging_rows"] == []
    codes = {issue["error_code"] for issue in result["data_issues"]}
    assert codes == {"PA-006", "PA-007"}
    assert len(result["data_issues"]) == 2


def test_watch_priority_due_within_seven_days():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(-5))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "Current"
    assert row["follow_up_priority"] == "Watch"
    assert row["suggested_action"] == "Monitor before due date"


def test_due_today_is_current_and_watch():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=AS_OF)), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["days_overdue"] == 0
    assert row["aging_bucket"] == "Current"
    assert row["follow_up_priority"] == "Watch"


def test_not_due_soon_is_current_and_none():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(-30))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "Current"
    assert row["follow_up_priority"] == "None"
    assert row["suggested_action"] == "No action required"


@pytest.mark.parametrize(
    "days_overdue,expected_bucket,expected_priority",
    [
        (30, "1-30 Days", "Low"),
        (31, "31-60 Days", "Medium"),
        (60, "31-60 Days", "Medium"),
        (61, "61-90 Days", "High"),
        (90, "61-90 Days", "High"),
        (91, "90+ Days", "High"),
    ],
)
def test_aging_bucket_and_priority_boundaries(days_overdue, expected_bucket, expected_priority):
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=_due(days_overdue))), as_of_date=AS_OF
    )
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == expected_bucket
    assert row["follow_up_priority"] == expected_priority


def test_aging_bucket_counts_always_has_all_five_keys():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(20))), as_of_date=AS_OF)
    assert set(result["summary"]["aging_bucket_counts"].keys()) == {
        "Current",
        "1-30 Days",
        "31-60 Days",
        "61-90 Days",
        "90+ Days",
    }
    assert result["summary"]["aging_bucket_counts"]["1-30 Days"] == 1
    assert result["summary"]["aging_bucket_counts"]["90+ Days"] == 0


def test_draft_message_generated_only_for_overdue_high_medium_low():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(invoice_id="INV-PAID", invoice_amount=100.0, paid_amount=100.0, due_date=_due(20)),
            _invoice_row(invoice_id="INV-CURRENT", due_date=_due(-30)),
            _invoice_row(invoice_id="INV-WATCH", due_date=_due(-5)),
            _invoice_row(invoice_id="INV-ISSUE", due_date=None),
            _invoice_row(invoice_id="INV-LOW", due_date=_due(20)),
        ),
        as_of_date=AS_OF,
    )
    assert len(result["draft_messages"]) == 1
    assert result["draft_messages"][0]["invoice_id"] == "INV-LOW"


def test_draft_message_currency_formatting_with_currency():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(
                invoice_id="INV-2026-777",
                customer_name="Acme Co",
                invoice_amount=12345.67,
                paid_amount=0.0,
                due_date=_due(20),
                currency="SGD",
            )
        ),
        as_of_date=AS_OF,
    )
    message = result["draft_messages"][0]["message_text"]
    assert "SGD 12,345.67" in message
    assert "Dear Acme Co," in message
    assert "invoice INV-2026-777" in message
    assert "20 days overdue" in message


def test_draft_message_currency_formatting_without_currency():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=5000.0, paid_amount=0.0, due_date=_due(10), currency=None)),
        as_of_date=AS_OF,
    )
    message = result["draft_messages"][0]["message_text"]
    assert "5,000.00" in message
    assert "$" not in message


def test_total_invoices_counts_all_rows_including_data_issues():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(invoice_id="INV-VALID", due_date=_due(10)),
            _invoice_row(invoice_id="INV-ISSUE", due_date=None),
        ),
        as_of_date=AS_OF,
    )
    assert result["summary"]["total_invoices"] == 2
    assert len(result["aging_rows"]) == 1
    assert sum(result["summary"]["aging_bucket_counts"].values()) == 1


def test_summary_aggregates_total_outstanding_overdue_and_high_priority():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(invoice_id="INV-A", invoice_amount=1000.0, paid_amount=0.0, due_date=_due(20)),
            _invoice_row(invoice_id="INV-B", invoice_amount=2000.0, paid_amount=0.0, due_date=_due(70)),
            _invoice_row(invoice_id="INV-C", invoice_amount=500.0, paid_amount=0.0, due_date=_due(-30)),
        ),
        as_of_date=AS_OF,
    )
    summary = result["summary"]
    assert summary["total_outstanding_amount"] == 3500.0
    assert summary["overdue_amount"] == 3000.0
    assert summary["high_priority_count"] == 1


def test_missing_paid_amount_column_entirely_defaults_to_zero():
    rows = [
        {
            "invoice_id": "INV-2026-300",
            "customer_name": "No Paid Column Ltd",
            "invoice_date": date(2026, 6, 1),
            "due_date": _due(20),
            "invoice_amount": 4000.0,
        }
    ]
    result = calculate_payment_aging(pd.DataFrame(rows), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["paid_amount"] == 0.0
    assert row["outstanding_amount"] == 4000.0


def test_as_of_date_defaults_to_today_when_not_provided():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=date.today())))
    assert result["aging_rows"][0]["days_overdue"] == 0


# --- Loaders: required columns --------------------------------------------


def test_load_invoices_raises_when_due_date_column_missing(tmp_path):
    df = _invoices_df(_invoice_row()).drop(columns=["due_date"])
    file_path = tmp_path / "invoices_missing_column.xlsx"
    df.to_excel(file_path, index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        load_invoices(file_path)
    assert "due_date" in str(exc_info.value)


def test_load_invoices_succeeds_when_paid_amount_column_absent(tmp_path):
    df = _invoices_df(_invoice_row()).drop(columns=["paid_amount"])
    file_path = tmp_path / "invoices_no_paid_amount.xlsx"
    df.to_excel(file_path, index=False)

    loaded = load_invoices(file_path)
    assert "paid_amount" not in loaded.columns
    assert set(INVOICES_REQUIRED_COLUMNS) <= set(loaded.columns)
