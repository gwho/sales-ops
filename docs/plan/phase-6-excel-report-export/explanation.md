# Explanation — Feature phase-6-excel-report-export: Excel Report Export

## 1. The end-to-end data flow, from envelope to workbook bytes

Every export function follows the same four-step shape, and understanding it once
means understanding all three. Take `export_payment_aging_report(result, generated_at)`
as the concrete example: `result` is a `PaymentAgingResult` — the exact dict
`calculate_payment_aging()` already returned, untouched, containing `summary`,
`aging_rows`, `data_issues`, and `draft_messages`. Step one, `_new_workbook()` creates
an `openpyxl.Workbook()` and immediately removes the default `"Sheet"` it ships with —
without this, every workbook would carry a stray blank first sheet ahead of the real
ones, which would break every `wb.sheetnames == expected` assertion in the test suite.
Step two, the function calls `_write_summary_sheet`, `_write_detail_sheet` (four
times, once per detail sheet), each of which calls `wb.create_sheet(name)` in the exact
order the sheets must appear — `openpyxl` preserves creation order in `wb.sheetnames`,
so sheet order in the code *is* sheet order in the file; there is no separate ordering
step. Step three, `wb.save(buffer)` writes the whole workbook into an `io.BytesIO()`
buffer instead of a file path — `openpyxl.Workbook.save()` accepts either a path string
or any file-like object, and a `BytesIO` satisfies the file-like-object contract, which
is what makes an entirely disk-free save possible. Step four, `_build_manifest` builds
the `ReportManifest` dict from `wb.sheetnames` (the *actual* sheets just created, not a
hardcoded list, so the manifest can never drift out of sync with the real workbook) plus
the report type, file name, and the resolved timestamp. The function returns both the
raw bytes (`buffer.getvalue()`) and the manifest together — nothing downstream has to
reconstruct either one from the other.

## 2. Why the envelope types had to be imported from three different modules, not `contracts.py`

The first version of `report_export.py` imported `OrderValidationResult`,
`InventoryAllocationResult`, and `PaymentAgingResult` from `src.contracts`, alongside
`ReportManifest`. Running the new tests immediately failed at collection time with
`ImportError: cannot import name 'InventoryAllocationResult' from 'src.contracts'`.
The reason is a distinction the Phase 6 planning session's research had actually
already surfaced but which didn't get carried through into the first draft of the
code: `contracts.py` only holds the individual row/summary `TypedDict`s
(`ValidationSummary`, `PaymentAgingRow`, etc.) — the *envelope* types that bundle them
together (`OrderValidationResult`, `InventoryAllocationResult`, `PaymentAgingResult`)
are defined locally inside `order_validation.py`, `inventory_allocation.py`, and
`payment_aging.py` respectively, one per module, established back in Phases 3–5. This
is a real module-boundary decision, not an oversight: each business module owns the
shape of its own output, and `contracts.py` only owns the shared row-level building
blocks those envelopes are made of. The fix was a three-line import split:
`from src.contracts import ReportManifest`, then one `from src.<module> import
<Module>Result` per business module. The lesson for future modules that consume
multiple business-module outputs: check where an envelope type is actually defined
before importing, don't assume everything JSON-serializable lives in `contracts.py`.

## 3. A genuine `openpyxl` behavior that looked like a bug in `_safe_cell_value` but wasn't

`_safe_cell_value` converts `None` to `""` specifically so that a blank `NotRequired`
field or a blank pandas cell never writes the literal text `"None"` or a raw `NaN`
float into a spreadsheet cell. The first draft of the tests asserted this literally:
write `None`, expect to read back `""`. Three tests failed with an unexpected
diff — `None != ''` — even though `_safe_cell_value` was working exactly as designed.
Isolating the behavior with a four-line reproduction (write `''` to a cell, save to
`BytesIO`, reload with `load_workbook`, print the value) confirmed the mechanism:
`openpyxl` does not preserve a written empty string as a distinct value through a
save/reload round trip. Internally, an empty string cell has no meaningful XML
representation distinct from "no value here" in the underlying `.xlsx` format, so on
reload it comes back as `None` — a genuinely blank cell, not the string `""`. This
isn't a defect in `_safe_cell_value` or in `report_export.py` — the actual goal (no
visible `"None"` text, no `NaN` artifact, a clean blank cell in the real spreadsheet a
person opens) is fully achieved. It's a fact about how `openpyxl`/`.xlsx` represent
"nothing" that only becomes visible once you write, save, and reload, rather than just
inspecting the in-memory `Workbook` object before saving. The fix was in the tests, not
the implementation: every assertion checking a `_safe_cell_value`-cleaned cell now
expects `None` post-round-trip, with a one-line comment explaining why, so a future
reader doesn't mistake the `None` for evidence the cleaning didn't happen.

