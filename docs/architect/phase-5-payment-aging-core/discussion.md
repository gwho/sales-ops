# Phase 5: Payment Aging Core — Architect Session Discussion

This is the full reasoning record behind the Phase 5 blueprint: how the research was
structured, what ambiguities the spec actually contained (with exact text), which
alternatives were seriously weighed before each decision in `decisions.md`, and what
happened during the correction round that followed the first rejected plan draft.

## How the session was structured, and a genuine process wrinkle

The session opened as `/architect`, whose own procedure (Understand → Align on
Language → Think Through Decisions Together → Blueprint Ready → Implementation Plan)
is a conversational, one-question-at-a-time Socratic loop. But the harness had also
put the session into Plan Mode, which carries its own generic workflow: Explore
agents for research, a Plan agent for design, `AskUserQuestion` for clarification, and
a mandatory plan file ending in `ExitPlanMode`. These two processes aren't identical,
and reconciling them mattered: rather than treat Plan Mode's generic workflow as
overriding `/architect`'s intent, the session used Plan Mode's tools to *carry out*
`/architect`'s actual goals — parallel `Explore` agents did the "Understand What's
Here" research step, and `AskUserQuestion` (rather than freeform chat) carried out the
"Think Through Decisions Together" step, one batch of related decisions at a time,
each option framed with a recommendation and reasoning to react to, exactly as
`/architect`'s Step 3 describes ("share what you would do and why — give the developer
something to react to, not a blank page to fill"). The plan file and `ExitPlanMode`
call satisfied Plan Mode's own requirement while also being `/architect`'s Step 5
("Produce the Implementation Plan"). This is worth remembering for future phases: when
a slash-command skill and Plan Mode are both active, the skill's *intent* should drive
how Plan Mode's tools get used, not the other way around.

## Research phase: what the two parallel Explore agents actually found

Two agents ran in parallel rather than sequentially, split by concern rather than by
file, because the two concerns don't depend on each other: one agent read the spec,
`CONTEXT.md`, `contracts.py`, `contract_fixtures.py`, and `sample_data.py`'s
`generate_invoices()` to establish *what the rules and shapes actually say*; the other
read Phase 3/4's actual source code to establish *what the codebase's existing
conventions actually are*. Running them together rather than one-then-the-other meant
the pattern-matching research (loader shape, envelope pattern, error-handling style)
didn't wait on the spec research to finish, since neither needed the other's output —
only the synthesis step (turning both reports into `AskUserQuestion` prompts) did.

The spec-research agent surfaced a detail that shaped several later decisions before
any question was even asked: **the fixture file `tests/contract_fixtures.py` was
itself internally suspicious**. Its own docstring already warns "Hand-authored, not
computed by `src/sample_data.py` or any business-rule module... these only prove the
contract shapes can hold believable demo data; they are not evidence that any business
rule is implemented correctly." The agent additionally flagged, without being asked to
look for it, that `PAYMENT_AGING_SUMMARY_FIXTURE`'s `aging_bucket_counts` values sum
to 8 while `total_invoices` says 10 — a two-invoice gap that turned out to *predict*
Decision 3 (`total_invoices` counts everything, bucket counts don't) before the
question was ever formally asked. This is a useful pattern: a fixture's internal
arithmetic can leak the fixture author's original intent even when nothing in prose
states it directly.

## The ambiguities that actually existed in the spec text

It's worth being precise about which of PA-001 through PA-007 were genuinely ambiguous
versus which just needed careful reading, because the difference matters for how much
weight to give the decisions:

**PA-002 ("mark invoice as Paid and exclude it from overdue follow-up")** is
genuinely ambiguous about *scope of exclusion* — "overdue follow-up" could mean "the
Follow-up List sheet" or "the entire aging output." This was resolved by
cross-referencing three other parts of the same spec document (the sheet name, the
suggested-actions table, the output-columns table) rather than by picking either
reading arbitrarily. See Decision 2.

**PA-005's High condition ("days_overdue > 60 or outstanding_amount >= 50000")** is
not ambiguous in isolation — it's a plain unconditional `or` — but its *consequence*
when combined with Decision 5 (signed `days_overdue`) is a behavior a reader
skimming the rule in isolation wouldn't predict: a not-yet-due invoice can be
High-priority. This isn't spec ambiguity so much as spec *literalism producing a
counter-intuitive result* — worth flagging separately from genuine ambiguity, because
the fix for genuine ambiguity is "pick the right reading," while the fix here was
"implement it literally, then add a narrower guard somewhere else (draft messages)
so the literal reading's edge case doesn't cause a worse problem."

**PA-001/PA-007's treatment of `paid_amount` vs `invoice_amount`** is a case of the
spec being asymmetric on purpose (one field has a documented "missing → 0" fallback,
the other has a documented "flag as error" rule) and the ambiguity being "does this
silence about `paid_amount`'s *other* failure modes (non-numeric, negative) mean
*no rule*, or *the same rule as invoice_amount by implication*?" This is the one place
in the session where "the spec doesn't say" was explicitly *not* read as "infer the
stricter behavior," on Scope Gate grounds — see the Decision 7 discussion below for
why that's not just deference to a formatting rule but a real judgment call.

**The reference-date parameter** isn't spec-ambiguous at all — `as_of_date: date` with
no default is explicit in section 11. The tension here was entirely *between the spec
and the existing codebase*, not within the spec itself: `sample_data.py` had already
established a different, better pattern (optional param resolved at call time) for the
same underlying problem (what does "today" mean to a business-rule function), and the
question was whether to follow the spec's literal signature or the codebase's already-
proven convention. This is a different category of decision from the others — it's a
codebase-consistency call, not a spec-interpretation call.

## Alternatives seriously considered and why they lost

**For the envelope/function-shape decision (1):** the losing alternative — three
functions with a DataFrame-tuple return — was not weighed lightly. It's the spec's own
literal suggestion, and dismissing spec suggestions carries real risk: specs are
sometimes suggesting a shape *because* it maps cleanly onto some downstream consumer
the implementer doesn't have visibility into (e.g., a specific Excel-export function
that wants two separate DataFrames to write to two separate sheets). The counter-
argument that won was architectural precedent, not spec-disagreement: Phase 3 and
Phase 4 already answered this exact question for this codebase, and answering it
differently for Phase 5 with no new information would mean report_export.py (Phase 6)
has to special-case one module's return shape against the other two's.

