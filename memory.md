# Memory — Phase 9 + Phase 9.1: Reusable UI Components, Static Pages, Visual Alignment Fixes + PR #8

Last updated: 2026-07-10

## What was built

- **Phase 9 (prior commit `a7dcf1a`, already on this branch before this session started):** the 12 registry components (AppShell, SidebarNav, TopHeader, MetricCard, WorkflowStepper, UploadPanel, StatusBadge, DataTable, ReportCard, EmptyState, LoadingState, BusinessErrorMessage) and the 5 routes (`/dashboard`, `/order-validation`, `/inventory-allocation`, `/payment-aging`, `/reports`) filled in as a static showcase against committed mock JSON.
- **Phase 9.1 Visual Alignment Fixes (this session, commit `9e930d5`):** a large multi-addendum pass reconciling the built UI against the 4 original Figma Make prototypes:
  - Critical layout fix: `AppShell`/`SidebarNav` switched from `min-h-screen` to a fixed `h-screen overflow-hidden` shell with independently scrolling sidebar and main content.
  - New `components/charts/DonutBreakdownChart.tsx` and `VerticalBucketBarChart.tsx` (pure SVG/CSS, no charting library) replacing simpler bar treatments on the dashboard for Allocation Status and Outstanding-by-Aging-Bucket; both have zero-value guards (neutral ring+"0" for donut, `EmptyState` caption for bars).
  - New `components/tables/`: `FilterToolbar.tsx` + `FilterSelect.tsx` (client-side search/filter bars), `MiniBar.tsx`/`SegmentedBar.tsx`/`AgingBucketBars.tsx` (inline visualizations), `TableSectionHeading.tsx` (icon+title+caption header) — used across all workflow tables.
  - Dashboard gained "Inventory Shortage Alerts" and "Payment Follow-up Items" tables, a "How the Workflows Connect" infographic, and a "How This Demo Works" guide section (English only, by explicit user choice).
  - Table density/tag/typography overhaul, extended sort coverage, `align`/`wrap` column flags, truncate+`title` tooltips on long text, download actions (disabled, static-showcase-appropriate) across Order Validation, Inventory Allocation, Payment Aging.
  - New derived display-only aggregates documented in `context/ui-contract-plan.md`: "Gap to Reorder Point" (never call it "suggested reorder quantity") and "Outstanding amount by aging bucket".
  - `docs/plan/phase-9.1-visual-alignment-fixes/` (via `/feature-docs`) and `docs/architect/phase-9-9.1-reusable-ui-and-visual-alignment/` (via `/session-docs`, synthesizing both `/architect` sessions) written this session.
  - `docs/diagnosing-bugs/phase-9-1-hydration-extension-warning/` also exists on disk (a `/recover`-style diagnosis of a hydration warning) — committed alongside Phase 9.1 since it's clearly part of this same body of work, though its creation wasn't part of this session's visible transcript.
- **Phase 9.1 Review Findings Fix (same commit `9e930d5`, folded into the same push):** 4 narrow pre-commit findings fixed directly (no new `/architect` plan-mode round needed beyond confirming scope):
  1. `FilterToolbar.tsx` search input — added `aria-label={search.placeholder ?? "Search"}`.
  2. `app/payment-aging/page.tsx` — replaced plain "As of {date}" text with a real, labeled, disabled `<input type="date">` (via `useId()`, same pattern as `UploadPanel.tsx`), prefilled from `report.generated_at.slice(0, 10)`, `title` explaining live wiring arrives in Phase 10.
  3. `app/inventory-allocation/page.tsx` — restored `starting_available_qty` ("Starting Qty") and `allocated_qty` ("Allocated Qty") columns to `REMAINING_INVENTORY_COLUMNS`.
  4. `memory.md` confirmed excluded from staging throughout.
- **Git:** committed as `9e930d5` ("feat: add Phase 9.1 visual alignment fixes", 34 files) on `phase/9-reusable-ui-components-static-pages`, pushed. This updated the **already-existing PR #8** (opened previously for the Phase 9 commit `a7dcf1a`, `base=phase/8-nextjs-frontend-foundation`) rather than creating a new PR — PR #8 now shows 2 commits. https://github.com/gwho/sales-ops/pull/8
  - Deliberately left `docs/architect/phase-8-nextjs-frontend-foundation/` and `sample_excel_data_requirements/` unstaged — both untracked, both unrelated to Phase 9.1 (the former belongs conceptually on the Phase 8 branch, not Phase 9; the latter is new unrelated spec material the user had just opened in the IDE, not part of this work).

## Decisions made

1. **Static showcase discipline held throughout Phase 9.1** — despite 6 large sequential scope-expanding addenda (filter bars, table density, dashboard visuals, guide/infographic, advanced table UX, chart swap), no fake async state machines, no fake loading/upload logic, no live API calls were introduced. Every addendum was still mock-data-driven.
2. **Charts live in `components/charts/`, not `components/tables/`** — a dedicated taxonomy split from table-adjacent visualizations (`MiniBar`/`SegmentedBar`/`AgingBucketBars` stay in `tables/`), reserved for whole-chart cards.
3. **No dynamic Tailwind class construction anywhere** — every tone→class mapping (`DonutBreakdownChart`, `VerticalBucketBarChart`, `MiniBar`, `SegmentedBar`, `Badge`) uses a literal `Record<Tone, string>` object, never a template-string interpolation like `` `bg-${tone}` ``. Verified via grep at the end of the chart-addendum work.
4. **Chart components never decide their own colors** — callers resolve `Tone` via the existing `allocationStatusTone`/`agingBucketTone` helpers from `StatusBadge.tsx` and pass it in as a prop, so a chart segment and a table badge for the same status can never visually drift apart.
5. **No implied currency in amount displays** — no contract field carries a currency code, so chart/table amount captions stay neutral ("Outstanding amount by bucket"), never "$" or "Total Outstanding: $X".
6. **RSC/Client boundary: whole pages become Client Components**, not just `DataTable` — any page constructing a `DataTable` columns config with `render`/`sortValue` functions must itself carry `"use client"`, since Server Components cannot pass functions as props.
7. **Payment Aging date selector is a real disabled `<input type="date">`, not decorative text** — satisfies `ui-contract-plan.md`'s "UploadPanel + date selector" composition requirement without pretending it changes results before Phase 10's live API wiring.
8. **Header-level per-column filter popovers explicitly rejected** for Phase 9.1 — filtering stays in the visible `FilterToolbar`, sorting stays in column headers; no second filter system layered on top.

## Problems solved

- **Critical sidebar-height bug**: `min-h-screen` on both the outer shell and the sidebar caused the whole page (not just main content) to scroll, breaking the fixed-sidebar look from the Figma prototypes. Fixed via `h-screen overflow-hidden` (outer) + `h-full overflow-hidden` (content column) + `h-full overflow-y-auto` (sidebar).
- **RSC function-prop build failure**: `next build` failed with "Functions cannot be passed directly to Client Components" — root cause was `DataTable` column configs carrying `render`/`sortValue` functions while the pages building those configs were still Server Components. Fixed by adding `"use client"` to all 3 affected pages.
- **`Badge.tsx` TS nullable-index error**: `cva`'s `VariantProps` makes `tone` nullable, but `DOT_TONE_CLASSES[tone]` needs a non-null key — fixed with `const resolvedTone = tone ?? "neutral"`.
- **Stray macOS Finder-duplicate `.next/types` files** (`routes.d 2.ts` etc.) caused a spurious `tsc` duplicate-identifier error — fixed with `rm -rf .next && npm run build` (safe, gitignored build output).
- **Figma MCP Starter-plan rate limit** (6 read-calls/month) was exhausted mid-screenshot-capture (3 of 5 routes done) — fell back to the user's own pre-documented plan: manually-provided developer screenshots, confirmed via `AskUserQuestion`.
- **Verification false negative**: a first curl-based grep pass (port 3050) for `aria-label="..."` found nothing due to RSC-serialized HTML formatting, not a real missing fix — a second pass (port 3051) with corrected patterns confirmed the `aria-label`, the "As of Date" label, and the prefilled date value all render correctly.

## Current state

- `main`: still only PR #1 merged, stale locally — unchanged this session.
- PR #2 through #6: unchanged, still open, stacked.
- **PR #7 (Phase 8 → PR #6's branch)**: unchanged this session, still open. https://github.com/gwho/sales-ops/pull/7
- **PR #8 (Phase 9 + 9.1 → PR #7's branch)**: updated this session, now 2 commits (`a7dcf1a` Phase 9, `9e930d5` Phase 9.1), still open. https://github.com/gwho/sales-ops/pull/8
- Local checkout is on `phase/9-reusable-ui-components-static-pages`.
- 152 pytest tests passing (Python untouched all session). `npm run build`/`lint`/`typecheck` all clean as of the final verification pass.
- `context/progress-tracker.md`: Current Status = "Phase 9.1 - Visual Alignment Fixes (complete)". `context/ui-registry.md`: fully populated — all Phase 9 + 9.1 components documented, including a new "Charts" section and a "Page composition notes (Phase 9.1)" section.
- Two untracked, uncommitted items remain in the working tree, deliberately left alone (not part of Phase 9.1): `docs/architect/phase-8-nextjs-frontend-foundation/` (belongs on the Phase 8 branch conceptually) and `sample_excel_data_requirements/` (new unrelated spec material the user has open in the IDE — purpose/next steps unknown, not discussed this session).

## Next session starts with

1. User's call: start Phase 10 (live API layer — FastAPI wrapping the tested Python modules, wiring the Payment Aging date selector and UploadPanel for real) — this is the next hard-gated milestone per `CLAUDE.md`'s Phase 8/9/10 sequencing.
2. **Before Phase 10 work**: re-check live merge status of PR #2 through #8 (don't assume) and branch off whichever is the current tip — standing rule, now confirmed across Phases 4–9.1.
3. Clarify with the user what `sample_excel_data_requirements/` is for — it's untracked, recently edited (same day), and was opened in the IDE right before this session's commit/push/PR/remember-save request, but was never discussed. It may be new scope, a separate project, or leftover scratch material — don't assume either way.
4. `docs/architect/phase-8-nextjs-frontend-foundation/` exists on disk but is uncommitted — confirm with the user whether it should be committed to the Phase 8 branch/PR #7, or elsewhere, since it wasn't produced by this session's tracked `/session-docs` invocation.

## Open questions

Carried forward from the Phase 8 session (still genuinely unresolved — do not treat any decision above as having silently resolved these):

