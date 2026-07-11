"""Inventory allocation rules and allocation output (Phase 4 — sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md).

Implements IA-001 through IA-006 and IA-008. The Optional V2 region-matching
warehouse preference described in IA-007 is out of V1 scope per the Scope Gate
(context/build-plan.md, CONTEXT.md) and is not implemented here.
"""

from __future__ import annotations

from typing import TypedDict

import pandas as pd

from src.contracts import (
    AllocationResultRow,
    AllocationSummary,
    BackorderRow,
    RemainingInventoryRow,
    SupplierFollowUpRow,
)
from src.excel_io import load_excel, validate_required_columns

INVENTORY_ORDERS_REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_region",
    "sku",
    "quantity",
    "requested_delivery_date",
    "priority",
    "payment_terms",
]

INVENTORY_REQUIRED_COLUMNS = ["sku", "warehouse", "available_qty"]

# IA-001 — priority allocated High before Normal before Low.
PRIORITY_RANK = {"High": 0, "Normal": 1, "Low": 2}


class InvalidInventoryDataError(Exception):
    """Business-readable error for an inventory value that cannot be used for allocation."""

    def __init__(self, row_number: int, field: str, value: object = None) -> None:
        self.row_number = row_number
        self.field = field
        self.value = value
        value_text = "" if value is None else f": {_format_cell_value(value)}"
        message = (
            f"Inventory row {row_number} has a missing or invalid value for field "
            f"'{field}'{value_text}. Please check the sample file."
        )
        super().__init__(message)


class InvalidOrderDataError(Exception):
    """Business-readable error for a valid-orders value that cannot be used for allocation."""

    def __init__(self, row_number: int, field: str, value: object = None) -> None:
        self.row_number = row_number
        self.field = field
        self.value = value
        value_text = "" if value is None else f": {_format_cell_value(value)}"
        message = (
            f"Valid order row {row_number} has a missing or invalid value for required field "
            f"'{field}'{value_text}. Please re-run order validation or check the sample file."
        )
        super().__init__(message)


class InventoryAllocationResult(TypedDict):
    summary: AllocationSummary
    allocation_results: list[AllocationResultRow]
    backorders: list[BackorderRow]
    remaining_inventory: list[RemainingInventoryRow]
    supplier_follow_ups: list[SupplierFollowUpRow]


def load_valid_orders(file) -> pd.DataFrame:
    """Load valid_orders.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVENTORY_ORDERS_REQUIRED_COLUMNS, "valid orders file")
    return df


def load_inventory(file) -> pd.DataFrame:
    """Load inventory.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVENTORY_REQUIRED_COLUMNS, "inventory file")
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


def _format_cell_value(value: object) -> str:
    return repr(value)


def _to_trimmed_str(value: object) -> str:
    return str(value).strip()


