# Tutorial 11 — Portfolio UI Polish: Presentation Work as Constrained Systems Work

**After completing this tutorial you will understand:** why a "make it look nicer" phase was
planned with the same rigor as a feature phase, including an explicit list of what it would *not*
touch; how one shared token family serves two independently-styled components without letting them
drift apart; why restyling `MetricCard` internally required zero changes at any of its ~15 call
sites; why removing nine real KPIs from `/dashboard` was a deliberate, justified content decision
and not scope creep; why the exact same "add a hover tooltip" requirement was solved with React
state in one chart and pure CSS in the sibling chart; and how two real, user-facing bugs (a
hydration mismatch, a pointer-events trap) were found by scripted interaction checks that plain
visual review had already missed.

> [!NOTE]
> **Prerequisites:** [Tutorial 10](../10-reusable-ui-components-static-pages/README.md) — every
> component this tutorial modifies (`Button`, `MetricCard`, `UploadPanel`, `SidebarNav`) was fully
> covered there first; this tutorial only covers what changed and why. [Tutorial 07](../07-fastapi-integration/README.md) — for the live-page state that existed before this polish
> pass. Precisely what that means, timeline-wise, is worth being exact about: Phase 10.2 sits
> chronologically after Phase 10's FastAPI integration, so the **three workflow pages**
> (`/order-validation`, `/inventory-allocation`, `/payment-aging`) were already reading live data by
> Phase 10.2. `/dashboard` and `/reports` were not — they remained static, reading Tutorial 10's mock
> JSON, all the way through Phase 10.2. `/dashboard` only started reading live, session-scoped data
> in Phase 12 (Tutorial 12), well after this tutorial's subject phase ended — this tutorial's own
> `/dashboard` code citations are current (Phase 12-era `DashboardLiveSections.tsx`), but the
> *phase* this tutorial describes never itself made the dashboard live.

> [!NOTE]
> **A caveat about the current codebase, worth stating once, up front:** two things this tutorial
> touches were later revised past their Phase 10.2 shape, and both are called out explicitly, in
> place, rather than silently smoothed over. First: the fixed-width, non-responsive `SidebarNav`
> limitation this tutorial's Part 8 covers as a deliberately-deferred bug was later actually
> resolved by the `mobile-nav-shell-responsiveness` work (a real drawer now exists in
> `AppShell.tsx`/`TopHeader.tsx`, per Tutorial 10's own opening caveat) — treat Part 8's discussion
> as a real decision made at a real point in time, not a still-open defect. Second: Phase 12 moved
> the dashboard's live KPI/chart/table sections out of `app/dashboard/page.tsx` and into a new
> Client Component, `components/dashboard/DashboardLiveSections.tsx`, to support session-scoped,
> per-visitor saved results (Tutorial 12 covers this in full). This tutorial cites the *current*
> `DashboardLiveSections.tsx` for every dashboard-visual code excerpt, and names each Phase 12
> addition (the `liveInventoryAllocation ?? inventoryAllocationResult`-style fallback pattern, the
> `sample` chip) the moment it appears — Phase 10.2 itself never touched session state at all.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Shared token family as a single source of truth across components | `--surface-inverse` consumed by both `SidebarNav.tsx` and `Button.tsx`'s `dark` variant | System design |
| Two solutions to the same coordination problem: component state vs. pure CSS | `DonutBreakdownChart`'s `useState` vs. `VerticalBucketBarChart`'s `group`/`group-hover` | Design patterns |
| CSS Grid's default cross-axis stretch | Chart-card sizing bug — `align-items: stretch` making a shorter sibling match a taller one's height | System design |
| Filesystem duplicate-file collision breaking module resolution | The stray macOS Finder-duplicated `.next/types/*.d.ts` files causing a `tsc` "duplicate identifier" error | OS fundamentals |
| Hydration as an exact content/DOM-match requirement | The `DonutBreakdownChart` `<title>` hydration mismatch — server-rendered content and the client's initial render must agree | System design |

## How to use an LLM before this tutorial

### Concept 1 — Scoping a "polish" phase like a feature phase

> "Explain why a team doing pure visual/UX polish work on an existing, working application would
> still benefit from writing down an explicit scope boundary (a list of what will and won't
> change) before touching any code — the same discipline as scoping a new feature, even though
> nothing about the underlying data or business logic is changing. Give a concrete failure mode
> that an unscoped 'just make it look better' pass tends to fall into. Quiz me on the difference
> between a screenshot revealing a bug and a screenshot being permission to fix every bug it
> reveals."

*What to listen for:* visual/UX polish work is exactly as prone to scope creep as feature work,
maybe more so, because "does this look better" has no natural stopping point the way "does this
pass the test suite" does — an explicit non-goals list (no backend changes, no new contracts, no
new business metrics) gives the work a boundary that "it still looks like there's more to improve"
never would on its own. The sharpest version of the failure mode: a screenshot showing one bug
often sits next to several other things that also look imperfect, and treating the screenshot as
license to fix everything visible in it, rather than the one specific thing it was sent to
illustrate, is how a bounded polish pass balloons into an unplanned rewrite.

*Practice question:* if a developer is shown a screenshot to fix one specific alignment bug, and
notices while there that a nearby button's hover color also looks slightly off, should fixing the
hover color be treated as included in the same request by default, or as a separate decision?

### Concept 2 — One shared token versus two independently-tuned ones

> "Two different UI components need visually similar dark, high-contrast styling — say, a sidebar
> background and a button variant. Compare two designs: (A) both consume the exact same set of
> shared color tokens, or (B) each has its own separately-defined, independently-tunable dark
> color. Walk through what happens six months later when someone wants to slightly adjust 'the dark
> navy color' — under each design, how many places does that edit touch, and what's the risk of the
> two components visually drifting apart from each other over time under design (B)? Quiz me on
> when design (B) — independent tokens — is actually the *right* choice instead."

*What to listen for:* design (A) guarantees the two components can never visually drift apart from
each other, because there is structurally only one value to change — editing "the dark navy color"
is a single edit that affects both consumers identically, by construction. Design (B) allows each
component to evolve independently, which is a real advantage precisely when the two components
are *not* supposed to always look identical — sharing a token is the right call for "these are the
same visual role," and the wrong call for "these coincidentally started out looking similar but
represent genuinely different concepts."

*Practice question:* if a design system's button component and its alert-banner component happen
to use the same shade of red today, is that a sign they should share one red token, or a
coincidence worth leaving as two independently-defined values?

### Concept 3 — CSS Grid's stretch behavior and why "the same height" isn't automatic

> "Explain CSS Grid's (or Flexbox's) default cross-axis alignment behavior: when several sibling
> items sit in the same row/column and one has more natural content than the others, what happens
> to the shorter ones by default, and why? Then explain why simply matching heights this way can
> still leave a visually broken result — what has to *also* be true about a shorter item's own
> internal layout for the extra stretched space to look intentional rather than like a mistake?
> Quiz me on the difference between 'the box is now tall enough' and 'the box's content fills that
> height sensibly.'"

*What to listen for:* CSS Grid/Flexbox's default cross-axis behavior (`align-items: stretch`)
automatically makes every item in a row match the height of the tallest one — this happens for
free, with no extra CSS needed, the moment items share a grid row. But a stretched box whose inner
content wasn't designed to use the extra space (no `flex flex-col justify-center`-style content
distribution) just accumulates the leftover height as dead space at the bottom, which reads as
broken even though the *box* itself is now technically the "correct" height — the fix has to
address both the outer stretch *and* how the inner content responds to having more room than its
natural content needs.

*Practice question:* if two sibling cards in a CSS Grid row are stretched to equal height by
default, but only one of them has its inner content wrapped in a vertically-centering flex
container, what will the *other* card look like once both are stretched?

### Concept 4 — Filesystem duplicate files and build-tool confusion

> "On a filesystem where a file-manager application can silently create a duplicate copy of a file
> with a modified name (e.g. appending ' 2' before the extension) — often from a sync conflict or
> an accidental duplicate-and-rename — explain what happens when a compiler or type-checker that
> discovers source files by scanning a directory encounters two files that both appear to define
> the same thing (the same exported type, the same route). Why would deleting the *build output*
> directory, not the *source* files, sometimes be the correct fix? Quiz me on how you'd tell a
> genuine duplicate-identifier bug in your own source code apart from this specific
> filesystem-artifact problem."

