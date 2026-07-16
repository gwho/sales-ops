# Tutorial 04 — Inventory Allocation Core: From Trusted Rows to Depleting Stock

**After completing this tutorial you will understand:** why `allocate_inventory()` re-validates
required columns even though its input already passed through Phase 3's `validate_orders()`, why
IA-001's sort must run to completion *before* a single unit of stock is allocated, why
`allocatable_qty` (not raw `available_qty`) is the only number this module trusts as "usable
stock," why allocation has to mutate a shared, aliased dictionary in place rather than compute
each SKU's outcome independently, why a fully-backordered line still records which warehouse it
would have shipped from, why supplier follow-up has a narrower trigger than the project's own
glossary implies, and why `low_stock_sku_count` is a distinct-SKU count answering a different
question than `len(supplier_follow_ups)`.

> [!NOTE]
> **Prerequisites:** Tutorial 03 (`03-order-validation-core/README.md`) — this is a direct
> continuation. Phase 3 built `validate_orders()`, whose `valid_orders` output is this phase's
> primary input; the result-envelope pattern, the loader-vs-row-rule boundary, the
> distinct-row-count summary technique, and defensive parsing are all reused here, not
> re-explained. Tutorial 01 (`01-python-foundation/README.md`) — background on
> `MissingColumnsError`/exception translation and `TypedDict` contracts. Tutorial 02
> (`02-sample-data/README.md`) — background on why exhaustive rule coverage lives in
> `tests/test_inventory_allocation.py`'s inline DataFrames, not `sample_data/sample_inventory.xlsx`.
> Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py),
> [`src/contracts.py`](../../../src/contracts.py), and
> [`tests/test_inventory_allocation.py`](../../../tests/test_inventory_allocation.py) alongside
> this tutorial.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Aliasing: two indexes pointing at the same mutable object | `by_sku` and `entries` in `_build_inventory_state()` both hold *the same* `entry` dict per SKU/warehouse | Python language |
| Composite-key sort as an `ORDER BY` equivalent | `_sort_orders_for_allocation()`'s `(priority_rank, delivery_date, order_date, order_id)` key tuple | Algorithms |
| Dict-of-lists grouping (a poor man's multimap) | `by_sku: dict[str, list[dict]]` grouping inventory rows by SKU | Data structures |
| Greedy, order-dependent allocation | The entire `allocate_inventory()` loop — each line's outcome is locked in immediately and never revisited | Algorithms |
| Fail-fast vs. graceful-degradation as two validation strategies in one module | `_require_quantity()` (raises) vs. `_optional_quantity()` (degrades to `None`) | Design patterns |

## How to use an LLM before this tutorial

### Concept 1 — Stateful computation vs. pure computation

> "Explain the difference between a *pure* function (given the same inputs, always returns the
> same output, with no observable side effects) and a *stateful* one that mutates data as it goes
> and whose result for call N can depend on what happened in calls 1 through N-1. Give a concrete
> example where a real-world allocation or scheduling problem genuinely *requires* statefulness —
> not just as an implementation detail, but because the correct answer depends on processing order.
> Quiz me on whether a 'sum then divide proportionally' approach can ever produce the same result
> as processing requests one at a time in priority order."

*What to listen for:* a proportional/aggregate approach and a strict-priority sequential approach
produce genuinely different, both 'reasonable-sounding' answers whenever demand exceeds supply —
proportional allocation gives every claimant a fair share, while strict-priority allocation gives
the highest-priority claimant everything they asked for before the next claimant gets anything.
Neither is a bug; they're different specifications, and only one of them requires the process to
be stateful and order-dependent rather than computable as one aggregate pass.

*Practice question:* if 100 units of stock exist and three orders for 40 units each arrive with
priorities High, Normal, Normal, does "highest priority first, in full" ever produce a different
allocation than "share proportionally"? Work out both by hand.

### Concept 2 — Greedy algorithms and irrevocable decisions

> "Explain what makes an algorithm 'greedy': at each step, it makes the locally best choice
> available right now and never revisits that choice later, even if a different order of decisions
> might have produced a better overall outcome. Give an example of a real scheduling or allocation
> problem where a greedy approach is provably correct (produces the true optimal answer), and one
> where greedy is merely 'reasonable' but not guaranteed optimal. Quiz me on which category a
> strict-priority order-fulfillment system falls into."