def _parse_date(value: object) -> pd.Timestamp | None:
    """Return a normalized Timestamp, or None if value cannot be parsed as a date."""
    if isinstance(value, pd.Timestamp):
        return value
    try:
        parsed = pd.to_datetime(value)
    except (ValueError, TypeError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _require_order_quantity(value: object, row_number: int, field: str) -> int:
    """Return a positive whole-number order quantity, or raise InvalidOrderDataError."""
    if _is_blank(value) or isinstance(value, bool):
        raise InvalidOrderDataError(row_number, field, value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            raise InvalidOrderDataError(row_number, field, value)
        quantity = int(value)
    else:
        try:
            numeric = float(str(value).strip())
        except (ValueError, TypeError):
            raise InvalidOrderDataError(row_number, field, value) from None
        if not numeric.is_integer():
            raise InvalidOrderDataError(row_number, field, value)
        quantity = int(numeric)
    if quantity <= 0:
        raise InvalidOrderDataError(row_number, field, value)
    return quantity


def _require_order_date(value: object, row_number: int, field: str) -> pd.Timestamp:
    """Return a normalized order date, or raise InvalidOrderDataError."""
    if _is_blank(value):
        raise InvalidOrderDataError(row_number, field, value)
    parsed = _parse_date(value)
    if parsed is None:
        raise InvalidOrderDataError(row_number, field, value)
    return parsed


def _require_order_text(value: object, row_number: int, field: str) -> str:
    """Return trimmed required valid-order text, or raise InvalidOrderDataError."""
    if _is_blank(value):
        raise InvalidOrderDataError(row_number, field, value)
    return _to_trimmed_str(value)


def _require_order_priority(value: object, row_number: int) -> str:
    priority = _require_order_text(value, row_number, "priority")
    if priority not in PRIORITY_RANK:
        raise InvalidOrderDataError(row_number, "priority", value)
    return priority


def _require_non_blank(value: object, row_number: int, field: str) -> str:
    if _is_blank(value):
        raise InvalidInventoryDataError(row_number, field, value)
    return _to_trimmed_str(value)


def _require_quantity(value: object, row_number: int, field: str) -> int:
    """Return a validated non-negative whole number, or raise InvalidInventoryDataError."""
    if _is_blank(value) or isinstance(value, bool):
        raise InvalidInventoryDataError(row_number, field, value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            raise InvalidInventoryDataError(row_number, field, value)
        quantity = int(value)
    else:
        try:
            numeric = float(str(value).strip())
        except (ValueError, TypeError):
            raise InvalidInventoryDataError(row_number, field, value) from None
        if not numeric.is_integer():
            raise InvalidInventoryDataError(row_number, field, value)
        quantity = int(numeric)
    if quantity < 0:
        raise InvalidInventoryDataError(row_number, field, value)
    return quantity


def _optional_quantity(value: object, row_number: int, field: str) -> int | None:
    """Return a whole number, or None if the optional value is blank/unrecognized."""
    if _is_blank(value) or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return None
        quantity = int(value)
        if quantity < 0:
            raise InvalidInventoryDataError(row_number, field, value)
        return quantity
    try:
        numeric = float(str(value).strip())
    except (ValueError, TypeError):
        return None
    if not numeric.is_integer():
        return None
    quantity = int(numeric)
    if quantity < 0:
        raise InvalidInventoryDataError(row_number, field, value)
    return quantity


def _build_inventory_state(inventory_df: pd.DataFrame) -> tuple[dict[str, list[dict]], list[dict]]:
    """Return (entries grouped by sku, entries in original file order)."""
    by_sku: dict[str, list[dict]] = {}
    entries: list[dict] = []
    for position, (_, row) in enumerate(inventory_df.iterrows()):
        row_number = position + 2
        sku = _require_non_blank(row.get("sku"), row_number, "sku")
        warehouse = _require_non_blank(row.get("warehouse"), row_number, "warehouse")
        available_qty = _require_quantity(row.get("available_qty"), row_number, "available_qty")
        reserved_qty = _optional_quantity(row.get("reserved_qty"), row_number, "reserved_qty") or 0
        reorder_point = _optional_quantity(row.get("reorder_point"), row_number, "reorder_point")
        lead_time_days = _optional_quantity(row.get("lead_time_days"), row_number, "lead_time_days")
        supplier_name_value = row.get("supplier_name")
        supplier_name = None if _is_blank(supplier_name_value) else _to_trimmed_str(supplier_name_value)

        entry = {
            "sku": sku,
            "warehouse": warehouse,
            "starting_available_qty": available_qty,
            # IA-002 — allocatable_qty = available_qty - reserved_qty (reserved_qty defaults to 0 when missing).
            "allocatable_qty": max(available_qty - reserved_qty, 0),
            "allocated_qty": 0,
            "reorder_point": reorder_point,
            "supplier_name": supplier_name,
            "lead_time_days": lead_time_days,
        }
        by_sku.setdefault(sku, []).append(entry)
        entries.append(entry)
    return by_sku, entries


def _sort_orders_for_allocation(valid_orders_df: pd.DataFrame) -> list[dict]:
    """IA-001 — sort by priority, then requested delivery date, then order date, then order ID."""
    prepared: list[dict] = []
    for position, (_, row) in enumerate(valid_orders_df.iterrows()):
        row_number = position + 2
        requested_delivery = _require_order_date(
            row.get("requested_delivery_date"), row_number, "requested_delivery_date"
        )
        order_date = _require_order_date(row.get("order_date"), row_number, "order_date")
        product_name = row.get("product_name")
        prepared.append(
            {
                "order_id": _require_order_text(row.get("order_id"), row_number, "order_id"),
                "customer_name": _require_order_text(
                    row.get("customer_name"), row_number, "customer_name"
                ),
                "sku": _require_order_text(row.get("sku"), row_number, "sku"),
                "product_name": None if _is_blank(product_name) else _to_trimmed_str(product_name),
                "quantity": _require_order_quantity(row.get("quantity"), row_number, "quantity"),
                "priority": _require_order_priority(row.get("priority"), row_number),
                "requested_delivery_date": requested_delivery.date().isoformat(),
                "_requested_delivery_sort": requested_delivery,
                "_order_date_sort": order_date,
            }
        )
    prepared.sort(
        key=lambda o: (
            PRIORITY_RANK.get(o["priority"], len(PRIORITY_RANK)),
            o["_requested_delivery_sort"],
            o["_order_date_sort"],
            o["order_id"],
        )
    )
    return prepared


def _pick_warehouse(entries: list[dict]) -> dict:
    """IA-007 V1 — warehouse with the highest allocatable_qty for the SKU; ties broken by warehouse name."""
    return sorted(entries, key=lambda e: (-e["allocatable_qty"], e["warehouse"]))[0]


def _allocate_order_line(order: dict, inventory_by_sku: dict[str, list[dict]]) -> AllocationResultRow:
    entries = inventory_by_sku.get(order["sku"], [])
    if entries:
        chosen = _pick_warehouse(entries)
        warehouse = chosen["warehouse"]
        allocatable = chosen["allocatable_qty"]
        if allocatable >= order["quantity"]:
            # IA-003 — full allocation.
            allocated_qty = order["quantity"]
            status = "Fully Allocated"
        elif allocatable > 0:
            # IA-004 — partial allocation.
            allocated_qty = allocatable
            status = "Partially Allocated"
        else:
            # IA-005 — backorder.
            allocated_qty = 0
            status = "Backordered"
        chosen["allocatable_qty"] -= allocated_qty
        chosen["allocated_qty"] += allocated_qty
    else:
        warehouse = ""
        allocated_qty = 0
        status = "Backordered"

    backorder_qty = order["quantity"] - allocated_qty

    result: AllocationResultRow = {
        "order_id": order["order_id"],
        "customer_name": order["customer_name"],
        "sku": order["sku"],
        "requested_qty": order["quantity"],
        "allocated_qty": allocated_qty,
        "backorder_qty": backorder_qty,
        "warehouse": warehouse,
        "status": status,
        "priority": order["priority"],
        "requested_delivery_date": order["requested_delivery_date"],
    }
    if order["product_name"] is not None:
        result["product_name"] = order["product_name"]
    return result


def _build_remaining_inventory_row(entry: dict) -> tuple[RemainingInventoryRow, SupplierFollowUpRow | None]:
    remaining_qty = entry["starting_available_qty"] - entry["allocated_qty"]
    reorder_point = entry["reorder_point"]
    # IA-008 — reorder alert fires only when reorder_point is known and remaining_qty is strictly below it.
    reorder_alert = "Yes" if reorder_point is not None and remaining_qty < reorder_point else "No"

    row: RemainingInventoryRow = {
        "sku": entry["sku"],
        "warehouse": entry["warehouse"],
        "starting_available_qty": entry["starting_available_qty"],
        "allocated_qty": entry["allocated_qty"],
        "remaining_qty": remaining_qty,
        "reorder_alert": reorder_alert,
    }
    if reorder_point is not None:
        row["reorder_point"] = reorder_point

    follow_up: SupplierFollowUpRow | None = None
    if reorder_alert == "Yes":
        follow_up = {
            "sku": entry["sku"],
            "warehouse": entry["warehouse"],
            "remaining_qty": remaining_qty,
            "reorder_point": reorder_point,
        }
        if entry["supplier_name"] is not None:
            follow_up["supplier_name"] = entry["supplier_name"]
        if entry["lead_time_days"] is not None:
            follow_up["lead_time_days"] = entry["lead_time_days"]

    return row, follow_up


def _build_summary(allocation_results: list[AllocationResultRow], low_stock_sku_count: int) -> AllocationSummary:
    fully_allocated_count = sum(1 for r in allocation_results if r["status"] == "Fully Allocated")
    partially_allocated_count = sum(1 for r in allocation_results if r["status"] == "Partially Allocated")
    backordered_count = sum(1 for r in allocation_results if r["status"] == "Backordered")
    return {
        "total_order_lines": len(allocation_results),
        "fully_allocated_count": fully_allocated_count,
        "partially_allocated_count": partially_allocated_count,
        "backordered_count": backordered_count,
        "low_stock_sku_count": low_stock_sku_count,
    }


def allocate_inventory(valid_orders_df: pd.DataFrame, inventory_df: pd.DataFrame) -> InventoryAllocationResult:
    """Allocate validated order lines against inventory and return the full result envelope."""
    validate_required_columns(valid_orders_df, INVENTORY_ORDERS_REQUIRED_COLUMNS, "valid orders file")
    validate_required_columns(inventory_df, INVENTORY_REQUIRED_COLUMNS, "inventory file")

    inventory_by_sku, inventory_entries = _build_inventory_state(inventory_df)
    sorted_orders = _sort_orders_for_allocation(valid_orders_df)

    allocation_results = [_allocate_order_line(order, inventory_by_sku) for order in sorted_orders]
    # Backorders sheet is allocation_results filtered to status=Backordered (BackorderRow adds no new fields).
    backorders: list[BackorderRow] = [row for row in allocation_results if row["status"] == "Backordered"]

    remaining_inventory: list[RemainingInventoryRow] = []
    supplier_follow_ups: list[SupplierFollowUpRow] = []
    low_stock_skus: set[str] = set()

    for entry in inventory_entries:
        remaining_row, follow_up_row = _build_remaining_inventory_row(entry)
        remaining_inventory.append(remaining_row)
        if follow_up_row is not None:
            supplier_follow_ups.append(follow_up_row)
            low_stock_skus.add(entry["sku"])

    summary = _build_summary(allocation_results, len(low_stock_skus))

    return {
        "summary": summary,
        "allocation_results": allocation_results,
        "backorders": backorders,
        "remaining_inventory": remaining_inventory,
        "supplier_follow_ups": supplier_follow_ups,
    }
