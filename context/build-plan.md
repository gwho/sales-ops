# Build Plan

## Principle

Build the **Python business-rule core first**, then build the polished Next.js dashboard on top of stable outputs.

The portfolio value is: clear sales admin workflows, tested Excel automation, and a professional UI that presents real business-rule results. Do not spend the first implementation milestone on UI polish before the substantive Python automation exists.

Keep scope mechanical: implement only V1 or unlabeled rules in the three in-scope demo specs. Optional/V1.5/V2 rules and the CRM Cleaner module require a new ADR before implementation.

Use two separate gates:

- **UI planning gate:** Phase 7 may start after Phase 2, because contracts and representative fixtures are enough for wireframes, route planning, table mapping, and Figma/MCP review.
- **UI implementation gate:** Phase 8 must wait until Phases 3-6 pass their required tests. No real Next.js code before the Python rule tests and Excel report structure tests are green.

## Phase 0 - Planning Reset

- [x] Rewrite all context files for Sales Admin Automation Toolkit.
- [x] Add root `CONTEXT.md` glossary.
- [x] Add ADRs for the initial UI-first decisions.
- [x] Mark old JobPilot context as superseded.
- [x] Supersede UI-first sequence with ADR 0003: Python core before polished UI.

## Phase 1 - Python Project Foundation

Create a Python-first project structure, plus the cross-cutting infrastructure every later phase depends on.

Tooling and scaffolding conventions are locked in `docs/adr/0004-phase-1-python-tooling.md`: Python 3.12 (pinned via `.python-version`), `pyproject.toml` + `uv` (no `requirements.txt`), pytest config under `[tool.pytest.ini_options]` in `pyproject.toml`, and a README documenting the `uv sync` / `uv run pytest` workflow only.

Includes:

- Python project config: `pyproject.toml`, `.python-version` (3.12), `uv.lock`
- `src/` package containing only `__init__.py`, `excel_io.py`, `contracts.py` - no placeholder files for later-phase modules (see ADR 0004 §4)
- `tests/` package containing only `test_excel_io.py`, `test_contracts.py`
- `sample_data/` folder (empty; population is Phase 2)
- pytest configuration in `pyproject.toml` (`testpaths`, `pythonpath`, `addopts`); function-based tests, `test_*.py` files, `test_<behavior>` names, no coverage threshold yet
- README setup notes documenting `uv sync` and `uv run pytest`
- `src/excel_io.py`
  - load Excel helper
  - required-column validation helper
  - consistent missing-column error shape
- `src/contracts.py`
  - `TypedDict` definitions for the output families listed in `context/architecture.md` ("Python Output Contracts")
  - dictionary-shaped by design, since the eventual FastAPI/Next.js boundary is JSON, not dataclasses
  - no business calculations
  - fields follow the field scope boundary in `context/architecture.md`: only fields the corresponding workflow spec explicitly defines (e.g. `suggested_action` on `PaymentAgingRow` but not `AllocationResultRow`) - contracts are allowed to be asymmetric across families

Excludes:

- order validation rules
- allocation rules
- payment aging rules
- sample workbook generation (Phase 2) and its `src/sample_data.py` module
- report export logic and its `src/report_export.py` module
- FastAPI or UI work
- pytest-cov / coverage thresholds (deferred to post-Phase-3-5 or Phase 6)

Reason: `excel_io.py` and `contracts.py` are cross-cutting infrastructure shared by every business module (see the system-boundaries table in `context/architecture.md`). Defining them once in Phase 1 prevents Phases 3-5 from each inventing slightly different field names and error shapes before a UI consumer exists to catch the drift.

Planned modules:

```text
src/
  excel_io.py
  contracts.py
  order_validation.py
  inventory_allocation.py
  payment_aging.py
  report_export.py
  sample_data.py
```

No Next.js scaffold, FastAPI, auth, or database work in this phase.

## Phase 2 - Sample Data and Contract Fixtures

Create fictional sample inputs and representative output fixtures that prove the Phase 1 contracts can hold real demo data.