*What to listen for:* greedy is correct/optimal precisely when the problem has a defined priority
total order (e.g., "always serve the highest priority claimant completely before touching the
next") — the 'optimal' outcome *is* whatever the greedy process for that exact tie-break rule
by definition produces. Greedy is *not* guaranteed optimal for a fundamentally different objective,
such as "maximize the total number of orders that are at least partially satisfied," where
processing in a different order could satisfy more distinct customers even if it makes the
top-priority customer wait.

*Practice question:* if a system's spec literally *defines* correctness as "process in this exact
priority order, first-come-first-served," is a greedy, one-pass, no-backtracking implementation a
compromise — or is it the only correct implementation the spec permits?

### Concept 3 — Disambiguating an underspecified phrase (not a contradiction)

> "In Tutorial 03 of this series, a business-rule spec had two *rules* that literally contradicted
> each other. This is a related but different problem: imagine a spec has a single rule that uses
> a phrase like 'the highest available quantity,' and a completely separate, earlier rule defines
> a *derived* quantity (e.g., 'available minus reserved') without the later rule ever saying which
> one it means. Explain why this is ambiguity, not contradiction, and why 'pick whichever reading
> keeps the module internally consistent with a concept it already defined' is a different kind of
> justification than 'the text explicitly says so.' Quiz me on when that justification is risky."

*What to listen for:* a contradiction has two rules making incompatible claims about the same
fact — there's no reading that satisfies both. An ambiguous phrase has *one* rule whose plain
words are compatible with more than one interpretation, and nothing in the rule's own text picks a
winner. Resolving ambiguity by "internal consistency with an adjacent, already-defined concept" is
a reasonable default, but it's not textual proof — it risks overriding what a domain expert
actually meant if their intent diverges from what reads as internally tidy to the implementer.

*Practice question:* if a future stakeholder said "no, IA-007 really did mean the raw `available_qty`
column, reserved stock or not," would anything in the rule's own text have been able to settle
that argument before this tutorial's Part 4?

### Concept 4 — Fail-fast vs. graceful degradation

> "In a data-processing pipeline, explain two different strategies for handling a field with a bad
> or missing value: (1) fail fast — stop processing immediately and report the exact problem, and
> (2) graceful degradation — treat the missing/bad value as 'not provided' and continue with a
> sensible default. Give one example of a field where fail-fast is clearly correct, and one example
> of a field where graceful degradation is clearly correct, and explain what makes them different.
> Quiz me with a made-up field and ask me to argue for one strategy over the other."

*What to listen for:* the deciding factor is usually whether the *rest of the system's correctness
depends directly* on that field's value. A field that flows straight into a core calculation
(e.g., a warehouse's stock count) is dangerous to silently default, because a wrong default
produces a plausible-looking but incorrect result nobody notices. A field that's purely
supplementary (e.g., an optional contact name) can safely degrade to "absent," because nothing
downstream computes anything incorrect from its absence — it just omits an optional detail.

*Practice question:* between a warehouse's stock count and a warehouse's supplier contact name,
which one, if silently defaulted to zero/blank on bad data, would produce a wrong *business
decision* rather than just a slightly less complete report?

### Concept 5 — Distinct-count vs. row-count summary statistics

> "Tutorial 03 of this series covered why a summary count of 'how many rows have at least one
> problem' must be a distinct-row count, not a sum of per-category counts. Here's a related but
> different version of the same trap: a system tracks *action items* at a fine granularity (e.g.,
> one restock action per warehouse), but also wants a KPI at a coarser granularity (e.g., how many
> distinct *products* need attention, regardless of how many warehouses each one is short in).
> Explain why 'count the fine-grained action items' and 'count the distinct coarse-grained things
> they refer to' are two different, both-legitimate numbers. Quiz me with a scenario (a product
> low in two of three warehouses it's stocked in) and ask me to compute both numbers."

*What to listen for:* both numbers answer real, different operational questions — "how many restock
actions does the ops team have to take" (fine-grained, can exceed the number of distinct products)
versus "how many distinct products are at risk" (coarse-grained, a merchandising-level KPI). Neither
is more "correct" than the other; the bug is *conflating* them — using the fine-grained count where
a KPI card promises the coarse-grained answer, silently overstating how many distinct things need
attention.

*Practice question:* a product is stocked in three warehouses and is below its reorder point in
two of them. How many restock action items exist, and how many distinct products need supplier
attention?

## Architecture overview

Phase 3 ended with a trusted `valid_orders` list — every row already passed OV-001 through OV-007.
Phase 4 doesn't re-validate *business* correctness; it consumes that trust and introduces something
Phase 3 never needed: **state that changes while the module runs.**

```text
   Phase 3 output                              inventory.xlsx
  (list[ValidOrderRow],                              │
   rebuilt as a DataFrame —                           ▼
   OR a fresh file via                        load_inventory(file)
   load_valid_orders(file))                   (excel_io.load_excel +
         │                                     validate_required_columns)
         │                                              │
         └──────────────────┬───────────────────────────┘
                             ▼
          allocate_inventory(valid_orders_df, inventory_df)
          ── re-validates required columns on BOTH DataFrames itself,
             regardless of whether a caller already used the loaders
                             │
        ┌────────────────────┼─────────────────────────┐
        ▼                                                ▼
 _build_inventory_state()                    _sort_orders_for_allocation()
   by_sku: dict[str, list[dict]]               IA-001 sort:
   entries: list[dict]                         priority → delivery date →
   (by_sku and entries hold the                 order date → order_id
    SAME dict objects — mutating                (defensive parsing of every
    one is visible through the other)            order field happens HERE)
        │                                                │
        └──────────────────┬─────────────────────────────┘
                            ▼
        for each order, in IA-001 order (never re-sorted, never revisited):
          _allocate_order_line(order, inventory_by_sku)
            → _pick_warehouse() — highest allocatable_qty, tie → name
            → mutates chosen["allocatable_qty"] / ["allocated_qty"]
              IN PLACE — the next order to want this SKU sees the
              depleted balance automatically
                            │
                            ▼
        allocation_results  ──filter status=="Backordered"──▶  backorders
                            │
                            ▼
        for each ORIGINAL inventory entry (already mutated above):
          _build_remaining_inventory_row()
            → remaining_qty = starting_available_qty - allocated_qty
            → reorder_alert: strictly remaining_qty < reorder_point
            → optionally a SupplierFollowUpRow (IA-008 only)
                            │
                            ▼
              InventoryAllocationResult
    { summary, allocation_results, backorders,
      remaining_inventory, supplier_follow_ups }
```

Key invariants for this phase:

1. **Every order must be fully sorted into IA-001 order before any allocation math runs.** There
   is no re-sort, no re-check — get the sort wrong once and every downstream status is silently
   wrong, with no exception anywhere to catch it (Part 3).
2. **A single order line is filled from exactly one warehouse, chosen by `allocatable_qty`, never
   split.** (Part 6.)
3. **Allocation state lives in mutable dicts shared by two indexes (`by_sku` and `entries`).**
   Mutating a chosen entry during allocation is what makes `remaining_inventory` (built afterward
   from `entries`) automatically reflect every line that touched it (Part 5).

## Part 1 — Result envelope symmetry with Phase 3

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 71–76:

```python
class InventoryAllocationResult(TypedDict):
    summary: AllocationSummary
    allocation_results: list[AllocationResultRow]
    backorders: list[BackorderRow]
    remaining_inventory: list[RemainingInventoryRow]
    supplier_follow_ups: list[SupplierFollowUpRow]
```

This follows Tutorial 03's `OrderValidationResult` pattern exactly: a single `TypedDict` envelope,
defined locally in `inventory_allocation.py` rather than promoted into `src/contracts.py`, bundling
every contract this function's caller needs into one JSON-serializable return value. The reasoning
is identical to Phase 3's — this is a transport shape composed of contracts the spec already
defines (`AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`,
`SupplierFollowUpRow`, all in `src/contracts.py`), not a new business-facing shape of its own.

The interesting difference from Phase 3 is *shape*, not philosophy: `OrderValidationResult` has
one summary plus two lists (`valid_orders`, `errors`); `InventoryAllocationResult` has one summary
plus *four* lists. That's not an arbitrary expansion — it mirrors `02_demo_inventory_allocation.md`
§6's five suggested report sheets (`Allocation Summary`, `Allocation Results`, `Backorders`,
`Remaining Inventory`, `Supplier Follow-up`) one-for-one. Open lines 390–392:

```python
    allocation_results = [_allocate_order_line(order, inventory_by_sku) for order in sorted_orders]
    # Backorders sheet is allocation_results filtered to status=Backordered (BackorderRow adds no new fields).
    backorders: list[BackorderRow] = [row for row in allocation_results if row["status"] == "Backordered"]
```

As covered in Tutorial 01 Part 5, `BackorderRow` inherits from `AllocationResultRow` and adds no
new fields — this line is where that decision actually gets exercised for the first time in the
codebase: `backorders` isn't independently computed at all, it's a plain list-comprehension filter
over `allocation_results` that already produced every field `BackorderRow` needs. If `BackorderRow`
ever needed a field `AllocationResultRow` doesn't have, this one-line filter would stop working and
the two contracts would need to diverge — which is exactly the risk Tutorial 01 named for
structural typing's blind spot, now made concrete.

**Checkpoint:** Why compute `backorders` as a *filtered view* of `allocation_results` instead of
appending to a separate list inside `_allocate_order_line` as each backordered line is produced?

<details>
<summary>Reveal answer</summary>

Filtering afterward keeps `_allocate_order_line`'s only job "decide and record this one line's
outcome" — it doesn't need to know that its caller also wants a backorders-only view, so it stays
simpler and more reusable. It also guarantees the two lists can never drift out of sync: there's no
way for `backorders` to contain a row that isn't (by identical value) also present in
`allocation_results`, because it's derived from that exact list, not maintained as a separate
parallel accumulator that a future edit could update inconsistently.
</details>

**Checkpoint:** `AllocationSummary` (`src/contracts.py:40-46`) has five fields:
`total_order_lines`, `fully_allocated_count`, `partially_allocated_count`, `backordered_count`,
`low_stock_sku_count`. The first four are all built from `allocation_results` in one function,
`_build_summary` (lines 369-379); `low_stock_sku_count` is computed separately, in the main
`allocate_inventory` loop (lines 396-403), and passed into `_build_summary` as an argument rather
than computed inside it. Why the split?

<details>
<summary>Reveal answer</summary>

The first four counts only need `allocation_results` — they're pure aggregations over one already-
built list, cleanly expressible as a small helper function. `low_stock_sku_count` needs something
`_build_summary` doesn't have access to: the `entries`/`remaining_inventory` pass, which runs
*after* allocation and inspects each inventory row's post-allocation `remaining_qty` against its
`reorder_point` (Part 7). Rather than pass the entire `inventory_entries` list into `_build_summary`
and make it responsible for two unrelated computations, the caller (`allocate_inventory`) computes
the `low_stock_skus` set during its own remaining-inventory loop (where that data already lives)
and hands `_build_summary` just the one number it needs — keeping `_build_summary`'s only
dependency `allocation_results`, matching what its name promises.
</details>

**Try it yourself:** Run
`uv run python -c "from src.inventory_allocation import allocate_inventory; import pandas as pd; from datetime import date; orders = pd.DataFrame([{'order_id':'SO-1','order_date':date(2026,7,1),'customer_name':'Test','customer_region':'HK','sku':'X-1','quantity':5,'requested_delivery_date':date(2026,7,10),'priority':'High','payment_terms':'30 days'}]); inv = pd.DataFrame([{'sku':'X-1','warehouse':'HK','available_qty':3}]); r = allocate_inventory(orders, inv); print(r.keys()); print(r['backorders'][0] in r['allocation_results'])"`
and confirm the printed keys match the five `InventoryAllocationResult` fields, and that the one
backordered row is genuinely a member of `allocation_results`, not a separately-built duplicate.

## Part 2 — Loader boundary: missing columns vs. malformed required inventory values

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 23–35 and 79–90:

```python
INVENTORY_ORDERS_REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_region",
    "sku",
    "quantity",
    "requested_delivery_date",
    "priority",
    "payment_terms",
]

INVENTORY_REQUIRED_COLUMNS = ["sku", "warehouse", "available_qty"]
```

```python
def load_valid_orders(file) -> pd.DataFrame:
    """Load valid_orders.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVENTORY_ORDERS_REQUIRED_COLUMNS, "valid orders file")
    return df


def load_inventory(file) -> pd.DataFrame:
    """Load inventory.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVENTORY_REQUIRED_COLUMNS, "inventory file")
    return df
```

This is the same loader pattern Tutorial 03 covered — `load_excel` plus
`validate_required_columns`, reused unchanged from `excel_io.py`. But Phase 4 does something Phase
3 never needed: `allocate_inventory` itself re-validates required columns, independent of whether a
caller ever went through `load_valid_orders`/`load_inventory` at all. Open lines 382–386:

```python
def allocate_inventory(valid_orders_df: pd.DataFrame, inventory_df: pd.DataFrame) -> InventoryAllocationResult:
    """Allocate validated order lines against inventory and return the full result envelope."""
    validate_required_columns(valid_orders_df, INVENTORY_ORDERS_REQUIRED_COLUMNS, "valid orders file")
    validate_required_columns(inventory_df, INVENTORY_REQUIRED_COLUMNS, "inventory file")
```

Phase 3's `validate_orders()` never does this — it trusts that `load_orders`/`load_product_master`
already ran. Phase 4 can't make that same assumption, because `valid_orders_df`'s *realistic*
source isn't a fresh Excel upload at all — it's Phase 3's own `validate_orders()` output
(`valid_orders`, a `list[ValidOrderRow]`) rebuilt into a DataFrame, which never passes through
`load_valid_orders`. `tests/test_inventory_allocation.py:369-373` proves this defense actually
matters:

```python
def test_allocate_inventory_validates_required_columns_when_called_directly():
    orders = _orders_df(_order_row()).drop(columns=["quantity"])
    with pytest.raises(MissingColumnsError) as exc_info:
        allocate_inventory(orders, _inventory_df(_inventory_row()))
    assert "quantity" in str(exc_info.value)
```

Beyond the *column* boundary, Phase 4 introduces a second required-value boundary Phase 3's module
doesn't have. Open lines 41–68:

```python
class InvalidInventoryDataError(Exception):
    """Business-readable error for an inventory value that cannot be used for allocation."""

    def __init__(self, row_number: int, field: str, value: object = None) -> None:
        self.row_number = row_number
        self.field = field
        self.value = value
        value_text = "" if value is None else f": {_format_cell_value(value)}"
        message = (
            f"Inventory row {row_number} has a missing or invalid value for field "
            f"'{field}'{value_text}. Please check the sample file."
        )
        super().__init__(message)


class InvalidOrderDataError(Exception):
    """Business-readable error for a valid-orders value that cannot be used for allocation."""

    def __init__(self, row_number: int, field: str, value: object = None) -> None:
        self.row_number = row_number
        self.field = field
        self.value = value
        value_text = "" if value is None else f": {_format_cell_value(value)}"
        message = (
            f"Valid order row {row_number} has a missing or invalid value for required field "
            f"'{field}'{value_text}. Please re-run order validation or check the sample file."
        )
        super().__init__(message)
```

Phase 3 turned every malformed *order* value into a `ValidationErrorRow` — a row could be flagged
and excluded while the rest of the batch kept processing, because `contracts.py` defines exactly
that output surface (`errors`). Phase 4 has no equivalent contract for inventory data — there's no
`InventoryDataIssueRow` family, and nothing in `02_demo_inventory_allocation.md` describes a "soft"
inventory data-quality report. Silently defaulting a malformed `available_qty` to `0` would make a
warehouse look phantom-empty without telling anyone why — worse than failing loudly, since
`available_qty` directly drives every downstream allocation decision this whole module makes.
Raising is the fail-fast strategy (this tutorial's pre-study Concept 4); it's the correct choice
here specifically because `available_qty` is a field the rest of the system's correctness depends
on directly, unlike the *optional* inventory fields (`reserved_qty`, `reorder_point`,
`lead_time_days`), which the spec already defines blank-behavior for and which degrade gracefully
instead (Part 4 and Part 7 use this distinction directly).

> **Design patterns — Fail-fast vs. graceful degradation in one module:** `_require_quantity`
> (lines 176-194, used for `available_qty`) raises `InvalidInventoryDataError` on anything blank,
> non-numeric, non-whole, or negative. `_optional_quantity` (lines 197-217, used for `reserved_qty`,
> `reorder_point`, `lead_time_days`) returns `None` on the same blank/unparseable inputs and only
> raises for a value that parses but is out of range (negative). Both strategies coexist
> deliberately in the same file — the choice per field isn't stylistic, it follows directly from
> whether the spec defines a safe "absent" behavior for that specific field.

**Checkpoint:** Phase 3 converts malformed order data into structured error rows
(`ValidationErrorRow`); Phase 4 raises an exception (`InvalidInventoryDataError`) for the analogous
problem in inventory data, because no equivalent output contract exists. Is "we don't have a
contract for this, so raise instead" a good long-term rule, or does it mean Phase 4 is missing a
contract that should be added via ADR?

<details>
<summary>Reveal answer</summary>

It's a reasonable *short-term* rule but not a permanent one — it correctly avoids inventing an
output contract mid-implementation (which would itself be a scope/process violation, since Field
Scope Boundary changes go through an ADR, not an ad hoc addition inside a business-rule module).
Raising is the right behavior *given* the current contract surface. Whether Phase 4 is *missing* a
contract is a separate, legitimate question: `PaymentDataIssueRow` already exists precisely because
Phase 5's spec anticipates soft, reportable payment data issues — if inventory data quality turns
out to be a recurring real-world problem (not just a theoretical one), an `InventoryDataIssueRow`
mirroring that pattern would be a reasonable future ADR. Today, raising is correct because no design
work has gone into what a soft inventory-error report should even look like; inventing one under
pressure, inside `_build_inventory_state`, would be worse than a clear, documented boundary that
says "not supported yet."
</details>

**Checkpoint:** If a future ADR did add `InventoryDataIssueRow`, would that change the *loader*
(`load_inventory`), the *allocation function* (`allocate_inventory`), or both? Where's the right
boundary between "the file structurally can't be trusted" (loader's job) and "a specific cell's
value is bad" (allocation's job)?

<details>
<summary>Reveal answer</summary>

It would change `allocate_inventory` (specifically `_build_inventory_state`, where
`InvalidInventoryDataError` is currently raised) and not `load_inventory` at all — mirroring
exactly the Part 2 boundary Tutorial 03 established: a missing *column* is a structural problem the
loader owns (nothing downstream can process any row at all), while a bad *value* in a column that
exists is a per-row concern for whatever code actually consumes that value, which for inventory
data is `_build_inventory_state`/`allocate_inventory`, not `load_inventory`. Adding
`InventoryDataIssueRow` would mean `_require_quantity`-style checks return a soft issue record
instead of raising, collected alongside `allocation_results` the same way Phase 3 collects `errors`
alongside `valid_orders` — the loader's job (column presence) stays completely unrelated to this
change.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_inventory_allocation.py -k "malformed_available_qty or blank_sku_in_inventory or blank_warehouse_in_inventory" -v`
and read all three error messages produced — confirm each names the exact row number, field, and
offending value, the same business-readable shape Tutorial 01 covered for `MissingColumnsError`.

## Part 3 — IA-001 order sorting as the hidden precondition for every later result

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 251–284:

```python
def _sort_orders_for_allocation(valid_orders_df: pd.DataFrame) -> list[dict]:
    """IA-001 — sort by priority, then requested delivery date, then order date, then order ID."""
    prepared: list[dict] = []
    for position, (_, row) in enumerate(valid_orders_df.iterrows()):
        row_number = position + 2
        requested_delivery = _require_order_date(
            row.get("requested_delivery_date"), row_number, "requested_delivery_date"
        )
        order_date = _require_order_date(row.get("order_date"), row_number, "order_date")
        product_name = row.get("product_name")
        prepared.append(
            {
                "order_id": _require_order_text(row.get("order_id"), row_number, "order_id"),
                "customer_name": _require_order_text(
                    row.get("customer_name"), row_number, "customer_name"
                ),
                "sku": _require_order_text(row.get("sku"), row_number, "sku"),
                "product_name": None if _is_blank(product_name) else _to_trimmed_str(product_name),
                "quantity": _require_order_quantity(row.get("quantity"), row_number, "quantity"),
                "priority": _require_order_priority(row.get("priority"), row_number),
                "requested_delivery_date": requested_delivery.date().isoformat(),
                "_requested_delivery_sort": requested_delivery,
                "_order_date_sort": order_date,
            }
        )
    prepared.sort(
        key=lambda o: (
            PRIORITY_RANK.get(o["priority"], len(PRIORITY_RANK)),
            o["_requested_delivery_sort"],
            o["_order_date_sort"],
            o["order_id"],
        )
    )
    return prepared
```

Every field this function needs for allocation *and* every field it needs only for sorting are
extracted and defensively parsed in the same pass — `_require_order_quantity`,
`_require_order_date`, `_require_order_text`, and `_require_order_priority` all raise
`InvalidOrderDataError` immediately on a malformed value, before sorting even starts. This isn't
incidental: sorting has to happen before any allocation math runs, so any order-line data bad
enough to make sorting unreliable (an unparseable date, an unrecognized priority string) has to be
caught here, not deferred to whenever `_allocate_order_line` happens to touch that field later.

`PRIORITY_RANK` (line 38, `{"High": 0, "Normal": 1, "Low": 2}`) converts the spec's named priority
levels into a comparable integer — `_require_order_priority` (lines 163-167) already guarantees the
value is one of exactly those three strings, so the sort key's `.get(..., len(PRIORITY_RANK))`
fallback for an unrecognized priority is defensive redundancy, not a real code path once that
validation has already run. `sorted()`/`.sort()`'s tuple comparison does the rest: Python compares
tuples element by element, so `(0, delivery_a, order_a, "SO-1")` sorts before
`(1, delivery_b, order_b, "SO-2")` purely because `0 < 1`, regardless of what the remaining three
elements are — this is this tutorial's pre-study Concept 2 (greedy, order-defining decisions) made
concrete: the *entire* rest of the module trusts that once this sort finishes, iterating
`sorted_orders` in order *is* IA-001's specified processing order, with nothing downstream ever
re-checking that assumption.

> **Algorithms — Composite-key sort:** The same technique Tutorial 03 Part 8 used for deterministic
> error ordering reappears here for a different purpose: not just making output stable for tests,
> but *defining correctness itself* — IA-001 isn't a display-ordering nicety, it's the literal
> specification for which order deserves scarce stock first. `PRIORITY_RANK.get(...)`,
> `_requested_delivery_sort`, `_order_date_sort`, and `order_id` form a four-level `ORDER BY`
> equivalent, evaluated left to right exactly the way a SQL `ORDER BY priority, delivery_date,
> order_date, order_id` clause would be.

**Checkpoint:** The correctness of the whole module depends on orders being processed in *exactly*
IA-001's sort order before allocation starts — get that sort wrong and every downstream status is
wrong too, with no exception thrown to catch it. What kind of test would catch "the sort is
slightly wrong" as opposed to "the sort is completely missing"?

<details>
<summary>Reveal answer</summary>

"Completely missing" is easy to catch — almost any test with two competing orders for the same
scarce SKU (like `test_high_priority_allocated_before_normal`,
`tests/test_inventory_allocation.py:100-108`) fails loudly, because the wrong order gets stock at
all. "Slightly wrong" needs *narrower, single-level* tests that isolate exactly one tie-break level
at a time, holding every earlier level equal — `test_sort_tie_breaks_by_order_date_then_order_id`
(lines 170-181) is exactly this: three orders with the *same* priority and requested delivery date
implicitly (all default to the same date via `_order_row()`), differing only in `order_date` and
`order_id`, asserting the exact resulting order. A sort that got priority right but broke the
*third* tie-break level (order_date before order_id) would pass every "does high priority beat
normal" test and only fail this one, narrowly-scoped test — which is exactly why
`tests/test_inventory_allocation.py` has a dedicated test per sort *level*, not just one test per
sort *outcome*.
</details>

**Checkpoint:** Why does `_sort_orders_for_allocation` perform full defensive parsing of every
order field (not just the four sort-key fields: priority, delivery date, order date, order ID)
before sorting, rather than extracting only what sorting needs and deferring `quantity`/`sku`
validation to `_allocate_order_line`?

<details>
<summary>Reveal answer</summary>

Two reasons converge here. First, `row_number` (needed for any `InvalidOrderDataError` raised for
*any* field) is only available during this same `enumerate(valid_orders_df.iterrows())` pass — once
the function moves on to building `prepared` dicts and sorting them, the original DataFrame
position is gone unless captured now. Second, and more important: this function already has to
iterate the raw DataFrame once to extract sort keys, so validating every other required field in
that same pass means a single malformed row (bad `quantity`, blank `sku`) fails immediately and
loudly, before any allocation work starts on a still-partially-untrusted batch — consistent with
Part 2's fail-fast reasoning. Deferring `quantity`/`sku` validation to `_allocate_order_line` would
mean a malformed value could survive all the way into the middle of allocation, potentially after
some *other* orders have already mutated shared inventory state (Part 5) — a much messier failure
to reason about and recover from than "the whole request never started."
</details>

**Try it yourself:** Run `uv run pytest tests/test_inventory_allocation.py -k sort -v` and read
both sort-related test names. Then, in `tests/test_inventory_allocation.py:170-181`, temporarily
swap `SO-2026-002`'s and `SO-2026-001`'s `order_date` values so the third tie-break level (order
date) no longer distinguishes them, leaving only `order_id` to break the tie — confirm the test
still passes, proving `order_id` really is evaluated as the final tie-breaker level, not an unused
fallback. Revert the change afterward.

## Part 4 — `allocatable_qty` as the only usable-stock concept

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 235–247 and
287–289:

```python
        entry = {
            "sku": sku,
            "warehouse": warehouse,
            "starting_available_qty": available_qty,
            # IA-002 — allocatable_qty = available_qty - reserved_qty (reserved_qty defaults to 0 when missing).
            "allocatable_qty": max(available_qty - reserved_qty, 0),
            "allocated_qty": 0,
            "reorder_point": reorder_point,
            "supplier_name": supplier_name,
            "lead_time_days": lead_time_days,
        }
        by_sku.setdefault(sku, []).append(entry)
        entries.append(entry)
    return by_sku, entries
```

```python
def _pick_warehouse(entries: list[dict]) -> dict:
    """IA-007 V1 — warehouse with the highest allocatable_qty for the SKU; ties broken by warehouse name."""
    return sorted(entries, key=lambda e: (-e["allocatable_qty"], e["warehouse"]))[0]
```

`02_demo_inventory_allocation.md` §5's IA-007 V1 text says to allocate from "the warehouse with the
highest available quantity for that SKU." Read completely literally, that's the raw `available_qty`
column. But IA-002, one rule earlier, already defines `allocatable_qty = available_qty -
reserved_qty` as *the* quantity actually usable for allocation this round — IA-007 never explicitly
says which of the two it means, and nothing in its own text contradicts either reading. This is
this tutorial's pre-study Concept 3: not a spec contradiction (Tutorial 03's OV-001/OV-007 problem),
but a single ambiguous phrase compatible with two different numbers.

The failure mode of choosing raw `available_qty` for warehouse *selection* is concrete:
`explanation.md` names it directly — a warehouse with `available_qty=50` but `reserved_qty=48`
(only 2 units actually allocatable) would beat a warehouse with `available_qty=20`, `reserved_qty=0`
(20 units allocatable), routing every order for that SKU to the warehouse that can *least* fulfill
it. `_pick_warehouse`'s sort key uses `-e["allocatable_qty"]` (descending allocatable quantity, not
`available_qty`) specifically to avoid this — the same value that decides *how much* to allocate
(IA-002/IA-003/IA-004/IA-005) also decides *where* to allocate from, so the module has exactly one
definition of "usable stock," not two that could disagree with each other.

Ties are broken by `e["warehouse"]` ascending (alphabetical) — the spec defines no tie-breaker at
all for equal `allocatable_qty` across warehouses; this is a project-level default, not something
`02_demo_inventory_allocation.md` specifies.

**Checkpoint:** Unlike Tutorial 03's OV-001/OV-007 conflict, IA-007's "highest available quantity"
isn't a contradiction between two rules — it's a single phrase compatible with two different
readings because IA-002 defines a derived quantity one rule earlier without IA-007 explicitly
saying which one it means. What's the general tell that a spec phrase needs disambiguating even
when nothing in the text technically conflicts?

<details>
<summary>Reveal answer</summary>

The tell is a *derived quantity with its own name* existing anywhere nearby in the spec, and a
later rule using generic, un-qualified language ("available quantity," not "allocatable_qty" or
"the raw available_qty column") that could plausibly refer to either the raw source field or the
derived one. Whenever a spec defines a named derived concept (`allocatable_qty`) and then a
different rule uses looser natural-language phrasing that overlaps with what that concept means,
that's exactly the shape of ambiguity worth flagging and resolving explicitly — even though, unlike
a contradiction, there's no pair of rules that can be shown to disagree by quoting them side by
side. The systematic check: for every quantity/derived value the spec names explicitly (search for
"=" or "defined as" patterns), check every *other* rule that later uses similar plain-language
phrasing for whether it could mean that same named value.
</details>

**Checkpoint:** The resolution (use `allocatable_qty`) was chosen because it's "the value the rest
of the module already treats as usable stock," not because of any textual signal in IA-007 itself.
Is "prefer internal consistency with an adjacent rule" a reliable tiebreaker in general, or does it
risk quietly overriding what a domain expert actually meant by the literal words?

<details>
<summary>Reveal answer</summary>

It's a reasonable *default* tiebreaker, not a guaranteed-correct one — it optimizes for a system
that behaves coherently (one definition of "usable stock," used everywhere) over one that might
technically match a domain expert's unstated intent but internally contradicts itself the moment
two rules that use the same underlying concept are compared. The risk is real: if a domain expert
actually meant the raw `available_qty` column deliberately (e.g., a business rule where reserved
stock should sometimes be visible in scoring which warehouse "looks strongest" even if it isn't
literally allocatable this instant), this resolution would silently pick the wrong reading with no
mechanism to ever surface the disagreement — nothing in the code or a passing test suite would
reveal that a human's real intent diverged from the internally-consistent interpretation. This is
exactly why `explanation.md` documents the *reasoning*, not just the *conclusion* — a future domain
expert reading it has something concrete to push back on if this guess turns out wrong, rather than
an unexplained implementation detail.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_inventory_allocation.py -k reserved_stock_reduces -v` and read
`test_reserved_stock_reduces_allocatable_qty` (`tests/test_inventory_allocation.py:122-130`) —
confirm it asserts `allocated_qty == 15` for an order of 20 against `available_qty=20,
reserved_qty=5` (`allocatable_qty = 20 - 5 = 15`), proving the module used the derived value, not
the raw `20`, for the actual allocation decision this test checks.

## Part 5 — Stateful per-line depletion and why batch-by-SKU allocation fails

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 292–333:

```python
def _allocate_order_line(order: dict, inventory_by_sku: dict[str, list[dict]]) -> AllocationResultRow:
    entries = inventory_by_sku.get(order["sku"], [])
    if entries:
        chosen = _pick_warehouse(entries)
        warehouse = chosen["warehouse"]
        allocatable = chosen["allocatable_qty"]
        if allocatable >= order["quantity"]:
            # IA-003 — full allocation.
            allocated_qty = order["quantity"]
            status = "Fully Allocated"
        elif allocatable > 0:
            # IA-004 — partial allocation.
            allocated_qty = allocatable
            status = "Partially Allocated"
        else:
            # IA-005 — backorder.
            allocated_qty = 0
            status = "Backordered"
        chosen["allocatable_qty"] -= allocated_qty
        chosen["allocated_qty"] += allocated_qty
    else:
        warehouse = ""
        allocated_qty = 0
        status = "Backordered"
```

Lines 310–311 are the whole module's linchpin: `chosen["allocatable_qty"] -= allocated_qty` and
`chosen["allocated_qty"] += allocated_qty` mutate the dict `chosen` *in place*. `chosen` isn't a
copy — it's whichever dict `_pick_warehouse` returned from `entries`, and `entries` came from
`inventory_by_sku.get(order["sku"], [])`, which is the *same* list of dicts `_build_inventory_state`
built. Go back to lines 246–247 from Part 4: `by_sku.setdefault(sku, []).append(entry)` and
`entries.append(entry)` append the *same* `entry` object to two different data structures — the
per-SKU grouping (`by_sku`, used during allocation) and the flat original-order list (`entries`,
used afterward to build `remaining_inventory`, Part 7). Mutating `chosen` through `by_sku`
automatically changes what the `entries` list sees too, because there was never a second, separate
copy — both names point at the identical object in memory.

This is why `allocate_inventory` never has to explicitly "sync" allocation results back into
inventory state: there's only one state, referenced from two places. explanation.md names the
alternative and its failure mode directly: *"A naive per-SKU calculation (sum all orders for a SKU,
sum all inventory for a SKU, distribute) can't reproduce IA-001's priority ordering: if a
High-priority order and a Normal-priority order both want the same SKU and there's only enough
stock for one, the High order must win outright, not receive a proportional share."* Aggregating
first and distributing second is exactly the "proportional" strategy this tutorial's pre-study
Concept 1 contrasted with "strict priority, in full" — and only the sequential, order-dependent,
mutating approach can guarantee the second.

`tests/test_inventory_allocation.py:194-210` proves the mutation is actually observed by later
lines, not just theoretically correct:

```python
def test_warehouse_choice_switches_as_stock_depletes():
    orders = _orders_df(
        _order_row(order_id="SO-2026-001", quantity=15),
        _order_row(order_id="SO-2026-002", quantity=15, requested_delivery_date=date(2026, 7, 16)),
    )
    inventory = _inventory_df(
        _inventory_row(warehouse="HK Warehouse", available_qty=20),
        _inventory_row(warehouse="SG Warehouse", available_qty=10),
    )
    result = allocate_inventory(orders, inventory)
    first = _result_by_order_id(result, "SO-2026-001")
    second = _result_by_order_id(result, "SO-2026-002")
    assert first["warehouse"] == "HK Warehouse"
    assert first["status"] == "Fully Allocated"
    assert second["warehouse"] == "SG Warehouse"
    assert second["allocated_qty"] == 10
    assert second["backorder_qty"] == 5
```

The first line depletes HK Warehouse from 20 allocatable down to 5; by the time the second line is
processed, SG Warehouse's untouched 10 is now the higher allocatable balance, so `_pick_warehouse`
genuinely picks a *different* warehouse for the same SKU mid-batch — something a batch-per-SKU
aggregate calculation could never reproduce, because it never models "already spent by an earlier,
higher-priority line" as a fact the next decision must see.

> **Python language — Aliasing: two indexes, one mutable object:** When two variables (or, here,
> two container structures) hold a reference to the *same* mutable object rather than independent
> copies, mutating through either one is visible through the other — this is aliasing. It's a
> common source of confusing bugs when unintended (two callers unexpectedly stepping on each
> other's data), but here it's the intentional mechanism that makes stateful depletion work without
> an explicit "write back the updated balance" step: `by_sku` and `entries` were built to alias
> deliberately, precisely so allocation's mutations and the later remaining-inventory pass over
> `entries` can never see two different, out-of-sync versions of the same warehouse's balance.

**Checkpoint:** `allocate_inventory` mutates shared dicts (`inventory_by_sku` entries) as a side
effect of iterating orders in a specific sequence — a different design could thread an immutable
balance through each call and return a new one instead. What would change about testability,
debuggability, or correctness risk if the allocation loop were rewritten to be side-effect-free?

<details>
<summary>Reveal answer</summary>

An immutable/functional rewrite (each call to something like `_allocate_order_line(order,
inventory_state) -> (result, new_inventory_state)`, threading `new_inventory_state` into the next
call explicitly) would make each step's inputs and outputs fully visible in a debugger or test
without needing to inspect the shared dict's contents *between* calls — every step becomes
independently testable by constructing exactly the "before" state it needs, with no risk of a
leftover mutation from an earlier test polluting a later one (mutable shared fixtures are a classic
source of order-dependent test flakiness). The correctness trade-off runs the other way, though:
the mutable version has exactly one gathering point for "did this stock actually get consumed
correctly" (the dict itself, inspectable at any point), while the immutable version requires
correctly threading the return value through 20+ sequential calls — a single dropped or
mis-threaded `new_inventory_state` silently reverts to stale data with no error, which is arguably
an *easier* bug to introduce than an aliasing mistake in a small, well-scoped module like this one.
For a module this size, the mutable version's simplicity (no explicit threading, no wrapper return
values everywhere) plausibly wins; the immutable version would earn its complexity in a much larger
system where inventory state needed to be inspected, replayed, or rolled back independently of the
allocation loop itself.
</details>

**Try it yourself:** In a Python shell, run
`from src.inventory_allocation import _build_inventory_state; import pandas as pd; df = pd.DataFrame([{"sku":"X","warehouse":"HK","available_qty":10}]); by_sku, entries = _build_inventory_state(df); by_sku["X"][0]["allocatable_qty"] = 999; print(entries[0]["allocatable_qty"])`
and confirm the printed value is `999`, not `10` — direct proof that `by_sku` and `entries` share
the identical dict object, not independent copies.

## Part 6 — Warehouse selection, full backorders, and the meaning of `warehouse`

Continue in [`src/inventory_allocation.py`](../../../src/inventory_allocation.py), the `else`
branch of `_allocate_order_line` (lines 312–315), and the fixture that shaped this decision. Open
[`tests/contract_fixtures.py`](../../../tests/contract_fixtures.py) lines 81–93:

```python
BACKORDER_ROW_FIXTURE: BackorderRow = {
    "order_id": "SO-2026-012",
    "customer_name": "Formosa Industrial Group",
    "sku": "IND-PUMP-005",
    "product_name": "Hydraulic Pump Unit",
    "requested_qty": 6,
    "allocated_qty": 0,
    "backorder_qty": 6,
    "warehouse": "HK Warehouse",
    "status": "Backordered",
    "priority": "Normal",
    "requested_delivery_date": "2026-07-28",
}
```

This fixture predates Phase 4 — it was hand-authored in Phase 2, before `inventory_allocation.py`
existed, purely to prove `BackorderRow`'s shape could hold believable data (Tutorial 02 Part 3). It
shows `allocated_qty: 0` *and* a populated `warehouse: "HK Warehouse"` on the same row. Once Phase 4
actually had to decide what a fully-backordered line's `warehouse` should contain, this fixture
became evidence, not just an example: a `BackorderRow` with zero allocation still names a specific
warehouse, not an empty string.

Two genuinely different situations both produce `status == "Backordered"`, and they get different
`warehouse` treatment. When `entries` is non-empty (the SKU *has* inventory rows somewhere, just
not enough allocatable stock right now), `_pick_warehouse` still runs and still selects a best
candidate — `warehouse = chosen["warehouse"]` — even though `allocatable == 0` means
`allocated_qty` stays `0`. `explanation.md` frames this as `warehouse` recording *which* warehouse
IA-007 selected as the best candidate for this SKU, independent of whether that candidate had
enough stock — genuinely useful operationally, since supplier follow-up (Part 7) is per-warehouse,
so "where would this ship from once restocked" is worth keeping. Only when `entries` is completely
empty — the SKU has *no* inventory rows anywhere in the file — does `warehouse` fall back to `""`,
because there's no candidate to name at all:

```python
    else:
        warehouse = ""
        allocated_qty = 0
        status = "Backordered"
```

`tests/test_inventory_allocation.py:213-222` proves the empty-SKU case specifically:

```python
def test_sku_with_no_inventory_rows_is_backordered_with_blank_warehouse():
    result = allocate_inventory(
        _orders_df(_order_row(sku="MED-MASK-003", quantity=5)),
        _inventory_df(_inventory_row(sku="MED-LENS-001")),
    )
    row = result["allocation_results"][0]
    assert row["status"] == "Backordered"
    assert row["allocated_qty"] == 0
    assert row["backorder_qty"] == 5
    assert row["warehouse"] == ""
```

The other named failure mode belongs here too: `_allocate_order_line` calls `_pick_warehouse` at
most once per order line and never loops over a *second* warehouse to cover whatever the first
couldn't. If SKU `X` has 6 units allocatable in HK Warehouse and 6 more in SG Warehouse, and an
order needs 10, `_pick_warehouse` picks whichever warehouse has the higher allocatable quantity
(both entries would tie or nearly tie), allocates up to *that one warehouse's* balance, and
backorders the rest — even though the SKU's *combined* stock across both warehouses (12) could have
covered the order in full. This is IA-004's own literal wording ("allocate the available amount and
backorder the remaining"), read as scoped to the one chosen warehouse, matching the pre-existing
`BackorderRow`/`AllocationResultRow` shape, which has exactly one `warehouse` field per row — there
is no shape in `src/contracts.py` today for "this line was split across two warehouses."

**Checkpoint:** The spec's test-case table (§11) never describes a SKU with zero inventory rows, or
an order line that's fully backordered needing a `warehouse` value. Both behaviors were decided by
inference — one from a pre-existing fixture (`BACKORDER_ROW_FIXTURE`), one from first-principles
reasoning about what's operationally useful. Which of these two justifications is the stronger
basis for a decision that isn't in the spec, and would you trust a fixture's implicit shape over
your own reasoning if the two conflicted?

<details>
<summary>Reveal answer</summary>

Neither is unconditionally stronger — they answer different questions. The fixture is *stronger
evidence of committed intent*: someone already made a concrete decision and wrote it down as a
real, specific data example, even if the decision predates and doesn't explain itself. First-
principles reasoning is *stronger evidence of correctness for a case the fixture doesn't cover* —
`BACKORDER_ROW_FIXTURE` says nothing about the zero-inventory-rows case, so that decision had
nowhere to lean on precedent and had to be reasoned out independently. If the two conflicted — say,
first-principles reasoning suggested `warehouse` should always be `""` on any zero-allocation row,
including the case the fixture covers — the fixture should generally win for the *specific* case it
already commits to, on the theory that it likely reflects an earlier, deliberate decision (or at
minimum, changing it now is itself a decision with its own consequences for whatever already reads
that fixture); first-principles reasoning should govern any case the fixture is genuinely silent
about, since there's no existing commitment to defer to.
</details>

**Checkpoint:** Design (don't implement — this would need its own ADR, since it changes what an
`AllocationResultRow` can represent) how the module would need to change to let one order line be
split across two warehouses when no single warehouse holds enough stock but the SKU's *combined*
stock across all its warehouses would cover it in full.

<details>
<summary>Reveal answer</summary>

At minimum: `_pick_warehouse` would need to return an ordered list of candidates instead of a
single winner; `_allocate_order_line` would need a loop that keeps drawing from the next-best
warehouse until either the order is fully covered or every warehouse is exhausted, instead of its
current single `if/elif/else` on one `chosen` entry; and the return shape would need to change from
"one `AllocationResultRow` per order line" to either multiple rows per line (requiring a new field
like `order_line_id` to group them, since `order_id` alone might span multiple lines) or a single
row with a new list-valued field naming every warehouse contributed and how much each gave — either
way, a genuine `src/contracts.py` change requiring its own Field Scope Boundary justification, not
just an internal refactor. It would also complicate Part 7's reorder-alert calculation, since a
single order line could now deplete *two* warehouses' `allocatable_qty` simultaneously instead of
one, meaning `_build_remaining_inventory_row` would need no changes itself (it already just reads
post-allocation `entries`) but the depletion pattern it observes would look different. No existing
test covers any of this — a new test proving "one order line's total allocated quantity across
multiple `AllocationResultRow`s sums to no more than the order's requested quantity, and never
exceeds any single warehouse's allocatable balance" would be required before trusting such a
change.
</details>

**Try it yourself:** Run `uv run pytest tests/test_inventory_allocation.py -k backorder -v` and
read both backorder-related test names — confirm one asserts a populated `warehouse` (`"HK
Warehouse"`, in `test_no_stock_backordered`, lines 89-97) and the other asserts `warehouse == ""`
(`test_sku_with_no_inventory_rows_is_backordered_with_blank_warehouse`) — the same `status ==
"Backordered"` value covering two genuinely different `warehouse` outcomes.

## Part 7 — Supplier follow-up and strict reorder-point semantics

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 336–366:

```python
def _build_remaining_inventory_row(entry: dict) -> tuple[RemainingInventoryRow, SupplierFollowUpRow | None]:
    remaining_qty = entry["starting_available_qty"] - entry["allocated_qty"]
    reorder_point = entry["reorder_point"]
    # IA-008 — reorder alert fires only when reorder_point is known and remaining_qty is strictly below it.
    reorder_alert = "Yes" if reorder_point is not None and remaining_qty < reorder_point else "No"

    row: RemainingInventoryRow = {
        "sku": entry["sku"],
        "warehouse": entry["warehouse"],
        "starting_available_qty": entry["starting_available_qty"],
        "allocated_qty": entry["allocated_qty"],
        "remaining_qty": remaining_qty,
        "reorder_alert": reorder_alert,
    }
    if reorder_point is not None:
        row["reorder_point"] = reorder_point

    follow_up: SupplierFollowUpRow | None = None
    if reorder_alert == "Yes":
        follow_up = {
            "sku": entry["sku"],
            "warehouse": entry["warehouse"],
            "remaining_qty": remaining_qty,
            "reorder_point": reorder_point,
        }
        if entry["supplier_name"] is not None:
            follow_up["supplier_name"] = entry["supplier_name"]
        if entry["lead_time_days"] is not None:
            follow_up["lead_time_days"] = entry["lead_time_days"]

    return row, follow_up
```

`remaining_qty = starting_available_qty - allocated_qty` matches spec §6's column table literally —
notice `reserved_qty` doesn't appear in this formula at all. `reserved_qty` only ever gates
allocation *eligibility* through `allocatable_qty` (Part 4); it's never subtracted a second time
from the reported remaining balance. `CONTEXT.md`'s glossary entry for Supplier Follow-up describes
a broader trigger in prose: *"An operational follow-up item created when stock is low, backordered,
or below reorder point."* That's not what this function implements — `reorder_alert` (and therefore
`follow_up`) depends on exactly one condition: `reorder_point is not None and remaining_qty <
reorder_point`. A SKU that's fully backordered but whose warehouse never had a `reorder_point` set
gets *no* follow-up row, no matter how badly backordered it is — the named failure mode "triggering
supplier follow-up from backorder alone" is explicitly what this function does *not* do, even though
a plain reading of the glossary might suggest it should.

`plan.md`'s decision #5 explains why: *"the only numbered rule that defines a trigger is IA-008"* —
the Scope Gate governs numbered rules in the three spec files, and `CONTEXT.md`'s glossary is
descriptive color explaining what a `SupplierFollowUpRow` is *for*, not an independent source of
new trigger conditions. Widening the trigger to match the glossary's looser phrasing would be
implementing behavior no numbered rule actually specifies — the same category of scope drift the
Scope Gate exists to prevent, just arriving from a glossary entry instead of an "Optional"-labeled
spec rule.

The comparison is also strictly `<`, not `<=`: `tests/test_inventory_allocation.py:240-248` locks
in the boundary case directly:

```python
def test_remaining_qty_equal_to_reorder_point_does_not_alert():
    result = allocate_inventory(
        _orders_df(_order_row(quantity=15)),
        _inventory_df(_inventory_row(available_qty=20, reorder_point=5)),
    )
    remaining = result["remaining_inventory"][0]
    assert remaining["remaining_qty"] == 5
    assert remaining["reorder_alert"] == "No"
    assert result["supplier_follow_ups"] == []
```

and `test_missing_reorder_point_never_alerts` (lines 228-237) locks in the other guard — no
`reorder_point` at all means `reorder_alert` is unconditionally `"No"`, never treated as "0, so
anything triggers it."

**Checkpoint:** `SupplierFollowUpRow` was kept scoped to only IA-008's literal trigger, deliberately
narrower than `CONTEXT.md`'s glossary description of "stock is low, backordered, or below reorder
point." The Scope Gate says only numbered V1/unlabeled rules get implemented — but a glossary entry
isn't a numbered rule, so is it authoritative at all, or just descriptive color? What's the rule for
when a glossary term should expand what gets built versus when it's just loose prose?

<details>
<summary>Reveal answer</summary>

`CONTEXT.md` itself states its own scope: it's "the domain glossary... business terms only, not
implementation details" — it exists to give shared vocabulary to concepts the numbered specs
already define, not to independently author new trigger conditions of its own. The rule this
project follows: a numbered rule in one of the three in-scope spec files (`01_demo_*`, `02_demo_*`,
`03_demo_*`) is the only thing that can authorize new implemented behavior; a glossary entry can
*describe* what that numbered rule produces (in looser, more readable prose, for human orientation)
but can never be read as a wider specification in its own right — precisely because glossary prose
is written for readability, not precision, and treating it as authoritative would mean every
future glossary edit could silently expand scope without going through the ADR process the Scope
Gate requires for genuine rule changes. The tell for "just descriptive color" versus "should expand
scope": does the phrase trace back to and stay consistent with an already-numbered rule (color), or
does it introduce a genuinely new condition no numbered rule mentions (scope creep requiring an
ADR, not a silent implementation choice)?
</details>

**Try it yourself:** Run `uv run pytest tests/test_inventory_allocation.py -k reorder -v` and read
both reorder-related test names. Then construct a scenario by hand: a SKU with `available_qty=0`,
no `reorder_point` set at all, and an order for 10 units. Predict `reorder_alert` and whether
`supplier_follow_ups` contains an entry for it — despite this SKU being maximally backordered —
then verify your prediction with a quick Python shell call to `allocate_inventory`.

## Part 8 — Summary KPIs: distinct SKUs vs. warehouse-level follow-up rows

Open [`src/inventory_allocation.py`](../../../src/inventory_allocation.py) lines 394–405:

```python
    remaining_inventory: list[RemainingInventoryRow] = []
    supplier_follow_ups: list[SupplierFollowUpRow] = []
    low_stock_skus: set[str] = set()

    for entry in inventory_entries:
        remaining_row, follow_up_row = _build_remaining_inventory_row(entry)
        remaining_inventory.append(remaining_row)
        if follow_up_row is not None:
            supplier_follow_ups.append(follow_up_row)
            low_stock_skus.add(entry["sku"])

    summary = _build_summary(allocation_results, len(low_stock_skus))
```

As covered in Tutorial 03 Part 7, a `set` is the standard tool for "how many *distinct* things have
at least one problem" — the same pattern reappears here, one phase later, for a different reason.
`supplier_follow_ups` accumulates one `SupplierFollowUpRow` per *(sku, warehouse)* pair that
alerts — a genuinely operational, warehouse-level list: "here are the restock actions the ops team
needs to take." `low_stock_skus` accumulates only the *SKU*, and `set.add()` silently no-ops if
that SKU is already present — so a SKU alerting in two different warehouses adds its name to the
set twice but only counts once in `len(low_stock_skus)`.

`explanation.md` names the exact scenario this distinction protects: `MED-LENS-001` alerts in both
HK and SG Warehouse in the sample data. `len(supplier_follow_ups)` for that SKU alone would be `2`
— correct as an answer to "how many warehouse-level restock actions exist," but wrong as an answer
to "how many distinct products need supplier attention," which is what `AllocationSummary.
low_stock_sku_count` is meant to report — a merchandising-level question, not an operational-task
count. `tests/test_inventory_allocation.py:251-258` proves the distinction directly:

```python
def test_low_stock_sku_count_counts_distinct_skus_not_warehouse_rows():
    inventory = _inventory_df(
        _inventory_row(warehouse="HK Warehouse", available_qty=3, reorder_point=5),
        _inventory_row(warehouse="SG Warehouse", available_qty=2, reorder_point=5),
    )
    result = allocate_inventory(_orders_df(_order_row(quantity=1)), inventory)
    assert len(result["supplier_follow_ups"]) == 2
    assert result["summary"]["low_stock_sku_count"] == 1
```

Both numbers are computed, both are correct, and both are already exposed in the result envelope
(`supplier_follow_ups` as a list, `summary.low_stock_sku_count` as a count) — the bug this test
guards against isn't either number being wrong in isolation, it's a KPI card or a summary sentence
accidentally reading `len(supplier_follow_ups)` where the UI promised "distinct SKUs," silently
overstating how many distinct products are actually at risk. Compare this failure mode to the named
one this tutorial called out: "counting follow-up rows as low-stock SKUs" is exactly this mistake —
substituting the fine-grained count where the coarse-grained one is what's actually being reported.

**Checkpoint:** `low_stock_sku_count` (distinct SKUs) and `len(supplier_follow_ups)` (warehouse-
level rows) are both legitimate, both already computed, and easy to accidentally conflate. Now that
this distinction exists for Phase 4, does `PaymentAgingSummary` in Phase 5 have an analogous risk —
some count that could mean "distinct invoices" or "distinct customers" depending on which one a KPI
card actually needs?

<details>
<summary>Reveal answer</summary>

Yes, structurally the same risk exists wherever a summary aggregates over one grain but a detail
list exists at a finer grain. `PaymentAgingSummary.high_priority_count` (`src/contracts.py:85-90`)
is the most likely candidate: if it's meant to answer "how many distinct customers need urgent
follow-up," but the underlying detail rows are per-*invoice* (`PaymentAgingRow`, one row per
invoice, not per customer), a customer with two separate high-priority overdue invoices would
inflate a naive `len(rows)`-style count exactly the way `len(supplier_follow_ups)` inflates
distinct-SKU count here. The general audit question this tutorial's pre-study Concept 5 names:
for every summary count, ask "what's the grain of the underlying detail rows, and does the KPI's
name promise that same grain, or a coarser one?" — if coarser, verify a `set()`-based distinct
count is used, not a row count.
</details>

