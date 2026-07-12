# AI Discussion Topics — Feature phase-10.2-portfolio-ui-polish: Portfolio UI Polish

## Token architecture

1. Why does `surface-inverse` use a nested Tailwind config object (`{ DEFAULT, hover }`) while `text-on-inverse` and `text-on-inverse-muted` use two flat sibling keys, when both are arguably "a base value plus a variant"? What's the actual distinguishing rule?
2. `--surface-inverse` was set to the exact same HSL value as the pre-existing `--text-primary`. What would be lost if a brand-new, unrelated navy value had been chosen instead? What would be lost if `--surface-inverse` had simply *been* `--text-primary`, reused directly with no new variable?
3. The `dark` `Button` variant and `SidebarNav` share one token family instead of two. Walk through a concrete scenario, six months from now, where someone tweaks `--surface-inverse-hover` for the sidebar only — what protects the `dark` button from silently going out of sync, and what would happen if the two had used separate token families instead?

## Bugs found during implementation

4. Walk through exactly why the JSX `<title>{a}: {b} ({c}%)</title>` written across multiple lines produced a hydration mismatch, while the same expression built as one string (`` `${a}: ${b} (${c}%)` ``) assigned to a variable first did not. What specifically differs between the two at the text-node level?
5. The pointer-events bug (the donut's center-total overlay blocking hover on the ring) was discovered via a failed Playwright test, not by eye. Why might this bug have been easy to miss in ordinary manual browser testing, and what does that suggest about when automated interaction tests catch things visual review doesn't?
6. The `UploadPanel` request described the problem as a same-row alignment issue, but the real bug was a bottom-anchoring issue across a multi-card grid row. What evidence (reading the component source vs. reading the screenshot) resolved that gap, and what would have happened if the fix had been aimed at the row's `flex` properties instead?
7. Explain why `align-items: stretch` (CSS Grid's default) doesn't automatically make a `<Card>` visually taller unless the card itself also has `h-full`. Why does the chart-card fix need *both* `h-full`-style participation in row-stretch *and* an explicit `min-h-48` on the inner body — wouldn't one or the other be enough?
8. The `Sample file` button wrapped onto two lines specifically in the 3-column Inventory Allocation layout but not elsewhere. What made that particular layout trigger the bug, and why does `min-w-0` on the caption (not the button) fix it?

## Dashboard content decisions

9. The dashboard KPI consolidation removed real data (9 KPIs) from `/dashboard`, not just restyled it. What's the specific condition the user gave that made this acceptable, and how would you verify that condition still holds if a workflow's summary grid changes in the future?
10. Why does `/dashboard`'s Overview row stay capped at 5 columns while the three workflow pages' own summary grids each fit their own count (4, 5, or 6)? What would break, conceptually, if the same "cap at 4" rule had been kept for both?
11. The `SegmentedBar` (Valid vs. Invalid orders) was dropped rather than moved elsewhere. What's the argument that its information is now redundant, and under what future change would that argument stop holding?

## Chart tooltip implementation

12. `DonutBreakdownChart` needed `useState` and became a Client Component; `VerticalBucketBarChart` didn't and stayed a Server Component. What's the precise test for "does this interactive behavior need component state," and how does each chart's answer map onto that test?
13. If a future chart needed a bar's hover state to update a legend rendered outside that bar's own DOM subtree (like the donut's shared state today), could that still be done with pure CSS `group-hover`? Why or why not?

## Verification process and scope discipline

14. The stray `.next/types` duplicate-file typecheck error was described as "the same class of bug" seen in an earlier Phase 9.1 session. What's the actual mechanism connecting a macOS Finder-duplicated file to a TypeScript "duplicate identifier" error, and why does `rm -rf .next` fix it safely?
15. The sidebar's lack of mobile responsiveness was found during verification but explicitly not fixed in this phase. What's the argument for surfacing a bug without fixing it, and what would have to be true about the bug for "just fix it while I'm in here" to be the better call instead?