> Sample workbooks are demo fixtures, not exhaustive test fixtures. They should be plausible and mostly clean, with a small number of realistic imperfections. Exhaustive edge-case coverage belongs in pytest DataFrame fixtures (see `context/code-standards.md`).

Sample files:

- `sample_orders.xlsx` - mostly valid orders, 1 duplicate order ID, 1 missing field or invalid SKU, enough valid rows to feed allocation
- `sample_product_master.xlsx` - mostly active SKUs, 1 inactive SKU for a realistic validation issue
- `sample_inventory.xlsx` - enough stock for some orders, limited stock for 1-2 SKUs to create partial allocation/backorder, at least 1 SKU near reorder point
- `sample_invoices.xlsx` - mix of current, paid, partial, and overdue invoices, 1 high-priority overdue invoice, at most 1 missing-due-date or invalid-amount row

Contract fixtures:

- Populate the `ValidationSummary`, `ValidationErrorRow`, and `ValidOrderRow` TypedDicts with realistic sample values.
- Populate the `AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`, and `SupplierFollowUpRow` TypedDicts with realistic sample values.
- Populate the `PaymentAgingSummary`, `PaymentAgingRow`, and `DraftMessageRow` TypedDicts with realistic sample values.
- Populate the `ReportManifest` / report pack metadata TypedDict with realistic sample values.

Phase 2 does not define new contract shapes. It uses the `src/contracts.py` definitions from Phase 1 and catches field-name gaps before business-rule implementation begins.

## Phase 3 - Order Validation Core

Build and test:

- Required column checks
- Missing required field checks
- Duplicate order ID detection
- SKU existence and active-status checks
- Positive whole-number quantity checks
- Delivery date not earlier than order date
- Controlled priority values
- Payment terms present
- Business-readable validation errors

Tests must cover every rule in `sales_admin_automation_toolkit_specs/01_demo_order_validation.md`.

## Phase 4 - Inventory Allocation Core

Build and test:

- Allocation sort order: priority, requested delivery date, order date, order ID
- Allocatable quantity calculation
- Full allocation
- Partial allocation
- Backorder
- Inventory never negative
- Warehouse choice by highest available quantity
- Reorder alert / supplier follow-up

Tests must cover every rule in `sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md`.

Do not implement the Optional V2 region-matching warehouse preference in IA-007 during V1.

## Phase 5 - Payment Aging Core

Build and test:

- Outstanding amount calculation
- Paid invoice handling
- Days overdue calculation
- Aging bucket assignment
- Follow-up priority assignment
- Missing due-date issues
- Invalid amount issues
- Draft reminder messages

Tests must cover every rule in `sales_admin_automation_toolkit_specs/03_demo_payment_aging.md`.

## Phase 6 - Excel Report Export

Build and test Excel exports:

- `order_validation_report.xlsx`
- `inventory_allocation_report.xlsx`
- `payment_aging_report.xlsx`
- optional `operations_follow_up_pack.xlsx`

Use business-readable sheet names and include summaries, detail rows, data issues, and follow-up lists.

Phase 6 is a standalone fallback demo milestone. If time runs out before Next.js, the project should still have tested Python logic, fictional sample files, and professional `.xlsx` reports that can be opened or screenshotted in an interview.

## Phase 7 - UI Contract and Wireframe Planning

Phase 7 is planning only and can start after Phase 2 is complete. It may run in parallel with Phases 3-6.

Use the Phase 1 contracts and Phase 2 contract fixtures to define:

- TypeScript interfaces
- route/page structure
- table columns
- KPI cards
- status badges
- report cards
- empty/loading/error states

Figma/Figma MCP can be used here to inspect references, generate wireframes, and map reusable components. This phase must not create production frontend code.

## Phase 8 - Next.js Frontend Foundation

Create the Next.js dashboard only after the Python implementation gate is satisfied.

Hard gate before Phase 8:

- Every test case listed in `sales_admin_automation_toolkit_specs/01_demo_order_validation.md` §12 passes.
- Every test case listed in `sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md` §11 passes.
- Every test case listed in `sales_admin_automation_toolkit_specs/03_demo_payment_aging.md` §12 passes.
- Phase 6 Excel report structure tests pass for required workbook names, sheet names, and representative values.

