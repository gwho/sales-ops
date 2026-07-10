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
