# UI Registry

Living registry for Sales Admin Automation Toolkit components.

Read this before building a new UI component. After building any reusable component, update this file using `/imprint` or the same table format below.

## Component Registry Format

```text
### ComponentName

File: `components/.../ComponentName.tsx`
Last updated: YYYY-MM-DD

| Property | Class |
| --- | --- |
| Background |  |
| Border |  |
| Border radius |  |
| Text - primary |  |
| Text - secondary |  |
| Spacing |  |
| Hover/focus state |  |
| Shadow |  |
| Accent/status usage |  |

Pattern notes:
[Short notes that future agents must preserve.]
```

## Primitives

Hand-written under `components/ui/` in Phase 9 — never generated via `npx shadcn add` (that would inject shadcn's default `--primary`/`--card`/`--destructive`/`--ring` tokens into `globals.css`, colliding with this project's tokens, notably `--accent`). These aren't in the 12-component registry below; they're the building blocks the registered components compose.

| Component | File | Classes |
| --- | --- | --- |
| `Button` | `components/ui/Button.tsx` | `rounded-md px-4 py-2 text-sm font-medium`; primary: `bg-accent text-text-on-accent hover:bg-accent-hover`; secondary: `border border-border bg-surface text-text-primary hover:bg-surface-muted` |
| `Card` | `components/ui/Card.tsx` | `rounded-xl border border-border bg-surface p-6 shadow-sm` |
| `Badge` | `components/ui/Badge.tsx` | `rounded-full px-3 py-1 text-xs font-semibold`; tone maps to `bg-{success,warning,danger,info}-subtle text-{success,warning,danger,info}` or `bg-surface-muted text-text-secondary` for neutral. Phase 9.1: leading `dot?: boolean` (default `true`) renders a `h-1.5 w-1.5 rounded-full bg-{tone}` (solid) dot before the label — every current `StatusBadge` usage keeps it on; pass `dot={false}` only for a hypothetical future non-status badge. |
| `Table` (+ `TableHead`/`TableBody`/`TableRow`/`TableHeaderCell`/`TableCell`) | `components/ui/Table.tsx` | Wrapper: `rounded-xl border border-border overflow-hidden`; header cells: `px-3 py-2 text-xs font-medium uppercase tracking-wide text-text-secondary whitespace-nowrap`; body cells: `px-3 py-2 text-xs text-text-primary` (Phase 9.1: tightened from `px-4 py-3 text-sm` for a denser operations-table look, matching the Figma references' table density) |

## Components

### AppShell

File: `components/layout/AppShell.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-background` (outer flex container) |
| Border | none (children own their borders) |
| Border radius | none |
| Text — primary | inherited |
| Text — secondary | inherited |
| Spacing | none of its own — composes `SidebarNav` + `TopHeader` + `{children}` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | none |

Pattern notes:
Server Component. Root layout wraps `{children}` in this once (`app/layout.tsx`), not per-route — no route group was introduced, so it also (harmlessly) wraps the `/` redirect page for an instant before it navigates away. Structure: `flex min-h-screen` → `SidebarNav` (fixed width) + a flex-col column of `TopHeader` + `<main className="flex-1 overflow-y-auto">`.

### SidebarNav

File: `components/layout/SidebarNav.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` |
| Border | `border-r border-border` |
| Border radius | none (full-height panel) |
| Text — primary | active link: `text-accent` on `bg-accent-subtle` |
| Text — secondary | inactive link: `text-text-secondary`, hover `text-text-primary` |
| Spacing | `w-60 p-4`, links `gap-1` |
| Hover/focus state | inactive link hover: `hover:bg-surface-muted hover:text-text-primary` |
| Shadow | none |
| Accent/status usage | active route: `bg-accent-subtle text-accent` |

Pattern notes:
Client Component (`usePathname()` for active-route highlighting via exact match). Fixed 5-item nav — do not add ERP-style extra destinations; the route set is closed per `architecture.md`.

### TopHeader

File: `components/layout/TopHeader.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` |
| Border | `border-b border-border` |
| Border radius | none |
| Text — primary | `text-sm font-medium text-text-primary` (app name) |
| Text — secondary | n/a |
| Spacing | `h-14 px-6` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | `bg-info-subtle text-info` demo-mode pill (per `ui-rules.md` Demo Mode rule) |

Pattern notes:
Server Component, static content only — layouts can't read per-page pathname/props (Next 16), so this never shows a dynamic page title. Page titles stay in each page's own `<h1>`.

### EmptyState

File: `components/feedback/EmptyState.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface-subtle` |
| Border | `border border-dashed border-border` |
| Border radius | `rounded-xl` |
| Text — primary | `text-sm font-medium text-text-primary` (title) |
| Text — secondary | `text-sm text-text-secondary` (description) |
| Spacing | `p-10`, `gap-2` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | none — intentionally neutral, not a status/warning state |

Pattern notes:
Server Component. Used as `DataTable`'s built-in zero-row fallback and standalone for `DraftMessages`. Dashed border + subtle bg is this project's one established "nothing here yet" pattern — reuse it, don't invent a second empty-state look.

### LoadingState

File: `components/feedback/LoadingState.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` |
| Border | `border border-border` |
| Border radius | `rounded-xl` |
| Text — primary | n/a |
| Text — secondary | `text-sm text-text-secondary` |
| Spacing | `p-10`, `gap-3` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | spinner: `border-t-accent` |

Pattern notes:
Server Component, built but not wired to a real Suspense boundary in Phase 9 — there's no live async fetch yet (static mock JSON import), so this has no current call site. Ready for Phase 10 when real API calls exist.

### BusinessErrorMessage

File: `components/feedback/BusinessErrorMessage.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-danger-subtle` |
| Border | `border border-border` |
| Border radius | `rounded-xl` |
| Text — primary | `text-sm text-danger` |
| Text — secondary | n/a |
| Spacing | `p-4` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | `bg-danger-subtle text-danger`, `role="alert"` |

Pattern notes:
Server Component. Always render business-readable copy here, never a raw exception — see `ui-rules.md`'s Error Messages bad/good example. No current call site in Phase 9 (no real parsing failures to surface yet); ready for Phase 10.

### StatusBadge

File: `components/workflow/StatusBadge.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | delegates to `Badge`'s tone classes |
| Border | none |
| Border radius | `rounded-full` (via `Badge`) |
| Text — primary | n/a |
| Text — secondary | n/a |
| Spacing | `px-3 py-1` (via `Badge`) |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | `success`/`warning`/`danger`/`info`/`neutral` — see mapping table below |

Pattern notes:
Server Component, thin wrapper over `Badge`. Tone is never inferred from the label string inside the component — callers pass an explicit `tone` computed by a colocated domain helper, because the same label ("High") means a different tone depending on which contract field it came from. Fixed mapping (from `docs/plan/phase-9-reusable-ui-components-static-pages/plan.md`):

| Field | Values → tone |
| --- | --- |
| `severity` | Error→danger, Warning→warning |
| `AllocationResultRow.status` | Fully Allocated→success, Partially Allocated→warning, Backordered→danger |
| Order/allocation `priority` (importance) | High→warning, Normal/Low→neutral |
| `reorder_alert` derived | "Below Reorder Point" (when Yes)→warning |
| Supplier follow-up list membership | "Supplier Follow-up"→info |
| `aging_bucket` | Current→success, 1-30 Days→info, 31-60/61-90 Days→warning, 90+ Days→danger |
| `follow_up_priority` (urgency) | High→danger, Medium→warning, Low→info, Watch/None→neutral |
| `PaymentDataIssueRow.severity` | Error (only value)→danger |
| Report lifecycle (visual variants only) | Ready→success, Processing→info, Not Generated/Needs Input→neutral |

### MetricCard

File: `components/workflow/MetricCard.tsx`
Last updated: 2026-07-09 (Phase 9.1: icon chip added)

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`); icon chip: `bg-{tone}-subtle` |
| Border | `border border-border` (via `Card`) |
| Border radius | `rounded-xl` (via `Card`); icon chip: `rounded` |
| Text — primary | `text-2xl font-semibold text-text-primary` (value) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (label) |
| Spacing | `p-4` (compact card override, not `Card`'s default `p-6`), `gap-3`; icon chip: `h-7 w-7` |
| Hover/focus state | none |
| Shadow | `shadow-sm` (via `Card`) |
| Accent/status usage | optional `icon`/`tone` props render a `w-7 h-7 rounded` chip (`bg-{tone}-subtle`, icon `text-{tone}`) top-right of the label — `success`/`warning`/`danger`/`info`/`neutral`, same `Tone` type `StatusBadge` exports |

Pattern notes:
Server Component. `p-4` overrides `Card`'s default `p-6` — KPI tiles are "compact cards" per `ui-tokens.md`'s spacing table, not "primary dashboard cards". **Phase 9.1:** icon chip is optional and purely decorative, added because `context/ui-contract-plan.md`'s Figma Reference Reconciliation had already pre-approved "label + big number + icon chip" as a safe KPI-card pattern in Phase 8/9 but it was never built. Every KPI tile across the 4 pages (~15 call sites) now passes a `lucide-react` icon + matching `tone`. Deliberately **not** adopted: the trend-delta (`+12.4%` arrow) that sits next to the icon chip in the same Figma reference — that stays rejected (no time-series data exists to back it).

### ReportCard

File: `components/workflow/ReportCard.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`) |
| Border | `border border-border` (via `Card`) |
| Border radius | `rounded-xl` (via `Card`) |
| Text — primary | `text-base font-semibold text-text-primary` (title) |
| Text — secondary | `text-sm text-text-secondary` / `text-xs text-text-muted` (manifest details) |
| Spacing | `gap-3` (via `Card` default `p-6`) |
| Hover/focus state | none |
| Shadow | `shadow-sm` (via `Card`) |
| Accent/status usage | `StatusBadge` with `reportLifecycleTone` |

