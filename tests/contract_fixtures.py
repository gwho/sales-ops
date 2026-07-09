"""Realistic example values for each Phase 1 output-contract family (Contract Fixtures).

Hand-authored, not computed by src/sample_data.py or any business-rule module —
order_validation.py, inventory_allocation.py, and payment_aging.py don't exist
until Phases 3-5. These only prove the contract shapes can hold believable demo
data; they are not evidence that any business rule is implemented correctly.
"""

from __future__ import annotations

from src.contracts import (
    AllocationResultRow,
    AllocationSummary,
    BackorderRow,
    DraftMessageRow,
    PaymentAgingRow,
    PaymentAgingSummary,
    PaymentDataIssueRow,
    RemainingInventoryRow,
    ReportManifest,
    SupplierFollowUpRow,
    ValidationErrorRow,
    ValidationSummary,
    ValidOrderRow,
)

VALIDATION_SUMMARY_FIXTURE: ValidationSummary = {
    "total_orders": 12,
    "valid_orders": 9,
    "invalid_orders": 3,
    "duplicate_orders": 2,
    "invalid_skus": 1,
    "missing_field_count": 0,
}

VALIDATION_ERROR_ROW_FIXTURE: ValidationErrorRow = {
    "row_number": 11,
    "order_id": "SO-2026-009",
    "sku": "MED-LENS-999",
    "error_code": "OV-003",
    "error_message": "SKU does not exist in product master",
    "severity": "Error",
}

VALID_ORDER_ROW_FIXTURE: ValidOrderRow = {
    "order_id": "SO-2026-006",
    "order_date": "2026-07-03",
    "customer_name": "Golden Harbor Logistics",
    "customer_region": "Hong Kong",
    "sku": "OFF-CHAIR-006",
    "product_name": "Ergonomic Office Chair",
    "quantity": 15,
    "requested_delivery_date": "2026-07-18",
    "priority": "Normal",
    "payment_terms": "30 days",
    "sales_owner": "Wendy",
}

ALLOCATION_SUMMARY_FIXTURE: AllocationSummary = {
    "total_order_lines": 9,
    "fully_allocated_count": 7,
    "partially_allocated_count": 2,
    "backordered_count": 0,
    "low_stock_sku_count": 1,
}

ALLOCATION_RESULT_ROW_FIXTURE: AllocationResultRow = {
    "order_id": "SO-2026-008",
    "customer_name": "Silver Oak Supplies",
    "sku": "MED-LENS-001",
    "product_name": "Optical Lens Kit",
    "requested_qty": 25,
    "allocated_qty": 20,
    "backorder_qty": 5,
    "warehouse": "HK Warehouse",
    "status": "Partially Allocated",
    "priority": "High",
    "requested_delivery_date": "2026-07-14",
}

BACKORDER_ROW_FIXTURE: BackorderRow = {
    "order_id": "SO-2026-012",
    "customer_name": "Formosa Industrial Group",
    "sku": "IND-PUMP-005",
    "product_name": "Hydraulic Pump Unit",
    "requested_qty": 6,
    "allocated_qty": 0,
    "backorder_qty": 6,
    "warehouse": "HK Warehouse",
    "status": "Backordered",
    "priority": "Normal",
    "requested_delivery_date": "2026-07-28",
}

REMAINING_INVENTORY_ROW_FIXTURE: RemainingInventoryRow = {
    "sku": "MED-LENS-001",
    "warehouse": "HK Warehouse",
    "starting_available_qty": 20,
    "allocated_qty": 20,
    "remaining_qty": 0,
    "reorder_point": 5,
    "reorder_alert": "Yes",
}

SUPPLIER_FOLLOW_UP_ROW_FIXTURE: SupplierFollowUpRow = {
    "sku": "MED-LENS-001",
    "warehouse": "HK Warehouse",
    "remaining_qty": 0,
    "reorder_point": 5,
    "supplier_name": "Vista Optics Supply",
    "lead_time_days": 18,
}

PAYMENT_AGING_SUMMARY_FIXTURE: PaymentAgingSummary = {
    "total_invoices": 10,
    "total_outstanding_amount": 165000.0,
    "overdue_amount": 111000.0,
    "high_priority_count": 1,
    "aging_bucket_counts": {
        "Current": 2,
        "1-30 Days": 3,
        "31-60 Days": 2,
        "61-90 Days": 1,
        "90+ Days": 0,
    },
}

PAYMENT_AGING_ROW_FIXTURE: PaymentAgingRow = {
    "invoice_id": "INV-2026-001",
    "customer_name": "Bright Medical Trading Ltd",
    "invoice_date": "2026-03-31",
    "due_date": "2026-04-30",
    "invoice_amount": 58000.00,
    "paid_amount": 0.0,
    "outstanding_amount": 58000.00,
    "days_overdue": 70,
    "aging_bucket": "61-90 Days",
    "follow_up_priority": "High",
    "suggested_action": "Call or email customer urgently",
}

PAYMENT_DATA_ISSUE_ROW_FIXTURE: PaymentDataIssueRow = {
    "invoice_id": "INV-2026-009",
    "customer_name": "Formosa Industrial Group",
    "error_code": "PA-006",
    "error_message": "Due date is missing",
    "severity": "Error",
}

DRAFT_MESSAGE_ROW_FIXTURE: DraftMessageRow = {
    "invoice_id": "INV-2026-001",
    "customer_name": "Bright Medical Trading Ltd",
    "outstanding_amount": 58000.00,
    "days_overdue": 70,
    "message_text": (
        "Dear Bright Medical Trading Ltd,\n\n"
        "Hope you are well. We would like to follow up on invoice INV-2026-001, "
        "with an outstanding amount of HKD 58,000.00, which is currently 70 days overdue.\n\n"
        "Please let us know the expected payment status or if any further information "
        "is required from our side.\n\nThank you."
    ),
}

REPORT_MANIFEST_FIXTURES: list[ReportManifest] = [
    {
        "report_id": "rpt-order-validation-20260709-001",
        "report_type": "order_validation",
        "file_name": "order_validation_report.xlsx",
        "generated_at": "2026-07-09T09:15:00",
        "sheet_names": ["Summary", "Valid Orders", "Validation Errors", "Original Orders"],
    },
    {
        "report_id": "rpt-inventory-allocation-20260709-001",
        "report_type": "inventory_allocation",
        "file_name": "inventory_allocation_report.xlsx",
        "generated_at": "2026-07-09T09:20:00",
        "sheet_names": [
            "Allocation Summary",
            "Allocation Results",
            "Backorders",
            "Remaining Inventory",
            "Supplier Follow-up",
        ],
    },
    {
        "report_id": "rpt-payment-aging-20260709-001",
        "report_type": "payment_aging",
        "file_name": "payment_aging_report.xlsx",
        "generated_at": "2026-07-09T09:25:00",
        "sheet_names": [
            "Aging Summary",
            "Follow-up List",
            "All Invoices with Aging",
            "Data Issues",
            "Draft Messages",
        ],
    },
]
