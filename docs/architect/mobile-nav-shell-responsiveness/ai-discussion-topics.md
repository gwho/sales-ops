# AI Discussion Topics — Mobile Nav/Shell Responsiveness Pass (Architect Session)

## Scoping and exploration approach

1. The session used direct file reads instead of an Explore subagent. What specifically about this task made that the right call — restate the skill's own stated exception in your own words, and give a scope where the opposite call (spawning Explore) would have been correct instead.
2. `context/ui-registry.md` already documented this exact limitation as "out of scope" back in Phase 10.2. What's the value of a project explicitly writing down "known limitation, not fixing this now" rather than just leaving it undocumented and silently unfixed?
3. Language alignment surfaced four term definitions before any implementation questions were asked. Which of the four (if any) would you argue *didn't* need explicit confirmation, and why?

## The breakpoint decision

4. Walk through why choosing `md` (768px) instead of `lg` would have left the reported bug only *partially* fixed. Name the specific viewport-width band where it would still reproduce.
5. This app has no custom Tailwind breakpoints. If it did need one (say, a `2xl` cutoff for a future wide-dashboard layout), what would the decision-making process look like compared to this session's `lg`-vs-`md` question?

## The `--overlay` token decision

6. Why does `ui-tokens.md`'s "no new token without an explicit decision" rule exist at all — what failure mode does it prevent, concretely, in a project of this size?
7. `--overlay` was given the exact same HSL triple as `--surface-inverse` rather than a new value. Argue the case for giving it a genuinely different value instead — what would that buy, and what would it cost in terms of "provably drawn from the existing palette"?
8. If a future feature needed a *second* semi-transparent backdrop (say, a full-page loading overlay, not a drawer), should it reuse `--overlay`, or does `ui-tokens.md`'s "scoped to drawer/modal backdrops only" note mean that needs its own new token decision?

## The drawer-build decision (hand-rolled vs. library)

9. This project's "hand-roll everything against our own tokens" convention was set for a specific reason — shadcn's default token names collide with `ui-tokens.md`'s names. Does that same specific reason apply to a headless dialog library like Radix (which is typically unstyled)? If not, what's the actual argument against it here?
10. At what point would this project's navigation surface become complex enough (more nested menus? more items? sub-groups?) that reaching for a headless library would flip from "unnecessary footprint" to "clearly justified"?

## The plan-review correction round

11. The tab-order objection ("`-translate-x-full` alone is not enough") was caught from a written plan before any code existed. What made this catchable at plan-review time, versus needing a running implementation to discover?
12. The user offered two acceptable fixes for the tab-order problem: conditional rendering, or `inert`/`aria-hidden`. What's the strongest argument for choosing `inert` instead of the conditional-rendering approach that was ultimately implemented?
13. The "avoid claiming full modal behavior" correction is fundamentally about not overstating what the implementation does. Find another place in this same feature (or a hypothetical future one) where a similar "don't claim more than you deliver" principle could apply to an ARIA attribute, a prop name, or a doc comment.
14. The "separate desktop/mobile wrappers" correction and the tab-order correction reinforced each other. Explain concretely why trying to satisfy the tab-order fix using a *single* dual-purpose wrapper would have been harder to reason about than the two-wrapper structure that was chosen.
15. Two real accessibility bugs (tab-order, and later — during implementation, not planning — focus-entry) both trace back to the same underlying off-canvas drawer pattern. Does this suggest the plan-review round should have caught the focus-entry problem too, or is that genuinely a category of bug that only a running, tested implementation can surface? Defend your answer.

## Process and documentation

16. This work was deliberately tracked as a named entry in `context/progress-tracker.md`, not a numbered phase — following the precedent of "Sample Data Enrichment" and the mock-data pipeline reconnection. What's the actual criterion this project seems to be using to decide "numbered phase" vs. "named fix," based on the examples given?
17. The user required `/feature-docs` and named the *specific* five topics `explanation.md` had to cover, rather than leaving the scope of documentation up to the writer. What's the risk of leaving that scope undefined, especially for a feature this narrow?
18. This session produced a plan file the user rejected once (with five corrections) before approving. What does that rejection-then-approval cycle suggest about how much weight to put on a *first* draft of an architecture plan versus treating it as a genuine first offer meant to be stress-tested?