Required:

- Next.js App Router
- TypeScript strict
- Tailwind CSS 3.4
- shadcn/ui setup
- Inter font
- Project tokens from `ui-tokens.md`
- routes:
  - `/dashboard`
  - `/order-validation`
  - `/inventory-allocation`
  - `/payment-aging`
  - `/reports`

The first UI data source should be mock JSON generated from the Python output contracts.

## Phase 9 - Reusable UI Components and Static Pages

Build:

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

Then build:

- Dashboard
- Order Validation
- Inventory Allocation
- Payment Aging
- Reports

Update `context/ui-registry.md` after each reusable component is built.

## Phase 10 - FastAPI Integration

Only begin after the Python core and static UI are reviewed.

Resolved in a `/grilling` planning session before implementation — see `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md` and `context/library-docs.md`'s "Future FastAPI" section for the full endpoint list and conventions. Summary: the API is stateless (no persisted Workflow Run/job store, no `GET /api/reports/{report_id}`); each workflow gets a `POST .../validate|allocate|aging` endpoint plus a matching `POST .../report` endpoint that re-accepts source files and recomputes rather than trusting a client-supplied result; report downloads return `.xlsx` bytes directly, never a stored artifact fetched by ID.

FastAPI should wrap the already-tested Python modules. It should not duplicate business rules in route handlers.

## Phase 10.2 - Portfolio UI Polish

Planned via `/architect` after Phase 10 shipped — see `docs/architect/phase-10.2-portfolio-ui-polish/`. A token-only visual/hierarchy pass, no backend/API/contract changes, inserted ahead of Phase 11.

- New "Inverse Surface" token family (`surface-inverse`, `surface-inverse-hover`, `text-on-inverse`, `text-on-inverse-muted`) — dark navy sidebar + a new `Button` `dark` variant, both sharing one token family so they can't visually drift apart.
- `SidebarNav` recolored dark navy with a solid-accent active state and a `lucide-react` icon per nav item.
- `MetricCard` restructured into a compact, roughly square tile (icon → value → label, centered, min-height) with a hover/shadow lift, applied across `/dashboard`'s Overview row and all 3 workflow pages' post-run summary grids.
- `/dashboard` consolidated from 3 separate per-workflow KPI groups (~15 tiles) into one 5-card "Overview" row, matching the reference dashboard's composition — a deliberate content reduction, not just a restyle (dropped KPIs remain on their workflow page's own summary).
- `/dashboard`'s two chart cards (Allocation Status, Outstanding by Aging Bucket) fixed for a card-sizing bug (stable min-height instead of accidental CSS Grid row-stretch), gained a compact top-right action link (new `TableSectionHeading` `action` prop), a hover/shadow lift, and genuine data-bearing hover/focus tooltips on every donut segment and bar — no new charting library.
- `/dashboard`'s "Inventory Shortage Alerts" and "Payment Follow-up Items" paired side by side (`grid lg:grid-cols-2`) instead of stacked full-width.
- `UploadPanel` fixed to bottom-anchor its drop zone across multi-panel rows (previously misaligned when "Required columns" text wrapped to different line counts), and its "Sample file" link switched to the new `dark` `Button` variant with a sizing fix so it never wraps to two lines.
- Each workflow page's "Download Report" button switched to the `dark` variant; KPI summary grids fit each page's own card count in a single row on desktop.
- Full detail, including bugs found and fixed along the way (a hydration mismatch, a pointer-events bug), is in `context/ui-registry.md`'s Phase 10.2 entries and "Page composition notes (Phase 10.2)".

## Phase 11 - Deployment Baseline

Deploy the current, post-Phase-10.2 app to a stable public URL a hiring manager can open and use — no new backend logic, no database, no auth, no persistence. Planned via `/grill-with-docs` + `/architect`; see `context/architecture.md`'s "Deployment (Phase 11)" section for the full shape.