Pattern notes:
Server Component — static showcase decision means it never live-transitions between lifecycle states. `state: "Ready"` renders straight from a `ReportManifest`; the other 3 states (`Needs Input`/`Not Generated`/`Processing`) are prop-driven visual variants only, with a disabled "Download .xlsx" button in the Ready state (no real file exists to download until Phase 10's API layer).

### UploadPanel

File: `components/workflow/UploadPanel.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`), file-drop zone: `bg-surface-subtle` |
| Border | `border border-border` (via `Card`), drop zone: `border border-dashed border-border-strong`, hover: `hover:border-accent` |
| Border radius | `rounded-xl` (via `Card`), drop zone: `rounded-md` |
| Text — primary | `text-sm font-semibold text-text-primary` (label) |
| Text — secondary | `text-xs text-text-muted` / `text-xs text-text-secondary` |
| Spacing | `gap-3` (via `Card` default `p-6`) |
| Hover/focus state | drop zone: `hover:border-accent` |
| Shadow | `shadow-sm` (via `Card`) |
| Accent/status usage | "Browse" chip: `bg-accent text-text-on-accent` |

Pattern notes:
Client Component (`useState` for selected filename). Real file picker — accepts a file, shows the filename — but never parses the file and never gates page content (static showcase decision). "Sample template" is a disabled `Button` with an explanatory `title`, not wired to a real download (no generated `.xlsx` exists in the repo to link to).

