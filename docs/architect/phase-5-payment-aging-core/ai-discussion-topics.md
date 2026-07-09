# Phase 5: Payment Aging Core — AI Discussion Topics

## On reconciling a slash-command skill with Plan Mode's generic workflow

1. This session ran `/architect` inside Plan Mode, and the two processes were
   reconciled by using Plan Mode's tools (`Explore` agents, `AskUserQuestion`,
   `ExitPlanMode`) to carry out `/architect`'s actual steps rather than letting either
   process fully override the other. What would have gone wrong if Plan Mode's generic
   workflow had been followed literally instead — research, single Plan agent,
   `AskUserQuestion` only for "remaining questions," write the plan?
2. `/architect`'s own procedure describes one-question-at-a-time conversational
   dialogue; this session batched four related decisions per `AskUserQuestion` call
   instead. What's lost and what's gained by batching decisions rather than resolving
   them strictly one at a time?

## On the two parallel Explore agents and what running them simultaneously bought

3. The two research agents split by *concern* (spec/contracts vs. codebase patterns)
   rather than by *file*. What would have gone wrong — or just been less efficient —
   if the split had instead been "agent 1 reads files A-M, agent 2 reads files N-Z"?
4. One research agent surfaced the `PAYMENT_AGING_SUMMARY_FIXTURE`'s 10-vs-8 arithmetic
   gap without being explicitly asked to look for inconsistencies — it was reading for
   facts and happened to notice the numbers didn't add up. Is "notice when numbers
   don't reconcile" something worth asking a research agent to check for explicitly, or
   is it inherently the kind of thing you only find by accident while reading for
   something else?

## On distinguishing genuine spec ambiguity from literal-reading surprises

5. PA-002's "exclude it from overdue follow-up" was resolved by cross-referencing three
   *other* parts of the same document (sheet name, suggested-actions table, output-
   columns table) rather than picking a reading and defending it directly. Is
   cross-referencing sibling sections of the same spec a generally reliable
   disambiguation technique, or does it risk over-fitting to incidental phrasing (a
   sheet name chosen for brevity, not semantics) that wasn't meant to bear that much
   interpretive weight?
6. PA-005's High-priority `or` condition isn't ambiguous — it's a plain unconditional
   `or` — but implementing it literally produces a "High priority, not yet due"
   combination a spec reader skimming the rule wouldn't predict. When a literal reading
   produces a surprising result like this, is "implement literally, then narrow the
   *consequence* elsewhere" (what happened here, via the draft-message guard) the right
   general move, or should the surprising rule itself be questioned back to whoever
   wrote the spec?

## On the difference between "the spec is silent" meaning two different things

7. `paid_amount`'s failure modes beyond "missing" (non-numeric, negative) got the
   lenient treatment — degrade to 0 — specifically because extending PA-007's stricter
   rule by analogy would be "inventing a rule the spec doesn't state." But isn't
   *choosing* the lenient behavior for an unstated case also inventing a rule, just a
   more forgiving one? What's the actual principled difference between "spec silence
   defaults to lenient" and "spec silence defaults to strict," or is the real
   justification narrower than "spec silence" — specifically that `paid_amount` is
   already documented as optional?
8. If a future spec revision explicitly said "negative paid_amount should also be
   flagged as an error," would that be a natural rule *addition* (no ADR needed, since
   it's clarifying an already-in-scope rule) or a scope *change* requiring the Scope
   Gate process? Where's the line between clarifying an existing numbered rule and
   changing what it means?

## On the "implicit decision buried in passing text" failure mode from the correction round

9. Three of the six correction-round catches (row_number-in-message, None-priority
   suggested_action, paid_amount-not-required) share the same shape: a locally-correct
   sentence in the plan implied a decision that was never explicitly surfaced as one.
   What's a concrete technique — beyond "read the plan more carefully" — for catching
   this class of gap systematically, rather than relying on a second reviewer to spot
   it by chance?
10. The session's takeaway was "an assumption without a locking test is functionally
    the same as no decision at all." Is that true in general, or does it depend on how
    likely the assumption is to be silently reversed by a future edit — is a locking
    test overkill for an assumption nobody has any real reason to touch later?
11. The non-numeric-`invoice_amount` test gap happened because the plan's test list
    leaned on the *examples* PA-007 gives ("missing or less than 0") rather than the
    *category* the rule actually describes ("invalid"). Is there a general rule for
    spotting when a spec's examples are narrower than its stated scope, before writing
    the test list rather than after?

## On fixtures as evidence, given one turned out to be factually wrong

12. The research phase used `PAYMENT_AGING_SUMMARY_FIXTURE`'s bucket-count arithmetic
    as a signal that predicted Decision 3, and separately, implementation surfaced that
    `DRAFT_MESSAGE_ROW_FIXTURE` had a factually wrong currency symbol the whole time.
    Both fixtures came from the same hand-authored Phase 2 file. Should a hand-authored
    fixture's *internal consistency* (do the numbers add up) be trusted more than its
    *content accuracy* (are the specific values correct), or are both equally
    fallible in different ways?
13. Phase 4's session treated a different Phase 2 fixture (`BACKORDER_ROW_FIXTURE`) as
    strong evidence for an ambiguous design decision (whether backordered lines should
    carry a warehouse value). Given that this session's fixture turned out to contain
    an outright factual error, should that change how much weight future sessions give
    to Phase 2 fixtures as evidence, or was the Phase 4 case different in kind (a shape
    question the fixture author would have gotten right by construction) from this
    session's case (a specific string value the fixture author would have had no way
    to verify without the module that didn't exist yet)?

## On decisions that are architectural precedent vs. decisions that are genuine spec interpretation

14. The envelope-shape decision (single function, Phase 3/4 pattern) and the
    reference-date decision (optional param resolved at call time, `sample_data.py`
    pattern) were both won primarily by *codebase consistency* rather than *spec
    interpretation* — the spec's own suggested shape lost in both cases. Is there a
    risk that "match what Phase 3/4 already did" becomes a reflexive default that stops
    getting re-examined on its own merits by, say, Phase 8 or 9, even in a case where
    the earlier phases' pattern genuinely doesn't fit?
15. If Phase 6 (Excel Report Export) needs a shape from `payment_aging.py` that the
    single-envelope-function pattern doesn't cleanly provide — for instance, if writing
    each output family to its own Excel sheet turns out to want DataFrames, not
    lists of dicts — does that mean the Phase 5 decision was wrong, or that Phase 6 is
    the layer responsible for the dict-to-DataFrame conversion, keeping the business
    module's JSON-serializable contract unchanged?

## On what this session leaves unresolved for later phases

16. `PaymentAgingResult`'s field names (`aging_rows`, `data_issues`, `draft_messages`)
    don't share a naming convention with Phase 3's (`valid_orders`, `errors`) or Phase
    4's (`allocation_results`, `backorders`, ...). This wasn't raised as a question in
    this session at all. Should naming consistency *across* envelope shapes have been
    a ninth decision, or is per-module naming freedom actually fine as long as each
    envelope is internally coherent and always accessed by key rather than iterated
    generically?
17. The correction round re-confirmed the "verify PR merge status before branching"
    rule from Phase 4, and it turned out to matter in practice (PR #2/#3 were still
    open). Now that this has been the right call twice in a row, at what point does a
    standing verification habit like this stop needing an explicit re-confirmation
    step in each new session's correction round, versus just becoming assumed
    background practice the way "run the tests before claiming done" already is?