## 4. Where `NaN`/`NaT` actually come from, and why two different code paths need `_safe_cell_value`

`_safe_cell_value` is called from two structurally different places, because "missing
data" arrives in two structurally different shapes. In `_write_detail_sheet`, every row
is already a `TypedDict` instance from a business module's envelope — a plain Python
dict. A field declared `NotRequired[str]` (like `ValidationErrorRow.order_id`) is
either present with a real string, or simply absent from the dict entirely; nothing in
this path ever produces a genuine `NaN`. `row.get(col, "")` already handles the absent
case, but a row *could* still explicitly carry `None` for a key that's present but
unset, which `.get()` alone wouldn't catch (it only substitutes the default for a
missing key, not for a key mapped to `None`) — `_safe_cell_value` closes that gap. In
`_write_raw_dataframe_sheet`, the input is a raw pandas `DataFrame` — `original_orders_df`,
built via `pd.read_excel()` on an uploaded file, or in tests, `pd.DataFrame([...])`
constructed directly from Python dicts. Any blank cell in a real uploaded spreadsheet
becomes `NaN` once pandas parses it (or `NaT` if the column is dtype `datetime64`), and
critically, `pd.DataFrame`'s column-type inference means a column with one `None` and
one `15` gets upcast to `float64`, turning the `15` into `15.0` and the `None` into
`float('nan')` — a completely different runtime representation than the `TypedDict`
path ever produces. `_safe_cell_value`'s `isinstance(value, float) and math.isnan(value)`
check catches this float-NaN case; the `pd.isna(value)` fallback (wrapped in
`try/except` since it raises on some non-scalar inputs) catches `NaT` and `pd.NA`
similarly. Both call sites route through the same helper specifically so a future
change to how one path cleans data doesn't silently diverge from how the other does.

## 5. Why sheet headers are hardcoded constants instead of `list(rows[0].keys())`

An early instinct when writing `_write_detail_sheet` might be to derive the header row
from whatever the first row's keys happen to be — it's less code, and for a
non-empty list of uniform rows, it produces the same output as an explicit constant.
Two real scenarios rule this out, both of which the test suite deliberately exercises.
First, `test_order_validation_report_empty_errors_sheet_has_header_only` passes an
empty `errors` list — there is no "first row" to derive keys from, so this approach
would need a special case just for the empty-list scenario, or the sheet would render
with zero header cells at all, which is arguably worse than a header with zero data
rows. Second, `test_order_validation_report_missing_notrequired_field_renders_blank`
constructs a `ValidationErrorRow` missing the `NotRequired` `sku` and `order_id`
fields entirely (not blank, *absent* from the dict) — if a report ever had one row with
`sku` present and another without it, and headers were derived from "whichever row
happens to be at index 0," the rendered column set would depend on data ordering, which
is not a property a report a human reads and files away should have. The chosen
solution — `VALIDATION_ERROR_COLUMNS = ["row_number", "order_id", "sku", "error_code",
"error_message", "severity"]`, defined once per sheet type, matching each `TypedDict`'s
field-declaration order in `contracts.py` — makes the header row a property of the
*contract*, not of whatever data happens to be present. `row.get(col, "")` for every
column in the constant, on every row, is what makes this indifferent to which
`NotRequired` fields any individual row omits.

## 6. `Follow-up List`: the one sheet report_export.py actually derives, and why it's an allow-list

Every sheet except one is a direct pass-through of a list already sitting in an
envelope — `Backorders` writes `result["backorders"]` as-is because
`inventory_allocation.py` already filtered it to `status == "Backordered"` when it
built `InventoryAllocationResult`. `Follow-up List` is different: `PaymentAgingResult`
has no precomputed field matching it, so `export_payment_aging_report` builds it itself
by filtering `result["aging_rows"]`. The filter predicate —
`row["follow_up_priority"] in FOLLOW_UP_PRIORITIES` where `FOLLOW_UP_PRIORITIES =
{"High", "Medium", "Low", "Watch"}` — is deliberately an allow-list rather than the
equivalent-today exclusion `row["follow_up_priority"] != "None"`. For every row
`payment_aging.py` actually produces (which only ever emits one of exactly five known
priority strings, per Phase 5's own test coverage), the two versions produce identical
output; `test_payment_aging_report_follow_up_list_includes_watch_high_medium_low`
confirms this for all four included tiers plus the excluded `"None"` tier in one test.
The reason for the stricter version shows up in
`test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string`, which
feeds a row with `follow_up_priority: "Unexpected"` and asserts it does *not* appear in
`Follow-up List`. This is presentation-layer defense-in-depth over a module that
`report_export.py` deliberately never revalidates — if `payment_aging.py` ever changes
in a way that produces an unanticipated priority string, an allow-list means that row
silently doesn't show up in the "needs attention" sheet (safe direction: a human might
miss a row, but no wrong-looking row appears), whereas the exclusion version would
silently *include* it as something requiring follow-up (less safe direction: a report a
sales rep acts on now contains an entry with a priority value the code never
anticipated).

