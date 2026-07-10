# Plan — Feature phase-9.1-visual-alignment-fixes: Visual Alignment Fixes

## What was built

**Modified:**

- `app/dashboard/page.tsx` — icon chips on every `MetricCard`; removed the inline `SegmentedBar`/`AgingBucketBars` calls from the Inventory Allocation and Payment Aging KPI sections; added a new `DonutBreakdownChart` + `VerticalBucketBarChart` section directly below the 3 KPI strips; added "Inventory Shortage Alerts" and "Payment Follow-up Items" plain (non-`DataTable`) tables; added a "How the Workflows Connect" infographic and an English-only "How This Demo Works" guide section; `mt-8` → `mt-6` section spacing.
- `app/inventory-allocation/page.tsx` — restructured from 4 stacked tables to 1 main "Allocation Results" table (Status/Priority/Warehouse `FilterToolbar` + search) plus "Remaining Inventory" and "Supplier Follow-up" in a compact `grid lg:grid-cols-2` pair with `bg-surface-subtle` panels; the standalone "Backorders" table was removed (now a `Status` filter option on the main table); `MiniBar`s on `allocated_qty`/`backorder_qty`/`remaining_qty`; icons/captions via `TableSectionHeading`; extended sort coverage, right-aligned numeric columns, truncate+`title` on long text; added the disabled "Download Report" button.
- `app/order-validation/page.tsx` — `FilterToolbar` (Severity + search on Validation Errors; Priority + search on Valid Orders); icons/captions; extended sort coverage, alignment, truncation; download action.
- `app/payment-aging/page.tsx` — `FilterToolbar` (Aging Bucket + Follow-up Priority + search); icons/captions; extended sort coverage, alignment, truncation; download action; static "As of {generated_at}" date label; local `AgingBucketBars` function extracted to the new shared component.
- `app/reports/page.tsx` — `FileSpreadsheet` icon on the page title; `max-w-5xl` → `max-w-6xl`.
- `components/layout/AppShell.tsx` — outer wrapper `flex min-h-screen` → `flex h-screen overflow-hidden`; content column `flex min-h-screen flex-col` → `flex h-full flex-col overflow-hidden` (Critical sidebar-height fix).
- `components/layout/SidebarNav.tsx` — `h-screen` → `h-full` (+ `overflow-y-auto`); brand label `"Sales Admin Toolkit"` → `"Sales Admin Automation Toolkit"`.
- `components/tables/DataTable.tsx` — zebra striping (odd rows `bg-surface-muted`); new `wrap?: boolean` column flag (default `whitespace-nowrap`); new `align?: "left" | "right"` column flag; updated doc comment (filtering lives outside `DataTable`).
- `components/ui/Badge.tsx` — leading tone-colored dot (`dot?: boolean`, default `true`); `font-medium` → `font-semibold`.
- `components/ui/Table.tsx` — `px-4 py-3 text-sm` → `px-3 py-2 text-xs` (header and body cells); header cells gained `whitespace-nowrap`.
- `components/workflow/MetricCard.tsx` — optional `icon`/`tone` props render a `w-7 h-7 rounded` chip.
- `components/workflow/WorkflowStepper.tsx` — collapsed the 3-state (`done`/`current`/`upcoming`) model to 2 states (`done`/`upcoming`); every step at or before `currentStep` now renders as `done`.
- `context/progress-tracker.md` — Phase 9.1 status, checklist, and Decisions Made entries.
- `context/ui-contract-plan.md` — 2 new Derived Display-Only Aggregates: "Gap to Reorder Point," "Outstanding amount by aging bucket."
- `context/ui-registry.md` — updated entries for every changed component; new entries for every new component; new "Charts" section; new "Page composition notes (Phase 9.1)" section.
- `lib/mock-data.ts` — added `amountByAgingBucket()`.

**Created:**

- `components/charts/DonutBreakdownChart.tsx` — pure-SVG donut (stacked circle strokes), Server Component.
- `components/charts/VerticalBucketBarChart.tsx` — pure-CSS vertical bar chart, Server Component.
- `components/tables/AgingBucketBars.tsx` — extracted from `payment-aging/page.tsx`, now shared by `/dashboard` and `/payment-aging`.
- `components/tables/FilterSelect.tsx` — one labeled dropdown filter control (funnel icon + "FILTER" label).
- `components/tables/FilterToolbar.tsx` — composes an optional search input, `FilterSelect` children, and a clear action.
- `components/tables/MiniBar.tsx` — inline quantity/progress indicator for table cells.
- `components/tables/SegmentedBar.tsx` — multi-category share-of-total bar + legend.
- `components/tables/TableSectionHeading.tsx` — icon + title + one-line caption, used above every table/panel section.

`memory.md` is excluded from this feature — pre-existing modified state from a prior session, left alone per standing user instruction.

## Schema changes

None. No database exists in this project.

## Key invariants

- **`AppShell`'s outer wrapper must stay `h-screen overflow-hidden`, and `SidebarNav` must stay `h-full`, never `h-screen`.** Reintroducing `h-screen` on `SidebarNav` (or removing the `overflow-hidden`/height cap on `AppShell`'s wrappers) reintroduces the Critical bug this phase fixed: the sidebar pins to exactly one viewport while the content column grows past it on any route with real content.
- **Every `Tone → class` mapping is a literal `Record<Tone, string>` object, never a dynamically interpolated class name** (e.g. never `` `bg-${tone}` ``). Tailwind's static scanner only finds classes that appear as literal substrings somewhere in the source. This rule now applies to `Badge`'s dot, `MiniBar`, `SegmentedBar`, `DonutBreakdownChart`'s stroke map, and `VerticalBucketBarChart`'s fill map — five separate maps, all following the same pattern.
- **Chart components (`components/charts/`) never decide their own tone.** They accept a `tone: Tone` per segment/bar already resolved by the caller via `allocationStatusTone`/`agingBucketTone` (exported from `components/workflow/StatusBadge.tsx`). Only the `Tone` *type* is imported into chart/table-viz files — never the tone-resolution functions themselves — so there is no runtime dependency from `components/charts/` or `components/tables/` back into `components/workflow/`.
- **`DataTable` still does not filter.** Pages own filter state via `FilterToolbar`/`FilterSelect` and pass an already-filtered array into `DataTable`'s `data` prop. `DataTable` only ever decides whether that array is empty (falls back to `EmptyState`) — it has no filtering logic of its own and should not gain any.
- **`DataTable` columns are `whitespace-nowrap` by default.** Set `wrap: true` only for genuinely long free text (there is currently no column using it — `error_message`/`suggested_action` truncate with a `title` tooltip instead, per the Phase 9.1 review correction that superseded an earlier `wrap: true` attempt). Numeric/amount/count columns set `align: "right"`.
- **Never run `npx shadcn add`.** `components.json`'s `baseColor: "slate"` still risks injecting shadcn's default `--primary`/`--card`/`--destructive`/`--ring` tokens into `globals.css` on first generate. All primitives (`components/ui/`) stay hand-written.
- **`amountByAgingBucket()` (amount) and `PaymentAgingSummary.aging_bucket_counts` (count) are different aggregates — do not conflate them.** The dashboard's `VerticalBucketBarChart` uses the former; `AgingBucketBars` (both on `/dashboard`'s Order Validation... no, Payment Aging section removed — and on `/payment-aging` itself) uses the latter.
- **Every new/changed component pattern is documented in `context/ui-registry.md` before being considered "done."** This phase touched or added 14 components across 4 review passes; the registry is the only place all of it is reconciled in one document — treat it as more current than this file for exact class strings.