*What to listen for:* a type-checker or bundler that discovers files by scanning a directory tree
has no way to know that a file named with a stray " 2" suffix is an accidental duplicate rather
than a deliberately different file — if both define the same exported symbol, the tool reports a
genuine "duplicate identifier" error, exactly as it would for a real naming collision in
intentional source code. When the duplicated files live inside a tool-generated output directory
(like `.next/`) rather than hand-written source, deleting and letting the tool regenerate that
directory is safe and sufficient — the duplicate was never meant to exist as source at all, so
there's nothing to "fix," only to remove and regenerate cleanly.

*Practice question:* if a duplicate-identifier error names two files, and one of them lives inside
a `.gitignore`d build-output directory while the other is genuine hand-written source, which one is
almost certainly the actual problem?

### Concept 5 — Hydration as an exact-match requirement, not an approximate one

> "In a framework that renders the same component tree once on the server (producing HTML sent to
> the browser) and then again on the client (to attach interactivity, a process often called
> 'hydration'), explain why the framework needs the server-rendered output and the client's
> first render to match *exactly*, down to whitespace inside text nodes, rather than just
> 'looking the same visually.' What does the framework do when it detects a mismatch, and why is
> that response expensive? Quiz me on why two renders that look pixel-identical in a screenshot
> could still fail a hydration check."

*What to listen for:* hydration isn't a visual comparison — it's the framework reusing the
server-rendered DOM nodes and attaching event handlers/state to them directly, which only works
safely if the framework can trust that what the client *would have* rendered is identical to what's
already sitting in the DOM from the server. A mismatch means that trust is broken, so the framework
falls back to discarding and re-rendering that part of the tree from scratch on the client — safe,
but expensive, and visible to a real user as a flash/flicker. Two renders can look visually
identical in a screenshot while still differing at the raw-text-node level (extra whitespace,
different line-break placement inside a text node) — a mismatch a human eye would never catch, but
React's hydration check, which expects the client's initial rendered output to match the
server-generated content, does.

*Practice question:* if a server-rendered `<title>` element's text content has one extra space
character compared to what the client would render, would that difference be visible to a user
looking at the page, and would it still trigger a hydration mismatch?

## Architecture overview

Every earlier Track 5 tutorial covered code that changed *what* the application could do —
new routes, new data, a new component system. Phase 10.2 changes none of that; every artifact this
tutorial covers is presentation-only, layered on top of Tutorial 10's already-complete component
system:

```text
   context/ui-tokens.md                Tutorial 10's finished component system
   (already-established token          (Button, Card, Badge, Table, MetricCard,
    naming conventions)                 UploadPanel, DataTable, StatusBadge, ...)
              │                                       │
              │ new "Inverse Surface" family           │ restyled internally,
              ▼                                        │ prop contracts unchanged
   app/globals.css :root                                ▼
   + 4 new CSS variables               components/ui/Button.tsx (+ "dark" variant)
   (--surface-inverse, -hover,         components/layout/SidebarNav.tsx (recolored,
    --text-on-inverse, -muted)          + icons)
              │                        components/workflow/MetricCard.tsx (restructured)
              ▼                        components/workflow/UploadPanel.tsx (bottom-anchored)
   tailwind.config.ts
   (mapped into 2 differently-shaped
    config-key conventions — Part 2)

   ── real bugs found only once real interaction was scripted ──

   components/charts/DonutBreakdownChart.tsx  ──┐
   (promoted to Client Component,               ├─► hydration mismatch (Part 6)
    useState for shared hover/tooltip state)    └─► pointer-events trap (Part 6)

   components/charts/VerticalBucketBarChart.tsx (stayed Server, pure CSS group-hover)

   ── a deliberate content decision, not a restyle ──

   app/dashboard/page.tsx / components/dashboard/DashboardLiveSections.tsx
   3 per-workflow KPI groups (~15 tiles) ──► 1 "Overview" row (5 tiles) + 2 charts
```

Key invariants for this phase:

1. **The Inverse Surface token family is scoped to exactly two consumers** — `SidebarNav` and
   `Button`'s `dark` variant. Nothing else in the app may reach for these tokens without a new
   token-change decision (Part 2).
2. **`MetricCard`'s prop contract (`label`, `value`, `icon?`, `tone?`) did not change** — only its
   internal layout did. Roughly 15 call sites across four pages depend on that contract holding
   (Part 3).
3. **`/dashboard`'s 5-card Overview row is a deliberate, user-approved content reduction**, not the
   full KPI set — the dropped KPIs remain fully available on each workflow page's own summary grid
   (Part 4).

## Part 1 — A bounded polish phase with non-goals

[`docs/plan/phase-10.2-portfolio-ui-polish/explanation.md`](../../plan/phase-10.2-portfolio-ui-polish/explanation.md) §1 states this phase's framing plainly,
before any code is discussed: "a token-only visual/hierarchy pass — no backend, API, contract, or
Phase 11 (SQL Reporting) changes." That framing came out of a prior `/grilling` planning pass, and
the actual `/architect` session that followed pinned down exactly the kind of ambiguous terms a
polish pass tends to leave loose — what "compact tile" means concretely, whether new tokens are
shared or per-component, which specific buttons get the new dark variant and which explicitly
don't.

Worth naming honestly, because it's a genuinely useful thing to notice about how this feature
actually shipped: the approved plan was not the whole story. `explanation.md` §1 records that the
user kept extending scope *during* implementation by sending live screenshots of the running
app — a reference dashboard image, a broken `UploadPanel` alignment, a chart-card blank-space bug,
a request to consolidate the dashboard's KPI layout, a sample-file button sizing bug, a request for
sidebar icons and card hover effects. None of these triggered a second full plan-mode round — each
was small enough, and grounded enough in a concrete visual artifact, to implement directly and fold
into the same Phase 10.2 scope. This is Concept 1's practice question playing out for real: a
screenshot revealing a bug was treated as permission to fix *that* bug, evaluated each time on its
own merits, not as blanket license to redesign anything else visible in the same image.

**Try it yourself:** Open [`docs/plan/phase-10.2-portfolio-ui-polish/plan.md`](../../plan/phase-10.2-portfolio-ui-polish/plan.md)'s Key Invariants
section and count how many of its six bullets name something this phase explicitly did *not* do or
must *not* be extended to do, versus how many describe what it built. The ratio itself is evidence
of how seriously the non-goals were tracked, not just the goals.

## Part 2 — Inverse-surface tokens as a shared visual role

Open [`app/globals.css`](../../../app/globals.css) lines 40–43 and
[`tailwind.config.ts`](../../../tailwind.config.ts) lines 57–62:

```css
--surface-inverse: 222 47% 11%;
--surface-inverse-hover: 222 39% 20%;
--text-on-inverse: 0 0% 100%;
--text-on-inverse-muted: 215 20% 65%;
```

```ts
"surface-inverse": {
  DEFAULT: "hsl(var(--surface-inverse))",
  hover: "hsl(var(--surface-inverse-hover))",
},
"text-on-inverse": "hsl(var(--text-on-inverse))",
"text-on-inverse-muted": "hsl(var(--text-on-inverse-muted))",
```

`explanation.md` §2 records the core design decision directly: one shared token family, not a
`SidebarNav`-only dark tone plus a separately-tuned dark color for `Button`'s new variant — "the
sidebar and dark buttons should look like the same visual system... a shared inverse token family...
prevents two separate token families from drifting." Both `SidebarNav.tsx` and `Button.tsx`'s
`dark` variant (Tutorial 10 Part 1) consume these same four variables; there is no second,
independently-tunable "dark navy" anywhere in the codebase.

