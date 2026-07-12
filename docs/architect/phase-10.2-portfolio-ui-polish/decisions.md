# Decisions — Phase 10.2: Portfolio UI Polish

Architecture decisions from the `/architect` planning session for Phase 10.2, a token-only
visual/hierarchy pass on the existing Next.js UI. No backend, API, contract, or Phase 11
(SQL Reporting) work is in scope. Source: the planning conversation (AskUserQuestion rounds
+ the user's plan-review corrections), not the code — implementation happens after this
session.

## 1. Shared "inverse surface" token family, not sidebar-only tokens

**Decision:** Add one small token family — `--surface-inverse`, `--surface-inverse-hover`,
`--text-on-inverse`, `--text-on-inverse-muted` — reused by both `SidebarNav` and a new
`Button` `dark` variant, instead of a `SidebarNav`-scoped `--sidebar-*` family plus a
separate dark tone for buttons.

**How it works:** Defined once in `app/globals.css`'s `:root` as HSL triples (matching the
project's existing token convention), mapped in `tailwind.config.ts`'s
`theme.extend.colors`, and consumed via semantic classes (`bg-surface-inverse`,
`text-text-on-inverse-muted`, etc.) — never raw Tailwind palette classes or hex.

**Why this over the alternative:** The requested design intent was explicit — "same dark
navy tone family as the sidebar" for the Download Report / Sample file buttons. A dedicated
`sidebar-*` family plus a separate button-dark tone would require two token sets tuned to
look identical, which is exactly the kind of duplication that drifts apart over time (one
gets adjusted for contrast, the other doesn't, and the "same visual system" claim quietly
becomes false). One shared family makes "look the same" structurally guaranteed rather than
a matching exercise done by eye twice.

**Cost of the alternative:** More token surface area for no visual difference, and a latent
bug class (the two families silently diverging after a future edit to only one of them).

## 2. MetricCard is restructured, not just its grid wrapper

**Decision:** Redesign `MetricCard`'s internal layout (icon chip in a stable position,
value as the dominant centered element, label below, fixed/min-height) rather than leaving
its markup untouched and only changing the wrapping grid's column count.

**Why this over the alternative:** The reference dashboard's KPI tiles read as compact,
roughly square tiles; the current `MetricCard` is a short, wide strip (label+icon row, big
value below, `p-4`) that stays a strip no matter how many grid columns wrap it — narrowing
the columns makes the *card* narrower but doesn't make it *taller* or more centered. The
user explicitly rejected the safer "grid-only retune" option for this reason: "too subtle
for the design goal." This decision was made knowing it touches all ~15 existing
`MetricCard` call sites (3 dashboard KPI groups + all 3 workflow pages' post-run summary
groups) — accepted because the component's public contract (`label`/`value`/`icon`/`tone`
props) doesn't change, so every call site keeps working without edits; only the component's
internals change.

## 3. Grid density capped at 4 columns, following the existing breakpoint convention

**Decision:** Every KPI group (dashboard and workflow-page summary grids alike) moves to
`grid-cols-2 sm:grid-cols-3 lg:grid-cols-4`, replacing today's per-group
`lg:grid-cols-{4,5,6}` variety.

**Why:** The codebase already has a consistent, documented convention of skipping the `md:`
breakpoint entirely (base → `sm:` → `lg:`), discovered during exploration by grepping every
existing grid in `app/` and `components/`. Reusing that exact convention for the new KPI
grids, rather than inventing new breakpoints, keeps the responsive behavior predictable
across the app. Capping at 4 columns (instead of the current per-section 4–6) means a
6-tile group wraps to two rows (4+2) instead of stretching one row edge-to-edge — directly
addressing "avoid long horizontal strips."

## 4. Dashboard's two supporting tables become one paired grid section

**Decision:** "Inventory Shortage Alerts" and "Payment Follow-up Items" — currently two
separate full-width `<section className="mt-6">` blocks, stacked vertically — merge into
one `<section className="mt-6 grid gap-4 lg:grid-cols-2">` wrapping both existing inner
blocks.

**Why this pattern specifically:** This is not a new layout invented for this feature — the
dashboard's own chart pair (`DonutBreakdownChart` + `VerticalBucketBarChart`) and Inventory
Allocation's Remaining Inventory / Supplier Follow-up pair already use exactly this
`grid lg:grid-cols-2` pattern with no `sm:` step. Reusing it here (rather than a new
side-by-side convention) means the two tables stack automatically below `lg` for free, with
no new responsive logic to write or test.

## 5. UploadPanel: fix is bottom-anchoring, not row alignment

**Decision:** The visible bug (drop-zone rows at different heights across 3 upload panels
in a row) is fixed by giving `Card` a `h-full` and wrapping the drop-zone `<label>` plus the
Sample-file `<div>` in a new `<div className="mt-auto flex flex-col gap-3">`, not by
touching the row's internal layout.