- Two independently hosted services, mirroring the app's existing local architecture: Vercel (Next.js frontend, Hobby tier) and Render (FastAPI backend, Free Web Service), connected by the same `NEXT_PUBLIC_API_BASE_URL` / `CORS_ALLOWED_ORIGINS` contract already used locally.
- Deployed from a dedicated `deploy/portfolio-demo` branch, fast-forwarded from the active implementation branch after each verified change — never `main` directly (the PR-stack merge decision stays deferred, as it has been every session) and never an active feature branch (which keeps receiving unrelated WIP).
- No secrets: the only two env vars are the plain config strings above.
- Accepted trade-off: Render's free tier sleeps after ~15 minutes idle, ~1 minute cold-start on wake — mitigated with a README note, not a keep-alive job or paid tier.

**Note on the prior Phase 11 scope:** an earlier "SQL Reporting and Active Sample Dashboard" phase (a SQLite-backed `Demo Reporting Database` and a live `GET /api/dashboard`) was planned and partially implemented — see the archived plan at `docs/archive/phase-11-sql-reporting-sqlite-plan.md` and `docs/grilling/phase-11-sql-reporting-and-active-dashboard/`. Its own ADR (originally intended as `0007`) was never actually written before the phase was paused in favor of deploying first; the working code was preserved in a git stash, and the `0007` slot was later filled by a materially different design — see Phase 12 below and `docs/adr/0007-session-scoped-workflow-result-persistence.md`.

## Phase 12 - Postgres-Backed Latest-Session Dashboard

Deploy-baseline-complete, planned via `/grill-with-docs` (13 resolved decisions) — see `docs/adr/0007-session-scoped-workflow-result-persistence.md` for the full design and `context/architecture.md`'s "Persistence" section for a summary. Replaces the paused SQLite "Demo Reporting Database" idea with genuinely session-specific persistence of real visitor results, not a reseeded demo dataset.

- **Anonymous Session ID**: browser-generated UUID in `localStorage`, sent as `X-Session-Id`. No cookies, no accounts.
- **`workflow_results` table** (Neon Postgres): one JSONB row per `(session_id, workflow_type)`, upserted latest-wins, versioned via `src/contracts.py`'s `CONTRACT_SCHEMA_VERSIONS` and hidden (not deleted) after a 30-day TTL.
- **Write path**: the three JSON workflow endpoints (not their `.../report` counterparts) make a best-effort save after computing, reported via `X-Persisted` (`true`/`false`/`skipped`) — never fails the request. `POST /api/inventory/allocate` persists only `inventory_allocation`, never its internal validation byproduct.
- **Read path**: new `GET /api/dashboard`, per-workflow independent sample-data fallback — `200` all-`null` for "nothing saved yet" (including when `DATABASE_URL` is unset), `503` only for a genuine outage.
- **Frontend**: `components/dashboard/DashboardLiveSections.tsx`, a Client Component fetching on mount (not a Server Component fetch — `localStorage` doesn't exist during Vercel's render); `app/dashboard/page.tsx` stays a Server Component for the static shell. A "Sample data" chip marks any section still showing seeded demo content.
- **Hosting**: Neon Postgres, three branches (`main`/`dev`/`test`), hand-written SQL migrations run in the FastAPI lifespan hook (no Alembic), `psycopg` 3 (no ORM) — consistent with this project's existing precedents.
- **Testing**: two layers — mocked-repository route-orchestration tests (fast, offline, always run) plus real-Neon repository/SQL tests marked `@pytest.mark.db` (skip, don't fail, when `TEST_DATABASE_URL` is unset), preserving `uv run pytest`'s zero-configuration hermeticity on a fresh clone.

## Optional Design Workflow

Use `ui_reference_to_figma_workflow/` and `ui_prompts_for_agents_mcp/` as guidance:

- Collect or generate references.
- Inspect Figma through MCP if available.
- Extract screen inventory, component mapping, and design tokens.
- Classify UI ideas as V1, V1.5, V2, or remove.
- Keep designs aligned with the Python output contracts.