**Checkpoint:** This is the second phase in a row (after Phase 3's `invalid_orders` distinct-row-
count decision) where a naive "sum/count the sub-items" implementation would have silently double-
counted something. Is there a way to catch this class of bug systematically — a review checklist, a
property-based test, a naming convention — rather than relying on remembering it happened twice?

<details>
<summary>Reveal answer</summary>

A concrete, checkable convention: any summary field whose name implies a *distinct entity count*
(anything read as "how many X" where X is a real-world thing like a row, SKU, customer, or
invoice — as opposed to "how many events/actions/violations") should be computed from
`len(some_set)`, never from `sum(...)` or `len(some_list)`, as a matter of house style — and a code
reviewer (human or an automated check grepping for `_count` fields assigned from `sum(` or a bare
list) can mechanically flag any exception for justification. A property-based test could
independently generate random overlapping violation patterns and assert `distinct_count <=
sum_of_category_counts` always holds with equality only when no row/entity has more than one
issue — catching the double-counting bug class generically instead of one hand-written scenario at
a time. The through-line across both phases: `invalid_orders` and `low_stock_sku_count` are both
"how many distinct entities have at least one qualifying property," and both were correctly
implemented as `len(some_set)` — the naming convention above is really just making that pattern
explicit and checkable instead of something a developer has to independently re-derive each time.
</details>

