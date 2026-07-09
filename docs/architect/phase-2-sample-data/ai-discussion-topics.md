# Phase 2 /architect Session — AI Discussion Topics

## On time-dependent test/demo data

1. "Why does an invoice's `due_date` need to be relative to `date.today()` while an order's
   `requested_delivery_date` doesn't? What's the general rule for deciding when generated data
   needs a moving reference point versus a fixed one?"
2. "What other kinds of stored data have this same 'correct when written, wrong later' property as
   payment aging buckets? (Think beyond this project — session expiry, cache TTLs, 'new' badges on
   product listings.)"
3. "If you regenerated `sample_data/*.xlsx` on every CI run instead of committing it once, what
   would you gain and what would you lose? Why did this project choose to commit generated files
   instead?"
4. "The 'Current, not yet due' invoice example was identified as the one most likely to silently
   break over time. How would you go about finding *other* pieces of demo/seed data in a codebase
   that have this same latent staleness risk, before they actually break?"

## On Python default argument semantics

5. "Walk through exactly when `def f(x=some_call()):` evaluates `some_call()`. Why does this differ
   from what a Java or JavaScript default parameter would do?"
6. "The classic version of this bug uses `def f(x=[]):`. This session's version used
   `def f(x=date.today()):` — no mutation involved. Explain why both are the same underlying bug
   despite one 'obviously' being about mutable state and the other not."
7. "Is `x: date | None = None` with a body-level resolution the *only* fix, or are there
   alternatives (e.g. a sentinel object instead of `None`, a factory pattern, a class-based
   default)? When would you reach for something other than `None`?"
8. "This bug was caught during plan review, before any code was written. What would it have taken
   to catch it via testing instead, after the code existed? Is a plan-time catch strictly better,
   or does it just move the cost earlier?"

## On module boundaries and where things belong

9. "`context/architecture.md` names exactly six `src/` modules and none of them is 'fixtures.' Why
   was that treated as a real constraint on where `contract_fixtures.py` could live, rather than
   just adding a seventh module since it would be equally easy to write?"
10. "What's the actual difference between 'business logic' and 'test/fixture data,' in terms of why
    one belongs in `src/` and the other in `tests/`? Is this distinction always clean, or are there
    gray areas?"
11. "`REPORT_MANIFEST_FIXTURES` was allowed to be a list of 3 instead of matching every other
    fixture's single-dict pattern. What made this a legitimate exception rather than the start of
    inconsistency? How do you decide when a stated rule ('one fixture per family') should bend?"

## On not reimplementing future work early

12. "The plan was corrected to stop `test_sample_data.py` from computing `aging_bucket` for the
    sample invoices. What's the concrete cost of a test quietly reimplementing logic that a later,
    not-yet-written module is supposed to own?"
13. "How is 'a test asserts what a function actually does' different from 'a test asserts what a
    function's *output* will eventually be used for downstream'? Which one should tests target?"
14. "If you were reviewing a pull request and saw a test file compute business-rule-shaped logic
    (date arithmetic, bucket assignment, priority rules) inline in an assertion rather than calling
    a real function, what would that suggest about the PR's scope?"
15. "The fixtures in `contract_fixtures.py` are hand-authored to be internally consistent
    (`outstanding_amount = invoice_amount - paid_amount`) without being computed by any real
    module. Is 'internally consistent but hand-typed' example data actually risky in a different
    way than computed data? What could go wrong with it that wouldn't go wrong with generated data?"

## On demo data design and realism

16. "Optional columns (`sales_owner`, `remarks`, etc.) were added to sample workbooks even though no
    test checks for them. What's the argument for spending effort on data that no test validates?"
17. "The build-plan explicitly distinguishes 'demo fixtures' (mostly clean, a few realistic
    imperfections) from 'test fixtures' (exhaustive edge-case DataFrames in pytest). Why maintain
    two separate mechanisms instead of one comprehensive set of test data used everywhere?"
18. "The inventory data was deliberately constructed so `MED-LENS-001` demand (35 units) exceeds
    supply (25 units) across two warehouses — designed to force a partial-allocation/backorder
    scenario once Phase 4 exists, without Phase 2 actually computing that outcome. Is 'pre-shaping
    data for an algorithm that doesn't exist yet' a form of scope creep, or good foresight? Where's
    the line?"

## On the plan-mode workflow itself

19. "The first `ExitPlanMode` request was rejected, and the user's feedback included a real bug
    (the default-argument issue) rather than a stylistic complaint. What does that suggest about
    the value of writing a complete, detailed plan file *before* asking for approval, versus
    treating the approval step as a formality?"
20. "This session batched two decisions into a single `AskUserQuestion` call with multiple options
    each, rather than asking one question, waiting, then asking the next. What do you gain and
    lose by batching structured questions like this compared to a back-and-forth conversation?"
21. "Every option presented in the `AskUserQuestion` calls included a full rationale in its
    description, not just a label. Why does that matter more in a structured-question format than
    it would in free conversation?"
