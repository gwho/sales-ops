# Discussion — Phase 10.2: Portfolio UI Polish

A deeper teaching record of the reasoning behind this planning session, for a reader who
wasn't there and has no memory of the conversation. Where `decisions.md` states *what* was
decided, this file explains the underlying mechanics, the alternatives that were considered
and rejected, and what would go wrong if the alternative had been chosen instead.

## Why a "token-only" polish pass is a real architectural constraint, not just a style note

This project's `context/ui-tokens.md` states, almost as a warning: "Light theme only. Do
not add or rename tokens without a token-change decision." That single sentence is why this
whole session existed as an `/architect` planning pass rather than a quick "make the
sidebar dark" edit. Adding a dark surface to an app whose entire token system was designed
around one light `background`/`surface` pair is not a CSS tweak — it's an addition to the
single source of truth that every component in the app reads from. If a future component
reached for `bg-slate-900` directly instead of a token, it would work visually and then
silently drift the moment someone tuned the "real" dark tone — the token discipline exists
specifically to prevent that class of bug. That's why every decision in this session routes
through `app/globals.css` → `tailwind.config.ts` → `context/ui-tokens.md`, in that order,
rather than touching component class names directly with ad hoc values.

## HSL variables, and why the new tokens reuse existing hues instead of inventing new ones

The project's colors are stored as HSL *channel triples* in CSS custom properties (e.g.
`--text-primary: 222 47% 11%`), consumed via `hsl(var(--text-primary))`. This indirection is
what makes "semantic tokens" possible: components never see a color value, only a name
(`text-text-primary`), so the actual color can be retuned globally by editing one variable.

The new `--surface-inverse: 222 47% 11%` deliberately reuses the exact same hue/saturation/
lightness as the existing `--text-primary`. This is a small but real design move: rather
than picking an arbitrary "looks navy enough" value, the plan noticed that this palette
*already contains* a vetted dark navy — it's just currently only used as *text* color on
light backgrounds. Turning that same value into a *fill* for the sidebar means the new dark
surface is provably part of the same design system, not a new hue introduced by feel. The
same logic applies to `--text-on-inverse: 0 0% 100%` reusing `--text-on-accent`'s pure
white — white text already exists in this palette (for text on the blue accent button), so
reusing it for text on the new dark navy surface is consistent rather than coincidental.

This is a useful general habit: before adding a new design token, check whether the
palette already contains an unnamed version of what you need under a different semantic
role. Reusing the *value* while giving it a new *name* keeps the palette small without
forcing two visually different things to share one semantic name.

## Why the exact shape of the Tailwind config keys was worth a correction

Tailwind color config supports two shapes for a family of related colors: nested objects
(`{ surface: { DEFAULT, muted, subtle } }` → `bg-surface`, `bg-surface-muted`,
`bg-surface-subtle`) or flat sibling keys (`{ "text-primary": ..., "text-secondary": ... }`
→ `text-text-primary`, `text-text-secondary`). This project's existing config uses *both*
shapes for different reasons: background/border families are nested because they share a
literal visual relationship (a surface and its muted/subtle variants), while text colors
are flat because "primary" and "secondary" text aren't variants of one base color so much
as independently-named roles.

The first plan draft didn't specify which shape the two new families should use. On review,
the user pinned this down precisely: `surface-inverse` nested (because `hover` genuinely is
a state-variant of the base surface color, same relationship as `surface`/`surface-muted`),
but `text-on-inverse`/`text-on-inverse-muted` flat (because they're two independently-named
text roles, matching how `text-primary`/`text-secondary` are structured, not a base+variant
relationship). Getting this wrong wouldn't cause a build error necessarily — Tailwind would
happily generate *some* class name from whatever shape was given — but it could generate an
unexpected one (e.g. nesting the text tokens might produce `text-text-on-inverse` and
`text-text-on-inverse-muted` correctly, or might not, depending on exactly how the nested
object is shaped), and "unexpected class name that silently doesn't match what every
component file references" is a categorically annoying bug to track down, because it fails
at the CSS level (missing utility class) not the TypeScript level (no compile error). Being
explicit about the exact key shape up front converts a class of runtime-visual bug into a
non-issue.

## The real bug in UploadPanel, and why "read the code" beat "read the request"

The user's original request described the problem as an alignment issue *within* a single
upload card's file-picker row ("align the 'Choose a file...' area and 'Browse' button
cleanly on the same horizontal row"). Read literally, that would suggest the row's own flex
properties were wrong. Reading the actual `UploadPanel.tsx` source showed the row was
already `flex items-center justify-between` — correct, already doing exactly what the
request asked for in isolation.

The screenshot the user then provided of the real, rendered Inventory Allocation page
revealed the actual mechanism: three `UploadPanel` cards sit side by side in a grid. Each
card's "Required columns" text is a different length (Orders File's column list is much
longer than Product Master's or Inventory's), so it wraps to a different number of lines.
Since the drop-zone row sits directly below that text in normal document flow, and nothing
was anchoring it to a fixed position, the drop-zone naturally starts lower in cards with
longer required-columns text and higher in cards with shorter text — an *inter-card*
vertical misalignment, not an *intra-row* one.

