# Phase 6: Excel Report Export — AI Discussion Topics

## On reading `ExitPlanMode` rejections correctly

1. This session had three tool-use rejections total: one mid-`AskUserQuestion`
   ("let's continue," no answers given) and two at `ExitPlanMode` (a six-point written
   correction, then a one-line addition). None were a rejection of the plan's
   substance. What signals in a rejection message distinguish "the direction is wrong,
   start over" from "the direction is right, fix these specific things"? Would a
   different phrasing of the same six corrections have changed how much of the plan
   needed to be reworked versus just amended?
2. The mid-session rejection ("let's continue") produced *silent adoption* of four
   recommended defaults rather than explicit confirmation. The later written
   correction then revisited two of those four more closely than the two that had been
   explicitly confirmed in Round 1. Is "recommended defaults get more scrutiny at
   review time" a pattern worth expecting generally, or specific to this session?
3. When a request arrives that Plan Mode's write restrictions can't fulfill yet (here,
   `/session-docs`), the resolution was to fold it into the plan as an explicit build
   step rather than attempt it or drop it. What would break about this approach if the
   requested action needed to happen *before* the plan could even be written, not after
   it was approved?

## On inheriting decisions instead of making them

4. `REPORT_MANIFEST_FIXTURES` was authored in Phase 2 — two business modules and one
   architect session before `report_export.py` existed — and already locked the exact
   sheet names Phase 6 had to produce. How should an architect session distinguish
   between "this looks like an open design question" and "this was already decided by
   an earlier phase and just needs to be honored"? What would have happened if this
   session had redesigned the sheet names from scratch, reasoning purely from the specs,
   without checking whether a fixture already committed to specific strings?
5. The specs' suggested function signatures (separate DataFrames per report) directly
   contradicted the envelope pattern Phases 3–5 already established. This is the same
   category of conflict Phase 5's session hit with payment aging's suggested
   three-function split. Now that it's happened twice, should future phases assume the
   specs' "Suggested functions" sections are *always* stale relative to whatever the
   actual modules ended up returning, or does each case still need to be checked
   individually?

## On the Scope Gate as a mechanical check versus a judgment call

6. `context/build-plan.md` describes `operations_follow_up_pack.xlsx` as merely
   "optional," but its actual source spec labels it V1.5. If the Scope Gate check had
   relied on `build-plan.md`'s phrasing instead of tracing the feature to its original
   spec section, Phase 6 would likely have built it. What does this suggest about how
   much a build plan or progress tracker should be trusted as a scope authority versus
   treated as a summary that still needs verification against the underlying specs?
7. The CRM Data Issues sheet (item 9 of the excluded operations pack) is out of scope
   for two independent reasons at once — it's part of a V1.5 feature, and it depends on
   the entirely-out-of-scope CRM Cleaner module. Is a feature excluded by two
   overlapping Scope Gate reasons meaningfully "more out of scope" than one excluded by
   a single reason, or is scope binary once any exclusion applies?

## On the sheet-derivation rules that emerged (write-as-is vs. filter)

8. `Backorders` is written as-is from `InventoryAllocationResult.backorders` (already
   filtered inside `inventory_allocation.py`), while `Follow-up List` has to be derived
   by `report_export.py` filtering `aging_rows`, because `PaymentAgingResult` has no
   equivalent precomputed field. Should this asymmetry between the two modules'
   envelopes be considered a design inconsistency worth fixing in a future phase (e.g.
   adding a `follow_up_rows` field to `PaymentAgingResult`), or is "report_export.py
   sometimes has to filter, sometimes doesn't" an acceptable, permanent consequence of
   each module's envelope being shaped by its own spec rather than a shared convention?
9. The rule that emerged — "if the envelope already has the list, use it; only derive
   a sheet by filtering when no matching field exists" — is a report_export.py-specific
   convention, not something stated in any spec. Where should a convention like this
   live once it's discovered: a comment in the code, `code-standards.md`, or nowhere
   beyond the architect session that produced it?

## On the two data-cleanliness corrections (`_safe_cell_value`, header hex framing)

10. `_safe_cell_value` wasn't in the original plan at all — it was a gap, not a wrong
    decision. Given the project's sample data is deliberately designed to include
    "realistic imperfections" including blank cells, was this gap actually likely to
    surface as a real bug on the very first test run against `sample_orders.xlsx`, or
    was the correction addressing a more theoretical risk? How would you have caught
    this gap during the original planning pass, before the user had to catch it?
11. The header-fill-color correction didn't change the underlying technical conclusion
    (the UI-token rule doesn't govern openpyxl) — it changed how that conclusion was
    *presented* in the plan, from a blanket exemption claim to a self-documenting named
    constant. Is this distinction — "right answer, wrong framing" — a category of
    planning mistake that's fundamentally different from getting the technical answer
    wrong, and does it deserve a different kind of scrutiny during plan review?

## On defensive coding for inputs that are already validated upstream

12. The `Follow-up List` allow-list (`{"High", "Medium", "Low", "Watch"}`) versus a
    `!= "None"` exclusion produces identical behavior today, since `payment_aging.py`
    only ever emits five known priority strings. The correction changes *only* the
    failure direction for a hypothetical future input that doesn't exist yet. Given
    `report_export.py`'s whole design principle is "trust the envelope, don't
    revalidate," is adding this kind of defensive allow-list actually consistent with
    that principle, or is it a small, justified exception to it? Where's the line
    between reasonable defense-in-depth and the kind of speculative validation the
    project's own coding standards discourage ("don't add validation for scenarios that
    can't happen")?
13. `_safe_cell_value` is a genuine bug fix (NaN cells are a near-certainty), while the
    allow-list change is a hardening choice against an input that can't currently occur.
    Both arrived in the same correction message. Should these be weighted differently
    when deciding what to prioritize if time were constrained — e.g., is one "must fix
    before merging" and the other "nice to have"?

## On the manual-verification boundary

14. The correction distinguishing `openpyxl.load_workbook()` structural checks (fine to
    run automatically) from actually opening a workbook in Excel/Preview (needs
    permission first) draws a line between "test the code" and "launch an application."
    What other verification steps in this project might cross a similar boundary
    without it being as obvious as "open a GUI app" — e.g., would sending a generated
    report as an email attachment, or opening a localhost URL in a browser, fall on the
    same side of this line?
15. If a future phase needs genuine visual/formatting verification (not just structural
    correctness) — for instance, confirming a chart renders correctly, or that column
    widths actually look reasonable rather than just being set to *some* value — what
    would an automated equivalent look like that doesn't require asking permission to
    open a desktop application every time?

## On what this session implies for report_export.py's actual boundaries

16. `report_export.py` is designed to never write to disk, only return bytes. The
    future FastAPI layer is expected to handle persistence/serving. If a later phase
    discovers report_export.py *does* need some disk-adjacent responsibility (e.g.
    caching a generated report to avoid recomputation), would that belong in
    `report_export.py` itself, in the future API route, or in a new module — and how
    would you decide, given the module-boundary table doesn't currently anticipate this?
17. The explicit-column-constants decision (never deriving headers from `dict.keys()`)
    was motivated by two failure modes: empty lists and `NotRequired`-field asymmetry
    between rows. Are there other places in this codebase (or likely to appear in
    future phases) where a similar "derive from data vs. derive from the contract
    definition" choice matters, and does the same reasoning apply each time, or does it
    depend on specifics?
