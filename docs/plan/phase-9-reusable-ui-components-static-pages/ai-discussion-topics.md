# AI Discussion Topics — Feature phase-9-reusable-ui-components-static-pages: Reusable UI Components and Static Pages

## 1. Server/Client component boundary

1. Walk through exactly what happens, step by step, when Next.js tries to serialize `ERROR_COLUMNS` (with its `render` functions) to send from a Server Component to `DataTable`. Why does the error happen at build/prerender time rather than at runtime in the browser?
2. `dashboard` and `reports` stayed Server Components because they never build a `DataTable` columns array. What is the first new feature you could imagine adding to `dashboard` that would force it to become a Client Component too — and is there a way to add that feature without paying that cost?
3. The plan.md invariant suggests an alternative fix that wasn't used: move each page's column definitions into a small dedicated Client child that receives only serializable `data`. Sketch what `ValidationErrorsTable.tsx` would look like under that approach. What would it cost in file count, and what would it buy back in "Server Components by default" purity?
4. If a future page needed to fetch data with `async`/`await` inside a Server Component (e.g. reading a file with `fs.readFileSync` at request time) *and* also needed a sortable `DataTable`, what's the actual pattern to get both — a Server Component parent that does the fetch, passing only plain data down to a small Client child that owns the column defs?

## 2. StatusBadge and the tone-mapping design

5. `importancePriorityTone` and `followUpPriorityTone` both take a `"High"` value but return different tones (`warning` vs. `danger`). What would a bug look like if a future developer accidentally called the wrong helper for the wrong field — and would TypeScript catch it, or only a visual review?
6. Why does `StatusBadge` not just accept the raw contract field name (e.g. `"severity"`) and a value, then do the field→tone lookup internally? What specific ambiguity in this project's contracts makes that design worse than the explicit-helper-per-caller approach that was chosen?
7. `RemainingInventoryRow.reorder_alert === "No"` renders plain text instead of a badge. Is "no badge for the non-alerting case" a good general rule for this design system, or does it just happen to work here because there's no interesting "OK" status to call out? Would Order Validation's `severity` field want the same treatment for a hypothetical "no errors" case?
8. The mapping table lives in `context/ui-registry.md`, not in code comments or a shared constants file that both `StatusBadge.tsx` and the pages could import from. What's the risk of the registry table silently drifting from the actual `switch` statements in `StatusBadge.tsx` over time, and how would you catch that drift?

## 3. The shadcn hand-write decision

9. `components.json` still has `baseColor: "slate"` even though `npx shadcn add` is never supposed to run. Is leaving that config in place a trap for a future session that forgets this project's rule, or is it harmless because nothing reads it unless the CLI is invoked? Would you delete it, or leave it with a comment?
10. The verification pass used `git diff app/globals.css` returning empty as proof the collision never happened. What's a scenario where that check would pass even if a real problem had been introduced — i.e., what does an empty `globals.css` diff *not* tell you?
11. If Phase 10 needs a genuinely complex primitive — say, a `Select` with keyboard navigation and portal-rendered options — does hand-writing still make sense, or is that the point where the shadcn-CLI-plus-manual-token-cleanup tradeoff flips in the other direction?

## 4. The static showcase decision and its edges

12. `ReportCard`'s `Needs Input`/`Not Generated`/`Processing` states have no current call site anywhere in the app. How would you verify they actually render correctly (not just typecheck) before Phase 10 wires them up for real — write a quick throwaway page, a Storybook-style story, or something else?
13. `UploadPanel`'s "Sample template" button is permanently disabled with an explanatory `title`. Is a disabled button with a tooltip a good pattern for "not implemented yet" in a portfolio project meant to be reviewed by a hiring manager, or does it read as an unfinished feature rather than an intentional one? What's the alternative?
14. `WorkflowStepper` always renders `currentStep={steps.length - 1}` — the last step as current. If Phase 10 wires up a real (if fast) API call, does the stepper need to become a Client Component at that point, or can the parent page still compute the correct `currentStep` server-side per request and pass it down as a prop?

## 5. DataTable design and verification methodology

15. `DataTable`'s sort comparator does `va < vb ? -1 : va > vb ? 1 : 0` directly on whatever `sortValue` returns. `AllocationResultRow.priority` is sorted this way as a string (`"High" < "Low" < "Normal"` alphabetically) rather than by actual importance rank. Is that a real bug worth fixing now, or acceptable because the mock data only has one row per table so it's never visibly wrong yet?
16. The content-verification route checks grepped for specific strings like `"OV-003"` in the response body. What would make that check *not* actually prove the page works — i.e., what's a way a page could contain the string `"OV-003"` in its HTML without the Validation Errors table actually being correct?
17. The Figma-vocabulary grep for `"—"` returned several false positives (optional-field placeholders). Is a blunt string grep still worth keeping in the verification routine given how many false positives it produces, or would a more targeted check (e.g. grepping only inside `StatusBadge`/tone-helper call sites) be worth writing instead?