**Try it yourself:** Run `uv run pytest tests/test_inventory_allocation.py -k low_stock -v` and read
the test's two assertions side by side — confirm `len(result["supplier_follow_ups"]) == 2` and
`result["summary"]["low_stock_sku_count"] == 1` both pass simultaneously for the same
`allocate_inventory` call, proving these are two different, both-correct numbers, not one right and
one wrong.

## Part 9 — Tests as executable specification for ambiguity, tie-breaking, and edge cases

Open [`tests/test_inventory_allocation.py`](../../../tests/test_inventory_allocation.py) and
compare its section comments to `02_demo_inventory_allocation.md` §11's eight-row table:

```python
# --- Spec section 11 test cases ------------------------------------------


def test_enough_stock_fully_allocated():
    ...
def test_partial_stock_partially_allocated():
    ...
def test_no_stock_backordered():
    ...
```

As in Tutorial 03, the first eight tests map one-to-one onto the spec's own §11 table. Everything
after that section comment exists because a decision this tutorial has walked through needed
executable proof, not just prose: `# --- IA-001 sort order edge cases ---` (Part 3),
`# --- IA-002 / IA-007 warehouse choice edge cases ---` (Parts 4 and 6),
`# --- IA-008 reorder alert edge cases ---` (Part 7), `# --- AllocationSummary ---` (Parts 1 and 8),
and `# --- Malformed / missing required inventory data ---` / `# --- Malformed / missing required
valid order data ---` (Part 2). The file's own docstring (lines 1-3) states this directly: *"every
IA-001..IA-008 rule (V1 only, no Optional V2 region-matching)... plus the edge cases resolved
during the Phase 4 `/architect` session."*

