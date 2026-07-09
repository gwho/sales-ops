"""Tests for src/inventory_allocation.py — every IA-001..IA-008 rule (V1 only, no
Optional V2 region-matching) from sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md,
plus the edge cases resolved during the Phase 4 /architect session."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from src.excel_io import MissingColumnsError
from src.inventory_allocation import (
    InvalidInventoryDataError,
    allocate_inventory,
    load_inventory,
    load_valid_orders,
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
    }
    row.update(overrides)
    return row


def _orders_df(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows))


def _inventory_row(**overrides) -> dict:
    row = {
        "sku": "MED-LENS-001",
        "warehouse": "HK Warehouse",
        "available_qty": 20,
        "reserved_qty": 0,
        "reorder_point": 5,
        "supplier_name": "Vista Optics Supply",
        "lead_time_days": 18,
    }
    row.update(overrides)
    return row


def _inventory_df(*rows: dict) -> pd.DataFrame:
    return pd.DataFrame(list(rows))


def _result_by_order_id(result, order_id: str) -> dict:
    return next(r for r in result["allocation_results"] if r["order_id"] == order_id)


# --- Spec section 11 test cases ------------------------------------------


def test_enough_stock_fully_allocated():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=10)), _inventory_df(_inventory_row(available_qty=20))
    )
    row = result["allocation_results"][0]
    assert row["status"] == "Fully Allocated"
    assert row["allocated_qty"] == 10
    assert row["backorder_qty"] == 0
    assert result["remaining_inventory"][0]["remaining_qty"] == 10


def test_partial_stock_partially_allocated():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=10)), _inventory_df(_inventory_row(available_qty=6))
    )
    row = result["allocation_results"][0]
    assert row["status"] == "Partially Allocated"
    assert row["allocated_qty"] == 6
    assert row["backorder_qty"] == 4


def test_no_stock_backordered():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=10)), _inventory_df(_inventory_row(available_qty=0))
    )
    row = result["allocation_results"][0]
    assert row["status"] == "Backordered"
    assert row["allocated_qty"] == 0
    assert row["backorder_qty"] == 10
    assert row["warehouse"] == "HK Warehouse"


def test_high_priority_allocated_before_normal():
    orders = _orders_df(
        _order_row(order_id="SO-2026-002", priority="Normal", quantity=10),
        _order_row(order_id="SO-2026-001", priority="High", quantity=10),
    )
    result = allocate_inventory(orders, _inventory_df(_inventory_row(available_qty=10)))
    assert [r["order_id"] for r in result["allocation_results"]] == ["SO-2026-001", "SO-2026-002"]
    assert _result_by_order_id(result, "SO-2026-001")["status"] == "Fully Allocated"
    assert _result_by_order_id(result, "SO-2026-002")["status"] == "Backordered"


def test_earlier_delivery_date_allocated_first_within_same_priority():
    orders = _orders_df(
        _order_row(order_id="SO-2026-002", requested_delivery_date=date(2026, 7, 20), quantity=10),
        _order_row(order_id="SO-2026-001", requested_delivery_date=date(2026, 7, 10), quantity=10),
    )
    result = allocate_inventory(orders, _inventory_df(_inventory_row(available_qty=10)))
    assert [r["order_id"] for r in result["allocation_results"]] == ["SO-2026-001", "SO-2026-002"]
    assert _result_by_order_id(result, "SO-2026-001")["status"] == "Fully Allocated"
    assert _result_by_order_id(result, "SO-2026-002")["status"] == "Backordered"


def test_reserved_stock_reduces_allocatable_qty():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=20)),
        _inventory_df(_inventory_row(available_qty=20, reserved_qty=5)),
    )
    row = result["allocation_results"][0]
    assert row["allocated_qty"] == 15
    assert row["backorder_qty"] == 5
    assert row["status"] == "Partially Allocated"


def test_inventory_never_goes_negative_across_multiple_orders():
    orders = _orders_df(
        _order_row(order_id="SO-2026-001", priority="High", quantity=15),
        _order_row(
            order_id="SO-2026-002",
            priority="High",
            quantity=15,
            requested_delivery_date=date(2026, 7, 16),
        ),
    )
    result = allocate_inventory(orders, _inventory_df(_inventory_row(available_qty=20)))
    remaining = result["remaining_inventory"][0]
    assert remaining["remaining_qty"] == 0
    second = _result_by_order_id(result, "SO-2026-002")
    assert second["allocated_qty"] == 5
    assert second["backorder_qty"] == 10


def test_reorder_alert_triggers_supplier_follow_up():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=16)),
        _inventory_df(_inventory_row(available_qty=20, reorder_point=5)),
    )
    remaining = result["remaining_inventory"][0]
    assert remaining["remaining_qty"] == 4
    assert remaining["reorder_alert"] == "Yes"
    assert len(result["supplier_follow_ups"]) == 1
    follow_up = result["supplier_follow_ups"][0]
    assert follow_up["sku"] == "MED-LENS-001"
    assert follow_up["remaining_qty"] == 4
    assert follow_up["reorder_point"] == 5
    assert result["summary"]["low_stock_sku_count"] == 1


# --- IA-001 sort order edge cases ----------------------------------------


def test_sort_tie_breaks_by_order_date_then_order_id():
    orders = _orders_df(
        _order_row(order_id="SO-2026-003", order_date=date(2026, 7, 2)),
        _order_row(order_id="SO-2026-002", order_date=date(2026, 7, 1)),
        _order_row(order_id="SO-2026-001", order_date=date(2026, 7, 1)),
    )
    result = allocate_inventory(orders, _inventory_df(_inventory_row(available_qty=100)))
    assert [r["order_id"] for r in result["allocation_results"]] == [
        "SO-2026-001",
        "SO-2026-002",
        "SO-2026-003",
    ]


# --- IA-002 / IA-007 warehouse choice edge cases --------------------------


def test_missing_reserved_qty_column_defaults_to_zero():
    inventory_row = _inventory_row(available_qty=10)
    del inventory_row["reserved_qty"]
    result = allocate_inventory(_orders_df(_order_row(quantity=10)), _inventory_df(inventory_row))
    assert result["allocation_results"][0]["allocated_qty"] == 10


def test_warehouse_choice_switches_as_stock_depletes():
    orders = _orders_df(
        _order_row(order_id="SO-2026-001", quantity=15),
        _order_row(order_id="SO-2026-002", quantity=15, requested_delivery_date=date(2026, 7, 16)),
    )
    inventory = _inventory_df(
        _inventory_row(warehouse="HK Warehouse", available_qty=20),
        _inventory_row(warehouse="SG Warehouse", available_qty=10),
    )
    result = allocate_inventory(orders, inventory)
    first = _result_by_order_id(result, "SO-2026-001")
    second = _result_by_order_id(result, "SO-2026-002")
    assert first["warehouse"] == "HK Warehouse"
    assert first["status"] == "Fully Allocated"
    assert second["warehouse"] == "SG Warehouse"
    assert second["allocated_qty"] == 10
    assert second["backorder_qty"] == 5


def test_sku_with_no_inventory_rows_is_backordered_with_blank_warehouse():
    result = allocate_inventory(
        _orders_df(_order_row(sku="MED-MASK-003", quantity=5)),
        _inventory_df(_inventory_row(sku="MED-LENS-001")),
    )
    row = result["allocation_results"][0]
    assert row["status"] == "Backordered"
    assert row["allocated_qty"] == 0
    assert row["backorder_qty"] == 5
    assert row["warehouse"] == ""


# --- IA-008 reorder alert edge cases --------------------------------------


def test_missing_reorder_point_never_alerts():
    inventory_row = _inventory_row(available_qty=20)
    del inventory_row["reorder_point"]
    result = allocate_inventory(_orders_df(_order_row(quantity=20)), _inventory_df(inventory_row))
    remaining = result["remaining_inventory"][0]
    assert remaining["remaining_qty"] == 0
    assert remaining["reorder_alert"] == "No"
    assert "reorder_point" not in remaining
    assert result["supplier_follow_ups"] == []
    assert result["summary"]["low_stock_sku_count"] == 0


def test_remaining_qty_equal_to_reorder_point_does_not_alert():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=15)),
        _inventory_df(_inventory_row(available_qty=20, reorder_point=5)),
    )
    remaining = result["remaining_inventory"][0]
    assert remaining["remaining_qty"] == 5
    assert remaining["reorder_alert"] == "No"
    assert result["supplier_follow_ups"] == []


def test_low_stock_sku_count_counts_distinct_skus_not_warehouse_rows():
    inventory = _inventory_df(
        _inventory_row(warehouse="HK Warehouse", available_qty=3, reorder_point=5),
        _inventory_row(warehouse="SG Warehouse", available_qty=2, reorder_point=5),
    )
    result = allocate_inventory(_orders_df(_order_row(quantity=1)), inventory)
    assert len(result["supplier_follow_ups"]) == 2
    assert result["summary"]["low_stock_sku_count"] == 1


# --- AllocationSummary --------------------------------------------------


def test_summary_counts_match_result_statuses():
    orders = _orders_df(
        _order_row(order_id="SO-2026-001", sku="MED-LENS-001", quantity=5),
        _order_row(order_id="SO-2026-002", sku="MED-MASK-003", quantity=5),
        _order_row(order_id="SO-2026-003", sku="IND-PUMP-005", quantity=5),
    )
    inventory = _inventory_df(
        _inventory_row(sku="MED-LENS-001", available_qty=5),
        _inventory_row(sku="MED-MASK-003", available_qty=2),
    )
    result = allocate_inventory(orders, inventory)
    summary = result["summary"]
    assert summary["total_order_lines"] == 3
    assert summary["fully_allocated_count"] == 1
    assert summary["partially_allocated_count"] == 1
    assert summary["backordered_count"] == 1
    assert len(result["backorders"]) == 1
    assert result["backorders"][0]["order_id"] == "SO-2026-003"


# --- Malformed / missing required inventory data --------------------------


def test_malformed_available_qty_raises():
    bad_row = _inventory_row(available_qty="not-a-number")
    with pytest.raises(InvalidInventoryDataError):
        allocate_inventory(_orders_df(_order_row()), _inventory_df(bad_row))


def test_blank_sku_in_inventory_raises():
    bad_row = _inventory_row(sku="")
    with pytest.raises(InvalidInventoryDataError):
        allocate_inventory(_orders_df(_order_row()), _inventory_df(bad_row))


def test_blank_warehouse_in_inventory_raises():
    bad_row = _inventory_row(warehouse="")
    with pytest.raises(InvalidInventoryDataError):
        allocate_inventory(_orders_df(_order_row()), _inventory_df(bad_row))


# --- Loaders: required columns -------------------------------------------


def test_load_valid_orders_raises_when_payment_terms_column_missing(tmp_path):
    df = _orders_df(_order_row()).drop(columns=["payment_terms"])
    file_path = tmp_path / "valid_orders_missing_column.xlsx"
    df.to_excel(file_path, index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        load_valid_orders(file_path)
    assert "payment_terms" in str(exc_info.value)


def test_load_inventory_raises_when_available_qty_column_missing(tmp_path):
    df = _inventory_df(_inventory_row()).drop(columns=["available_qty"])
    file_path = tmp_path / "inventory_missing_column.xlsx"
    df.to_excel(file_path, index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        load_inventory(file_path)
    assert "available_qty" in str(exc_info.value)


def test_load_inventory_succeeds_when_optional_columns_absent(tmp_path):
    df = _inventory_df(_inventory_row()).drop(columns=["reorder_point", "supplier_name", "lead_time_days"])
    file_path = tmp_path / "inventory_minimal_columns.xlsx"
    df.to_excel(file_path, index=False)

    loaded = load_inventory(file_path)
    assert "available_qty" in loaded.columns
    assert "reorder_point" not in loaded.columns
