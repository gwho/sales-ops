# Decisions — Architect Sessions: Phase 9 (Reusable UI Components and Static Pages) and Phase 9.1 (Visual Alignment Fixes)

This covers two separate `/architect` sessions in the same overall build: the original Phase 9 planning session (before any component code existed), and a later Phase 9.1 "Chart Alignment Addendum" session (after the visual-alignment review had already found and fixed several issues, when two new chart components were being added). Each entry states the decision, why it was made, and what the rejected alternative would have cost.

---

## Phase 9 planning session

### 1. Static showcase, not a simulated live app

**Decision:** The 5 pages render committed mock JSON immediately on load. `UploadPanel` is a real, working file-picker (accepts a file, shows the filename) but never gates or replaces the page's rendered content. `WorkflowStepper` renders a fixed, appropriate step. `ReportCard` renders `Ready` directly from the mock `ReportManifest`; its other 3 lifecycle states exist only as prop-driven visual variants, never live-wired via timers.

**Why:** The alternative — a simulated live flow where uploading a file triggers a fake processing delay before results appear — would mean building a real (if fake) client-side state machine for something Phase 10's actual FastAPI integration will replace wholesale. That's throwaway work: every line of fake-async logic written in Phase 9 would need to be deleted, not adapted, once real API calls exist. Building the static showcase instead means Phase 9's job is proving the components render real contract data correctly, which is exactly the risk Phase 9 exists to retire.

**Cost of the alternative:** Extra Client Component surface area, extra state to test, and a false sense that Phase 9 "works end to end" when it would only be working end to end against fake timers.

### 2. `DataTable`: plain client-side sort, no TanStack Table

**Decision:** `DataTable` is a Client Component with a single-column ascending/descending sort via local `useState` and a plain comparator. No filtering, no pagination, no TanStack Table dependency.

**Why:** The mock fixtures generated from `tests/contract_fixtures.py` are 1-2 rows per table at this point in the build. A full table library's column-def API, virtualization, and pagination controls have nothing real to demonstrate against data that small — adding the dependency now buys nothing observable and adds a real dependency-upgrade and API-surface cost later. The column-def shape (`key`, `header`, `render`, `sortable`, `sortValue`) was deliberately kept close to what TanStack Table would expect, so a future swap changes `DataTable`'s internals without forcing every page's column definitions to be rewritten.

**Cost of the alternative:** A library dependency whose main value propositions (virtualized rendering, complex filtering, pagination) are invisible against single-digit-row mock data — paying an API-surface and bundle-size cost for capability that can't be verified working until Phase 10 brings real data anyway.

### 3. shadcn primitives are hand-written, never generated

**Decision:** `Button`, `Card`, `Badge`, and `Table` live in `components/ui/`, written by hand using shadcn's public `new-york` source as a style/API reference only. `npx shadcn add` is never run.

**Why:** `components.json`'s `baseColor: "slate"` (set up as inert plumbing in an earlier phase) means the first `shadcn add` invocation would inject shadcn's own default CSS variables — `--primary`, `--card`, `--destructive`, `--ring` — into `app/globals.css`. This project's own token file, `--accent` specifically, means brand blue; shadcn's own `--accent` convention means a gray hover state — the exact opposite semantic meaning under the same variable name. Running the generator and then manually stripping the injected variables after each `add` is possible but fragile: it's a cleanup step that has to be remembered and correctly executed every single time a new primitive is needed, across however many future primitives get added. Hand-writing avoids the injection risk entirely — there's no generated output to clean up because nothing was ever generated.

**Cost of the alternative:** A recurring, easy-to-forget manual cleanup step per primitive, with a real risk that one `add` invocation ships colliding tokens into `globals.css` without anyone noticing until a component visually breaks.

### 4. No Recharts this phase

**Decision:** The Payment Aging aging-bucket breakdown renders as a token-styled bar list built from plain `div`s, not a Recharts component.

**Why:** Same reasoning as the TanStack Table decision — Recharts' value (interactive tooltips, responsive resizing, multiple chart types) has nothing to prove against a handful of mock rows, and adding a charting library is exactly the kind of dependency this project's phase-gate structure is designed to defer until it's actually load-bearing.

### 5. `StatusBadge`'s tone mapping is fixed before any component code, not decided ad hoc

**Decision:** A complete field→tone mapping table was written during planning, before `StatusBadge.tsx` existed. The component itself never infers tone from a label string — callers always pass an explicit `tone` computed by a small, typed helper function specific to the field it came from (`severityTone`, `allocationStatusTone`, `importancePriorityTone`, `agingBucketTone`, `followUpPriorityTone`, `reportLifecycleTone`).

**Why:** The same literal string means different things depending on which contract field it's attached to. `"High"` appears as `ValidOrderRow.priority` (an importance ranking — high priority is not itself a problem) and separately as `PaymentAgingRow.follow_up_priority` (an urgency-of-problem ranking — high follow-up priority means someone is dangerously overdue). A single lookup function keyed only on the string `"High"` would have to guess which meaning applies, and would guess wrong exactly half the time it mattered. Deciding the full mapping during planning, rather than component-by-component as pages were built, meant `/imprint` documented a finished decision rather than in-flight reasoning, and meant every call site across 4 pages used the same table instead of each page author re-deriving colors independently.