### WorkflowStepper

File: `components/workflow/WorkflowStepper.tsx`
Last updated: 2026-07-09 (Phase 9.1: terminal-step color fixed)

| Property | Class |
| --- | --- |
| Background | step circle: `bg-success` / `bg-surface-muted` by state |
| Border | none |
| Border radius | `rounded-full` (step circle) |
| Text — primary | `text-sm text-text-primary` (done step label) |
| Text — secondary | `text-sm text-text-muted` (upcoming step label) |
| Spacing | `gap-2` |
| Hover/focus state | none (no interaction) |
| Shadow | none |
| Accent/status usage | done step (index ≤ `currentStep`): `bg-success text-text-on-accent`; upcoming: `bg-surface-muted text-text-secondary` |

Pattern notes:
**Server Component** — takes `steps`/`currentStep` as plain props, no client state. **Phase 9.1 fix:** every step at or before `currentStep` now renders as "done" (green) — there is no separate blue "current" state anymore. The original 3-state version (done/current/upcoming) rendered the terminal step in `bg-accent` (blue), which the visual review found reads as "still in progress," the opposite of the static-showcase intent that every page represents an already-completed run. Re-introduce a distinct "current" state only once a real, live multi-step flow exists (Phase 10+).

### DataTable

File: `components/tables/DataTable.tsx`
Last updated: 2026-07-09 (Phase 9.1: zebra striping, column wrap flag, filter-toolbar composition)

