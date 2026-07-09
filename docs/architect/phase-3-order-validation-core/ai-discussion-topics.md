# Phase 3 /architect Session — AI Discussion Topics

## On finding and resolving contradictions in a source spec

1. "OV-001 and OV-007 contradict each other on `payment_terms`'s severity — not because either rule
   is individually wrong, but because they overlap on the same field. How would you write a
   systematic check (manual or automated) to find every place a multi-rule spec like this
   contradicts itself, rather than relying on noticing it while planning something else?"
2. "The resolution criterion used was 'the more specific, deliberately-authored rule wins over the
   more generic list membership,' reinforced by an already-locked-in principle (Warning-only rows
   stay valid). What would you do if no such tie-breaking principle already existed — how do you
   choose which of two contradicting rules to keep?"
3. "This contradiction was caught during planning, before any code existed. What would it have cost
   to catch it instead via a failing test, after `order_validation.py` was already implemented one
   way? Is a plan-time catch strictly cheaper, or does it just move the cost to a different phase?"
4. "If you inherited this codebase without reading `explanation.md` or this discussion, and noticed
   `payment_terms` isn't in `OV001_REQUIRED_FIELDS`, how long would it take you to realize that's
   deliberate rather than a bug? What would make that intent more discoverable directly from the
   code itself?"

## On error-granularity design (multiple errors per row)

5. "Field-level OV-001 errors were chosen over one combined 'several fields are missing' message,
   specifically to avoid forcing multiple upload/fix cycles. For a *form-based* UI (not a
   spreadsheet upload) would the same reasoning apply, or does the 'round-trip cost' argument depend
   specifically on the file-upload workflow?"
6. "'First failure wins' — stopping at the first violated rule per row — was explicitly rejected.
   Can you think of a validation context where 'first failure wins' would actually be the *better*
   design, despite hiding information? What property would that context have that this one
   doesn't?"
7. "A row can now accumulate errors from multiple different rule numbers (OV-001 and OV-004 and
   OV-006 all firing at once). What downstream consequences does this have for
   `ValidationSummary.invalid_orders`, and why does the implementation deliberately compute that
   count from a *set* of row numbers rather than summing per-rule counts?"

## On output contract and API shape design

8. "`OrderValidationResult` was kept local to `order_validation.py` instead of being added as a
   14th family to `src/contracts.py`, on the grounds that it's a transport envelope, not a
   business-facing output family. What test would you apply to a *new* type in the future to decide
   which category it falls into?"
9. "The dict-with-named-keys return shape was chosen over a positional tuple specifically because
   positional access 'carries no self-documentation.' What's the cost of the dict approach that the
   tuple approach doesn't have — is there a downside being traded away here?"
10. "If Phase 4 and Phase 5 each define their own local `AllocationResult`/`PaymentAgingResult`
    envelope following this precedent, at what point (if any) would you reconsider and promote a
    shared 'module result wrapper' pattern into `contracts.py` after all? What would have to be true
    about those envelopes for that to make sense?"

## On defensive parsing at a module boundary

11. "`numpy.bool_` is not a subclass of Python's `bool`, but `numpy.float64` *is* a subclass of
    `float`. Why does numpy make that distinction for some scalar types and not others? What does
    this tell you about relying on `isinstance` checks against boxed/object-dtype data in general?"
12. "The active-flag and quantity parsers both fall through to a string-coercion path when a direct
    type check fails, and that fallback happens to correctly handle the numpy-scalar case too. Is
    this an elegant unification, or does it paper over a type-system gap that could bite you in a
    case where the string representations *don't* happen to agree? Can you think of such a case?"
13. "Malformed quantity and date values convert to business-readable errors instead of raising, per
    `context/code-standards.md`'s module-boundary rule — even though the spec's own test cases never
    mention malformed strings. Where exactly is the line between 'this is a data-quality problem the
    business user needs to see' and 'this is a programming bug that should raise,' and does that line
    move if the input format changes from `.xlsx` to, say, a raw CSV upload with no schema at all?"

## On redundant signal vs. genuinely new information

14. "The blank-field skip rule (a blank `priority` triggers only OV-001, not also OV-006) treats
    'empty' and 'invalid' as different problems even though an empty string trivially fails a
    controlled-value check. Where else in a validation system might two technically-true error
    conditions actually represent the same underlying fact, and how would you catch that pattern
    systematically rather than one rule pair at a time?"
15. "Extending the skip rule to OV-002 (duplicates) and OV-006 (priority) was a plan-review addition,
    not part of the original proposal — the first draft only covered OV-003/004/005. What made this
    an easy addition to accept rather than a sign the original design needed to be rethought from
    scratch?"

## On the /architect workflow itself

16. "This session ran the `/architect` skill directly, without the plan-mode harness that forced the
    Phase 2 session into structured `AskUserQuestion` turns. The result was a mix of plain
    conversational turns and structured multiple-choice ones. What determines, in general, when a
    decision is better presented as prose ('here's my thinking, does it work for you?') versus as a
    multiple-choice form with self-contained options?"
17. "The Phase 3 plan was approved with six specific corrections layered on, rather than being
    rejected and rewritten the way the Phase 2 plan was. Does 'approved with corrections' versus
    'rejected and redone' tell you anything meaningful about plan quality, or is it more about how
    much the reviewer already agreed with the overall direction before reading the details?"
18. "One of the six plan-review corrections was a git-state check that turned out to already be
    resolved (Phase 2 had, in fact, already been committed). Is flagging a concern that turns out to
    be a non-issue still valuable review behavior, or does it risk becoming noise if repeated too
    often? How would you calibrate that?"
19. "The language-alignment step (defining 'Valid Order,' 'row_number,' etc. before any architecture
    decision) surfaced user-driven corrections and confirmations rather than agent proposals. Why
    might starting with vocabulary alignment, before any design question, change the quality of the
    decisions that follow it?"
20. "Compare this session's contradiction-catching (OV-001 vs. OV-007) to Phase 2's
    default-argument-bug-catching (`date.today()` as a literal default). Both were caught during
    planning, before code existed. What's different about the *kind* of error each represents — one
    is a logic bug in a not-yet-written implementation, the other is a genuine ambiguity in the
    source-of-truth document itself. Does that distinction change how you'd go about looking for each
    kind in a future planning session?"
