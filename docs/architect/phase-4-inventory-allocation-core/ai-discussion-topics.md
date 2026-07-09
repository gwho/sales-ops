# Phase 4: Inventory Allocation Core — AI Discussion Topics

## On resolving spec ambiguity that isn't a contradiction

1. IA-007's "highest available quantity" wasn't a contradiction between two rules (unlike
   Phase 3's OV-001/OV-007 conflict) — it's one phrase compatible with two readings because an
   earlier rule (IA-002) had already defined a more precise derived term. What's a general way
   to *notice* this kind of latent ambiguity before it becomes a bug, given that nothing in the
   text technically conflicts?
2. The resolution (use `allocatable_qty`) was justified by "this keeps the spec internally
   consistent with the definition it already gave us," not by any explicit textual signal in
   IA-007 itself. Is "prefer the reading that keeps adjacent rules consistent" a reliable
   general heuristic, or could it override what a domain expert actually meant by the literal
   words in a case where the literal words really were intentional?
3. If IA-007 had instead said "highest **on-hand** quantity" — a term with no prior technical
   definition in the spec — would that unambiguously mean `available_qty`? What word choice
   would have made the raw-column reading unambiguous, and is that level of precision realistic
   to expect from a product spec versus something you should always double-check?

## On stateful, order-dependent business logic

4. `allocate_inventory` mutates shared dictionaries as a side effect of iterating orders in a
   specific sequence, rather than threading an immutable balance through a pure function. What
   would change about testability or debuggability if this were rewritten to be side-effect-free
   — and is the current approach's simplicity worth the mutation risk in a function this size?
5. The correctness of every downstream status depends on IA-001's sort running *before*
   allocation starts, with no assertion anywhere that verifies the sort actually happened
   correctly. What test would catch "the sort is subtly wrong" (e.g. tie-break order reversed)
   as opposed to "the sort is completely missing"?
6. Because warehouse choice is re-evaluated per line rather than decided once per SKU, the same
   SKU can be fulfilled from different warehouses across different lines in one batch as stock
   depletes. Is this dynamic re-evaluation the only sane reading of IA-007, or could "pick one
   warehouse per SKU for the whole batch, upfront" also be defended from the spec text — and
   what would the sample data's `MED-LENS-001` scenario look like under that alternative?

## On inferring behavior the spec never describes

7. The `warehouse=""` vs "best candidate warehouse" decision for backordered lines was resolved
   partly by treating a Phase-2-authored test fixture as evidence of intended behavior, even
   though that fixture predates any Phase 4 implementation. When should a pre-existing fixture
   be treated as a signal worth weighting, and when is it just one person's earlier guess with
   no more authority than any other inference you'd make today?
8. If the fixture and the first-principles operational argument ("useful routing hint") had
   *disagreed*, which should win — and how would you decide, given that changing the fixture is
   also an option?
9. `SupplierFollowUpRow` was kept scoped strictly to IA-008's literal trigger, deliberately
   narrower than `CONTEXT.md`'s glossary description. Is a glossary entry ever authoritative
   enough to expand implemented scope on its own, or should every scope expansion always require
   a new ADR regardless of how the glossary reads? Where's the line between "glossary as
   descriptive color" and "glossary as an unwritten rule"?

## On failure handling and where a problem belongs

10. Phase 3 converts malformed order data into structured `ValidationErrorRow` entries; Phase 4
    raises an exception for the analogous inventory-data problem, because no equivalent output
    contract exists yet. Is "we don't have a contract for this, so raise" a durable rule for the
    rest of this project, or a sign that Phase 4 is *missing* a contract (an `InventoryDataIssueRow`,
    mirroring `PaymentDataIssueRow`'s Phase 2 addition) that should exist via a new ADR?
11. If `InventoryDataIssueRow` were added later, would the change belong in the *loader*
    (`load_inventory`) or in `allocate_inventory` itself? What's the right boundary between "the
    file structurally can't be trusted" (a loader's job) and "one specific cell's value is bad"
    (a business-logic concern)?
12. `_require_quantity` raises for a malformed `available_qty`, but `_optional_quantity` silently
    returns `None` for a malformed (not just blank) `reorder_point` or `lead_time_days`. Is
    silently swallowing a *malformed-but-present* optional value the right call, or should that
    specific case (present, non-blank, but unparseable) be distinguished from a truly blank cell
    and handled differently?

## On summary statistics and what a count is actually answering

13. `low_stock_sku_count` (distinct SKUs) and `len(supplier_follow_ups)` (warehouse-level rows)
    are both legitimate numbers, easy to conflate, and answer genuinely different operational
    questions. Now that this distinction exists in Phase 4, does `PaymentAgingSummary` (Phase 5)
    have an analogous risk — a count that could mean "distinct invoices" or "distinct customers"
    depending on which the KPI card actually needs?
14. This is the second phase in a row (after Phase 3's `invalid_orders` distinct-row-count
    decision) where a naive "sum the category counts" implementation would have silently
    double- or over-counted something. Is there a systematic way to catch this class of bug —
    a review checklist item, a property-based test, a naming convention that makes "distinct
    count" vs "row count" unambiguous at the call site — rather than relying on someone noticing
    it by inspection each time?

## On boundary conditions and what test coverage actually proves

15. Every test case in the spec's own §11 table happens to produce identical output whether the
    reorder-alert comparison uses `<` or `<=` — the divergent case only shows up at exact
    equality, which the spec's examples never hit. What other rules in this module (or in
    Phase 3/5) might have a similar "the spec's own examples never test the boundary" blind
    spot, and how would you audit for that systematically instead of catching it by chance?
16. `test_remaining_qty_equal_to_reorder_point_does_not_alert` now locks the strict-inequality
    behavior in as a tested contract. If a future spec revision changed IA-008's wording from
    "below" to "at or below," would you expect that test to fail loudly, or could a careless
    edit change the comparison operator without any existing test catching it?

## On process discipline: verifying state before acting on it

17. The first plan draft assumed local `main` and PR #2's merge state without checking either at
    planning time — an assumption that turned out to be wrong by the time execution happened.
    What's the general principle for deciding which parts of a plan need a "verify immediately
    before executing" step versus which parts are safe to plan once and trust?
18. The corrected verification chain routes `sample_orders.xlsx` through `validate_orders()`
    before allocation, because the sample file is deliberately not fully valid on its own. If a
    future Phase 5 sanity check needed to chain off *both* Phase 3's and Phase 4's outputs, what
    would the equivalent "don't skip the upstream filtering step" mistake look like there?
19. The final sanity check reproduced `tests/contract_fixtures.py`'s hand-authored values exactly.
    What does that agreement actually prove about correctness, and what does it *not* prove —
    and is "matches a fixture written before the code existed" meaningfully stronger evidence
    than "matches a fixture written after," or is it the same strength either way?

## On scope boundaries across the whole module

20. IA-007's Optional V2 region-matching preference was excluded per the Scope Gate without
    much discussion — it's clearly labeled Optional/V2 in the spec, so there's no ambiguity to
    resolve. Contrast that with the Supplier Follow-up scope question (topic 9), where the
    "extra" behavior wasn't labeled V2 at all, just implied by looser glossary prose. Which kind
    of scope creep is more dangerous to a project like this — the kind that's clearly labeled
    and easy to say no to, or the kind that never gets a version label because nobody thought to
    ask whether it needed one?
