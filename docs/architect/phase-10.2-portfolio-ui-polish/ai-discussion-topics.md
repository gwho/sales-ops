# AI Discussion Topics — Phase 10.2: Portfolio UI Polish

Questions for deeper exploration, grouped by concept. Each probes why a decision was made
the way it was, or what would break under a different choice.

## Design Tokens & Theming

1. Why does this project store colors as HSL *channel triples* in CSS custom properties
   (`--text-primary: 222 47% 11%`) instead of storing full `hsl(...)` strings or hex codes
   directly? What does splitting the channels out enable that a single string value
   wouldn't?
2. `--surface-inverse` was deliberately set to the exact same HSL value as the existing
   `--text-primary`. What would be lost if instead a brand-new, unrelated navy value had
   been chosen? What would be lost if, conversely, `--surface-inverse` had simply *been*
   `--text-primary` reused directly, with no new variable at all?
3. This is described as adding a token "family" (`surface-inverse` + `surface-inverse-hover`
   + `text-on-inverse` + `text-on-inverse-muted`) rather than a single new color. Why do
   hover and muted states need their own tokens instead of being computed at the component
   level with something like `opacity-80`?
4. The plan explicitly avoids adding `--surface-inverse-active` and `--border-inverse`,
   reusing existing `--accent`/`--text-on-accent` and dropping the border entirely instead.
   What's the general principle for deciding "reuse an existing token" vs. "this genuinely
   needs a new one"?
5. If a second component (not the sidebar or the dark button) needed a dark background six
   months from now, should it reuse `--surface-inverse` directly, or should that trigger a
   fresh token-change decision? What would you check before answering?

## Tailwind Config Shape & Class Generation

6. Why does `surface-inverse` use a *nested* config object (`{ DEFAULT, hover }`) while
   `text-on-inverse`/`text-on-inverse-muted` use two *flat* sibling keys, when both are
   "a base value plus a variant"? What's the actual distinguishing factor?
7. What category of bug would result from getting this config shape wrong — would it be a
   TypeScript compile error, a Tailwind build error, or something else? Why does that
   category of failure make it more important to get right up front rather than "fix it
   after the fact"?
8. The project's rule is "no raw Tailwind palette classes, no hardcoded hex." Why does that
   rule specifically target *color* values and not, say, spacing (`p-4`) or typography
   (`text-sm`)? Is there a version of this rule that would make sense for spacing too?

## CSS Grid & Flexbox Layout Mechanics

9. Explain, in your own words, why `align-items: stretch` (CSS Grid's default) alone
   doesn't make a `<Card>` visually taller unless the card itself also has `h-full`. What's
   the difference between "the grid cell is tall" and "the element inside it is tall"?
10. Why does the `mt-auto` fix for `UploadPanel` need to be scoped to *just* the drop-zone +
    Sample-file wrapper, rather than applied to the `Card` itself or to every child?
11. The plan predicts this fix will be a no-op on mobile (single-column stack) but says to
    verify that in a real browser rather than trust it. What's a concrete way this
    prediction could turn out to be wrong in practice?
12. `MetricCard`'s redesign gives it a fixed/min-height so a row of tiles aligns regardless
    of value length. What CSS property or properties would you reach for first, and what
    happens if a future `value` prop is unexpectedly long (e.g. a 7-digit currency amount)?
13. The dashboard's KPI grids move to `grid-cols-2 sm:grid-cols-3 lg:grid-cols-4`, capping
    at 4 columns so a 6-tile group wraps to two rows. Why is "wrap to two rows" considered
    better here than "shrink each tile to fit 6 across," given the stated design goal?

## Component Reuse & Blast Radius

14. `MetricCard`'s internals changed but its props (`label`/`value`/`icon`/`tone`) didn't.
    Why does that distinction mean `npm run typecheck`/`build` passing is meaningful
    evidence that no call site broke, even though there are ~15 call sites and none of them
    were individually reviewed?
15. Contrast the "restructure the shared component" approach with the rejected "grid-only
    retune" alternative, which would have edited each page's grid classes independently.
    Which approach has a single point of truth, and why does that matter for future
    consistency (e.g., if someone wants to tweak tile spacing again in Phase 11+)?
16. The plan scopes the new `dark` button variant to exactly two usages (Download Report,
    Sample file) and explicitly excludes `ReportCard`'s "Go to workflow" link. What would
    go wrong, concretely, if `dark` had instead been applied to "every button that isn't
    primary"?

## Accessibility & Contrast

17. Why can a disabled button at `opacity-50` look "clearly inert" on a light `secondary`
    background but risk looking "clickable but greyed" on a solid dark `surface-inverse`
    background, even though the opacity value is identical in both cases?
18. `--text-on-inverse-muted` reuses `--text-muted`'s exact HSL value (`215 20% 65%`), a
    lightness tuned for legibility *on a light surface*. Why might the same lightness value
    not automatically carry over to being legible on a much darker background — what's the
    actual visual property that matters here, and how would you measure it rather than
    eyeball it?
19. The plan calls for a live-browser check of the sidebar's muted text contrast rather than
    computing a contrast ratio in advance. What tool or method would give you a more
    rigorous answer than "it looks fine to me"?

## Reference Material vs. Scope Discipline

20. The reference screenshot included a search bar, a "Synced 2 min ago" freshness label,
    and a notification bell — none of which were adopted. What's the test this project uses
    to decide which parts of a visual reference are in scope and which aren't?
21. If a future reference screenshot showed a feature that *could* be built from existing
    output-contract data (e.g., a search box that filtered already-loaded workflow results
    client-side), would that change the answer? Why or why not?

## Documentation & Process Discipline

22. Why does `ui-registry.md`/`ui-tokens.md` get updated *during* implementation while
    `progress-tracker.md`/`build-plan.md` gets updated only *after* verification passes?
    What's the difference in what each document is claiming to be true?
23. What's a scenario where updating `progress-tracker.md` *before* running
    `npm run build`/live-browser checks could actively mislead someone reading it later
    (e.g., in a future session's `/remember restore`)?