What took a genuine correction round, per `explanation.md` §2, was the exact *shape* of the
Tailwind config entries — not the values, the structure. This codebase already mixes two
conventions: some color families are nested objects (`surface: { DEFAULT, muted, subtle }`,
expanding into `bg-surface`, `bg-surface-muted`, `bg-surface-subtle`), while text colors are flat
sibling keys (`"text-primary"`, `"text-secondary"`, each its own top-level entry). The first
implementation pass didn't commit to either shape for the two new families; the correction applied
the precedent precisely: `surface-inverse` nested (`{ DEFAULT, hover }`, matching `surface`/`border`,
since `hover` is a genuine state-variant of one base color), `text-on-inverse` and
`text-on-inverse-muted` as two separate flat keys (matching `text-primary`/`text-secondary`, since
they're independently-named text roles, not a base-plus-variant pair).

> **System design — Shared token family as a single source of truth:** This is Concept 2's design
> (A) made concrete — one set of variables, two consumers, with no independent per-component
> copies to drift apart. It's the identical pattern Tutorial 09 Part 4 covered for `--accent` more
> generally; the new fact this Part adds is that the *shape* of the config entry (nested object vs.
> flat sibling keys) also has to follow an existing convention, or Tailwind will still generate
> *some* class — just not necessarily the one component code actually references, a bug that
> surfaces as a missing utility class rather than a build error.

One more decision worth naming precisely: `--surface-inverse`'s value (`222 47% 11%`) is the
*exact same* HSL triple as the pre-existing `--text-primary`. Not a coincidence — rather than
picking an arbitrary "looks navy enough" value, this reuses a hue/lightness the palette already
uses (as a *text* color on light backgrounds) and repurposes it as a *fill*. `--text-on-inverse:
0 0% 100%` does the same, reusing `--text-on-accent`'s pure white.

**Checkpoint:** Why does `surface-inverse` use a nested Tailwind config object (`{ DEFAULT, hover
}`) while `text-on-inverse` and `text-on-inverse-muted` use two flat sibling keys, when both are
arguably "a base value plus a variant"?

<details>
<summary>Reveal answer</summary>

The distinguishing rule isn't "does a variant exist" — both cases technically have one — it's
whether the variant is a genuine *state* of the same underlying color (hover being a darker/lighter
version of the same base fill, the way `surface-inverse-hover` relates to `surface-inverse`) versus
two *independently meaningful* roles that happen to both be text colors on the same background
(`text-on-inverse` for primary text, `text-on-inverse-muted` for secondary/de-emphasized text — one
isn't a hover state of the other; a component could use either independently, and does). The
existing precedent already drew this exact line: `surface`/`border` nest their state variants
(`muted`, `subtle`, `strong`), while `text-primary`/`text-secondary`/`text-muted` sit as flat
top-level siblings, because those are independent roles a component picks one of, not a base-plus-
hover pair.
</details>

**Checkpoint:** `--surface-inverse` was set to the exact same HSL value as the pre-existing
`--text-primary`. What would be lost if a brand-new, unrelated navy value had been chosen instead?
What would be lost if `--surface-inverse` had simply *been* `--text-primary`, reused directly with
no new variable?

<details>
<summary>Reveal answer</summary>

A brand-new, unrelated navy value would work visually but would introduce a color with no
provenance — nothing ties it to the rest of the palette, and a future reviewer auditing "does this
app use a disciplined, bounded color palette" would have to take it on faith rather than being able
to trace it back to an already-justified value. Reusing the *exact same HSL triple* as
`--text-primary` gives that provenance for free: the new dark surface is provably drawn from the
existing palette, not invented by feel. Going the other direction — literally making
`--surface-inverse` *be* `--text-primary` with no separate variable — would lose something more
concrete: `--text-primary` is semantically a *text* role (used with `text-*` utilities, expected to
sit *on* a light background), and `--surface-inverse` is a *fill* role (used with `bg-*` utilities).
Collapsing them into one variable would mean any future change intended for "text color on light
backgrounds" (the actual, ongoing meaning of `--text-primary`) would silently also change "the
sidebar's background color" — the two roles need independent names precisely so they can be edited
independently in the future, even though they start out numerically identical today.
</details>

**Checkpoint:** The `dark` `Button` variant and `SidebarNav` share one token family instead of two.
Walk through a concrete scenario, six months from now, where someone tweaks
`--surface-inverse-hover` for the sidebar only — what protects the `dark` button from silently
going out of sync, and what would happen if the two had used separate token families instead?

<details>
<summary>Reveal answer</summary>

Nothing has to "protect" the `dark` button from going out of sync, because there is structurally
only one variable to tweak — a future developer editing `--surface-inverse-hover` in
`app/globals.css`'s `:root` block changes the value every consumer reads, `SidebarNav`'s inactive-
link hover and `Button`'s `dark`-variant hover alike, in the same edit, automatically. There's no
second copy that could be forgotten. If the two components had used separate token families from
the start (say, `--sidebar-hover` and `--button-dark-hover`, independently valued), a developer
intending "make the dark hover state slightly lighter everywhere" would have to remember both
variables exist and edit both — and if they only knew about (or only tested) one consumer, the two
would drift apart silently, with no error or warning, exactly the failure mode a shared token
family exists to make structurally impossible rather than merely discouraged.
</details>

**Try it yourself:** Run `rg -n "bg-surface-inverse|surface-inverse-hover" components/layout/SidebarNav.tsx components/ui/Button.tsx`
from the repo root. Confirm both files show up, and that each match is a real class reference to the
shared token family — not a hardcoded color, not a component-local redefinition. This is the same
mechanical proof Challenge 1 asks for later, done once here in miniature.

## Part 3 — Restyle internals while preserving prop contracts

Open [`components/workflow/MetricCard.tsx`](../../../components/workflow/MetricCard.tsx) lines
11–20 and 31–32:

```tsx
type MetricCardProps = {
  label: string;
  value: string | number;
  icon?: ReactNode;
  tone?: Tone;
  /** Dashboard-only (Phase 12): true when this card's value came from the
   * static sample fallback rather than the visitor's own Saved Workflow
   * Result -- see docs/adr/0007-session-scoped-workflow-result-persistence.md. */
  sample?: boolean;
};
```

```tsx
/** Icon chip is optional and decorative only — matches the Figma-approved "label + big number + icon chip" KPI card pattern, never the trend-delta that sits next to it in the same reference (that stays out of scope). Phase 10.2: restructured into a compact, roughly square tile (icon top, value centered/prominent, label below) instead of a short wide strip, with a min-height so a row of tiles aligns regardless of value/label length. */
export function MetricCard({ label, value, icon, tone = "neutral", sample = false }: MetricCardProps) {
```

`plan.md`'s own invariant states this Part's whole point directly: `MetricCard`'s prop contract —
`label`, `value`, `icon?`, `tone?` — did not change this phase; only its internal JSX layout did
(the component's own comment names the shift precisely: from "a left-aligned label+icon row, value
below" strip into a centered column, icon chip → value → label, with a fixed `min-h-[104px]`).
Every one of the roughly 15 call sites across `/dashboard` and all three workflow pages continued
to call `<MetricCard label="..." value={...} icon={...} tone="..." />` completely unchanged — the
restyle is entirely internal to the component's own return statement.

This is possible specifically because a component's *props* are its real interface — as long as
the shape of what a caller must supply stays fixed, the component's own rendering logic can change
freely with zero coordinated edits anywhere else. `sample?: boolean` is visible in the type above as
a genuinely *new* prop, but its own comment dates it to Phase 12, not Phase 10.2 — it's shown here,
labeled, because it's the natural next thing a reader of this exact prop type would ask about; Phase
10.2 itself added no new props to `MetricCard`, only restructured the JSX behind the existing four.

**Try it yourself:** Run `grep -rn "<MetricCard" app/ components/` from the repo root. Pick any
three results and confirm each one passes only `label`, `value`, `icon`, `tone`, and (only in
`DashboardLiveSections.tsx`) `sample` — no call site reaches into or depends on anything about the
component's internal layout structure this Part just covered.

## Part 4 — Executive hierarchy through deliberate omission

`explanation.md` §7 names this phase's most consequential decision directly: "The dashboard KPI
consolidation was a deliberate content decision, not a restyle." Every other edit in Phase 10.2
preserves all existing data and values, restyling only — this one genuinely removes content from
`/dashboard`. The originally approved plan kept all three per-workflow KPI groups intact (roughly
15 `MetricCard` tiles, plus a `SegmentedBar`), only restyling `MetricCard` itself. Mid-session, the
user redirected explicitly: "The current dashboard has too many KPI cards arranged in
workflow-specific groups... I want the dashboard to feel more like a modern executive overview:
fewer top-level KPI cards."

Open [`components/dashboard/DashboardLiveSections.tsx`](../../../components/dashboard/DashboardLiveSections.tsx)
lines 109–148 (the current file — Phase 12 moved this section here from `app/dashboard/page.tsx`,
per this tutorial's opening caveat):

```tsx
<section className="mt-6">
  <h2 className="text-base font-semibold text-text-primary">Overview</h2>
  <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
    <MetricCard
      label="Total Orders"
      value={formatNumber(validation.total_orders)}
      icon={<ClipboardList size={16} />}
      tone="info"
      sample={orderValidationIsSample}
    />
    <MetricCard
      label="Invalid Orders"
      value={formatNumber(validation.invalid_orders)}
      icon={<XCircle size={16} />}
      tone="danger"
      sample={orderValidationIsSample}
    />
    <MetricCard
      label="Fully Allocated"
      value={formatNumber(allocation.fully_allocated_count)}
      icon={<CheckCircle2 size={16} />}
      tone="success"
      sample={inventoryAllocationIsSample}
    />
    <MetricCard
      label="Backordered"
      value={formatNumber(allocation.backordered_count)}
      icon={<Truck size={16} />}
      tone="danger"
      sample={inventoryAllocationIsSample}
    />
    <MetricCard
      label="Overdue Amount"
      value={formatAmount(aging.overdue_amount)}
      icon={<AlertTriangle size={16} />}
      tone="warning"
      sample={paymentAgingIsSample}
    />
  </div>
</section>
```

Five tiles, down from roughly fifteen. The justification that made this acceptable, per
`explanation.md` §7, is a specific, checkable condition, not just a taste preference: dropping a
KPI from `/dashboard` is fine *because the same information remains available elsewhere* — each
workflow page's own post-run summary grid still displays the complete, un-trimmed KPI set for that
workflow. `/dashboard` becomes a curated overview; it never becomes the *only* place a number is
shown. The five tiles chosen (four counts, one dollar amount) deliberately mirror a reference
dashboard's own composition, giving the row variety in what kind of number each tile shows rather
than five same-shaped counts. The `SegmentedBar` (Valid vs. Invalid orders) was dropped outright,
not relocated — its information (the ratio between two numbers) became redundant the moment
Total Orders and Invalid Orders both got their own tiles in the same row.

A closely related correction followed almost immediately: the first pass had applied a shared "cap
every KPI grid at 4 columns" rule to *both* `/dashboard` and the three workflow pages' own summary
grids. A screenshot of Inventory Allocation's summary wrapping to 4+1 across two rows showed this
was wrong for the workflow pages specifically. `plan.md`'s own invariant states the resolution: the
three workflow pages each fit their own actual card count in one row on desktop
(`lg:grid-cols-6`/`5`/`4` for Order Validation/Inventory Allocation/Payment Aging), while
`/dashboard`'s Overview row stays capped at a fixed 5 columns — a deliberately different rule for a
deliberately different kind of page.

**Checkpoint:** The dashboard KPI consolidation removed real data (9 KPIs) from `/dashboard`, not
just restyled it. What's the specific condition the user gave that made this acceptable, and how
would you verify that condition still holds if a workflow's summary grid changes in the future?

<details>
<summary>Reveal answer</summary>

The specific condition: every KPI dropped from `/dashboard` must still be fully visible somewhere
else in the app — specifically, on that workflow's own post-run summary grid — so nothing is
actually *lost*, only de-duplicated off the landing page. Verifying this condition holds in the
future is mechanical, not a matter of taste: for each of the nine dropped KPIs
(Duplicate Orders, Invalid SKUs, Missing Fields, Total Order Lines, Partially Allocated, Low Stock
SKUs, Total Outstanding, High Priority Count, 90+ Days Amount), confirm it still appears in its
originating workflow page's own summary `MetricCard` grid. If a future edit ever removed one of
these from its workflow page's summary *without* re-adding it to `/dashboard`, that specific KPI
would become genuinely unavailable anywhere in the app — the condition that licensed dropping it
from the dashboard would no longer hold, and `plan.md`'s own invariant explicitly warns against
exactly this drift.
</details>

**Checkpoint:** Why does `/dashboard`'s Overview row stay capped at 5 columns while the three
workflow pages' own summary grids each fit their own count (4, 5, or 6)? What would break,
conceptually, if the same "cap at 4" rule had been kept for both?

<details>
<summary>Reveal answer</summary>

`/dashboard`'s row is capped because its card *count* is a fixed, deliberate editorial choice (five
specific tiles, chosen for variety, not "however many KPIs this workflow happens to produce") — a
column count matching a fixed content count is simply correct there. A workflow page's summary
grid, by contrast, has to display *every* KPI that workflow's own contract produces, whatever that
count happens to be (`ValidationSummary` has six fields, `AllocationSummary` has five,
`PaymentAgingSummary` effectively contributes four tiles) — capping that grid at a number smaller
than its real content count would force wrapping to a second row regardless of screen width, which
is exactly the bug the mid-session correction fixed. Applying "cap at 4" uniformly to both would
have meant Order Validation's six real KPIs wrapping awkwardly to 4+2, a visually broken layout for
a page whose card count isn't a curated five-item list — it's the workflow's entire, uncurated
summary.
</details>

**Checkpoint:** The `SegmentedBar` (Valid vs. Invalid orders) was dropped rather than moved
elsewhere. What's the argument that its information is now redundant, and under what future change
would that argument stop holding?

<details>
<summary>Reveal answer</summary>

The argument: a segmented bar showing "Valid vs. Invalid" as a ratio is visually communicating
exactly the same two numbers the new Total Orders and Invalid Orders `MetricCard` tiles already
show individually, in the same row, a few pixels away — a reader can already compute "how many are
valid" by subtracting, or simply see both raw counts directly. The redundancy argument would stop
holding the moment `/dashboard`'s Overview row *stopped* showing both `total_orders` and
`invalid_orders` as separate tiles — if a future redesign trimmed the Overview row further and
dropped one of those two specific tiles, the ratio the `SegmentedBar` communicated would no longer
be reconstructable from what's left on the page, and reintroducing some form of that visual (a bar,
a percentage, or the tile itself) would become a legitimate consideration again.
</details>

**Try it yourself:** Inventory all nine KPIs dropped from `/dashboard`'s Overview row — Duplicate
Orders, Invalid SKUs, Missing Fields, Total Order Lines, Partially Allocated, Low Stock SKUs, Total
Outstanding, High Priority Count, 90+ Days Amount — and confirm each still appears as a real
`MetricCard label="..."` on its originating workflow page's own summary grid. Run
`rg -n "label=\"Duplicate Orders\"|label=\"Invalid SKUs\"|label=\"Missing Fields\""
"app/(workspace)/order-validation/page.tsx"`, then the equivalent for the Inventory Allocation and
Payment Aging KPIs on their own pages, and confirm every one of the nine is a real match — direct,
current proof that the "still fully visible somewhere else" condition genuinely holds today.

## Part 5 — Two interaction strategies for two chart shapes

`explanation.md` §8 frames the deciding question precisely: not "does this need to react to hover,"
but "does reacting to hover on element A need to change something rendered somewhere *other than*
element A."

Open [`components/charts/DonutBreakdownChart.tsx`](../../../components/charts/DonutBreakdownChart.tsx)
line 1 and lines 47–51:

```tsx
"use client";
```

```tsx
export function DonutBreakdownChart({ segments, totalLabel }: DonutBreakdownChartProps) {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0);
  const [hoveredLabel, setHoveredLabel] = useState<string | null>(null);
  const hovered = segments.find((segment) => segment.label === hoveredLabel) ?? null;
  const hoveredPercent = hovered && total > 0 ? Math.round((hovered.value / total) * 100) : null;
```

The donut's tooltip content is *shared and swappable* across two physically separate pieces of
markup: a single floating tooltip card near the ring, and every legend row below it, both need to
know *which* segment (if any) is currently active — hovering ring segment A needs to change what's
displayed in a totally different DOM subtree (the floating card) and also change a different
sibling element's own styling (the matching legend row's background highlight). That kind of
cross-element coordination has no pure-CSS solution without much more elaborate, less-supported
tricks (modern `:has()` selectors), so the component was promoted to a Client Component holding
`hoveredLabel` as real React state — both the ring segments' `onMouseEnter`/`onFocus` handlers and
the legend rows' identical handlers read and write that one shared piece of state.

Now open [`components/charts/VerticalBucketBarChart.tsx`](../../../components/charts/VerticalBucketBarChart.tsx)
lines 50–69 — no `"use client"` anywhere in this file:

```tsx
<div
  key={datum.label}
  tabIndex={0}
  aria-label={`${datum.label}: ${formatAmount(datum.value)} (${percent}% of total)`}
  className="group relative flex h-full flex-1 cursor-default flex-col items-center justify-end gap-1 focus:outline-none"
>
  <div
    role="tooltip"
    className="pointer-events-none absolute -top-2 left-1/2 z-10 -translate-x-1/2 -translate-y-full whitespace-nowrap rounded-md border border-border bg-surface px-2 py-1 text-[10px] font-medium text-text-primary opacity-0 shadow-md transition-opacity duration-150 group-hover:opacity-100 group-focus:opacity-100"
  >
    {datum.label}: {formatAmount(datum.value)} ({percent}%)
  </div>
  <span className="text-[10px] font-medium tabular-nums text-text-secondary">
    {formatAmount(datum.value)}
  </span>
  <div
    className={`w-full rounded-t-md transition-opacity duration-150 group-hover:opacity-70 group-focus:opacity-70 ${BAR_FILL_CLASSES[datum.tone]}`}
    style={{ height: `${(datum.value / max) * 100}%` }}
  />
</div>
```

Each bar's tooltip is entirely self-contained — hovering bar N only ever needs to affect bar N's
own fill opacity and bar N's own tooltip, never anything about bar N+1 or any element outside this
one `<div>`. That's precisely the shape Tailwind's `group`/`group-hover`/`group-focus` utilities
solve with zero JavaScript: each bar column becomes a `group relative` container holding both the
bar (with `group-hover:opacity-70`) and an absolutely-positioned tooltip (with `opacity-0
group-hover:opacity-100`), coordinated entirely by the browser's own `:hover`/`:focus` pseudo-class
matching — the bar column itself carries `tabIndex={0}`, and it's that focused *group* element
`group-focus:*` reacts to, not `:focus-within` (which would instead react to focus landing on a
*descendant* of the group). The component stayed directive-free and CSS-driven — nothing about its
own logic needs anything beyond what CSS alone already provides. Worth being precise about what that
means today, though: `DashboardLiveSections.tsx` (Part 4) is the component's current caller, and that
file carries its own `"use client"` — so while `VerticalBucketBarChart` is genuinely
server-compatible and could be rendered from a Server parent elsewhere, its actual current usage is
bundled beneath that Client boundary, part of the client module graph, not executing as a Server
Component in the running app today.

> **Design patterns — Two solutions to the same coordination problem:** The donut and the bar
> chart both needed "reveal detail on hover/focus" — an identical *product* requirement — and
> landed on genuinely different *implementations* because the actual coordination shape differed.
> This is a useful general test for "does this interactive behavior need component state": if
> hovering element A only ever needs to change element A's own rendering, CSS pseudo-classes (or
> `group-*` variants for a parent/descendant relationship) are sufficient and cost nothing in
> JavaScript. The moment hovering A needs to change something about a *sibling* element B that
> isn't a CSS descendant of A, only shared component state (or, in more complex cases, a signal/
> observable) can coordinate the two. The installed Next.js docs
> (`node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`)
> cover the general Server/Client module-boundary mechanism this whole distinction rests on.

