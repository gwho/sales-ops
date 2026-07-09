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
| `Badge` | `components/ui/Badge.tsx` | `rounded-full px-3 py-1 text-xs font-medium`; tone maps to `bg-{success,warning,danger,info}-subtle text-{success,warning,danger,info}` or `bg-surface-muted text-text-secondary` for neutral |
| `Table` (+ `TableHead`/`TableBody`/`TableRow`/`TableHeaderCell`/`TableCell`) | `components/ui/Table.tsx` | Wrapper: `rounded-xl border border-border overflow-hidden`; header cells: `text-xs font-medium uppercase tracking-wide text-text-secondary` |

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
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` (via `Card`) |
| Border | `border border-border` (via `Card`) |
| Border radius | `rounded-xl` (via `Card`) |
| Text — primary | `text-2xl font-semibold text-text-primary` (value) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (label) |
| Spacing | `p-4` (compact card override, not `Card`'s default `p-6`), `gap-1` |
| Hover/focus state | none |
| Shadow | `shadow-sm` (via `Card`) |
| Accent/status usage | none |

Pattern notes:
Server Component. `p-4` overrides `Card`'s default `p-6` — KPI tiles are "compact cards" per `ui-tokens.md`'s spacing table, not "primary dashboard cards".

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
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | step circle: `bg-success` / `bg-accent` / `bg-surface-muted` by state |
| Border | none |
| Border radius | `rounded-full` (step circle) |
| Text — primary | `text-sm text-text-primary` (done/current step label) |
| Text — secondary | `text-sm text-text-muted` (upcoming step label) |
| Spacing | `gap-2` |
| Hover/focus state | none (no interaction) |
| Shadow | none |
| Accent/status usage | current step: `bg-accent text-text-on-accent`; done step: `bg-success text-text-on-accent` |

Pattern notes:
**Server Component** — takes `steps`/`currentStep` as plain props, no client state. Every Phase 9 page calls it with `currentStep={steps.length - 1}` (always shows the final/"Review Results" step as current), matching the static-showcase decision that nothing live-transitions. Re-evaluate as Client once a real multi-step live flow exists.

### DataTable

File: `components/tables/DataTable.tsx`
Last updated: 2026-07-09

| Property | Class |
| --- | --- |
| Background | `bg-surface` (body, via `Table`), `bg-surface-muted` (header, via `Table`) |
| Border | `border border-border` (via `Table`), rows: `divide-y divide-border` |
| Border radius | `rounded-xl` (via `Table`) |
| Text — primary | `text-sm text-text-primary` (cells, via `Table`) |
| Text — secondary | `text-xs font-medium uppercase tracking-wide text-text-secondary` (headers, via `Table`) |
| Spacing | `px-4 py-3` (cells, via `Table`) |
| Hover/focus state | sortable header hover: `hover:text-text-primary` |
| Shadow | none |
| Accent/status usage | none directly — status cells render `StatusBadge` |

Pattern notes:
**Always a Client Component** (`"use client"`, one file, no server-rendered fallback) — see `docs/plan/phase-9-reusable-ui-components-static-pages/plan.md` decision #2. Typed `columns`/`data` props; sort (single-column, ascending/descending, local `useState`) only activates on columns with `sortable: true`. Falls back to `EmptyState` when `data.length === 0`. Because its column config carries `render` functions, every page that uses it is *also* a Client Component (functions can't cross the Server→Client props boundary) — `order-validation`, `inventory-allocation`, and `payment-aging` pages are `"use client"` for this reason. `dashboard` and `reports` don't use `DataTable` and stay Server Components.
