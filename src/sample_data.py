"""Fictional sample workbook generation for demo/manual use — not business logic.

Scenario: a fictional regional medical optics / healthcare equipment company
(inspired only by the general shape of a Far East regional optics/healthcare
operating model — HK/China/Europe supply, HK + Mainland China customers). No
real company, product, customer, or pricing data is used anywhere below;
China/Europe appear only as fictional warehouse/supplier context, never as
new forecasting or production-planning logic.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"


def generate_product_master() -> pd.DataFrame:
    """Build the product master reference list. Exactly 2 SKUs are inactive
    (discontinued legacy items)."""
    rows = [
        {"sku": "VIS-SLIT-001", "product_name": "Slit Lamp Examination Unit", "category": "Vision Systems", "active": True},
        {"sku": "VIS-LENS-002", "product_name": "Trial Lens Set (Standard)", "category": "Vision Systems", "active": True},
        {"sku": "VIS-REFR-003", "product_name": "Digital Refractor Head", "category": "Vision Systems", "active": True},
        {"sku": "VIS-LOUPE-004", "product_name": "Surgical Loupe Set (Legacy)", "category": "Vision Systems", "active": False},
        {"sku": "DIAG-OCT-005", "product_name": "Handheld OCT Scanner", "category": "Diagnostic Equipment", "active": True},
        {"sku": "DIAG-FUND-006", "product_name": "Fundus Camera Unit", "category": "Diagnostic Equipment", "active": True},
        {"sku": "DIAG-TONO-007", "product_name": "Non-Contact Tonometer", "category": "Diagnostic Equipment", "active": True},
        {"sku": "DIAG-AUTO-008", "product_name": "Auto Lensmeter", "category": "Diagnostic Equipment", "active": True},
        {"sku": "CONS-WIPE-009", "product_name": "Lens Cleaning Wipes (Pack of 200)", "category": "Clinical Consumables", "active": True},
        {"sku": "CONS-DROP-010", "product_name": "Diagnostic Dilation Drops (Box of 50)", "category": "Clinical Consumables", "active": True},
        {"sku": "CONS-COVER-011", "product_name": "Disposable Chin Rest Covers (Pack of 500)", "category": "Clinical Consumables", "active": True},
        {"sku": "CONS-CALSTRIP-012", "product_name": "Calibration Test Strips (Box of 100)", "category": "Clinical Consumables", "active": True},
        {"sku": "PART-BULB-013", "product_name": "Slit Lamp Replacement Bulb", "category": "Service Parts", "active": True},
        {"sku": "PART-CHINREST-014", "product_name": "Chin Rest Assembly (Replacement)", "category": "Service Parts", "active": True},
        {"sku": "PART-CAL-015", "product_name": "Tonometer Calibration Kit", "category": "Service Parts", "active": True},
        {"sku": "PART-FILTER-016", "product_name": "Legacy Filter Module (Discontinued)", "category": "Service Parts", "active": False},
        {"sku": "SW-LIC-017", "product_name": "Diagnostic Imaging Software License (Annual)", "category": "Software & Service Packages", "active": True},
        {"sku": "SW-SVC-018", "product_name": "Preventive Maintenance Service Package (Standard)", "category": "Software & Service Packages", "active": True},
    ]
    return pd.DataFrame(rows)


def generate_orders(product_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build order lines for a fictional HK/Mainland-China customer base.

    ~19% of rows carry at least one intentional issue, several combining more
    than one problem on the same row (a sloppy data-entry day), rather than
    dedicating a separate row to every issue type:
      - 1x duplicate order_id (SO-2026-010 reused)
      - 1x unknown sku (not in product master)
      - 1x inactive sku referenced
      - 1x missing sku + blank payment_terms (warning-only)
      - 1x quantity = 0 + missing requested_delivery_date
      - 1x quantity negative + invalid priority value
      - 1x quantity non-whole-number + requested_delivery_date before order_date
    """
    rows = [
        {"order_id": "SO-2026-001", "order_date": date(2026, 7, 1), "customer_name": "Victoria Harbour Eye Institute", "customer_region": "Hong Kong", "sku": "VIS-SLIT-001", "product_name": "Slit Lamp Examination Unit", "quantity": 3, "requested_delivery_date": date(2026, 7, 15), "priority": "High", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-002", "order_date": date(2026, 7, 1), "customer_name": "Pearl River Medical Distribution Co", "customer_region": "Guangdong", "sku": "VIS-LENS-002", "product_name": "Trial Lens Set (Standard)", "quantity": 20, "requested_delivery_date": date(2026, 7, 12), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-003", "order_date": date(2026, 7, 1), "customer_name": "Huangpu District Eye Hospital", "customer_region": "Shanghai", "sku": "CONS-WIPE-009", "product_name": "Lens Cleaning Wipes (Pack of 200)", "quantity": 100, "requested_delivery_date": date(2026, 7, 10), "priority": "Normal", "payment_terms": "15 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-004", "order_date": date(2026, 7, 2), "customer_name": "Kowloon Central Hospital", "customer_region": "Hong Kong", "sku": "DIAG-TONO-007", "product_name": "Non-Contact Tonometer", "quantity": 2, "requested_delivery_date": date(2026, 7, 20), "priority": "High", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-005", "order_date": date(2026, 7, 2), "customer_name": "Beijing Capital Eye Center", "customer_region": "Beijing", "sku": "DIAG-OCT-005", "product_name": "Handheld OCT Scanner", "quantity": 5, "requested_delivery_date": date(2026, 7, 22), "priority": "High", "payment_terms": "45 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-006", "order_date": date(2026, 7, 2), "customer_name": "Golden Bay Optical Chain", "customer_region": "Guangdong", "sku": "CONS-DROP-010", "product_name": "Diagnostic Dilation Drops (Box of 50)", "quantity": 40, "requested_delivery_date": date(2026, 7, 14), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-007", "order_date": date(2026, 7, 3), "customer_name": "Lion Rock Vision Clinic Group", "customer_region": "Hong Kong", "sku": "CONS-CALSTRIP-012", "product_name": "Calibration Test Strips (Box of 100)", "quantity": 15, "requested_delivery_date": date(2026, 7, 16), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-008", "order_date": date(2026, 7, 3), "customer_name": "Shanghai Vision Research Institute", "customer_region": "Shanghai", "sku": "VIS-REFR-003", "product_name": "Digital Refractor Head", "quantity": 2, "requested_delivery_date": date(2026, 7, 25), "priority": "Low", "payment_terms": "45 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-009", "order_date": date(2026, 7, 3), "customer_name": "Chaoyang Medical Equipment Co", "customer_region": "Beijing", "sku": "DIAG-AUTO-008", "product_name": "Auto Lensmeter", "quantity": 6, "requested_delivery_date": date(2026, 7, 18), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-010", "order_date": date(2026, 7, 4), "customer_name": "Harbour City Biomedical Services", "customer_region": "Hong Kong", "sku": "PART-BULB-013", "product_name": "Slit Lamp Replacement Bulb", "quantity": 10, "requested_delivery_date": date(2026, 7, 17), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-011", "order_date": date(2026, 7, 4), "customer_name": "Northern Star University Hospital", "customer_region": "Beijing", "sku": "PART-CHINREST-014", "product_name": "Chin Rest Assembly (Replacement)", "quantity": 4, "requested_delivery_date": date(2026, 7, 19), "priority": "Low", "payment_terms": "45 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-012", "order_date": date(2026, 7, 4), "customer_name": "New Territories Optical Supplies", "customer_region": "Hong Kong", "sku": "VIS-LENS-002", "product_name": "Trial Lens Set (Standard)", "quantity": 30, "requested_delivery_date": date(2026, 7, 16), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-013", "order_date": date(2026, 7, 5), "customer_name": "Zhuhai Cross-Border Medical Center", "customer_region": "Guangdong", "sku": "CONS-WIPE-009", "product_name": "Lens Cleaning Wipes (Pack of 200)", "quantity": 80, "requested_delivery_date": date(2026, 7, 15), "priority": "Normal", "payment_terms": "15 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-014", "order_date": date(2026, 7, 5), "customer_name": "Bund Optical Partners", "customer_region": "Shanghai", "sku": "DIAG-FUND-006", "product_name": "Fundus Camera Unit", "quantity": 2, "requested_delivery_date": date(2026, 7, 21), "priority": "High", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-015", "order_date": date(2026, 7, 5), "customer_name": "Sichuan Regional Health Distributors", "customer_region": "Other Mainland China", "sku": "CONS-COVER-011", "product_name": "Disposable Chin Rest Covers (Pack of 500)", "quantity": 50, "requested_delivery_date": date(2026, 7, 13), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-016", "order_date": date(2026, 7, 6), "customer_name": "Yangtze Vision Clinic Network", "customer_region": "Other Mainland China", "sku": "VIS-SLIT-001", "product_name": "Slit Lamp Examination Unit", "quantity": 2, "requested_delivery_date": date(2026, 7, 24), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-017", "order_date": date(2026, 7, 6), "customer_name": "Fujian Coastal Eye Care Group", "customer_region": "Other Mainland China", "sku": "DIAG-TONO-007", "product_name": "Non-Contact Tonometer", "quantity": 3, "requested_delivery_date": date(2026, 7, 23), "priority": "Normal", "payment_terms": "45 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-018", "order_date": date(2026, 7, 6), "customer_name": "Victoria Harbour Eye Institute", "customer_region": "Hong Kong", "sku": "CONS-DROP-010", "product_name": "Diagnostic Dilation Drops (Box of 50)", "quantity": 25, "requested_delivery_date": date(2026, 7, 18), "priority": "Low", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-019", "order_date": date(2026, 7, 7), "customer_name": "Pearl River Medical Distribution Co", "customer_region": "Guangdong", "sku": "PART-CAL-015", "product_name": "Tonometer Calibration Kit", "quantity": 4, "requested_delivery_date": date(2026, 7, 27), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-020", "order_date": date(2026, 7, 7), "customer_name": "Huangpu District Eye Hospital", "customer_region": "Shanghai", "sku": "CONS-CALSTRIP-012", "product_name": "Calibration Test Strips (Box of 100)", "quantity": 10, "requested_delivery_date": date(2026, 7, 19), "priority": "Normal", "payment_terms": "15 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-021", "order_date": date(2026, 7, 7), "customer_name": "Kowloon Central Hospital", "customer_region": "Hong Kong", "sku": "VIS-LENS-002", "product_name": "Trial Lens Set (Standard)", "quantity": 15, "requested_delivery_date": date(2026, 7, 17), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-022", "order_date": date(2026, 7, 8), "customer_name": "Beijing Capital Eye Center", "customer_region": "Beijing", "sku": "DIAG-AUTO-008", "product_name": "Auto Lensmeter", "quantity": 3, "requested_delivery_date": date(2026, 7, 22), "priority": "High", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-023", "order_date": date(2026, 7, 8), "customer_name": "Lion Rock Vision Clinic Group", "customer_region": "Hong Kong", "sku": "PART-BULB-013", "product_name": "Slit Lamp Replacement Bulb", "quantity": 6, "requested_delivery_date": date(2026, 7, 20), "priority": "Low", "payment_terms": "30 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-024", "order_date": date(2026, 7, 8), "customer_name": "Golden Bay Optical Chain", "customer_region": "Guangdong", "sku": "VIS-REFR-003", "product_name": "Digital Refractor Head", "quantity": 1, "requested_delivery_date": date(2026, 7, 26), "priority": "Normal", "payment_terms": "45 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-025", "order_date": date(2026, 7, 8), "customer_name": "Chaoyang Medical Equipment Co", "customer_region": "Beijing", "sku": "CONS-WIPE-009", "product_name": "Lens Cleaning Wipes (Pack of 200)", "quantity": 60, "requested_delivery_date": date(2026, 7, 16), "priority": "Normal", "payment_terms": "15 days", "sales_owner": "Priya"},
        {"order_id": "SO-2026-026", "order_date": date(2026, 7, 9), "customer_name": "Harbour City Biomedical Services", "customer_region": "Hong Kong", "sku": "PART-CHINREST-014", "product_name": "Chin Rest Assembly (Replacement)", "quantity": 5, "requested_delivery_date": date(2026, 7, 21), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        {"order_id": "SO-2026-027", "order_date": date(2026, 7, 9), "customer_name": "Shanghai Vision Research Institute", "customer_region": "Shanghai", "sku": "DIAG-OCT-005", "product_name": "Handheld OCT Scanner", "quantity": 1, "requested_delivery_date": date(2026, 7, 24), "priority": "Normal", "payment_terms": "45 days", "sales_owner": "Marcus"},
        {"order_id": "SO-2026-028", "order_date": date(2026, 7, 9), "customer_name": "Northern Star University Hospital", "customer_region": "Beijing", "sku": "CONS-COVER-011", "product_name": "Disposable Chin Rest Covers (Pack of 500)", "quantity": 40, "requested_delivery_date": date(2026, 7, 19), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Jesse"},
        {"order_id": "SO-2026-029", "order_date": date(2026, 7, 9), "customer_name": "New Territories Optical Supplies", "customer_region": "Hong Kong", "sku": "DIAG-FUND-006", "product_name": "Fundus Camera Unit", "quantity": 1, "requested_delivery_date": date(2026, 7, 25), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Priya"},
        # Unknown SKU not present in product master — the required invalid-SKU imperfection.
        {"order_id": "SO-2026-030", "order_date": date(2026, 7, 10), "customer_name": "Zhuhai Cross-Border Medical Center", "customer_region": "Guangdong", "sku": "VIS-SCOPE-099", "product_name": "Portable Slit Lamp (New Model)", "quantity": 2, "requested_delivery_date": date(2026, 7, 28), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Wendy"},
        # Inactive SKU referenced — the required inactive-SKU imperfection.
        {"order_id": "SO-2026-031", "order_date": date(2026, 7, 10), "customer_name": "Bund Optical Partners", "customer_region": "Shanghai", "sku": "VIS-LOUPE-004", "product_name": "Surgical Loupe Set (Legacy)", "quantity": 2, "requested_delivery_date": date(2026, 7, 26), "priority": "Low", "payment_terms": "30 days", "sales_owner": "Marcus"},
        # Combo issue: missing sku + blank payment_terms (warning-only).
        {"order_id": "SO-2026-032", "order_date": date(2026, 7, 10), "customer_name": "Sichuan Regional Health Distributors", "customer_region": "Other Mainland China", "sku": None, "product_name": None, "quantity": 5, "requested_delivery_date": date(2026, 7, 25), "priority": "Normal", "payment_terms": None, "sales_owner": "Jesse"},
        # Combo issue: quantity = 0 + missing requested_delivery_date.
        {"order_id": "SO-2026-033", "order_date": date(2026, 7, 10), "customer_name": "Yangtze Vision Clinic Network", "customer_region": "Other Mainland China", "sku": "CONS-WIPE-009", "product_name": "Lens Cleaning Wipes (Pack of 200)", "quantity": 0, "requested_delivery_date": None, "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Priya"},
        # Combo issue: quantity negative + invalid priority value.
        {"order_id": "SO-2026-034", "order_date": date(2026, 7, 10), "customer_name": "Fujian Coastal Eye Care Group", "customer_region": "Other Mainland China", "sku": "CONS-DROP-010", "product_name": "Diagnostic Dilation Drops (Box of 50)", "quantity": -5, "requested_delivery_date": date(2026, 7, 27), "priority": "Urgent", "payment_terms": "30 days", "sales_owner": "Wendy"},
        # Combo issue: quantity non-whole-number + delivery date before order date.
        {"order_id": "SO-2026-035", "order_date": date(2026, 7, 10), "customer_name": "Victoria Harbour Eye Institute", "customer_region": "Hong Kong", "sku": "VIS-SLIT-001", "product_name": "Slit Lamp Examination Unit", "quantity": 2.5, "requested_delivery_date": date(2026, 7, 5), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Marcus"},
        # Duplicate order_id (reuses SO-2026-010 by mistake) — the required duplicate-order-id imperfection.
        {"order_id": "SO-2026-010", "order_date": date(2026, 7, 10), "customer_name": "Pearl River Medical Distribution Co", "customer_region": "Guangdong", "sku": "DIAG-TONO-007", "product_name": "Non-Contact Tonometer", "quantity": 1, "requested_delivery_date": date(2026, 7, 29), "priority": "Normal", "payment_terms": "30 days", "sales_owner": "Priya"},
    ]
    return pd.DataFrame(rows)


def generate_inventory(product_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build inventory records across HK, China, and Europe warehouses.

    DIAG-TONO-007's HK Warehouse row is deliberately below its reorder point
    before any allocation runs and stays untouched by orders (China Warehouse
    has more allocatable stock, so IA-007's stand-in warehouse-pick rule
    routes demand there instead). PART-CAL-015 has no inventory row at all,
    guaranteeing at least one valid order fully backorders.
    """
    rows = [
        {"sku": "VIS-SLIT-001", "warehouse": "HK Warehouse", "available_qty": 15, "reserved_qty": 0, "reorder_point": 4, "supplier_name": "Reingold Optical Instruments Ltd", "lead_time_days": 35},
        {"sku": "VIS-SLIT-001", "warehouse": "Europe Warehouse", "available_qty": 8, "reserved_qty": 0, "reorder_point": 3, "supplier_name": "Reingold Optical Instruments Ltd", "lead_time_days": 25},
        {"sku": "VIS-LENS-002", "warehouse": "HK Warehouse", "available_qty": 60, "reserved_qty": 5, "reorder_point": 15, "supplier_name": "Pearl Vision Manufacturing Ltd", "lead_time_days": 14},
        {"sku": "VIS-LENS-002", "warehouse": "China Warehouse", "available_qty": 40, "reserved_qty": 0, "reorder_point": 10, "supplier_name": "Pearl Vision Manufacturing Ltd", "lead_time_days": 10},
        {"sku": "VIS-REFR-003", "warehouse": "HK Warehouse", "available_qty": 6, "reserved_qty": 0, "reorder_point": 2, "supplier_name": "Reingold Optical Instruments Ltd", "lead_time_days": 30},
        {"sku": "DIAG-OCT-005", "warehouse": "HK Warehouse", "available_qty": 4, "reserved_qty": 0, "reorder_point": 2, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 40},
        {"sku": "DIAG-OCT-005", "warehouse": "Europe Warehouse", "available_qty": 3, "reserved_qty": 1, "reorder_point": 2, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 32},
        {"sku": "DIAG-FUND-006", "warehouse": "HK Warehouse", "available_qty": 5, "reserved_qty": 0, "reorder_point": 2, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 28},
        {"sku": "DIAG-TONO-007", "warehouse": "HK Warehouse", "available_qty": 2, "reserved_qty": 0, "reorder_point": 3, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 21},
        {"sku": "DIAG-TONO-007", "warehouse": "China Warehouse", "available_qty": 10, "reserved_qty": 2, "reorder_point": 4, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 15},
        {"sku": "DIAG-AUTO-008", "warehouse": "China Warehouse", "available_qty": 12, "reserved_qty": 0, "reorder_point": 4, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 15},
        {"sku": "CONS-WIPE-009", "warehouse": "HK Warehouse", "available_qty": 300, "reserved_qty": 20, "reorder_point": 50, "supplier_name": "Everclean Medical Supply", "lead_time_days": 7},
        {"sku": "CONS-DROP-010", "warehouse": "HK Warehouse", "available_qty": 150, "reserved_qty": 10, "reorder_point": 30, "supplier_name": "Everclean Medical Supply", "lead_time_days": 7},
        {"sku": "CONS-COVER-011", "warehouse": "China Warehouse", "available_qty": 400, "reserved_qty": 0, "reorder_point": 60, "supplier_name": "Everclean Medical Supply", "lead_time_days": 5},
        {"sku": "CONS-CALSTRIP-012", "warehouse": "HK Warehouse", "available_qty": 90, "reserved_qty": 5, "reorder_point": 20, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 12},
        {"sku": "PART-BULB-013", "warehouse": "HK Warehouse", "available_qty": 25, "reserved_qty": 0, "reorder_point": 8, "supplier_name": "Reingold Optical Instruments Ltd", "lead_time_days": 20},
        {"sku": "PART-CHINREST-014", "warehouse": "China Warehouse", "available_qty": 18, "reserved_qty": 2, "reorder_point": 6, "supplier_name": "Pearl Vision Manufacturing Ltd", "lead_time_days": 12},
    ]
    return pd.DataFrame(rows)


def generate_invoices(reference_date: date | None = None) -> pd.DataFrame:
    """Build invoices with due dates offset from reference_date so the mix
    stays believable (every aging bucket, Paid/Partial/Unpaid, high-priority
    by age and by amount) no matter when this is regenerated. Exactly 1
    invoice has a missing due date, exactly 1 has an invalid/negative
    amount, and exactly 1 is a deliberate overpayment (paid_amount >
    invoice_amount)."""
    if reference_date is None:
        reference_date = date.today()

    def offset(days: int) -> date | None:
        if days is None:
            return None
        return reference_date - timedelta(days=days)

    rows = [
        # High-priority by both age (>60 days) and amount (>=50000).
        {"invoice_id": "INV-2026-001", "customer_name": "Victoria Harbour Eye Institute", "invoice_date": offset(160), "due_date": offset(130), "invoice_amount": 68000.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": "Awaiting wire confirmation from finance", "order_id": "SO-2026-001"},
        {"invoice_id": "INV-2026-002", "customer_name": "Kowloon Central Hospital", "invoice_date": offset(55), "due_date": offset(25), "invoice_amount": 14000.00, "paid_amount": 14000.00, "currency": "HKD", "payment_status": "Paid", "sales_owner": "Jesse", "remarks": None, "order_id": "SO-2026-004"},
        {"invoice_id": "INV-2026-003", "customer_name": "Lion Rock Vision Clinic Group", "invoice_date": offset(20), "due_date": offset(-10), "invoice_amount": 9600.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": None, "order_id": "SO-2026-007"},
        {"invoice_id": "INV-2026-004", "customer_name": "Harbour City Biomedical Services", "invoice_date": offset(15), "due_date": offset(-3), "invoice_amount": 4200.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": "Confirm PO before due date", "order_id": "SO-2026-010"},
        {"invoice_id": "INV-2026-005", "customer_name": "New Territories Optical Supplies", "invoice_date": offset(40), "due_date": offset(12), "invoice_amount": 21000.00, "paid_amount": 5000.00, "currency": "HKD", "payment_status": "Partial", "sales_owner": "Jesse", "remarks": "Partial payment received, balance pending", "order_id": "SO-2026-012"},
        {"invoice_id": "INV-2026-006", "customer_name": "Pearl River Medical Distribution Co", "invoice_date": offset(50), "due_date": offset(20), "invoice_amount": 18000.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None, "order_id": "SO-2026-002"},
        {"invoice_id": "INV-2026-007", "customer_name": "Golden Bay Optical Chain", "invoice_date": offset(65), "due_date": offset(35), "invoice_amount": 12500.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None, "order_id": "SO-2026-006"},
        {"invoice_id": "INV-2026-008", "customer_name": "Zhuhai Cross-Border Medical Center", "invoice_date": offset(75), "due_date": offset(48), "invoice_amount": 27000.00, "paid_amount": 8000.00, "currency": "CNY", "payment_status": "Partial", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-013"},
        {"invoice_id": "INV-2026-009", "customer_name": "Huangpu District Eye Hospital", "invoice_date": offset(45), "due_date": offset(18), "invoice_amount": 9500.00, "paid_amount": 3000.00, "currency": "CNY", "payment_status": "Partial", "sales_owner": "Marcus", "remarks": "Partial payment received, balance pending", "order_id": "SO-2026-003"},
        {"invoice_id": "INV-2026-010", "customer_name": "Shanghai Vision Research Institute", "invoice_date": offset(80), "due_date": offset(52), "invoice_amount": 16000.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-008"},
        {"invoice_id": "INV-2026-011", "customer_name": "Bund Optical Partners", "invoice_date": offset(95), "due_date": offset(68), "invoice_amount": 23000.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None, "order_id": "SO-2026-014"},
        {"invoice_id": "INV-2026-012", "customer_name": "Beijing Capital Eye Center", "invoice_date": offset(110), "due_date": offset(82), "invoice_amount": 31000.00, "paid_amount": 6000.00, "currency": "CNY", "payment_status": "Partial", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-005"},
        {"invoice_id": "INV-2026-013", "customer_name": "Chaoyang Medical Equipment Co", "invoice_date": offset(60), "due_date": offset(33), "invoice_amount": 13500.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": None, "order_id": "SO-2026-009"},
        {"invoice_id": "INV-2026-014", "customer_name": "Northern Star University Hospital", "invoice_date": offset(5), "due_date": offset(-25), "invoice_amount": 8700.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": None, "order_id": "SO-2026-011"},
        {"invoice_id": "INV-2026-015", "customer_name": "Sichuan Regional Health Distributors", "invoice_date": offset(100), "due_date": offset(72), "invoice_amount": 19000.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-015"},
        {"invoice_id": "INV-2026-016", "customer_name": "Yangtze Vision Clinic Network", "invoice_date": offset(140), "due_date": offset(112), "invoice_amount": 52000.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": "High-value order, follow up urgently", "order_id": "SO-2026-016"},
        {"invoice_id": "INV-2026-017", "customer_name": "Fujian Coastal Eye Care Group", "invoice_date": offset(150), "due_date": offset(122), "invoice_amount": 6400.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-017"},
        {"invoice_id": "INV-2026-018", "customer_name": "Kowloon Central Hospital", "invoice_date": offset(25), "due_date": offset(-2), "invoice_amount": 3100.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": "Confirm receipt of goods", "order_id": "SO-2026-021"},
        {"invoice_id": "INV-2026-019", "customer_name": "Victoria Harbour Eye Institute", "invoice_date": offset(35), "due_date": offset(8), "invoice_amount": 5600.00, "paid_amount": 5600.00, "currency": "HKD", "payment_status": "Paid", "sales_owner": "Jesse", "remarks": None, "order_id": "SO-2026-018"},
        {"invoice_id": "INV-2026-020", "customer_name": "Lion Rock Vision Clinic Group", "invoice_date": offset(28), "due_date": offset(1), "invoice_amount": 2100.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": None, "order_id": "SO-2026-023"},
        {"invoice_id": "INV-2026-021", "customer_name": "Golden Bay Optical Chain", "invoice_date": offset(62), "due_date": offset(31), "invoice_amount": 9800.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": None, "order_id": "SO-2026-024"},
        {"invoice_id": "INV-2026-022", "customer_name": "Chaoyang Medical Equipment Co", "invoice_date": offset(92), "due_date": offset(61), "invoice_amount": 15300.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Priya", "remarks": None, "order_id": "SO-2026-025"},
        {"invoice_id": "INV-2026-023", "customer_name": "Northern Star University Hospital", "invoice_date": offset(120), "due_date": offset(90), "invoice_amount": 8900.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": None, "order_id": "SO-2026-026"},
        # Data issue: missing due date — the required imperfection.
        {"invoice_id": "INV-2026-024", "customer_name": "Shanghai Vision Research Institute", "invoice_date": offset(60), "due_date": None, "invoice_amount": 11200.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Priya", "remarks": "Due date pending confirmation from customer", "order_id": "SO-2026-027"},
        # Data issue: invalid/negative invoice amount — the required imperfection.
        {"invoice_id": "INV-2026-025", "customer_name": "Bund Optical Partners", "invoice_date": offset(45), "due_date": offset(18), "invoice_amount": -500.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Wendy", "remarks": "Amount under review — possible entry error", "order_id": None},
        # Deliberate overpayment example (paid_amount > invoice_amount) — documented in README_sample_data.md.
        {"invoice_id": "INV-2026-026", "customer_name": "Beijing Capital Eye Center", "invoice_date": offset(50), "due_date": offset(20), "invoice_amount": 7000.00, "paid_amount": 8500.00, "currency": "CNY", "payment_status": "Paid", "sales_owner": "Priya", "remarks": "Overpayment recorded — refund or credit pending finance review", "order_id": None},
        {"invoice_id": "INV-2026-027", "customer_name": "Sichuan Regional Health Distributors", "invoice_date": offset(15), "due_date": offset(-12), "invoice_amount": 16400.00, "paid_amount": 0.0, "currency": "CNY", "payment_status": "Unpaid", "sales_owner": "Marcus", "remarks": None, "order_id": None},
    ]
    return pd.DataFrame(rows)


def generate_customers() -> pd.DataFrame:
    """Build the optional, reference-only customer list. No Python business
    module reads this file — it exists purely so the demo feels like a real
    regional sales-ops workflow. `customer_name` values mostly match those
    used in generate_orders()/generate_invoices()."""
    rows = [
        {"customer_id": "CUST-001", "customer_name": "Victoria Harbour Eye Institute", "customer_region": "Hong Kong", "customer_type": "Public Hospital", "contact_person": "Alice Fong", "email": "alice.fong@victoriaharboureye.example", "phone": "+852 2345 6001", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-002", "customer_name": "Kowloon Central Hospital", "customer_region": "Hong Kong", "customer_type": "Public Hospital", "contact_person": "Brian Tsui", "email": "brian.tsui@kowlooncentral.example", "phone": "+852 2345 6002", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-003", "customer_name": "Lion Rock Vision Clinic Group", "customer_region": "Hong Kong", "customer_type": "Private Clinic Group", "contact_person": "Carmen Lai", "email": "carmen.lai@lionrockvision.example", "phone": "+852 2345 6003", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-004", "customer_name": "Harbour City Biomedical Services", "customer_region": "Hong Kong", "customer_type": "Service Partner", "contact_person": "Derek Ho", "email": "derek.ho@harbourcitybio.example", "phone": "+852 2345 6004", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-005", "customer_name": "New Territories Optical Supplies", "customer_region": "Hong Kong", "customer_type": "Medical Distributor", "contact_person": "Ella Yip", "email": "ella.yip@ntoptical.example", "phone": "+852 2345 6005", "payment_terms": "30 days", "credit_status": "Watch"},
        {"customer_id": "CUST-006", "customer_name": "Pearl River Medical Distribution Co", "customer_region": "Guangdong", "customer_type": "Medical Distributor", "contact_person": "Feng Zhao", "email": "feng.zhao@pearlrivermed.example", "phone": "+86 20 8100 6006", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-007", "customer_name": "Golden Bay Optical Chain", "customer_region": "Guangdong", "customer_type": "Optical Clinic Chain", "contact_person": "Grace Huang", "email": "grace.huang@goldenbayoptical.example", "phone": "+86 20 8100 6007", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-008", "customer_name": "Zhuhai Cross-Border Medical Center", "customer_region": "Guangdong", "customer_type": "Public Hospital", "contact_person": "Hao Chen", "email": "hao.chen@zhuhaicrossborder.example", "phone": "+86 756 300 6008", "payment_terms": "15 days", "credit_status": "Watch"},
        {"customer_id": "CUST-009", "customer_name": "Huangpu District Eye Hospital", "customer_region": "Shanghai", "customer_type": "Public Hospital", "contact_person": "Irene Shen", "email": "irene.shen@huangpueye.example", "phone": "+86 21 6100 6009", "payment_terms": "15 days", "credit_status": "Good"},
        {"customer_id": "CUST-010", "customer_name": "Shanghai Vision Research Institute", "customer_region": "Shanghai", "customer_type": "University / Research Lab", "contact_person": "Jason Pan", "email": "jason.pan@shvisionresearch.example", "phone": "+86 21 6100 6010", "payment_terms": "45 days", "credit_status": "Good"},
        {"customer_id": "CUST-011", "customer_name": "Bund Optical Partners", "customer_region": "Shanghai", "customer_type": "Private Clinic Group", "contact_person": "Karen Xu", "email": "karen.xu@bundoptical.example", "phone": "+86 21 6100 6011", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-012", "customer_name": "Beijing Capital Eye Center", "customer_region": "Beijing", "customer_type": "Public Hospital", "contact_person": "Leo Wang", "email": "leo.wang@capitaleyecenter.example", "phone": "+86 10 8500 6012", "payment_terms": "45 days", "credit_status": "Good"},
        {"customer_id": "CUST-013", "customer_name": "Chaoyang Medical Equipment Co", "customer_region": "Beijing", "customer_type": "Medical Distributor", "contact_person": "Mia Sun", "email": "mia.sun@chaoyangmedequip.example", "phone": "+86 10 8500 6013", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-014", "customer_name": "Northern Star University Hospital", "customer_region": "Beijing", "customer_type": "University / Research Lab", "contact_person": "Nathan Guo", "email": "nathan.guo@northernstaruh.example", "phone": "+86 10 8500 6014", "payment_terms": "45 days", "credit_status": "Good"},
        {"customer_id": "CUST-015", "customer_name": "Sichuan Regional Health Distributors", "customer_region": "Other Mainland China", "customer_type": "Medical Distributor", "contact_person": "Olivia Deng", "email": "olivia.deng@sichuanregionalhealth.example", "phone": "+86 28 8600 6015", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-016", "customer_name": "Yangtze Vision Clinic Network", "customer_region": "Other Mainland China", "customer_type": "Optical Clinic Chain", "contact_person": "Peter Lin", "email": "peter.lin@yangtzevision.example", "phone": "+86 27 8700 6016", "payment_terms": "30 days", "credit_status": "Good"},
        {"customer_id": "CUST-017", "customer_name": "Fujian Coastal Eye Care Group", "customer_region": "Other Mainland China", "customer_type": "Private Clinic Group", "contact_person": "Queenie Lau", "email": "queenie.lau@fujiancoastaleye.example", "phone": "+86 591 8800 6017", "payment_terms": "45 days", "credit_status": "Watch"},
    ]
    return pd.DataFrame(rows)


def write_sample_workbooks(
    output_dir: Path = SAMPLE_DATA_DIR, reference_date: date | None = None
) -> None:
    """Generate and write all five sample workbooks to output_dir."""
    if reference_date is None:
        reference_date = date.today()

    output_dir.mkdir(parents=True, exist_ok=True)

    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)
    inventory_df = generate_inventory(product_master_df)
    invoices_df = generate_invoices(reference_date)
    customers_df = generate_customers()

    product_master_df.to_excel(output_dir / "sample_product_master.xlsx", index=False)
    orders_df.to_excel(output_dir / "sample_orders.xlsx", index=False)
    inventory_df.to_excel(output_dir / "sample_inventory.xlsx", index=False)
    invoices_df.to_excel(output_dir / "sample_invoices.xlsx", index=False)
    customers_df.to_excel(output_dir / "sample_customers.xlsx", index=False)


if __name__ == "__main__":
    write_sample_workbooks()
