# Progress Tracker

Update this file after every completed feature.

## Current Status

**Project:** Sales Admin Automation Toolkit  
**Phase:** Phase 1 - Python Project Foundation (complete)  
**Last completed:** Phase 1 scaffolding — `pyproject.toml`/`uv`, `src/excel_io.py`, `src/contracts.py` (13 output families incl. `PaymentDataIssueRow` per ADR 0005), tests passing (`uv run pytest` — 7 passed)  
**Next:** Phase 2 — Sample Data and Contract Fixtures

## Important Note

Previous JobPilot planning and progress are no longer active for this project. Treat those decisions as superseded. The active project is the Sales Admin Automation Toolkit.

The previous static-UI-first decision is also superseded. The active build order is Python business logic and output contracts first, polished Next.js dashboard second.

Phase 7 is allowed to start after Phase 2 because it is planning-only. Phase 8 is hard-gated on passing Phase 3-6 tests.

## Progress

### Phase 0 - Planning Reset

- [x] Rewrite context files for Sales Admin Automation Toolkit
- [x] Add root `CONTEXT.md` domain glossary
- [x] Add ADR: Next.js V2 first instead of Streamlit V1
- [x] Add ADR: static mock UI before Python/FastAPI integration
- [x] Add docs for context reset
- [x] Add ADR: Python core before polished UI
- [x] Revise context files for Python-first sequence

### Phase 1 - Python Project Foundation

Tooling conventions locked via `/grill-with-docs` session, see `docs/adr/0004-phase-1-python-tooling.md`: Python 3.12, `pyproject.toml` + `uv`, pytest config in `pyproject.toml`, no placeholder modules for later phases.

- [x] Create Python project config (`pyproject.toml`, `.python-version` = 3.12)
- [x] Create `src/` package (`__init__.py`, `excel_io.py`, `contracts.py` only)
- [x] Create `tests/` package (`test_excel_io.py`, `test_contracts.py` only)
- [x] Create `sample_data/` folder (empty)
- [x] Add pytest configuration (`[tool.pytest.ini_options]` in `pyproject.toml`)
- [x] Add README setup notes (`uv sync`, `uv run pytest`)
- [x] Add `src/excel_io.py` (load helper, required-column validation, missing-column error shape)
- [x] Add `src/contracts.py` (TypedDicts for all 13 output families incl. `PaymentDataIssueRow`, no business logic)

### Phase 2 - Sample Data and Contract Fixtures

- [ ] Generate `sample_orders.xlsx` (mostly valid, 1 duplicate order ID, 1 missing field/invalid SKU)
- [ ] Generate `sample_product_master.xlsx` (mostly active SKUs, 1 inactive SKU)
- [ ] Generate `sample_inventory.xlsx` (limited stock for 1-2 SKUs, 1 SKU near reorder point)
- [ ] Generate `sample_invoices.xlsx` (mix of current/paid/partial/overdue, 1 high-priority overdue, at most 1 data-issue row)
- [ ] Populate validation contract fixtures with realistic sample values
- [ ] Populate allocation contract fixtures with realistic sample values
- [ ] Populate payment aging contract fixtures with realistic sample values
- [ ] Populate report manifest fixture with realistic sample values

### Phase 3 - Order Validation Core

- [ ] Required column checks
- [ ] Required field validation
- [ ] Duplicate order ID detection
- [ ] Valid active SKU checks
- [ ] Positive whole-number quantity checks
- [ ] Delivery date validation
- [ ] Priority controlled values
- [ ] Payment terms check
- [ ] pytest coverage

### Phase 4 - Inventory Allocation Core

- [ ] Allocation sort order
- [ ] Allocatable quantity calculation
- [ ] Full allocation
- [ ] Partial allocation
- [ ] Backorder handling
- [ ] Non-negative inventory guarantee
- [ ] Warehouse choice rule
- [ ] Reorder alert / supplier follow-up
- [ ] pytest coverage

### Phase 5 - Payment Aging Core

- [ ] Outstanding amount calculation
- [ ] Paid invoice handling
- [ ] Days overdue calculation
- [ ] Aging bucket assignment
- [ ] Follow-up priority assignment
- [ ] Missing due-date issues
- [ ] Invalid amount issues
- [ ] Draft reminder generation
- [ ] pytest coverage

### Phase 6 - Excel Report Export

- [ ] Order validation report
- [ ] Inventory allocation report
- [ ] Payment aging report
- [ ] Optional full operations report pack
- [ ] pytest coverage for workbook structure
- [ ] Fallback demo milestone: tested logic + professional `.xlsx` reports are interview-ready

### Phase 7 - UI Contract and Wireframe Planning

- [ ] Gate check: Phase 2 contract fixtures complete
- [ ] TypeScript interface plan from Python outputs
- [ ] Route/page plan
- [ ] Table column plan
- [ ] KPI and chart mapping
- [ ] Figma/MCP reference review if useful

### Phase 8 - Next.js Frontend Foundation

- [ ] Gate check: all spec-listed pytest cases pass for Phases 3-5
- [ ] Gate check: Phase 6 Excel report structure tests pass
- [ ] Scaffold Next.js App Router project
- [ ] Configure TypeScript strict
- [ ] Configure Tailwind CSS 3.4 tokens
- [ ] Add shadcn/ui base setup
- [ ] Add app shell routes

### Phase 9 - Reusable UI Components and Static Pages

- [ ] AppShell
- [ ] SidebarNav
- [ ] TopHeader
- [ ] MetricCard
- [ ] WorkflowStepper
- [ ] UploadPanel
- [ ] StatusBadge
- [ ] DataTable
- [ ] ReportCard
- [ ] EmptyState
- [ ] LoadingState
- [ ] BusinessErrorMessage
- [ ] Dashboard
- [ ] Order Validation
- [ ] Inventory Allocation
- [ ] Payment Aging
- [ ] Reports

### Phase 10 - FastAPI Integration

- [ ] FastAPI endpoints
- [ ] Frontend API adapter
- [ ] Contract tests
- [ ] End-to-end workflow checks

## Decisions Made

- The active project is Sales Admin Automation Toolkit, not JobPilot.
- First implementation target is Python business-rule core.
- The polished UI target remains Next.js V2, but after Python outputs are stable.
- UI contract/wireframe planning may run after Phase 2 and in parallel with Python business-rule implementation.
- Real Next.js implementation must wait until all spec-listed Python tests and Excel report structure tests pass.
- Streamlit is not the active UI implementation path.
- FastAPI comes after the Python core and UI contracts are stable.
- CRM Cleaner is postponed.
- Optional/V1.5/V2 spec items are out of scope unless a new ADR explicitly adds them.
- Legacy JobPilot design images remain in `context/designs/` only as archived assets and are not active UI references.
- Phase 1 tooling locked: Python 3.12, `pyproject.toml` + `uv` (no `requirements.txt`), pytest config in `pyproject.toml`, no placeholder files for later-phase modules (`docs/adr/0004-phase-1-python-tooling.md`).
- Added `PaymentDataIssueRow` as a 13th output-contract family: the payment-aging Data Issues sheet (PA-006/PA-007) had no matching contract in the original 12-family list (`docs/adr/0005-payment-data-issue-row-contract.md`).
- Phase 1 complete: `pyproject.toml`/`uv` project config, `src/excel_io.py`, `src/contracts.py` (13 output families), `tests/test_excel_io.py`, `tests/test_contracts.py` all in place; `uv run pytest` passes (7 tests).
