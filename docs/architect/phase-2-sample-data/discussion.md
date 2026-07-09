# Phase 2 /architect Session — Discussion

This is the deep record of the reasoning behind the Phase 2 (Sample Data and Contract Fixtures)
planning session — not a summary of the decisions (see `decisions.md`), but the thinking that
produced them, the alternatives that were considered and rejected, and the concrete failure modes
each choice was designed to avoid.

## Why this session ran in plan mode with `AskUserQuestion`, not free conversation

The `/architect` skill's own instructions describe a Socratic back-and-forth: ask one question,
listen, ask the next. The session that actually ran was constrained by an active plan-mode
harness, which enforces a stricter shape — every turn has to end in either a tool call that asks a
structured question (`AskUserQuestion`) or a request for plan approval (`ExitPlanMode`); it cannot
end in plain conversational text waiting for a reply. The system-level instruction was explicit
that this constraint "supersedes any other instructions" the skill itself describes.

This mattered concretely: instead of asking the date-anchoring question and the fixture-location
question as two separate conversational turns, both were batched into a single `AskUserQuestion`
call with two questions and four total options. The practical effect was the same as the skill
intends — align on the decisions that matter before writing a plan — but the mechanism was a
structured multiple-choice form rather than open dialogue. This is worth noting because it changes
what "asking a good question" looks like: each option needed a self-contained description precise
enough that the user could choose correctly without a follow-up clarifying exchange, since there
was no cheap way to ask "wait, what do you mean by X?" mid-question.

## The staleness problem, in more depth

The core insight behind reference-date anchoring is that this project is explicitly a **portfolio
demo**, meant to be reopened, re-shown, or re-forked at unpredictable future points — not a
one-time script run. Any generated data that encodes "today" as a frozen constant is making an
implicit bet that nobody will look at it again after some horizon. For most generated fixtures that
bet is safe (an order's `requested_delivery_date` of `2026-07-15` will always mean the same thing
relative to its own `order_date` of `2026-07-01` — the *relationship* between the two dates is what
OV-005 cares about, and that relationship doesn't decay).

Payment aging is different in kind, not degree: its entire output is a function of the gap between
a stored date and *whenever the code happens to run*. This is the same category of bug as
comparing a cached timestamp against `Date.now()` in any long-lived system — the data was correct
when captured, and becomes progressively more wrong the longer it sits unchanged. The fix pattern
(store an offset, not an absolute value, when the reference point is expected to move) generalizes
well beyond this project: it's the same reason relative timestamps ("3 days ago") are computed at
render time rather than stored, and the same reason a "trial expires in 14 days" feature stores
`trial_start + 14`, not a hardcoded expiry date computed once.

An alternative that was implicitly considered and rejected without much debate: regenerate
`sample_data/*.xlsx` on some cadence (a CI cron, a pre-demo checklist item) instead of designing the
generator to self-correct. This was rejected mostly by omission — the committed-file approach with
a `reference_date` parameter gets the same freshness property "for free" the next time someone runs
`write_sample_workbooks()`, without needing separate process infrastructure that a portfolio-scale
project has no real reason to build.

## The mutable/time-dependent default argument trap

This is a well-known Python pitfall (usually taught via `def f(x=[]):` silently accumulating state
across calls), but the session surfaced a less commonly discussed variant: the same evaluate-once
semantics apply to *any* expression in a default position, not just mutable literals. `date.today()`
isn't mutable — it returns a fresh, immutable `date` object each time it's called — but the *call
itself* only happens once, at `def` time, because Python evaluates default argument expressions
when the function is defined, not when it's invoked. The bug isn't about mutability; it's about
*when* the expression runs.

This is worth internalizing as a general rule: any default argument value that is supposed to
reflect "current" state at call time — the current time, a freshly-opened resource, a randomly
generated value meant to differ per call — cannot be a literal default. It must be deferred behind
a sentinel (`None` is idiomatic) and resolved inside the function body. The bug this specific
instance would have caused was subtle enough that the first plan draft, and the code sketch
inside it, both used the literal-default form before the user caught it during plan review — which
is itself a small demonstration of why a second pair of eyes on a plan (even a fast one) catches
categories of bug that don't show up in a quick read-through of "does this look reasonable."

## Why fixtures resist the temptation to be computed

There's a natural instinct, once `sample_orders.xlsx`/`sample_inventory.xlsx`/`sample_invoices.xlsx`
exist as real generated data, to derive the contract fixtures *from* them — write a small allocation
simulation, run it against the generated orders and inventory, and populate `AllocationResultRow`
with whatever comes out. This was never seriously proposed in the session, but it's worth
articulating why it would have been wrong, because the temptation will recur in Phase 3-5: doing
this means writing throwaway versions of `order_validation.py`/`inventory_allocation.py`/
`payment_aging.py` — the exact modules Phases 3, 4, and 5 exist to build properly, with their own
spec-derived tests. A "quick and dirty" allocation function written just to populate a fixture
would have no test coverage of its own, would very likely diverge from what the real Phase 4
implementation eventually decides for edge cases (tie-breaking, warehouse choice when two
warehouses have equal stock, etc.), and would create a second, unofficial implementation of
business rules with no spec authority behind it.

The chosen approach — hand-author fixtures that are *internally consistent* (the math checks out:
`outstanding_amount = invoice_amount - paid_amount`) but not *derived* from running any algorithm —
keeps Phase 2 honestly scoped to "prove the shape holds data," full stop. The explicit boundary
note in `contract_fixtures.py` (decision #6) exists specifically to prevent this distinction from
being lost on a future reader who doesn't have this session's context.

## Reading test coverage as a signal of scope, not just correctness

The test-scope boundary decision (decision #4) generalizes into a broader principle that came up
implicitly throughout the session: **a test's assertions are a specification of what the code under
test is responsible for.** If `test_sample_data.py` asserted `aging_bucket == "61-90 Days"` for the
high-priority invoice, that assertion would be silently claiming `generate_invoices()` (or
something in its call path) is responsible for bucket-boundary logic — which is false, and would
mislead anyone reading the test suite to understand module ownership. The fix wasn't to write a
*weaker* test; it's exactly as strong at proving what `generate_invoices()` actually does (produces
a `due_date` at a specific offset), just scoped honestly to that module's real responsibility. This
is the same instinct as `context/architecture.md`'s System Boundaries table (`payment_aging.py`
"owns" outstanding amount/aging buckets/priority/reminders; nothing else does) — applied to test
assertions, not just production code.

## The plan-mode rejection and what it revealed

The first `ExitPlanMode` call was rejected by the user, who then supplied five specific, technically
precise corrections rather than a vague "this isn't right." That the corrections were this specific
(a named Python semantics bug, a named test-scope risk, a named list of missing columns, a named
missing disclaimer, a named stale file) suggests the review was a genuine technical read of the plan
document, not a rubber-stamp rejection. The practical lesson for future planning sessions: writing
the plan file completely before requesting approval — rather than treating `ExitPlanMode` as a
formality — pays off when the reviewer actually reads it, because the plan is detailed enough to
catch real bugs (the default-argument issue) before a single line of implementation code exists.
