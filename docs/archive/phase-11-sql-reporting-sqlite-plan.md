# Phase 11: SQL Reporting and Active Sample Dashboard

## Context

Phase 10 shipped a stateless FastAPI layer over the tested Python business core (`docs/adr/0006`), but the `/dashboard` page still reads static JSON generated once at build time by `scripts/generate_mock_data.py`. The goal of Phase 11 is to make the dashboard genuinely data-backed by real SQL — both to make the portfolio project demonstrate SQL fluency and to give the dashboard a live-computed feel — without reopening anything Phase 10 already settled (workflow uploads stay stateless/page-local) and without expanding into deployment (Phase 11.1, deferred) or business-rule scope (no new classifications; SQL reports on facts the tested Python modules already computed).

This plan is the output of a full `/grill-with-docs` session (`docs/grilling/phase-11-sql-reporting-and-active-dashboard/`, `docs/adr/0007-sql-reporting-seeds-from-tested-workflow-outputs.md`) followed by a full `/architect` session, both already confirmed decision-by-decision with the developer. Every decision below is locked; this document exists to hand it to implementation cleanly, with the developer's final precision tweaks folded in.

## Correction: re-verified against the actual post-Phase-10.2 dashboard

This plan was originally written against the pre-Phase-10.2 dashboard (three separate per-workflow KPI groups, ~15 tiles + a `SegmentedBar`). **Phase 10.2 has since been implemented** (uncommitted in the working tree as of this update) and materially consolidated `/dashboard`. Re-read `app/dashboard/page.tsx` and `context/ui-registry.md` directly rather than trusting the earlier "seven dashboard sections" framing. What actually changed:

- The three per-workflow KPI groups were replaced by **one 5-card "Overview" row**: Total Orders, Invalid Orders, Fully Allocated, Backordered, Overdue Amount. Every other KPI that used to appear on the dashboard (Duplicate Orders, Invalid SKUs, Missing Fields, Total Order Lines, Partially Allocated, Low Stock SKUs, Total Outstanding, High Priority Count, 90+ Days Amount) was **deliberately dropped from the dashboard** — per `ui-registry.md`, they remain available on each workflow page's own post-run summary, and `ui-registry.md` explicitly instructs "do not silently re-add dropped KPIs to `/dashboard`."
- The `SegmentedBar` (Valid/Invalid) was removed from the dashboard entirely, not relocated.
- `lib/mock-data.ts`'s `ninetyPlusDaysAmount` is no longer imported by `app/dashboard/page.tsx` at all (confirmed via grep) — `/payment-aging`'s live page already has its own page-local copy, unrelated to this file. `amountByAgingBucket` is still imported and used.
- The two chart cards (Allocation Status donut, Outstanding-by-Aging-Bucket bar chart) and the two tables (Inventory Shortage Alerts, Payment Follow-up Items) are **unchanged in data shape** — only layout/hover/tooltip polish was added (`DonutBreakdownChart` became a Client Component with hover/focus tooltips; both gained a `TableSectionHeading` `action` link). Their percentage-of-total tooltip math is computed **client-side** from the values already passed in — confirmed by reading both components' pattern notes in `ui-registry.md` — so no new backend percentage field is needed.

Net effect: the SQL-backed response is **smaller** than originally planned, not larger. `low_stock_sku_count` and everything sourced from `remaining_inventory` is no longer needed by any dashboard section, so **`remaining_inventory` is dropped from the schema** (5 tables, not 6). `total_order_lines` is no longer needed either — the donut computes its own center total by summing the three status counts it's given, client-side, as it always has.

## What we are building

A `Demo Reporting Database` (SQLite, disposable, rebuilt from the tested Python pipeline on every FastAPI startup) backing a new `GET /api/dashboard` endpoint. Exactly what the actual post-Phase-10.2 `/dashboard` needs moves from static mock JSON to real SQL query results: the 5-card Overview row (`total_orders`, `invalid_orders`, `fully_allocated_count`, `backordered_count`, `overdue_amount`), the Allocation Status donut (adds `partially_allocated_count`, chart-only), the Outstanding-by-Aging-Bucket chart, the Inventory Shortage Alerts table, and the Payment Follow-up Items table. Everything else on the page (Reports, Workflow nav cards, infographic, guide text) stays static. `GET /health` is added. Workflow upload pages are untouched.

## Locked architecture decisions

