# AI Discussion Topics — Architect Sessions: Phase 9 (Reusable UI Components and Static Pages) and Phase 9.1 (Visual Alignment Fixes)

## 1. Static showcase vs. simulated live app

1. What's the general test for deciding whether a piece of "fake it for now" UI logic is a wise deferral versus wasted work that will be thrown away? Apply that test to `ReportCard`'s non-`Ready` states versus a hypothetical fake `setTimeout`-driven upload flow — why does one pass the test and not the other?
2. `UploadPanel` is explicitly described as "functional but never gates content." What's the argument for making it *fully* functional (real file picker, real filename display) rather than a purely decorative placeholder, given that Phase 9 never parses the file anyway?
3. If Phase 10 arrives and the real API turns out to need a *different* shape of loading/error state than what `ReportCard`'s prop-driven variants already model, how much of the Phase 9 work would actually be salvageable versus needing to be redesigned? What would you check first to estimate that risk before Phase 9 shipped?

## 2. Server/Client boundaries and generic component APIs

4. Walk through, mechanically, why a Server Component can pass a `string` prop to a Client Component but not a `function` prop. What specifically does "serialization" mean here, and what would have to be true of JavaScript for functions to be serializable?
5. The chosen fix was "make the whole page a Client Component." The rejected alternative was "move column definitions into small Client child components that receive only data." Under what conditions would the rejected alternative's extra file-per-table cost become worth paying — i.e., what would the page need to be doing that it currently isn't for staying a Server Component to actually matter?
6. Is there a generic table-component API design that avoids this problem entirely — i.e., a `DataTable` shape where columns never need to carry render functions as props? What would such an API look like, and what capability would it trade away to get there?

## 3. Controlled vocabularies with overloaded values

7. `"High"` means different things as `ValidOrderRow.priority` versus `PaymentAgingRow.follow_up_priority`. Can you think of another field pair in this project's contracts (`src/contracts.py`) where the same literal value might carry different meanings depending on context? How would you audit for this systematically rather than catching it one bug at a time?
8. The fix uses per-field TypeScript function signatures to make misuse a compile error. What's the equivalent technique in a language or context without a structural type system — how would you get the same safety guarantee using only runtime checks or naming conventions?
9. Is there a cost to having six separate tone-resolution functions (`severityTone`, `allocationStatusTone`, `importancePriorityTone`, `agingBucketTone`, `followUpPriorityTone`, `reportLifecycleTone`) instead of one general-purpose one? Where's the line between "appropriately specific" and "unnecessary proliferation" here?

## 4. Tailwind's static scanning model

10. Explain, in your own words, why Tailwind's approach (scan source text for literal class-name substrings) is fundamentally different from how a CSS-in-JS library like styled-components resolves dynamic styling. What would Tailwind have to become to support `` `bg-${tone}` `` safely?
11. The fix pattern is a literal `Record<Tone, string>` object per component. If five components each need their own copy of a similar-shaped map, at what point does the duplication become a liability worth consolidating — and what would you lose by consolidating (e.g. into one shared `TONE_CLASSES` export) that the current per-component maps preserve?
12. Suppose a future component genuinely needs a class name built from *two* independent dynamic values (e.g. a tone and a size). How would you extend the literal-map pattern to cover that without falling back into string interpolation?

## 5. Type-only imports and dependency coupling

13. What's the practical difference, if any, between `import type { Tone } from "./StatusBadge"` and `import { type Tone } from "./StatusBadge"` (inline type modifier vs. import-type statement)? Does either change the runtime-erasure guarantee discussed in `discussion.md` §5?
14. The session concluded a type-only import doesn't create "real" coupling because it's erased at compile time. Is there a *type-level* coupling cost that still matters even though there's no runtime cost — e.g., what happens to the chart components if `StatusBadge.tsx`'s `Tone` union gains a sixth value?
15. If this project eventually wants a stricter rule like "components under `components/charts/` may never import anything, even types, from `components/workflow/`," what would the actual enforcement mechanism be (lint rule, dependency-cruiser config, code review checklist)? Is that rule worth adopting given what this session found?

## 6. Design token collisions and third-party component libraries

16. The shadcn/project token collision is specifically about CSS custom property *names*. If shadcn had used a prefixed convention (e.g. `--shadcn-accent` instead of `--accent`), would the "hand-write everything" decision still have been the right call? What would change?
17. What's a concrete way to *detect* this class of collision automatically, before it becomes a build-time surprise — e.g., diffing the token names a new dependency's generator would write against the project's existing `tailwind.config.ts` color keys?
18. This project chose to never run the generator at all. A different project might choose to rename its own tokens to avoid the collision instead. What factors would push a team toward one resolution over the other?

## 7. Defensive math and zero-value edge cases

19. `DonutBreakdownChart`'s zero-guard renders a neutral ring with "0" in the center; `VerticalBucketBarChart`'s renders an `EmptyState` caption. Propose a third scenario (e.g. a horizontal stacked bar, a sparkline) and reason about which of these two treatments — or a third one — would communicate "zero" most honestly for that shape of chart.
20. These guards were written proactively, against data that never actually triggers them with the current mock fixtures. What's the argument that this is *good* engineering practice rather than premature optimization for a case that "will never happen"? What would change your answer if this were, instead, a one-off internal script rather than a portfolio-facing UI component?

## 8. Component folder taxonomy

21. `components/tables/` holds `MiniBar`, `SegmentedBar`, and `AgingBucketBars` — all "table-adjacent" visualizations — while `components/charts/` holds the two whole-chart cards. Where would you put a hypothetical new component that's a full-width chart *inside* a table's expanded row (neither purely table-adjacent nor a standalone card)? What does your answer reveal about the limits of a two-bucket taxonomy?
22. Folder structure was described as "a promise about what you'll find inside it." What's a lightweight way to keep that promise honest over time in a fast-moving codebase, short of a formal architecture review before every new component?
