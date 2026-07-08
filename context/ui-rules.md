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

Use consistent labels:

Order validation:

- Valid
- Missing Field
- Invalid SKU
- Duplicate Order
- Invalid Quantity
- Needs Review

Inventory allocation:

- Fully Allocated
- Partially Allocated
- Backordered
- Below Reorder Point
- Supplier Follow-up

Payment aging:

- Current
- Due Soon
- Overdue
- High Priority
- Paid

Reports:

- Ready
- Not Generated
- Processing
- Needs Input

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