**Checkpoint:** `DonutBreakdownChart` needed `useState` and required its own `"use client"`;
`VerticalBucketBarChart` needed neither. What's the precise test for "does this interactive behavior
need component state," and how does each chart's answer map onto that test?

<details>
<summary>Reveal answer</summary>

The precise test, per this Part's own framing: does reacting to hover/focus on one element need to
change something rendered *outside* that element's own DOM subtree? For the donut, yes, in one
direction: hovering or focusing a `<circle>` needs to update a floating tooltip card that lives in a
sibling `<div>`, *and* needs to update the matching legend row's own background highlight — a
genuinely different element. (The reverse doesn't currently happen: hovering a legend row updates
the tooltip card and that row's own highlight/percent text, but nothing in the current code
conditions a `<circle>`'s own class on `hoveredLabel` — the ring segments only ever react to their
*own* `hover`/`focus` state, not to legend interaction.) Either direction of that cross-subtree
coordination is exactly what requires a shared source of truth only real component state can
provide. For the vertical bar chart, no — hovering bar N's `group` container only ever needs to
change things declared *inside* that same `group` container (its own fill, its own tooltip child) —
CSS's `group-hover`/`group-focus` selectors are purpose-built for exactly "a descendant reacts to
its ancestor's hover state," with no JavaScript required.
</details>

