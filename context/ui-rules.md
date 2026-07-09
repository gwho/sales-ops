# UI Rules

## Current UI Status

The polished UI is not the first implementation milestone. Build and test the Python outputs first, then design the UI around those outputs.

UI work before the Python core is stable should stay at planning level:

- reference collection
- Figma/Figma MCP inspection
- low-fidelity wireframes
- component inventory
- table-column planning
- TypeScript contract planning

Do not spend time polishing final screens or writing production frontend code until validation, allocation, payment aging, and report exports pass their test gates.

## Visual Direction

The eventual UI should look like a clean internal B2B operations dashboard. It should feel credible for sales admin, operations, trading, logistics, and supply-chain workflows.

Use:

- Light theme first
- Sidebar navigation
- White cards on soft gray page background
- Blue accent for primary actions
- Green, amber, red, and neutral status badges
- Dense but readable tables
- Minimal, useful charts
- Business-readable copy

Avoid:

- Dark crypto-dashboard styling
- Decorative gradients as main surfaces
- Generic AI-dashboard copy
- Too many charts
- ERP-style mega navigation
- Raw technical errors

## Future Layout

- Desktop-first dashboard with left sidebar and top header.
- Main content should use a constrained, readable width while still allowing wide tables.
- Use `gap-6` between major page sections.
- Use card sections for KPIs, upload panels, charts, rules panels, and report cards.
- Do not nest cards more than one level deep.

## Future Pages

1. Overview Dashboard
2. Order Validation
3. Inventory Allocation
4. Payment Aging
5. Reports

Every page must map to Python output contracts. Do not invent KPI cards or table columns that the Python core cannot produce.

## Core Components

Required reusable components for the future Next.js phase:

- `AppShell`
- `SidebarNav`
- `TopHeader`
- `MetricCard`
- `WorkflowStepper`
- `UploadPanel`
- `StatusBadge`
- `DataTable`
- `ReportCard`
- `EmptyState`
- `LoadingState`
- `BusinessErrorMessage`

Use shadcn/ui primitives where they help, but keep project-specific patterns in project components.

## Tables

Tables are the most important UI surface.

Rules:

- Columns must map to Python outputs.
- Visible column headers.
- Compact row spacing without crowding.
- Search/filter controls where useful.
- Pagination for long tables.
- Status badges in status columns.
- Business-readable suggested action columns.
- No raw object dumps or developer labels.

Important table sets:

- Validation errors
- Valid orders preview
- Allocation results
- Backorders and supplier follow-up
- Remaining inventory
- Payment aging rows
- Draft reminder messages
- Export history

## Upload Panels

Upload panels in the future UI should show:

- Accepted file type
- Required columns
- Sample template action
- Selected filename
- Business-readable validation message

Real file parsing belongs in the Python/FastAPI layer, not React components.

## Status Badges

Every badge label is either **direct** (comes verbatim from a controlled-vocabulary Python contract field) or **derived** (computed client-side from row/list membership or a display transform of a direct field — never a new business rule). Full field-level detail and TypeScript types: `context/ui-contract-plan.md`.

Order validation:

- direct (`ValidationErrorRow.severity`): `Error`, `Warning`
- derived (list membership in `valid_orders`/`errors`): `Valid`, `Has Errors`, `Has Warnings`

(The previous list — `Missing Field`, `Invalid SKU`, `Duplicate Order`, `Invalid Quantity`, `Needs Review` — mistook error *categories* for row statuses. Those categories are `error_code`/`error_message`, shown verbatim in the error table; a row doesn't need a badge duplicating them.)

Inventory allocation:

- direct (`AllocationResultRow.status`): `Fully Allocated`, `Partially Allocated`, `Backordered`
- direct/derived (`RemainingInventoryRow.reorder_alert`, `Yes`/`No`): render as `Below Reorder Point` only when `reorder_alert = "Yes"` — this is a display label for the field, not a separate vocabulary
- derived (list membership in `supplier_follow_ups`): `Supplier Follow-up`

Payment aging:

- direct (`PaymentAgingRow.aging_bucket`): `Current`, `1-30 Days`, `31-60 Days`, `61-90 Days`, `90+ Days`
- direct (`PaymentAgingRow.follow_up_priority`): `High`, `Medium`, `Low`, `Watch`, `None`

(The previous list — `Overdue`, `Due Soon`, `High Priority`, `Paid` — was an unexplained ad hoc simplification never actually derived from these two fields. If a shorthand label like `Paid` is still wanted, its exact derivation rule must be defined explicitly — e.g. `outstanding_amount <= 0` — before use.)

Reports — client-side session state only, not Python-sourced (no report has a persisted lifecycle; a workbook exists only once its export function has been called this session). Lifecycle order:

- `Needs Input` — the underlying workflow hasn't been run this session, so there's no result envelope to export yet
- `Not Generated` — the workflow has run and an envelope exists, but the export function hasn't been called yet
- `Processing` — the export function is in flight
- `Ready` — `ReportManifest` received; card shows `file_name`, `sheet_names`, `generated_at`, and a download action

An export failure reverts the card to `Not Generated` with a `BusinessErrorMessage` shown, rather than adding a fifth persisted state.

## Error Messages

Bad:

```text
KeyError: 'sku'
```

Good:

```text
The uploaded order file is missing the required column: SKU. Please use the sample template and try again.
```

## Demo Mode

Every page should make it clear the project uses fictional sample data. A small top-header label or page-level note is enough.

## Figma and MCP Workflow

If Figma designs or screenshots are used:

1. Inspect and critique the design before coding.
2. Map screens to routes and reusable components.
3. Extract design tokens and table patterns.
4. Classify design elements as V1, V1.5, V2, or remove.
5. Confirm every UI element maps to Python output contracts.

Figma output is guidance. The business workflow, specs, and Python output contracts take precedence.
