# Phase 4: Inventory Allocation Core — Architectural Decisions

Eight decisions came out of this `/architect` session: four resolved up front via a batched
`AskUserQuestion` round, and four more surfaced by the user during a correction pass after
the first plan draft was rejected. Each section covers what was decided, how it's implemented,
why it beat the alternative, and what the alternative would have cost.

---

## 1. Result envelope: local TypedDict, not the spec's DataFrame tuple

**What:** `allocate_inventory()` returns a single `InventoryAllocationResult` TypedDict —
`{summary, allocation_results, backorders, remaining_inventory, supplier_follow_ups}` —
defined locally inside `inventory_allocation.py`, not added to `src/contracts.py`.

```python
class InventoryAllocationResult(TypedDict):
    summary: AllocationSummary
    allocation_results: list[AllocationResultRow]
    backorders: list[BackorderRow]
    remaining_inventory: list[RemainingInventoryRow]
    supplier_follow_ups: list[SupplierFollowUpRow]
```

**Why over the alternative:** `sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md`
§10 literally suggests `allocate_inventory(...) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]`.
That signature is a reasonable *early implementation hint*, but it conflicts with the direction
already set by Phase 3 and by `contracts.py`'s own docstring ("JSON-serializable output-contract
shapes shared across business modules and the future API/UI boundary"). A raw `pd.DataFrame`
isn't JSON-serializable without a conversion step, and Phase 3's `OrderValidationResult` had
already established the "local envelope wrapping typed dict lists" pattern as the project's
convention for a module's top-level result.