## 7. `report_id` and `generated_at`: deterministic without any persistent state

`report_id` is built as `f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"` —
purely a function of two inputs the call already has, with no module-level counter,
no database lookup, nothing that persists between calls. This matters because
`tests/contract_fixtures.py`'s hand-authored `REPORT_MANIFEST_FIXTURES` end their
`report_id` values in `-001`, which reads like a sequential counter — but nothing in
this project has a report registry to count against, and inventing one (even a simple
in-memory dict mapping `report_type` to a running count) would be exactly the "hidden
global state" `context/code-standards.md` prohibits, plus it would make report
generation order-dependent in a way tests would have to carefully control. A
timestamp-based ID sidesteps this entirely: two calls in the same second for the same
report type would collide, but that's an acceptable risk for a portfolio demo with no
concurrent-request scenario, and it's trivially fixable later (e.g. appending a short
random suffix) without changing the function's signature. `generated_at` itself follows
the exact pattern Phase 5's `as_of_date` established: `generated_at: datetime | None =
None` in the signature, resolved via `effective_generated_at = generated_at or
datetime.now()` inside the function body — never `datetime.now()` as a literal default
argument value, which Python evaluates once at module-import time and would silently
freeze at whatever moment the interpreter first loaded `report_export.py`. The one
addition beyond the `as_of_date` precedent is `effective.isoformat(timespec="seconds")`
instead of a bare `.isoformat()` — without `timespec="seconds"`, the ISO string
includes microseconds, and `GENERATED_AT = datetime(2026, 7, 9, 9, 15, 0, 123456)` in
the test file (deliberately constructed with a nonzero microsecond component) proves
the manifest's `generated_at` field ends up exactly `"2026-07-09T09:15:00"`, not
`"2026-07-09T09:15:00.123456"` — the microseconds are dropped, not just happening to
be absent because the test picked a round number.

## 8. `Original Orders`: the one sheet whose data doesn't come from the envelope at all

`OrderValidationResult` — the return value of `validate_orders()` — contains exactly
`summary`, `valid_orders`, and `errors`. It was designed in Phase 3 around what the
*validation rules* in `01_demo_order_validation.md` require, and nothing in that scope
called for retaining the raw uploaded rows. But the report's `Original Orders` sheet
(required by `REPORT_MANIFEST_FIXTURES`, which locks it as the fourth sheet in the
order-validation workbook) comes from a *different* section of the same spec — §7's
Downloadable Output — written with the report in mind, not the validation function.
`export_order_validation_report` resolves this by accepting a second parameter,
`original_orders_df: pd.DataFrame | None = None`, entirely separate from `result`. This
keeps `OrderValidationResult`'s contract untouched — no `raw_orders` field was added to
it — while still letting the report include the data. The `Original Orders` sheet is
always created regardless of whether this parameter is provided: passing `None`
(as several structural tests in `test_report_export.py` do, since they're testing the
other three sheets and don't need a real orders DataFrame) produces a header-only
"Original Orders" sheet rather than a workbook missing that sheet entirely — dropping
the sheet conditionally would mean the workbook's sheet count depends on an
implementation detail of the caller, not on anything the `REPORT_MANIFEST_FIXTURES`
contract actually varies by.

## 9. The header-fill-color constant, and why it's framed as Excel styling, not a UI-token exception

`HEADER_FILL_COLOR = "D9E1F2"` is a literal hex string passed to `openpyxl.styles.
PatternFill`, which requires an RGB hex value — there is no semantic-token equivalent
in the `openpyxl` API the way `bg-accent` is a semantic Tailwind class in this
project's Next.js design system. `CLAUDE.md`'s "no hardcoded hex values" rule is scoped
to that Next.js/Tailwind UI layer (`context/ui-tokens.md` defines the semantic
vocabulary it's about); it was never written with backend `.xlsx` generation in mind,
since no Python module touched `openpyxl` before this phase. Rather than lean on that
scoping distinction implicitly, the constant is named and commented in the code itself
(`report_export.py`'s constants section carries a one-line note that this is workbook
styling, distinct from the UI design system) so a future reader — or a future automated
lint pass looking for raw hex strings — has the reasoning available at the point of
use, not just in a planning document that may not be open at the same time.