**Checkpoint:** If a future chart needed a bar's hover state to update a legend rendered outside
that bar's own DOM subtree (like the donut's shared state today), could that still be done with
pure CSS `group-hover`? Why or why not?

<details>
<summary>Reveal answer</summary>

Not with the `group`/`group-hover` mechanism specifically — that pattern only lets a *descendant*
of the hovered ancestor react; it has no mechanism for an unrelated sibling elsewhere in the tree
(a legend rendered in a completely different part of the DOM) to react to another element's hover
state. Modern CSS does have a theoretical answer (the `:has()` pseudo-class combined with sibling
selectors can express some cross-element reactions without JavaScript), but browser support and the
complexity of expressing "which specific bar is hovered, then style a specific matching legend row"
purely in CSS selectors would likely be more fragile and harder to read than simply reaching for the
same `useState` pattern the donut chart already uses — which is exactly why the donut chart, facing
this identical requirement today, was promoted to a Client Component rather than attempting a
CSS-only solution.
</details>

**Try it yourself:** Before looking anything up, predict, in writing, whether each of these three
hypothetical hover interactions would need shared component state (per this Part's own test — does
reacting to hover on element A need to change something *outside* A's own DOM subtree):

1. A `MetricCard` tile that reveals a full-precision number in a tooltip when hovered.
2. A table row that highlights itself when hovered.
3. A legend swatch that, when hovered, highlights *every* row in a table sharing that swatch's
   category — not just one row.

<details>
<summary>Reveal answer</summary>

(1) and (2) are both self-contained — the affected element and the hovered element are the same
element (or a descendant of it) — so both are answerable with `group`/`group-hover` alone, no state
needed. (3) is the donut-chart shape exactly: hovering the swatch needs to change *multiple other*
elements elsewhere in the DOM that aren't descendants of the swatch, so it would need shared
component state (or the same `:has()`-based CSS workaround the previous checkpoint judged more
fragile than it's worth) — the same test, applied to a new hypothetical, gives the same kind of
answer it gave for the donut and the bar chart.
</details>

## Part 6 — Hydration and pointer-event failures found by real interaction checks

Two real, user-facing bugs in this phase were found only because verification actually scripted
interaction — not by reading the code, and not by eye.

**The hydration mismatch.** `explanation.md` §3 walks through the exact failure. Adding hover/focus
tooltips to the donut chart originally wrote each ring's accessible title as ordinary multi-line
JSX:

```tsx
<title>
  {segment.label}: {formatNumber(segment.value)} ({percent}%)
</title>
```

Loading `/dashboard` in a real browser (during a scripted verification pass, by tailing the dev
server log) surfaced a genuine React error: "Hydration failed because the server rendered HTML
didn't match the client." React's hydration algorithm compares the server-rendered HTML text
content against what the client's re-render produces, and how JSX serializes text split across
multiple lines with embedded expressions — the line breaks and indentation between
`{segment.label}:`, `{formatNumber(...)}`, and `({percent}%)` become part of the text node's actual
structure — differed subtly enough between server and client output to trip the mismatch check. The
real, visible consequence for any user loading the dashboard: React discarded and fully remounted
that part of the tree client-side, a visible flash on every page load.

The fix, visible in the current file at line 72 (building the string) and line 92 (using it) —
shown as two separate excerpts since they're not adjacent lines:

```tsx
const segmentTitle = `${segment.label}: ${formatNumber(segment.value)} (${percent}%)`;
```

```tsx
<title>{segmentTitle}</title>
```

Building the text as one atomic JavaScript string, assigned to a variable *before* the JSX, and
referencing only that variable as `<title>`'s sole child, means server and client produce content
that agrees exactly — no JSX-formatting whitespace anywhere near the text node for the two renders
to disagree about.

> **System design — Hydration as an exact content-match requirement:** This bug is a concrete
> instance of the pre-study's Concept 5 — two renders that are visually indistinguishable in a
> screenshot can still fail hydration, because React's hydration check compares the server-rendered
> content/DOM against what the client's first render would produce, not pixels on screen. This
> reproduced failure was specifically about an SVG `<title>` text node splitting across multiple
> JSX expressions on separate lines — it is not a general claim that every multi-expression JSX text
> node is unsafe. Ordinary deterministic JSX text expressions hydrate correctly every day; the rule
> that actually generalizes from this bug is narrower. `plan.md`'s own invariant states it precisely
> for this codebase: any multi-segment text passed to a JSX text-content position must be built as a
> single JS expression before the return statement, never as multi-line JSX children with embedded
> expressions — a specific, narrow discipline this one reproduced failure justifies, not a blanket
> rule against multi-expression text nodes in general.

**The pointer-events trap.** `explanation.md` §4 names how this one was actually found: a scripted
Playwright hover test against a ring segment failed with a timeout, and the test tool's own
diagnostic trace named the exact blocking element — the donut's center "total" label,
`<span class="text-xl font-semibold text-text-primary">28</span>`, reported as intercepting the
pointer event before it could reach the `<circle>` underneath.

The root cause: the center-total overlay is `<div className="absolute inset-0 flex flex-col
items-center justify-center">`, and `inset-0` stretches that div across the *entire* bounding box
of its relatively-positioned parent — not just the donut's hollow center, but the full square area
the visible ring occupies too. Rendering after the `<svg>` in DOM order puts it on top in the
default stacking order, and with no `pointer-events` override, any part of its box — including the
parts sitting directly over the visible ring — captures mouse events meant for the `<circle>`
elements beneath it. (The overlay itself carries no `tabIndex`, so it was never part of the tab
order and never blocked *keyboard* focus reaching the ring segments — this was purely a
pointer/hit-testing defect, not a keyboard-accessibility one.) `explanation.md` is explicit that this was a real bug affecting real
users, not a test artifact: anyone hovering the ring in a real browser would have hit the identical
dead zone.

The fix, visible on line 99 of the current file:

```tsx
<div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
```

One class addition. Once the overlay stopped capturing events, mouse hover worked immediately —
though the *test script* still needed its own separate adjustment, switching from `.hover()`
(which targets an element's geometric bounding-box center — always the donut's empty hole for an
annulus shape, never a point on the visible stroke) to `.focus()` (which exercises the `onFocus`
handler directly, sidestepping the geometry question and testing the more important
accessibility-relevant behavior anyway).

**Checkpoint:** Walk through exactly why the JSX `<title>{a}: {b} ({c}%)</title>` written across
multiple lines produced a hydration mismatch, while the same expression built as one string
(`` `${a}: ${b} (${c}%)` ``) assigned to a variable first did not. What specifically differs between
the two at the text-node level?

<details>
<summary>Reveal answer</summary>

Multi-line JSX with several embedded expressions compiles into several *separate* text-node-
producing pieces stitched together by React's rendering machinery, and the literal whitespace
between them in the source (line breaks, leading indentation on each line) becomes meaningful input
to how those pieces get concatenated — and browsers/renderers can normalize or handle that
inter-expression whitespace slightly differently between a server-side string-rendering pass and a
client-side DOM-construction pass, especially inside an SVG `<title>` element specifically. Building
the full string in plain JavaScript first (`` `${a}: ${b} (${c}%)` ``) produces one single, already-
concatenated string value with no JSX-structural whitespace anywhere inside it — there's only one
possible way to serialize that one string, so server and client necessarily agree, because there's
no multi-piece structure left for them to disagree about.
</details>

**Checkpoint:** The pointer-events bug was discovered via a failed Playwright test, not by eye. What
specifically caught it, and what does that suggest about when automated interaction tests catch
things visual review doesn't? (This is a different question from why `.hover()` itself later needed
adjusting — keep the two separate.)

<details>
<summary>Reveal answer</summary>

Playwright's `.hover()` performs an actionability check before acting — it verifies the target
element genuinely would receive the pointer event at the point it's about to interact with, and if
some other element sits on top and would intercept it instead, Playwright's own failure trace names
that specific intercepting element. That's exactly what happened here: the trace directly identified
the center-total `<span>`'s wrapping `<div>` as the element receiving the event instead of the
`<circle>`. This is reliable, mechanical evidence, not a guess about mouse trajectories — visual
review misses this class of bug because looking at a resting-state screenshot (or even watching a
human casually mouse around the chart) reveals nothing about *which* element specifically receives a
pointer event at a *given* point; nothing about the page's rendered appearance changes because of an
invisible overlay sitting on top of an SVG ring. The general lesson: an automated check that actually
asks "would this exact point be receivable by this exact element" catches an entire class of
hit-testing defect that no amount of looking at the page, however carefully, can surface — the defect
isn't visible, it's about event routing.

A separate, secondary issue surfaced only *after* this fix: `.hover()` targets an element's
calculated bounding-box center, and for a hollow ring (an annulus), that center point is the empty
hole — never a point on the visible stroke. That's a geometric ambiguity specific to targeting an
annulus shape with a center-point-based interaction, not the reason the overlay bug was originally
caught, and not itself a defect in the application — it's what motivated switching the test to
`.focus()` instead, which exercises the `onFocus` handler directly and sidesteps the geometry
question entirely.
</details>

**Try it yourself:** Load `/dashboard` in a real browser, find the Allocation Status donut, and
using only the keyboard (Tab to move focus, no mouse), focus one legend row, then separately focus
one ring segment. Record exactly which UI regions change each time — the floating tooltip card, the
focused legend row's own background, and (per the corrected model above) whether the ring itself
visibly reacts to a *legend* row being focused. Confirm your observation matches this Part's
correction: the ring segments only ever react to their own hover/focus state, never to
`hoveredLabel` being set by a legend interaction.

## Part 7 — Grid/flex mechanics behind UploadPanel and chart-card alignment

`explanation.md` §5 opens with a warning worth taking seriously as a general debugging lesson: the
initial request described the `UploadPanel` problem as the "Choose a file…" text and "Browse"
button not being aligned "cleanly on the same horizontal row." Read literally, that implies the
row's own flex properties are wrong — but `UploadPanel.tsx`'s existing markup for that row was
already `flex items-center justify-between gap-3`, already doing exactly what a same-row-alignment
fix would produce. Tweaking that row further would have changed nothing visible; the request's own
wording pointed at the wrong mechanism.

A real screenshot of three `UploadPanel` cards side by side, each with a different-length "Required
columns" list above the drop zone, revealed the actual mechanism: that text wraps to a different
number of lines per card (a long column list wraps to three lines; short ones wrap to one), so the
drop-zone row sitting in normal document flow beneath it lands at a different vertical height in
each card — an *inter-card* misalignment across a grid row, not an *intra-row* one. Open
[`components/workflow/UploadPanel.tsx`](../../../components/workflow/UploadPanel.tsx) lines 52 and
63:

```tsx
<Card className="flex h-full flex-col gap-3">
```

```tsx
<div className="mt-auto flex flex-col gap-3">
```

`Card` gained `h-full`, letting it participate in CSS Grid's default `align-items: stretch` — every
card in a grid row now matches the tallest one's natural height. The drop-zone `<label>` and the
Sample-file `<div>` were wrapped in a new `mt-auto flex flex-col gap-3` block, pinning that specific
content to the *bottom* of the now-equal-height card regardless of how many lines the required-
columns text above it took. This is a standard "stretch the outer box, then push a specific inner
block to the far edge" pattern, and it's self-limiting in a useful way: on a narrow mobile viewport,
where the grid collapses to one column, there's no taller sibling for `h-full` to stretch against,
so the fix is inert there rather than introducing a new gap.

> **System design — CSS Grid's default cross-axis stretch:** `align-items: stretch` is CSS Grid's
> default, requiring no explicit opt-in — but it only stretches the grid *item* (the `Card` div
> itself); nothing about it automatically distributes that extra height sensibly among the item's
> own children unless the item's internal layout is also built to use it (`h-full` on the `Card`
> plus `mt-auto` on the specific child that should anchor to the bottom). The chart-card sizing bug
> (below) is the same mechanic's inverse failure mode: the outer stretch happened automatically, but
> nothing inside the shorter card was set up to use the extra space, so it just accumulated as dead
> space.