Two of this module's decisions have no textual anchor in the spec at all —
`allocatable_qty` vs. `available_qty` for warehouse choice, and what `warehouse` means on a fully-
backordered line — and for exactly those two, the tests are the *only* place the decision is
pinned down as a checkable fact rather than a sentence someone has to trust. A future contributor
who reads only `02_demo_inventory_allocation.md` and never opens `tests/test_inventory_
allocation.py` would have no way to discover that `_pick_warehouse` uses `allocatable_qty`, not
`available_qty` — `test_reserved_stock_reduces_allocatable_qty` and `test_warehouse_choice_
switches_as_stock_depletes` are the executable evidence Part 4 and Part 5 both leaned on.

**Checkpoint:** `plan.md` states the module was "manually verified against `sample_data/
sample_orders.xlsx` + `sample_data/sample_inventory.xlsx`... output matches the hand-authored
fixtures in `tests/contract_fixtures.py` field-for-field." Why does this manual verification matter
in addition to the 22 new inline-DataFrame tests, given Tutorial 02's point that exhaustive rule
coverage belongs in pytest fixtures, not sample workbooks?

<details>
<summary>Reveal answer</summary>

The inline-DataFrame tests each isolate exactly one rule or edge case, deliberately stripped of
everything else (Tutorial 02's test-fixture-vs-demo-fixture distinction) — they prove each rule
works in isolation, but say nothing about whether the rules compose correctly when a realistic,
multi-SKU, multi-warehouse, many-orders batch runs through the *whole* module at once, in the
believable shape a real portfolio reviewer would actually open and inspect. Manually checking the
full sample-data run against `tests/contract_fixtures.py`'s hand-authored (Tutorial 02 Part 3:
independently-authored, not derived from the generator) fixtures is a different kind of check — an
integration-level sanity pass that the isolated unit tests can't provide by construction, precisely
because each one only ever sets up the minimal scenario needed to exercise its own rule.
</details>

**Try it yourself:** Run `uv run pytest tests/test_inventory_allocation.py -v` and count the total
number of tests. Then find the one test (`test_missing_reserved_qty_column_defaults_to_zero`,
lines 187-191) that proves `reserved_qty`'s graceful-degradation behavior specifically — confirm it
constructs an inventory row with the `reserved_qty` *column* entirely removed (`del
inventory_row["reserved_qty"]`), not merely left blank, and cross-reference this against Part 2's
fail-fast/graceful-degradation distinction: this is exactly the kind of test a required field like
`available_qty` could never pass, since removing its column would trigger `MissingColumnsError`
instead.

## Full data flow: MED-LENS-001, across two warehouses and two competing orders

Trace two already-validated order lines and one SKU stocked in two warehouses through the entire
module — built to exercise warehouse switching (Part 5/6), the strict reorder boundary (Part 7),
and distinct-SKU counting (Part 8) in one pass.

**Input — inventory (file order):**

| sku | warehouse | available_qty | reserved_qty | reorder_point |
|---|---|---|---|---|
| MED-LENS-001 | HK Warehouse | 20 | 0 | 5 |
| MED-LENS-001 | SG Warehouse | 10 | 0 | 3 |

**Input — valid orders (file order, note SO-2026-010 appears first in the file but is Normal
priority):**

| order_id | priority | quantity | requested_delivery_date | order_date |
|---|---|---|---|---|
| SO-2026-010 | Normal | 8 | 2026-07-20 | 2026-07-01 |
| SO-2026-011 | High | 15 | 2026-07-18 | 2026-07-02 |

1. **Validated order row.** Both rows already carry `sku=MED-LENS-001` and passed Phase 3 in full —
   this module trusts them as-is, only re-checking presence/parseability of each required field
   (`_require_order_quantity`, `_require_order_date`, `_require_order_priority`,
   `src/inventory_allocation.py:255-275`).
2. **IA-001 sort position.** `_sort_orders_for_allocation` (lines 251-284) builds both `prepared`
   dicts, then sorts by `(PRIORITY_RANK, delivery, order_date, order_id)`. `SO-2026-011` is `High`
   (rank `0`); `SO-2026-010` is `Normal` (rank `1`). Despite appearing *second* in the source file,
   `SO-2026-011` sorts first — `sorted_orders = [SO-2026-011, SO-2026-010]`.
3. **`_build_inventory_state`** (lines 220-248) builds `by_sku["MED-LENS-001"]` as two entries —
   HK: `{"allocatable_qty": 20, "allocated_qty": 0, "reorder_point": 5, ...}`, SG:
   `{"allocatable_qty": 10, "allocated_qty": 0, "reorder_point": 3, ...}` — and `entries` holds the
   *same two dict objects* (Part 5's aliasing).
4. **First line: `SO-2026-011` (High, qty 15).** `_allocate_order_line` (lines 292-333) looks up
   `entries = inventory_by_sku["MED-LENS-001"]` — both HK and SG present.
5. **Warehouse candidates → chosen warehouse.** `_pick_warehouse` (lines 287-289) sorts by
   `(-allocatable_qty, warehouse)`: HK's `20` beats SG's `10` — **HK Warehouse chosen**.
6. **Allocatable balance mutation.** `allocatable (20) >= quantity (15)` → IA-003 full allocation:
   `allocated_qty = 15`, `status = "Fully Allocated"`. Lines 310-311 mutate HK's entry in place:
   `allocatable_qty: 20 → 5`, `allocated_qty: 0 → 15`.
7. **Allocation row.** `SO-2026-011` → `{"warehouse": "HK Warehouse", "allocated_qty": 15,
   "backorder_qty": 0, "status": "Fully Allocated", ...}`.
8. **Second line: `SO-2026-010` (Normal, qty 8).** Same `entries` list — but HK's entry now shows
   `allocatable_qty = 5` (Part 5's mutation, observed automatically through the shared dict).
9. **Warehouse candidates → chosen warehouse, again.** `_pick_warehouse` re-sorts the *same two
   entries*, now `(-5, "HK Warehouse")` vs. `(-10, "SG Warehouse")` — **SG Warehouse now wins**,
   demonstrating mid-batch warehouse switching (Part 5/6) — a genuinely different SKU/warehouse
   choice than line 1, computed by the identical `_pick_warehouse` function with no special-casing.
10. **Allocatable balance mutation.** `allocatable (10) >= quantity (8)` → IA-003 full allocation
    again: `allocated_qty = 8`. SG's entry mutates: `allocatable_qty: 10 → 2`, `allocated_qty: 0 →
    8`.
11. **Allocation row.** `SO-2026-010` → `{"warehouse": "SG Warehouse", "allocated_qty": 8,
    "backorder_qty": 0, "status": "Fully Allocated", ...}`. Neither line backorders in this trace —
    `backorders` ends up empty.
12. **Remaining inventory** (lines 394-403, after all allocation finishes). For HK's entry:
    `remaining_qty = starting_available_qty (20) - allocated_qty (15) = 5`; `reorder_point = 5`;
    `5 < 5` is `False` — `reorder_alert = "No"` (Part 7's strict-`<` boundary, exactly on the line).
    For SG's entry: `remaining_qty = 10 - 8 = 2`; `reorder_point = 3`; `2 < 3` is `True` —
    `reorder_alert = "Yes"`.
13. **Supplier follow-up.** Only SG's entry produces a `SupplierFollowUpRow`:
    `{"sku": "MED-LENS-001", "warehouse": "SG Warehouse", "remaining_qty": 2, "reorder_point": 3,
    ...}`. `low_stock_skus.add("MED-LENS-001")` runs once, for SG's alert only — HK's entry never
    alerts, so it never adds to the set a second time regardless.
14. **Summary count.** `_build_summary` (lines 369-379): `total_order_lines = 2`,
    `fully_allocated_count = 2`, `partially_allocated_count = 0`, `backordered_count = 0`,
    `low_stock_sku_count = len(low_stock_skus) = 1` — one distinct SKU, even though only one of its
    two warehouses actually alerted (Part 8; had *both* warehouses alerted, this number would still
    read `1`, exactly `test_low_stock_sku_count_counts_distinct_skus_not_warehouse_rows`'s point).

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Open
`tests/test_inventory_allocation.py:133-148` (`test_inventory_never_goes_negative_across_multiple_
orders`). Before reading the assertions, predict — using Parts 3, 4, and 5 — the `warehouse`,
`status`, `allocated_qty`, and `backorder_qty` for *both* orders, and the final `remaining_qty` for
the one inventory row. Both orders share the same `priority` (`High`); work out which one wins the
IA-001 tie-break and why.

<details>
<summary>Hint</summary>

Both orders are `High` priority, so `PRIORITY_RANK` alone doesn't separate them — check each
order's `requested_delivery_date` (the second sort key) directly from `_order_row`'s default
(`date(2026, 7, 15)`) versus what `SO-2026-002` explicitly overrides. Then apply Part 5's
depletion logic: whichever order sorts first gets first claim on the single warehouse's
`allocatable_qty`, and the second order sees whatever's left, exactly like the end-to-end trace's
second line.
</details>

**Challenge 2 — Extend** (20–30 min): Design (don't implement — this needs its own ADR, since it
changes what an `AllocationResultRow` can represent) how the module would support one order line
being split across two warehouses when no single warehouse holds enough stock but the SKU's
*combined* stock across all its warehouses would fully cover it. This is the same design question
raised as a checkpoint in Part 6 — here, write out a concrete answer covering: which function(s)
enforce today's "one line, one warehouse" rule and would need to change; what the new
`AllocationResultRow`-family shape would need to look like; how the change would affect Part 7's
reorder-alert calculation, since one order line could now deplete two warehouses' balances at once
instead of one; and the name and assertion of at least one new test that doesn't exist today
because splitting can't currently happen.

<details>
<summary>Hint</summary>

Re-read Part 6's checkpoint answer for the mechanical starting point (`_pick_warehouse` returning a
ranked list, `_allocate_order_line` looping until the order is filled or candidates are exhausted).
The genuinely new part of this challenge is the *test*: think about what property must hold across
*all* the rows produced for one split order line (their `allocated_qty` values sum to no more than
`requested_qty`, and no single row's `allocated_qty` exceeds that warehouse's `allocatable_qty` at
the moment it was drawn from) — write that as a concrete `assert`.
</details>

**Challenge 3 — Break and fix** (30–45 min): Imagine `_pick_warehouse` (line 289) used raw
`available_qty` instead of `allocatable_qty` for warehouse selection — the literal, ambiguous
reading of IA-007's text that Part 4 explains was rejected. Before changing any code, predict:
which existing test would fail first, and what *wrong* warehouse it would pick instead of the
correct one. Then actually change `_pick_warehouse`'s sort key from `-e["allocatable_qty"]` to
`-e["available_qty"]` (note: `available_qty` isn't a key in `entry` — you'll need to also change
what field name is being read, or temporarily add one), run
`uv run pytest tests/test_inventory_allocation.py -v`, and compare the actual failure to your
prediction. Revert the change afterward.

<details>
<summary>Hint</summary>

`test_reserved_stock_reduces_allocatable_qty` (lines 122-130) is a single-warehouse test, so it
won't distinguish the two readings by itself — look instead for a test with *two* warehouses where
one has a much higher `available_qty` but also a much higher `reserved_qty`. If no existing test
happens to construct exactly that scenario, that's itself worth noting as a finding: it means this
specific failure mode — the one `explanation.md` names as the reason `allocatable_qty` was chosen
— currently has no regression test guarding it directly, only Part 4's narrower single-warehouse
proof that reservations reduce what's allocatable at all.
</details>

For deeper exploration, `docs/plan/phase-4-inventory-allocation-core/ai-discussion-topics.md` has
10 prompts covering ambiguity resolution versus contradiction, stateful business logic, inferring
undocumented behavior, and summary-statistic double-counting. Feed them to an LLM *after* forming
your own answer first — the gap between what you thought and what you learn is where understanding
lands.
