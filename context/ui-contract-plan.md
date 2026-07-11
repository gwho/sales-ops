# UI Contract Plan

Phase 7 deliverable (planning only — no production frontend code). Maps every future Next.js surface (route, table, KPI, badge, report card, empty/loading/error state) to a real Python output contract or an explicitly-labeled display-only derivation. Living reference, same tier as `ui-tokens.md`/`ui-rules.md` — update it whenever `src/contracts.py` or the business-module envelopes change.

Four Figma Make prototype references were inspected via the Figma MCP server during Phase 8 (they were not available when the rest of this doc was written in Phase 7). They are visual reference only — this doc, `ui-rules.md`, `ui-tokens.md`, `src/contracts.py`, and `tests/contract_fixtures.py` remain source of truth. The full classification (V1 / correction-needed / out-of-scope) is in [Figma Reference Reconciliation](#figma-reference-reconciliation) at the end of this file. Rule: Figma never introduces a table column, KPI, or badge the contracts can't back.

## Glossary

- **Status Badge** — a UI label that either comes directly from a controlled-vocabulary contract field (e.g. `PaymentAgingRow.aging_bucket`), or is derived client-side from row/list membership (e.g. "Valid" = row is in `valid_orders`). Either way it must trace to real contract data — see the [Status Badges](#status-badges) section below for the full direct/derived breakdown per workflow.
- **Derived Display Value** — a value computed client-side from existing contract fields (a group-by/sum for a chart, a label transform of an existing field) that introduces no new business logic and requires no contract change. See [Derived Display-Only Aggregates](#derived-display-only-aggregates).

These are UI-planning/process terms, not business-domain terms, so they live here rather than in root `CONTEXT.md`.

## TypeScript Interfaces

Literal `type` definitions (`code-standards.md`: prefer `type` over `interface` for data shapes/unions), copy-pasteable into `types/index.ts` in Phase 8. Snake_case fields preserved verbatim to match the JSON the Python core returns — no camelCase adapter layer decided yet.

### Order Validation

```ts
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
```

### Inventory Allocation

```ts
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
```

### Payment Aging

```ts
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
```

### Reports

```ts
export type ReportManifest = {
  report_id: string; // "rpt-{report_type}-{YYYYMMDDHHMMSS}", e.g. "rpt-order_validation-20260709091500"
  report_type: "order_validation" | "inventory_allocation" | "payment_aging";
  file_name: string; // "order_validation_report.xlsx" | "inventory_allocation_report.xlsx" | "payment_aging_report.xlsx"
  generated_at: string; // ISO datetime, second precision
  sheet_names: string[];
};
```

**Data-accuracy note:** `tests/contract_fixtures.py`'s `REPORT_MANIFEST_FIXTURES` now matches the real exporter format: `f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"` from `src/report_export.py`'s `_build_manifest()`. Use the fixture values directly for Phase 8 mock data; `tests/test_contracts.py` includes a regression assertion that each fixture ID is derived from its own `report_type` and second-precision `generated_at` timestamp.

## Route / Page Plan

Fixed 5-route set (`build-plan.md` Phase 8, `architecture.md`):

| Route | Consumes | Composes |
|---|---|---|
| `/dashboard` | All 3 summaries (when run this session) + all 3 `ReportManifest`s (when generated) | KPI strip (3 sections, independent empty states) + 3 workflow entry cards + 3 report cards + demo-mode note |
| `/order-validation` | `OrderValidationResult` | `UploadPanel` ×2, KPI strip (`ValidationSummary`), Validation Errors table, Valid Orders preview table, download action |
| `/inventory-allocation` | `InventoryAllocationResult` | `UploadPanel` ×2, KPI strip (`AllocationSummary`), Allocation Results table, Backorders table, Remaining Inventory table, Supplier Follow-up table, download action |
| `/payment-aging` | `PaymentAgingResult` | `UploadPanel` + date selector, KPI strip (`PaymentAgingSummary`), aging bucket chart, Follow-up List table, Draft Messages preview, Data Issues section, download action |
| `/reports` | All 3 `ReportManifest`s (session-derived) | 3 `ReportCard`s, one per `report_type` |

### `/dashboard` scope (confirmed decision)

Read-only aggregate landing page composed strictly from existing outputs — no persisted cross-workflow state, no new backend contract. Each summary section shows its own empty state independently if that workflow hasn't run this session.

Good V1 dashboard content: Order Validation summary tiles, Inventory Allocation summary tiles, Payment Aging summary tiles, 3 report cards (from `ReportManifest`, once generated), 3 workflow entry cards ("Validate Orders," "Allocate Inventory," "Review Payment Aging").

Explicitly avoid: a global health score, a cross-workflow risk score, a unified operations queue, historical trends — none of these have a Python source and would require persistence or new business logic.

## Table Column Plan

Every column maps to a real field. `StatusBadge` column noted where applicable.

**Validation Errors** (`ValidationErrorRow`) — Row, Order ID, SKU, Error Code, Error Message, Severity (`StatusBadge`: Error/Warning)

**Valid Orders preview** (`ValidOrderRow`) — Order ID, Order Date, Customer, Region, SKU, Product, Qty, Requested Delivery, Priority (`StatusBadge`: High/Normal/Low), Payment Terms, Sales Owner

**Allocation Results** (`AllocationResultRow`) — Order ID, Customer, SKU, Product, Requested Qty, Allocated Qty, Backorder Qty, Warehouse, Status (`StatusBadge`), Priority (`StatusBadge`), Requested Delivery

**Backorders** (`BackorderRow`) — same columns as Allocation Results (identical shape, pre-filtered to `status === "Backordered"` — no separate column plan needed)

**Remaining Inventory** (`RemainingInventoryRow`) — SKU, Warehouse, Starting Qty, Allocated Qty, Remaining Qty, Reorder Point, Reorder Alert (`StatusBadge`: derived "Below Reorder Point" label when `reorder_alert === "Yes"`)

**Supplier Follow-up** (`SupplierFollowUpRow`) — SKU, Warehouse, Remaining Qty, Reorder Point, Supplier, Lead Time (Days)

**Payment Aging rows** (`PaymentAgingRow`) — Invoice ID, Customer, Invoice Date, Due Date, Invoice Amount, Paid Amount, Outstanding Amount, Days Overdue, Aging Bucket (`StatusBadge`), Follow-up Priority (`StatusBadge`), Suggested Action

**Data Issues** (`PaymentDataIssueRow`) — Invoice ID, Customer, Error Code, Error Message, Severity (`StatusBadge`: always "Error" currently)

**Draft Messages** (`DraftMessageRow`) — Invoice ID, Customer, Outstanding Amount, Days Overdue, Message (rendered as wrapped multi-line text/textarea preview, not a single-line cell — matches how `report_export.py` applies `wrap_text` to this column)

## KPI Card Mapping

**Order Validation** (`ValidationSummary`, 6 tiles — all direct): Total Orders, Valid Orders, Invalid Orders, Duplicate Orders, Invalid SKUs, Missing Field Count.

**Inventory Allocation** (`AllocationSummary`, 5 tiles — all direct): Total Order Lines, Fully Allocated, Partially Allocated, Backordered, Low Stock SKUs.

**Payment Aging** (`PaymentAgingSummary`, mixed):
- Total Outstanding (`total_outstanding_amount`) — direct
- Overdue Amount (`overdue_amount`) — direct
- High Priority Count (`high_priority_count`) — direct
- Aging bucket chart (`aging_bucket_counts`) — direct, 5-way breakdown
- **"90+ Days Amount"** — the spec (`03_demo_payment_aging.md` §9) lists this as a 4th KPI card, but no summary field produces it: `aging_bucket_counts` is a *count* dict, not an *amount* dict. This is a **derived display-only aggregate**: sum `aging_rows[].outstanding_amount` where `aging_bucket === "90+ Days"`. See [Derived Display-Only Aggregates](#derived-display-only-aggregates).

**Dashboard aggregate strip**: the same tiles above, grouped per workflow, each group independently empty-stated if that workflow hasn't run this session.

## Status Badges

Corrected in full in `context/ui-rules.md` (see that file's Status Badges section for the canonical version this session rewrote). Summary, direct vs. derived, for all four groups — not just the two that were originally broken:

| Workflow | Direct (contract field) | Derived (client-side) |
|---|---|---|
| Order Validation | `ValidationErrorRow.severity`: Error, Warning | `Valid`, `Has Errors`, `Has Warnings` — from `valid_orders`/`errors` list membership |
| Inventory Allocation | `AllocationResultRow.status`: Fully Allocated, Partially Allocated, Backordered | `Below Reorder Point` — display label when `RemainingInventoryRow.reorder_alert === "Yes"`; `Supplier Follow-up` — from `supplier_follow_ups` list membership |
| Payment Aging | `PaymentAgingRow.aging_bucket`: 5 buckets; `PaymentAgingRow.follow_up_priority`: High/Medium/Low/Watch/None | none needed — both fields are already controlled vocab; any additional shorthand (e.g. "Paid", "Overdue") must define its exact derivation rule before use, not be assumed |
| Reports | none — no Python-tracked lifecycle | `Needs Input` → `Not Generated` → `Processing` → `Ready` — pure client session state, keyed off whether that workflow has run and its export function has been called this session |

## Report Cards

One `ReportCard` per `report_type` (`order_validation`, `inventory_allocation`, `payment_aging`) on `/reports`, mirrored on `/dashboard`.

Derived client-state model (UI-only, not Python-sourced), matching `context/ui-rules.md`'s Reports badge lifecycle:

```
Needs Input     -- underlying workflow hasn't run this session, no result envelope to export
Not Generated   -- envelope exists, export function not yet called
Processing      -- export function in flight
Ready           -- ReportManifest received; card shows file_name, sheet_names, generated_at, download action
```

An export failure reverts the card to `Not Generated` with a `BusinessErrorMessage` shown — no separate persisted error state.

Card content once `Ready`: `file_name`, `sheet_names` (as a compact list), `generated_at` (formatted), download action.

## Empty / Loading / Error States

Exact copy from each spec's own §UI-requirements section — not invented:

**Order Validation** (`01_demo_order_validation.md` §9)
- Empty: *"Upload an orders file and product master file to begin validation."*
- Error (missing columns): *"The uploaded file is missing required columns: [column list]. Please check the sample file."*

**Inventory Allocation** (`02_demo_inventory_allocation.md` §8)
- Empty: *"Upload validated orders and inventory files to run allocation."*
- Processing: *"Allocating inventory by priority, delivery date, and stock availability..."*

**Payment Aging** (`03_demo_payment_aging.md` §9)
- Empty: *"Upload an invoice/payment file to generate an aging report."*
- Error: invalid due dates or amounts surface in a `Data Issues` section (i.e. `PaymentDataIssueRow` rows), not a blocking error banner.

**Reports** — no spec-defined copy exists (no source file). Use `ui-rules.md`'s bad/good error pattern as the template if a report export fails: never a raw exception, always a business-readable sentence.

**General error copy pattern** (`ui-rules.md`): bad — `KeyError: 'sku'`; good — *"The uploaded order file is missing the required column: SKU. Please use the sample file and try again."*

## Derived Display-Only Aggregates

Each entry: source rows, source fields, grouping rule. No new Python fields, no new business logic — client-side aggregation only.

| Chart / value | Source | Rule |
|---|---|---|
| Backordered Qty by SKU | `InventoryAllocationResult.allocation_results` | group by `sku`, sum `backorder_qty` where `status === "Backordered"` |
| Allocation status mix | `InventoryAllocationResult.allocation_results` | count rows by `status` |
| Aging bucket distribution | `PaymentAgingSummary.aging_bucket_counts` | direct — not actually derived, listed here only for completeness since it's chart-shaped |
| Overdue amount by customer | `PaymentAgingResult.aging_rows` | group by `customer_name`, sum `outstanding_amount` where `days_overdue > 0` |
| "90+ Days Amount" KPI | `PaymentAgingResult.aging_rows` | sum `outstanding_amount` where `aging_bucket === "90+ Days"` |
| "Gap to Reorder Point" (Dashboard Inventory Shortage Alerts) | `InventoryAllocationResult.supplier_follow_ups` | `reorder_point - remaining_qty`, per row. Display label only — never call this "suggested reorder quantity" (that would be a new business recommendation the Python core doesn't produce; `SupplierFollowUpRow` has no such field). |
| Outstanding amount by aging bucket (Dashboard `VerticalBucketBarChart`) | `PaymentAgingResult.aging_rows` | group by `aging_bucket` (fixed order: Current, 1-30 Days, 31-60 Days, 61-90 Days, 90+ Days), sum `outstanding_amount`. Distinct from `PaymentAgingSummary.aging_bucket_counts`, which is a *count* per bucket, not an amount — same relationship as the existing "90+ Days Amount" KPI to that same count dict. |

Boundary: aggregation for visualization is fine; new business interpretation is not. No risk score, forecast, recommendation, or priority calculation that the Python core doesn't already produce.

## Figma Reference Reconciliation

Inspected in Phase 8 via the Figma MCP server (remote `mcp.figma.com`) — four Figma Make prototypes, read as source via `get_design_context` (Make path, `nodeId="0:1"`). These are AI-generated visual prototypes, useful for layout/component vocabulary only. Every element below is classified against the real contracts; anything that contradicts a contract is a **correction**, not a spec change. Phase 9 must build from the corrected version, not copy the Figma output.

References: *Design Inventory Allocation Screen*, *Overview Dashboard Screen*, *Inventory Allocation Screen Design*, *Payment Aging Screen Design*.

### V1 — safe visual reference (maps to already-planned components)

- KPI/metric card (label + big number + icon chip) → `MetricCard`.
- Filter bar (search + selects + clear) → generic pattern, no new component.
- Data table with sortable headers, zebra rows, status badges → `DataTable` + `StatusBadge`.
- Per-workflow stepper (client-only progress) → `WorkflowStepper`.
- Aging-bucket cards, supplier follow-up side panel, draft-reminder panel *layout* → inform panel treatments around `ReportCard`/tables.

### Corrections required before Phase 9 builds from these

- **Inventory Allocation priority vocab.** Figma uses `Critical | High | Medium | Low`. Real vocab (`inventory_allocation.py` `PRIORITY_RANK`) is `High | Normal | Low` — no "Critical"; "Medium" is really "Normal".
- **Allocation `status`.** Figma treats `Invalid SKU` and `Supplier Follow-up` as status values. Real `AllocationResultRow.status` has exactly three: `Fully Allocated | Partially Allocated | Backordered`. Invalid SKUs never reach allocation (caught upstream by OV-003). "Supplier Follow-up" is a separate list (`supplier_follow_ups`), never a status-column value.
- **Supplier Follow-up fields.** Figma invents `shortageQty`, `suggestedReorderQty`, `followUpPriority`. Real `SupplierFollowUpRow` = `sku`, `warehouse`, `remaining_qty`, `reorder_point`, optional `supplier_name`, optional `lead_time_days`. No priority, no reorder-qty recommendation — those are new business rules, out of scope without an ADR.
- **Payment Aging priority.** Figma: `High | Medium | Low | "—"`. Real `follow_up_priority`: `High | Medium | Low | Watch | None`. Include "Watch"; render "None", not "—".
- **Payment Aging high-priority threshold.** Figma's rules panel says **$40,000**. Real threshold (`payment_aging.py`) is **$50,000** (`outstanding_amount >= 50000` or `days_overdue > 60`). Any rules-explainer must use the real number.
- **Draft reminders.** Figma composes the email client-side from raw fields. The core already emits the finished multi-line `DraftMessageRow.message_text` — Phase 9 renders that verbatim, no React templating.
- **Dashboard nav.** Figma shows an 8-item ERP-style mega-nav (Overview, Orders, Invoices, Inventory, Purchase Orders, Customers, Reports, Analytics). Real route set is the fixed 5 (`/dashboard`, `/order-validation`, `/inventory-allocation`, `/payment-aging`, `/reports`). The extras have no contract behind them — exactly the mega-nav `CLAUDE.md` warns against.
- **Dashboard trends & status mix.** Figma shows `+12.4%`/`−18.2%` deltas and statuses like "On Hold"/"Pending Review"/"Cancelled". No time-series/history exists in the core (single-run snapshot), and those statuses aren't on any contract — out of scope.

### Chrome pattern

Only the Dashboard prototype uses the sidebar nav `ui-rules.md`/`CLAUDE.md` mandate. The Inventory prototypes use a top-nav+stepper; Payment Aging uses a bare top bar. The existing sidebar decision wins — Phase 9's `AppShell`/`SidebarNav` is uniform across all 5 routes. The other prototypes remain reference for their *content* (stepper, filter bar, upload panel), not their chrome.

### Tokens

All four prototypes use raw Tailwind palette classes and ad-hoc hex (`bg-red-100`, `#0f4c81`, …). Expected from AI output, but a hard reminder: Phase 9 routes every color through `ui-tokens.md` semantic tokens — never copy Figma color classes verbatim.
