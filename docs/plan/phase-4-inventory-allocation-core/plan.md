# Phase 4: Inventory Allocation Core — Plan

## What was built

| Artifact | Purpose |
|---|---|
| `src/inventory_allocation.py` | `load_valid_orders`, `load_inventory`, `allocate_inventory`, and the local `InventoryAllocationResult` envelope. Implements every rule in `02_demo_inventory_allocation.md` (IA-001–IA-006, IA-008). |
| `tests/test_inventory_allocation.py` | Every spec §11 test case plus edge cases resolved during `/architect`: sort tie-breaking at each level, missing `reserved_qty`, warehouse choice switching mid-batch as stock depletes, zero-inventory SKU, missing `reorder_point`, the `remaining_qty == reorder_point` boundary, `low_stock_sku_count` distinct-SKU counting, malformed/blank required inventory values, and loader column-vs-value tests. |

`uv run pytest` passes — 85 tests (63 from Phases 1–3, 22 new).

## Why this order

`context/build-plan.md` Phase 4 is the second business-rule module, consuming Phase 3's validated order output against inventory data. It depends on Phase 1's `excel_io.py`/`contracts.py` and Phase 2's proof that the contract shapes hold real demo data, but does not depend on payment aging. No UI, FastAPI, report export, or payment-aging logic is included — those stay out of scope per the Scope Gate. The Optional V2 region-matching warehouse preference in IA-007 is explicitly excluded.

## Key decisions (resolved via `/architect` before implementation)

1. **Result envelope, not a tuple**: `allocate_inventory()` returns a single `InventoryAllocationResult` dict (`{"summary", "allocation_results", "backorders", "remaining_inventory", "supplier_follow_ups"}`), defined locally in `inventory_allocation.py` rather than added to `src/contracts.py` — mirrors Phase 3's `OrderValidationResult` pattern rather than the spec's suggested plain-DataFrame-tuple signature.
2. **Warehouse choice uses `allocatable_qty`, not raw `available_qty`**: IA-007 V1 compares `available_qty - reserved_qty` (floored at 0) across warehouses for a SKU — the spec's literal "highest available quantity" phrasing was ambiguous between the raw column and the derived ceiling; the derived value was chosen so a warehouse that looks full on paper but is mostly reserved doesn't win. Ties are broken by warehouse name ascending (the spec defines no tie-breaker).
3. **Stateful, per-line allocation, single warehouse per line**: orders are processed strictly in IA-001 order (priority → requested delivery date → order date → order ID), one line at a time, mutating a running per-(sku, warehouse) allocatable balance as each line is filled. Warehouse choice can change between lines for the same SKU as stock depletes. A single order line is filled from exactly one warehouse — matches IA-004's "allocate the available amount and backorder the remaining," not a cross-warehouse split.
4. **Backorder/no-inventory `warehouse` field**: if the SKU has any inventory rows, `warehouse` is still the best candidate even when `allocated_qty == 0` (matches the pre-existing `BACKORDER_ROW_FIXTURE`). If the SKU has zero inventory rows anywhere, `warehouse = ""`.
5. **Supplier Follow-up scoped strictly to IA-008**: a (sku, warehouse) row gets a `SupplierFollowUpRow` only when `reorder_point` is present and `remaining_qty` is strictly below it, evaluated once per (sku, warehouse) after the full batch is allocated. Not triggered by backorder status alone, despite `CONTEXT.md`'s broader glossary phrasing ("stock is low, backordered, or below reorder point") — the only numbered rule that defines a trigger is IA-008.
6. **`remaining_qty = starting_available_qty - allocated_qty`**: matches spec §6's column table, which defines `remaining_qty` purely in terms of `starting_available_qty` and `allocated_qty`. `reserved_qty` only gates allocation eligibility via `allocatable_qty`; it isn't subtracted again in the output.
7. **`low_stock_sku_count` is a distinct-SKU count**: counts SKUs with at least one alerting (sku, warehouse) row, not the number of `SupplierFollowUpRow` entries — a SKU stocked (and alerting) in two warehouses counts once.
8. **Reorder threshold is strict**: `remaining_qty < reorder_point` triggers the alert; `remaining_qty == reorder_point` does not, per IA-008's literal "below reorder_point" wording.
9. **Malformed required inventory values raise, they don't silently coerce**: `sku`, `warehouse`, and `available_qty` are required per spec §4 File 2; a present-but-blank or non-numeric `available_qty` raises the new `InvalidInventoryDataError` rather than defaulting to 0 or skipping the row — there's no `InventoryDataIssueRow` contract to report it as a soft error instead. Optional numeric fields (`reserved_qty`, `reorder_point`, `lead_time_days`) still degrade gracefully to "not present" when blank or unparseable.
10. **Loader vs. rule distinction**: `load_valid_orders`/`load_inventory` raise `MissingColumnsError` when a required *column* is absent — a structurally different problem from a present-but-invalid cell value, which `InvalidInventoryDataError` (for required fields) or graceful degradation (for optional fields) handles instead.

## Scope boundary held

- No payment aging, report export, FastAPI, or UI code touched.
- Only V1/unlabeled rules from `02_demo_inventory_allocation.md` implemented. IA-007's Optional V2 region-matching warehouse preference is explicitly **not** implemented.
- Exhaustive rule/edge-case coverage lives entirely in `tests/test_inventory_allocation.py`'s inline DataFrame fixtures, not in `sample_data/sample_inventory.xlsx`, per `context/code-standards.md`.
- Manually verified against `sample_data/sample_orders.xlsx` + `sample_data/sample_inventory.xlsx` (routed through Phase 3's `validate_orders()` first, since the sample orders file is not fully valid on its own) — output matches the hand-authored fixtures in `tests/contract_fixtures.py` field-for-field.
