# Plan — Feature phase-9-reusable-ui-components-static-pages: Reusable UI Components and Static Pages

## What was built

**Created — `components/ui/` (hand-written primitives, never `npx shadcn add`):**

- `Button.tsx` — `cva`-variant button (`primary`/`secondary`), forwards ref.
- `Card.tsx` — token-styled card shell (`rounded-xl border border-border bg-surface p-6 shadow-sm`).
- `Badge.tsx` — `cva`-variant pill with a `tone` prop (`success`/`warning`/`danger`/`info`/`neutral`).
- `Table.tsx` — semantic table primitives (`Table`, `TableHead`, `TableBody`, `TableRow`, `TableHeaderCell`, `TableCell`).

**Created — `components/layout/`:**

- `SidebarNav.tsx` (Client — `usePathname()`) — fixed 5-route nav with active-link highlighting.
- `TopHeader.tsx` (Server) — static app name + demo-mode pill.
- `AppShell.tsx` (Server) — composes `SidebarNav` + `TopHeader` + `{children}`.

**Created — `components/feedback/`:**

- `EmptyState.tsx`, `LoadingState.tsx`, `BusinessErrorMessage.tsx` — all Server Components.

**Created — `components/workflow/`:**

- `StatusBadge.tsx` (Server) — thin `Badge` wrapper plus 5 exported tone-mapping helper functions (`severityTone`, `allocationStatusTone`, `importancePriorityTone`, `agingBucketTone`, `followUpPriorityTone`, `reportLifecycleTone`) and the `ReportLifecycleState`/`Tone` types.
- `MetricCard.tsx` (Server) — label + value KPI tile.
- `ReportCard.tsx` (Server) — renders a `ReportManifest` in the `Ready` state, or one of 3 other lifecycle states as a prop-driven visual variant.
- `UploadPanel.tsx` (Client — `useState`) — functional file picker; never parses the file or gates content.
- `WorkflowStepper.tsx` (Server) — fixed-step progress indicator, `steps`/`currentStep` props only.

**Created — `components/tables/`:**

- `DataTable.tsx` (Client, always) — generic typed-column table with single-column local sort; falls back to `EmptyState` on zero rows.

**Created — `lib/`:**

- `mock-data.ts` — typed re-exports of the 4 committed mock JSON files, plus `ninetyPlusDaysAmount()` (derived aggregate for the Payment Aging "90+ Days Amount" KPI).
- `formatters.ts` — `formatNumber`, `formatAmount`, `formatDate` (timezone-safe for `YYYY-MM-DD` contract dates), `formatDateTime`.

**Modified:**

- `app/layout.tsx` — wraps `{children}` in `AppShell`.
- `app/dashboard/page.tsx` — real per-workflow KPI strips, 3 `ReportCard`s, 3 workflow entry cards (Server Component).
- `app/reports/page.tsx` — one `ReportCard` per `report_type` from `lib/mock-data.ts` (Server Component).
- `app/order-validation/page.tsx`, `app/inventory-allocation/page.tsx`, `app/payment-aging/page.tsx` — full workflow screens (`UploadPanel`(s), `WorkflowStepper`, KPI strip, `DataTable`s, badges). **All 3 are Client Components** (`"use client"`) — see Key invariants.
- `context/ui-registry.md` — 12 real component entries + a `Primitives` section, replacing the "planned" placeholder list.
- `context/progress-tracker.md` — Phase 9 checklist checked off, Current Status advanced, 2 new Decisions Made entries.

## Schema changes

None. No database exists in this project; the Python core and the Next.js UI are both stateless and file-driven.

## Key invariants

- **Any page that builds a `DataTable` `columns` prop must be a Client Component.** React Server Components cannot pass functions as props to Client Components, and `DataTable`'s column config carries `render`/`sortValue` functions. This is why `order-validation`, `inventory-allocation`, and `payment-aging` pages are `"use client"` even though the original plan expected them to stay Server Components — only `DataTable` itself was planned as client. `dashboard` and `reports` don't use `DataTable` and correctly remain Server Components. If a future page needs `DataTable` and should stay a Server Component, the fix is to move that page's column definitions into a small dedicated Client child component that receives only serializable `data` as a prop — not to try to pass functions across the boundary.
- **`StatusBadge` never infers tone from the label string.** The same label ("High") means a different tone depending on which contract field it came from (order/allocation `priority` is an importance ranking → `warning`; payment `follow_up_priority` is an urgency ranking → `danger`). Callers must always pass an explicit `tone` computed via one of `StatusBadge.tsx`'s exported domain helpers. The full mapping is documented in `context/ui-registry.md`'s StatusBadge entry — treat that table as the single source of truth, not this file.
- **`components.json`'s `baseColor: "slate"` must never be exercised.** Never run `npx shadcn add`. It will inject shadcn's default `--primary`/`--card`/`--destructive`/`--ring` CSS variables into `app/globals.css`, colliding with this project's `--accent` and friends. All primitives live under `components/ui/`, hand-written.
- **`lib/mock-data.ts` is the only place pages import mock JSON from.** Pages must not `import` from `lib/mock-data/*.json` directly — importing through `lib/mock-data.ts` keeps the `as OrderValidationResult` (etc.) type assertion in exactly one place.
- **No Recharts, no TanStack Table, no fake async/timer-driven state.** These are all deliberate Phase 9 scope boundaries (see `docs/plan/phase-9-reusable-ui-components-static-pages/plan.md`'s original architect plan for the reasoning) — do not reach for them to "improve" a Phase 9 page without a scope decision, since Phase 10's real API integration will likely change what's actually needed.
- **`ReportCard`'s non-`Ready` states, `LoadingState`, and `BusinessErrorMessage` have no live call sites yet.** They exist as correctly-built, prop-driven visual variants (captured in `/imprint`) specifically so Phase 10 can wire them to real state without rebuilding them — don't delete them for being "unused" by static analysis.