A later screenshot showed the "Allocation Status" donut card with a large blank area beneath the
donut and legend — the two chart `Card`s sit in one `grid gap-4 lg:grid-cols-2` row, and Grid's
default stretch made both cards match the taller `VerticalBucketBarChart`'s natural content height
(a subtitle line, a fixed bar area, a bucket-label row), leaving the shorter `DonutBreakdownChart`
card stretched with nothing inside it set up to fill the extra room. Open
[`components/dashboard/DashboardLiveSections.tsx`](../../../components/dashboard/DashboardLiveSections.tsx)
lines 166 and 204 — both chart bodies:

```tsx
<div className="mt-3 flex min-h-48 flex-col justify-center">
```

An explicit, *identical* minimum height (`min-h-48`, Tailwind's standard `12rem`/192px scale value,
chosen over an arbitrary bracket value to stay on the project's existing spacing scale) on both
chart bodies, with `justify-center` vertically centering whatever sits inside. Once both chart
bodies commit to the same explicit minimum height, Grid's row-stretch has little or nothing left to
stretch — the two cards are already near-equal by design, not by chance.

**Checkpoint:** The `UploadPanel` request described the problem as a same-row alignment issue, but
the real bug was a bottom-anchoring issue across a multi-card grid row. What evidence resolved that
gap, and what would have happened if the fix had been aimed at the row's `flex` properties instead?

<details>
<summary>Reveal answer</summary>

The evidence that resolved the gap was a real screenshot of the *actual, live, multi-card* page,
not the request's own verbal description — reading `UploadPanel.tsx`'s source alone would have
shown the row's flex properties were already correct, but wouldn't by itself have revealed *where*
the visible misalignment was actually coming from (a taller sibling card, not this card's own
markup) without also seeing several real cards side by side. If the fix had targeted the row's
`flex` properties as the request's wording suggested, nothing about the actual bug — cards of
unequal height, drop zones landing at different vertical positions across cards — would have
changed at all; the fix would have been a no-op, since the row itself was never broken.
</details>

**Checkpoint (corrected premise):** An earlier version of this question asked why
`align-items: stretch` "doesn't automatically make a `<Card>` visually taller unless the card itself
also has `h-full`" — that premise is inaccurate, and worth correcting explicitly before answering.
For an auto-sized direct grid item (no explicit height set), Grid's default `stretch` *already*
makes the item's own margin box fill the grid area, with no extra class required — this is the same
fact Concept 3's pre-study already states correctly. So what is `h-full` actually doing in the real
`UploadPanel.tsx` fix, and why does the *chart-card* fix additionally need `min-h-48` on the inner
body? Are those two additions solving the same problem, or two different ones?

<details>
<summary>Reveal answer</summary>

`align-items: stretch` operates on the grid *items* directly — the immediate children of the grid
container — and for an item with no explicit height set, that default stretch already sizes the
item's own margin box to match the tallest sibling's row height, automatically, with no `h-full`
needed to "activate" it. `h-full` on `Card` is reinforcing/making the intent explicit rather than
causing the stretch to happen at all; the two additions in this Part solve two genuinely different
problems, not the same one twice. `UploadPanel`'s fix (`h-full` on `Card`, `mt-auto` on the
drop-zone block) is about the card's *internal* content responding to the height it already has —
the outer box was already stretched by Grid's default, but nothing inside it was positioned to use
the extra room, so the drop-zone content stayed at the top instead of anchoring to the bottom where
it needs to sit regardless of how many lines the text above it wrapped to. The chart-card fix
(`min-h-48` on both chart bodies) solves a different problem: rather than relying on stretch to
match two chart cards' heights implicitly (letting whichever card has more natural content define
the row height, and leaving the other stretched with dead space), it gives both bodies the *same*
explicit minimum height directly, so there's little or nothing left for Grid's stretch to even need
to equalize. Neither fix is about making stretch itself happen — stretch was never the missing
piece in either bug; how the *inner* content responds to (`UploadPanel`) or preempts
(chart cards) the stretched space is what each fix actually addresses. Without `min-h-48 flex
flex-col justify-center` on the inner chart body, the extra stretched space would still appear as
blank space below the chart's natural content, exactly the original bug — the outer box being the
correct height was never in question for either fix; making the content inside it use that height
sensibly is the actual work both fixes do, each in its own component.
</details>

