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

Planned endpoints:

```text
POST /api/orders/validate
POST /api/inventory/allocate
POST /api/payments/aging
GET  /api/reports/{report_id}
```

FastAPI should wrap the already-tested Python modules. It should not duplicate business rules in route handlers.

## Optional Design Workflow

Use `ui_reference_to_figma_workflow/` and `ui_prompts_for_agents_mcp/` as guidance:

- Collect or generate references.
- Inspect Figma through MCP if available.
- Extract screen inventory, component mapping, and design tokens.
- Classify UI ideas as V1, V1.5, V2, or remove.
- Keep designs aligned with the Python output contracts.
