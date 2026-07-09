# Phase 3 /architect Session — Discussion

This is the deep record of the reasoning behind the Phase 3 (Order Validation Core) planning
session — not a summary of the decisions (see `decisions.md`), but the thinking that produced them,
the alternatives that were weighed, and the general principles each choice illustrates.

## How this session's mechanics differed from Phase 2's

The Phase 2 `/architect` session ran inside an active plan-mode harness, which forced every turn to
end in a structured tool call (`AskUserQuestion` or `ExitPlanMode`) rather than free conversational
text. This session ran the `/architect` skill directly, without that constraint — which meant the
skill's own prescribed shape (Step 2: align on language via plain conversational text; Step 3: ask
one decision at a time, in prose, waiting for a reply each time) could actually run as written. The
practical difference shows up in how the session opened: instead of a single batched
`AskUserQuestion` call covering multiple terms at once, the first message was plain text laying out
four term definitions ("Valid Order," "Duplicate order ID," "row_number," "Invalid SKU vs. Inactive
SKU") and asking for confirmation — the Socratic format the skill actually describes. Later
decisions in the session mixed both styles: some were plain-text "here's my thinking, does it work
for you?" turns, others used `AskUserQuestion` once a decision had enough discrete options to
present as a multiple-choice form (the quantity-parsing and date-parsing edge cases, and the
active-flag normalization question). This is worth noting as a general pattern: structured
multiple-choice works well when the decision space has 2-3 clearly distinct, self-contained
options; prose works better when a decision is more naturally "here's my reasoning, correct me if
it's wrong" — which is closer to how a senior engineer actually talks through an ambiguous call.

## Finding — and resolving — a real contradiction inside the source spec

The single most consequential thing this session produced wasn't a design preference; it was
catching that `01_demo_order_validation.md` contradicts itself. Rule OV-001's required-fields list
includes `payment_terms`, and every other field in that list is unambiguously Error-severity (every
worked example in §8 for OV-001 through OV-006 is `Error`). But Rule OV-007 is a *separate*,
specifically-numbered rule that covers the exact same underlying condition — a blank
`payment_terms` cell — and its own worked example in §8 explicitly labels it `Warning`. Read
independently, each rule is perfectly sensible. Read together, they can't both be followed
literally without producing an internally inconsistent system: is a blank `payment_terms` an Error
or a Warning? The spec, taken as two separate rule statements, says both.

This wasn't found by reading the spec start to finish looking for contradictions — it surfaced
naturally while trying to answer a much narrower question during planning: "exactly which fields
does OV-001 check, and in what order should each field's error message appear?" Enumerating the
field list forced a side-by-side comparison with OV-007's field (they're the same field), and the
severity mismatch became visible as soon as both were written down next to each other. This is a
useful debugging/spec-reading technique in general: contradictions in prose specifications often
hide in the gap between two sections that were each written to be locally correct, and the way to
surface them is to try to mechanically enumerate something the spec implies (a field list, a state
machine, a decision table) rather than just reading prose linearly.

