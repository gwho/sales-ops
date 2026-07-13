"""JSON-serializable output-contract shapes shared across business modules and the future API/UI boundary."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class ValidationSummary(TypedDict):
    total_orders: int
    valid_orders: int
    invalid_orders: int
    duplicate_orders: int
    invalid_skus: int
    missing_field_count: int


class ValidationErrorRow(TypedDict):
    row_number: int
    order_id: NotRequired[str]
    sku: NotRequired[str]
    error_code: str
    error_message: str
    severity: str


class ValidOrderRow(TypedDict):
    order_id: str
    order_date: str
    customer_name: str
    customer_region: str
    sku: str
    product_name: NotRequired[str]
    quantity: int
    requested_delivery_date: str
    priority: str
    payment_terms: str
    sales_owner: NotRequired[str]


class AllocationSummary(TypedDict):
    total_order_lines: int
    fully_allocated_count: int
    partially_allocated_count: int
    backordered_count: int
    low_stock_sku_count: int


class AllocationResultRow(TypedDict):
    order_id: str
    customer_name: str
    sku: str
    product_name: NotRequired[str]
    requested_qty: int
    allocated_qty: int
    backorder_qty: int
    warehouse: str
    status: str
    priority: str
    requested_delivery_date: str


class BackorderRow(AllocationResultRow):
    """Same shape as AllocationResultRow — the Backorders sheet is that table filtered to status=Backordered."""


class RemainingInventoryRow(TypedDict):
    sku: str
    warehouse: str
    starting_available_qty: int
    allocated_qty: int
    remaining_qty: int
    reorder_point: NotRequired[int]
    reorder_alert: str


class SupplierFollowUpRow(TypedDict):
    sku: str
    warehouse: str
    remaining_qty: int
    reorder_point: int
    supplier_name: NotRequired[str]
    lead_time_days: NotRequired[int]


class PaymentAgingSummary(TypedDict):
    total_invoices: int
    total_outstanding_amount: float
    overdue_amount: float
    high_priority_count: int
    aging_bucket_counts: dict[str, int]


class PaymentAgingRow(TypedDict):
    invoice_id: str
    customer_name: str
    invoice_date: str
    due_date: str
    invoice_amount: float
    paid_amount: float
    outstanding_amount: float
    days_overdue: int
    aging_bucket: str
    follow_up_priority: str
    suggested_action: str


class PaymentDataIssueRow(TypedDict):
    invoice_id: NotRequired[str]
    customer_name: NotRequired[str]
    error_code: str
    error_message: str
    severity: str


class DraftMessageRow(TypedDict):
    invoice_id: str
    customer_name: str
    outstanding_amount: float
    days_overdue: int
    message_text: str


class ReportManifest(TypedDict):
    report_id: str
    report_type: str
    file_name: str
    generated_at: str
    sheet_names: list[str]


# Version of each workflow type's persisted Output Contract shape (see ADR 0007).
# Bump the relevant entry whenever OrderValidationResult, InventoryAllocationResult,
# or PaymentAgingResult's field shape changes — this is what lets the dashboard read
# path detect and discard stale saved rows instead of serving a shape the frontend
# no longer expects.
CONTRACT_SCHEMA_VERSIONS: dict[str, int] = {
    "order_validation": 1,
    "inventory_allocation": 1,
    "payment_aging": 1,
}
