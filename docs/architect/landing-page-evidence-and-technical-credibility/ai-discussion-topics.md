# AI Discussion Topics — Landing Page Evidence and Technical Credibility

Use these with an AI assistant (or as self-study prompts) to go deeper on the reasoning behind this
session's decisions. Grouped by concept; each question asks *why* or *how*, or probes an edge case.

## Group 1 — Evidence integrity and build-time invariants

1. Why does the evidence loader check for *exactly* two matching rows instead of *at least* two?
   Walk through a concrete future scenario where "at least two" would let a false claim ship.
2. The loader also cross-checks `summary.duplicate_orders === 2` against the row count, even though
   both numbers ultimately come from the same `validate_orders()` run. Why check the same fact twice
   from two different places in the output instead of trusting one of them?
3. What would happen — build failure, wrong content, or silent success — if `sample_data/sample_orders.xlsx`
   were regenerated in a way that removed the `SO-2026-010` duplicate entirely? Trace it through
   `scripts/generate_mock_data.py` → `lib/mock-data.ts` → `lib/content/landing-evidence.ts`.
4. This pattern (verify precisely, fail loudly on drift) mirrors `context/code-standards.md`'s
   existing rule that exhaustive edge-case coverage belongs in pytest fixtures, not sample workbooks.
   What's the common principle connecting a testing convention and a landing-page content convention?
5. Could this same invariant-checking pattern be applied to other places in the app where copy
   implicitly claims something about data (e.g. `/dashboard`'s "How This Demo Works" or `BoundaryNote`)?
   What would need to change for it to apply there too?

## Group 2 — Content ownership boundaries

6. Why does `lib/content/landing-evidence.ts` read its lookup selector (`orderId`, `errorCode`) from
   the content JSON instead of hardcoding it as a constant, even though the JSON's `orderId` value
   and the "correct" order ID are — at this moment — the same string?
7. What's the difference between "the JSON owns 100% of the prose" and "the JSON owns 100% of the
   content"? Why does this session insist on the first, narrower claim rather than the second?
8. This is the first landing component that imports from outside `content/portfolio/...json`. What
   guardrail keeps this from becoming a slippery slope where every future component reaches into
   whatever data source is convenient?
9. If a second piece of evidence were added later (say, a real payment-aging example), should it
   follow the exact same three-layer split (JSON/loader/component), or would a different shape make
   sense? What would change if there were two evidence sections instead of one?

## Group 3 — Editorial identity, real data, and why ideas were rejected

10. Compare the failure modes of three rejected ideas: a fabricated ROI percentage, an isometric hero
    mockup, and a React Flow diagram. Each was rejected, but for a different underlying reason — name
    each reason precisely.
11. Why was a standalone output table rejected even though it would also be "real data," unlike the
    isometric mockup? What's the difference between "real" and "fits this page's established identity"?
12. The "Operations Philosophy" bio-section idea wasn't rejected outright — it was flagged as needing
    the user's explicit call. What distinguishes it from the "Role Fit" section that *was* rejected
    outright in the original landing-page build? Where exactly is that line?
13. If someone proposed adding a live-updating counter (e.g. "X validations run today") to the
    landing page, which of this session's established failure categories would that fall into, and
    why?

## Group 4 — Accessibility semantics

14. Why is `role="alert"` correct for `BusinessErrorMessage` but wrong for `ValidationEvidence`'s
    quoted error message, even though both are displaying the same underlying kind of text
    (a validation error)?
15. `PersistenceNotice` was cited as an existing precedent for "not every error-adjacent UI element
    needs `role="alert"`." What's the general rule for deciding whether a piece of UI is a live event
    versus a static fact about an event?
16. Why does turning the four workflow cards into real links matter for accessibility specifically,
    given that they were already visually distinguishable and readable by a screen reader before this
    change? What was actually missing?
17. `lib/content/landing-evidence.ts` is required to never be imported into a Client Component. What
    would break — concretely — if it were?

## Group 5 — Responsive precision

18. Why was "hide the anchor links below `sm`" judged insufficient on its own, even though it
    correctly fixes the most visually obvious mobile problem?
19. Why is 320px specifically named as a required verification width instead of "test on mobile"?
    What's a viewport width where a fix could look fine but still fail at 320px?
20. The locked brand treatment uses two fixed strings with no CSS-truncation fallback. What would a
    truncation-based approach have looked like instead, and why might "two fixed strings, chosen in
    advance" be more predictable than "let the browser truncate whatever doesn't fit"?

## Group 6 — Process and session discipline

21. Three separate rounds of plan review each caught a different class of problem (data integrity,
    then scope-locking, then precision). Could a single, more thorough first pass have caught all
    three at once — or is there a reason iterative review tends to surface different categories of
    issue in sequence rather than all at once?
22. Why did this session require a `/session-docs` pass *before* implementation, rather than after —
    given that `/feature-docs` already documents what gets built, after the fact?
23. Two research agents ran in parallel before any of the six decisions were finalized, even though
    the user had already supplied a recommendation for each one. What did verifying those
    recommendations against the actual codebase change, versus just accepting them as given?
24. This plan explicitly refuses to claim live browser verification happened, because no
    browser-control tool was available in the session. What's the risk of a plan (or a person)
    reporting "verified" for something that was only checked at the code level?
