# Progress Tracker

Update this file after every completed feature.

## Current Status

**Project:** Sales Admin Automation Toolkit  
**Phase:** Sample Data Enrichment (complete, Python-only revisit of Phase 2 — no phase-number bump, Next.js state unchanged)  
**Last completed:** Sample Data Enrichment — following `sample_excel_data_requirements/` planning docs (treated as planning input only, current `src/` modules/tests as schema authority), `src/sample_data.py` was rewritten with a richer fictional scenario: a regional medical optics/healthcare equipment company (HK + Mainland China customers, HK/China/Europe warehouses/suppliers), still fully fictional and hand-authored/deterministic (no `random`/seed). Scale: 18 products (2 inactive), 36 orders (7 issue-bearing rows, ~19%, several combining multiple issues per row), 17 inventory rows across 3 warehouses, 27 invoices (all 5 aging buckets, all payment states, 1 missing-due-date issue, 1 invalid-amount issue, 1 deliberate overpayment), and a new optional/reference-only `sample_customers.xlsx` (17 rows, no Python module reads it). New `sample_data/README_sample_data.md` documents the fictional-data disclosure, determinism approach, schemas, and every intentional issue. `tests/test_sample_data.py` rewritten to assert the same structural properties plus new coverage for every newly introduced issue type. Zero changes to `src/order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, `report_export.py`, `contracts.py`. `uv run pytest` 172 passing (up from 152). **Follow-on same session:** `scripts/generate_mock_data.py` was rewritten (via `/architect`) to derive `lib/mock-data/*.json` from the real `sample_data/*.xlsx` pipeline (`validate_orders` → `allocate_inventory`, plus independent `calculate_payment_aging`, plus `report_export` manifests) instead of `tests/contract_fixtures.py`'s single-row fixtures — so the static UI now reflects the enriched dataset (28 valid orders, 25 aging rows, etc.) instead of 1-2 rows per table. `tests/contract_fixtures.py` is untouched and still used only by `test_contracts.py`/`test_report_export.py`. `lib/mock-data.ts`'s header comment and `package.json` (new `npm run mock-data` alias) updated to match. `MOCK_AS_OF_DATE`/`MOCK_GENERATED_AT` are pinned constants (2026-07-10) so the committed JSON is deterministic across re-runs. `sample_customers.xlsx` is never read by this script. `uv run pytest` (172), `npm run typecheck`, `npm run lint`, and `npm run build` (all 9 routes still prerender statically) all clean after regenerating.
**Next:** Phase 10 (FastAPI Integration) — unchanged in scope by this work. Wires the 4 upload panels and report-download buttons to real endpoints, replaces `lib/mock-data.ts` static imports with live API calls, and gives `LoadingState`/`BusinessErrorMessage`/`ReportCard`'s non-Ready states and the report-lifecycle visual variants real client-driven transitions for the first time. The committed `sample_data/*.xlsx` files (now richer) are well positioned to back a future "Sample template" download feature — `UploadPanel.tsx`'s disabled "Sample template" button already anticipates this but wiring it is still out of scope until Phase 10. Bilingual (Traditional Chinese) guide content and a possible header-level per-column filter mechanism were both explicitly deferred in Phase 9.1 — revisit only if requested.

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

### Sample Data Enrichment (Phase 2 revisit)

- [x] Fictional regional medical optics/healthcare equipment scenario (HK + Mainland China customers, HK/China/Europe warehouses)
- [x] `sample_product_master.xlsx` — 18 SKUs, 2 inactive
- [x] `sample_orders.xlsx` — 36 rows, 7 issue-bearing (~19%), several combined-issue rows
- [x] `sample_inventory.xlsx` — 17 rows across 3 warehouses, guaranteed partial/backorder/reorder-alert cases
- [x] `sample_invoices.xlsx` — 27 rows, all 5 aging buckets, both data-issue types, 1 deliberate overpayment
- [x] `sample_customers.xlsx` — new, optional/reference-only, 17 rows
- [x] `sample_data/README_sample_data.md` — new
- [x] `tests/test_sample_data.py` rewritten for new dataset + new issue coverage
- [x] End-to-end compatibility check against `order_validation.py`/`inventory_allocation.py`/`payment_aging.py`/`report_export.py`

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

- [x] Gate check: Phase 2 contract fixtures complete
- [x] TypeScript interface plan from Python outputs
- [x] Route/page plan
- [x] Table column plan
- [x] KPI and chart mapping
- [x] Figma/MCP reference review if useful — deferred in Phase 7 (no connector then); actually performed in Phase 8 once the Figma MCP was connected. Four Figma Make prototypes inspected and classified in `ui-contract-plan.md`'s Figma Reference Reconciliation section.

### Phase 8 - Next.js Frontend Foundation

- [x] Gate check: all spec-listed pytest cases pass for Phases 3-5 — line-by-line audit, all 26 spec §11/§12 cases map to named tests (8 order-validation, 8 inventory-allocation, 10 payment-aging)
- [x] Gate check: Phase 6 Excel report structure tests pass — 24/24 in `test_report_export.py`
- [x] Scaffold Next.js App Router project — Next 16 + React 19 at repo root, transplanted from a scratchpad scaffold so no existing Python/context/docs files were clobbered
- [x] Configure TypeScript strict — `strict: true`, `@/*` path alias, `typecheck` script (`tsc --noEmit`)
- [x] Configure Tailwind CSS 3.4 tokens — pinned 3.4.19 (no v4), `tailwind.config.ts` + `globals.css` wired to `ui-tokens.md` tokens verbatim, Inter via `next/font`
- [x] Add shadcn/ui base setup — plumbing only: `cn()` (`lib/utils.ts`), `components.json`, deps (clsx/tailwind-merge/cva/lucide). Primitive components and any shadcn-token bridge deferred to Phase 9 (see Decisions Made) to avoid injecting a token set that collides with `ui-tokens.md`
- [x] Add app shell routes — 5 stub routes (`/dashboard`, `/order-validation`, `/inventory-allocation`, `/payment-aging`, `/reports`) + root redirect to `/dashboard`; real `AppShell`/`SidebarNav` and page content are Phase 9

### Phase 9 - Reusable UI Components and Static Pages

- [x] AppShell
- [x] SidebarNav
- [x] TopHeader
- [x] MetricCard
- [x] WorkflowStepper
- [x] UploadPanel
- [x] StatusBadge
- [x] DataTable
- [x] ReportCard
- [x] EmptyState
- [x] LoadingState
- [x] BusinessErrorMessage
- [x] Dashboard
- [x] Order Validation
- [x] Inventory Allocation
- [x] Payment Aging
- [x] Reports

### Phase 9.1 - Visual Alignment Fixes

- [x] Visual alignment review (code + rendered-HTML audit, cross-checked against 4 Figma Make prototypes)
- [x] Critical: `AppShell`/`SidebarNav` height model fix
- [x] Brand name consistency, `/reports` width fix, `WorkflowStepper` terminal-step color
- [x] Download actions on 3 workflow pages, Payment Aging "As of" date
- [x] Icon-chip `MetricCard`, zebra-striped `DataTable`
- [x] Table density/typography/truncation/sort-coverage pass (all 3 workflow pages)
- [x] `FilterToolbar`/`FilterSelect`/`MiniBar` — filtering and sorting restored to `DataTable` via page-level composition
- [x] `TableSectionHeading` icon+caption pattern across all tables/panels
- [x] Dashboard: Inventory Shortage Alerts, Payment Follow-up Items, workflow infographic, "How This Demo Works" guide (English only)
- [x] `DonutBreakdownChart`/`VerticalBucketBarChart` (`components/charts/`) replacing dashboard mini-bar visuals
- [x] Before/after manual screenshot verification (Figma MCP rate-limited mid-session; fell back to developer-provided screenshots per the documented fallback)

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
- Phase 7 decisions (via `/architect` + `AskUserQuestion`): TypeScript interfaces are literal `.ts` code blocks in `context/ui-contract-plan.md` (new), snake_case fields preserved verbatim, no camelCase adapter decided. `context/ui-rules.md`'s Status Badges section rewritten in full for all 4 workflow groups (not just the 2 originally flagged) into an explicit direct-vs-derived structure — Inventory Allocation and Payment Aging were also mixing controlled-vocabulary fields with unexplained derived shorthand. `/dashboard` scoped as a read-only aggregate landing page (per-workflow KPI strips with independent empty states + 3 report cards + 3 entry cards), no persisted cross-workflow state, no new contract. Client-side derived aggregates permitted for charts/KPIs (e.g. "90+ Days Amount", "Backordered Qty by SKU") as long as each is explicitly labeled with its source rows/fields/grouping rule. `CONTEXT.md` not edited this phase — `Status Badge`/`Derived Display Value` are UI-planning terms, defined in `ui-contract-plan.md` instead. Figma/MCP reference deferred (none available this session). Discovered and flagged a `ReportManifest.report_id` format mismatch between `tests/contract_fixtures.py` (stale) and the real `report_export.py` exporter; corrected after Phase 7 before Phase 8 prep.
- Post-Phase-7 fixture correction complete: `REPORT_MANIFEST_FIXTURES.report_id` now uses the real timestamp-based exporter format for all 3 report types, and `tests/test_contracts.py` verifies each fixture ID matches its own `report_type` + `generated_at`.
- Phase 7 complete: `context/ui-contract-plan.md` (new), `context/ui-rules.md` (Status Badges section rewritten), `context/progress-tracker.md` updated; no `src/`/`tests/` changes, `uv run pytest` still passes (151 tests, unchanged).
- Phase 8 decisions (via `/architect` + `AskUserQuestion`, Figma MCP now connected): scaffolded into a scratchpad temp dir and transplanted only Next.js files to the repo root, because `create-next-app` generates its own `AGENTS.md`/`CLAUDE.md`/`README.md`/`.gitignore` that would clobber the real ones — `git status` confirmed no Python/context/docs file was touched. Tailwind pinned to 3.4.19 (create-next-app defaults to v4); set up via the v3 path (`tailwind.config.ts` + `@tailwind` directives + autoprefixer), not v4's CSS-first config. Snake_case preserved verbatim in `types/index.ts` and mock JSON — no camelCase adapter (carried from Phase 7). Payment Aging badges stay direct-fields-only (`aging_bucket`, `follow_up_priority`); no Paid/Overdue shorthand. **shadcn is plumbing-only this phase** (`cn()`, `components.json`, deps) — primitive components deferred to Phase 9. Reason: `ui-tokens.md`'s token names are authoritative and collide with shadcn's default set (notably `--accent` = brand blue here vs shadcn's gray hover); adding primitives now would force injecting shadcn's parallel tokens, which the CRITICAL "never add tokens without approval" rule (`skills/tailwind-best-practices`) forbids. Phase 9 adds each primitive only when a real component needs it, reconciles its classes to `ui-tokens.md`, and `/imprint`s the pattern. Mock JSON is generated build-time-only by `scripts/generate_mock_data.py` from `tests/contract_fixtures.py`; the Next.js app never imports `tests/` at runtime — it reads committed `lib/mock-data/*.json`.
- Phase 8 complete: `app/` (root layout + 5 stub routes + root redirect), `tailwind.config.ts`, `postcss.config.mjs`, `app/globals.css` (tokens), `lib/utils.ts`, `components.json`, `types/index.ts`, `scripts/generate_mock_data.py`, `lib/mock-data/*.json`, `package.json`/lockfile, merged `.gitignore`. `npm run build`/`lint`/`typecheck` clean; all 5 routes serve 200 with semantic-token CSS compiled; `uv run pytest` still 152 (Python untouched). `context/ui-registry.md` intentionally left empty — no reusable components built this phase.
- Phase 9 decisions (via `/architect` + `AskUserQuestion`): static showcase, not a simulated live app — pages render `lib/mock-data.ts`'s typed mock data immediately, `UploadPanel` is a real file-picker that never gates content, `ReportCard` renders `Ready` straight from the mock `ReportManifest`, and the other 3 report-lifecycle states plus `WorkflowStepper`'s steps exist only as prop-driven visual variants, never live-wired via timers. `DataTable` is plain client-side single-column sort with no new dependency (no TanStack Table this phase — mock fixtures are 1-2 rows). All primitives (`Button`/`Card`/`Badge`/`Table`) are hand-written under `components/ui/`, never generated via `npx shadcn add`, because `components.json`'s `baseColor: "slate"` would inject shadcn's own colliding tokens into `globals.css`. No Recharts — the Payment Aging aging-bucket breakdown is a token-styled bar list. `StatusBadge`'s status→tone mapping was fixed before build (see `context/ui-registry.md`'s StatusBadge entry), not decided ad hoc. Added `lib/mock-data.ts` and `lib/formatters.ts` per `architecture.md`'s already-documented Future Frontend Shape.
- Phase 9 build-time discovery (not anticipated in planning): React Server Components cannot pass functions as props to Client Components. `DataTable`'s `columns` config carries `render`/`sortValue` functions, so every page that builds a `DataTable` column config must itself be a Client Component, not just `DataTable` — `order-validation`, `inventory-allocation`, and `payment-aging` pages are `"use client"` for this reason (discovered via a real `next build` prerender failure, not a review pass). `dashboard` and `reports` don't use `DataTable` and stay Server Components as originally planned.
- Phase 9 complete: 12 registry components + 4 hand-written primitives (`components/ui/`, `components/layout/`, `components/feedback/`, `components/workflow/`, `components/tables/`), `lib/mock-data.ts`, `lib/formatters.ts`, all 5 routes filled in against mock JSON. `npm run build`/`lint`/`typecheck` clean; `uv run pytest` still 152 (Python untouched); route smoke checks confirm real contract data (not placeholder text) renders on all 5 routes; token/raw-color scan and `globals.css` diff (no shadcn-default variables introduced) both clean; Figma Reference Reconciliation corrections (real priority vocab, real allocation status values, real $50k threshold, real supplier-follow-up field set, verbatim draft-message text, fixed 5-route nav) verified present, not the Figma prototypes' invented versions.
- Phase 9.1 decisions (via `/project-review` + `/architect` + `AskUserQuestion`, multiple review passes in one session): the sidebar-height bug (`SidebarNav`'s `h-screen` inside `AppShell`'s uncapped `min-h-screen` shell — sidebar stops at one viewport while content grows taller) was Critical and confirmed only via rendered-HTML class inspection, not source reading alone; fixed by capping the whole shell to `h-screen overflow-hidden` (matching the pattern found in the Figma Overview Dashboard prototype's own root) and making `<main>` the sole internal scroll region. Filtering was reintroduced to `DataTable` as page-level composition (`FilterToolbar`/`FilterSelect` filter the `data` array before it reaches `DataTable`) rather than teaching `DataTable` about filters itself — revises Phase 9's "sort only, no filtering" decision without growing `DataTable`'s own prop surface. `StatusBadge`'s `Tone` type is imported into the new `components/charts/` components as a type-only import from `components/workflow/StatusBadge.tsx` (matching the existing `MiniBar`/`SegmentedBar` precedent) — the actual `allocationStatusTone`/`agingBucketTone` tone-resolution functions are called only at page level, so charts never decide their own colors and can't drift from what table badges show for the same status. All tone→class mappings across every new component (`Badge`'s dot, `MiniBar`, `SegmentedBar`, `DonutBreakdownChart`, `VerticalBucketBarChart`) are literal `Record<Tone, string>` objects — never dynamic template-string class construction — so Tailwind's static scanner always finds them. Bilingual (Traditional Chinese) guide content and a second per-column header-filter mechanism (distinct from the toolbar filters) were both explicitly deferred, not built.
- Phase 9.1 complete: Critical sidebar fix; brand/width/stepper-color fixes; download actions + Payment Aging date; icon-chip `MetricCard` + zebra-striped `DataTable`; full table density/typography/truncation/sort-coverage pass; `FilterToolbar`/`FilterSelect`/`MiniBar`/`TableSectionHeading` (new `components/tables/` additions); `/dashboard` gained Inventory Shortage Alerts, Payment Follow-up Items, a workflow infographic, and an English-only guide section; `DonutBreakdownChart`/`VerticalBucketBarChart` (new `components/charts/` folder) replaced the dashboard's Allocation/Payment-Aging mini-bar visuals, sourced from 2 new `ui-contract-plan.md` derived aggregates ("Gap to Reorder Point," "Outstanding amount by aging bucket"). `npm run build`/`lint`/`typecheck` clean and `uv run pytest` still 152 at every checkpoint across the whole phase; before/after manual screenshots (Figma MCP capture hit its Starter-plan rate limit mid-session, 3 of 5 "before" routes captured before falling back to developer-provided screenshots per the documented fallback) confirm every fix rendered correctly with no regressions.
- Sample Data Enrichment decisions (via built-in Plan Mode acting as the `/architect` step, + `AskUserQuestion` + a user follow-up correction before implementation): scenario fictionalized as a regional medical optics/healthcare equipment company "inspired by a ZEISS Far East-style operating model" (tonal/structural inspiration only — no real company name, trademark, product line, pricing, or confidential detail used anywhere in generated data, code, or docs). Generation stays hand-authored literal rows in `src/sample_data.py` (no `random`/seed module) — README states "deterministic by construction," not a random-seed strategy, resolving a wording mismatch with the planning docs. Orders hold ~19% issue-bearing rows by combining multiple intentional issues onto the same row (e.g. missing SKU + blank `payment_terms` together) rather than one row per issue type. `sample_invoices.xlsx` gained the optional `order_id` column (mostly references a real generated order, non-functional context, not in `payment_aging.py`'s required columns). `sample_customers.xlsx` generated but strictly reference-only — no loader/validation function anywhere in `src/`. No output contract, business rule, or UI/`app`/`components`/`types`/`lib` file changed. `unit_price`/`default_supplier` product-master columns and `customer_id`-based validation from the planning docs were rejected as out of scope (unused by any business module; `reorder_point` already lives per-warehouse in inventory).
- Sample Data Enrichment complete: `src/sample_data.py` rewritten (18 products/36 orders/17 inventory rows/27 invoices/17 customers), `sample_data/README_sample_data.md` (new), `sample_data/sample_customers.xlsx` (new), all 5 `sample_data/*.xlsx` regenerated, `tests/test_sample_data.py` rewritten (32 tests, up from 11). `uv run pytest` passes (172 tests, up from 152). End-to-end compatibility verified by running the real `validate_orders`/`allocate_inventory`/`calculate_payment_aging`/`report_export` pipeline against the newly generated files (28 valid/8 invalid orders spanning 8 distinct error codes; 26 fully/1 partially allocated/1 backordered + 3 supplier follow-ups; all 5 aging buckets + both data-issue types + 17 draft messages; all 3 Excel reports export without error).
- Mock-data pipeline reconnection decisions (via `/architect`, same session, user-directed "Option C"): `tests/contract_fixtures.py` stays exactly as-is — small, single-row, contract-shape fixtures for `test_contracts.py`/`test_report_export.py` only, never touched by or coupled to the UI mock-data pipeline again. `scripts/generate_mock_data.py` was rewritten in place (not a second script) to become the single sanctioned generator of `lib/mock-data/*.json`, reading `sample_data/*.xlsx` via each business module's own `load_*` helper (the same code path a real upload exercises) and running the real `validate_orders`/`allocate_inventory`/`calculate_payment_aging`/`report_export` pipeline — framed in its own docstring as a compatibility smoke test: a failure here means the committed sample Excel no longer matches what the Python loaders/business modules expect, not routine noise. `MOCK_AS_OF_DATE = date(2026, 7, 10)` and `MOCK_GENERATED_AT = datetime(2026, 7, 10, 9, 0, 0)` are fixed module-level constants (matching `sample_data/README_sample_data.md`'s stated generation date) passed into `calculate_payment_aging`/`report_export` so the committed JSON's aging buckets and `report_id`/`generated_at` values are deterministic across re-runs, not dependent on whatever day the script happens to run. `sample_customers.xlsx` is never read by this script — reference-only status holds all the way through the UI layer. `package.json` gained a manual-only `"mock-data"` alias, not wired into `build`/`lint`/`typecheck`. `lib/mock-data.ts`'s header comment updated to stop claiming the JSON comes from `tests/contract_fixtures.py`.
- Mock-data pipeline reconnection complete: `scripts/generate_mock_data.py` rewritten, `lib/mock-data.ts` comment corrected, `package.json` `mock-data` script added, all 4 `lib/mock-data/*.json` files regenerated from real sample data (28 valid orders, 28 allocation results/1 backorder/3 supplier follow-ups, 25 aging rows/2 data issues/17 draft messages, 3 report manifests — up from 1-2 rows per table). `uv run pytest` (172), `npm run typecheck`, `npm run lint`, and `npm run build` (all 9 routes still prerender statically) all clean after regenerating.
