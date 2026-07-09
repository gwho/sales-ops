"""Tests for src/order_validation.py — every OV-001..OV-007 rule from
sales_admin_automation_toolkit_specs/01_demo_order_validation.md, plus the
edge cases resolved during the Phase 3 /architect session."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.excel_io import MissingColumnsError
from src.order_validation import load_orders, load_product_master, validate_orders


def _product_master_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"sku": "MED-LENS-001", "product_name": "Optical Lens Kit", "category": "Medical Device", "active": True},
            {"sku": "MED-GLOVE-002", "product_name": "Nitrile Exam Gloves", "category": "Medical Device", "active": True},
            {"sku": "OFF-CHAIR-006", "product_name": "Ergonomic Office Chair", "category": "Office Furniture", "active": False},
            {"sku": "OFF-DESK-007", "product_name": "Standing Desk", "category": "Office Furniture", "active": "maybe"},
        ]
    )


def _order_row(**overrides) -> dict:
    row = {
        "order_id": "SO-2026-001",
        "order_date": date(2026, 7, 1),
        "customer_name": "Bright Medical Trading Ltd",
        "customer_region": "Hong Kong",
        "sku": "MED-LENS-001",
        "product_name": "Optical Lens Kit",
        "quantity": 10,
        "requested_delivery_date": date(2026, 7, 15),
        "priority": "High",
        "payment_terms": "30 days",
        "sales_owner": "Jesse",
    }
    row.update(overrides)
    return row


def _orders_df(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows))


def _errors_by_code(result, code: str) -> list:
    return [error for error in result["errors"] if error["error_code"] == code]


# --- Spec section 12 test cases -----------------------------------------


def test_missing_customer_name_raises_ov001():
    result = validate_orders(_orders_df(_order_row(customer_name="")), _product_master_df())
    errors = _errors_by_code(result, "OV-001")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Customer name is missing."
    assert errors[0]["severity"] == "Error"
    assert result["valid_orders"] == []


def test_duplicate_order_id_flags_every_row():
    df = _orders_df(
        _order_row(order_id="SO-2026-005"),
        _order_row(order_id="SO-2026-005", customer_name="Formosa Industrial Group"),
    )
    result = validate_orders(df, _product_master_df())
    errors = _errors_by_code(result, "OV-002")
    assert {error["row_number"] for error in errors} == {2, 3}
    assert result["summary"]["duplicate_orders"] == 2
    assert result["valid_orders"] == []


def test_invalid_sku_not_in_master_raises_ov003_unknown_sku():
    result = validate_orders(_orders_df(_order_row(sku="MED-LENS-999")), _product_master_df())
    errors = _errors_by_code(result, "OV-003-UNKNOWN_SKU")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "SKU does not exist in product master."
    assert result["summary"]["invalid_skus"] == 1


def test_zero_quantity_raises_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=0)), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Quantity must be greater than zero."


def test_negative_quantity_raises_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=-3)), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Quantity must be greater than zero."


def test_delivery_before_order_raises_ov005():
    result = validate_orders(
        _orders_df(_order_row(order_date=date(2026, 7, 10), requested_delivery_date=date(2026, 7, 5))),
        _product_master_df(),
    )
    errors = _errors_by_code(result, "OV-005-DELIVERY_BEFORE_ORDER")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Requested delivery date is earlier than order date."


def test_invalid_priority_raises_ov006():
    result = validate_orders(_orders_df(_order_row(priority="Urgent")), _product_master_df())
    errors = _errors_by_code(result, "OV-006")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Priority must be High, Normal, or Low."


def test_clean_order_appears_in_valid_orders():
    result = validate_orders(_orders_df(_order_row()), _product_master_df())
    assert result["errors"] == []
    assert len(result["valid_orders"]) == 1
    assert result["valid_orders"][0]["order_id"] == "SO-2026-001"


# --- Multiple errors per row / field-level OV-001 -------------------------


def test_row_can_emit_multiple_errors_across_rules():
    result = validate_orders(
        _orders_df(_order_row(customer_name="", quantity=-1)), _product_master_df()
    )
    codes = {error["error_code"] for error in result["errors"]}
    assert "OV-001" in codes
    assert "OV-004" in codes
    assert result["valid_orders"] == []


def test_ov001_emits_one_error_per_missing_field_in_fixed_order():
    result = validate_orders(
        _orders_df(_order_row(customer_name="", priority="")), _product_master_df()
    )
    ov001_errors = _errors_by_code(result, "OV-001")
    assert [error["error_message"] for error in ov001_errors] == [
        "Customer name is missing.",
        "Priority is missing.",
    ]
    assert result["summary"]["missing_field_count"] == 2


# --- Blank-field skip rule extends to OV-002 and OV-006 --------------------


def test_blank_order_id_does_not_trigger_duplicate_check():
    df = _orders_df(_order_row(order_id=""), _order_row(order_id=""))
    result = validate_orders(df, _product_master_df())
    assert _errors_by_code(result, "OV-002") == []
    ov001_messages = [error["error_message"] for error in _errors_by_code(result, "OV-001")]
    assert ov001_messages.count("Order ID is missing.") == 2


def test_blank_priority_does_not_trigger_ov006():
    result = validate_orders(_orders_df(_order_row(priority="")), _product_master_df())
    assert _errors_by_code(result, "OV-006") == []
    ov001_errors = _errors_by_code(result, "OV-001")
    assert any(error["error_message"] == "Priority is missing." for error in ov001_errors)


# --- OV-003 SKU sub-cases ---------------------------------------------------


def test_inactive_sku_raises_ov003_inactive_sku():
    result = validate_orders(_orders_df(_order_row(sku="OFF-CHAIR-006")), _product_master_df())
    errors = _errors_by_code(result, "OV-003-INACTIVE_SKU")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "SKU exists but is marked inactive in product master."
    assert result["valid_orders"] == []


def test_invalid_active_flag_raises_ov003_invalid_active_flag():
    result = validate_orders(_orders_df(_order_row(sku="OFF-DESK-007")), _product_master_df())
    errors = _errors_by_code(result, "OV-003-INVALID_ACTIVE_FLAG")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "SKU active status is not valid in product master."


def test_active_flag_string_true_false_normalize_correctly():
    product_master = pd.DataFrame(
        [
            {"sku": "A-001", "product_name": "Widget A", "category": "Test", "active": "TRUE"},
            {"sku": "B-002", "product_name": "Widget B", "category": "Test", "active": "FALSE"},
        ]
    )
    result = validate_orders(
        _orders_df(
            _order_row(order_id="SO-2026-001", sku="A-001"),
            _order_row(order_id="SO-2026-002", sku="B-002"),
        ),
        product_master,
    )
    assert _errors_by_code(result, "OV-003-INACTIVE_SKU") == [
        error for error in result["errors"] if error["row_number"] == 3
    ]
    assert len(result["valid_orders"]) == 1


# --- OV-004 quantity type handling ------------------------------------------


def test_non_numeric_quantity_raises_ov004_whole_number_message():
    result = validate_orders(_orders_df(_order_row(quantity="ten")), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert errors[0]["error_message"] == "Quantity must be a valid whole number."


def test_whole_number_float_quantity_is_accepted():
    result = validate_orders(_orders_df(_order_row(quantity=10.0)), _product_master_df())
    assert result["errors"] == []
    assert result["valid_orders"][0]["quantity"] == 10


def test_non_whole_float_quantity_raises_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=10.5)), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert errors[0]["error_message"] == "Quantity must be a valid whole number."


def test_blank_quantity_raises_ov001_not_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=None)), _product_master_df())
    assert _errors_by_code(result, "OV-004") == []
    ov001_errors = _errors_by_code(result, "OV-001")
    assert any(error["error_message"] == "Quantity is missing." for error in ov001_errors)


# --- OV-005 date parseability ------------------------------------------------


def test_unparseable_order_date_raises_ov005_invalid_order_date():
    result = validate_orders(_orders_df(_order_row(order_date="not a date")), _product_master_df())
    errors = _errors_by_code(result, "OV-005-INVALID_ORDER_DATE")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Order date is not a valid date."


def test_unparseable_delivery_date_raises_ov005_invalid_delivery_date():
    result = validate_orders(
        _orders_df(_order_row(requested_delivery_date="not a date")), _product_master_df()
    )
    errors = _errors_by_code(result, "OV-005-INVALID_DELIVERY_DATE")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Requested delivery date is not a valid date."


# --- OV-007 payment terms warning-only, and its conflict with OV-001 -------


def test_missing_payment_terms_is_warning_only_and_row_stays_valid():
    result = validate_orders(_orders_df(_order_row(payment_terms="")), _product_master_df())
    ov007_errors = _errors_by_code(result, "OV-007")
    assert len(ov007_errors) == 1
    assert ov007_errors[0]["severity"] == "Warning"
    assert ov007_errors[0]["error_message"] == "Payment terms are missing."
    assert _errors_by_code(result, "OV-001") == []
    assert len(result["valid_orders"]) == 1
    assert result["valid_orders"][0]["payment_terms"] == ""
    assert result["summary"]["valid_orders"] == 1
    assert result["summary"]["invalid_orders"] == 0


# --- Summary counting semantics, including overlapping violations ----------


def test_invalid_orders_counts_distinct_rows_not_sum_of_categories():
    df = _orders_df(
        # one row with BOTH a duplicate order_id AND an unknown SKU
        _order_row(order_id="SO-DUP", sku="UNKNOWN-SKU"),
        _order_row(order_id="SO-DUP", customer_name="Other Customer"),
        _order_row(),  # clean row
    )
    result = validate_orders(df, _product_master_df())
    # 2 rows share order_id SO-DUP (both invalid); the unknown SKU is on one of them already
    assert result["summary"]["total_orders"] == 3
    assert result["summary"]["invalid_orders"] == 2
    assert result["summary"]["valid_orders"] == 1
    assert result["summary"]["duplicate_orders"] == 2
    assert result["summary"]["invalid_skus"] == 1


# --- row_number correctness --------------------------------------------------


def test_row_number_is_excel_visible_row_starting_at_two():
    df = _orders_df(_order_row(customer_name=""), _order_row(customer_name=""))
    result = validate_orders(df, _product_master_df())
    row_numbers = sorted({error["row_number"] for error in result["errors"]})
    assert row_numbers == [2, 3]


# --- Deterministic error ordering --------------------------------------------


def test_errors_are_ordered_by_row_then_rule_then_field():
    df = _orders_df(
        _order_row(order_id="SO-2026-100", priority="Urgent", customer_name=""),
        _order_row(order_id="SO-2026-101", quantity=0),
    )
    result = validate_orders(df, _product_master_df())
    ordered_pairs = [(error["row_number"], error["error_code"]) for error in result["errors"]]
    assert ordered_pairs == [
        (2, "OV-001"),
        (2, "OV-006"),
        (3, "OV-004"),
    ]


# --- Optional field handling: product_name fill-from-master, sales_owner ---


def test_blank_product_name_fills_from_product_master():
    result = validate_orders(_orders_df(_order_row(product_name="")), _product_master_df())
    assert result["valid_orders"][0]["product_name"] == "Optical Lens Kit"


def test_present_product_name_is_not_overridden_by_master():
    result = validate_orders(
        _orders_df(_order_row(product_name="Custom Label")), _product_master_df()
    )
    assert result["valid_orders"][0]["product_name"] == "Custom Label"


def test_blank_sales_owner_is_omitted_from_valid_order_row():
    result = validate_orders(_orders_df(_order_row(sales_owner="")), _product_master_df())
    assert "sales_owner" not in result["valid_orders"][0]


# --- Loaders: required columns vs. blank cell values ------------------------


def test_load_orders_raises_when_payment_terms_column_missing(tmp_path):
    df = _orders_df(_order_row())
    df = df.drop(columns=["payment_terms"])
    file_path = tmp_path / "orders_missing_column.xlsx"
    df.to_excel(file_path, index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        load_orders(file_path)
    assert "payment_terms" in str(exc_info.value)


def test_load_orders_succeeds_when_payment_terms_column_present_but_blank(tmp_path):
    df = _orders_df(_order_row(payment_terms=""))
    file_path = tmp_path / "orders_blank_payment_terms.xlsx"
    df.to_excel(file_path, index=False)

    loaded = load_orders(file_path)
    assert "payment_terms" in loaded.columns


def test_load_product_master_raises_when_active_column_missing(tmp_path):
    df = _product_master_df().drop(columns=["active"])
    file_path = tmp_path / "product_master_missing_column.xlsx"
    df.to_excel(file_path, index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        load_product_master(file_path)
    assert "active" in str(exc_info.value)
