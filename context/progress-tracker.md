# Progress Tracker

Update this file after every completed feature.

## Current Status

**Project:** Sales Admin Automation Toolkit  
**Phase:** Phase 4 - Inventory Allocation Core (complete)  
**Last completed:** Phase 4 — `src/inventory_allocation.py` (`load_valid_orders`, `load_inventory`, `allocate_inventory`, local `InventoryAllocationResult` envelope) implementing every IA-001–IA-006 and IA-008 rule (Optional V2 region-matching in IA-007 excluded per Scope Gate), `tests/test_inventory_allocation.py` covering all spec §11 cases plus resolved edge cases, tests passing (`uv run pytest` — 85 passed)  
**Next:** Phase 5 — Payment Aging Core (Phase 7 UI planning may also continue in parallel, since it's planning-only)

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

- [x] Generate `sample_orders.xlsx` (mostly valid, 1 duplicate order ID, 1 invalid SKU)
- [x] Generate `sample_product_master.xlsx` (mostly active SKUs, 1 inactive SKU)
- [x] Generate `sample_inventory.xlsx` (limited stock for MED-LENS-001 across 2 warehouses, 1 SKU below reorder point)
- [x] Generate `sample_invoices.xlsx` (mix of current/paid/partial/overdue, 1 high-priority overdue, 1 missing-due-date data-issue row)
- [x] Populate validation contract fixtures with realistic sample values
- [x] Populate allocation contract fixtures with realistic sample values
- [x] Populate payment aging contract fixtures with realistic sample values
- [x] Populate report manifest fixture with realistic sample values

### Phase 3 - Order Validation Core

- [x] Required column checks
- [x] Required field validation
- [x] Duplicate order ID detection
- [x] Valid active SKU checks
- [x] Positive whole-number quantity checks
- [x] Delivery date validation
- [x] Priority controlled values
- [x] Payment terms check
- [x] pytest coverage

### Phase 4 - Inventory Allocation Core

- [x] Allocation sort order
- [x] Allocatable quantity calculation
- [x] Full allocation
- [x] Partial allocation
- [x] Backorder handling
- [x] Non-negative inventory guarantee
- [x] Warehouse choice rule
- [x] Reorder alert / supplier follow-up
- [x] pytest coverage

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
- Phase 2 tooling decisions (via `/architect`): `sample_invoices.xlsx` due dates are generated as offsets from a `reference_date: date | None = None` parameter (resolved to `date.today()` inside the function, not a literal default) so the aging demo stays believable whenever regenerated; orders/inventory use plain fixed dates since their rules don't depend on "today". Contract fixtures live in `tests/contract_fixtures.py` (not inline in tests, not a new `src/` module) so Phase 7 UI planning can read them directly.
- Phase 2 complete: `src/sample_data.py`, `sample_data/*.xlsx` (4 files), `tests/contract_fixtures.py`, `tests/test_sample_data.py`, extended `tests/test_contracts.py`; `uv run pytest` passes (32 tests).
- Phase 3 decisions (via `/architect`): `validate_orders()` returns a single `OrderValidationResult` dict envelope (`summary`/`valid_orders`/`errors`), defined locally in `order_validation.py`, not added to `contracts.py`. Multiple validation errors allowed per row; OV-001 emits one error per missing field. Resolved an internal spec contradiction (OV-001 vs OV-007 both covering blank `payment_terms`) in favor of OV-007-Warning-only, so Warning-only rows stay valid. Blank fields skip their downstream value-quality rule (OV-002/003/004/005/006) to avoid double-flagging. OV-003 split into `UNKNOWN_SKU`/`INACTIVE_SKU`/`INVALID_ACTIVE_FLAG`; OV-005 split into `INVALID_ORDER_DATE`/`INVALID_DELIVERY_DATE`/`DELIVERY_BEFORE_ORDER`. Malformed quantity/dates convert to business-readable errors rather than raising. `product_name` fills from product master only when the order row's own value is blank.
- Phase 3 complete: `src/order_validation.py`, `tests/test_order_validation.py`; `uv run pytest` passes (63 tests).
- Phase 4 decisions (via `/architect`): `allocate_inventory()` returns a local `InventoryAllocationResult` dict envelope (`summary`/`allocation_results`/`backorders`/`remaining_inventory`/`supplier_follow_ups`), defined locally in `inventory_allocation.py`, not added to `contracts.py` — mirrors Phase 3's envelope pattern. IA-007 V1 warehouse choice compares `allocatable_qty` (`available_qty - reserved_qty`, floored at 0), not raw `available_qty`; ties broken by warehouse name ascending. Allocation is stateful and per-line: orders processed strictly in IA-001 order, one line fulfilled from exactly one warehouse, with warehouse choice re-evaluated per line as stock depletes. A fully-backordered line still records the best-candidate warehouse when the SKU has any inventory rows; `warehouse` is `""` only when the SKU has zero inventory rows anywhere. Supplier Follow-up is scoped strictly to IA-008's literal trigger (`reorder_point` present and `remaining_qty` strictly below it, evaluated once per (sku, warehouse) after the full batch) — not triggered by backorder status alone, despite `CONTEXT.md`'s broader glossary phrasing. `remaining_qty = starting_available_qty - allocated_qty` (not `allocatable_qty`, since `reserved_qty` only gates allocation eligibility). `low_stock_sku_count` counts distinct SKUs with at least one alerting (sku, warehouse) row, not follow-up row count. Malformed/blank required inventory values (`sku`, `warehouse`, `available_qty`) raise a new `InvalidInventoryDataError` rather than silently coercing, since no `InventoryDataIssueRow` contract exists to report them as soft errors; optional numeric fields (`reserved_qty`, `reorder_point`, `lead_time_days`) still degrade gracefully to "not present" when blank/unparseable.
- Phase 4 complete: `src/inventory_allocation.py`, `tests/test_inventory_allocation.py`; `uv run pytest` passes (85 tests). Sanity-checked against `sample_data/sample_orders.xlsx` + `sample_data/sample_inventory.xlsx` (routed through Phase 3's `validate_orders()` first) — output matches the hand-authored fixtures in `tests/contract_fixtures.py` field-for-field.
