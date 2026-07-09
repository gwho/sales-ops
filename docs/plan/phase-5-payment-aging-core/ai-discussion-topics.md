# Phase 5: Payment Aging Core — AI Discussion Topics

## On priority rules that override the bucket they're computed alongside

1. High priority can fire from `outstanding_amount >= 50000` alone, completely independent of `days_overdue` — including on an invoice that isn't due yet (`aging_bucket = "Current"`, `follow_up_priority = "High"`). This was implemented literally because PA-005's `or` has no accompanying "and overdue" clause, and section 12's test table lists the amount trigger as a standalone case. If a domain expert looked at a "Current, High priority" row in the report, would that read as intentional urgency or as a bug — and does the literal-spec-reading defense actually survive that reaction?
2. Draft messages deliberately don't follow the same "amount alone triggers it" logic — a High-priority-by-amount, not-yet-due invoice gets no draft reminder, because section 8 only describes reminders "for each overdue customer." Now that priority and reminder-eligibility diverge on purpose, is there a risk a future feature (e.g. a "Follow-up List" UI view) accidentally uses `follow_up_priority == "High"` as its filter and pulls in a not-yet-due invoice that was never meant to appear there?

## On keeping `days_overdue` signed instead of flooring it

3. Flooring `days_overdue` at 0 for non-overdue rows was rejected because it would collapse "due in 2 days" and "due in 200 days" into the same value, breaking Watch's `-7..0` window. Is there a comparably clean way to express Watch without a signed field, or was flooring genuinely a dead end here?
4. `PaymentAgingRow.days_overdue: int` can now be negative in the JSON contract a future Next.js UI consumes. What's the risk that a naive frontend renders a negative value as literal text ("-5 days overdue") instead of translating it to "due in 5 days," and whose job is it to prevent that — the Python layer, the API layer, or the UI layer?

## On asymmetric validation between two fields governed by the same rule family

5. `invoice_amount` failing to parse raises a PA-007 data issue and excludes the row; `paid_amount` failing to parse (including negative values, which the spec never discusses) silently defaults to `0.0`. This mirrors Phase 4's required-vs-optional field split, but Phase 5 has a `PaymentDataIssueRow` contract to report failures softly where Phase 4 had to raise a hard exception. Does having a soft-failure contract available change what "should" happen to an invalid optional field, or is "the spec never says to flag it" still the right bar regardless of whether flagging it would be easy?
6. Two explicit tests (`test_invalid_paid_amount_degrades_to_zero_no_data_issue`, `test_negative_paid_amount_degrades_to_zero_no_data_issue`) exist specifically to stop a future agent from "tightening" this behavior to match `invoice_amount`'s. Is a named regression test actually a strong enough guardrail against scope creep, compared to, say, a comment at the validation site itself?

## On paid invoices remaining visible in the aging table

7. The decision to keep Paid invoices in `aging_rows` (rather than filtering them out entirely) was inferred from three indirect signals — the "All Invoices with Aging" sheet name, section 7's `Paid → "No action required"` table row, and the absence of any carve-out in the output-columns table — none of which is a direct instruction. How confident should an implementation be when a decision rests entirely on naming and table-shape inference rather than an explicit sentence in the spec?
8. `total_invoices` counts every loaded row including data-issue rows, but `aging_bucket_counts` only counts `aging_rows`. A screen showing "10 total invoices" next to a bucket breakdown that sums to 8 could read as a bug to someone unfamiliar with the PA-006/PA-007 exclusion. Is that a UI-labeling problem to solve later (e.g. an explicit "2 invoices need attention" callout), or should the Python summary itself expose a reconciling count?

## On a fixture that turned out to be wrong, and what that implies about trusting fixtures

9. Phase 2's `DRAFT_MESSAGE_ROW_FIXTURE` hardcoded a `$` symbol for an invoice that's actually HKD — a mistake that existed, uncaught, from Phase 2 until Phase 5's implementation and sanity check surfaced it. Phase 4's explanation doc treated a similar pre-existing fixture (`BACKORDER_ROW_FIXTURE`) as authoritative evidence for an ambiguous design decision. Given that fixtures can themselves be wrong, what should change about how much weight a hand-authored Phase 2 fixture gets when it conflicts with, or is used to resolve, a Phase 3+ implementation decision?
10. The `invoice_date`/`due_date` one-day discrepancy was caught only because the sanity check happened to compare the *exact* real sample file's output against the fixture. If that manual check weren't run, would the mismatch have been caught by anything in `tests/test_contracts.py` or `tests/test_payment_aging.py`, or does it reveal a gap in what the automated suite actually verifies?

## On what happens when Phase 6 (Excel export) needs to combine this module's rows with the others'

11. `PaymentAgingResult`'s field names (`aging_rows`, `data_issues`, `draft_messages`) don't share a naming pattern with Phase 3's (`valid_orders`, `errors`) or Phase 4's (`allocation_results`, `backorders`, `remaining_inventory`, `supplier_follow_ups`) — each module picked names that read well for its own domain. When `report_export.py` needs to pull from all three envelopes to build sheets, does that naming inconsistency create any real friction, or is it a non-issue since each envelope is only ever destructured by key, never iterated generically?
