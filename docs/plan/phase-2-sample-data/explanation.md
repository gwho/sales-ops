# Phase 2: Sample Data and Contract Fixtures — Technical Explanation

## Why `reference_date: date | None = None` instead of `reference_date: date = date.today()`

Python evaluates default argument values exactly once, when the `def` statement runs (at module import time), not on every call. A literal `date.today()` default would freeze to whatever date `src/sample_data.py` happened to be imported on in the current process — every subsequent call in that process would silently reuse that stale value, and long-running processes (a notebook kernel, a FastAPI worker later on) would never see it advance. The `None`-sentinel pattern defers the `date.today()` call to function-call time:

```python
def generate_invoices(reference_date: date | None = None) -> pd.DataFrame:
    if reference_date is None:
        reference_date = date.today()
```

This is the standard fix for any "mutable or time-dependent default argument" case in Python, not just lists/dicts.

## Why invoice dates are relative but order/inventory dates are fixed

Payment-aging rules (`03_demo_payment_aging.md` PA-003/PA-004) compute `days_overdue = today - due_date` and bucket by how large that gap is. A hardcoded `due_date` of, say, `2026-06-01` reads as "20 days overdue" today and "400+ days overdue" a year from now — the "Current, not yet due" example would eventually flip into the 90+ Days bucket, breaking the believable mix the sample data is supposed to demonstrate. Order validation (`OV-005`) and inventory allocation only ever compare dates *within the same file* to each other (`requested_delivery_date` vs `order_date`), never against "today", so those two workbooks don't have this drift problem and use plain fixed 2026-07 dates matching the specs' own examples.

## Why contract fixtures aren't computed from the sample workbooks

`ValidationErrorRow`, `AllocationResultRow`, and `PaymentAgingRow` are all *outputs* of business rules that don't exist until Phases 3-5. Computing them from `sample_orders.xlsx`/`sample_inventory.xlsx`/`sample_invoices.xlsx` right now would mean writing throwaway validation/allocation/aging logic just to populate fixtures — exactly the kind of premature implementation the Phase 2 scope excludes. Instead, each fixture is a hand-authored dict that's *internally consistent* with the sample data where it's easy to be (e.g. `VALIDATION_ERROR_ROW_FIXTURE` cites the same `MED-LENS-999` SKU that's actually in `sample_orders.xlsx`), but the fixture module carries an explicit docstring boundary noting it is not proof any rule is implemented.

## Why the reorder-point scenario is a static fact, not a computed one

`context/build-plan.md` asks for "at least 1 SKU near reorder point" in `sample_inventory.xlsx`. The natural way to get there would be to simulate allocation (deplete stock against `sample_orders.xlsx` demand, then check what's left) — but that's Phase 4's algorithm. Instead, `MED-LENS-001`'s SG Warehouse row is authored so `available_qty` (5) is already below `reorder_point` (6) as written, with no allocation math involved. `tests/test_sample_data.py` asserts this directly (`available_qty - reserved_qty < reorder_point`) rather than reimplementing IA-002/IA-008.

Separately, `MED-LENS-001`'s total order demand (10 + 25 = 35 units, from `SO-2026-001` and `SO-2026-008`) exceeds its total inventory across both warehouses (20 + 5 = 25 units) by construction — this is what will force Phase 4's allocation engine to produce a partial allocation and a backorder once it exists, but Phase 2 doesn't assert or compute that outcome.

## Why `sample_data.py` writes single-sheet workbooks

Each spec's "Input file" section (`01_demo_order_validation.md` §4, `02_demo_inventory_allocation.md` §4, `03_demo_payment_aging.md` §4) describes a flat table of source data — these are the files a sales admin would actually receive from customers or accounting, not report packs. Multi-sheet workbooks with summaries, detail rows, and data-issue sheets are the *output* of `report_export.py`, which is Phase 6.