**For the `days_overdue` sign decision (5):** the losing alternative — floor at 0 for
non-overdue rows — is not a bad idea in a vacuum; many aging-report tools do exactly
this, treating "days overdue" as meaningless (hence `0`, not negative) for anything not
actually overdue. It lost specifically *because* PA-005's Watch rule needs a signed
concept to be expressible without adding an uncontracted field. If Watch didn't exist
as a rule, flooring would likely have won on the grounds of being less surprising to a
report reader.

**For the draft-message currency formatting (8):** two options were originally
offered — always `$`, or no symbol at all — and the user chose neither, proposing
`{currency} {amount}` instead. This is the one decision in the session where the
offered options were both worse than the eventual answer, worth noting because it's a
reminder that a well-framed multiple-choice question can still miss the actual best
answer if the person answering has domain context (here: "the amount already knows its
own currency, just use it") that the question-framer didn't fully apply when
generating options.

## The correction round: what the rejected first plan draft was missing, and why each catch mattered

After the eight `AskUserQuestion` decisions were resolved, a first plan draft was
written and submitted via `ExitPlanMode`. It was rejected — not because any of the
eight decisions were wrong, but because the draft had **implementation-level gaps that
the decisions didn't fully specify**, which the user caught in one pass:

1. **The `row_number`-in-error-message detail.** The draft's own text ("used to build
   a business-readable `error_message`... 'Row 5: due date is missing.'") described a
   phrasing choice that, if implemented literally, would embed a row number into
   output text — without the plan ever deciding whether a `row_number` *field* should
   also be added to `PaymentDataIssueRow`. This is a subtle failure mode: a plan can
   describe an implementation detail in passing without realizing that detail implies
   a contract change. The fix was explicit: no `contracts.py` change, `row_number`
   stays internal-only, plain error message text.

2. **The overpayment test gap.** The plan's decisions established outstanding-amount
   clamping (`max(0, invoice_amount - paid_amount)`) as an *assumption*, not a decision
   put to the user, and — critically — nothing in the original test list would have
   caught a regression if a future edit silently removed the clamp. The user added an
   explicit test case (`invoice_amount=100, paid_amount=150`) specifically because an
   assumption without a locking test is an assumption a future refactor can quietly
   undo.

3. **Promoting the "None priority → No action required" assumption to a decision.**
   Similar shape to the overpayment gap: the plan had reasoned its way to a sensible
   default but hadn't flagged it as something the user should explicitly bless, since
   it's a genuine judgment call (the spec's suggested-actions table really does have no
   row for "None") rather than something derivable mechanically.

4. **The `invoice_amount` non-numeric test gap.** PA-007 says "missing *or less than
   0*" — but the plan's test list, as originally drafted, leaned toward missing/negative
   cases without an explicit non-numeric-string case (e.g. `invoice_amount="abc"`).
   "Invalid" in PA-007 is broader than the two examples the rule text gives; a test
   suite that only covers the examples named in the rule, not the category the rule
   describes, has a coverage gap that's easy to miss because the passing tests give no
   signal anything is wrong.

5. **Making the `paid_amount`-not-required decision explicit in the loader design,**
   rather than leaving it as an implicit consequence of "not being in the required
   columns list." Same shape as points 1 and 3: a true statement that was never
   written down as a decision is a true statement a future agent has to
   re-derive — or worse, might get wrong — instead of reading directly.

6. **Re-confirming the branch-point verification rule** that Phase 4's session had
   already established as a standing pattern (check live PR merge status right before
   branching, don't assume). This wasn't a new catch so much as the user making sure
   the standing rule actually got applied this time, not just remembered in the
   abstract — which in the event mattered directly: PR #2 and PR #3 were still both
   open when Phase 5 actually started, and a stale assumption would have branched off
   local `main`, which was missing all of Phase 3 and Phase 4's code entirely.

The common thread across catches 1, 3, and 5 is the same failure mode: **a plan can
contain a locally-correct sentence that implies a decision without that decision ever
being surfaced as a decision.** None of the three were wrong calls once made explicit
— they're exactly what a careful engineer would have chosen anyway — but "the right
answer, buried in passing text" is a different, weaker state than "the right answer,
stated as a decision with a name attached to it and a test locking it in." This is
the same lesson Phase 4's session learned about stale-branch assumptions, applied to a
different kind of gap (implicit decisions inside an otherwise-sound plan, rather than
an unchecked precondition about external state).

## What this means for the next phase's architect session

Two process notes worth carrying forward: first, when a plan file states an
implementation detail in passing (a helper function's exact behavior, a formatting
choice, a validation rule not directly demanded by the spec), it's worth explicitly
asking "does this detail imply a decision nobody has actually confirmed yet?" before
treating the plan as done — the three implicit-decision catches in this session all
had that shape. Second, low-risk assumptions are fine to make without a full
`AskUserQuestion` round, but they should come with a named test that would fail if the
assumption were silently reversed later — an assumption without a locking test is
functionally the same as no decision at all, just with extra confidence attached.
