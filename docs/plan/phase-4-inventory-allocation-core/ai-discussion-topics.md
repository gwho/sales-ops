# Phase 4: Inventory Allocation Core — AI Discussion Topics

## On resolving ambiguity the spec doesn't flag as a contradiction

1. Unlike Phase 3's OV-001/OV-007 conflict, IA-007's "highest available quantity" isn't a contradiction between two rules — it's a single phrase that's compatible with two different readings (`available_qty` vs. `allocatable_qty`) because IA-002 defines a derived quantity one rule earlier without IA-007 explicitly saying which one it means. What's the general tell that a spec phrase needs disambiguating even when nothing in the text technically conflicts?
2. The resolution (use `allocatable_qty`) was chosen because it's "the value the rest of the module already treats as usable stock," not because of any textual signal in IA-007 itself. Is "prefer internal consistency with an adjacent rule" a reliable tiebreaker in general, or does it risk quietly overriding what a domain expert actually meant by the literal words?

## On stateful, order-dependent business logic

3. `allocate_inventory` mutates shared dicts (`inventory_by_sku` entries) as a side effect of iterating orders in a specific sequence — a different design could thread an immutable balance through each call and return a new one. What would change about testability, debuggability, or correctness risk if the allocation loop were rewritten to be side-effect-free?
4. The correctness of the whole module depends on orders being processed in *exactly* IA-001's sort order before allocation starts — get that sort wrong and every downstream status is wrong too, with no exception thrown to catch it. What kind of test would catch "the sort is slightly wrong" as opposed to "the sort is completely missing"?

## On inferring behavior for cases the spec never mentions

5. The spec's test-case table (§11) never describes a SKU with zero inventory rows, or an order line that's fully backordered needing a `warehouse` value. Both behaviors were decided by inference — one from a pre-existing fixture (`BACKORDER_ROW_FIXTURE`), one from first-principles reasoning about what's operationally useful. Which of these two justifications is the stronger basis for a decision that isn't in the spec, and would you trust a fixture's implicit shape over your own reasoning if the two conflicted?
6. `SupplierFollowUpRow` was kept scoped to only IA-008's literal trigger, deliberately narrower than `CONTEXT.md`'s glossary description of "stock is low, backordered, or below reorder point." The Scope Gate says only numbered V1/unlabeled rules get implemented — but a glossary entry isn't a numbered rule, so is it authoritative at all, or just descriptive color? What's the rule for when a glossary term should expand what gets built versus when it's just loose prose?

## On failure modes and where they belong

7. Phase 3 converts malformed order data into structured error rows (`ValidationErrorRow`); Phase 4 raises an exception (`InvalidInventoryDataError`) for the analogous problem in inventory data, because no equivalent output contract exists. Is "we don't have a contract for this, so raise instead" a good long-term rule, or does it mean Phase 4 is missing a contract that should be added via ADR (an `InventoryDataIssueRow`, mirroring `PaymentDataIssueRow`'s addition in Phase 2)?
8. If a future ADR did add `InventoryDataIssueRow`, would that change change change the *loader* (`load_inventory`), the *allocation function* (`allocate_inventory`), or both? Where's the right boundary between "the file structurally can't be trusted" (loader's job) and "a specific cell's value is bad" (allocation's job)?

## On summary statistics and what a number is actually answering

9. `low_stock_sku_count` (distinct SKUs) and `len(supplier_follow_ups)` (warehouse-level rows) are both legitimate, both already computed, and easy to accidentally conflate. Now that this distinction exists for Phase 4, does `PaymentAgingSummary` in Phase 5 have an analogous risk — some count that could mean "distinct invoices" or "distinct customers" depending on which one a KPI card actually needs?
10. This is the second phase in a row (after Phase 3's `invalid_orders` distinct-row-count decision) where a naive "sum the sub-counts" implementation would have silently double-counted something. Is there a way to catch this class of bug systematically — a review checklist, a property-based test, a naming convention — rather than relying on remembering it happened twice?
