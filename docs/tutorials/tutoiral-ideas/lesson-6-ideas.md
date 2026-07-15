/tutorial docs/plan/phase-6-excel-report-export

Create Tutorial 06 as Track 3 — Presentation Without Leakage. This tutorial should pivot from Tutorials 03–05, which produced business results, to Phase 6, which consumes those result envelopes and formats them without recomputing any business logic.

Treat the main teaching arc as:

1. Phases 3–5 produce trusted envelopes.
2. Phase 6 accepts those envelopes as already-computed truth.
3. `report_export.py` is a presentation layer: it writes workbooks, manifests, sheet order, headers, blanks, and formatting.
4. The core invariant is “format, don’t recalculate.”

Before writing, read at minimum:

- `docs/teach/ROADMAP.md`
- `docs/tutorials/03-order-validation-core/README.md`
- `docs/tutorials/04-inventory-allocation-core/README.md`
- `docs/tutorials/05-payment-aging-core/README.md`
- `docs/plan/phase-6-excel-report-export/plan.md`
- `docs/plan/phase-6-excel-report-export/explanation.md`
- `docs/plan/phase-6-excel-report-export/ai-discussion-topics.md`
- `src/report_export.py`
- `tests/test_report_export.py`
- `tests/contract_fixtures.py`
- `src/contracts.py`
- `src/order_validation.py`
- `src/inventory_allocation.py`
- `src/payment_aging.py`
- `context/code-standards.md`
- `context/build-plan.md`

Make Tutorial 05 the immediate prerequisite because it completes the business-core trilogy. Reference Tutorials 03 and 04 when explaining the three envelope inputs. Do not re-teach validation, allocation, or payment aging internals except to show that Phase 6 must not duplicate them.

Recommended Part structure:

1. Result envelopes become workbook inputs, not raw DataFrames
2. Workbook generation in memory: `Workbook` → sheets → `BytesIO` → bytes
3. Manifest generation from actual workbook state
4. Envelope imports: why result types live in business modules, not `contracts.py`
5. Explicit sheet/header constants instead of deriving from row data
6. `_safe_cell_value` and the `openpyxl` empty-string/`None` round trip
7. Raw DataFrame sheet handling for `Original Orders`
8. `Follow-up List` as the one derived presentation sheet, using an allow-list
9. Deterministic timestamps, report IDs, and no hidden global state
10. Presentation-only formatting: header styles, autosize, and draft-message wrapping

For every Part, include verbatim code from `src/report_export.py` or `tests/test_report_export.py`. Prefer tests when they prove the design rule better than the implementation alone, especially:

- `test_order_validation_report_sheet_names_match_manifest_fixture`
- `test_order_validation_report_empty_errors_sheet_has_header_only`
- `test_order_validation_report_missing_notrequired_field_renders_blank`
- `test_order_validation_report_original_orders_empty_when_none`
- `test_inventory_allocation_report_backorders_sheet_uses_precomputed_list_as_is`
- `test_payment_aging_report_follow_up_list_includes_watch_high_medium_low`
- `test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string`
- `test_payment_aging_report_aging_summary_follows_provided_dict_not_hardcoded_order`
- `test_payment_aging_report_draft_message_cell_wraps_text`
- `test_payment_aging_report_report_id_format`

The end-to-end trace should follow one `PaymentAgingResult` through:
`export_payment_aging_report()` → `follow_up_rows` filter → workbook creation → summary sheet → follow-up sheet → all invoices sheet → data issues sheet → draft messages sheet → wrap-text helper → `wb.sheetnames` → `_save_workbook_bytes()` → `_build_manifest()` → `(bytes, manifest)`.

Also include a shorter trace for `export_order_validation_report()` showing why `Original Orders` comes from a separate `original_orders_df` parameter instead of being added to `OrderValidationResult`.

Weave all 14 questions from `ai-discussion-topics.md` into the Parts as checkpoints with collapsible answers. Do not create a separate quiz section.

Name failure modes explicitly:

- report export recalculating business rules and disagreeing with the source module
- deriving headers from `rows[0].keys()` and breaking empty sheets or `NotRequired` fields
- hardcoding manifest sheet names separately from the real workbook
- trusting in-memory workbook values without save/load round-trip verification
- writing raw `NaN`, `NaT`, `pd.NA`, or `None` into cells
- using `!= "None"` instead of an explicit follow-up allow-list
- adding a global report counter and introducing hidden state
- conditionally omitting `Original Orders`
- duplicating payment-aging bucket order inside `report_export.py`
- folding draft-message wrapping into generic detail-sheet logic

Write the tutorial to:
`docs/tutorials/06-excel-report-export/README.md`

Do not update `progress-tracker.md` or `ui-registry.md`.
