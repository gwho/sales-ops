# Phase 3: Order Validation Core — AI Discussion Topics

## On resolving contradictions in a source spec

1. Rule OV-001 and Rule OV-007 literally contradict each other on `payment_terms`'s severity. What signals were used to decide OV-007 should win (more specific rule, explicit severity in the example table) rather than OV-001 (the more generic, earlier-listed rule)? When would the opposite resolution — the earlier/broader rule wins — be the more defensible call?
2. This conflict was caught by working through a concrete "which fields does OV-001 actually check" question during planning, not by reading the spec start to finish. What's a systematic way to find every place a source-of-truth document contradicts itself before code depends on the wrong interpretation?

## On rule granularity and error-message design

3. The decision to emit one `ValidationErrorRow` per missing OV-001 field (instead of one combined message per row) trades a longer error table for more actionable repair information. What's the threshold where "one row, N errors" becomes too noisy for a human reviewing a table, and how would you redesign the UI (not the data) to manage that instead of coarsening the data?
4. OV-003 and OV-005 were each split into sub-codes (`OV-003-UNKNOWN_SKU` vs `OV-003-INACTIVE_SKU`; three `OV-005-*` variants) that don't exist in the original spec's rule numbering. Is inventing sub-codes a deviation from the spec, or a legitimate refinement of it? What would make a future reviewer trust this decision versus see it as unauthorized scope drift?

## On defensive parsing at a module boundary

5. `_parse_quantity` and `_normalize_active` both use "convert to string and pattern-match" as a fallback for types that don't cleanly match `isinstance` checks (numpy scalar types boxed in object-dtype Series). Is this an elegant unification or a code smell masking a type-system gap? What would the numpy-aware version look like, and is it worth the added import/coupling?
6. Malformed quantity and malformed dates both convert to business-readable errors instead of raising. What's the actual boundary between "this is data quality the business user needs to fix" (return a `ValidationErrorRow`) and "this is a programming bug" (let it raise) — and does that boundary hold if the input file format changes (e.g. CSV instead of `.xlsx`)?

## On summary statistics with overlapping categories

7. `invalid_orders` is deliberately computed as a distinct-row count rather than summed from `duplicate_orders + invalid_skus + missing_field_count`, specifically to avoid double-counting a row that fails multiple rules. What other summary/KPI fields in this project (`AllocationSummary`, `PaymentAgingSummary`) might have the same double-counting risk once Phase 4/5 are implemented, and how would you audit for it systematically instead of catching it ad hoc?

## On testing order and determinism

8. `test_errors_are_ordered_by_row_then_rule_then_field` locks in an ordering that wasn't explicitly required by the spec — it emerged from wanting stable test assertions and a predictable future UI table. Is testing an implementation choice like this (rather than a spec-mandated rule) good practice or over-specification? What would you lose if this test were deleted?

## On the overall Phase 3 boundary

9. `order_validation.py` fills `product_name` from `product_master_df` when the order row's own value is blank, even though the spec never explicitly describes this fallback behavior — it was inferred from "product master is the reference file." Is this the kind of small, reasonable inference that's fine to make without a new ADR, or does it cross into the same "don't invent business outcomes" territory the Field Scope Boundary warns about for UI work?
10. `OrderValidationResult` was kept local to `order_validation.py` rather than promoted into `src/contracts.py`. Now that Phase 3 is done, what would have to be true about Phase 4/5's own result envelopes for this precedent to still make sense — and what would be the tell that a shared "module result wrapper" pattern belongs in `contracts.py` after all?