**Cost of the alternative:** A `StatusBadge` that silently picks the wrong color for `"High"` in one of its two meanings, discovered only by someone noticing a Payment Aging follow-up badge and an Order Priority badge disagreeing about what "High" should look like.

---

## Phase 9.1 Chart Alignment Addendum session

### 6. Chart components live in `components/charts/`, not `components/tables/`

**Decision:** `DonutBreakdownChart` and `VerticalBucketBarChart` got their own top-level folder, separate from `MiniBar`/`SegmentedBar`/`AgingBucketBars`, which stayed in `components/tables/`.

**Why:** A review pass on the first draft plan flagged that grouping whole-chart components under `tables/` alongside small in-cell/in-row indicators would muddy the folder's taxonomy — `components/tables/` is for things that live *inside or directly beside* a table row, and a donut chart is neither. This is a small decision on its own, but it's the kind of thing that compounds: a folder whose name stops matching its actual contents becomes a folder nobody trusts to navigate by name, and every subsequent "where does X go" decision gets harder to make consistently.

### 7. No dynamic Tailwind class construction — every tone→class mapping is a literal object

**Decision:** Every place a component needs to pick a CSS class based on a `Tone` value uses a literal `Record<Tone, string>` object (e.g. `{ success: "stroke-success", warning: "stroke-warning", ... }`), never a template string that builds the class name at runtime from the `tone` variable (e.g. never `` `stroke-${tone}` ``).

**Why:** Tailwind's build-time scanner works by treating the whole source tree as one big string and searching for substrings that look like utility classes — it does not execute JavaScript or evaluate template literals to see what they'd produce at runtime. A class name assembled as `` `stroke-${tone}` `` never appears as a literal substring anywhere in the source (only the fragments `"stroke-"` and whatever `tone` happens to hold do), so Tailwind's scanner has nothing to match and never generates the CSS for that class — the styling silently fails in production even though it might appear to work in development under some configurations. A literal object where every value is a complete, real class name (`"stroke-success"`) sidesteps this entirely: the full string exists in the source file exactly where Tailwind's scanner looks.

**Cost of the alternative:** Styling that appears to work while developing (if a dev-mode JIT compiler is more permissive) and silently disappears in a production build — a class of bug that's easy to miss because nothing throws an error; the element just renders unstyled.

### 8. Chart components reuse existing tone helpers instead of re-deciding colors

**Decision:** `DonutBreakdownChart` and `VerticalBucketBarChart` never decide what color a status or bucket should be. The caller (`dashboard/page.tsx`) resolves each data point's `tone` via the same `allocationStatusTone`/`agingBucketTone` functions already used to color the equivalent `StatusBadge` tags elsewhere in the app, and passes the result in as a plain prop.

**Why:** The addendum that introduced these charts initially proposed specifying tones per-bucket directly in the chart-wiring code (e.g. "61-90 Days → warning/danger emphasis"), which would have been a second, independent color decision for data that already had one. A review pass caught this and asked for the existing helpers to be reused instead. The alternative — hand-picking colors again — creates a latent drift risk: if `agingBucketTone`'s mapping is ever revised (say, because a business rule threshold changes which bucket counts as "danger"), only the `StatusBadge` usages would pick up the change automatically; the chart's independently-hardcoded colors would need a second, easy-to-forget edit to stay in sync, and nothing would flag the mismatch except a human noticing the chart and the table disagree.

### 9. `Tone` stays a type-only import from `StatusBadge.tsx` — no new shared file

**Decision:** Chart and table-viz components import `Tone` via `import type { Tone } from "@/components/workflow/StatusBadge"` — a type-only import with zero runtime footprint — rather than the project growing a new `components/workflow/status-tones.ts` file to hold the type and helpers separately from the component.

**Why:** The review question that raised this ("does a chart importing from a component file create an awkward dependency?") turned out to have a factual answer once actually traced: the chart components only ever need the `Tone` *type* for their prop signatures; the *functions* (`allocationStatusTone`, `agingBucketTone`) are called exactly once each, inside the page that wires the chart up, never inside the chart component itself. A type-only import is erased entirely by the TypeScript compiler — there's no runtime coupling to untangle, because there isn't one. Moving `Tone` to a new file would have "solved" a problem that, on inspection, didn't exist, at the cost of one more file and one more place a future reader has to know to look.

### 10. Zero-value guards added proactively, not after hitting a real bug

**Decision:** `DonutBreakdownChart` renders a neutral full ring with `"0"` in the center if every segment's value is 0; `VerticalBucketBarChart` renders an empty-state caption instead of a bar row if every bar's value is 0.

**Why:** Both components' core math divides by a total (`value / total` for the donut's arc-length calculation, `value / max` for each bar's height). Dividing by zero doesn't throw in JavaScript — it silently produces `NaN`, which then flows into a CSS `stroke-dasharray` or a `height: NaN%` style, rendering as either nothing or something visually broken, with no error anywhere to point at the cause. This was caught during a review pass on the plan, before any code existed to hit the bug — the current mock data always has a non-zero total, so the guard was never "discovered" by a failure, only anticipated. The two components chose different guard behaviors (a neutral ring vs. an empty-state message) because a donut chart with a literal "0" in the middle is still a meaningful, honest representation of "there is genuinely nothing here," while a bar chart with every bar flattened to zero height reads as visually broken rather than intentional — an explicit caption communicates the same fact more clearly.
