# Library Docs

Project-specific library guidance for Sales Admin Automation Toolkit.

Before adding a third-party library, check whether a local skill or MCP tool provides current docs. Do not rely only on training data for framework APIs.

## Python

Use Python for the first implementation milestone.

Rules:

- Keep business logic in `src/`.
- Keep tests in `tests/`.
- Keep sample data generation deterministic.
- Use fictional records only.
- Avoid introducing web framework concerns before the business modules are stable.

## pandas

Use pandas for spreadsheet-like transformations:

- required-column checks
- row normalization
- validation output tables
- allocation result tables
- payment aging calculations
- summary metrics

Rules:

- Validate required columns before accessing them.
- Normalize blanks consistently.
- Preserve source row references for user-facing error rows.
- Avoid chained assignment ambiguity.
- Keep DataFrame columns business-readable and stable.

## openpyxl

Use openpyxl for writing `.xlsx` report workbooks when formatting or multiple sheets matter.

Rules:

- Use business-readable sheet names.
- Include summary and detail sheets.
- Keep report generation separate from business calculations.
- Tests should verify expected sheet names and representative cell values.

## pytest

Use pytest for business-rule coverage before UI work.

Required test areas:

- Order validation rules
- Inventory allocation ordering and stock depletion
- Payment aging buckets and priority
- Missing-column handling
- Excel report sheet creation

## Future FastAPI

Use FastAPI only after the Python core is reviewed.

Planned endpoints:

```text
POST /api/orders/validate
POST /api/inventory/allocate
POST /api/payments/aging
GET  /api/reports/{report_id}
```

Rules:

- Keep route handlers thin.
- Call Python business modules from route handlers.
- Return JSON matching stable contracts.
- Return downloadable Excel files for reports.
- Never expose Python tracebacks to users.

## Future Next.js

Use Next.js App Router for the polished dashboard after Python rule tests and Excel report structure tests pass.

Rules:

- Read installed Next.js docs under `node_modules/next/dist/docs/` before implementing framework-specific behavior.
- Use Server Components by default.
- Use Client Components only for interactive widgets such as filters, upload controls, tabs, and table state.
- Keep route files thin.
- Do not add auth, middleware/proxy logic, or database routes in the first UI milestone.

## Tailwind CSS 3.4

The future Next.js UI must use Tailwind CSS 3.4. Do not upgrade to Tailwind v4.

Rules:

- Define project colors as CSS variables and expose them through `tailwind.config.ts`.
- Components must use semantic project tokens, not raw Tailwind palette classes.
- No hardcoded hex values in JSX.
- Use consistent spacing, radius, and status tokens from `ui-tokens.md`.

## shadcn/ui

Use shadcn/ui for future UI primitives when useful:

- Button
- Card
- Input
- Badge
- Table
- Tabs
- Dropdown/select

Rules:

- Keep project-specific wrappers in `components/workflow/`, `components/tables/`, or `components/layout/`.
- Do not let generated shadcn code introduce raw color classes that conflict with tokens.
- Do not make every page a collection of unstructured shadcn snippets; extract reusable components.

## TanStack Table

Use for operations tables when sorting, filtering, pagination, or column definitions become non-trivial.

Rules:

- Column labels must use business language.
- Status cells should render `StatusBadge`.
- Empty states must be explicit.
- Table columns must map to Python output contracts.

## Recharts

Use only for simple charts that explain business outcomes:

- Order status breakdown
- Payment aging buckets
- Backordered quantity by SKU
- Follow-up priority count

Avoid decorative charts that do not support the demo narrative.

## Figma / MCP Design Inputs

The prompt packs in `ui_reference_to_figma_workflow/` and `ui_prompts_for_agents_mcp/` define a useful workflow:

1. Generate or collect references.
2. Inspect Figma frames through MCP if available.
3. Produce screen inventory, component mapping, token extraction, data requirements, and scope-control notes.
4. Confirm every UI surface maps to a Python output.
5. Implement approved scope only.

Figma designs are not source of truth for product scope. The context files, specs, and Python output contracts are.
