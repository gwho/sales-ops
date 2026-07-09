# Phase 6: Excel Report Export — Architect Session Discussion

This is the full reasoning record behind the Phase 6 blueprint: how the research was
structured, what the specs and existing contracts actually said, the two rounds of
`AskUserQuestion` (one completed normally, one rejected and replaced), the six
corrections the user made to the first plan draft, and a process observation about
Plan Mode that's worth remembering for future phases.

## Session structure and a genuine process wrinkle, repeated from Phase 5

Like Phase 5, this session ran `/architect` inside Plan Mode, and reconciled the two
processes the same way Phase 5's session established as the working pattern: Plan
Mode's `Explore` agents carried out `/architect`'s "Understand What's Here" research
step, and `AskUserQuestion` carried out "Think Through Decisions Together" — each
question framed with a recommendation to react to, not a blank page. This is now a
confirmed, repeated pattern across two consecutive phases, not a one-off improvisation
— worth treating as the project's actual convention for running `/architect` whenever
Plan Mode is active, rather than re-deriving it from scratch each time.

What's new this session: **two tool-use rejections**, both from the user, at two
different points — mid-decision-gathering and (twice) at plan-approval time. Neither
was a rejection of the plan's substance; both were process corrections. The first
happened when a second `AskUserQuestion` batch was proposed; instead of answering it,
the user said "Let's continue," which was a signal to stop asking and proceed with the
stated recommended defaults rather than force a second round of multiple-choice
questions. The second and third happened at `ExitPlanMode`: the first rejection came
with a detailed six-point written correction to the plan draft (covered below), and
the second came with a one-line addition ("also `/session-doc` the architect discussion
for this feature") after the corrections had already been folded in. Both are evidence
that `ExitPlanMode` rejections in this project aren't necessarily "the plan is wrong"
— they can be "the plan is nearly right, here's what to fix before I approve it,"
which is a different signal to read than a flat rejection.

## Research phase: what the two parallel Explore agents found

Two agents ran in parallel, split by concern the same way Phase 5's were: one read the
three in-scope specs, `CONTEXT.md`, `contracts.py`, `build-plan.md`,
`code-standards.md`, `library-docs.md`, and the `REPORT_MANIFEST_FIXTURES` fixture data
to establish *what the report structure is actually supposed to be*; the other read
`order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, `excel_io.py`,
`sample_data.py`, and the Phase 3–5 test files to establish *what the codebase's real
shapes and conventions already are*.

Three findings from this research shaped the entire session before a single question
was asked:

**The sheet names were already locked, not open for design.** `tests/contract_fixtures.py`'s
`REPORT_MANIFEST_FIXTURES` — authored back in Phase 2, before any business module
existed — already pins the exact `sheet_names` list for all three reports (e.g.
`["Summary", "Valid Orders", "Validation Errors", "Original Orders"]` for order
validation). `tests/test_contracts.py` already asserts this fixture's structure. This
meant Phase 6 wasn't *designing* sheet names — it was *implementing code that produces
what a Phase 2 fixture already committed to*. This reframes the whole architect
session: several apparent "design decisions" (sheet order, sheet names, manifest
key-set) were actually already made two phases ago and just needed to be honored
correctly, not re-litigated.

**The specs' suggested function signatures don't match what the real modules
return.** `01_demo_order_validation.md` §10–11 suggests
`export_order_validation_report(valid_orders_df, validation_errors_df,
original_orders_df) -> bytes` — three separate DataFrame parameters. But
`validate_orders()` (implemented in Phase 3, before this spec section was ever revisited)
already returns a single `OrderValidationResult` envelope bundling `valid_orders` and
`errors` together. This is the same "spec-suggestion vs. established-codebase-pattern"
tension Phase 5's decision #1 hit with the payment aging module's three-function
suggestion — and this session resolved it the same way: the established codebase
pattern wins, because the spec's function signatures were always illustrative
suggestions ("Suggested functions"), never a contract.

**`operations_follow_up_pack.xlsx` traces to a V1.5 label the build-plan's phrasing
obscures.** `context/build-plan.md`'s Phase 6 section calls it merely "optional," which
reads as a low-stakes nice-to-have. Tracing the actual feature to its source —
`05_integration_and_app_flow.md` §7 — found it explicitly labeled "Optional V1.5
feature." This is a good example of why the Scope Gate is defined as a *mechanical
check* ("grep the spec for a version label") rather than a judgment call: relying on
`build-plan.md`'s casual phrasing alone would have produced a different, wrong answer
about scope than actually reading the source spec's own label.

## The ambiguities that were genuinely open vs. things needing careful reading

**Where does "Original Orders" data come from, given the envelope doesn't have it?**
This is a genuine gap, not a misreading — `OrderValidationResult` was designed in Phase
3 with exactly the fields `01_demo_order_validation.md`'s validation *rules* require
(`summary`, `valid_orders`, `errors`), and nothing in Phase 3's scope called for
retaining the raw uploaded rows. The "Original Orders" sheet requirement comes from a
*different* section of the same spec (§7's Downloadable Output), written with the
report in mind, not the validation function. Resolving this required recognizing that
report_export.py's inputs don't have to be limited to one envelope — accepting the raw
`orders_df` as a second, presentation-only parameter doesn't touch
`OrderValidationResult`'s contract at all.

**Does "Follow-up List" include Watch-priority rows?** Genuinely ambiguous — the spec's
"follow-up table" description in §6 doesn't define the sheet's exact filter, and unlike
Phase 5's PA-002 ambiguity (which had three cross-referencing signals in the same spec
to resolve it), there was no equivalent evidence here. This was resolved by
recommendation and reasoning (Watch-priority invoices are, definitionally, invoices
someone should be keeping an eye on — excluding them from a "Follow-up List" would be
a stranger reading than including them) rather than textual triangulation, since the
text itself doesn't settle it. Worth flagging for a future session: if this
interpretation turns out wrong once a real UI consumer exists, it's a one-line filter
change, not a contract change.

**Is "Backorders" a separately-computed sheet or a filtered view?** This *looked* like
an open design question during initial research but wasn't — `inventory_allocation.py`
already computes `backorders` as its own field in `InventoryAllocationResult`
(filtered by `status == "Backordered"` inside the module itself, per Phase 4's own
design). `report_export.py` doesn't need to filter anything for this sheet; it just
writes the list it's handed. This is a useful contrast with "Follow-up List," which
*does* need report_export.py to filter, because no equivalent field exists in
`PaymentAgingResult`. The general rule that emerged: if the envelope already has a list
for a sheet, write it as-is; only derive a sheet by filtering when the envelope
genuinely has no matching field.

## The rejected second `AskUserQuestion` round, and what "let's continue" actually meant

The first round of four questions (input shape, return shape, Original Orders source,
operations pack scope) was answered normally, each with the recommended option and the
user's own added reasoning layered on top — notably, the user's answer to the "Original
Orders source" question already previewed what would later become the plan's correction
(making the parameter genuinely optional rather than "required in practice"), which the
first plan draft didn't fully carry through consistently. That inconsistency is exactly
what the written correction later caught.

The second round (Follow-up List filter, report_id generation, generated_at
injectability, formatting depth) was rejected as a tool call rather than answered. The
user's next message was "Let's continue" with no further elaboration. Rather than
re-prompt with a smaller or reworded question, the read on this was: the four questions
each already had a stated recommendation with reasoning attached, and the user was
signaling "stop asking, proceed with what you already told me you'd do." This produced
four decisions (6, 7, 8, and the plain-string formatting half of decision 9) that
entered the plan as "recommended defaults, silently adopted" rather than "explicitly
confirmed by the user's own words" — a real, worth-noting difference in confidence
level from the Round 1 decisions and from the corrections that followed. It's exactly
these four "silently adopted" decisions that the user's subsequent written correction
then revisited and tightened (6 stayed as recommended; 8's formatting recommendation
was corrected into two separate pieces — hex-constant framing and `_safe_cell_value` —
neither of which had been asked about at all). This suggests a pattern: defaults
adopted via "let's continue" get a closer second look at plan-review time than defaults
the user explicitly picked from a menu.

## The six corrections, and why each one is a different *kind* of catch

The user's rejection-with-corrections message is worth reading as six distinct failure
modes, not six versions of the same mistake:

1. **A stale to-do that was already resolved.** The plan told the user to "resolve
   `memory.md` and the untracked docs folders before branching" — but those folders had
   already been committed and pushed to PR #4 *earlier in this same session*, before
   the architect discussion even started. This is a context-tracking failure: the plan
   was drafted without re-checking git state that had changed mid-session, not a
   knowledge gap.

2. **An internal contradiction in the plan text.** Decision 5's original phrasing said
   the `original_orders_df` parameter was "required in practice" while also giving it a
   `None`-typed default and describing `None`-handling behavior. A parameter can't be
   both required and optional — this is a logic error in the writing itself, not a
   design disagreement, and the fix (always create the sheet, let the parameter
   genuinely be optional) resolved the contradiction rather than picking a side.

3. **A missing implementation detail with real correctness consequences.** No
   `_safe_cell_value` handling had been planned at all — this wasn't a wrong decision,
   it was an absent one. `NaN`/`NaT` cells are a near-certainty in any sheet built from
   real pandas DataFrames (`Original Orders` especially, since blank cells in an
   uploaded `.xlsx` become `NaN` on load), so this gap would have surfaced as a real bug
   the first time someone ran the code against sample data with any blank cell — which,
   per the project's own sample-data design philosophy, is guaranteed to happen (sample
   workbooks are deliberately "mostly clean with a small number of realistic
   imperfections").

4. **Overclaiming a rule doesn't apply, rather than showing why.** The first draft's
   treatment of the "no hardcoded hex" rule technically reached the right conclusion
   (the rule doesn't govern openpyxl) but stated it as a blanket exemption rather than
   demonstrating the boundary in the code itself. This is a documentation/framing
   correction more than a technical one — the fix (name the constant, comment why) makes
   the reasoning inspectable by a future reader instead of asking them to trust a claim.

5. **A recommendation adopted via "let's continue" that could be made strictly safer at
   no cost.** The `!= "None"` vs. explicit-allow-list distinction for Follow-up List
   produces identical output today; the correction doesn't fix a bug, it changes which
   *direction* a future, unanticipated input fails in. This is the kind of correction
   that's easy to skip because nothing is currently broken — worth remembering as a
   category: "no behavior change today, but changes the failure mode" is still worth
   raising even when nothing is provably wrong yet.

6. **A verification step that quietly assumed a permission it didn't have.** The
   original verification section described manually opening a generated workbook as
   though it were just another automated check. Actually launching a desktop
   application is a different category of action than running `pytest` — the
   correction didn't remove the verification value of eyeballing a real workbook, it
   just moved the decision of *whether to do it* back to the user.

## A process lesson: Plan Mode's file-write restriction and where `/session-docs` has to sit

One structural point worth recording separately from the six corrections: `/session-docs`
was requested as part of the plan-approval rejection, but it couldn't actually run
until after `ExitPlanMode` succeeded, because Plan Mode in this session restricted all
file writes to the single designated plan file. The fix wasn't to argue about this —
it was to add `/session-docs` as an explicit build step (step 0, before any Phase 6
code) inside the plan itself, so the ordering became a locked part of the sequence
rather than something negotiated in the moment. This is a reusable pattern for future
sessions: if a request during Plan Mode requires a write Plan Mode won't allow yet, the
right move is to fold the request into the plan as a first post-approval step, not to
attempt it anyway or to drop it.