| Property | Class |
| --- | --- |
| Background | `bg-surface` (body, via `Table`), `bg-surface-muted` (header, via `Table`; also odd-row zebra stripe) |
| Border | `border border-border` (via `Table`), rows: `divide-y divide-border` |
| Border radius | `rounded-xl` (via `Table`) |
| Text — primary | `text-xs text-text-primary` (cells, via `Table`) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (headers, via `Table`) |
| Spacing | `px-3 py-2` (cells, via `Table`) |
| Hover/focus state | sortable header hover: `hover:text-text-primary` |
| Shadow | none |
| Accent/status usage | none directly — status cells render `StatusBadge`; quantity/progress cells may render `MiniBar` alongside the number |

Pattern notes:
**Always a Client Component** (`"use client"`, one file, no server-rendered fallback) — see `docs/plan/phase-9-reusable-ui-components-static-pages/plan.md` decision #2. Typed `columns`/`data` props; sort (single-column, ascending/descending, local `useState`) only activates on columns with `sortable: true`. Falls back to `EmptyState` when `data.length === 0`. Because its column config carries `render` functions, every page that uses it is *also* a Client Component (functions can't cross the Server→Client props boundary) — `order-validation`, `inventory-allocation`, and `payment-aging` pages are `"use client"` for this reason. `dashboard` and `reports` don't use `DataTable` and stay Server Components.

**Phase 9.1 additions:**
- **Zebra striping**: odd rows (`index % 2 === 1`) get `bg-surface-muted`; even rows stay the default `bg-surface`.
- **`wrap?: boolean` column flag**: every cell is `whitespace-nowrap` by default (dense, single-line rows); a column sets `wrap: true` to allow wrapping, reserved for long free text (`error_message`, `suggested_action`). Short identifier/date/badge columns never wrap.
- **Filtering stays outside DataTable** — this decision (Phase 9's original "sort only, no filtering") was revised in Phase 9.1, but the fix was adding `FilterToolbar`/`FilterSelect` as page-level composition, not teaching DataTable about filters. Pages own filter state and pass an already-filtered `data` array in; DataTable still only cares whether that array is empty. This keeps DataTable's own responsibility narrow and matches the "extend via composition, not by growing DataTable's prop surface" instruction.
- **Typography hierarchy inside cells**: identifier columns (order ID, SKU, invoice ID, customer name) render with `font-medium text-text-primary`; supporting metadata (dates, region, payment terms, warehouse) render with `text-text-secondary` or `text-text-muted`. This is applied per-column in each page's `render` function, not inside `DataTable`/`TableCell` itself, since only the page knows which field is the "identifier" for that row shape.
- **`align?: "left" | "right"` column flag**: right-aligns both the header and every cell in that column (plus `tabular-nums` at the call site) — used for every quantity/amount/count column (`requested_qty`, `allocated_qty`, `invoice_amount`, `days_overdue`, etc.). Sortable-column headers keep the sort arrow adjacent to the label even when right-aligned (`flex-row-reverse`).
- **Long-text truncation**: columns whose values can run long (`customer_name`, `product_name`, `supplier_name`, `error_message`, `suggested_action`) render with `block max-w-[Npx] truncate` plus a native `title={value}` attribute — one line, ellipsis, full value on hover/focus. This replaced an earlier Phase 9.1 pass that used the `wrap: true` column flag for `error_message`/`suggested_action`; that was superseded — those columns truncate-with-tooltip now, matching every other long-text column, and `wrap` is reserved for `DraftMessageRow.message_text`-style content that lives in a card panel, not a table cell (no current table column uses `wrap: true`).
- **Page composition: `/inventory-allocation` moved from 4 stacked tables to 1 main table + 2 compact supporting tables.** The standalone "Backorders" `DataTable` (Phase 9) was removed — it was always exactly `allocation_results` filtered to `status === "Backordered"`, so it's now just a `Status` filter option (`FilterSelect`) on the single "Allocation Results" table (Figma's "single main table with filter views" pattern). "Remaining Inventory" and "Supplier Follow-up" moved into a `grid lg:grid-cols-2` pair instead of two full-width stacked sections, signaling they're supporting context rather than peer-weight tables. No columns, fields, or statuses were added or removed from any contract in this restructuring — it's page composition only.

### FilterToolbar