**Cost of the DataFrame-tuple alternative:** every consumer (Phase 6's report export, a future
FastAPI route, this session's own sanity-check script) would need to know how to convert
DataFrames to the contract dict shapes, and that conversion logic would either be duplicated
per-consumer or awkwardly bolted onto the business-logic module. Returning the contract shapes
directly means `allocate_inventory()`'s output *is* the API response body, with no adapter layer.

---

## 2. Warehouse-selection metric: `allocatable_qty`, not raw `available_qty`

**What:** IA-007 V1's warehouse choice compares `available_qty - reserved_qty` (floored at 0)
across candidate warehouses for a SKU — not the raw `available_qty` column.

```python
def _pick_warehouse(entries: list[dict]) -> dict:
    """IA-007 V1 — warehouse with the highest allocatable_qty for the SKU; ties broken by warehouse name."""
    return sorted(entries, key=lambda e: (-e["allocatable_qty"], e["warehouse"]))[0]
```

**Why over the alternative:** the spec text is genuinely ambiguous. IA-007 says "highest
available quantity," which taken completely literally names the `available_qty` column. But
IA-002, one rule earlier, defines `allocatable_qty = available_qty - reserved_qty` as *the*
quantity actually usable this round. The user's own reasoning locked this in: "if `available_qty`
is partly reserved, choosing by raw `available_qty` can select a warehouse that cannot fulfill
as much as another warehouse with lower raw stock but higher usable stock."

**Cost of the raw-`available_qty` alternative:** a warehouse showing `available_qty=50,
reserved_qty=48` (2 usable) could be chosen over one showing `available_qty=20, reserved_qty=0`
(20 usable) — routing every order to the warehouse least able to fulfill it, silently, with no
error or warning anywhere in the output. This is the kind of bug that would only surface once
someone manually cross-checked allocation output against physical stock.

**Tie-breaker, decided alongside this:** warehouse name ascending. The spec defines no
tie-breaker at all; ascending name was picked purely for determinism (matches the project's
established pattern from Phase 3 — every ordering decision gets pinned down explicitly rather
than left to whatever order the underlying data structure happens to iterate in).

---

## 3. Stateful, per-line allocation with single-warehouse-per-line

**What:** orders are processed one at a time, strictly in IA-001 sort order (priority →
requested delivery date → order date → order ID), each line mutating a shared running balance
keyed by `(sku, warehouse)`. A single order line is filled from exactly one warehouse — never
split across two.

```python
chosen["allocatable_qty"] -= allocated_qty
chosen["allocated_qty"] += allocated_qty
```

This line runs inside `_allocate_order_line`, mutating the same dict object stored in
`inventory_by_sku`, so the *next* order line sees the depleted balance immediately.

**Why over the alternative:** this wasn't asked as an `AskUserQuestion` — it was stated as an
assumption in the plan and implicitly confirmed when the user approved the plan without
objecting to it. The reasoning: IA-001's whole point is that a High-priority order must win
outright over a competing Normal-priority order for the same SKU, not receive a proportional
share. That only falls out correctly if allocation is sequential and stateful. A batch/vectorized
approach (sum all orders per SKU, sum all inventory per SKU, distribute) can't reproduce
strict priority precedence — it would naturally gravitate toward some kind of proportional or
first-come split, which isn't what IA-001 describes.

**Cost of the alternative (split allocation across warehouses per line):** IA-004's wording
("allocate the available amount and backorder the remaining") reads as single-warehouse — the
"remaining" becomes a *backorder*, not a search for a second warehouse. Allowing a line to pull
partial stock from two warehouses simultaneously would be a materially more complex algorithm
(multi-warehouse fulfillment, split shipments) that the spec's language doesn't ask for and the
test-case table (§11) never exercises.

---

## 4. Backorder / no-inventory `warehouse` field population

**What:** if the SKU has *any* inventory rows, `warehouse` is still populated with the best
candidate (per decision #2) even when `allocated_qty == 0`. Only when the SKU has *zero*
inventory rows anywhere does `warehouse` become `""`.

```python
if entries:
    chosen = _pick_warehouse(entries)
    warehouse = chosen["warehouse"]
    ...
else:
    warehouse = ""
    allocated_qty = 0
    status = "Backordered"
```

**Why over the alternative:** the spec's test-case table never describes this situation at all
— it was resolved by reading a signal outside the spec text. `tests/contract_fixtures.py`
(authored during Phase 2, before any Phase 4 rule was implemented) already contained
`BACKORDER_ROW_FIXTURE` with a populated `warehouse` value on a zero-`allocated_qty` row. The
user's stated reasoning: "it preserves the operational answer 'where would this be fulfilled
from once stock arrives?' ... gives the future UI/report a useful routing hint."

**Cost of the "always blank on zero allocation" alternative:** it's defensible in isolation
(no warehouse *actually* shipped anything), but it throws away real information — which
warehouse the reorder alert and supplier follow-up should be routed to — and it would have
broken the sanity check against `tests/contract_fixtures.py`, since that fixture was written
with a populated warehouse.

---

## 5. Supplier Follow-up trigger scope: IA-008 literal text only

**What:** a `(sku, warehouse)` combination gets a `SupplierFollowUpRow` only when
`reorder_point` is present *and* `remaining_qty` is below it — never merely because a line was
backordered.

```python
reorder_alert = "Yes" if reorder_point is not None and remaining_qty < reorder_point else "No"
...
follow_up: SupplierFollowUpRow | None = None
if reorder_alert == "Yes":
    follow_up = {...}
```

**Why over the alternative:** `CONTEXT.md`'s glossary defines Supplier Follow-up broadly —
"an operational follow-up item created when stock is low, backordered, or below reorder
point" — but the only *numbered rule* that defines an actual trigger condition is IA-008,
which only describes the reorder-point case. The user's reasoning: "Phase 4 should implement
the numbered V1 rule literally... Triggering follow-up rows for every backorder would expand
the rule beyond the spec and blur two different outputs: `BackorderRow` (demand could not be
fulfilled now) vs. `SupplierFollowUpRow` (remaining inventory is below its reorder threshold)."
This is the same Scope Gate discipline CLAUDE.md establishes project-wide — implement only
what a numbered V1/unlabeled rule says, treat glossary prose as descriptive color, not an
independent source of rules.

**Cost of the broader alternative:** every backordered line with no known `reorder_point`
would need a `SupplierFollowUpRow`, but `SupplierFollowUpRow.reorder_point` is a *required*
field in `contracts.py` (not `NotRequired`) — there'd be no valid value to put in it, forcing
either a contract change (out of scope without a new ADR) or a fabricated placeholder value.
It would also have collapsed two operationally distinct signals — "we're out of stock right
now" and "we need to reorder before we run out" — into one undifferentiated list.

---

## 6. `remaining_qty` formula: against `starting_available_qty`, not `allocatable_qty`

**What:** `remaining_qty = starting_available_qty - allocated_qty`. `reserved_qty` is not
subtracted a second time in the output.

**Why:** spec §6's Remaining Inventory column table defines `remaining_qty` purely in terms of
`starting_available_qty` ("Original available quantity") and `allocated_qty` ("Total allocated
quantity") — `reserved_qty` doesn't appear in that table at all. `reserved_qty`'s only job is
gating *how much could be allocated* via `allocatable_qty`; reserved stock is still physically
sitting in the warehouse, so it shouldn't be subtracted twice from what the report calls
"remaining."

**Cost of subtracting `reserved_qty` again:** `remaining_qty` would under-report physical stock
on hand, and it would silently diverge from the fixture values in `tests/contract_fixtures.py`
(which show `remaining_qty` computed directly from `starting_available_qty - allocated_qty`).

---

## 7. `low_stock_sku_count`: distinct-SKU count, not follow-up-row count *(added during correction round)*

**What:** `AllocationSummary.low_stock_sku_count` counts distinct SKUs with at least one
alerting `(sku, warehouse)` row — not the number of `SupplierFollowUpRow` entries.

```python
low_stock_skus: set[str] = set()
for entry in inventory_entries:
    remaining_row, follow_up_row = _build_remaining_inventory_row(entry)
    remaining_inventory.append(remaining_row)
    if follow_up_row is not None:
        supplier_follow_ups.append(follow_up_row)
        low_stock_skus.add(entry["sku"])
...
summary = _build_summary(allocation_results, len(low_stock_skus))
```

**Why this needed calling out explicitly:** the user caught this in the review round — it
wasn't part of the original four `AskUserQuestion` decisions. A SKU stocked (and alerting) in
two warehouses — exactly `MED-LENS-001` in the sample data, which alerts in both HK and SG
Warehouse — would report as "2 low-stock SKUs" under a naive `len(supplier_follow_ups)`
implementation, when it's actually one product needing attention with two separate restock
actions. This mirrors a bug class Phase 3 already had to solve once (`invalid_orders` computed
as a distinct-row `set`, not summed from category counts) — see `ai-discussion-topics.md` #19–20
for the discussion question this raised about auditing for the same risk elsewhere.

**Cost of counting follow-up rows:** the summary KPI overstates how many distinct products need
attention, which is exactly the number a merchandising/ops audience would read off a dashboard
first.

---

## 8. Reorder threshold is strict (`<`, not `<=`) *(added during correction round)*

**What:** `remaining_qty == reorder_point` does **not** trigger a reorder alert. Only
`remaining_qty < reorder_point` does.

**Why:** IA-008's literal wording is "remaining stock after allocation is **below**
`reorder_point`." "Below" means strictly less than; landing exactly on the threshold isn't
below it. The user flagged this specifically because it's an off-by-one class of bug that's
easy to get wrong silently — `<=` and `<` produce identical output for every test case *except*
the exact-equality boundary, so a wrong implementation could ship and pass every other test.

**Cost of getting this wrong:** a reorder point is meant to be "the level at which you should
already be reordering" — if `<=` were used, a warehouse sitting exactly at its safety threshold
(not yet below it) would trigger a supplier follow-up a cycle early, which is a real operational
difference, not just a semantic one. `tests/test_inventory_allocation.py::test_remaining_qty_equal_to_reorder_point_does_not_alert`
locks this boundary in as a tested contract.

---

## 9. Malformed required inventory data raises, it doesn't silently coerce *(added during correction round)*

**What:** a blank or non-numeric `available_qty` (or blank `sku`/`warehouse`) raises a new
`InvalidInventoryDataError`, rather than defaulting to 0 or silently dropping the row.

```python
class InvalidInventoryDataError(Exception):
    """Business-readable error for a required inventory value that is missing or not a valid whole number."""

    def __init__(self, row_number: int, field: str) -> None:
        self.row_number = row_number
        self.field = field
        message = (
            f"Inventory row {row_number} has a missing or invalid value for required field "
            f"'{field}'. Please check the sample template."
        )
        super().__init__(message)
```

**Why over the alternative:** this directly contradicts Phase 3's own precedent — Phase 3
converts every malformed order value into a business-readable `ValidationErrorRow` rather than
raising, specifically because `contracts.py` defines an output surface (`ValidationErrorRow`)
for exactly that case. Phase 4 has no equivalent — there's no `InventoryDataIssueRow` family in
`contracts.py`, and nothing in the spec describes a "soft" inventory data-quality report. The
user's explicit instruction: "Since there is no `InventoryDataIssueRow`, I'd raise a
business-readable `ValueError` or similar module-level exception, not silently coerce."

**Cost of silent coercion (e.g. defaulting bad `available_qty` to 0):** a malformed cell would
make a warehouse look phantom-empty without telling anyone why — every downstream allocation
decision for that SKU/warehouse would be silently wrong, and there'd be no error, no log, no
signal that anything happened. Failing loudly is strictly better here precisely *because* there's
no contract to report the problem softly.

**Note the asymmetry this creates on purpose:** optional numeric fields (`reserved_qty`,
`reorder_point`, `lead_time_days`) still degrade gracefully to "not present" when blank or
unparseable — this stricter fail-loud rule applies only to the required fields the spec's own
§4 table marks "Yes."

---

## Process decision: conditional branching on PR merge state *(added during correction round)*

Not a code-architecture decision, but a workflow one worth recording since it changed how the
plan's last step was written. The first plan draft assumed Phase 4 would branch from `main`
now that PR #1 had merged. The user caught that this was wrong: PR #2 (Phase 3) was *still
open* against `main`, and the local `main` checkout was stale — branching from it would have
produced a Phase 4 branch missing `src/order_validation.py` and the 63-test baseline entirely.

The plan was rewritten to make branching conditional, checked at execution time rather than
assumed at planning time:

```text
- If PR #2 has merged by the time Phase 4 starts: sync local main, branch from main.
- If PR #2 is still open: branch from phase/3-order-validation-core instead,
  stack the new PR on it.
- Do not branch from local main while PR #2 is still open and unmerged.
```

This is the same discipline as "verify before recommending" applied to git state rather than
code: a plan that names a specific branch/commit is a claim about state *at planning time*,
and that claim needs re-checking at execution time rather than trusted blindly.
