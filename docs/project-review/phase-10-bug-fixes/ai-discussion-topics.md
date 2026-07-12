# AI Discussion Topics: Phase 10 Bug-Fix Cycle

## Error Handling as an Architectural Boundary

1. Why is it not sufficient to catch a business exception "somewhere" in the request lifecycle — why does it matter specifically *which* function's try/except catches it?
2. `backend/uploads.py` catches exceptions from the file-*loading* step; `inventory.py`'s `_run_allocation` now separately catches exceptions from the *computation* step. Why wasn't the fix to just move all exception handling into one wide `try` around the entire request?
3. `validate_orders()` never raises `MissingColumnsError`/`InvalidOrderDataError` — it returns error rows in its result envelope instead. Why does the codebase use two different error-reporting mechanisms (exceptions vs. result-envelope rows) for what might look like "the same kind of problem," and how do you decide which one a new business function should use?
4. If a third business function were added to this pipeline tomorrow that could also raise these exception types, how would you know whether its call site needs its own catch block, without waiting for a bug report?

## Race Conditions in Client State

5. Why is disabling a button not enough on its own to prevent a race condition — what would still go wrong if `sampleDataLoading` gated only the "Run sample data" button but not the primary "Run" button?
6. The fix combines two independently-named loading flags (`status === "submitting"` and `sampleDataLoading`) into one disabled expression, rather than merging them into a single flag. What's the argument for keeping them separate state variables but combining them at the point of use?
7. This bug shipped because a *second* trigger for an existing action was added without revisiting the *first* trigger's guard condition. What's a systematic way to catch this class of bug before it ships, given this project has no automated frontend tests?

## Component State Ownership

8. Why does a component owning `useState` for information the parent also has access to become a bug risk specifically when a *second* way to change that information is introduced — what made it safe before that?
9. The `selectedFileName` fix works for any future third way of setting the file (drag-and-drop, paste, etc.) without further changes. Why does fixing the actual root cause (instead of special-casing "Run sample data" specifically) produce that property?
10. Are there other components in this codebase that might have the same "component owns state a parent also owns" shape, and how would you go looking for them systematically?

## Accessibility as a Consistency Problem

11. Why is it more dangerous to have one correct accessible pattern (`BusinessErrorMessage`) sitting next to one incorrect one (a bare `<p>`) on the same page, than to have zero accessible error patterns anywhere in the codebase?
12. What's a concrete technique for catching "this new UI element should have reused an existing component but didn't" during a review, versus only during implementation?

## TDD vs. Live-Browser Verification

13. Why did the Critical bug get a written regression test while the four Important UX bugs did not? Is that the right line to draw, or should this project invest in a frontend test harness specifically because of what this bug-fix round revealed?
14. The RED step (watching the test fail with the predicted exception) is described as confirming the diagnosis, not just proving the test works. What's the difference, and why does that distinction matter for trusting the eventual fix?

## Review Process

15. The re-review agent found a documentation staleness issue (Decision 12's now-inaccurate wording) that the original fixing session never surfaced. Why is a *second*, independently-scoped review pass positioned to catch that kind of thing when the first pass — done by the same agent that wrote the fix — structurally could not?