File: `components/tables/FilterToolbar.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | `bg-surface` |
| Border | `border border-border` |
| Border radius | `rounded-xl` |
| Text — primary | n/a |
| Text — secondary | `text-xs` search placeholder: `placeholder:text-text-muted` |
| Spacing | `px-4 py-3`, `gap-3` |
| Hover/focus state | search/select focus: `focus:ring-1 focus:ring-accent` |
| Shadow | none |
| Accent/status usage | "Clear filters" action: `text-accent hover:text-accent-hover` |

Pattern notes:
Client Component. Composes an optional search `<input>`, any number of `FilterSelect` children, and a "Clear filters" action that only renders when `hasActiveFilters` is true. Purely client-side filtering against already-loaded mock data — never a new fetch, never introduces a business field the contracts don't already have. Added in Phase 9.1, revising Phase 9's original "sort only, no filtering" `DataTable` decision — the revision keeps filtering as page-level composition rather than growing `DataTable` itself (see `DataTable`'s Pattern notes).

### FilterSelect

File: `components/tables/FilterSelect.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | `bg-surface` |
| Border | `border border-border` |
| Border radius | `rounded-md` |
| Text — primary | `text-sm text-text-primary` (selected value) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (label) |
| Spacing | `px-2 py-1`, `gap-2` |
| Hover/focus state | `focus:ring-1 focus:ring-accent` |
| Shadow | none |
| Accent/status usage | none |

