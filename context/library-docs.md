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

Use FastAPI only after the Python core is reviewed. Resolved in a `/grilling` planning session before Phase 10 implementation; the stateless architecture behind these endpoints is recorded in `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md` — see that ADR before changing the shape below.

Planned endpoints:

```text
POST /api/orders/validate
POST /api/orders/validate/report

POST /api/inventory/allocate
POST /api/inventory/allocate/report

POST /api/payments/aging
POST /api/payments/aging/report

GET  /api/templates/{template_name}
```

`GET /api/reports/{report_id}` is not used — see ADR 0006. Each `.../report` endpoint re-accepts the same source file(s)/parameters as its non-report counterpart and recomputes server-side rather than accepting a client-supplied result. Inventory allocation's endpoints take `orders_file`, `product_master_file`, and `inventory_file`, and run `validate_orders` internally before `allocate_inventory`, since `allocate_inventory` requires already-valid orders. Payment aging's endpoints take `invoices_file` plus a required `as_of_date` form field (`YYYY-MM-DD`) — the client always sends it explicitly; the Python function's `as_of_date=None` fallback stays for direct/test callers only.

`GET /api/templates/{template_name}` serves the existing committed `sample_data/*.xlsx` files as downloads (a "Sample File," not a generated template — see `CONTEXT.md`) through an allowlisted name→path mapping, never a raw filesystem path. `sample_customers.xlsx` is not exposed here — it's reference-only and unused by any live workflow.

Rules:

- Keep route handlers thin. Call the tested Python business modules from route handlers; never duplicate business rules in a route.
- Use sync `def` path operations (not `async def`) for handlers that call blocking pandas/openpyxl code, per the `fastapi` skill's guidance.
- Use `Annotated[UploadFile, File()]` and `Annotated[str, Form()]` for upload/form parameters.
- Return JSON matching stable Output Contracts for the three workflow endpoints; return `.xlsx` bytes directly (`Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `Content-Disposition: attachment`) for the three report endpoints, with `X-Report-Id` / `X-Generated-At` headers for download metadata. Don't force `sheet_names` into a header unless the UI actually needs it.
- Uploaded files must be `.xlsx`. Check the filename extension (mandatory) and content-type (advisory) before parsing; reject with `400` otherwise.
- Every failure response uses a uniform `{ "detail": "<business-readable message>" }` shape — never a raw traceback, pandas/openpyxl exception, or FastAPI's default list-shaped validation error. Add a `RequestValidationError` handler that normalizes validation failures into a single string `detail`.
- Known business/input failures (`MissingColumnsError`, `InvalidInventoryDataError`, `InvalidOrderDataError`, missing/malformed `as_of_date`, missing file, wrong extension, unreadable/corrupt `.xlsx`) return `400`. Truly unexpected failures return a generic `500` message — never expose Python tracebacks to users.
- No custom upload size limit in Phase 10 (demo-scale files only); revisit if this is ever deployed beyond a portfolio demo.
- The frontend's `ReportLifecycleState` (`Needs Input` / `Not Generated` / `Processing` / `Ready`) does not gain an `Error` state. A failed request renders `BusinessErrorMessage` in place of the `ReportCard`/`DataTable`, at the page level.

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
