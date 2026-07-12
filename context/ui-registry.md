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
| `Button` | `components/ui/Button.tsx` | `rounded-md px-4 py-2 text-sm font-medium`; primary: `bg-accent text-text-on-accent hover:bg-accent-hover`; secondary: `border border-border bg-surface text-text-primary hover:bg-surface-muted`; **Phase 10.2** dark: `bg-surface-inverse text-text-on-inverse hover:bg-surface-inverse-hover disabled:bg-surface-muted disabled:text-text-muted` — the disabled override is deliberate: the base `disabled:opacity-50` (shared by all variants) reads as clearly inert on the light `secondary` variant, but a dimmed solid-navy fill could still look "present"/clickable at 50% opacity, so `dark` falls back to a neutral light-gray disabled look instead. Scoped to exactly two usages — `UploadPanel`'s Sample file link and each workflow page's "Download Report" button — never the primary Run action or "Run sample data". Phase 10: `buttonVariants` (the underlying `cva`) is now exported, so a styled-but-non-`<button>` element (e.g. an `<a>` acting as a button) can apply the identical classes without duplicating them — used by `UploadPanel`'s Sample File link and `ReportCard`'s "Go to workflow" link (the latter stays `secondary`, not `dark` — Phase 10.2 didn't touch it). |
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
Last updated: 2026-07-12 (Phase 10.2)

| Property | Class |
| --- | --- |
| Background | `bg-surface-inverse` (dark navy — Phase 10.2 Inverse Surface tokens, see `ui-tokens.md`) |
| Border | none (the navy/off-white boundary is its own separation; the old `border-r border-border` was dropped as redundant against the dark fill) |
| Border radius | none (full-height panel) |
| Text — primary | active link: solid `bg-accent text-text-on-accent` (changed from a subtle light-tint in Phase 9, which had poor contrast against the new dark background) |
| Text — secondary | inactive link: `text-text-on-inverse-muted`, hover `text-text-on-inverse` |
| Spacing | `w-60 p-4`, links `gap-1`, each link `flex items-center gap-2` for its icon |
| Hover/focus state | inactive link hover: `hover:bg-surface-inverse-hover hover:text-text-on-inverse` |
| Shadow | none |
| Accent/status usage | active route: solid `bg-accent text-text-on-accent` (reuses the same accent as `Button`'s `primary` variant, not a separate "selected-on-dark" token) |

Pattern notes:
Client Component (`usePathname()` for active-route highlighting via exact match). Fixed 5-item nav — do not add ERP-style extra destinations; the route set is closed per `architecture.md`. Phase 10.2 added a `lucide-react` icon per nav item (`LayoutDashboard`, `ClipboardList`, `PackageCheck`, `Clock`, `FileSpreadsheet`) rendered before the label — decorative only, reusing icons already established elsewhere in the app for the same concepts (e.g. `Clock` for Payment Aging matches its `FlowRow` icon on `/dashboard`). Known limitation, out of scope for Phase 10.2: the sidebar has no responsive collapse/drawer behavior — it stays a fixed `w-60` on every viewport, which squeezes the main content column on narrow mobile widths. This predates Phase 10.2 (only the color/icons changed here, not the width or breakpoints) and would need its own planning decision.

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
Server Component. **Phase 10:** now has real call sites — all 3 workflow pages render it while `status === "submitting"` (a live `postJSON` request in flight), with a workflow-specific `label` (e.g. "Validating orders…", "Allocating inventory by priority, delivery date, and stock availability…").

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
Server Component. Always render business-readable copy here, never a raw exception — see `ui-rules.md`'s Error Messages bad/good example. **Phase 10:** now has real call sites — all 3 workflow pages render it when `status === "failed"` with the API's `{"detail": "..."}` message (via `ApiError`), and again in a smaller inline form next to the "Download Report" button when the separate report request fails. Never a raw exception in either spot — confirmed live: a deliberately malformed upload renders exactly the backend's business-readable `detail` string, not a stack trace.

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
Last updated: 2026-07-12 (Phase 10.2: restructured into a compact tile)

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`); icon chip: `bg-{tone}-subtle` |
| Border | `border border-border` (via `Card`) |
| Border radius | `rounded-xl` (via `Card`); icon chip: `rounded` |
| Text — primary | `text-2xl font-semibold text-text-primary` (value) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (label) |
| Spacing | `min-h-[104px] flex-col items-center justify-center gap-2 p-4`, centered/stacked: icon chip → value → label |
| Hover/focus state | `transition-shadow hover:border-border-strong hover:shadow-md` (Phase 10.2) |
| Shadow | `shadow-sm` (via `Card`), `hover:shadow-md` on hover |
| Accent/status usage | optional `icon`/`tone` props render a `w-7 h-7 rounded` chip (`bg-{tone}-subtle`, icon `text-{tone}`) above the value — `success`/`warning`/`danger`/`info`/`neutral`, same `Tone` type `StatusBadge` exports |

Pattern notes:
Server Component. Same `label`/`value`/`icon`/`tone` prop contract as Phase 9.1 — only the internal layout changed, so every existing call site (~15, across `/dashboard`'s Overview row and all 3 workflow pages' post-run summary grids) kept working with no edits. **Phase 10.2:** restructured from a short wide strip (label+icon row, value below, left-aligned) into a compact, roughly square, centered tile (icon chip → big value → label, all centered, `min-h-[104px]`) to read as a "dashboard tile" rather than a KPI strip, matching the reference dashboard's tile proportions. Added a subtle hover lift (`hover:border-border-strong hover:shadow-md`) matching the chart-card hover treatment below. Deliberately **not** adopted: the trend-delta (`+12.4%` arrow) from the same reference — still rejected, no time-series data exists to back it.

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
Server Component — still never live-transitions between lifecycle states; that decision holds even in Phase 10, because `ReportCard` is only used on the two pages that deliberately stayed static (`/dashboard`, `/reports` — see Page composition notes below). `state: "Ready"` renders straight from a `ReportManifest`. **Phase 10:** added an optional `workflowHref` prop on the `Ready` variant — when provided, the Ready branch renders a `Link` (styled via `buttonVariants`) reading "Go to workflow" instead of the disabled "Download .xlsx" `Button`; when omitted (still `/dashboard`'s usage, unchanged), the disabled button remains, now with copy that reads "Sample manifest only — no live download from this card" rather than the old "becomes available once Phase 10 is live" (now false, since Phase 10 is live — just not through this card). Live report downloads never go through `ReportCard`; see Page composition notes.

### UploadPanel

File: `components/workflow/UploadPanel.tsx`
Last updated: 2026-07-12 (Phase 10.2: bottom-anchored drop zone, dark Sample file button)

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`), file-drop zone: `bg-surface-subtle` |
| Border | `border border-border` (via `Card`), drop zone: `border border-dashed border-border-strong`, hover: `hover:border-accent` |
| Border radius | `rounded-xl` (via `Card`), drop zone: `rounded-md` |
| Text — primary | `text-sm font-semibold text-text-primary` (label) |
| Text — secondary | `text-xs text-text-muted` / `text-xs text-text-secondary` |
| Spacing | `Card` gets `h-full`; drop zone + Sample file row wrapped in `mt-auto flex flex-col gap-3` so they anchor to the bottom of the card |
| Hover/focus state | drop zone: `hover:border-accent` |
| Shadow | `shadow-sm` (via `Card`) |
| Accent/status usage | "Browse" chip: `bg-accent text-text-on-accent`; "Sample file" link: `buttonVariants({ variant: "dark" })` |

Pattern notes:
Client Component (`useState` for selected filename). Real file picker — accepts a file, shows the filename, never parses it itself (parsing stays a `backend/` concern). Gained two Phase 10 props — `onFileChange?: (file: File | null) => void` and `sampleFileName?: string` (an allowlisted `backend/routers/templates.py` key), rendering a real `<a href download>` "Sample file" link via `buttonVariants` only when `sampleFileName` is provided. **Phase 10.2 fix:** when several `UploadPanel`s sit side by side in a grid (e.g. Inventory Allocation's 3 panels), each panel's "Required columns" text wraps to a different number of lines, which previously left the drop-zone rows at inconsistent heights across the row — not a same-row alignment bug (that row was already `flex items-center justify-between`), but a bottom-anchoring one. Fixed by giving `Card` `h-full` (so it stretches to match the tallest sibling in its grid row) and wrapping the drop-zone `<label>` + Sample-file `<div>` in `mt-auto flex flex-col gap-3`, pinning them to the bottom regardless of the required-columns text length above. Also switched the "Sample file" link from `secondary` to the new Phase 10.2 `dark` `Button` variant (same inverse-surface tokens as `SidebarNav`), and added `min-w-0` to the caption span + `shrink-0 whitespace-nowrap` to the link — without these, a long caption in a narrow (3-column) card could squeeze the link's width enough that "Sample file" wrapped onto two lines and the button rendered oversized; now the caption wraps/truncates instead and the button always stays single-line at its normal compact size.

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
**Server Component** — takes `steps`/`currentStep` as plain props, no client state. **Phase 9.1 fix:** every step at or before `currentStep` now renders as "done" (green) — there is no separate blue "current" state anymore. The original 3-state version (done/current/upcoming) rendered the terminal step in `bg-accent` (blue), which the visual review found reads as "still in progress," the opposite of the static-showcase intent that every page represents an already-completed run. **Phase 10:** `currentStep` is now driven by real client state on all 3 workflow pages (0 = no files selected, 1 = files selected but not yet run, 2 = `status === "succeeded"`) instead of being hardcoded to the last step — the component itself is unchanged, still just done/upcoming with no distinct "current" visual, which continues to read correctly now that "done" genuinely means "this step happened."

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
Last updated: 2026-07-12 (Phase 10.2: optional `action` slot)

| Property | Class |
| --- | --- |
| Background | none (transparent, sits directly on the page) |
| Border | none |
| Border radius | none |
| Text — primary | `text-base font-semibold text-text-primary` (title, matches the pre-existing "Section title" typography token) |
| Text — secondary | `text-xs text-text-muted` (one-line caption) |
| Spacing | `flex items-start justify-between gap-3` (title block vs. optional action); `gap-2` (icon-to-title), `mt-1` (title-to-caption) |
| Hover/focus state | none (the `action` slot's own element, e.g. a `Link`, carries its own hover state) |
| Shadow | none |
| Accent/status usage | icon renders in `text-text-secondary`, never a status color — it's a category icon (what kind of table this is), not a status indicator |

Pattern notes:
Server Component. Replaces the bare `<h2>` pattern above every table/panel section with `icon + title` plus an optional one-line business-readable caption showing the data relationship (e.g. *"Requested qty → allocated qty → backorder qty."*). Icon choice must clarify the table's purpose, not decorate randomly — see each page's call site for the specific `lucide-react` icon chosen (`AlertTriangle` for Validation Errors, `PackageCheck` for Allocation Results, `Warehouse` for Remaining Inventory, `Truck` for Supplier Follow-up, `ReceiptText` for Payment Aging, `Mail` for Draft Messages, etc.). Captions are short by design — this is not a place for instructional copy. **Phase 10.2:** added an optional `action?: ReactNode` prop, rendered top-right of the title/caption block (`shrink-0 pt-0.5`) — a compact text link only, never a large CTA (e.g. `/dashboard`'s two chart cards pass a small `text-xs font-medium text-accent` `Link` reading "View all"/"AR report", pointing at the workflow page that owns that data). Every other call site omits `action` and renders exactly as before — this is additive, not a breaking change.

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
Last updated: 2026-07-12 (Phase 10.2: hover/focus tooltip + right-aligned legend)

| Property | Class |
| --- | --- |
| Background | ring track: none (segments are drawn directly, no separate track circle unless `total === 0`); floating tooltip: `bg-surface` |
| Border | none; floating tooltip: `border border-border` |
| Border radius | `rounded-full` (legend dots); floating tooltip: `rounded-lg`; legend-row hover: `rounded` |
| Text — primary | `text-xl font-semibold text-text-primary` (center total); tooltip label: `text-sm font-semibold text-text-primary` |
| Text — secondary | `text-[10px] uppercase tracking-wide text-text-muted` (center label); `text-xs text-text-secondary` (legend labels); legend count: `font-semibold tabular-nums text-text-primary` right-aligned |
| Spacing | `h-32 w-32` (ring), `gap-6` (ring-to-legend), `gap-2` (legend rows, each `flex items-center justify-between`) |
| Hover/focus state | ring segment: `hover:opacity-70 focus:opacity-70` (each `<circle>` is `tabIndex={0}` + `role="img"`); legend row: `hover:`/focus-driven `bg-surface-muted` highlight, both share one `hoveredLabel` state |
| Shadow | floating tooltip: `shadow-md` |
| Accent/status usage | one `stroke-{tone}` ring segment per category (literal `Record<Tone, string>` map, never interpolated), matching legend dot in `bg-{tone}` |

Pattern notes:
Pure-SVG donut (stacked `<circle>` strokes, `stroke-dasharray`/`stroke-dashoffset`, `viewBox="0 0 100 100"`, `-rotate-90` so the first segment starts at 12 o'clock). `tone` per segment is **never decided inside this component** — callers resolve it via the existing `allocationStatusTone`/`agingBucketTone` helpers from `StatusBadge.tsx` before passing it as a prop, so a chart segment and a table badge for the same status can never show different colors. **Zero guard:** if every segment's value is 0, renders one full-circumference neutral ring (`stroke-border-strong`) with center text `"0"` instead of computing `0/0`. Used once today: `/dashboard`'s "Allocation Status" card. **Phase 10.2:** promoted to a Client Component (`"use client"` + local `useState<string | null>` for `hoveredLabel`) to support data-bearing hover/focus — hovering *or* keyboard-focusing a ring segment (or its matching legend row; both drive the same state) shows a floating tooltip card (`label`, count, `%` of total) anchored at the donut's bottom-left, overlapping the ring like the reference dashboard, without replacing the always-visible center total. Each `<circle>` also carries a native SVG `<title>` (built from one single-expression string, not multi-line JSX children — a multi-line `<title>{a}: {b} ({c}%)</title>` produced a real hydration mismatch, since server/client whitespace inside `<title>` didn't match bit-for-bit) and an `aria-label`, so the same info is available without JS/mouse. The center total overlay is `pointer-events-none` — without that, it sat on top of the entire ring (not just the hole) and silently ate every hover/focus event meant for the segments beneath it. Legend rows now show count **right-aligned** (`justify-between`, not the old inline `label: value` string) with `%` appended only while that row (or its ring segment) is hovered/focused.

### VerticalBucketBarChart

File: `components/charts/VerticalBucketBarChart.tsx`
Last updated: 2026-07-12 (Phase 10.2: per-bar hover/focus tooltip)

| Property | Class |
| --- | --- |
| Background | bars: `bg-{tone}`; guide lines: `border-t border-border`; tooltip: `bg-surface` |
| Border | none; tooltip: `border border-border` |
| Border radius | `rounded-t-md` (bar tops only); tooltip: `rounded-md` |
| Text — primary | n/a |
| Text — secondary | `text-xs text-text-muted` (subtitle), `text-[10px]` (value-above-bar, bucket-label-below-bar, and tooltip text) |
| Spacing | `h-32` (chart area), `gap-3` (columns) |
| Hover/focus state | each bar column: `group`, `tabIndex={0}`; bar fill: `group-hover:opacity-70 group-focus:opacity-70`; tooltip: `opacity-0` → `group-hover:opacity-100 group-focus:opacity-100` |
| Shadow | tooltip: `shadow-md` |
| Accent/status usage | one `bg-{tone}` bar per bucket (literal `Record<Tone, string>` map), tone resolved by the caller via `agingBucketTone`, same reuse rule as `DonutBreakdownChart` |

Pattern notes:
Plain CSS bar chart — `div` columns, height as a `%` of a fixed `h-32` container, 3 absolute-positioned `border-t border-border` guide lines at 25/50/75%. The formatted value always renders above the bar, never bar-only. **Zero guard:** if every value is 0, renders `EmptyState` instead of a row of degenerate flat bars. Subtitle text is deliberately neutral, no `$`/"Total Outstanding" framing, since no contract field carries a currency code (Field Scope Boundary, Phase 5). Used once today: `/dashboard`'s "Outstanding by Aging Bucket" card, sourced from `amountByAgingBucket()` in `lib/mock-data.ts`. **Phase 10.2:** stayed a Server Component — no local state needed, since each bar's tooltip is an independent pure-CSS `group-hover`/`group-focus` reveal (no cross-element coordination like the donut's shared hover state). Each bar column is `tabIndex={0}` with an `aria-label` (label, formatted amount, `%` of total across all buckets) and a `role="tooltip"` div positioned `absolute -top-2 -translate-y-full` above the column (not the bar itself, so it lands at a consistent height regardless of that bar's own height) showing the same three facts on hover or keyboard focus.

## Page composition notes (Phase 9.1)

**`/dashboard` gained 4 new sections, still a Server Component.** "Inventory Shortage Alerts" (from `supplier_follow_ups`, plus the "Gap to Reorder Point" derived value — see `context/ui-contract-plan.md`'s Derived Display-Only Aggregates table) and "Payment Follow-up Items" (from `aging_rows` filtered to `follow_up_priority !== "None"`) render as **plain, non-sortable tables** using the `Table`/`TableHead`/`TableBody`/`TableRow`/`TableHeaderCell`/`TableCell` primitives directly — deliberately **not** `DataTable`, specifically so `/dashboard` doesn't inherit the "any page using `DataTable`'s column config must be a Client Component" constraint documented above. Dashboard summary tables don't need sorting; staying server-rendered is the better tradeoff here. A "How the Workflows Connect" section (compact icon-chip + `ArrowRight` flow rows, 4 rows matching the 4 real data flows: Orders→Validation→Valid Orders, Valid Orders+Inventory→Allocation→Backorders/Supplier Follow-up, Invoices→Aging→Draft Reminders, Outputs→Reports) and a "How This Demo Works" guide section (English only — bilingual deferred, see Open Questions in the Phase 9.1 session docs) round out the page. Both are explanatory-only: no new data, no fake metrics, no trend/history.

**Supersedes the above for 2 of the 3 KPI-strip visuals:** `/dashboard`'s Inventory Allocation and Payment Aging sections no longer render `SegmentedBar`/`AgingBucketBars` inline — those calls were removed. In their place, a new section (`grid gap-4 lg:grid-cols-2`, directly after the 3 KPI strips) holds a `DonutBreakdownChart` (Allocation Status) and a `VerticalBucketBarChart` (Outstanding by Aging Bucket) side by side — see the Charts section above. Order Validation's `SegmentedBar` (Valid vs Invalid) is untouched and still renders inline in that KPI-strip section; it was never in scope for the chart-alignment addendum.

**Section spacing tightened from `mt-8` to `mt-6` between major sections, page-wide.** Applies to every `<section>` on all 5 routes. `mt-3` (heading → content) and `mt-1`/`mt-2` (title → caption) were already tight and are unchanged.

**Secondary/supporting sections get a `rounded-xl border border-border bg-surface-subtle p-4` wrapper** to visually separate them from primary sections (KPI strips, main tables) now that spacing between all sections is tighter. Applied to: Inventory Allocation's "Remaining Inventory" and "Supplier Follow-up" (the `grid lg:grid-cols-2` pair), Payment Aging's "Data Issues", and both new Dashboard sections ("Inventory Shortage Alerts", "Payment Follow-up Items"). Primary sections (KPI strips, the main "Allocation Results"/"Payment Aging"/"Validation Errors"/"Valid Orders" tables) stay on the plain page background — no wrapper. This is the only background-tone distinction in use; do not introduce a third tier without updating this note.

## Page composition notes (Phase 10)

**The 3 workflow pages (`/order-validation`, `/inventory-allocation`, `/payment-aging`) are now genuinely live**, driven by page-local React state, not `lib/mock-data.ts` imports. Each page owns: `RequestStatus` (`"idle" | "submitting" | "succeeded" | "failed"`), `currentResult` (the typed Workflow Result, or `null`), `errorDetail` (the API's `{detail}` string on failure), and a separate `ReportRequestState` (`"idle" | "processing" | "failed"`) for the "Download Report" button, which is an independent request/response cycle from the main "Run" action (per `docs/adr/0006` — reports recompute from source, they don't reuse `currentResult`). This state lives in each page directly, not in a shared hook — see `docs/architect/phase-10-fastapi-integration/decisions.md` #4 for why. `lib/api-client.ts` is the one shared piece: low-level `postJSON`/`postReport`/`downloadBlob`/`fetchSampleFile` mechanics, reused identically by all 3 pages.

**Explicit "Run" action, not upload-triggers-computation.** Each page has a primary button ("Run Validation" / "Run Allocation" / "Calculate Aging") that only enables once every required file (and, for Payment Aging, a non-empty as-of date) is selected. Selecting a file alone never triggers a request.

**"Run sample data" is a second, secondary-styled button next to the primary "Run" action** — added mid-session, after the original Phase 10 plan. It fetches the page's required sample file(s) via `fetchSampleFile()` (which wraps `GET /api/templates/{name}`'s response blob into a real `File` object), sets them into the same file state the manual `UploadPanel`s use, shows a small `text-xs text-text-muted` status line ("Using sample data: sample_orders.xlsx, sample_product_master.xlsx"), and then runs the exact same request path as a manual upload — no separate backend endpoint, no shortcut around validation. Distinct from `UploadPanel`'s own "Sample File" link, which only downloads the workbook.

**`ReportLifecycleState`/`ReportCard` and `ReportRequestState`/live download buttons are two unrelated systems that happen to share visual language.** `ReportCard` (with its 4-state lifecycle) only ever appears on `/dashboard` and `/reports`, both of which stayed static — it has no live call site. The 3 workflow pages' "Download Report" buttons are plain `Button`s with their own `ReportRequestState`, never `ReportCard`. Do not attempt to unify these two into one component; the underlying data they represent (a static mock manifest vs. a live binary download that either succeeded or didn't) isn't the same shape.

**`/reports` reframed, not rebuilt.** Still a Server Component reading `reportManifests` from static mock JSON, same as Phase 9 — only the heading ("Sample Report Overview"), intro copy, and each `ReportCard`'s action (now `workflowHref` pointing at the matching workflow page instead of a disabled download button) changed. `/dashboard` is completely unchanged from Phase 9.1.

**Payment Aging's date input is now a real, enabled, required `<input type="date">`**, defaulting to the browser's current date via `new Date().toISOString().slice(0, 10)` and updating `asOfDate` state directly on change — no more `disabled`/`readOnly`, no more prefilling from a mock `ReportManifest.generated_at`.

## Page composition notes (Phase 10.2)

**`/dashboard`'s three per-workflow KPI groups (Order Validation / Inventory Allocation / Payment Aging, ~15 tiles total + a `SegmentedBar`) were consolidated into one unified "Overview" row of 5 `MetricCard`s** (`grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5`): Total Orders, Invalid Orders, Fully Allocated, Backordered, Overdue Amount — 4 counts + 1 amount, mirroring the reference dashboard's own mix. This was a deliberate, user-directed content reduction (not just a restyle): dropped KPIs (Duplicate Orders, Invalid SKUs, Missing Fields, Total Order Lines, Partially Allocated, Low Stock SKUs, Total Outstanding, High Priority Count, 90+ Days Amount) remain available on each workflow page's own post-run summary grid — `/dashboard` is an executive overview, not a mirror of every summary metric. The `SegmentedBar` (Valid/Invalid) was dropped, not relocated — its information is already conveyed by the Total Orders/Invalid Orders cards, and the reference's "main insight row" only specified two charts, not a third. **Do not silently re-add dropped KPIs to `/dashboard`** without the same explicit user direction this consolidation had.

**Workflow pages' post-run summary grids intentionally do NOT follow the dashboard's 4-column cap.** `/order-validation` (6 KPIs) uses `lg:grid-cols-6`, `/inventory-allocation` (5 KPIs) uses `lg:grid-cols-5`, `/payment-aging` (4 KPIs) uses `lg:grid-cols-4` — each fits its own card count in a single row on desktop, a direct user correction to an earlier draft that capped all KPI grids (dashboard and workflow pages alike) at 4 columns. Only `/dashboard`'s 5-card Overview row is deliberately capped/single-row by card count; the three workflow pages should keep matching their own count if a KPI is ever added/removed from a workflow's summary.

**Chart-card sizing fix (`/dashboard`'s Allocation Status + Outstanding by Aging Bucket cards):** both charts' body wrapper (the `<div className="mt-3">` between `TableSectionHeading` and the chart) is `flex min-h-48 flex-col justify-center` — a stable, identical minimum height with vertically centered content, replacing plain `<div className="mt-3">` which let CSS Grid's default row-stretch (the two `Card`s sit in one `grid lg:grid-cols-2` row) pull one card to match whatever height the other's content happened to need, leaving a large blank area under the shorter chart. Both cards also gained `transition-shadow hover:border-border-strong hover:shadow-md`, matching `MetricCard`'s hover treatment.

**Chart-card headers gained a compact top-right action link** via `TableSectionHeading`'s new `action` prop (see above) — "View all" → `/inventory-allocation`, "AR report" → `/payment-aging`. Non-functional beyond navigation (no live cross-page state), but points at a real page with real data, not a dead end.

**`SidebarNav` gained a `lucide-react` icon per nav item** (see `SidebarNav`'s registry entry above) — purely decorative, reusing icons already established elsewhere in the app for the same concept.

**Known pre-existing limitation, out of scope this phase:** the sidebar has no responsive collapse/drawer — it's a fixed `w-60` on every viewport, so narrow mobile widths get a squeezed main-content column. This predates Phase 10.2 (only `SidebarNav`'s color/icons changed, not `AppShell`'s layout or breakpoints) and would need its own planning pass, not a silent fix folded into a token-polish phase.