Pattern notes:
Client Component, a native `<select>` (matches `UploadPanel`'s existing preference for native controls over a custom dropdown — no shadcn `Select`, no new dependency). Options always come from a typed contract vocabulary (e.g. `["All", "High", "Normal", "Low"]`) or are derived from the loaded data itself (e.g. distinct warehouse values) — never invented. First option is conventionally `"All"`. **Phase 9.1 addendum:** every control gets a leading `lucide-react` `Filter` icon + uppercase `"FILTER"` label (`text-text-muted`) before the field label, so a row of filters reads as `[icon] FILTER  Status:` with the `<select>` itself in `font-semibold` for scannability — applied once inside `FilterSelect`, not repeated per call site.

### TableSectionHeading

File: `components/tables/TableSectionHeading.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | none (transparent, sits directly on the page) |
| Border | none |
| Border radius | none |
| Text — primary | `text-base font-semibold text-text-primary` (title, matches the pre-existing "Section title" typography token) |
| Text — secondary | `text-xs text-text-muted` (one-line caption) |
| Spacing | `gap-2` (icon-to-title), `mt-1` (title-to-caption) |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | icon renders in `text-text-secondary`, never a status color — it's a category icon (what kind of table this is), not a status indicator |

Pattern notes:
Server Component. Replaces the bare `<h2>` pattern above every table/panel section with `icon + title` plus an optional one-line business-readable caption showing the data relationship (e.g. *"Requested qty → allocated qty → backorder qty."*). Icon choice must clarify the table's purpose, not decorate randomly — see each page's call site for the specific `lucide-react` icon chosen (`AlertTriangle` for Validation Errors, `PackageCheck` for Allocation Results, `Warehouse` for Remaining Inventory, `Truck` for Supplier Follow-up, `ReceiptText` for Payment Aging, `Mail` for Draft Messages, etc.). Captions are short by design — this is not a place for instructional copy.

### SegmentedBar

File: `components/tables/SegmentedBar.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | track: `bg-surface-muted` |
| Border | none |
| Border radius | `rounded-full` (bar), `rounded-full` (legend dots) |
| Text — primary | `text-text-primary` (legend counts, `font-medium`) |
| Text — secondary | `text-xs text-text-secondary` (legend labels) |
| Spacing | `h-2` (bar), `gap-2`/`gap-x-4 gap-y-1` (legend) |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | one `bg-{tone}` fill segment per category, proportional width by share of total; legend dot repeats the same tone |

Pattern notes:
Server Component. Multi-category share-of-total bar — used on `/dashboard` for "Valid vs Invalid" (Order Validation) and "Fully Allocated / Partially Allocated / Backordered" (Inventory Allocation). Always paired with a legend row showing the real counts (`Valid: 9`), never a bare bar with no numeric label. No charting library. Distinct from `MiniBar` (single value vs. a max, used inside table cells) and `AgingBucketBars` (a 5-row bar *list*, one bar per aging bucket) — three different shapes for three different data shapes, all built on the same "token-styled div, numbers always visible" idea.

### AgingBucketBars

File: `components/tables/AgingBucketBars.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | track: `bg-surface-muted` |
| Border | none |
| Border radius | `rounded-full` |
| Text — primary | n/a |
| Text — secondary | `text-xs text-text-secondary` (bucket label + count) |
| Spacing | `h-2`, `gap-2`/`gap-3` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | `bg-accent` fill for every bucket (this is a single-series breakdown, not a multi-tone comparison like `SegmentedBar`) |

Pattern notes:
Server Component. Extracted in Phase 9.1 from a page-local function in `payment-aging/page.tsx` into a shared component so `/dashboard`'s Payment Aging summary and `/payment-aging` itself render the exact same visualization from `PaymentAgingSummary.aging_bucket_counts` — no duplicated implementation to drift out of sync.

### MiniBar

File: `components/tables/MiniBar.tsx`
Last updated: 2026-07-09 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | track: `bg-surface-muted`; fill: `bg-{tone}` (solid, not `-subtle`) |
| Border | none |
| Border radius | `rounded-full` |
| Text — primary | n/a — always rendered next to the real numeric value, never a replacement for it |
| Text — secondary | n/a |
| Spacing | `h-1.5 w-14` |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | `tone` prop (`success`/`warning`/`danger`/`info`/`neutral`) picks the fill color, same `Tone` type as `StatusBadge`/`MetricCard` |

Pattern notes:
Server Component (no interactivity). Compact quantity/progress indicator for table cells — used for `allocated_qty` vs `requested_qty`, `backorder_qty` vs `requested_qty` (danger tone, only rendered when `backorder_qty > 0`), and `remaining_qty` vs `reorder_point` in the Inventory Allocation table. Always composed as `<div className="flex items-center gap-2"><MiniBar .../><span>{value}</span></div>` — the instruction that introduced this component was explicit that bars must be supplemental, never hide the numeric value. No charting library — a plain token-styled div, same family as `ReportCard`'s and `DraftMessages`' existing div-based visuals.

## Charts (`components/charts/`)

A separate top-level folder from `components/tables/` — these render whole-chart visualizations, not table-adjacent data viz (`MiniBar`/`SegmentedBar`/`AgingBucketBars` stay in `components/tables/`; they're small in-cell/in-row indicators, a different taxonomy tier). Both charts below are Server Components, pure CSS/SVG, **no charting library** — that stays deferred.

### DonutBreakdownChart

File: `components/charts/DonutBreakdownChart.tsx`
Last updated: 2026-07-10 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | ring track: none (segments are drawn directly, no separate track circle unless `total === 0`) |
| Border | none |
| Border radius | `rounded-full` (legend dots) |
| Text — primary | `text-xl font-semibold text-text-primary` (center total) |
| Text — secondary | `text-[10px] uppercase tracking-wide text-text-muted` (center label); `text-xs text-text-secondary` (legend labels) |
| Spacing | `h-32 w-32` (ring), `gap-6` (ring-to-legend), `gap-1.5` (legend rows) |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | one `stroke-{tone}` ring segment per category (literal `Record<Tone, string>` map, never interpolated), matching legend dot in `bg-{tone}` |

Pattern notes:
Pure-SVG donut (stacked `<circle>` strokes, `stroke-dasharray`/`stroke-dashoffset`, `viewBox="0 0 100 100"`, `-rotate-90` so the first segment starts at 12 o'clock). `tone` per segment is **never decided inside this component** — callers resolve it via the existing `allocationStatusTone`/`agingBucketTone` helpers from `StatusBadge.tsx` before passing it as a prop, so a chart segment and a table badge for the same status can never show different colors (only the `Tone` *type* is imported here, not the helper functions — no runtime coupling to the `StatusBadge` component). **Zero guard:** if every segment's value is 0, renders one full-circumference neutral ring (`stroke-border-strong`) with center text `"0"` instead of computing `0/0`. Used once today: `/dashboard`'s "Allocation Status" card (Fully Allocated / Partially Allocated / Backordered).

### VerticalBucketBarChart

File: `components/charts/VerticalBucketBarChart.tsx`
Last updated: 2026-07-10 (Phase 9.1)

| Property | Class |
| --- | --- |
| Background | bars: `bg-{tone}`; guide lines: `border-t border-border` |
| Border | none |
| Border radius | `rounded-t-md` (bar tops only) |
| Text — primary | n/a |
| Text — secondary | `text-xs text-text-muted` (subtitle), `text-[10px]` (value-above-bar and bucket-label-below-bar) |
| Spacing | `h-32` (chart area), `gap-3` (columns) |
| Hover/focus state | none |
| Shadow | none |
| Accent/status usage | one `bg-{tone}` bar per bucket (literal `Record<Tone, string>` map), tone resolved by the caller via `agingBucketTone`, same reuse rule as `DonutBreakdownChart` |

Pattern notes:
Plain CSS bar chart — `div` columns, height as a `%` of a fixed `h-32` container, 3 absolute-positioned `border-t border-border` guide lines at 25/50/75%. The formatted value always renders above the bar, never bar-only. **Zero guard:** if every value is 0, renders `EmptyState` (`"No outstanding amounts to show."`) instead of a row of degenerate flat bars. Subtitle text is deliberately neutral (`"Outstanding amount by bucket"`, no `$` or "Total Outstanding" framing) since no contract field carries a currency code (Field Scope Boundary, Phase 5). Used once today: `/dashboard`'s "Outstanding by Aging Bucket" card, sourced from the new `amountByAgingBucket()` helper in `lib/mock-data.ts` (see `context/ui-contract-plan.md`'s Derived Display-Only Aggregates table) — distinct from `PaymentAgingSummary.aging_bucket_counts`, which is a *count*, not an amount.

## Page composition notes (Phase 9.1)

**`/dashboard` gained 4 new sections, still a Server Component.** "Inventory Shortage Alerts" (from `supplier_follow_ups`, plus the "Gap to Reorder Point" derived value — see `context/ui-contract-plan.md`'s Derived Display-Only Aggregates table) and "Payment Follow-up Items" (from `aging_rows` filtered to `follow_up_priority !== "None"`) render as **plain, non-sortable tables** using the `Table`/`TableHead`/`TableBody`/`TableRow`/`TableHeaderCell`/`TableCell` primitives directly — deliberately **not** `DataTable`, specifically so `/dashboard` doesn't inherit the "any page using `DataTable`'s column config must be a Client Component" constraint documented above. Dashboard summary tables don't need sorting; staying server-rendered is the better tradeoff here. A "How the Workflows Connect" section (compact icon-chip + `ArrowRight` flow rows, 4 rows matching the 4 real data flows: Orders→Validation→Valid Orders, Valid Orders+Inventory→Allocation→Backorders/Supplier Follow-up, Invoices→Aging→Draft Reminders, Outputs→Reports) and a "How This Demo Works" guide section (English only — bilingual deferred, see Open Questions in the Phase 9.1 session docs) round out the page. Both are explanatory-only: no new data, no fake metrics, no trend/history.

**Supersedes the above for 2 of the 3 KPI-strip visuals:** `/dashboard`'s Inventory Allocation and Payment Aging sections no longer render `SegmentedBar`/`AgingBucketBars` inline — those calls were removed. In their place, a new section (`grid gap-4 lg:grid-cols-2`, directly after the 3 KPI strips) holds a `DonutBreakdownChart` (Allocation Status) and a `VerticalBucketBarChart` (Outstanding by Aging Bucket) side by side — see the Charts section above. Order Validation's `SegmentedBar` (Valid vs Invalid) is untouched and still renders inline in that KPI-strip section; it was never in scope for the chart-alignment addendum.

**Section spacing tightened from `mt-8` to `mt-6` between major sections, page-wide.** Applies to every `<section>` on all 5 routes. `mt-3` (heading → content) and `mt-1`/`mt-2` (title → caption) were already tight and are unchanged.

**Secondary/supporting sections get a `rounded-xl border border-border bg-surface-subtle p-4` wrapper** to visually separate them from primary sections (KPI strips, main tables) now that spacing between all sections is tighter. Applied to: Inventory Allocation's "Remaining Inventory" and "Supplier Follow-up" (the `grid lg:grid-cols-2` pair), Payment Aging's "Data Issues", and both new Dashboard sections ("Inventory Shortage Alerts", "Payment Follow-up Items"). Primary sections (KPI strips, the main "Allocation Results"/"Payment Aging"/"Validation Errors"/"Valid Orders" tables) stay on the plain page background — no wrapper. This is the only background-tone distinction in use; do not introduce a third tier without updating this note.
