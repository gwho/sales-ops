# AI Discussion Topics — Feature phase-6-excel-report-export: Excel Report Export

## On the envelope-to-workbook data flow and module boundaries

1. `_build_manifest` derives `sheet_names` from `wb.sheetnames` (the workbook's actual
   sheets) rather than from a hardcoded list passed in alongside the sheet-writing
   calls. What would have to go wrong in the code for this to actually drift out of
   sync with reality, given the alternative (a separate hardcoded list) could drift by
   a simple copy-paste mistake?
2. The `ImportError` for `InventoryAllocationResult` happened because envelope types
   live in each business module, not in `contracts.py`. If a fourth business module
   were added to this project later, how would you decide whether its envelope type
   belongs in that new module or should finally get promoted into `contracts.py`?
3. `report_export.py` takes each business module's *envelope* as input, never the raw
   DataFrames the specs originally suggested. Walk through what would have to change in
   this module, and in every caller, if a future spec change meant `payment_aging.py`
   needed to return a fourth piece of information not currently in `PaymentAgingResult`.

## On the `openpyxl` empty-string/`None` round-trip discovery

4. `_safe_cell_value` writes `""` for missing values, but reading a saved-and-reloaded
   workbook shows `None` instead. If a future test asserted `cell.value == ""` and
   passed against an in-memory `Workbook` object that was never saved and reloaded,
   would that test still be trustworthy? What's actually different between inspecting
   an unsaved `Workbook` and inspecting one that went through `save()` → `load_workbook()`?
5. The bug (or non-bug) was found by writing a four-line reproduction script isolated
   from the rest of the test suite, rather than by staring at the failing assertion
   diff. What made this the right next step here, versus just adjusting the assertion
   and moving on without confirming *why* it needed adjusting?

## On explicit column constants vs. deriving headers from data

6. `_write_detail_sheet` uses `row.get(col, "")` against an explicit column list. What
   happens — concretely, cell by cell — if a `TypedDict` row is passed with a key that
   isn't in the corresponding column constant at all (e.g. a typo'd field name)? Is
   that failure mode acceptable, or would you want it to raise instead?
7. The explicit-constants approach ties every sheet's headers to `contracts.py`'s field
   declaration order. If a field's order in a `TypedDict` definition were changed
   (with no other code change), would you expect that to be a breaking change for
   `report_export.py`, a silent behavior change, or a no-op? Why?
8. `BackorderRow(AllocationResultRow)` is a subclass with no new fields — `Backorders`
   and `Allocation Results` share the same `ALLOCATION_RESULT_COLUMNS` constant.  If
   `BackorderRow` ever gained a field `AllocationResultRow` doesn't have (say, a
   backorder-specific ETA), what would need to change, and where would that decision
   need to be made first — in `contracts.py`, in `inventory_allocation.py`, or in
   `report_export.py`?

## On the `Follow-up List` allow-list as defense-in-depth

9. The allow-list (`{"High", "Medium", "Low", "Watch"}`) and the equivalent exclusion
   (`!= "None"`) produce identical output for every row `payment_aging.py` currently
   emits. Is it worth adding a code comment explaining *why* the stricter version was
   chosen, given nothing currently exercises the difference — or does the dedicated
   test (`test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string`)
   already serve that documentation purpose on its own?
10. `report_export.py`'s stated design principle is "trust the envelope, don't
    revalidate." Does the allow-list choice violate that principle in spirit, or is
    filtering-with-a-safe-default a different category of thing from revalidation?
    Where exactly is the line between the two?
11. If `payment_aging.py` legitimately added a sixth priority tier in a future phase,
    the allow-list version would silently exclude every row with that tier from
    `Follow-up List` until someone updated `FOLLOW_UP_PRIORITIES` — with no error, no
    warning, just quietly missing rows. Is silent omission an acceptable failure mode
    here, or should there be some signal (a test, a runtime check) that fires when a
    priority string not in the allow-list appears?

## On manifest determinism and the no-hidden-state constraint

12. `report_id`'s timestamp-based scheme can collide if the same report type is
    generated twice within the same second. Given this project has no concurrent
    web-request scenario yet, is that an acceptable risk to leave unaddressed, or
    would you fix it now? If you'd fix it, what's the simplest change that doesn't
    reintroduce the hidden-state problem a counter would bring back?
13. `generated_at`'s injectable-parameter pattern exactly mirrors `payment_aging.py`'s
    `as_of_date`. Now that this pattern has been used twice, is it worth extracting
    into a shared helper (e.g. a small `resolve_now(explicit: T | None, factory:
    Callable[[], T]) -> T` utility), or does the one-line inline resolution
    (`x or default_factory()`) not carry enough duplication to justify the
    abstraction?
14. `effective.isoformat(timespec="seconds")` truncates microseconds from the manifest
    string, but the *test* fixture `GENERATED_AT` deliberately includes microseconds to
    prove the truncation happens. What other places in this codebase might have a
    similar "the test needs to inject a deliberately awkward value to prove the
    cleanup logic actually cleans" pattern worth applying — anywhere `_safe_cell_value`
    itself is tested comes to mind, but are there others?