**Checkpoint:** The `Sample file` button wrapped onto two lines specifically in the 3-column
Inventory Allocation layout but not elsewhere. What made that particular layout trigger the bug,
and why does `min-w-0` on the caption (not the button) fix it?

<details>
<summary>Reveal answer</summary>

`explanation.md` §9 traces the mechanism precisely: the row containing the caption and the sample-
file link had neither child given an explicit sizing hint, so by default, flex children can both
shrink to fit available space — and in the narrowest layout (three `UploadPanel` cards side by
side, versus one or two elsewhere), the caption text and the button were competing for genuinely
less horizontal room than on wider pages. Without `min-w-0`, a `<span>` in a flex context can refuse
to shrink below its content's intrinsic (unwrapped) width — so instead of the caption text wrapping
onto a second line to yield space, both elements shrank together, and shrinking a two-word anchor's
available width below its content's natural single-line width is exactly what forces its own text
onto two lines. `min-w-0` on the caption specifically grants *permission* for that span to shrink
below its intrinsic width (letting its own text wrap instead), which frees enough row width for the
button — now also marked `shrink-0 whitespace-nowrap` so it never participates in the shrink
calculation at all — to keep rendering at its normal, compact, single-line size regardless of how
narrow the row gets.
</details>

**Try it yourself:** Open `/order-validation` (or any workflow page) in a real browser at desktop
width, open devtools, and inspect the three `UploadPanel` `Card` elements as a group. Most browser
devtools highlight CSS Grid containers and their item boxes on hover/selection — confirm you can see
each `Card`'s margin box already matching the tallest sibling's height *before* checking whether
`h-full` is even applied, direct visual confirmation of Concept 3 and this Part's corrected model:
stretch is automatic, not `h-full`-gated. Then inspect the drop-zone block inside the shortest card
and confirm it's the `mt-auto` child, not the `Card` itself, that's actually anchored to the bottom.

## Part 8 — Verification and scope handoff

`explanation.md` §10 records that this project has no committed run/test skill for live-browser
verification, so this phase reused the same established, one-off pattern from the prior Phase 10
session: install Playwright without saving it to `package.json` (`npm install --no-save
playwright`), run a throwaway driver script, then remove it afterward. Checking `git diff --stat
package.json` alone is not quite enough proof of "no residue" — `package.json` only records
declared dependencies; `--no-save` is specifically about *that* file, and npm has historically had
version-dependent quirks around whether an ad-hoc install leaves `package-lock.json` untouched too.
The complete check is both manifests: `git diff --stat package.json package-lock.json` showing no
trace in either is the real proof this left no residue. A stronger version of this disposable-tool
pattern for a future session: reach for an already-installed browser-automation tool if one exists,
use `npx --no-install` where the package is already cached, or use a documented temporary
environment (a scratch directory with its own `package.json`) whose cleanup doesn't depend on
remembering to diff the right files afterward. Along the way, a stray
macOS Finder-duplicated file (`cache-life.d 2.ts`, `routes.d 2.ts` — note the literal space before
"2," the signature of a Finder-created duplicate) inside `.next/types/` confused `tsc`'s module
resolution with a spurious "duplicate identifier" error — the exact same class of bug a prior
Phase 9.1 session had already hit. `rm -rf .next` (safe; it's gitignored build output) and letting
the affected command regenerate a clean build directory resolved it.

> **OS fundamentals — Filesystem duplicate files confusing a build tool:** A type-checker
> discovering source (or generated-source) files by scanning a directory tree has no way to
> distinguish an accidental Finder-duplicated file from a deliberately different one — if both
> define the same exported symbol, it reports a genuine collision, exactly as it would for a real
> naming conflict. The safe fix here specifically depended on the duplicated files living inside a
> tool-*generated* output directory rather than hand-written source — there was nothing to actually
> repair, only to delete and let the tool regenerate cleanly.

**Checkpoint:** The stray `.next/types` duplicate-file typecheck error was described as "the same
class of bug" seen in an earlier Phase 9.1 session. What's the actual mechanism connecting a macOS
Finder-duplicated file to a TypeScript "duplicate identifier" error, and why does `rm -rf .next`
fix it safely?

<details>
<summary>Reveal answer</summary>

macOS's Finder (or a cloud-sync client encountering a conflict) can silently create a copy of a
file with a modified name — typically appending a literal space and a number before the extension
(`routes.d 2.ts`) — when it detects what looks like a naming collision it needs to resolve
non-destructively. `tsc`, scanning `.next/types/` as part of Next.js's own generated type
declarations, discovers both the original and the accidental duplicate, sees that both declare the
same exported route types, and correctly reports a duplicate-identifier error — from `tsc`'s
perspective, it has no way to know one of the two files shouldn't exist at all. `rm -rf .next` is
safe specifically because everything inside `.next/` (including `.next/types/`) is Next.js's own
build output, gitignored and fully regeneratable from real source on the next build — deleting it
removes both the genuine generated files *and* the accidental Finder duplicate together, and the
next build regenerates only the genuine ones, since there was never a real source-level duplicate to
begin with.
</details>

**Checkpoint:** The sidebar's lack of mobile responsiveness was found during verification but
explicitly not fixed in this phase. What's the argument for surfacing a bug without fixing it, and
what would have to be true about the bug for "just fix it while I'm in here" to be the better call
instead?

<details>
<summary>Reveal answer</summary>

`explanation.md` §11 makes the argument directly: `SidebarNav`'s fixed `w-60` width predates this
phase entirely — Phase 10.2 only recolored it and added icons, never touched its width or added any
responsive breakpoint behavior, so the identical mobile squeeze would have existed, pixel for
pixel, with the *old* light-colored sidebar, on the same viewport, before this phase ever started.
A responsive navigation pattern (overlay drawer? bottom tab bar? icon-only rail? at what
breakpoint?) is a real feature with its own genuine design questions — exactly the kind of decision
this phase's own Part 1 non-goals list exists to keep out of an explicitly-bounded "token-only
visual polish" phase. The condition under which "just fix it while I'm in here" would be the better
call: if the bug were a trivial, unambiguous, one-line fix with no real design decision embedded in
it (unlike a responsive-nav pattern, which has several genuinely different valid shapes) — the
general principle from Part 1's pre-study applies directly here: a screenshot revealing a bug is not
itself permission to solve every problem the screenshot happens to reveal, especially when the fix
requires its own scoping conversation. This bug was later actually addressed by a dedicated,
separately-scoped piece of work (`mobile-nav-shell-responsiveness`, per this tutorial's opening
caveat) — exactly the "give it its own planning pass" resolution `explanation.md` recommends here.
</details>

**Try it yourself:** Run `npm run typecheck` and `npm run lint` — both non-mutating, safe to run
anytime — and confirm both pass clean against the current codebase. Then load `/dashboard` on a
narrow (mobile-width) browser viewport and open the sidebar navigation. Confirm what this Part's
opening caveat states: a real overlay drawer with focus management now exists (the
`mobile-nav-shell-responsiveness` work), not the fixed `w-60` squeeze this Part originally describes
as a deferred bug — direct, current proof that Part 8's own non-goals discipline led to a real,
later, separately-scoped fix rather than the issue being silently dropped.

## Full data flow: an Allocation Status segment, from saved result to a keyboard-focusable ring

1. **The value resolves, live-or-sample.** `DashboardLiveSections.tsx`:
   `const resolvedInventoryAllocation = liveInventoryAllocation ?? inventoryAllocationResult;` — a
   **Phase 12 addition**; Phase 10.2 itself never had a live/sample distinction to resolve, because
   `/dashboard` was still entirely static at Phase 10.2's time — Phase 10 (Tutorial 07) made the
   three *workflow* pages FastAPI-backed, but `/dashboard` itself kept reading Tutorial 10's static
   mock JSON straight through Phase 10.2. Session-scoped per-visitor results, and the live/sample
   distinction they require, arrived only with Phase 12 (Tutorial 12).
2. **A count is read from the resolved summary.**
   `const allocation = resolvedInventoryAllocation.summary;` then `allocation.fully_allocated_count`
   — a plain number, already computed by `src/inventory_allocation.py`'s tested pipeline (Tutorial
   04), untouched by anything this tutorial covers.
