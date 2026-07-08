"""Fictional sample workbook generation for demo/manual use — not business logic."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def generate_product_master() -> pd.DataFrame:
    """Build the product master reference list. Exactly 1 SKU is inactive."""
    rows = [
        {"sku": "MED-LENS-001", "product_name": "Optical Lens Kit", "category": "Medical Device", "active": True},
        {"sku": "MED-GLOVE-002", "product_name": "Nitrile Exam Gloves (Box of 100)", "category": "Medical Device", "active": True},
        {"sku": "MED-MASK-003", "product_name": "Surgical Face Mask (Box of 50)", "category": "Medical Device", "active": True},
        {"sku": "IND-VALVE-004", "product_name": "Industrial Pressure Valve", "category": "Industrial Equipment", "active": True},
        {"sku": "IND-PUMP-005", "product_name": "Hydraulic Pump Unit", "category": "Industrial Equipment", "active": True},
        {"sku": "OFF-CHAIR-006", "product_name": "Ergonomic Office Chair", "category": "Office Furniture", "active": True},
        {"sku": "OFF-DESK-007", "product_name": "Adjustable Standing Desk", "category": "Office Furniture", "active": True},
        {"sku": "ELEC-CABLE-008", "product_name": "USB-C Cable 2m (Legacy)", "category": "Electronics", "active": False},
    ]
    return pd.DataFrame(rows)


def generate_orders(product_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build order lines. Exactly 1 duplicate order_id and 1 unknown-SKU row."""
    rows = [
        {"order_id": "SO-2026-001", "order_date": date(2026, 7, 1), "customer_name": "Bright Medical Trading Ltd", "customer_region": "Hong Kong", "sku": "MED-LENS-001", "product_name": "Optical Lens Kit", "quantity": 10, "requested_delivery_date": date(2026, 7, 15), "priority": "High", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-002", "order_date": date(2026, 7, 1), "customer_name": "Silver Oak Supplies", "customer_region": "Singapore", "sku": "MED-GLOVE-002", "product_name": "Nitrile Exam Gloves (Box of 100)", "quantity": 50, "requested_delivery_date": date(2026, 7, 10), "priority": "Normal", "payment_terms": "15 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-003", "order_date": date(2026, 7, 2), "customer_name": "Tai Yick Trading Co", "customer_region": "Hong Kong", "sku": "MED-MASK-003", "product_name": "Surgical Face Mask (Box of 50)", "quantity": 30, "requested_delivery_date": date(2026, 7, 12), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-004", "order_date": date(2026, 7, 2), "customer_name": "Formosa Industrial Group", "customer_region": "Taiwan", "sku": "IND-VALVE-004", "product_name": "Industrial Pressure Valve", "quantity": 5, "requested_delivery_date": date(2026, 7, 20), "priority": "High", "payment_terms": "45 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-005", "order_date": date(2026, 7, 3), "customer_name": "Bright Medical Trading Ltd", "customer_region": "Hong Kong", "sku": "IND-PUMP-005", "product_name": "Hydraulic Pump Unit", "quantity": 2, "requested_delivery_date": date(2026, 7, 25), "priority": "Low", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-006", "order_date": date(2026, 7, 3), "customer_name": "Golden Harbor Logistics", "customer_region": "Hong Kong", "sku": "OFF-CHAIR-006", "product_name": "Ergonomic Office Chair", "quantity": 15, "requested_delivery_date": date(2026, 7, 18), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-007", "order_date": date(2026, 7, 4), "customer_name": "Lion City Retail Pte Ltd", "customer_region": "Singapore", "sku": "OFF-DESK-007", "product_name": "Adjustable Standing Desk", "quantity": 8, "requested_delivery_date": date(2026, 7, 19), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-008", "order_date": date(2026, 7, 4), "customer_name": "Silver Oak Supplies", "customer_region": "Singapore", "sku": "MED-LENS-001", "product_name": "Optical Lens Kit", "quantity": 25, "requested_delivery_date": date(2026, 7, 14), "priority": "High", "payment_terms": "15 days", "sales_owner": "Wendy"},
        # Duplicate order_id (reused SO-2026-005 by mistake) — the required duplicate-order-id imperfection.
        {"order_id": "SO-2026-005", "order_date": date(2026, 7, 5), "customer_name": "Formosa Industrial Group", "customer_region": "Taiwan", "sku": "MED-GLOVE-002", "product_name": "Nitrile Exam Gloves (Box of 100)", "quantity": 20, "requested_delivery_date": date(2026, 7, 21), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        # Unknown SKU not present in product master — the required invalid-SKU imperfection.
        {"order_id": "SO-2026-009", "order_date": date(2026, 7, 5), "customer_name": "Tai Yick Trading Co", "customer_region": "Hong Kong", "sku": "MED-LENS-999", "product_name": "Optical Lens Kit (Discontinued Variant)", "quantity": 12, "requested_delivery_date": date(2026, 7, 22), "priority": "Low", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-010", "order_date": date(2026, 7, 6), "customer_name": "Golden Harbor Logistics", "customer_region": "Hong Kong", "sku": "IND-VALVE-004", "product_name": "Industrial Pressure Valve", "quantity": 3, "requested_delivery_date": date(2026, 7, 16), "priority": "High", "payment_terms": "45 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-011", "order_date": date(2026, 7, 6), "customer_name": "Lion City Retail Pte Ltd", "customer_region": "Singapore", "sku": "MED-MASK-003", "product_name": "Surgical Face Mask (Box of 50)", "quantity": 40, "requested_delivery_date": date(2026, 7, 17), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
    ]
    return pd.DataFrame(rows)


def generate_inventory(product_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build inventory records across 2 warehouses. MED-LENS-001 is deliberately
    stocked low across both warehouses to force partial allocation/backorder;
    its SG Warehouse row already sits below its reorder point before any
    allocation runs."""
    rows = [
        {"sku": "MED-LENS-001", "warehouse": "HK Warehouse", "available_qty": 20, "reserved_qty": 0, "reorder_point": 5, "supplier_name": "Vista Optics Supply", "lead_time_days": 18},
        {"sku": "MED-LENS-001", "warehouse": "SG Warehouse", "available_qty": 5, "reserved_qty": 0, "reorder_point": 6, "supplier_name": "Vista Optics Supply", "lead_time_days": 18},
        {"sku": "MED-GLOVE-002", "warehouse": "HK Warehouse", "available_qty": 80, "reserved_qty": 0, "reorder_point": 10, "supplier_name": "Everclean Medical Supply", "lead_time_days": 10},
        {"sku": "MED-GLOVE-002", "warehouse": "SG Warehouse", "available_qty": 30, "reserved_qty": 5, "reorder_point": 5, "supplier_name": "Everclean Medical Supply", "lead_time_days": 10},
        {"sku": "MED-MASK-003", "warehouse": "HK Warehouse", "available_qty": 100, "reserved_qty": 10, "reorder_point": 15, "supplier_name": "Everclean Medical Supply", "lead_time_days": 10},
        {"sku": "IND-VALVE-004", "warehouse": "HK Warehouse", "available_qty": 12, "reserved_qty": 0, "reorder_point": 4, "supplier_name": "Precision Hydraulics Ltd", "lead_time_days": 21},
        {"sku": "IND-VALVE-004", "warehouse": "SG Warehouse", "available_qty": 6, "reserved_qty": 0, "reorder_point": 2, "supplier_name": "Precision Hydraulics Ltd", "lead_time_days": 21},
        {"sku": "IND-PUMP-005", "warehouse": "HK Warehouse", "available_qty": 10, "reserved_qty": 1, "reorder_point": 3, "supplier_name": "Precision Hydraulics Ltd", "lead_time_days": 21},
        {"sku": "OFF-CHAIR-006", "warehouse": "HK Warehouse", "available_qty": 40, "reserved_qty": 0, "reorder_point": 8, "supplier_name": "Comfort Seating Supply Co", "lead_time_days": 30},
        {"sku": "OFF-DESK-007", "warehouse": "SG Warehouse", "available_qty": 20, "reserved_qty": 2, "reorder_point": 5, "supplier_name": "Comfort Seating Supply Co", "lead_time_days": 30},
    ]
    return pd.DataFrame(rows)


def generate_invoices(reference_date: date | None = None) -> pd.DataFrame:
    """Build invoices with due dates offset from reference_date so the mix stays
    believable (Current/overdue) no matter when this is regenerated. Exactly 1
    invoice is a clear high-priority overdue example; exactly 1 has a data issue
    (missing due date)."""
    if reference_date is None:
        reference_date = date.today()

    def offset(days: int) -> date:
        return reference_date - timedelta(days=days)

    rows = [
        # High-priority overdue: >60 days overdue and outstanding >= 50000 — the required imperfection.
        {"invoice_id": "INV-2026-001", "customer_name": "Bright Medical Trading Ltd", "invoice_date": offset(100), "due_date": offset(70), "invoice_amount": 58000.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": "Awaiting wire confirmation"},
        {"invoice_id": "INV-2026-002", "customer_name": "Silver Oak Supplies", "invoice_date": offset(60), "due_date": offset(30), "invoice_amount": 12000.00, "paid_amount": 0.0, "currency": "SGD", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None},
        {"invoice_id": "INV-2026-003", "customer_name": "Tai Yick Trading Co", "invoice_date": offset(75), "due_date": offset(45), "invoice_amount": 9000.00, "paid_amount": 3000.00, "currency": "HKD", "payment_status": "Partial", "sales_owner": "Jesse", "remarks": "Partial payment received, balance pending"},
        {"invoice_id": "INV-2026-004", "customer_name": "Formosa Industrial Group", "invoice_date": offset(40), "due_date": offset(10), "invoice_amount": 15000.00, "paid_amount": 15000.00, "currency": "TWD", "payment_status": "Paid", "sales_owner": "Marcus", "remarks": None},
        {"invoice_id": "INV-2026-005", "customer_name": "Golden Harbor Logistics", "invoice_date": offset(20), "due_date": offset(-15), "invoice_amount": 22000.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None},
        {"invoice_id": "INV-2026-006", "customer_name": "Lion City Retail Pte Ltd", "invoice_date": offset(10), "due_date": offset(-5), "invoice_amount": 18000.00, "paid_amount": 0.0, "currency": "SGD", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": "Confirm PO before due date"},
        {"invoice_id": "INV-2026-007", "customer_name": "Bright Medical Trading Ltd", "invoice_date": offset(85), "due_date": offset(55), "invoice_amount": 27000.00, "paid_amount": 4000.00, "currency": "HKD", "payment_status": "Partial", "sales_owner": "Jesse", "remarks": None},
        {"invoice_id": "INV-2026-008", "customer_name": "Silver Oak Supplies", "invoice_date": offset(35), "due_date": offset(5), "invoice_amount": 8000.00, "paid_amount": 0.0, "currency": "SGD", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None},
        # Data issue: missing due date — the required imperfection.
        {"invoice_id": "INV-2026-009", "customer_name": "Formosa Industrial Group", "invoice_date": offset(50), "due_date": None, "invoice_amount": 14000.00, "paid_amount": 0.0, "currency": "TWD", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": "Due date pending confirmation from customer"},
        {"invoice_id": "INV-2026-010", "customer_name": "Lion City Retail Pte Ltd", "invoice_date": offset(15), "due_date": offset(2), "invoice_amount": 6000.00, "paid_amount": 2000.00, "currency": "SGD", "payment_status": "Partial", "sales_owner": "Marcus", "remarks": None},
    ]
    return pd.DataFrame(rows)


def write_sample_workbooks(
    output_dir: Path = SAMPLE_DATA_DIR, reference_date: date | None = None
) -> None:
    """Generate and write all four sample workbooks to output_dir."""
    if reference_date is None:
        reference_date = date.today()

    output_dir.mkdir(parents=True, exist_ok=True)

    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)
    inventory_df = generate_inventory(product_master_df)
    invoices_df = generate_invoices(reference_date)

    product_master_df.to_excel(output_dir / "sample_product_master.xlsx", index=False)
    orders_df.to_excel(output_dir / "sample_orders.xlsx", index=False)
    inventory_df.to_excel(output_dir / "sample_inventory.xlsx", index=False)
    invoices_df.to_excel(output_dir / "sample_invoices.xlsx", index=False)


if __name__ == "__main__":
    write_sample_workbooks()