This is a common category of UI bug: a component that looks correct in isolation (one card,
one row, one browser tab open on just that component) but looks broken only when several
instances sit next to each other with genuinely different content lengths. It's also a
reminder that a bug report's *description* of the symptom and the *actual mechanism*
sometimes diverge — the fix here (bottom-anchoring via `h-full` + `mt-auto`) touches
completely different CSS properties than the fix implied by the literal request wording
(row alignment), and only reading the component source plus a real screenshot revealed
that.

## CSS Grid's row-stretch default, and why `h-full` + `mt-auto` is the right tool

By default, CSS Grid's `align-items` is `stretch` — grid *items* (the direct children of a
`grid` container) are stretched to fill the height of their row automatically, unless
something inside them opts out. But a `<Card>` inside a grid cell won't visually "reach"
that stretched height unless *it itself* is told to fill its container — hence `h-full` on
the `Card`. Once the `Card` fills the (now-equal) row height, its own children are laid out
in normal flow from the top — which is why a second step is needed: `mt-auto` on the wrapper
around the drop-zone + Sample-file block pushes *that specific block* down to the bottom of
the now-taller card, while the required-columns text above it stays anchored at the top.

The combination — outer stretch (`h-full`) + inner "push to the far edge" (`mt-auto` inside
a flex column) — is a standard pattern for "pin this to the bottom of a variable-height
container," and it's *self-correcting*: it only does anything when there's a taller sibling
to stretch to. On a narrow (mobile) viewport, where the grid collapses to a single column,
there's no multi-card row to stretch across, so `h-full` has nothing to stretch to beyond
the card's own natural content height — meaning the fix should be inert on mobile, not
introduce a new gap. This is exactly the kind of claim ("this fix has zero effect on
mobile") that's worth verifying in a real browser rather than trusting from the CSS
mental model alone, which is why it's called out explicitly as a live-browser check rather
than assumed correct from reasoning about `align-items: stretch` in the abstract.

## Why redesigning MetricCard's internals, not just its grid wrapper, was accepted despite touching ~15 call sites

There were two ways to make KPI tiles "more square": change the grid that wraps them
(fewer, wider columns → taller-looking cells by proportion) or change the card's own
internal layout (restructure where the icon, value, and label sit, and give the card a
fixed minimum height). The first is objectively lower-risk — it's a change to *page* files,
each independently, with no shared-component blast radius. The second changes one
component's internals that ~15 separate call sites across 4 pages all depend on.

The reason the riskier option was chosen anyway is that `MetricCard`'s *props* don't change
— every call site still passes the same `label`/`value`/`icon`/`tone` and gets the same
data rendered, just arranged differently inside the card. This is the core reason component
reuse is valuable in the first place: because the internal layout is encapsulated behind a
stable prop contract, a purely cosmetic internal change *cannot* introduce a data or
behavior bug at any call site — the blast radius of "this looks different" is total, but the
blast radius of "this breaks something" is close to zero, verifiable by the fact that
`npm run typecheck`/`build` would fail immediately if any call site needed a different prop
shape. Contrast this with the grid-only alternative: it would have required editing 6+
separate page-level grid class strings by hand, each independently, with no shared
enforcement that they end up consistent with each other — a classic case where the "safer
looking" option is actually more error-prone in practice, because it has no single point of
truth.

## Why "reference screenshot" was treated as inspiration, not spec

The reference dashboard screenshot the user provided includes a search bar, an "Upload
Orders" header action, a notification bell, a logo icon-badge, and live "Synced 2 min ago"
freshness copy — none of which exist in this project's actual output contracts (`src/`
never computes a "last synced" timestamp; there's no cross-workflow search). This project's
`CLAUDE.md` has a standing rule for exactly this situation: reference/Figma material is
"guidance, not final scope," and every UI element must still map back to a real Python
output contract or a documented derived display value. So the plan explicitly calls out,
as an *assumption* rather than a decision, which parts of the reference are adopted
(dark sidebar, compact KPI tiles, paired tables, button hierarchy — all achievable with
existing contract data) and which are not (anything implying a live sync/search feature the
backend doesn't have). This is a recurring discipline in this project: a picture of a nicer
dashboard is not itself permission to add UI surfaces the data layer can't actually back.

## Why documentation timing (during vs. after implementation) is itself a decision worth stating

It would be easy to treat "update the docs" as a single undifferentiated cleanup step at
the end. The plan instead splits it in two, based on what each document *asserts*:
`ui-tokens.md` and `ui-registry.md` describe *current styling reality* — they should be
accurate the moment the corresponding code exists, updated alongside it, the same way a
docstring should match the function it documents. `progress-tracker.md` and
`build-plan.md`, by contrast, assert *a phase is complete and verified* — a claim that can
only be true once verification has actually run. Writing "Phase 10.2 complete" before
`npm run build`/browser verification pass would be recording an intention as if it were a
confirmed fact, which every prior phase in this project's history was explicit about
avoiding (each phase's progress-tracker entry cites its own test/build counts as evidence,
not just a checklist tick). The distinction matters because these two document types answer
different questions for a future reader — "what does this look like" vs. "can I trust that
this shipped and works" — and conflating their update timing would make the second question
unreliable.
