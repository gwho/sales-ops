/**
 * Output-contract types for the Sales Admin Automation Toolkit UI.
 *
 * Copied verbatim from context/ui-contract-plan.md, which is the source of
 * truth (mirroring src/contracts.py + the three business-module result
 * envelopes). snake_case field names are intentional — they match the JSON the
 * Python core emits. No camelCase adapter (decided in Phase 7); if that changes,
 * update ui-contract-plan.md first, then regenerate this file.
 */

// ─── Order Validation ────────────────────────────────────────────────────────

export type ValidationSummary = {
  total_orders: number;
  valid_orders: number;
  invalid_orders: number;
  duplicate_orders: number;
  invalid_skus: number;
  missing_field_count: number;
};

export type ValidationErrorRow = {
  row_number: number;
  order_id?: string;
  sku?: string;
  error_code: string; // e.g. "OV-001", "OV-003-UNKNOWN_SKU", "OV-005-DELIVERY_BEFORE_ORDER"
  error_message: string;
  severity: "Error" | "Warning";
};

export type ValidOrderRow = {
  order_id: string;
  order_date: string; // ISO date
  customer_name: string;
  customer_region: string;
  sku: string;
  product_name?: string;
  quantity: number;
  requested_delivery_date: string; // ISO date
  priority: "High" | "Normal" | "Low";
  payment_terms: string;
  sales_owner?: string;
};

export type OrderValidationResult = {
  summary: ValidationSummary;
  valid_orders: ValidOrderRow[];
  errors: ValidationErrorRow[];
};

// ─── Inventory Allocation ────────────────────────────────────────────────────

export type AllocationSummary = {
  total_order_lines: number;
  fully_allocated_count: number;
  partially_allocated_count: number;
  backordered_count: number;
  low_stock_sku_count: number;
};

export type AllocationResultRow = {
  order_id: string;
  customer_name: string;
  sku: string;
  product_name?: string;
  requested_qty: number;
  allocated_qty: number;
  backorder_qty: number;
  warehouse: string; // "" only when the SKU has zero inventory rows anywhere
  status: "Fully Allocated" | "Partially Allocated" | "Backordered";
  priority: "High" | "Normal" | "Low";
  requested_delivery_date: string; // ISO date
};

// Same shape as AllocationResultRow — the Backorders sheet/table is
// allocation_results filtered to status === "Backordered". No new fields.
export type BackorderRow = AllocationResultRow;

export type RemainingInventoryRow = {
  sku: string;
  warehouse: string;
  starting_available_qty: number;
  allocated_qty: number;
  remaining_qty: number;
  reorder_point?: number;
  reorder_alert: "Yes" | "No";
};

export type SupplierFollowUpRow = {
  sku: string;
  warehouse: string;
  remaining_qty: number;
  reorder_point: number; // required here (only ever emitted when known), unlike RemainingInventoryRow
  supplier_name?: string;
  lead_time_days?: number;
};

export type InventoryAllocationResult = {
  summary: AllocationSummary;
  allocation_results: AllocationResultRow[];
  backorders: BackorderRow[];
  remaining_inventory: RemainingInventoryRow[];
  supplier_follow_ups: SupplierFollowUpRow[];
};

// ─── Payment Aging ───────────────────────────────────────────────────────────

export type PaymentAgingSummary = {
  total_invoices: number;
  total_outstanding_amount: number;
  overdue_amount: number;
  high_priority_count: number;
  // Always has all 5 keys, even when a bucket has zero rows.
  aging_bucket_counts: Record<
    "Current" | "1-30 Days" | "31-60 Days" | "61-90 Days" | "90+ Days",
    number
  >;
};

export type PaymentAgingRow = {
  invoice_id: string;
  customer_name: string;
  invoice_date: string; // ISO date
  due_date: string; // ISO date
  invoice_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  days_overdue: number; // signed — negative means not yet due
  aging_bucket: "Current" | "1-30 Days" | "31-60 Days" | "61-90 Days" | "90+ Days";
  follow_up_priority: "High" | "Medium" | "Low" | "Watch" | "None";
  suggested_action: string; // one of 5 fixed strings keyed by follow_up_priority
};

export type PaymentDataIssueRow = {
  invoice_id?: string;
  customer_name?: string;
  error_code: string; // "PA-006" | "PA-007" currently
  error_message: string;
  severity: "Error"; // always "Error" in the current implementation
};

export type DraftMessageRow = {
  invoice_id: string;
  customer_name: string;
  outstanding_amount: number;
  days_overdue: number;
  message_text: string; // multi-line — render with wrap/textarea, not a plain table cell
};

export type PaymentAgingResult = {
  summary: PaymentAgingSummary;
  aging_rows: PaymentAgingRow[];
  data_issues: PaymentDataIssueRow[];
  draft_messages: DraftMessageRow[];
};

// ─── Reports ─────────────────────────────────────────────────────────────────

export type ReportManifest = {
  report_id: string; // "rpt-{report_type}-{YYYYMMDDHHMMSS}", e.g. "rpt-order_validation-20260709091500"
  report_type: "order_validation" | "inventory_allocation" | "payment_aging";
  file_name: string; // e.g. "order_validation_report.xlsx"
  generated_at: string; // ISO datetime, second precision
  sheet_names: string[];
};
