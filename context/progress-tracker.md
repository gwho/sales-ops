# Progress Tracker

Update this file after every completed feature.

## Current Status

**Project:** Sales Admin Automation Toolkit  
**Phase:** Phase 6 - Excel Report Export (complete)  
**Last completed:** Phase 6 — `src/report_export.py` (`export_order_validation_report`, `export_inventory_allocation_report`, `export_payment_aging_report`, each returning `tuple[bytes, ReportManifest]` from in-memory `openpyxl` workbooks) consuming the Phase 3–5 result envelopes directly with zero recalculation, `tests/test_report_export.py` covering workbook structure, sheet names, representative cell values, and manifest shape, tests passing (`uv run pytest` — 149 passed)  
**Next:** Phase 7 UI planning continues in parallel (planning-only); Phase 8 (Next.js implementation) remains hard-gated until Phase 6's Excel report structure tests pass (now satisfied) plus every spec §12/§11/§12 test case

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

- [x] Outstanding amount calculation
- [x] Paid invoice handling
- [x] Days overdue calculation
- [x] Aging bucket assignment
- [x] Follow-up priority assignment
- [x] Missing due-date issues
- [x] Invalid amount issues
- [x] Draft reminder generation
- [x] pytest coverage

### Phase 6 - Excel Report Export

- [x] Order validation report
- [x] Inventory allocation report
- [x] Payment aging report
- [ ] Optional full operations report pack — deferred pending ADR. `operations_follow_up_pack.xlsx` is labeled V1.5 in `05_integration_and_app_flow.md` §7, not V1; per the Scope Gate it needs a new ADR before implementation, not just a build-plan checkbox.
- [x] pytest coverage for workbook structure
- [x] Fallback demo milestone: tested logic + professional `.xlsx` reports are interview-ready

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
- Phase 4 complete: `src/inventory_allocation.py`, `tests/test_inventory_allocation.py`; `uv run pytest` passes (93 tests). Sanity-checked against `sample_data/sample_orders.xlsx` + `sample_data/sample_inventory.xlsx` (routed through Phase 3's `validate_orders()` first) — output matches the hand-authored fixtures in `tests/contract_fixtures.py` field-for-field. Post-review hardening added business-readable direct-call failures for malformed valid-order inputs, negative optional inventory quantities, and offending cell values in inventory error messages.
- Phase 5 decisions (via `/architect`): `calculate_payment_aging()` returns a single local `PaymentAgingResult` dict envelope (`summary`/`aging_rows`/`data_issues`/`draft_messages`), defined locally in `payment_aging.py`, not added to `contracts.py` and not split into the spec's suggested multi-function/DataFrame-tuple shape — mirrors Phase 3/4's envelope pattern. Paid invoices (`outstanding_amount <= 0`, clamped, never negative) stay in `aging_rows` with `follow_up_priority="None"` and `suggested_action="No action required"` — excluded only from active follow-up (High/Medium/Low/Watch) and draft messages, not from the aging table itself. `total_invoices` counts every loaded row including PA-006/PA-007 data-issue rows; `aging_bucket_counts`/`total_outstanding_amount`/`overdue_amount`/`high_priority_count` are computed only from `aging_rows`, mirroring Phase 3's `total_orders` semantics. `as_of_date: date | None = None` resolves to `date.today()` inside the function body (never a literal default), matching the Phase 2 `sample_data.py` convention. `days_overdue` is the raw signed value (`effective_date - due_date`), negative for future due dates, letting Watch be derived as `-7 <= days_overdue <= 0`. Draft reminders are generated only when `outstanding_amount > 0 and days_overdue > 0 and follow_up_priority in {High, Medium, Low}` — never for Watch/Current/Paid/data-issue rows. Invalid/missing `paid_amount` (blank, non-numeric, or negative) silently degrades to `0.0` with no data issue, since PA-007 only names `invoice_amount`; only `invoice_amount` missing/non-numeric/negative triggers a PA-007 data issue, and a row can carry both a PA-006 and PA-007 issue independently. Draft message amounts are formatted with the invoice's own `currency` column when present (e.g. `"HKD 58,000.00"`), falling back to a bare `"58,000.00"` when blank — not the literal `$` the original hand-authored fixture used, since currency is not carried into any output contract per the Field Scope Boundary and a bare `$` would misrepresent HKD/SGD/TWD sample invoices. `PaymentDataIssueRow` does not surface `row_number`; it stays an internal-only loop index, matching the existing contract shape.
- Phase 5 complete: `src/payment_aging.py`, `tests/test_payment_aging.py`; `uv run pytest` passes (127 tests). Sanity-checked against `sample_data/sample_invoices.xlsx` (`as_of_date=2026-07-09`) — `INV-2026-001`'s computed row matched `tests/contract_fixtures.py`'s `PAYMENT_AGING_ROW_FIXTURE` field-for-field after correcting a pre-existing 1-day date typo in that fixture (`invoice_date`/`due_date` were off by one from the real generated sample data) and updating `DRAFT_MESSAGE_ROW_FIXTURE`'s hardcoded `$58,000.00` to the currency-aware `HKD 58,000.00`. Before starting Phase 5, committed substantial uncommitted Phase 4 hardening work found already sitting in the working tree (new `InvalidOrderDataError` for malformed valid-order fields, negative-quantity rejection on optional inventory fields, direct column validation inside `allocate_inventory()`) to PR #3 first, per user instruction, bringing Phase 4's test count from 85 to 93 before branching Phase 5.
