# Plan — Feature phase-6-excel-report-export: Excel Report Export

## What was built

- `src/report_export.py` (new) — `export_order_validation_report`, `export_inventory_allocation_report`, `export_payment_aging_report`. Each consumes an already-computed result envelope (`OrderValidationResult`, `InventoryAllocationResult`, `PaymentAgingResult`) and returns `tuple[bytes, ReportManifest]`: an in-memory `.xlsx` workbook built via `openpyxl`, plus a freshly-built manifest. Includes explicit per-sheet column-order constants, a `_safe_cell_value` helper, header styling/freeze-pane/autosize helpers, and `_build_manifest`.
- `tests/test_report_export.py` (new) — 22 tests covering sheet names/order against `REPORT_MANIFEST_FIXTURES`, manifest key-set and field values, detail-sheet header rows against the column constants, representative row values, empty-list edge cases (zero errors/backorders/data issues), the `Follow-up List` priority filter (including an unexpected-string exclusion case), `Original Orders` mirroring/empty behavior, `NotRequired`-field blank rendering, and `report_id`/`generated_at` formatting.
- `context/progress-tracker.md` — Phase 6 checklist items checked off (order/inventory/payment reports, workbook-structure test coverage); "Optional full operations report pack" left unchecked with an explicit note that it's deferred pending an ADR (V1.5-labeled in `05_integration_and_app_flow.md` §7), not silently skipped; current phase advanced past Phase 6.

`uv run pytest` passes — 149 tests (127 from Phases 1–5, 22 new).

## Schema changes

None. No fields were added to `src/contracts.py` — `ReportManifest` is used exactly as already defined (established in Phase 1). No database exists in this project.

## Key invariants

1. **`report_export.py` never performs business calculations, revalidation, allocation, or aging logic.** It only formats and writes already-computed envelope data. Any new calculation logic belongs in `order_validation.py`, `inventory_allocation.py`, or `payment_aging.py`, not here.
2. **Workbooks are built entirely in memory** (`io.BytesIO()` → `wb.save(buffer)` → `buffer.getvalue()`). `report_export.py` must never write to disk — persistence is a future API-layer concern.
3. **Sheet names and order per report are fixed by `REPORT_MANIFEST_FIXTURES`** in `tests/contract_fixtures.py`, which `tests/test_contracts.py` already asserts against. Order validation: `Summary`, `Valid Orders`, `Validation Errors`, `Original Orders`. Inventory allocation: `Allocation Summary`, `Allocation Results`, `Backorders`, `Remaining Inventory`, `Supplier Follow-up`. Payment aging: `Aging Summary`, `Follow-up List`, `All Invoices with Aging`, `Data Issues`, `Draft Messages`. Changing any sheet name or reordering sheet creation breaks both this module's own tests and the Phase 2 contract-fixture tests.
4. **Detail-sheet column headers always come from the explicit module-level constants** (`VALIDATION_ERROR_COLUMNS`, `VALID_ORDER_COLUMNS`, etc.), matching each `TypedDict`'s field-declaration order in `contracts.py`. Never derive headers from `dict.keys()` at runtime — this breaks on empty row lists and on `NotRequired`-field asymmetry between rows.
5. **Every cell value must pass through `_safe_cell_value` before being written.** Raw `None`, `NaN`, `NaT`, or `pd.NA` must never reach `ws.append()` or a direct cell assignment — doing so risks Excel flagging the workbook as containing invalid numeric content.
6. **`Follow-up List` uses the explicit `FOLLOW_UP_PRIORITIES` allow-list** (`{"High", "Medium", "Low", "Watch"}`), not a `!= "None"` exclusion. An unrecognized priority string is excluded by default, not included. If `payment_aging.py` ever adds a new priority tier, it must be added to `FOLLOW_UP_PRIORITIES` explicitly — it will not appear in the report automatically.
7. **`report_id` is timestamp-based** (`f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"`) with no persistent counter or module-level state. Do not add a sequential-counter mechanism — that would introduce hidden global state this project's coding standards explicitly prohibit.
8. **`generated_at` is always resolved inside the function body** via `generated_at or datetime.now()`, never as a literal default-argument value (the classic eager-default-evaluation trap). The manifest's `generated_at` string is always `effective.isoformat(timespec="seconds")` — never full microsecond precision.
9. **The `Original Orders` sheet is always created**, regardless of whether `original_orders_df` is `None`. It is never conditionally omitted from the workbook — only its row count varies (header-only when `None`/empty).
10. **`operations_follow_up_pack.xlsx` is out of scope.** It is V1.5-labeled in its source spec (`05_integration_and_app_flow.md` §7); implementing it requires a new ADR reopening scope, not just filling in the build-plan's checkbox.