- Whether/when to merge PR #2 through #8 is the user's call — not decided this or any prior session.
- Whether to eventually retrofit the pre-Phase-6 `docs/plan/*` folders to match `/feature-docs`'s real template — deferred, procedure documented in persistent cross-session memory (`docs_plan_feature_docs_gap.md`), not scheduled.
- camelCase vs. snake_case adapter layer for the eventual FastAPI/TS boundary — not decided; relevant again once Phase 10 (API layer) starts.
- Whether to reintroduce derived shorthand Payment Aging badges (Paid/Overdue) — not decided.
- Whether/how to address `/model sonnet` being unavailable in this environment — unresolved, unclear if in-scope for this project vs. a harness/environment issue; not raised again this session.

New this session, not yet resolved:

- Purpose of `sample_excel_data_requirements/` and whether/how it relates to this project (see Next session item 3).
- Disposition of the uncommitted `docs/architect/phase-8-nextjs-frontend-foundation/` docs (see Next session item 4).

---

# Memory — Sample Data Enrichment + Mock-Data Pipeline Reconnection

Last updated: 2026-07-11 (appended; prior session content above is unchanged)

## What was built

- `src/sample_data.py` rewritten: fictional regional medical optics/healthcare equipment scenario (inspired by a ZEISS Far East-style operating model, fully fictional — no real names/products/pricing), HK + Mainland China customers, HK/China/Europe warehouses. `generate_product_master()` → 18 SKUs (2 inactive). `generate_orders()` → 36 rows, 7 issue-bearing (~19%), several rows combining more than one intentional issue. `generate_inventory()` → 17 rows across 3 warehouses (`PART-CAL-015` has zero rows to guarantee a full backorder; `DIAG-TONO-007`/HK stays below reorder point through allocation). `generate_invoices()` → 27 rows covering all 5 aging buckets, all 3 payment states, 1 missing-due-date issue, 1 invalid/negative-amount issue, 1 deliberate overpayment, plus a new optional `order_id` column. New `generate_customers()` → 17-row `sample_customers.xlsx`, explicitly reference-only, read by zero `src/` modules.
- `sample_data/README_sample_data.md` — new: fictional-data disclosure, determinism approach, per-file schema table, demo workflow, full intentional-issue list with exact row IDs.
- `tests/test_sample_data.py` rewritten — 32 tests (up from 11), covering every new issue type plus the new `generate_customers()`.
- All 5 `sample_data/*.xlsx` regenerated and committed (including the new `sample_customers.xlsx`).
- `scripts/generate_mock_data.py` rewritten in place: now derives `lib/mock-data/*.json` from the real `sample_data/*.xlsx` pipeline (`validate_orders` → `allocate_inventory`, independently `calculate_payment_aging`, plus `report_export` manifests) instead of `tests/contract_fixtures.py`. New pinned constants `MOCK_AS_OF_DATE = date(2026, 7, 10)` / `MOCK_GENERATED_AT = datetime(2026, 7, 10, 9, 0, 0)` for determinism. Loads via each business module's own `load_*` helper (real upload code path), framed in its docstring as a compatibility smoke test.
- `lib/mock-data.ts` header comment corrected — no longer claims JSON comes from `tests/contract_fixtures.py`.
- `package.json` gained `"mock-data": "uv run python scripts/generate_mock_data.py"` (manual-only, not wired into `build`/`lint`/`typecheck`).
- `context/progress-tracker.md` updated (Current Status + 4 new Decisions Made entries, two follow-on paragraphs covering both halves of this session).
- `docs/plan/sample-data-enrichment/{plan.md,explanation.md,ai-discussion-topics.md}` written via `/feature-docs`, then `plan.md`/`explanation.md` updated again with a mock-data-pipeline addendum.
- Confirmed untouched (via `git diff --stat`, empty): `tests/contract_fixtures.py`, `src/order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, `report_export.py`, `contracts.py`, `app/`, `components/`, `types/`.

## Decisions made

- Scenario is fictional, "inspired by a ZEISS Far East-style operating model" — no real company/product/customer/pricing data anywhere; verified via case-insensitive grep (zero matches for "ZEISS" in generated content/docs).
- Sample-data generation stays hand-authored literal deterministic rows — no `random`/seed module, even though the planning docs describe a "fixed seed" strategy; `README_sample_data.md` documents "deterministic by construction" instead, so shipped docs match shipped code.
- Orders hold ~19% issue-bearing rows by combining multiple issues onto the same row (not one row per issue type) — a user-directed correction to an earlier draft that was closer to a disguised test matrix.
- `sample_customers.xlsx` is strictly reference-only — no loader/validation function anywhere in `src/`, never wired into the mock-data pipeline either.
- Mock-data pipeline ("Option C", user-directed): `tests/contract_fixtures.py` stays permanently as small, contract-shape-only fixtures (used only by `test_contracts.py`/`test_report_export.py`); `scripts/generate_mock_data.py` rewritten in place (not a second script) as the single source of `lib/mock-data/*.json`. This reverses the earlier Phase 8/9 assumption that sample-data changes never require a frontend data refresh — `lib/mock-data/*.json` is now genuinely coupled to `sample_data/*.xlsx` and must be regenerated (`npm run mock-data`) after any future sample-data change.
- Built-in Plan Mode was treated as satisfying `08_agent_instructions_with_skills.md`'s "`/architect` before coding" requirement for the sample-data-enrichment half; the actual `/architect` skill was invoked (at the user's explicit request) for the later mock-data-pipeline decision.

## Problems solved

- Test bug: `paid_amount > invoice_amount` overpayment check false-positived against a deliberately negative `invoice_amount` row (`0 > -500` is true) — fixed by filtering to `invoice_amount >= 0` first.
- Non-deterministic aging buckets: an early ad-hoc verification run of `calculate_payment_aging` with no `as_of_date` produced different bucket counts than the final pinned run (one invoice crossed a bucket boundary between runs) — concrete evidence pinning `MOCK_AS_OF_DATE`/`MOCK_GENERATED_AT` was necessary, not just tidy.
- Duplicate-order-id design: confirmed by running the real pipeline that `OV-002` flags *both* occurrences of a duplicated `order_id` as invalid, not just the second — so the "clean-looking" first occurrence (`SO-2026-010`, a `PART-BULB-013` order) never reaches allocation either.

## Current state

- `uv run pytest`: 172 passing (up from 152).
- `npm run typecheck`, `npm run lint`, `npm run build`: all clean; all 9 routes still prerender statically against the much larger real dataset (28 valid orders, 25 aging rows, etc. — up from 1-2 rows per table).
- `/project-review` run: 0 blocking issues across all 3 layers. 1 minor, non-blocking suggestion: manually eyeball `/order-validation` and `/payment-aging` in a running dev server to confirm table density/scrolling at real row counts — not yet done (build-time static prerender succeeded but no live-browser check performed).
- **This session's work is now committed and pushed**: commit `745ac10` ("feat: enrich sample Excel data and regenerate UI mock JSON") on `phase/9-reusable-ui-components-static-pages`, pushed to `origin`. This commit also swept in the two previously-untracked items from the prior session — `docs/architect/phase-8-nextjs-frontend-foundation/` and `sample_excel_data_requirements/` — both are now tracked and committed, resolving that open loose end.
- Working tree fully clean (verified via `git status --porcelain`) other than `memory.md` itself.
- **Live PR status (re-checked via `gh pr list --state all`, not assumed):**
  - PR #1 (`phase/1-python-foundation` → `main`) — **MERGED**.
  - PR #2 (`phase/3-order-validation-core` → `main`) — OPEN.
  - PR #3 (`phase/4-inventory-allocation-core` → PR #2's branch) — OPEN.
  - PR #4 (`phase/5-payment-aging-core` → PR #3's branch) — OPEN.
  - PR #5 (`phase/6-excel-report-export` → PR #4's branch) — OPEN.
  - PR #6 (`phase/7-ui-contract-wireframe-planning` → PR #5's branch) — OPEN.
  - PR #7 (`phase/8-nextjs-frontend-foundation` → PR #6's branch) — OPEN.
  - PR #8 (`phase/9-reusable-ui-components-static-pages` → PR #7's branch) — OPEN, now **3 commits** (`a7dcf1a` Phase 9, `9e930d5` Phase 9.1, `745ac10` sample-data enrichment). This session's work landed in PR #8, not a new PR — the branch is unchanged from prior sessions, just advanced.
  - `main` is still only PR #1 merged, stale locally, unchanged.

## Next session starts with

1. Phase 10 (FastAPI Integration) is the next hard-gated milestone per `CLAUDE.md`/`progress-tracker.md` — nothing blocks starting it now. The mock-data pipeline is genuinely real (derived from `sample_data/*.xlsx` via the actual business modules), so the UI already reflects true output shapes; Phase 10 just needs to live-wire the UploadPanel and Payment Aging date selector instead of reading static JSON.
2. Optional, not blocking: the live-browser density/scrolling spot-check of `/order-validation` and `/payment-aging` from `/project-review`'s minor suggestion — still not done.
3. Standing rule (confirmed again this session): re-check live PR merge status before assuming, don't rely on memory of prior sessions — statuses above were current as of 2026-07-11.

## Open questions

- Whether/when to merge PR #2 through #8 — still the user's call, not decided by any session so far.
- Whether the minor live-browser-check suggestion from `/project-review` is worth doing before moving on — not decided.
- camelCase vs. snake_case adapter layer for the eventual FastAPI/TS boundary — not decided; relevant again once Phase 10 starts.
- Whether to reintroduce derived shorthand Payment Aging badges (Paid/Overdue) — not decided (carried from Phase 9 session, still open).
- `docs/architect/phase-8-nextjs-frontend-foundation/` disposition question is now **resolved** — it was committed as-is to PR #8's branch rather than moved to the Phase 8 branch/PR #7. No further action needed unless the user objects.

---

# Memory — Phase 10: FastAPI Integration + Review/Fix/Recover Cycle

Last updated: 2026-07-12 (appended; all prior session content above is unchanged)

## What was built

- **Planning (this session):** `/grill-with-docs` (`/grilling` + `/domain-modeling`) resolved the stateless architecture and terminology, producing `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md` and 7 new `CONTEXT.md` terms (Workflow Request, Workflow Result, Current Result, Report Export Request, Report Artifact, Sample File, Business Error). Then `/architect` (via Plan Mode, one rejection round with 4 corrections) produced the approved implementation plan. Both sessions documented via `/session-docs` to `docs/grilling/phase-10-fastapi-integration/` and `docs/architect/phase-10-fastapi-integration/` (the latter also got a verbatim `approved-plan.md` copy on request).
- **`backend/` (new FastAPI package):** `main.py` (app + CORS + exception handlers), `errors.py` (`RequestValidationError` normalizer + generic 500 handler), `uploads.py` (shared `.xlsx` validation), `routers/{orders,inventory,payments,templates}.py`. Endpoints: `POST /api/orders/validate(/report)`, `POST /api/inventory/allocate(/report)` (runs `validate_orders` internally before `allocate_inventory`), `POST /api/payments/aging(/report)` (required `as_of_date`), `GET /api/templates/{name}` (allowlisted sample-file downloads). No `GET /api/reports/{report_id}` — stateless per ADR 0006, reports always recompute from re-submitted files.
- **Frontend:** new `lib/api-client.ts` (low-level fetch/error/blob mechanics, not a shared hook). All 3 workflow pages live-wired with page-local `RequestStatus`/`currentResult`/`errorDetail`/`ReportRequestState`, an explicit "Run" button, and a mid-session-added "Run sample data" shortcut (fetches allowlisted sample files, submits through the same path as a manual upload). Payment Aging's as-of-date field now live/required/editable. `/dashboard` and `/reports` deliberately stayed static (`/reports` reframed as "Sample Report Overview" with workflow links). `UploadPanel` gained `onFileChange`/`sampleFileName` props; "Sample Template" renamed "Sample File" everywhere including Python exception text in `src/excel_io.py`/`src/inventory_allocation.py`.
- **Tests:** `tests/test_backend_{orders,inventory,payments,templates,errors}.py`, 22 new tests using FastAPI's `TestClient` against real `sample_data/*.xlsx`.
- **Bug-fix round (`/project-review` → `/tdd` → `/project-review`):** independent review agent found 1 Critical + 4 Important + 3 Minor issues. Fixed via TDD (RED/GREEN regression test first for the Critical bug): `backend/routers/inventory.py`'s `_run_allocation` now catches `MissingColumnsError`/`InvalidOrderDataError`/`InvalidInventoryDataError` from `allocate_inventory()` (previously leaked as a `500` on e.g. zero-valid-orders input) → `400`. Frontend: `sampleDataLoading` added to all 6 Run/Download-Report button disable conditions across the 3 pages (race-condition fix); `UploadPanel` gained a `selectedFileName` prop so "Run sample data" visibly updates the panel; report-download errors now render via `BusinessErrorMessage` (`role="alert"`) instead of a bare `<p>`; `Button` defaults `type="button"`; `backend/routers/orders.py` factored to match `inventory.py`'s helper pattern. Second independent review confirmed all 6 fixes landed correctly, no architecture drift, 3 Minor housekeeping items left open (see Open Questions). Documented to `docs/project-review/phase-10-bug-fixes/`.
- **`/recover` session:** live bug after the fix round — "Could not reach the API server" on `/order-validation`. Three hypotheses tried and ruled out with direct evidence (backend down — no, it was up; wrong browser port — no, user confirmed `:3000`; stale client cache — no, hard refresh didn't help) before finding the real cause: `lib/api-client.ts` hardcoded `http://localhost:8000`, but `/etc/hosts` maps `localhost` to both `127.0.0.1` and `::1`, and the FastAPI dev server binds IPv4-only — a browser trying the IPv6 loopback first gets a silent connection failure. Fixed by changing the fallback to `http://127.0.0.1:8000` (one line). User confirmed fixed live. Documented to `docs/recover/phase-10-ipv6-localhost-mismatch/`.
- **Docs housekeeping:** `context/architecture.md`, `context/build-plan.md`, `context/library-docs.md`, `context/ui-contract-plan.md`, `context/ui-rules.md`, `context/progress-tracker.md`, `context/ui-registry.md` all updated for Phase 10 (endpoint lists corrected, Phase 10 marked complete, new component/page-composition notes added). `docs/plan/phase-10-fastapi-integration/{plan,explanation,ai-discussion-topics}.md` written via `/feature-docs` for the original implementation (not yet updated for the bug-fix round — see Open Questions).

## Decisions made

- **Stateless architecture is the load-bearing Phase 10 decision** (the one thing that became an ADR out of ~13 total decisions): no persisted Workflow Run, no `run_id`, no stored report artifacts. Report endpoints always re-accept raw files and recompute — never trust a client-supplied result. This is deliberately hard to reverse without a new ADR.
- **snake_case end-to-end, no camelCase adapter** — resolved this session (was open since Phase 7/8). If ever needed, an adapter lives only at the API-client boundary, never in components or Python.
- **No derived Payment Aging shorthand badges (Paid/Overdue) in Phase 10** — resolved as "deferred until derivation rules are explicitly documented," not a flat no forever. Contract-direct display only (`aging_bucket`, `follow_up_priority`).
- **Two independent dev servers + CORS, not a Next.js proxy** — FastAPI `:8000`, Next.js `:3000`, explicit `allow_origins`/`allow_methods`/`allow_headers`/`expose_headers` (the last one caught in plan review — cross-origin JS can't read a header the server doesn't explicitly expose).
- **Route handlers return real `src/`-module TypedDicts directly**, no parallel Pydantic models — verified empirically (Pydantic v2 validates TypedDicts natively) before committing to the pattern, not just assumed.
- **Frontend state is page-local**, no global store/context — `lib/api-client.ts` holds only stateless helpers. Confirmed to still hold after the bug-fix round (`selectedFileName`/`sampleDataLoading` are plain per-page `useState`).
- **`ReportLifecycleState`/`ReportCard`** (4-state, static `/dashboard`+`/reports` only) and **`ReportRequestState`** (3-state, live per-page download buttons) are deliberately two separate, unrelated types — do not merge them.
- **PR strategy confirmed and followed:** built on top of the existing Phase 9 branch (`phase/10-fastapi-integration` branched from `phase/9-reusable-ui-components-static-pages`), new PR #9 (base = PR #8's branch), continuing the stack. Did not merge PR #2–#8 first. Bug-fix-round commits pushed to the *same* branch, updating PR #9 in place (not a new PR) — matches the Phase 9.1 precedent.
- **Verification tooling:** no project run-skill existed for this app; used `npm install --no-save playwright` + a throwaway driver script each time live-browser verification was needed, cleaning up (`npm uninstall playwright`, delete script) afterward every time — confirmed via `git diff package.json` showing no trace. Did this 3 times across the session (initial verification, post-fix verification, `/recover` repro).

## Problems solved

- **Critical backend bug**: zero-valid-orders input to `/api/inventory/allocate` produced a `500` instead of `400` — `allocate_inventory()`'s internal exceptions were never caught (only the file-*loading* step was, in `backend/uploads.py`). Fixed with a scoped `try`/`except` around just the `allocate_inventory()` call in `_run_allocation`.
- **Frontend race condition**: primary "Run"/"Download Report" buttons weren't disabled during "Run sample data"'s fetch phase (separate `sampleDataLoading` flag the buttons didn't know about) — could fire overlapping requests. Fixed by adding `sampleDataLoading` to all 6 button disable expressions.
- **`UploadPanel` display bug**: component tracked filename in its own uncontrolled `useState`, so "Run sample data" (which bypasses the native file input) never updated the visible panel — fixed with a `selectedFileName` prop derived from the same state that's actually submitted.
- **`TestClient` gotcha (rediscovered, same as an earlier session)**: default `raise_server_exceptions=True` re-raises unhandled exceptions instead of exercising a registered handler — needed `TestClient(app, raise_server_exceptions=False)` to actually test the generic-500 handler.
- **IPv4/IPv6 `localhost` mismatch** (see `/recover` session above) — the actual root cause of a recurrence of "Could not reach the API server" that looked identical to an earlier, different bug (backend simply not running) from earlier in the session. Two other hypotheses (wrong port, stale cache) were tried and correctly ruled out with direct evidence first — worth remembering that this project has accumulated many stray dev-server ports (3010–3051) across the session from repeated verification passes, which was a real, if ultimately not-the-answer, red herring.
- **Playwright test-script flakiness**: `getByRole("alert").innerText()` intermittently returned empty despite the correct content being visibly rendered (a timing race against React's commit, not a product bug) — resolved by trusting screenshot evidence / waiting for a settled state rather than chasing the flaky assertion.

## Current state

- **PR #9** (`phase/10-fastapi-integration` → `phase/9-reusable-ui-components-static-pages`, https://github.com/gwho/sales-ops/pull/9): open, now 2 commits — original Phase 10 implementation (`8faf0ca`) + bug-fix/recover round (`5301e13`). Pushed.
- PR #1 merged; PR #2 through #8 unchanged, still open, stacked (not re-verified this session — see Open Questions, standing rule).
- `uv run pytest`: **196 passing** (up from 172). `npm run typecheck`/`lint`/`build`: all clean. Live-browser-verified multiple times, including the final IPv6 fix confirmed working in the user's actual browser (not just headless Chromium, which never reproduced that bug).
- Local checkout on `phase/10-fastapi-integration`.
- Both dev servers (FastAPI `:8000`, Next.js `:3000`) were running at end of session — plus **6 stray leftover Next.js instances** on ports 3010/3020/3030/3040/3050/3051 from earlier verification passes, never cleaned up (harmless — CORS blocks them from mattering — but real clutter).
- Working tree has one stray untracked file, never cleaned up: `sample_data/~$sample_invoices.xlsx` (an Excel lock file, unrelated to any work this session, flagged twice by review agents).
- `memory.md` itself deliberately excluded from every commit this session, per established practice.

## Next session starts with

1. **Re-check live PR merge status before assuming anything** — standing rule, now confirmed across Phases 4 through 10. Don't trust this memory's snapshot.
2. Optional cleanup, low priority: kill the 6 stray dev-server processes on ports 3010–3051; delete `sample_data/~$sample_invoices.xlsx` (do not commit it).
3. Minor doc-accuracy fix, not yet done: `docs/architect/phase-10-fastapi-integration/approved-plan.md`'s Decision 12 says `backend/uploads.py` is "the only place" certain exceptions are caught — no longer true since the Critical-bug fix added a second, necessary catch site in `backend/routers/inventory.py`. Either update that doc or add an explicit note.
4. Minor, not yet done: `context/progress-tracker.md` and `docs/plan/phase-10-fastapi-integration/{plan,explanation}.md` reflect the *original* Phase 10 implementation but not the subsequent bug-fix round (that round is documented separately in `docs/project-review/phase-10-bug-fixes/` and `docs/recover/phase-10-ipv6-localhost-mismatch/`, but the canonical progress/plan docs weren't cross-updated).
5. Phase 10 was the last phase explicitly defined in `context/build-plan.md` — next scope (if any) needs its own planning pass, not an assumed "Phase 11."

## Open questions

Carried forward, still genuinely unresolved:

- Whether/when to merge PR #2 through #9 — still the user's call, not decided by any session so far.
- Whether to eventually retrofit the pre-Phase-6 `docs/plan/*` folders to match `/feature-docs`'s real template — deferred since the Phase 9/9.1 session, still not scheduled, not raised again this session.
- Whether/how to address `/model sonnet` being unavailable in this environment — unresolved since Phase 9/9.1, likely stale/environment-specific rather than project-relevant, but never explicitly dropped or resolved, so kept here rather than silently discarded.

New this session, not yet resolved:

- Stale wording in `docs/architect/phase-10-fastapi-integration/approved-plan.md`'s Decision 12 (see Next Session item 3).
- `context/progress-tracker.md`/`docs/plan/phase-10-fastapi-integration/` not updated for the bug-fix round (see Next Session item 4).
- Stray untracked file and 6 leftover dev-server processes (see Next Session item 2) — low priority, not blocking.
- Whether the FastAPI backend should eventually bind to both IPv4 and IPv6 (`::` or `0.0.0.0`) as a more symmetric fix than the frontend-side `127.0.0.1` pin — noted as a valid alternative during the `/recover` session but not decided either way; the frontend fix was chosen as minimal and sufficient, not as a final word on the underlying asymmetry.
- Whether to reintroduce derived shorthand Payment Aging badges (Paid/Overdue) — still open in principle (carried since Phase 9), but now has an explicit unblock condition from this session's grilling decision: only if/when exact derivation rules are documented first.

---

# Memory — Phase 11 Planning: SQL Reporting and Active Sample Dashboard (Grilling + Architect)

Last updated: 2026-07-12 (appended; all prior session content above is unchanged)

## What was built

This was a **planning-only session** — no `src/`, `backend/`, `app/`, or `types/` code was touched. Output is docs plus an approved, decision-complete implementation plan file, not yet implemented.

- **`/grill-with-docs` session** (`/grilling` + `/domain-modeling`) resolved Phase 11's durable architecture ahead of `/architect`: `CONTEXT.md` gained a new term, **`Demo Reporting Database`**; `docs/adr/0007-sql-reporting-seeds-from-tested-workflow-outputs.md` created (SQL reports over tested-pipeline facts, never re-derives a business classification). Session documented via `/session-docs` to `docs/grilling/phase-11-sql-reporting-and-active-dashboard/{session.md, explanation.md, ai-discussion-topics.md}`.
- **`/architect` session** (run in Plan Mode) produced a fully negotiated, decision-complete implementation plan, written to `/Users/jessejames/.claude/plans/yes-the-plan-aligns-smooth-barto.md`. The user reviewed and refined it across three rounds of feedback before approving it as "decision-complete" — **the plan file itself is the authoritative spec for Phase 11 implementation**; this memory entry is a pointer/summary, not a duplicate of it.

## Decisions made

Full detail lives in the ADR, the grilling docs, and the plan file — summarized here only enough to orient a fresh session:

- **Sequencing locked**: a new **Phase 10.2 (Portfolio UI Polish)** was inserted ahead of Phase 11 — token-only visual/hierarchy fixes on the stable Phase 10 app (semantic color balance, button hierarchy, KPI grid arrangement/scanability), explicitly no backend/API/DB work. Full sequence is now **Phase 10.2 → Phase 11 → Phase 11.1 (deployment, deferred)**.
- **Phase 11 architecture** (all in the plan file): SQLite `Demo Reporting Database`, disposable/regenerated/gitignored (`backend/data/*.sqlite`), rebuilt atomically on every FastAPI startup via a lifespan hook (`rebuild_demo_reporting_database(db_path)`, temp-file-then-`os.replace`). Exactly 6 row-level tables (`valid_order_lines`, `validation_errors`, `allocation_results`, `remaining_inventory`, `supplier_follow_ups`, `aging_rows`) — deliberately no `products`/`customers`/`warehouses`/`backorders`/`payment_data_issues`/`draft_messages`/`report_manifests` tables and no forced `JOIN`, since none of the 7 SQL-backed dashboard sections need them (Field Scope Boundary discipline applied to schema design, not just Python contracts). Hand-written parameterized SQL only, no ORM. Seed reads exclusively from the tested pipeline's Output Contract results (ADR 0007), using a new pinned-date module `src/demo_constants.py` (`DEMO_AS_OF_DATE`/`DEMO_GENERATED_AT`, imported by both the seed and the existing `scripts/generate_mock_data.py`, replacing that script's local `MOCK_AS_OF_DATE`/`MOCK_GENERATED_AT`).
- **New endpoint**: single `GET /api/dashboard` (no query params) returns a `DashboardResponse` TypedDict defined in `backend/reporting_db/queries.py` (not `src/contracts.py` — it's a dashboard aggregate, not a spec-derived Output Contract). Plus a minimal `GET /health` (`{"status": "ok"}`, no DB check).
- **Frontend**: `/dashboard` becomes this project's first **async Server Component with a live fetch** (`fetch(..., { cache: "no-store" })` + explicit `export const dynamic = "force-dynamic"` — verified against the installed Next.js 16.2.10 docs under `node_modules/next/dist/docs/` that this export is still valid since `next.config.ts` doesn't enable Cache Components mode). New `types/dashboard.ts` (not `types/index.ts`) and `lib/dashboard-server.ts` (server-side fetch helper, distinct from the browser-oriented `lib/api-client.ts`). `CORS_ALLOWED_ORIGINS` env var replaces `backend/main.py`'s hardcoded origin list.
- **7 dashboard sections go SQL-backed**: Order Validation KPIs, Inventory Allocation KPIs + Allocation Status donut, Payment Aging KPIs, Outstanding-by-Aging-Bucket chart, Inventory Shortage Alerts table, Payment Follow-up Items table. Reports section, Workflow nav cards, infographic, and guide text stay static (unchanged) — explicitly not moved into SQL "to say everything is database-backed."

## Problems solved

None — no implementation happened this session. One useful verification finding worth keeping: confirmed via the installed Next.js docs (not assumed) that `export const dynamic = "force-dynamic"` is still valid syntax in this project's Next 16.2.10 setup, because Cache Components mode (which would remove that route-segment-config option entirely) is not enabled in `next.config.ts`.

## Current state

- **Phase 10 unchanged** — still the last *implemented* phase (PR #9, per prior session entry above, not re-verified this session since no code changed).
- **Phase 11 is fully planned and approved, but explicitly not started.** The user's instruction for this session: "Treat Phase 11 as approved but queued." The plan file at `/Users/jessejames/.claude/plans/yes-the-plan-aligns-smooth-barto.md` is decision-complete and ready to implement whenever picked up.
- **Phase 10.2 has no plan yet** — only the one-paragraph scope description from the grilling session (token-only visual/hierarchy fixes, no backend/DB work, update `context/ui-registry.md` after). No `/architect` session has run for it.
- Working tree: no code changes this session. `memory.md` itself excluded from any future commit, per established practice.

## Next session starts with

1. **User will plan and implement Phase 10.2 (Portfolio UI Polish) first** — this is the explicit next step, before touching Phase 11. Likely needs its own `/architect` pass since only a scope paragraph exists so far, no concrete decisions.
2. **After Phase 10.2 ships**, return to the approved Phase 11 plan at `/Users/jessejames/.claude/plans/yes-the-plan-aligns-smooth-barto.md` and implement it as written — it does not need to be re-planned or re-approved, only re-read for context at the start of that session.
3. Standing rule (confirmed across every phase since Phase 4): re-check live PR merge status before assuming anything — not re-verified this session.

## Open questions

Carried forward, still genuinely unresolved (unchanged from prior session, not revisited this session):

- Whether/when to merge PR #2 through #9 — still the user's call.
- Whether to eventually retrofit the pre-Phase-6 `docs/plan/*` folders to match `/feature-docs`'s real template — still deferred, still not scheduled.
- Whether/how to address `/model sonnet` being unavailable in this environment — still unresolved, likely stale/environment-specific.
- Whether to reintroduce derived shorthand Payment Aging badges — still open, still gated on documenting exact derivation rules first (unchanged from Phase 10 session).

New this session, not yet resolved:

- Phase 10.2's exact scope/design decisions — nothing beyond the one-paragraph description has been decided; needs its own planning pass.
- Phase 11.1 (deployment architecture, hosting choice, secrets, hiring-manager walkthrough) remains fully deferred — untouched by this session beyond the interface constraints already locked in the Phase 11 plan (`GET /health`, env-driven CORS, `NEXT_PUBLIC_API_BASE_URL`).

---

# Memory — Phase 11 Pivot: SQLite Reporting Paused, Deployment Baseline Started

Last updated: 2026-07-12 (appended; all prior session content above is unchanged)

## What was built

- **Phase 11 (SQL Reporting) was actually started this session**, then explicitly paused mid-implementation on user direction ("deploy first, Postgres-backed dashboard later instead of SQLite"). Working code was produced and smoke-tested against real `sample_data/*.xlsx` before the pause: `backend/reporting_db/schema.py` (5-table DDL — `valid_order_lines`, `validation_errors`, `allocation_results`, `supplier_follow_ups`, `aging_rows`; atomic `rebuild_demo_reporting_database()`), `backend/reporting_db/queries.py` (hand-written SQL + `DashboardResponse` TypedDicts, verified against known dataset values — 36 total orders/8 invalid, 26 fully/1 partially/1 backordered, 3 supplier follow-ups), `backend/routers/dashboard.py`, `src/demo_constants.py`. Also discovered and corrected mid-build: Phase 10.2 had already consolidated the dashboard (one 5-card Overview row + 2 charts + 2 tables, several old KPIs dropped) — the schema/response were revised down from 6 tables/many fields to 5 tables/trimmed fields to match the *actual* current UI, not the pre-10.2 assumption the original plan was written against.
- **All of the above is now in a named git stash**, not deleted: `git stash list` shows `"Phase 11 SQLite reporting WIP (paused): schema, queries, dashboard endpoint, lifespan seed hook, demo_constants"` (`stash@{0}`). Stashed: `backend/reporting_db/` (whole dir), `backend/routers/dashboard.py`, `backend/data/` (the generated `.sqlite` file, now removed from the working tree), `src/demo_constants.py`, `scripts/generate_mock_data.py`'s diff (cleanly reverted to its original `MOCK_AS_OF_DATE` form), `CONTEXT.md`'s diff (the `Demo Reporting Database` glossary term, reverted), `docs/adr/0007-sql-reporting-seeds-from-tested-workflow-outputs.md`, `docs/grilling/phase-11-sql-reporting-and-active-dashboard/`, and `backend/main.py`'s original full diff (lifespan hook + dashboard router registration).
- **`backend/main.py` and `backend/routers/health.py` were deliberately kept out of the stash** and rewritten cleanly with zero dependency on the stashed `reporting_db` module: env-driven `CORS_ALLOWED_ORIGINS` (comma-separated, trimmed, empty-entries dropped, default `http://localhost:3000`) and `GET /health` → `{"status": "ok"}`. Verified via `TestClient`: `/health` returns 200, `/api/dashboard` correctly 404s (not registered), and `uv run pytest` still passes all 196 tests.
- **A new `/architect` session for "Phase 11: Deployment Baseline" was started** (replacing the paused SQL-reporting Phase 11 in the phase sequence). Homework done (package.json, pyproject.toml, next.config.ts, git remote confirmed as `github.com/gwho/sales-ops`, confirmed no existing CI/deployment config). Language-alignment questions were posed to the user (stable permanent URL vs ephemeral, sample-data-just-needs-full-repo-checkout, single-container vs two-separate-services as the first real decision, resume/demo-readiness definition) — **not yet answered** when this session ended.

## Decisions made

- **Phase renumbering**: the SQL-reporting "Phase 11: SQL Reporting and Active Sample Dashboard" is retired as the active Phase 11. A new **"Phase 11: Deployment Baseline"** takes that slot instead — deploy the current post-Phase-10.2 app to a public URL, no Postgres/DuckDB/SQLite/auth/persisted-uploads/run-history in this phase.
- **The old plan file** (`/Users/jessejames/.claude/plans/yes-the-plan-aligns-smooth-barto.md`) **and its supporting docs** (`docs/adr/0007-...md`, `docs/grilling/phase-11-sql-reporting-and-active-dashboard/`) **are not deleted** — they remain accurate historical records of a real planning session and partially-working implementation, just no longer the active Phase 11. The stashed code is explicitly kept (not discarded) because "some structure may be useful for the future Postgres latest-session dashboard."
- **New intended phase sequence**: Phase 10.2 (UI polish, uncommitted) → **Phase 11: Deployment Baseline** (in progress) → **Phase 12: Postgres-backed latest-session dashboard** (future, replaces the SQLite sample-dashboard idea — store computed workflow outputs in Postgres after each run, anonymous session identity if needed, dashboard shows latest saved results with fallback to sample data, DuckDB explicitly out of scope unless separately approved).
- **Kept from the paused work regardless of the pivot**: env-driven CORS and `GET /health` — both are needed by the new Deployment Baseline phase anyway, so they were preserved fresh (not stashed) rather than thrown away and rebuilt later.

## Problems solved

- None new this session beyond the stash mechanics themselves. Worth remembering for a future session: `git stash push -u -m "<message>" -- <pathspec...>` with explicit pathspecs cleanly splits a working tree when some changes in the *same file* (`backend/main.py`) need to be kept and others discarded — stash the whole file's diff first (reverting it to HEAD), then hand-reapply only the wanted portion fresh. This avoided any risk of a manual partial-diff edit going wrong.

## Current state

- Working tree: Phase 10.2's uncommitted work (`app/`, `components/`, `context/*.md` except `build-plan.md`/`progress-tracker.md`/`ui-tokens.md`/`ui-registry.md` which *are* Phase 10.2, `tailwind.config.ts`, `CLAUDE.md`) is untouched and still uncommitted, exactly as it was when this session started. `backend/main.py` has only the CORS+health changes. `backend/routers/health.py` is new and untracked. Everything SQLite-related is in `stash@{0}`, out of the working tree.
- `uv run pytest`: 196 passing (unchanged). `backend/data/` no longer exists (the stray generated `.sqlite` file was stashed away).
- The `/architect` session for Phase 11: Deployment Baseline is **mid-flight** — language alignment was proposed, not yet confirmed by the user.
- `memory.md` itself intentionally excluded from any commit, per established practice.

## Next session starts with

1. **Resume the in-flight `/architect` session for Phase 11: Deployment Baseline** — the four language-alignment terms are awaiting confirmation, then the real decisions: (a) single containerized deployment vs. two separate hosted services matching the current local dev shape (architect's recommendation going in: two separate services, e.g. Vercel for Next.js + a Python-capable host for FastAPI), (b) specific backend host choice, trading off free-tier cold-start/sleep behavior vs. cost vs. setup complexity (Render/Railway/Fly.io were the candidates under consideration, not yet decided), (c) env var sequencing (`NEXT_PUBLIC_API_BASE_URL` on the frontend, `CORS_ALLOWED_ORIGINS` on the backend — chicken-and-egg: backend must deploy first to get its URL before the frontend can be configured with it, then CORS updated with the frontend's real URL).
2. If/when the user wants to resume the paused SQLite work instead (or reference it for Phase 12), it's fully intact in `git stash list` under the message `"Phase 11 SQLite reporting WIP (paused)..."` — `git stash show -p stash@{0}` to inspect, `git stash pop`/`git stash apply` to restore (note: `backend/main.py` in the stash is the *pre-CORS/health-rewrite* version, so popping it now would conflict with or overwrite the current clean CORS/health-only `backend/main.py` — reconcile by hand rather than blindly popping).

## Open questions

Carried forward from the Phase 10/Phase-11-planning sessions, still genuinely unresolved:

- Whether/when to merge the stacked PR chain — still the user's call.
- Whether to retrofit pre-Phase-6 `docs/plan/*` to the `/feature-docs` template — still deferred.
- `/model sonnet` availability — still unresolved, likely environment-specific.
- Derived shorthand Payment Aging badges — still gated on documenting derivation rules first.

New this session:

- The four `/architect` language-alignment terms for Phase 11: Deployment Baseline (stable URL definition, sample-data-availability scope, single-container-vs-two-services, resume/demo-readiness definition) — posed, not yet confirmed.
- Hosting architecture and specific backend host choice — not yet decided.
- Whether Phase 10.2's uncommitted work should be committed/PR'd before or alongside the deployment work — not discussed this session, worth raising early next session since deploying typically wants a clean/pushed branch state.

---

# Memory — Phase 10.2: Portfolio UI Polish

Last updated: 2026-07-12 (appended; all prior session content above is unchanged)

## What was built

- **Planning:** `/architect` session (approved plan at `/Users/jessejames/.claude/plans/plan-phase-10-2-portfolio-abstract-stream.md`, one review/correction round), documented via `/session-docs` to `docs/architect/phase-10.2-portfolio-ui-polish/{decisions,discussion,ai-discussion-topics}.md`.
- New **Inverse Surface** token family (`--surface-inverse`, `--surface-inverse-hover`, `--text-on-inverse`, `--text-on-inverse-muted`) in `app/globals.css`/`tailwind.config.ts`/`context/ui-tokens.md`.
- `components/ui/Button.tsx`: new `dark` variant, scoped to Download Report + Sample file only.
- `components/layout/SidebarNav.tsx`: dark navy bg, solid-accent active state, `lucide-react` icon per nav item.
- `components/workflow/MetricCard.tsx`: restructured into a compact centered tile (icon → value → label, `min-h-[104px]`) + hover/shadow, same prop contract, ~15 call sites unaffected.
- `components/workflow/UploadPanel.tsx`: `h-full` + `mt-auto` bottom-anchoring fix for multi-panel drop-zone misalignment; Sample file button switched to `dark` variant + `min-w-0`/`shrink-0`/`whitespace-nowrap` sizing fix.
- `components/tables/TableSectionHeading.tsx`: new optional `action` prop (top-right compact link).
- `components/charts/DonutBreakdownChart.tsx`: promoted to Client Component, hover/focus tooltip (floating card + legend right-aligned counts + `%`), fixed a hydration bug (multi-line JSX in `<title>`) and a pointer-events bug (center overlay blocking ring hover).
- `components/charts/VerticalBucketBarChart.tsx`: per-bar `group-hover`/`group-focus` tooltip (label/amount/% of total), stayed a Server Component.
- `app/dashboard/page.tsx`: consolidated 3 per-workflow KPI groups (~15 tiles + `SegmentedBar`) into one 5-card "Overview" row (Total Orders, Invalid Orders, Fully Allocated, Backordered, Overdue Amount) — a deliberate content reduction, not just a restyle; paired Inventory Shortage Alerts/Payment Follow-up Items side by side; fixed chart-card sizing (`min-h-48 flex-col justify-center`); added chart-card hover + action links ("View all" → `/inventory-allocation`, "AR report" → `/payment-aging`).
- `app/{order-validation,inventory-allocation,payment-aging}/page.tsx`: Download Report button → `dark` variant; each page's KPI summary grid reverted to fit its own card count in one row (`lg:grid-cols-6/5/4`) — distinct from dashboard's capped 5-column row.
- Docs: `context/ui-registry.md` (all touched components + new "Page composition notes (Phase 10.2)"), `context/build-plan.md` (new Phase 10.2 section), `context/progress-tracker.md` (Current Status + checklist + Decisions Made entries), `CLAUDE.md` (Project State + Build Sequence updated to Phase 10.2), `docs/plan/phase-10.2-portfolio-ui-polish/{plan,explanation,ai-discussion-topics}.md` via `/feature-docs`.

## Decisions made

- Shared "Inverse Surface" token family (not two separate families) — sidebar and dark button must look like the same visual system by construction, not by manually matching two token sets.
- Exact Tailwind config key shapes matter and were user-corrected: `surface-inverse` nested (`{DEFAULT,hover}`), `text-on-inverse`/`text-on-inverse-muted` flat — matching existing codebase conventions for surface vs. text color families respectively.
- `dark` Button variant scoped to exactly two usages (Download Report, Sample file) — never Run actions, never `ReportCard`'s "Go to workflow" link.
- `MetricCard`'s prop contract unchanged (`label`/`value`/`icon`/`tone`) — only internal layout changed, so all ~15 call sites needed zero edits.
- Dashboard KPI consolidation (5-card Overview row replacing ~15 tiles across 3 groups) is a deliberate, user-directed content reduction — dropped KPIs remain on each workflow page's own post-run summary, not silently lost. This overrode the original plan's assumption that dashboard groups would stay separate.
- Workflow-page KPI grids intentionally do NOT share dashboard's 4-column cap — each fits its own count (6/5/4) in one row; only dashboard's Overview row is capped/single-row by design.
- Donut chart needed client-side state (shared hover between ring segments and legend, both need to reflect the same hovered item); bar chart didn't (each bar's tooltip is fully self-contained, pure CSS `group-hover`/`group-focus`) — no new charting library used for either.
- Sidebar's lack of mobile responsive collapse was surfaced but explicitly NOT fixed — pre-existing, unrelated to this phase (only color/icons changed, not width/breakpoints), needs its own planning pass.

## Problems solved

- React hydration mismatch: multi-line JSX children inside an SVG `<title>` (`<title>{a}: {b} ({c}%)</title>` split across lines) produced server/client whitespace differences — fixed by building the string as one expression before the JSX.
- Pointer-events bug: donut's `absolute inset-0` center-total overlay had no `pointer-events-none`, so it silently blocked hover/focus on the ring segments beneath it across the whole donut area, not just the hole — found via a failing Playwright hover test, not visual inspection.
- `UploadPanel`'s reported "row alignment" bug was actually a bottom-anchoring bug across a multi-panel grid row (drop-zone position shifted per card based on how many lines "Required columns" text wrapped to) — diagnosed by reading the component source (row was already correct) plus a real screenshot of the live page.
- Chart-card oversized blank space: CSS Grid's default row-stretch pulled the shorter donut card to match its taller sibling's incidental content height — fixed with an explicit shared `min-h-48 flex-col justify-center` on both chart bodies instead of relying on accidental stretch.
- `UploadPanel` Sample-file button wrapping to two lines in the 3-column Inventory Allocation layout — fixed with `min-w-0` on the caption (lets it shrink/wrap) and `shrink-0 whitespace-nowrap` on the button (never wraps).
- Stray `.next/types` Finder-duplicate files caused a spurious `tsc` error (same class of bug as a Phase 9.1 session) — fixed with `rm -rf .next`; a stale `next-server` process serving from the deleted build then needed a restart (`npm run dev`) to stop 500-ing.

## Current state

- `uv run pytest`: 196 passing, unchanged (no Python touched this session).
- `npm run typecheck`/`lint`/`build`: all clean. Raw-color/hex grep across every touched file: clean.
- Live-browser verification (Playwright, desktop + mobile, hover/focus states) confirmed all fixes; test script and playwright package both cleaned up afterward (no trace in `package.json`).
- Working tree: **nothing committed this session** — all Phase 10.2 changes (component/page edits + all doc updates) sit uncommitted alongside the already-uncommitted Phase 11 planning artifacts from the prior session (`CLAUDE.md`, `CONTEXT.md`, `docs/adr/0007-*`, `docs/grilling/phase-11-*`) and the untracked `sample_data/~$sample_invoices.xlsx` lock file.
- `context/progress-tracker.md`: Current Status = "Phase 10.2 - Portfolio UI Polish (complete)".
- Dev servers: FastAPI on `:8000` and Next.js on `:3000` were both running and healthy at end of session (Next.js was restarted once mid-session after `.next` cleanup).

## Next session starts with

1. User's call: commit this session's Phase 10.2 changes — nothing has been committed yet; explicitly confirm scope/message with the user first, per standing git-safety practice.
2. After Phase 10.2 is committed/settled, return to the already-approved, still-queued Phase 11 plan at `/Users/jessejames/.claude/plans/yes-the-plan-aligns-smooth-barto.md` — no re-planning needed, just re-read for context.
3. Known open item, not scheduled: sidebar's lack of mobile responsive collapse — surfaced this session, needs its own planning pass if picked up.
4. Standing rule (confirmed across every phase since Phase 4): re-check live PR merge status before assuming anything — not touched or re-verified this session.

## Open questions

Carried forward, still genuinely unresolved:

- Whether/when to merge PR #2 through #9 — still the user's call.
- Whether to eventually retrofit the pre-Phase-6 `docs/plan/*` folders to match `/feature-docs`'s real template — still deferred.
- Whether/how to address `/model sonnet` being unavailable in this environment — still unresolved, likely stale/environment-specific.
- Whether to reintroduce derived shorthand Payment Aging badges — still open, still gated on documenting exact derivation rules first.

New this session, not yet resolved:

- Whether/how to eventually give `SidebarNav` responsive mobile behavior (collapse, drawer, icon-rail, etc.) — flagged, not decided, not scheduled.
- Whether the current 5-card dashboard Overview KPI selection (Total Orders, Invalid Orders, Fully Allocated, Backordered, Overdue Amount) is final, or might be revisited once Phase 11's SQL-backed dashboard work begins.

---

# Memory — Phase 11 Deployment Baseline: Shipped and Verified Live

Last updated: 2026-07-13 (appended; all prior session content above is unchanged)

## What was built

- **The app is live in production.** Backend on Render (Free Web Service, Python runtime): <https://sales-ops-6e84.onrender.com>. Frontend on Vercel (Hobby tier): <https://sales-ops-gamma.vercel.app/>. Both deployed from a dedicated `deploy/portfolio-demo` branch, currently at commit `974b348`, kept fast-forwarded in sync with `phase/10-fastapi-integration`.
- **Repo changes**, in two commits on `phase/10-fastapi-integration` (pushed, updating the existing **PR #9**, no new PR needed): (1) `a2615cc` — Phase 10.2's previously-uncommitted UI polish work (see prior session block above). (2) `6b6a716` — Phase 11 deployment-baseline prep: env-driven `CORS_ALLOWED_ORIGINS` (comma-separated, trimmed, empty-filtered) and a minimal `GET /health` on `backend/main.py`, new `.env.example` (had to add `!.env.example` to `.gitignore` — the blanket `.env*` rule was silently excluding it), `README.md`'s "Live Demo" section with the accepted Render cold-start note, `context/build-plan.md`/`context/architecture.md` updated with the two-service deployment shape, and `CLAUDE.md`'s stale "Candidate next scope" pointer (previously pointing at the paused SQLite plan file) corrected. A third small commit `974b348` filled the real live URLs into `README.md` once both were verified working.
- **`deploy/portfolio-demo`** branch created, pushed, and force-updated (fast-forward only) twice as new verified commits landed — matches the "explicit promotion, not continuous auto-deploy of WIP" model from the plan.
- Stray `sample_data/~$sample_invoices.xlsx` lock file deleted (not committed), per instruction.

## Decisions made

- **Vercel Hobby + Render Free Web Service**, two independent services, deployed from `deploy/portfolio-demo` — all as planned in the `/architect` session (see prior memory block's Phase 11 pivot entry for the full decision trail: two-service architecture, host choice reasoning, branch strategy, no-secrets, deploy sequencing).
- **Render build/start commands, as actually configured**: build `uv sync --frozen --no-dev && uv cache prune --ci` (Render's dashboard auto-suggested a `uv`-based build command, confirming `uv` is natively available on Render's Python runtime — the plan's `pip install uv` fallback step turned out to be unnecessary in practice); start `uv run fastapi run backend/main.py --host 0.0.0.0 --port $PORT`; Health Check Path `/health`.
- **Render's Pre-Deploy Command field is gated behind a payment method on free instance types** (confirmed via web search, not assumed) — left blank/untouched rather than adding a card to unlock it, since this app has no migration/asset-upload step that would need it anyway.
- **Render prompted for card verification on "Deploy Web Service" itself** (a $1 refundable auth-only hold, not a charge) — confirmed via web search as a known, real anti-abuse practice on Render's free tier, not caused by a wrong form selection. User proceeded with it.
- **`.env.example` stays a template with empty values in git** — the user locally filled in real URLs for their own convenience/reference while configuring the dashboards, but was advised not to commit that version; the real URLs' canonical homes are the Vercel/Render dashboard configs (already set) and `README.md`'s Live Demo section (filled in). `.env.example` remains modified-but-uncommitted locally as of this session's end — deliberately not staged in either deployment-prep commit.

## Problems solved

- **`.env.example` was being silently gitignored** by the pre-existing blanket `.env*` rule in `.gitignore` — caught via `git status`/`git check-ignore` before it went unnoticed; fixed with a `!.env.example` negation line added directly after the blanket rule.
- **CORS trailing-slash bug caught before it caused a live failure**: the user pasted the Vercel URL with a trailing slash (`https://sales-ops-gamma.vercel.app/`) into local scratch notes; flagged that browsers never send a trailing slash in the `Origin` header and `_cors_origins()` only trims whitespace/commas, not slashes — so a trailing-slash value would have silently broken CORS. User set the Render env var without the trailing slash; verified correct afterward via a live `OPTIONS` preflight curl showing `access-control-allow-origin: https://sales-ops-gamma.vercel.app` exactly matching.
- **Live deployment verified end-to-end via direct `curl`, not assumed**: backend `/health` → `200 {"status":"ok"}`; frontend `/` → `307` redirect to `/dashboard` (expected, matches the app's existing root-redirect behavior) → `200` with real rendered content (`<title>Sales Admin Automation Toolkit</title>` plus live dashboard chart titles matching the known dataset: 26 fully/1 partially/1 backordered); CORS preflight from the Vercel origin against the Render backend returns the correct `Access-Control-Allow-Origin`.

## Current state

- **Phase 11 (Deployment Baseline) is functionally complete and live-verified**, but **not yet marked complete in the docs** — `context/progress-tracker.md` and `docs/plan/phase-11-deployment-baseline/` (via `/feature-docs`) were deliberately deferred to "after verification, per this project's established sequencing," and verification just happened this session. This is the one remaining plan step.
- PR #9 and `deploy/portfolio-demo` are both at commit `974b348`, in sync.
- The paused SQLite reporting work remains untouched in `git stash` (`stash@{0}`), unrelated to and unaffected by this session's deployment work.
- `uv run pytest`: 196 passing (unchanged, no Python business logic touched this session beyond the two lines in `backend/main.py` already covered above).

## Next session starts with

1. **Update `context/progress-tracker.md`** to mark Phase 11 (Deployment Baseline) complete, with the live URLs and verification method (direct curl checks: health, CORS preflight, rendered content) as the completion evidence.
2. **Run `/feature-docs` for `docs/plan/phase-11-deployment-baseline/`** — this phase's `/architect` planning session was never captured via `/session-docs` either (unlike Phase 10's grilling+architect sessions); consider whether both are still worth doing retroactively, or just `/feature-docs` per this project's stated convention for phase completion.
3. **Phase 12 (Postgres-backed latest-session dashboard)** is the next real phase — not yet planned. Needs its own `/grill-with-docs` or `/architect` session per the standing intention recorded in the prior memory block.
4. Optional, low priority: decide whether to commit a version of `.env.example` with real values ever, or leave it permanently as an empty template (current recommendation: leave empty, real values live in the host dashboards + README).

## Open questions

Carried forward, still genuinely unresolved: PR #2–#9 merge timing, pre-Phase-6 `docs/plan/*` retrofit, `/model sonnet` availability, derived Payment Aging badges — all unchanged from prior sessions, not revisited.

New this session:

- Whether Phase 10's `/grill-with-docs`-style planning rigor (grilling + architect + ADR, fully documented) should be retroactively applied to Phase 11's `/architect`-only session, or whether the existing plan-file record is sufficient — not decided.
- Whether/when to revisit the stashed SQLite reporting work for Phase 12, versus building Phase 12 as a clean Postgres-first design without reusing any of it — not decided, genuinely open until Phase 12 planning starts.

---

# Memory — Phase 11 Doc Catch-Up + Mobile Nav/Shell Responsiveness Pass

Last updated: 2026-07-13 (appended; all prior session content above is unchanged)

## What was built

- **Phase 11 documentation catch-up:** `context/progress-tracker.md` updated to mark Phase 11 (Deployment Baseline) complete — "Current Status"/"Progress" checklist/"Decisions Made" all updated with the live URLs (Render `https://sales-ops-6e84.onrender.com`, Vercel `https://sales-ops-gamma.vercel.app/`) and the verification method (direct curl: `/health`, root redirect + rendered content, CORS preflight). `docs/plan/phase-11-deployment-baseline/{plan,explanation,ai-discussion-topics}.md` written via `/feature-docs`.
- **Mobile Nav/Shell Responsiveness pass (new, named, non-phase-numbered feature):** planned via `/architect` in Plan Mode, then implemented. Fixes the Phase 10.2-flagged limitation where the fixed `w-60` `SidebarNav` squeezed main content on mobile viewports — the app is live in production now, so this was a real user-facing gap, not theoretical.
  - **New `--overlay` token** (`app/globals.css`, `tailwind.config.ts`, `context/ui-tokens.md`) — reuses `--surface-inverse`'s HSL triple, exposed as `bg-overlay`/`bg-overlay/50`, scoped to drawer/modal backdrops only.
  - **`components/layout/AppShell.tsx`** promoted from Server to Client Component: holds `isDrawerOpen` state; two separate sidebar wrappers — an always-mounted desktop wrapper (`hidden lg:block`) and a mobile drawer + backdrop that are **conditionally rendered only while open** (not a permanently-mounted `-translate-x-full` panel); closes on backdrop click, `Escape`, and automatic route-change (render-time state adjustment, not a `useEffect`, to satisfy the `react-hooks/set-state-in-effect` lint rule); moves focus into the drawer's first link on open via a `drawerRef` effect.
  - **`components/layout/TopHeader.tsx`** promoted to Client Component: new `lg:hidden` icon toggle button (`Menu`/`X` from `lucide-react`), `aria-expanded`/`aria-controls="mobile-sidebar-drawer"`/state-dependent `aria-label`.
  - **`components/layout/SidebarNav.tsx`** — unchanged, reused as-is inside both wrappers.
  - Docs: `context/ui-tokens.md`, `context/ui-registry.md` (`AppShell`/`SidebarNav`/`TopHeader` entries + new "Page composition notes (Mobile Nav/Shell Responsiveness)" section, Phase 10.2 known-limitation note marked resolved), `context/progress-tracker.md` (new named checklist section + 2 Decisions Made entries). `docs/plan/mobile-nav-shell-responsiveness/{plan,explanation,ai-discussion-topics}.md` via `/feature-docs`; `docs/architect/mobile-nav-shell-responsiveness/{decisions,discussion,ai-discussion-topics}.md` via `/session-docs`.
  - `/imprint` run afterward on `AppShell`/`TopHeader` — entries already matched the registry format (written during implementation per the repo's own rule), so no duplication; added one small addendum flagging that this pass's `z-40`/`z-50` backdrop/drawer pair is the app's first stacking-context precedent above chart tooltips' `z-10`, with no documented z-index scale yet — worth deciding deliberately if a future modal/toast needs to layer above it.
- **Git:** committed as `a2cc9cb` ("docs: complete Phase 11 documentation and add mobile nav/shell responsiveness pass") on `phase/10-fastapi-integration`, pushed (updates PR #9). Verified `origin/deploy/portfolio-demo` was still at the prior commit (`974b348`, in sync with `origin/phase/10-fastapi-integration`) before fast-forwarding it to `a2cc9cb` and pushing — confirmed a clean fast-forward via `git merge-base --is-ancestor` first, no force-push needed. Both branches are now at `a2cc9cb` on GitHub; Render/Vercel should pick this up on their next deploy trigger.

## Decisions made

- **Breakpoint: `lg` (1024px)**, not `md` — matches the app's existing `lg`-based responsive convention (workflow-page KPI grids), and specifically fixes portrait-tablet widths that `md` would have left broken.
- **Two separate wrapper elements, not one dual-purpose `-translate-x-full` wrapper** — a direct user correction during plan review. A permanently-mounted, transform-only drawer leaves its nav links in the keyboard tab order even while visually off-canvas; the mobile wrapper is only mounted in the DOM while open, so there's nothing to tab into when closed.
- **No `role="dialog"`/`aria-modal="true"` on the drawer** — another direct user correction. Claiming modal semantics without a real focus trap (deliberately not implemented, to keep this a "narrow pass") would overstate what the implementation does; `SidebarNav`'s own `<nav>` landmark provides real semantics instead.
- **Hand-rolled drawer, no headless dialog library** — matches this project's established precedent (Phase 8/9) of hand-writing primitives against its own tokens rather than adopting a component library.
- **No animated slide transition in this pass** — conditional mounting (chosen for the tab-order fix) and a smooth bidirectional CSS transition don't compose without extra mount/unmount timing logic that was deliberately left out of scope; the dimmed backdrop gives feedback instead.
- **Docs required even though this isn't a numbered phase** — user-required. Followed the "Sample Data Enrichment"/mock-data-pipeline-reconnection precedent of full `/feature-docs` + `/session-docs` treatment for named, non-phase work. Tracked in `context/progress-tracker.md` as a named entry, not claiming the reserved Phase 12 slot.
- **Bundled into one commit**, not split across two, despite covering two distinct workstreams (Phase 11 docs + mobile nav feature) — `context/progress-tracker.md` had interleaved edits for both in the same session, and splitting would have needed a `git add -p` partial-file stage; the repo's own precedent (several past sessions) already bundles a whole session's work into one commit when done in one sitting.

## Problems solved

- **`react-hooks/set-state-in-effect` lint error**: the first implementation closed the drawer on route change via `useEffect(() => setIsDrawerOpen(false), [pathname])` — ESLint rejected this as an avoidable extra render pass. Fixed using React's documented "adjust state during render" pattern instead: track the last-seen `pathname` in state, and call `setState` directly in the render body (not inside an effect) when it differs. This does not cause an infinite loop — React detects the state change during render and restarts that same render before committing, rather than scheduling a whole separate render+effect cycle.
- **Real keyboard focus-management bug found by Playwright, not by inspection**: the first full verification pass (14/15 checks) caught that opening the drawer via keyboard and pressing Tab once jumped straight into `<main>` content, skipping the drawer's own links entirely. Root cause: the drawer wrapper renders *before* `TopHeader` in the DOM (fixed positioning controls visual placement, not tab order), so tabbing forward from the toggle button (which sits after the drawer in source order) moves into main, not backward into the drawer. Fixed by focusing the drawer's first `<a>` directly (`drawerRef.current?.querySelector("a")?.focus()`) in an effect keyed on `isDrawerOpen` — not a full focus trap, just a correct entry point. Re-verified: 15/15 checks passed after the fix.
- **IDE-reported ARIA diagnostic on `TopHeader.tsx` was a false positive**: an inline diagnostic claimed invalid `aria-expanded`/`aria-controls` values, but the project's real `npm run lint` (ESLint) passed clean on that exact file both before and after — treated as an editor-tooling artifact, not a real issue, and not investigated further since the authoritative lint command was unaffected.

## Current state

- **PR #9** (`phase/10-fastapi-integration` → `phase/9-...`) now at commit `a2cc9cb`, pushed. `deploy/portfolio-demo` fast-forwarded to the same commit and pushed — both branches in sync on GitHub as of this session.
- `npm run typecheck`/`lint`/`build` all clean. Live-browser verification via a throwaway Playwright script (installed, run, then fully uninstalled + scripts deleted per established practice — confirmed no trace via `git status`/`git diff --stat package.json`): 15/15 checks passed covering mobile drawer open/close (toggle, backdrop click, Escape, route-change auto-close), full-width main content when closed, desktop sidebar unchanged with no toggle/backdrop ever appearing, and a keyboard-only pass (nav links unreachable via Tab while closed, reachable once open).
- `uv run pytest` not re-run this session (no Python touched) — last known count 196 passing, unchanged.
- **Working tree has two small uncommitted items, deliberately left that way:** `.env.example` (locally filled with real deployed URLs for the user's own reference — including a trailing-slash CORS value, the same class of bug caught and fixed in the actual Render dashboard config during the Phase 11 session — per established practice this file stays an empty template in git, never committed with real values); `context/ui-registry.md` (the `/imprint` z-index addendum, made *after* this session's commit/push — not yet committed).
- `memory.md` itself intentionally excluded from every commit, per established practice.

## Next session starts with

1. **Commit the small `/imprint` addendum to `context/ui-registry.md`** (the z-index stacking-context note) whenever convenient — low priority, not blocking, just currently sitting uncommitted after the main commit/push already happened.
2. **Verify the live deployment actually picked up this session's UI change** — this was the first *visual/layout* change (not just docs/backend) pushed to `deploy/portfolio-demo` since the Phase 11 deploy baseline; worth a quick live check on `https://sales-ops-gamma.vercel.app/` at a mobile width once Vercel's redeploy completes, to confirm the drawer behaves the same in production as it did in local Playwright verification.
3. Standing rule (confirmed across every phase since Phase 4): re-check live PR merge status before assuming anything — not touched or re-verified this session.
4. Phase 12 (Postgres-backed latest-session dashboard) is still the next real phase — not yet planned, unaffected by this session's work.

## Open questions

Carried forward, still genuinely unresolved: PR #2–#9 merge timing, pre-Phase-6 `docs/plan/*` retrofit, `/model sonnet` availability, derived Payment Aging badges, Phase 10's planning rigor retroactively applied to Phase 11, stashed SQLite reporting work's fate for Phase 12 — all unchanged from prior sessions, not revisited this session.

New this session:

- **No documented z-index scale exists yet** — this session's `z-40`/`z-50` backdrop/drawer pair is the app's first stacking-context precedent above chart tooltips' `z-10`. Flagged via `/imprint`, not resolved — worth deciding deliberately (not picking an arbitrary higher number) the next time a modal, toast, or other layered UI element needs to coexist with this drawer.
- Whether the drawer should eventually get an animated slide-in/out transition — explicitly deferred this session in favor of the simpler conditional-mount fix for the keyboard tab-order bug; not decided whether it's worth revisiting.

---

# Memory — Phase 12: Postgres-Backed Latest-Session Dashboard (Planned, Built, Deployed, Live-Verified)

Last updated: 2026-07-14 (appended; all prior session content above is unchanged)

## What was built

- **Planning:** `/grill-with-docs` (`/grilling`, `/domain-modeling` folded in inline) — 13 resolved decisions plus a two-round "more to grill first" follow-up (4 more real gaps closed) plus two Plan Mode rejection rounds with substantive corrections before approval. Full session record written via `/session-docs` to `docs/grilling/phase-12-postgres-backed-latest-session-dashboard/{session,explanation,ai-discussion-topics}.md`.
- **`docs/adr/0007-session-scoped-workflow-result-persistence.md`** (new) — fills a filename slot that was reserved-but-never-written by the paused SQLite work. **`CONTEXT.md`** gained 5 new terms (Anonymous Session ID, Saved Workflow Result, Workflow Results Store, Persistence Outcome, Dashboard Latest Results, Result Schema Version, Display Expiry — 7 counting both) and 2 amended terms (Workflow Request, Current Result).
- **`docs/archive/phase-11-sql-reporting-sqlite-plan.md`** (new) — the old paused SQLite plan, copied in verbatim from `~/.claude/plans/`, with a note explaining it was superseded (not completed) by ADR 0007.
- **Neon Postgres** project created, 3 branches: `main` (Render's `DATABASE_URL` secret), `dev`, `test` (both in local gitignored `.env`, never `.env.example`).
- **Backend (all new unless noted):** `backend/db.py` (single-transaction, advisory-lock-guarded, checksum-verified migration runner; `DATABASE_URL`-optional pool with bounded cold-start retry), `backend/migrations/0001_create_workflow_results.sql`, `backend/session.py` (`get_session_id`), `backend/repositories/workflow_results.py` (`WorkflowResultsRepository`, FastAPI-injected), `backend/persistence.py` (`persist_workflow_result`, shared defensive write-path glue), `backend/routers/dashboard.py` (`GET /api/dashboard`). Modified: `backend/main.py` (lifespan hook, `app.state.db_pool = None` default, CORS `expose_headers += X-Persisted`), `orders.py`/`inventory.py`/`payments.py` routers (persist after computing; `inventory.py` persists only `inventory_allocation`, never its internal validation byproduct; report endpoints untouched), `src/contracts.py` (`CONTRACT_SCHEMA_VERSIONS`).
- **Frontend (all new unless noted):** `lib/session-id.ts` (`getOrCreateSessionId`), `types/dashboard.ts`, `components/feedback/PersistenceNotice.tsx`, `components/dashboard/DashboardLiveSections.tsx` (Client Component — required because `localStorage` doesn't exist during a Server Component's render). Modified: `lib/api-client.ts` (`X-Session-Id` header, `postJSON` now returns `{data, persisted}`, new `getDashboardResults()`), all 3 workflow pages (`PersistenceNotice` on `X-Persisted: false`), `app/dashboard/page.tsx` (trimmed to static shell + `<DashboardLiveSections />`), `components/workflow/MetricCard.tsx` (new optional `sample` chip prop).
- **Tests:** `tests/test_backend_persistence_routing.py` (15, mocked repository via `app.dependency_overrides`, always run) + `tests/test_workflow_results_repository.py` (8, `@pytest.mark.db`, real Neon `test` branch, skip — don't fail — without `TEST_DATABASE_URL`). `pyproject.toml` gained the `db` marker.
- **Docs updated:** `context/architecture.md`, `context/build-plan.md`, `context/progress-tracker.md`, `context/ui-registry.md`, `CLAUDE.md` — all for Phase 12. Feature docs written via `/feature-docs` to `docs/plan/phase-12-postgres-backed-latest-session-dashboard/{plan,explanation,ai-discussion-topics}.md`, plus a verbatim `approved-plan.md` copy of the Plan Mode document (explicit user request).
- **Git/deploy:** new branch `phase/12-postgres-session-dashboard` (off `phase/10-fastapi-integration`), committed as `f2e38e5`, pushed, **PR #10** opened (base `phase/10-fastapi-integration`, continuing the stacked chain): https://github.com/gwho/sales-ops/pull/10. `deploy/portfolio-demo` fast-forwarded `a2cc9cb` → `f2e38e5` and pushed. Render manually redeployed by the user; live-verified.

## Decisions made

- **`localStorage` + `X-Session-Id` header, no cookies** — avoids cross-site cookie complexity (`SameSite=None`, `allow_credentials`) between Vercel and Render for an identity that needs no auth properties. This single choice structurally forced the dashboard's live sections into a **Client Component** (`DashboardLiveSections`), not a Server Component fetch — a Vercel-side render has no access to `localStorage`. Explicitly retires the old paused-SQLite-plan assumption of an async Server Component + `force-dynamic` dashboard.
- **Persistence is folded into the existing 3 workflow endpoints, best-effort, never fails the request** — outcome always reported via `X-Persisted: true/false/skipped`, never silent. Enforced by a shared `persist_workflow_result` helper with its own defensive `try/except`, added after the route-orchestration tests themselves revealed the original per-router code had no defense against a repository that violates its own "never raises" contract.
- **`POST /api/inventory/allocate` never persists the internal `validate_orders()` byproduct** — only `inventory_allocation`. Report endpoints (`.../report`) are entirely untouched by Phase 12 — ADR 0006 stays fully accurate for them.
- **One JSONB table (`workflow_results`), verbatim Output Contract per row, upserted latest-wins** — not a normalized SQL-reporting schema like the paused SQLite design, since the read pattern is "latest result for this session," never cross-session analytics. `result_schema_version` (in `src/contracts.py`, next to the TypedDicts it versions) plus a 30-day TTL (**display expiry, not deletion**) both funnel through one shared "is this row usable?" predicate on read.
- **`psycopg` 3, hand-written SQL, no ORM; hand-written migrations (no Alembic), run in the FastAPI lifespan hook as one transaction**, advisory-lock-guarded, checksum-verified, with a bounded cold-start retry kept under Render's health-check timeout. Three distinct DB states, never conflated: `DATABASE_URL` unset (persistence off, not an error, `200` all-null), set-but-unreachable-at-boot (fail-closed startup after the bounded retry), and a post-startup outage (`GET /api/dashboard` → `503`, the only case that produces it).
- **Neon branching (`main`/`dev`/`test`) + a 2-layer test suite** — mocked-repository route-orchestration tests (always run, fast) + real-Neon repository/SQL tests (`@pytest.mark.db`, skip without `TEST_DATABASE_URL`, a deliberately separate env var from `DATABASE_URL` so a misconfigured environment can never point a cleanup-driven test at `dev`/`main`). Preserves `uv run pytest`'s zero-config hermeticity.
- **`X-Persisted: false` gets a small non-blocking `PersistenceNotice`; `true`/`skipped` render nothing** — matches this app's existing no-success-chrome convention. `skipped` is effectively unreachable from the real frontend.

## Problems solved

- **Real secret-leak near-miss**: real Neon connection strings (including the password) were briefly written into the *tracked* `.env.example` instead of the gitignored `.env`. Caught immediately via `git status`/`git diff --cached` before anything was staged or committed; moved to `.env` (confirmed gitignored), `.env.example` restored to its empty-template convention. Nothing was ever exposed on GitHub. **Going-forward rule for the user: real values always go in `.env`, never `.env.example`.**
- **`app.state.db_pool` `AttributeError`** in every pre-existing (Phase 10-era) backend test: those tests construct `TestClient(app)` at module scope without entering it as a context manager, so Starlette never runs the new `lifespan` hook. Fixed with a one-line default (`app.state.db_pool = None` right after `app = FastAPI(...)`) rather than touching any pre-existing test file.
- **`uv add psycopg[binary,pool]`** failed at the shell level (unquoted `[...]` is a glob metacharacter) — fixed by quoting: `uv add "psycopg[binary,pool]"`.
- **`source .env` parse error** on an unquoted Neon connection string containing `&` (a shell control character outside quotes, and every Postgres connection string with >1 query param has one) — fixed by quoting the value in `.env`.
- **Playwright verification false negative**: one check ("Outstanding by Aging Bucket still shows Sample data") failed while a structurally identical sibling check passed. Confirmed via direct DOM inspection (a separate xpath-ancestor query) that the product was correct and the verification script's own locator (`.locator("..")`, single-level parent) was the bug, not the app.
- **Stray `backend/reporting_db/__pycache__`** (compiled bytecode only, no source, untracked — leftover from the paused SQLite session) found and removed before starting new backend work.

## Current state

- **PR #10** open (`phase/12-postgres-session-dashboard` → `phase/10-fastapi-integration`), continuing the stacked chain (#2 through #9 all still open, unmerged, unchanged).
- **`deploy/portfolio-demo`** at commit `f2e38e5`, matching PR #10's head. **Render redeployed (manually triggered by the user) and is confirmed live** at https://sales-ops-6e84.onrender.com — `DATABASE_URL` is set there (screenshot-confirmed), pointing at Neon's `main` branch.
- **Full live end-to-end verification passed**, via direct curl against production: `/health` → `200`; fresh session → `GET /api/dashboard` → `200` all-null; running Order Validation with real sample data → `200`, `X-Persisted: true`; re-querying the dashboard with the same session → returns the real live result, not sample; CORS from the live Vercel origin correctly exposes `X-Persisted`. **Directly confirmed in Neon's own table browser** on the `main` branch: exactly one `workflow_results` row exists, matching the verification run's session ID, `workflow_type`, and result content.
- `uv run pytest`: 212 passing / 7 skipped, fully hermetic with zero env vars. `npm run typecheck`/`lint`/`build` clean. Local dev servers (FastAPI `:8000` against Neon `dev`, Next.js `:3000`) were left running earlier in the session — may or may not still be up depending on how much time has passed.
- One harmless leftover: the live verification run left one real row in the **production** `main` Neon branch (throwaway UUID, not attributable to any real visitor) — no cleanup needed or attempted; it will simply stop appearing on any dashboard after its 30-day TTL via Display Expiry.

## Next session starts with

1. **Nothing is blocking.** Phase 12 is planned, built, tested, documented, committed, PR'd, deployed, and live-verified in production — a genuinely complete phase, unusually so.
2. Whether/when to merge the stacked PR chain (#2 through #10) is still the user's call — unchanged across every phase since Phase 4, not revisited this session.
3. No phase is currently planned beyond Phase 12. Any new work (e.g. real cross-session history, active TTL deletion, authenticated accounts) is new scope needing its own planning pass — ADR 0007's "Consequences" section explicitly flags each of these as out of scope for what was just built.
4. The paused SQLite work (`git stash@{0}`) remains untouched and unaffected by Phase 12 — formally superseded for dashboard purposes, but its fate (delete vs. keep as historical reference) is still an open question, now with a permanent copy also living at `docs/archive/phase-11-sql-reporting-sqlite-plan.md` regardless of what happens to the stash itself.

## Open questions

Carried forward, still genuinely unresolved: PR #2-#10 merge timing, pre-Phase-6 `docs/plan/*` retrofit, `/model sonnet` availability, derived Payment Aging shorthand badges, Phase 10's grilling rigor retroactively applied to Phase 11, the stashed SQLite work's ultimate fate (delete vs. keep), whether the drawer should get an animated transition, no documented z-index scale yet — all unchanged from prior sessions, not revisited this session.

New this session:

- Whether to ever build active TTL deletion (the "opportunistic delete-on-write" upgrade path named in ADR 0007) — explicitly deferred, the bounded-per-session row count means it isn't solving a real problem yet; revisit only if Neon storage actually becomes a concern.
- Whether Render's auto-deploy is enabled for `deploy/portfolio-demo` or requires a manual trigger every time — this session needed a manual "Deploy latest commit" click; not confirmed whether that's a one-off or the standing behavior for future deploys.