- **SQLite, not Postgres.** Read-only, deterministic, demo-scale data; no hosting/secrets surface needed for Phase 11.
- **Schema — exactly 5 tables** (revised down from 6 after re-verifying against the actual post-Phase-10.2 dashboard — see correction note above), each mirroring one Output Contract row family verbatim (columns matching `src/contracts.py`/`types/index.ts` field-for-field): `valid_order_lines`, `validation_errors`, `allocation_results`, `supplier_follow_ups`, `aging_rows`. No `remaining_inventory` — nothing on the dashboard reads `reorder_alert` or needs `low_stock_sku_count` anymore. No `products`/`customers`/`warehouses`/`backorders`/`payment_data_issues`/`draft_messages`/`report_manifests` — none of the in-scope sections need them, and adding them would violate this project's Field Scope Boundary discipline (no fields/tables for symmetry alone). Backorders are `allocation_results WHERE status = 'Backordered'`, not a separate table.
- **No forced JOIN.** Every Output Contract row is already denormalized (flat `customer_name`/`sku`/`warehouse` strings), so none of the in-scope sections need one. SQL breadth still shows honestly via `GROUP BY`, `SUM`, `COUNT`, `WHERE`, a `CASE`-based `ORDER BY` for business-order aging buckets, and a derived `gap_to_reorder_point` expression column.
- **Hand-written parameterized SQL, no ORM** — every query stays visible in `backend/reporting_db/queries.py`.
- **Seed source is the tested pipeline only** (`sample_data/*.xlsx` → `load_*` helpers → `validate_orders()` → `allocate_inventory()` → `calculate_payment_aging()` → insert results). The seed never independently re-derives a business classification (allocation status, aging bucket, follow-up priority, reorder alert) — see ADR 0007.
- **Pinned `as_of_date`.** New neutral module `src/demo_constants.py` holds `DEMO_AS_OF_DATE = date(2026, 7, 10)` and `DEMO_GENERATED_AT = datetime(2026, 7, 10, 9, 0, 0)`. Both `scripts/generate_mock_data.py` and the Phase 11 seed import from there — no redefinition, no backend-importing-from-scripts dependency. Using `date.today()` would collapse all sample invoices into "90+ Days" as real time passes beyond the sample data's fixed era.
- **Rebuilt on every FastAPI startup** via a lifespan hook calling `rebuild_demo_reporting_database(db_path)`. Same function is reused by tests (`tmp_path`, not `:memory:` — `:memory:` databases are private per-connection and don't compose with "rebuild, then query" as separate calls) and an optional manual debug script. The app must never depend on a developer remembering to run something manually.
- **Atomic rebuild** (developer's tweak #2): write into a temp file in the same directory as the target (`backend/data/`), seed it fully, then atomically replace the final file (`os.replace`) only after seeding succeeds. Prevents a broken/partial SQLite file if startup fails halfway through seeding. The temp-build step should be factored into its own function so a failure point can be injected/monkeypatched in a test.
- **Env values resolved at call-time, not import-time.** `DEMO_REPORTING_DB_PATH` (and `CORS_ALLOWED_ORIGINS`) must be read from `os.environ` inside the functions that use them (the lifespan hook, the query/router functions) — never captured into a module-level constant at import time. If `backend/main.py` or `backend/reporting_db/schema.py` computed the DB path once at import, a test's `monkeypatch.setenv("DEMO_REPORTING_DB_PATH", ...)` would silently do nothing, since the module would already have resolved and cached the old value before the test ever ran.
- **Fresh `sqlite3.connect(db_path)` per call** (rebuild or query) — not one shared connection on `app.state`. FastAPI's sync `def` handlers run in a thread pool, and `sqlite3` connections aren't safe to share across threads by default. Cheap enough at this scale.
- **`DashboardResponse` lives in `backend/reporting_db/queries.py`**, not `src/contracts.py` — it's a dashboard aggregate, not a spec-derived Output Contract family (matches the existing precedent that `OrderValidationResult`/`InventoryAllocationResult`/`PaymentAgingResult` are all local envelope dicts, never merged into `contracts.py`). **Fields are trimmed to exactly what the current dashboard renders** (re-verified, see correction note): `order_validation` carries only `total_orders`/`invalid_orders`; `allocation` carries only `fully_allocated_count`/`partially_allocated_count`/`backordered_count` (`partially_allocated_count` feeds the donut only, no KPI card); `payment_aging` carries only `overdue_amount`. No `ninety_plus_days_amount` field — that KPI card doesn't exist on the dashboard anymore.
  ```python
  class DashboardOrderValidationSummary(TypedDict):
      total_orders: int
      invalid_orders: int

  class DashboardAllocationSummary(TypedDict):
      fully_allocated_count: int
      partially_allocated_count: int
      backordered_count: int

  class DashboardPaymentAgingSummary(TypedDict):
      overdue_amount: float

  class DashboardAgingBucketTotal(TypedDict):
      aging_bucket: str
      outstanding_amount: float

  class DashboardShortageAlertRow(TypedDict):
      sku: str
      warehouse: str
      remaining_qty: int
      reorder_point: int
      gap_to_reorder_point: int
      supplier_name: str | None
      lead_time_days: int | None

  class DashboardFollowUpRow(TypedDict):
      invoice_id: str
      customer_name: str
      outstanding_amount: float
      days_overdue: int
      aging_bucket: str
      follow_up_priority: str

  class DashboardResponse(TypedDict):
      order_validation: DashboardOrderValidationSummary
      allocation: DashboardAllocationSummary
      payment_aging: DashboardPaymentAgingSummary
      aging_bucket_totals: list[DashboardAgingBucketTotal]
      inventory_shortage_alerts: list[DashboardShortageAlertRow]
      payment_follow_up_items: list[DashboardFollowUpRow]
  ```
  `total_orders` is computed as `(SELECT COUNT(*) FROM valid_order_lines) + (SELECT COUNT(DISTINCT row_number) FROM validation_errors WHERE severity = 'Error')` — mirrors `order_validation.py`'s own `total_orders - invalid_orders = valid_orders` identity, just read from the two row-level tables instead of a precomputed summary. `invalid_orders` itself must count distinct `row_number`s with at least one `Error`-severity row, **not** a raw `COUNT(*)` on `validation_errors` — a row can carry multiple error rows (e.g. one `OV-001` per missing field), and a `severity = 'Warning'`-only row (e.g. blank `payment_terms`, OV-007) is still a valid order, not an invalid one.
- **Query wrappers own display-guarantee normalization** (developer's tweak #5): SQL computes counts/sums/groups; the thin Python wrapper around each query guarantees all 5 aging buckets are present in business order, numeric values default to `0` (never `null`/missing), and table rows are sorted in a business-useful order (e.g. shortage alerts by largest gap-to-reorder first, follow-up items by priority/days-overdue).
- **`/dashboard` becomes an async Server Component.** Uses `fetch(..., { cache: "no-store" })` via a small server-side fetch helper (not `lib/api-client.ts`, which is browser-oriented) — reads `API_BASE_URL ?? NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"`. Wrapped in try/catch rendering `BusinessErrorMessage` on failure. No loading spinner — this is a read-only page with no user-triggered request lifecycle, distinct from the Client Component `RequestStatus` pattern the 3 workflow pages use. The helper handles both failure modes: a network/fetch-level failure (server unreachable) and a non-2xx response with a JSON `{"detail": "..."}` body (reusing the same Business Error shape the workflow pages already parse) — falling back to a generic "dashboard unavailable" message only if the response can't be parsed at all.
- **Explicit dynamic rendering** (developer's tweak #1): also export `export const dynamic = "force-dynamic";` alongside `cache: "no-store"`, to make the intent explicit rather than relying on inference. **Verified against the installed Next.js 16.2.10 docs** (`node_modules/next/dist/docs/`): this project's `next.config.ts` does not enable `cacheComponents`, so the `dynamic` route segment config is still active (it is only removed when Cache Components mode is on). `cache: "no-store"` alone would already force per-request fetching and dynamic rendering, so this export is redundant-but-explicit today — worth a one-line code comment noting that if Cache Components mode is ever enabled in this project, `dynamic` exports are removed entirely and this line would need to migrate to that model's approach.
- **CORS**: `CORS_ALLOWED_ORIGINS` env var, default `http://localhost:3000`, replacing the hardcoded list in `backend/main.py`. Parsing is precise (developer's tweak #6): split on `,`, `.strip()` each entry, drop empty strings — so trailing commas or accidental whitespace in the env value don't produce a bad origin list.
- **DB path**: `DEMO_REPORTING_DB_PATH` env var, default `backend/data/demo_reporting.sqlite`. Seed function creates the parent directory (`mkdir(parents=True, exist_ok=True)`) before writing (developer's tweak #3). `.gitignore` gains the narrow rule `backend/data/*.sqlite`.
- **Test isolation** (developer's tweak #7): any test that instantiates `TestClient(app)` triggers real lifespan seeding. Backend dashboard/health tests must set `DEMO_REPORTING_DB_PATH` (via `monkeypatch.setenv`, pointed at `tmp_path`) before constructing the `TestClient`, so test runs never write to the default local `backend/data/demo_reporting.sqlite`.
- **Frontend TS types** (developer's tweak #4): mirror `DashboardResponse` and its section types in the frontend, snake_case preserved (no camelCase adapter, consistent with every other contract in this project). Given `types/index.ts`'s existing header comment ties it strictly to `context/ui-contract-plan.md`-mirrored Output Contracts, and `DashboardResponse` is explicitly *not* an Output Contract, these types go in a new `types/dashboard.ts` rather than being folded into `types/index.ts` — with a short header comment stating it mirrors `backend/reporting_db/queries.py`, not `src/contracts.py`, so a future contributor doesn't "fix" the asymmetry by merging it into the Output Contract file for symmetry.
- **`GET /health` stays minimal.** Returns a plain `{"status": "ok"}` with no database query — Phase 11 doesn't need DB-readiness checking; if a deployment health check needs to verify the database specifically, that's a Phase 11.1 concern to add then, not now.
- **`lib/mock-data.ts` trimming is narrow.** Only remove the dashboard-specific client-side aggregation helpers (`ninetyPlusDaysAmount`, `amountByAgingBucket`) once nothing references them. Keep every other export (`reportManifests`, the three per-workflow result objects) — `/reports` and the dashboard's static Reports section still read from this file, and the 3 workflow pages' mock-data imports (if any remain) are untouched by Phase 11.

## Module layout

```
src/
  demo_constants.py          # DEMO_AS_OF_DATE, DEMO_GENERATED_AT
backend/
  reporting_db/
    __init__.py
    schema.py                 # CREATE TABLE DDL + rebuild_demo_reporting_database(db_path)
    queries.py                 # hand-written SQL + DashboardResponse/section TypedDicts + display-guarantee wrappers
  routers/
    dashboard.py               # GET /api/dashboard
    health.py                   # GET /health
types/
  dashboard.ts                 # DashboardResponse + section types, mirrors queries.py, snake_case
lib/
  dashboard-server.ts           # server-side fetch helper (not lib/api-client.ts)
```

## Existing code to reuse (not reinvent)

- `scripts/generate_mock_data.py`'s pipeline-invocation pattern (`load_*` → `validate_orders` → `allocate_inventory` → `calculate_payment_aging`) is the template for the seed function's data-loading step.
- `backend/uploads.py` / `backend/errors.py` establish the "convert technical exceptions to business-readable `{"detail": ...}`" boundary pattern — the dashboard router should follow the same shape for its own error paths.
- `tests/backend_test_helpers.py` (`SAMPLE_DATA_DIR`, `XLSX_MEDIA_TYPE`) — reuse for any new backend test needing sample files.
- `components/feedback/BusinessErrorMessage` (already used by the 3 workflow pages) — reuse directly in the new Server Component error path, don't build a second error-message component.
- `AGENTS.md`/`context/library-docs.md`'s existing instruction to read installed framework docs under `node_modules/` before implementing framework-specific behavior — already applied above for the `dynamic` export decision.

## Build order

1. `src/demo_constants.py`; update `scripts/generate_mock_data.py` to import `DEMO_AS_OF_DATE`/`DEMO_GENERATED_AT` from it instead of defining `MOCK_AS_OF_DATE`/`MOCK_GENERATED_AT` locally. Update that file's own inline comment/docstring (currently describing these as module-level constants defined right there) to point at `src/demo_constants.py` as the source, so a future reader isn't misled about where the pinned date actually lives. **Scope this narrowly**: only `scripts/generate_mock_data.py`'s own comments need updating — `memory.md`, `context/progress-tracker.md`, and `docs/plan/sample-data-enrichment/*` all reference `MOCK_AS_OF_DATE` as accurate point-in-time records of a past session and should not be rewritten; they describe what was true when written, not the current state of the code.
2. `backend/reporting_db/schema.py`: DDL for the 5 tables + `rebuild_demo_reporting_database(db_path)` (atomic temp-file-then-replace, `mkdir(parents=True, exist_ok=True)`, runs the tested pipeline with `DEMO_AS_OF_DATE`, inserts rows).
3. `backend/reporting_db/queries.py`: `DashboardResponse` + section TypedDicts, one query function per section, each wrapped with its display-guarantee normalization (5 buckets always present, `0` defaults, sorted order).
4. `backend/routers/dashboard.py` (`GET /api/dashboard`) and `backend/routers/health.py` (`GET /health`); wire into `backend/main.py`.
5. FastAPI lifespan hook in `backend/main.py` calling `rebuild_demo_reporting_database()`; `CORS_ALLOWED_ORIGINS` env-driven with trim/empty-filtering.
6. `.gitignore`: add `backend/data/*.sqlite`.
7. `types/dashboard.ts`; `lib/dashboard-server.ts` (server-side fetch helper, `API_BASE_URL ?? NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"`).
8. Rewrite `app/dashboard/page.tsx` as an async Server Component: `export const dynamic = "force-dynamic";`, `fetch(..., { cache: "no-store" })`, try/catch → `BusinessErrorMessage` on failure, no loading spinner. **Preserve the current (post-Phase-10.2) JSX structure exactly** — the 5-card Overview row, both chart cards (including their `TableSectionHeading` `action` links and `min-h-48 flex flex-col justify-center` wrappers), both tables, and every static section — only swap `orderValidationResult.summary`/`inventoryAllocationResult.summary`/`paymentAgingResult.summary`/`amountByAgingBucket(...)`/`supplier_follow_ups`/`followUpItems` for the fetched `DashboardResponse`'s equivalent fields. Do not touch `SidebarNav.tsx`, `Button.tsx`, `MetricCard.tsx`, `DonutBreakdownChart.tsx`, or `VerticalBucketBarChart.tsx` — none of Phase 10.2's visual work is in scope here. Remove `amountByAgingBucket` from `lib/mock-data.ts` once the dashboard no longer imports it. `ninetyPlusDaysAmount` is already unused by the dashboard (confirmed via grep — `/payment-aging`'s live page has its own unrelated page-local copy) and can be removed from `lib/mock-data.ts` in the same pass.
9. Tests (any test using `TestClient(app)` must call `monkeypatch.setenv("DEMO_REPORTING_DB_PATH", str(tmp_path / "test.sqlite"))` **before** constructing `TestClient` — this only works because env values are resolved at call-time per the decision above, not captured at import time):
   - `tests/test_reporting_db.py`: schema creation, rebuild idempotency, expected row counts against real `sample_data/*.xlsx`. For the atomic-rebuild guarantee, don't try to assert atomicity directly (hard to prove without overfitting to internals) — instead test the observable behavior: seed successfully once, then trigger a rebuild whose temp-build step is monkeypatched to fail partway through, and assert the *existing* database file is untouched and still readable/queryable. The public `rebuild_demo_reporting_database(db_path)` signature stays exactly as clean as described above — testability comes from factoring the temp-build step into a small internal helper function that the test monkeypatches directly, not from adding test-only parameters or complexity to the public function.
   - Query-function correctness: each query's output matches values independently known from the existing tested pipeline (e.g. `28` valid order lines, matching `tests/test_backend_inventory.py`'s existing assertion).
   - `tests/test_backend_dashboard.py`: `TestClient` `GET /api/dashboard` returns 200 with the full `DashboardResponse` shape and spot-checked values; `GET /health` returns 200 with `{"status": "ok"}`.
10. Verify: `uv run pytest`, `npm run typecheck`/`lint`/`build` all clean. Live-browser check of `/dashboard` with FastAPI running (confirm real SQL values render) and with FastAPI stopped (confirm the `BusinessErrorMessage` fallback renders instead of a crash).
11. Docs: update `context/build-plan.md` (add Phase 11), `context/architecture.md` (Demo Reporting Database + dashboard API), `context/library-docs.md` (sqlite3/stdlib conventions) as part of this implementation pass. `context/progress-tracker.md` and `docs/plan/phase-11-sql-reporting-active-dashboard/` come after implementation is complete, per the developer's original instruction.

## Verification

- `uv run pytest` — all existing tests still pass, plus new Phase 11 tests (schema/seed/query/endpoint coverage above).
- `npm run typecheck && npm run lint && npm run build` — clean; `/dashboard` should appear as a dynamically-rendered route in the build output (not statically prerendered), which is expected and new for this route specifically.
- Manual: start both dev servers, load `/dashboard`, confirm KPI numbers match the known sample-dataset values already asserted elsewhere in the test suite (e.g. 28 valid order lines). Stop the FastAPI server, reload `/dashboard`, confirm `BusinessErrorMessage` renders cleanly instead of a Next.js error page.

---

**Archive note:** This was the original, fully `/grill-with-docs` + `/architect`-approved Phase 11 plan (SQLite `Demo Reporting Database`, rebuilt from `sample_data/*.xlsx` on every startup). It was paused mid-implementation in favor of shipping the deployment baseline first (working code from this plan is preserved in git stash — see `memory.md`'s "Phase 11 Pivot" session entry for the stash message and contents). It was formally superseded, not completed, by **ADR 0007 (Session-Scoped Workflow Result Persistence in Postgres)** for Phase 12 — the actual Postgres design is session-specific and stores real visitor results in a JSONB latest-result table, materially different from this SQLite, demo-dataset-only, SQL-reporting approach. Kept here for future study, e.g. if a later phase wants real cross-session SQL analytics over demo or aggregated data, which is a different problem than what Phase 12 solves.