3. **The count is paired with a tone via a Tutorial 10 helper.**
   `allocationStatusTone("Fully Allocated")` (Part 4 of Tutorial 10) — this call, and the whole
   `StatusBadge` tone-mapping discipline it belongs to, predates Phase 10.2 entirely; this Part's
   only new contribution is *where else* that tone gets consumed.
4. **The tone and value become one `DonutSegment`.**
   `{ label: "Fully Allocated", value: allocation.fully_allocated_count, tone:
   allocationStatusTone("Fully Allocated") }` — passed into `DonutBreakdownChart`'s `segments` prop,
   this Part's own subject.
5. **The literal stroke class resolves.**
   `STROKE_TONE_CLASSES[segment.tone]` (`DonutBreakdownChart.tsx`) maps `"success"` to
   `"stroke-success"` — the same semantic-token pipeline Tutorial 09 Part 4 traced for `bg-accent`,
   now applied to an SVG `stroke` property instead of a `background-color`.
6. **The segment becomes keyboard-focusable, not just hoverable.** `tabIndex={0}`, `onFocus`,
   `onBlur` on the `<circle>` — a Phase 10.2 addition (Part 5/6 of this tutorial); Phase 9's
   original chart (a much simpler version, per Tutorial 10's own component-registry discussion) had
   no interaction affordances at all.
7. **Hovering or focusing the segment updates shared state.** `setHoveredLabel(segment.label)` —
   this one state update is what simultaneously drives the floating tooltip card's content *and*
   the matching legend row's highlight, the cross-element coordination Part 5 covers as the reason
   this component needed `useState` (and its own `"use client"`) at all, unlike its directive-free,
   CSS-only sibling `VerticalBucketBarChart`.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Follow `surface-inverse` from its CSS variable declaration to
both of its real consumers. Open `app/globals.css`, find `--surface-inverse`'s declaration. Open
`tailwind.config.ts`, find its mapped Tailwind config entry. Then find every real usage of
`bg-surface-inverse`/`bg-surface-inverse-hover` across `components/layout/SidebarNav.tsx` and
`components/ui/Button.tsx`. Confirm both consumers reference the identical class names, with no
component-local override of the underlying color anywhere.

<details>
<summary>Hint</summary>

Don't stop at `bg-surface-inverse` alone — `SidebarNav`'s *active* link uses `bg-accent`, not
`bg-surface-inverse`, per this tutorial's Part 2 excerpt of `SidebarNav.tsx`'s active-link classes.
Make sure your trace correctly separates the sidebar's *background* (inverse family) from its
*active-link* treatment (accent family, unrelated to this Part's token family).
</details>

**Challenge 2 — Extend** (20–30 min): Design one additional hover/focus affordance for a component
this tutorial covers, while keeping it directive-free and CSS-only wherever no shared JavaScript
state is genuinely required — apply Part 5's own test. A reasonable candidate: a hover/focus
tooltip on `MetricCard` showing the exact underlying number with full precision (useful if
`formatAmount` ever truncates or rounds a large value for display). Walk through, using Part 5's
test explicitly: does this affordance need component state, or can it be expressed with CSS alone?
Justify your answer before deciding whether `MetricCard` would need its own `"use client"`.

<details>
<summary>Hint</summary>

A single tile's own hover tooltip, revealing content only about that same tile, is structurally
identical to `VerticalBucketBarChart`'s bar tooltips — self-contained, no cross-element
coordination needed. Per Part 5's test, this should be answerable with `group`/`group-hover` alone,
with no new `"use client"` directive on `MetricCard` itself. Note precisely what that does and
doesn't guarantee, though: every one of `MetricCard`'s real current call sites (all three workflow
pages, plus `DashboardLiveSections.tsx`) is already a Client Component today, so `MetricCard` is
already part of the client module graph regardless of whether this specific affordance needs state
— staying directive-free keeps the *option* open for a future Server-rendered caller, it doesn't
change where the component actually executes right now.
</details>

**Challenge 3 — Break and fix** (30–45 min): The center-total overlay lives in
`components/charts/DonutBreakdownChart.tsx` itself (line 99) — `DashboardLiveSections.tsx` only
renders `<DonutBreakdownChart>` as a child, it doesn't contain this markup. Rather than editing the
shared component directly (it's used on the live `/dashboard`, and reverting an edit correctly
requires remembering to do so), make a reversible scratch copy: duplicate
`DonutBreakdownChart.tsx` into a throwaway file, remove `pointer-events-none` from the copy's
center-total overlay div, and view it in isolation (a scratch page, or a component-explorer setup if
one exists) rather than swapping it into the live dashboard. Predict, in writing, before testing:
what specific interaction will silently stop working, and would a plain screenshot of the
resting-state page reveal the regression? Then actually try to hover/focus a ring segment against
your scratch copy and confirm your prediction. Explain in one paragraph why a screenshot alone —
even a very careful one — may not reveal this specific class of bug. Delete the scratch copy when
done.

<details>
<summary>Hint</summary>

The resting-state page looks pixel-identical with or without `pointer-events-none` — the bug is
purely about which element *intercepts an event*, something no static image can show at all. Your
explanation should connect back to Part 6's account of how this bug was actually found: not by
looking, but by scripting an interaction (or, here, trying the interaction yourself) and watching it
fail.
</details>

For deeper exploration,
[`docs/plan/phase-10.2-portfolio-ui-polish/ai-discussion-topics.md`](../../plan/phase-10.2-portfolio-ui-polish/ai-discussion-topics.md) has all 15 prompts this
tutorial's checkpoints were woven from, organized under their original five headings (token
architecture, bugs found during implementation, dashboard content decisions, chart tooltip
implementation, and verification process/scope discipline). Feed them to an LLM *after* forming
your own answer first — the gap between what you thought and what you learn is where understanding
lands.
