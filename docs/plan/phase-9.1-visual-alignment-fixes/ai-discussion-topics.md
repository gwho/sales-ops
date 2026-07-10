# AI Discussion Topics — Feature phase-9.1-visual-alignment-fixes: Visual Alignment Fixes

## 1. The sidebar height bug and how it was found

1. Walk through, step by step, why `SidebarNav`'s `h-screen` combined with `AppShell`'s `flex min-h-screen` produced a sidebar that visually "ends" partway down the page instead of an error or a crash. Why does this specific combination fail silently rather than loudly?
2. The fix caps the whole shell to `h-screen overflow-hidden` and makes `<main>` the only internally scrolling element. What would break if a future page needed the *whole document* to scroll (not just `<main>`) — e.g. a very tall single-column marketing-style page? Would that page need a different layout entirely?
3. This bug was invisible to a source-only code read and only surfaced by grepping the real compiled HTML output. What's another category of bug in this codebase that a source read would miss but a rendered-output check would catch? Is there a way to make that check automatic (e.g. a lint rule or a Playwright assertion) instead of manual?
4. The fix pattern was confirmed against the original Figma prototype's own root layout (`flex h-screen overflow-hidden`). Suppose the Figma prototype had gotten the pattern wrong too — how would you have caught that, given the prototypes are explicitly "visual reference only, not source of truth"?

## 2. Filtering architecture: composition over a growing `DataTable`

5. `FilterToolbar`/`FilterSelect` filter the array before it reaches `DataTable`, rather than `DataTable` accepting filter predicates directly. What's a concrete scenario where this composition choice would start to feel awkward — e.g. if two different tables on the same page needed to share one filter's state?
6. Each page currently re-implements its own `useMemo` filtering logic (severity check, priority check, search substring match) slightly differently across `order-validation`, `inventory-allocation`, and `payment-aging`. At what point would this duplication be worth extracting into a shared `useTableFilter` hook, and what would that hook's signature need to look like to cover all three pages' slightly different filter shapes (single-field vs. multi-field, with vs. without search)?
7. `DataTable`'s `EmptyState` fallback fires identically whether the underlying array is genuinely empty or just filtered to zero rows — the *page* decides which `emptyTitle`/`emptyDescription` to pass based on `hasActiveFilters`. What happens if a page forgets to make that distinction and always passes the "genuinely empty" copy? Is that a bug a type system could catch, or only a review?

## 3. Tone reuse and the chart components

8. `DonutBreakdownChart` and `VerticalBucketBarChart` only import the `Tone` *type* from `StatusBadge.tsx`, never its tone-resolution functions. Trace exactly what would go wrong (or wouldn't) if a chart component started importing `allocationStatusTone` directly and calling it internally instead of receiving `tone` as a prop.
9. The literal `Record<Tone, string>` class maps (five of them now, across `Badge`, `MiniBar`, `SegmentedBar`, and the two chart components) are a defense against Tailwind's static class scanner missing dynamically-built class names. Where exactly does Tailwind's scanner look for class names, and why does a template literal like `` `bg-${tone}` `` fail while `` `w-full rounded-t-md ${BAR_FILL_CLASSES[tone]}` `` succeeds?
10. If a sixth component needed tone-based styling tomorrow, would you add a sixth literal `Record<Tone, string>` map, or is there a point where the five existing maps should be consolidated into one shared source (accepting the tradeoff of an extra import) to prevent the five maps from drifting apart if a token's color ever changes?

## 4. Zero-value guards and defensive rendering

11. `DonutBreakdownChart`'s zero guard renders a full neutral ring with center text `"0"`; `VerticalBucketBarChart`'s zero guard renders an `EmptyState` caption instead of bars. Why are these two different treatments appropriate for their respective charts, rather than using the same pattern for both?
12. These guards were added proactively — during a design review, not because the app ever actually hit a zero-total case with the current mock data. Is that the right call for a portfolio project with fixed mock data, or is it premature defensiveness? What's the argument for writing this guard now versus waiting until Phase 10 brings real, variable data that could actually be all-zero?

## 5. Derived aggregates and currency-neutral formatting

13. `amountByAgingBucket()` and `PaymentAgingSummary.aging_bucket_counts` now coexist — one an amount, one a count, both keyed by the same 5 buckets. What's the risk of a future developer building a new visualization that accidentally mixes the two (e.g. sorting bars by `aging_bucket_counts` but labeling them with `amountByAgingBucket()`'s values)? Is there a naming or typing convention that would make that mistake harder to make?
14. The subtitle wording was changed from `"Total Outstanding: $165,000.00"` to `"Outstanding amount by bucket"` specifically to avoid implying USD. If Phase 10's real API integration eventually does add a `currency` field to invoice data, what would need to change across `formatAmount()`, the draft-message rendering (which already handles currency per-invoice, per Phase 5's decision), and this chart's subtitle to correctly show mixed-currency totals rather than just summing raw numbers across different currencies?
15. Every new derived aggregate this phase ("Gap to Reorder Point," "Outstanding amount by aging bucket") was added to `context/ui-contract-plan.md` before being used in a component. What would you check, as a reviewer, to confirm a *new* derived aggregate genuinely satisfies the "aggregation for visualization, not new business interpretation" boundary this project's documentation draws — versus one that's quietly invented a recommendation the Python core doesn't actually produce?