The resolution criterion that got applied — "the more specific, deliberately-authored rule wins over
the more generic list membership" — is a reasonable default but not the only possible one. The
opposite resolution (OV-001's Error severity wins, OV-007 is redundant/vestigial) was available and
would have been internally consistent too, just with different behavior: `payment_terms`-missing
rows would be excluded from `valid_orders`. What made OV-007-wins the right call *here*, specifically,
was an earlier decision already on the table: "Warning-only rows stay valid" had already been
established as a design principle before this contradiction was found, for reasons independent of
`payment_terms` (a sales-ops workflow shouldn't block downstream allocation over a missing payment
term when the order itself is otherwise sound). Given that principle already existed, OV-001-wins
would have silently broken it for exactly one field, while OV-007-wins keeps the principle
uniformly true. The lesson generalizes: when a spec contradicts itself, the resolution that's
consistent with other decisions you've already locked in is usually the right tiebreaker, because
it keeps the system's behavior predictable in one dimension you've already committed to, rather
than introducing a field-specific special case that a future reader would have to memorize.

## The cost/benefit of "one error per row, one error per missing field"

The explicit alternative to field-level OV-001 granularity — bundling every missing field into a
single combined message ("Several required fields are missing: customer_name, priority") — is not
an unreasonable design. It produces a shorter error table and a single row to review per bad order
line. It was rejected in favor of one-error-per-field for a specific, named cost: it "forces the
user into multiple upload/fix cycles." Unpacking that cost concretely: if a row is missing three
fields and the tool only ever reports the first one found, the user fixes that field, re-uploads,
and discovers the second missing field for the first time — information the tool already had on
the first pass but chose not to surface. This is the same shape of problem "first failure wins"
validation has always had (a classic complaint about early web form validators that reported one
error at a time), and the fix is the same: report everything you know is wrong in a single pass,
even if that means a longer report. The trade being made is table length for round-trip count — and
for a spreadsheet-based workflow specifically (where "round trip" means re-uploading an entire
Excel file, not just re-submitting one form field), minimizing round trips is worth a longer error
table.

This decision compounds with the separate "multiple *rules* can fire on one row" decision (not just
multiple missing fields under OV-001, but OV-001 *and* OV-004 *and* OV-006 all firing on the same
row if it happens to violate all three). Both decisions point the same direction: the validation
tool's job is to report the *complete* set of problems with a row in one pass, not act as a gate
that stops at the first thing it notices.

## Output contract design: why the envelope stayed out of `contracts.py`

The tuple-vs-dict question (should `validate_orders()` return `tuple[Summary, list[Valid], list[
Error]]` or a single named dict) is a fairly common API design fork, and the reasoning behind
choosing the dict — self-documenting access over positional access — is a standard argument. The
more interesting decision, layered on top of that one, is *where the wrapper type itself should
live*. `context/architecture.md` draws a real boundary: the 13 families in `contracts.py` are
described as things that map to a UI table, KPI, or chart — they represent business-facing output
shapes with spec authority behind every field (the Field Scope Boundary rule: a contract may only
contain fields its originating spec explicitly defines). `OrderValidationResult` doesn't have that
property. It's not a new business fact; it's purely a convenience for bundling three *already
contract-shaped* things into one return value. Treating it as equivalent to the 13 families and adding
it to `contracts.py` would have started eroding what that file means — the next module (Phase 4's
`inventory_allocation.py`) would have equal claim to add its own wrapper there too, and eventually
`contracts.py` stops being "the stable output families a UI can trust" and becomes "a junk drawer of
every dict shape any module happens to return."

Keeping the envelope local also has a second, quieter benefit: it makes the precedent explicit for
future phases without requiring a rule to be written down anywhere. Phase 4 and Phase 5 don't need
to consult a style guide to know "define your own local result envelope" — they can look at how
Phase 3 did it and follow the same pattern, because the pattern lives next to the code it describes
rather than in a separate policy document that could drift out of sync with what phases actually do.

## Defensive parsing at a module boundary: the numpy scalar type trap

The quantity-parsing and active-flag-normalization decisions both ran into the same underlying
Python/pandas quirk, discovered (and worked around) during implementation rather than during the
planning conversation itself, but worth recording here because it shaped how the *planned* rules
actually got implemented. `pandas.DataFrame.iterrows()` yields each row as a `pandas.Series` of
`object` dtype — because a single row spans columns of different original dtypes (`str`, `bool`,
`int64`, `datetime64`), pandas can't keep the row's own dtype narrow, so every value gets boxed as a
generic Python object. For a genuinely numeric or boolean *column*, the underlying scalar type
handed back is often a numpy scalar (`numpy.int64`, `numpy.float64`, `numpy.bool_`), not the
built-in Python `int`/`float`/`bool`. Critically, `numpy.bool_` is *not* a subclass of Python's
`bool` in Python 3 (unlike `numpy.float64`, which *is* a subclass of `float`) — so a naive
`isinstance(value, bool)` check silently fails to recognize a real, correctly-typed boolean value
read straight out of an Excel boolean column.

The fix that emerged (documented in `docs/plan/phase-3-order-validation-core/explanation.md`) was to
let the `isinstance` fast-path fail open into a string-coercion fallback: `str(numpy.bool_(True))`
renders as `"True"`, which — after lowercasing — lands in the exact same truthy-string set that
handles literal `"TRUE"`/`"yes"` text values from the spec's "boolean/string" column type. One code
path ends up correctly handling three different origin types (real Python `bool`, boxed
`numpy.bool_`, and literal string) without needing to import numpy or write a type-specific branch
for each. The general lesson: when a boundary has to accept "whatever pandas handed back," designing
the fallback path to be *string-representation-based* rather than *type-based* can accidentally
unify cases that would otherwise need separate handling — as long as the string representations of
the different underlying types happen to agree, which is worth verifying rather than assuming.

## Redundant signal vs. new information: the blank-field skip rule

The blank-field skip rule (a blank `priority` triggers only OV-001, not also OV-006; a blank
`order_id` triggers only OV-001, not also OV-002) is a small rule with a general principle behind
it: **an empty value and an invalid value are different kinds of problems, even when a naive
implementation of a "controlled value" check would flag both.** An empty string trivially fails "is
this one of {High, Normal, Low}" — so without the skip rule, every blank `priority` cell would
produce two errors under two different rule numbers for what is, from the user's perspective, a
single fact ("this cell is empty"). The cost of not having this rule isn't incorrectness exactly —
both errors would be individually true — it's *redundancy that looks like more information than it
actually is*. A user scanning an error table with two rows for the same blank cell has to notice
they're the same underlying problem before they can act on it once instead of twice. This is the
same instinct behind the OV-001/OV-007 resolution (one problem should produce one classification,
not two competing ones) applied at a smaller scale: every rule in the engine should answer "is this
field wrong" exactly once per row, even when multiple rule numbers could theoretically all fire on
the same underlying gap.

## The plan review, and what "no rejected draft" suggests

Unlike the Phase 2 session (where the first plan draft was rejected outright and rewritten), this
plan was approved on presentation, with six specific corrections layered on top rather than a
rejection-and-redo cycle. That the corrections were this precise — naming exact rule codes
(`OV-002`, `OV-006`), an exact contract field (`ValidOrderRow.payment_terms`), an exact test gap
(missing-column vs. blank-value loader coverage), and a real but already-resolved concern (the git
state check) — suggests the plan document itself was detailed enough that the reviewer could reason
about specific implementation consequences from reading it, not just judge it as "reasonable in
general." The git-state check in particular is worth noting as a habit rather than a decision: it
wasn't prompted by anything wrong in the plan's content, but by a general practice of verifying the
actual repository state (`git status`) matches what's assumed before treating a previous unit of
work as a stable foundation to build on top of — a cheap check that would have caught real trouble
if the earlier commit-and-push step had, for some reason, not actually happened.
