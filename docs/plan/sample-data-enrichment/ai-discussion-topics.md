# AI Discussion Topics — Feature sample-data-enrichment: Sample Data Enrichment

## Planning docs as input vs. schema authority

1. `sample_excel_data_requirements/` proposes `customer_id`, credit-status logic, and several optional product-master columns (`unit_price`, `default_supplier`) that never made it into the final generator. Walk through exactly why each was rejected — what's the test for "this is fine as reference data" vs. "this is scope creep"?
2. `sample_customers.xlsx` was generated but no `src/` function reads it. What would have to change — in `excel_io.py`, in a new module, in `contracts.py` — for it to become a real dependency, and why does `CLAUDE.md`'s Scope Gate require an ADR before that happens rather than just a code review?
3. If a future contributor didn't know this history and added a `load_customers()` helper "for consistency" with the other four loaders, what's the fastest way to catch that in review?

## Issue-ratio and combined-issue row design

4. The first plan draft gave every issue type its own row (~10+ issue rows); the shipped version combines issues onto 7 rows (~19%). What's actually being protected by keeping that ratio in the 15–20% band — who or what would be hurt by a sample dataset that looked more like a test matrix?
5. `SO-2026-032` combines a missing `sku` with a blank `payment_terms`. Why is that combination "realistic" but, say, combining "duplicate order_id" with "negative quantity" on the same row might not be? Is there a general principle here, or was it a case-by-case judgment call?
6. `test_generate_orders_row_count_and_issue_ratio_stay_moderate` hardcodes the set of issue-bearing order_ids and adds 1 for the duplicate row. What breaks first if someone adds an 8th issue row without updating this test's `issue_order_ids` set — does the test fail, silently under-count, or silently over-count?

## Allocation engine mechanics

7. Walk through exactly what happens to `SO-2026-010`'s two rows (the clean `PART-BULB-013` order and the duplicate `DIAG-TONO-007` order) from `validate_orders()` through `allocate_inventory()`. At what point does the "clean-looking" first occurrence get excluded, and would a downstream user ever see *why* it was excluded without reading `error_message`?
8. `PART-CAL-015` has zero inventory rows — that's the mechanism used to guarantee a full backorder. What's the difference, from `allocate_inventory()`'s perspective, between "SKU has zero inventory rows anywhere" and "SKU has inventory rows but `allocatable_qty = 0` everywhere"? Do they produce identically-shaped `BackorderRow`s?
9. `DIAG-OCT-005`'s HK Warehouse ended up as an *unplanned* third supplier-follow-up case (only two were hand-designed: `DIAG-TONO-007` and `DIAG-AUTO-008`). Was that emergent behavior a lucky accident of the chosen quantities, or was it actually foreseeable from the reorder_point/available_qty numbers before running the pipeline?
10. The warehouse-pick rule always chooses the single highest-`allocatable_qty` warehouse per order line, never splitting one order across two warehouses. If a future spec change wanted to allow split fulfillment, what would have to change in `inventory_allocation.py`, and would any of this sample data's "guaranteed" cases (the partial/backorder/reorder-alert trio) still work the same way?

## Payment aging and the overpayment test bug

11. The `paid_amount > invoice_amount` overpayment check false-positived on a row with negative `invoice_amount`. Are there other places in this generator (or in `payment_aging.py` itself) where two independently-valid "this row is broken in one specific way" conditions could interact to produce a misleading result if combined naively?
12. `payment_status` is explicitly documented as decorative — `payment_aging.py` derives bucket/priority from dates and amounts only. If a future contributor added a row where `payment_status="Paid"` but `paid_amount < invoice_amount` (a genuine, uncorrected data-entry contradiction, not the deliberate overpayment case), what would `calculate_payment_aging()` actually report, and is that the right behavior for a "decorative" column?
13. INV-2026-025 and INV-2026-026 (both order_id-less) were placed deliberately outside the SO-2026-0xx order chain. What's the argument for making some invoices *not* trace back to a generated order, versus making every invoice traceable for a cleaner demo narrative?

## Process: Plan Mode as `/architect`, and iterative correction

14. The plan went through two `ExitPlanMode` rejections before approval — one substantive (scenario/ratio/schema corrections), one procedural (asking for an explicit skill-usage section). What made the second rejection worth a full plan-file edit rather than just a conversational answer, given that plan mode was about to end anyway?
15. This session treated the harness's built-in Plan Mode as satisfying `08_agent_instructions_with_skills.md`'s "`/architect` before coding" requirement rather than invoking both. What's the risk in that substitution — is there anything `/architect` as a named skill would have forced that free-form Plan Mode didn't?