**Why this diagnosis matters:** The initial hypothesis (from the request wording — "align
the Choose-a-file area and Browse button cleanly on the same horizontal row") suggested a
same-row alignment problem. Reading the actual component source showed the row was already
correct: `flex items-center justify-between`. The screenshot the user provided of the real
Inventory Allocation page confirmed the *real* bug: because each panel's "Required columns"
text wraps to a different number of lines, the drop-zone that sits below it lands at a
different vertical position per card — a bottom-anchoring problem, not a within-row
alignment problem. Fixing the wrong diagnosis (e.g., tweaking `items-center`/`justify-between`
further) would have changed nothing visible.

## 6. Dark `Button` variant, scoped to exactly two usages

**Decision:** Add a third `cva` variant, `dark`, using the inverse-surface tokens. Apply it
*only* to the 3 workflow pages' "Download Report" buttons and `UploadPanel`'s "Sample file"
link. Explicitly do not touch "Run Validation/Allocation/Calculate" (stays `primary`), "Run
sample data" (stays `secondary`), or `ReportCard`'s "Go to workflow" link (stays
`secondary`) — that link only appears on the static `/dashboard`/`/reports` pages and was
never part of this request.

**Why the narrow scope:** The user's own framing was explicit: "The dark variant should
support secondary-but-important utility actions, not replace the primary workflow action."
Making every non-primary button dark would collapse three distinct visual tiers (primary
blue = main action, dark navy = important-but-secondary, bordered secondary = lesser action)
back down to two, undoing the button-hierarchy goal the change was meant to create.

## 7. Active sidebar link changes from subtle to solid accent (correction)

**Decision (corrected during plan review):** The active nav item changes from its current
`bg-accent-subtle text-accent` to solid `bg-accent text-text-on-accent`.

**Why this was a correction, not a detail:** The first plan draft described this as
"unchanged." That was wrong on inspection of the actual `SidebarNav.tsx` source — the
current active state is a light, subtle accent tint, designed to sit on the light
`bg-surface` background. Against the new dark navy `bg-surface-inverse`, that same subtle
tint would have poor contrast (a light-blue-on-light-tint color combination doesn't carry
over to a dark background). The fix reuses the existing `bg-accent`/`text-text-on-accent`
pair already used for the `Button` `primary` variant elsewhere — one accent color, doing
double duty as "primary action" and "selected nav item," rather than inventing a new
"selected-on-dark" token.

## 8. Exact Tailwind config key shape for the two new class-name families

**Decision (specified precisely during plan review):** `surface-inverse` is a *nested* key
(`{ DEFAULT, hover }`) producing `bg-surface-inverse` / `bg-surface-inverse-hover`, matching
the existing `surface`/`border` pattern. `text-on-inverse` and `text-on-inverse-muted` are
two separate *flat* top-level keys, matching the existing `text-primary`/`text-secondary`
pattern — not nested under a shared `text-on-inverse: { DEFAULT, muted }` object.

**Why this precision mattered:** The codebase mixes both conventions already (some color
families nested, text colors flat), and guessing wrong would either fail to compile or
silently produce a different, unintended class name (e.g. `text-text-on-inverse-DEFAULT` or
similar). Matching each existing convention exactly, rather than picking one shape for both
new families, avoids introducing a third, novel structure into a config file that
explicitly documents itself as the single source of truth for tokens.

## 9. Disabled dark buttons require a visual check, not an assumed pass

**Decision (added during plan review):** The base `disabled:pointer-events-none
disabled:opacity-50` (already global to all `Button` variants) is the starting point but
not treated as sufficient by assumption for the new `dark` variant. A fallback plan is
specified: if a disabled dark-navy button at 50% opacity still reads as "clickable but
greyed" rather than clearly inert, either add an explicit `disabled:bg-surface-muted
disabled:text-text-muted` override, or keep disabled Download Report on `secondary` styling
and only switch to `dark` once a request actually succeeds.

**Why:** Opacity-based disabling degrades differently depending on the base color — a light
`secondary` button already reads as washed-out at 50% opacity, but a solid dark fill can
still look saturated and "present" at the same opacity, giving a false affordance. The
plan treats this as something to verify in a running browser, not something to assert from
first principles.

## 10. Progress-tracker/build-plan docs are updated after verification, not before

**Decision (corrected during plan review):** `context/build-plan.md` and
`context/progress-tracker.md` get their new "Phase 10.2" entries only after the full
verification pass (typecheck/lint/build/pytest + live-browser checks) succeeds.
`context/ui-tokens.md` and `context/ui-registry.md`, by contrast, are updated *during*
implementation, alongside the code changes they describe.

**Why the split:** The first plan draft grouped all doc updates together. The user's
correction distinguishes two kinds of documentation: `ui-tokens.md`/`ui-registry.md`
describe *what a component looks like/how it's styled* — accurate the moment the code is
written. `progress-tracker.md`/`build-plan.md` assert *that a phase is done and verified* —
which is only true after verification actually passes. Writing the "Phase 10.2 complete"
line before running the checks would risk recording a phase as finished based on planned
intent rather than confirmed reality, which is exactly the discipline every prior phase's
progress-tracker entry was written under.
