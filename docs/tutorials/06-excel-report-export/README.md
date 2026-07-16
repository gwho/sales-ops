# Tutorial 06 — Excel Report Export: Presentation Without Leakage

**After completing this tutorial you will understand:** why `report_export.py` takes an
already-computed result envelope and never recalculates a single business rule, why workbooks
are built entirely in memory and a report's manifest is derived from the real `wb.sheetnames`
rather than a parallel hardcoded list, why the three envelope types
(`OrderValidationResult`, `InventoryAllocationResult`, `PaymentAgingResult`) live in their
owning business modules instead of `contracts.py`, why every sheet's headers come from
explicit column constants instead of `rows[0].keys()` — and what `openpyxl`'s save/reload
round trip reveals about `None` versus `""` — and why `Follow-up List` uses an explicit
allow-list while report IDs and timestamps are resolved fresh on every call with no
persistent state anywhere in the module.

> [!NOTE]
> **Prerequisites:** Tutorial 05 (`05-payment-aging-core/README.md`) — the immediate
> prerequisite. Phase 6 consumes the three result envelopes Phases 3–5 produced
> (`OrderValidationResult`, `InventoryAllocationResult`, `PaymentAgingResult`) as its *only*
> inputs, and this tutorial does not re-teach how any of their fields are computed. Tutorial 03
> (`03-order-validation-core/README.md`) and Tutorial 04
> (`04-inventory-allocation-core/README.md`) — referenced directly when explaining the other
> two envelope shapes this module consumes. Open
> [`src/report_export.py`](../../../src/report_export.py),
> [`tests/test_report_export.py`](../../../tests/test_report_export.py),
> [`tests/contract_fixtures.py`](../../../tests/contract_fixtures.py), and
> [`src/contracts.py`](../../../src/contracts.py) alongside this tutorial.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Set membership as an allow-list | `FOLLOW_UP_PRIORITIES = {"High", "Medium", "Low", "Watch"}`, `row["follow_up_priority"] in FOLLOW_UP_PRIORITIES` | Data structures |
| Duck-typed file object | `io.BytesIO()` passed to `wb.save(buffer)` — satisfies `openpyxl`'s "anything file-like" contract | Python language |
| Boundary-normalizing adapter | `_safe_cell_value()` — one function absorbing every "this isn't really data" representation into one clean value | Design patterns |
| Single source of truth, derived not duplicated | `_build_manifest(..., sheet_names=wb.sheetnames, ...)` reads the real workbook instead of a parallel list | System design |
| Recursive-ish flattening of nested structures | `_write_summary_sheet`'s `if isinstance(value, dict): for sub_key, sub_value in value.items(): ...` | Data structures |

## How to use an LLM before this tutorial

### Concept 1 — Presentation layer vs. business logic layer

> "Explain the difference between a 'business logic layer' (decides what a computed result
> *is* — classifies, validates, calculates) and a 'presentation layer' (formats an
> already-decided result for a human to read — a report, a screen, a printout). Give a
> concrete example of a real bug that happens when a presentation layer quietly recomputes
> something instead of trusting the value it was handed. Quiz me on how you'd tell, just by
> reading a function's body, whether it belongs to one layer or the other."

*What to listen for:* the tell is whether a function's output can *disagree* with another
part of the system looking at the same underlying fact. A presentation layer that only
formats can never disagree with the layer that computed the value — at worst it displays a
stale copy. A presentation layer that quietly recomputes can drift: a report generated an
hour after a dashboard, using logic that was patched in between, can show a different answer
for the same order than the screen the user is currently looking at, with nothing announcing
that a disagreement exists.

*Practice question:* if a report-generation function reads a value from `result["status"]`
in one line and then, two lines later, re-derives what it believes the status *should* be
from raw numbers to decide formatting, is that function still purely a presentation layer?

### Concept 2 — Deriving metadata from real state vs. hardcoding a parallel copy

> "Explain the difference between computing a piece of metadata (e.g., 'how many items are in
> this list') by *reading the real, already-built thing* versus maintaining a *second,
> separately-updated* value that's supposed to always match it. Give an example of a real bug
> class this causes — two numbers that were supposed to always agree, silently drifting apart
> after one code path is edited and the other isn't. Quiz me on which approach is safer by
> construction, not just by discipline."

*What to listen for:* deriving from the real thing is safer *by construction* — there's
structurally nothing to keep in sync, because there's only one value, read twice. A
parallel, separately-maintained copy is safer only as long as every future editor remembers
to update both places every time — which is a discipline problem, not a design guarantee,
and disciplines erode under time pressure in ways structural guarantees don't.

*Practice question:* if a function builds five things and then reports "I built five things"
by re-counting the five things it actually built, versus a function that separately tracks a
counter it increments once per thing — which one can silently become wrong if a future edit
adds a sixth thing to one code path but not the other?

### Concept 3 — Defensive normalization at a serialization boundary

> "A function is about to hand data to a serialization format (a spreadsheet cell, a JSON
> field, a database column) that has its own, narrower notion of 'nothing here' than the
> language you're writing in. Explain why a single, dedicated normalization function — one
> place that converts every one of that language's 'nothing' representations (`None`, a
> not-a-number float, a library's own null sentinel) into whatever the target format expects —
> is safer than handling each one ad hoc, inline, wherever it happens to come up. Quiz me on
> what breaks if two different call sites each write their own slightly different 'is this
> blank' check instead of sharing one."

*What to listen for:* a shared normalization function means every caller gets the exact same
definition of "blank," including edge cases the original author didn't personally anticipate
at every call site — and if that definition needs to change (a new kind of "nothing" is
discovered later), there's exactly one place to fix it. Ad hoc, inline checks scattered across
call sites can each be *individually* reasonable and still collectively disagree — one call
site treats a not-a-number float as blank, another doesn't, and nothing forces them to agree.

*Practice question:* a codebase has three different places that each write `if value is None
or value == ""`. A new kind of blank value shows up (a library's own null sentinel object)
that isn't caught by that check. How many places need to change, and how would you know you
found all of them?

### Concept 4 — Allow-lists vs. deny-lists as a safety default

> "Explain the difference between an allow-list (only explicitly known-good values are
> accepted; everything else is rejected by default) and a deny-list (only explicitly known-bad
> values are rejected; everything else is accepted by default), as a general security/safety
> pattern — not specific to any one domain. Give an example where a deny-list's 'accept
> anything I didn't think to exclude' default caused a real problem. Quiz me on which one fails
> *safer* when an input arrives that the original author never anticipated."

*What to listen for:* an allow-list fails safe — an unanticipated value is excluded by
default, meaning the failure mode is "the system silently does less than it should" (mildly
annoying, discoverable by comparing counts). A deny-list fails unsafe — an unanticipated value
is included by default, meaning the failure mode is "the system silently does something nobody
vetted" (potentially invisible, and potentially actively wrong).

*Practice question:* a system explicitly rejects `"admin"`, `"root"`, and `"system"` as
usernames, and accepts anything else. A new reserved word (`"superuser"`) is added to the
product later but nobody updates this specific check. What happens — and would an allow-list
version of the same check have the same gap?

### Concept 5 — Eager vs. lazy default-argument evaluation

> "In a language where a function's default argument value is computed exactly once — at the
> moment the function is *defined*, not each time it's *called* — explain what happens if that
> default expression reads something that changes over time (like 'the current moment'). Give
> a concrete symptom a developer would observe if this bit them in a long-running program (a
> web server that stays running for days). Quiz me on the fix, and why the sentinel value
> `None` is the conventional way to signal 'resolve this fresh, at call time' instead."

*What to listen for:* the symptom is a value that's silently *frozen* at whatever it was the
moment the module was first imported/the function was first defined — in a long-running
server process, every request would see the exact same "current time" the server happened to
start with, not the actual current time. The fix is to default the parameter to `None` and
resolve the real value inside the function body, on every call, so "call time" and
"resolution time" are the same moment.

*Practice question:* if a function is defined as `def f(x=some_expensive_computation()):`, how
many times does `some_expensive_computation()` actually run over the life of a program that
calls `f()` a thousand times?

## Architecture overview

Phases 3–5 each ended with a trusted result envelope — the full, already-computed return value
of `validate_orders()`, `allocate_inventory()`, or `calculate_payment_aging()`. Phase 6 is the
first module in this codebase that sits entirely on the *consuming* side of a contract: it
never produces a new business fact, only a new file format for facts that already exist.

```text
   OrderValidationResult        InventoryAllocationResult         PaymentAgingResult
   { summary, valid_orders,     { summary, allocation_results,    { summary, aging_rows,
     errors }                     backorders, remaining_            data_issues,
                                   inventory, supplier_               draft_messages }
                                   follow_ups }
            │                               │                               │
            └───────────────┬───────────────┴───────────────┬───────────────┘
                             ▼                                (same 4-step shape,
                  export_<workflow>_report(result, ...)        three call sites)
                             │
        1. _new_workbook() — Workbook(), remove the default "Sheet"
                             │
        2. _write_summary_sheet(...) / _write_detail_sheet(...) × N
           — wb.create_sheet(name) called in the exact order sheets must appear;
             openpyxl preserves creation order as wb.sheetnames — no separate
             "set sheet order" step exists anywhere
                             │
        3. _save_workbook_bytes(wb)
           io.BytesIO() → wb.save(buffer) → buffer.getvalue()   — never a disk path
                             │
        4. _build_manifest(..., sheet_names=wb.sheetnames, ...)
           — reads the REAL sheets just created, not a hardcoded parallel list
                             │
                             ▼
        return (workbook_bytes: bytes, manifest: ReportManifest)
```

Key invariants for this phase:

1. **`report_export.py` never performs business calculations, revalidation, allocation, or
   aging logic.** It only formats and writes already-computed envelope data — the "format,
   don't recalculate" invariant this whole tutorial is organized around (Part 1).
2. **Workbooks are built entirely in memory.** `report_export.py` never writes to disk;
   persistence is a later API-layer concern this module has no opinion about (Part 2).
3. **Sheet names and order per report are fixed by `REPORT_MANIFEST_FIXTURES`** in
   `tests/contract_fixtures.py`, and the manifest this module returns is always read from the
   real workbook it just built, never maintained as a second, independent list (Part 3).

## Part 1 — Result envelopes become workbook inputs, not raw DataFrames

Open [`src/report_export.py`](../../../src/report_export.py) lines 204–215, the start of
`export_order_validation_report`:

```python
def export_order_validation_report(
    result: OrderValidationResult,
    original_orders_df: pd.DataFrame | None = None,
    generated_at: datetime | None = None,
) -> tuple[bytes, ReportManifest]:
    """Build order_validation_report.xlsx from an already-computed OrderValidationResult."""
    effective_generated_at = generated_at or datetime.now()
    wb = _new_workbook()
    _write_summary_sheet(wb, "Summary", result["summary"])
    _write_detail_sheet(wb, "Valid Orders", result["valid_orders"], VALID_ORDER_COLUMNS)
    _write_detail_sheet(wb, "Validation Errors", result["errors"], VALIDATION_ERROR_COLUMNS)
    _write_raw_dataframe_sheet(wb, "Original Orders", original_orders_df)
```

`result` is typed as `OrderValidationResult` — the exact `TypedDict` envelope Tutorial 03 Part
1 covered, the literal dict `validate_orders()` returns. Every sheet-writing call reads a key
straight out of it (`result["valid_orders"]`, `result["errors"]`) and hands the list to a
generic writer function unchanged. Nowhere in this function, or anywhere else in
`report_export.py`, does a cell value get recomputed from anything other than what's already
sitting in that field — no re-parsing a date, no re-checking whether a SKU exists, no
re-deciding a status.

`tests/test_report_export.py:217–225` proves this trust concretely, for a genuinely different
envelope (`InventoryAllocationResult`) and a genuinely different field (`status`):

```python
def test_inventory_allocation_report_backorders_sheet_uses_precomputed_list_as_is():
    workbook_bytes, _ = export_inventory_allocation_report(
        _inventory_allocation_result(), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Backorders"]
    row = dict(zip(ALLOCATION_RESULT_COLUMNS, [c.value for c in ws[2]]))
    assert row["order_id"] == BACKORDER_ROW_FIXTURE["order_id"]
    assert row["status"] == "Backordered"
```

`BACKORDER_ROW_FIXTURE["status"]` is `"Backordered"` because Tutorial 04's
`_allocate_order_line` already decided that, comparing `allocatable_qty` against
`order["quantity"]`. `report_export.py` never touches that comparison again — it writes
whatever string is already sitting in `row["status"]`. This is the concrete shape of Track 3's
prerequisite lesson (L3.1): a presentation layer formats an already-decided result; it does
not re-decide it.

**Failure mode — report export recalculating business rules and disagreeing with the source
module:** if `_write_detail_sheet` (or a bespoke Backorders writer) instead re-derived
`status` from `allocated_qty` vs. `requested_qty` inline — say, `"Backordered" if
allocated_qty == 0 else "Fully Allocated"` — it would *usually* agree with
`inventory_allocation.py`'s own logic, right up until a future business-rule change to
`_allocate_order_line` (a new status tier, an edge case reclassified) shipped without an
identical change here. At that point the live `/dashboard` (reading the real
`InventoryAllocationResult`) and a downloaded report generated moments later (reading the
report's own stale reimplementation) would show two different answers for the same order line
— exactly the "report that quietly recomputes and disagrees with the screen" bug L3.1 names as
the reason this separation exists at all.

**Checkpoint:** `report_export.py` takes each business module's *envelope* as input, never the
raw DataFrames the original specs suggested. Walk through what would have to change in this
module, and in every caller, if a future spec change meant `payment_aging.py` needed to return
a fourth piece of information not currently in `PaymentAgingResult`.

<details>
<summary>Reveal answer</summary>

`src/contracts.py` wouldn't change at all — `PaymentAgingResult` isn't defined there (Part 4).
`payment_aging.py`'s own `PaymentAgingResult` `TypedDict` would gain the new field, and
`calculate_payment_aging()` would need to actually compute and populate it — that part is
outside this module's boundary entirely. Inside `report_export.py`, the change depends on what
kind of information it is: a new *summary* field needs zero code changes at all, since
`_write_summary_sheet` already iterates whatever keys the summary dict happens to have (Part
2); a new *list* of rows needing its own sheet would need one new `*_COLUMNS` constant plus one
new `_write_detail_sheet(...)` call inside `export_payment_aging_report`, and that new sheet
name would need to be added to the `payment_aging` entry in `REPORT_MANIFEST_FIXTURES` (Part
3), since sheet order is a tested contract, not an accident. Every *caller* of
`export_payment_aging_report` — anything holding a `(bytes, manifest)` tuple — needs no change
whatsoever, because callers never see `PaymentAgingResult`'s internal shape at all.

</details>

**Try it yourself:** Run
`uv run python -c "from src.report_export import export_inventory_allocation_report; from tests.contract_fixtures import ALLOCATION_SUMMARY_FIXTURE, ALLOCATION_RESULT_ROW_FIXTURE, BACKORDER_ROW_FIXTURE, REMAINING_INVENTORY_ROW_FIXTURE, SUPPLIER_FOLLOW_UP_ROW_FIXTURE; result = {'summary': ALLOCATION_SUMMARY_FIXTURE, 'allocation_results': [ALLOCATION_RESULT_ROW_FIXTURE], 'backorders': [BACKORDER_ROW_FIXTURE], 'remaining_inventory': [REMAINING_INVENTORY_ROW_FIXTURE], 'supplier_follow_ups': [SUPPLIER_FOLLOW_UP_ROW_FIXTURE]}; b, m = export_inventory_allocation_report(result); print(m['sheet_names'])"`
and confirm the five sheet names print in the exact order `_allocate_inventory_result`'s keys
are written, matching Part 3's manifest discussion ahead.

## Part 2 — Workbook generation in memory: `Workbook` → sheets → `BytesIO` → bytes

Open [`src/report_export.py`](../../../src/report_export.py) lines 101–104 and 198–201:

```python
def _new_workbook() -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)
    return wb
```

```python
def _save_workbook_bytes(wb: Workbook) -> bytes:
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
```

`Workbook()` ships with one default sheet already created, always named `"Sheet"` —
`wb.remove(wb.active)` deletes it immediately, before any real sheet is written. Without this
line, every workbook this module ever produced would carry a stray, empty first sheet ahead of
every real one; `wb.sheetnames == ["Summary", "Valid Orders", ...]` would instead read
`["Sheet", "Summary", "Valid Orders", ...]`, breaking every sheet-order assertion in the test
suite and every real download a user might open in Excel.

`_save_workbook_bytes` is where "in memory" actually becomes concrete: `openpyxl.Workbook.save`
accepts either a file path string or any file-like object — something with a `.write()` method
Python's I/O machinery recognizes, regardless of what class actually implements it.
`io.BytesIO()` is exactly that: an in-memory buffer that behaves like an open file without ever
touching a disk. `wb.save(buffer)` writes the whole `.xlsx` archive into that buffer, and
`buffer.getvalue()` reads the accumulated bytes back out. Nothing in this module ever imports
`os` or opens a path — Phase 6's entire output is a `bytes` object, ready to be returned from a
future API response or written to disk by *some other, later* layer that decides to.

> **Python language — Duck-typed file object:** `openpyxl` doesn't check
> `isinstance(buffer, SomeFileClass)` before calling `.write()` on it — it just calls
> `.write()` and trusts that whatever it was handed supports it. This is duck typing ("if it
> walks like a duck and quacks like a duck..."): `io.BytesIO` satisfies the file-like *protocol*
> `Workbook.save()` expects without inheriting from any specific "file" base class. The same
> pattern is why Python's `open()`-returning file objects, `io.StringIO`, and `io.BytesIO` are
> all interchangeable almost everywhere code expects "something you can `.read()`/`.write()`" —
> the contract is behavioral, not a type hierarchy.

The one sheet-writer this Part hasn't shown yet is where a second, independent
`report_export.py`-owned invariant lives — not about memory, but about genericity. Open
[`src/report_export.py`](../../../src/report_export.py) lines 149–161:

```python
def _write_summary_sheet(wb: Workbook, sheet_name: str, summary: dict) -> Worksheet:
    ws = wb.create_sheet(sheet_name)
    ws.append(["Metric", "Value"])
    for key, value in summary.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                label = f"{_label(key)}: {sub_key}"
                ws.append([label, _safe_cell_value(sub_value)])
        else:
            ws.append([_label(key), _safe_cell_value(value)])
    _style_header_row(ws, 2)
    _autosize_columns(ws, ["Metric", "Value"])
    return ws
```

`for key, value in summary.items()` iterates whatever the caller's summary dict actually
contains — there is no hardcoded list of expected metric names anywhere in this function. The
`isinstance(value, dict)` branch is what makes `PaymentAgingSummary`'s
`aging_bucket_counts` (itself a nested dict, `{"Current": 3, "1-30 Days": 5, ...}`) render as
several flattened rows instead of one unreadable cell containing a Python dict's `repr()`.
Crucially, this flattening reads the nested dict's *own* key order — it never sorts, never
reorders, never maintains any bucket-name list of its own. `plan.md`'s invariant 11 names the
concrete incident this protects against: an earlier draft of this function *did* hardcode its
own copy of the five aging-bucket names, found and fixed via `/project-review` — a second,
parallel definition of "what buckets exist" that would have silently dropped or misrendered any
future bucket `payment_aging.py` added on its own side, exactly the "duplicating
payment-aging bucket order inside `report_export.py`" failure mode this Part is named to avoid.
`tests/test_report_export.py:351–378` is the test written specifically to prove this generic
behavior, using a summary shape the real code has never produced:

```python
def test_payment_aging_report_aging_summary_follows_provided_dict_not_hardcoded_order():
    # Deliberately different keys/order/count than the old 5-key AGING_BUCKET_ORDER list
    # (Current, 1-30 Days, 31-60 Days, 61-90 Days, 90+ Days) — proves the summary writer
    # renders whatever dict it's handed, not a report_export-owned bucket list.
    custom_summary = {
        **PAYMENT_AGING_SUMMARY_FIXTURE,
        "aging_bucket_counts": {
            "91+ Days": 4,
            "Current": 1,
            "1-30 Days": 2,
            "61-90 Days": 3,
            "Zzz-Custom-Bucket": 9,
        },
    }
    workbook_bytes, _ = export_payment_aging_report(
        _payment_aging_result(summary=custom_summary), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Aging Summary"]
    rows = [(row[0].value, row[1].value) for row in ws.iter_rows(min_row=2)]
    bucket_rows = [r for r in rows if r[0].startswith("Aging Bucket Counts:")]
    assert bucket_rows == [
        ("Aging Bucket Counts: 91+ Days", 4),
        ("Aging Bucket Counts: Current", 1),
        ("Aging Bucket Counts: 1-30 Days", 2),
        ("Aging Bucket Counts: 61-90 Days", 3),
        ("Aging Bucket Counts: Zzz-Custom-Bucket", 9),
    ]
```

Five bucket names, in a deliberately scrambled, non-canonical order (`91+ Days` first, an
unrecognized `Zzz-Custom-Bucket` last) — a genuinely different shape than
`payment_aging.py`'s real `_AGING_BUCKET_ORDER`. If `_write_summary_sheet` maintained even a
partial list of its own, this test would either fail outright or silently drop
`Zzz-Custom-Bucket`. It doesn't, because there is no such list to maintain — bucket ordering
stays exclusively `payment_aging.py`'s responsibility, per Key Invariant 3 in `CLAUDE.md`'s
module-boundary rules.

**Checkpoint:** `_write_summary_sheet` is the one function in this module shared by all three
`export_*_report` functions, each passing it a structurally different summary
(`ValidationSummary`, `AllocationSummary`, `PaymentAgingSummary` — different field counts,
only `PaymentAgingSummary` has a nested dict). What would have to be true about a future fourth
summary shape for this function to need a code change to support it?

<details>
<summary>Reveal answer</summary>

Almost nothing would force a change — `_write_summary_sheet` only recognizes two shapes of
value: a plain scalar (written as one `[label, value]` row) and a `dict` (flattened one level
into `"{key}: {sub_key}"` rows). A fourth summary with any mix of new scalar fields, or even a
new nested-dict field with entirely different sub-keys, would render correctly with zero
changes, because the function was never written against a specific field list to begin with —
that's the entire point of iterating `summary.items()` rather than naming fields. It would need
a real change only if a future summary introduced a *third* level of nesting (a dict whose
values are themselves dicts) — the current `isinstance(value, dict)` branch only flattens one
level deep, so a doubly-nested value would render as a raw dict repr in a single cell, the same
unreadable outcome the one-level flattening was built to avoid.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k "aging_summary_follows_provided_dict or summary_sheet_flattens" -v`
and read both test names — confirm one proves the *canonical* five-bucket shape flattens
correctly and the other proves a deliberately non-canonical shape does too, the same "prove
both the expected case and the edge case" pattern Tutorial 03 Part 1 used for
`product_name` fill-from-master.

## Part 3 — Manifest generation from actual workbook state

Open [`src/report_export.py`](../../../src/report_export.py) lines 185–195 and 217–221:

```python
def _build_manifest(
    report_type: str, file_name: str, sheet_names: list[str], generated_at: datetime
) -> ReportManifest:
    report_id = f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"
    return {
        "report_id": report_id,
        "report_type": report_type,
        "file_name": file_name,
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "sheet_names": sheet_names,
    }
```

```python
    sheet_names = wb.sheetnames
    workbook_bytes = _save_workbook_bytes(wb)
    manifest = _build_manifest(
        "order_validation", "order_validation_report.xlsx", sheet_names, effective_generated_at
    )
```

`sheet_names = wb.sheetnames` reads the *real* workbook's actual sheet list — populated by
every `wb.create_sheet(...)` call that already ran inside `_write_summary_sheet` and
`_write_detail_sheet` — after every one of those calls has already executed, and passes it
straight into `_build_manifest`. There is no second, independently-typed-out list of sheet
names living anywhere in `export_order_validation_report`'s body that a manifest could
possibly disagree with; `manifest["sheet_names"]` and `wb.sheetnames` are, by construction, the
exact same list object handed to two different places.

`tests/test_report_export.py:70–78` is the direct proof, checking both values against a single
independent source of truth — the hand-authored `REPORT_MANIFEST_FIXTURES` from
`tests/contract_fixtures.py:164–198`, itself already asserted against in `tests/test_contracts.py`
(Tutorial 01 territory):

```python
def test_order_validation_report_sheet_names_match_manifest_fixture():
    orders_df = pd.DataFrame([{"order_id": "SO-2026-006", "sku": "OFF-CHAIR-006"}])
    workbook_bytes, manifest = export_order_validation_report(
        _order_validation_result(), orders_df, generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    expected = _sheet_names_for("order_validation")
    assert wb.sheetnames == expected
    assert manifest["sheet_names"] == expected
```

Both `wb.sheetnames` (the real, saved-and-reloaded workbook) and `manifest["sheet_names"]` are
asserted against the *same* `expected` list — proving they agree with each other and with the
project's own fixed contract, not just with each other in isolation (two values could
coincidentally agree with each other while both being wrong).

> **System design — Single source of truth, derived not duplicated:** `_build_manifest`
> receiving `wb.sheetnames` as a parameter, rather than recomputing or independently tracking
> "what sheets exist," is the general pattern of deriving metadata from the real, already-built
> artifact instead of maintaining a parallel copy of the same fact. This is the same principle
> behind, e.g., a database view computed from a table rather than a second table manually kept
> in sync, or a build tool's manifest listing files it actually wrote rather than files it
> *meant* to write — the derived version is correct by construction; the parallel-copy version
> is correct only as long as every future edit remembers to update both places.

**Checkpoint:** `_build_manifest` derives `sheet_names` from `wb.sheetnames` — the workbook's
actual sheets — rather than from a hardcoded list passed in alongside the sheet-writing calls.
What would have to go wrong in the code for this to actually drift out of sync with reality,
given that the alternative (a separate hardcoded list) could drift by a simple copy-paste
mistake?

<details>
<summary>Reveal answer</summary>

With the current design, the only way for the manifest to genuinely drift from the real
workbook is a bug in *call ordering* — `wb.sheetnames` would have to be read before every
`_write_*_sheet` call had actually finished running, which isn't a data-entry mistake, it's a
structural error in the function body itself (and every `export_*_report` function reads
`wb.sheetnames` only after every sheet-writing call, making this close to impossible today).
Contrast with the rejected alternative: a developer adding, renaming, or reordering a sheet has
to remember to update *two* separate places — the actual `wb.create_sheet(...)` call sequence,
and whatever list feeds `_build_manifest` — and nothing in Python's type system or a passing
test run enforces that two independently-written lists agree with each other just because
they're "supposed to." The current design doesn't eliminate the possibility of a bug; it
eliminates an entire *category* of bug (the two values disagreeing) by making it structurally
impossible for there to be two values in the first place.

</details>

**Try it yourself:** Run
`uv run python -c "from src.report_export import export_order_validation_report; from tests.contract_fixtures import VALIDATION_SUMMARY_FIXTURE, VALID_ORDER_ROW_FIXTURE, VALIDATION_ERROR_ROW_FIXTURE; result = {'summary': VALIDATION_SUMMARY_FIXTURE, 'valid_orders': [VALID_ORDER_ROW_FIXTURE], 'errors': [VALIDATION_ERROR_ROW_FIXTURE]}; b, m = export_order_validation_report(result); print(m)"`
and read `test_order_validation_report_manifest_shape` (`tests/test_report_export.py:81-89`)
side by side — confirm every key the test asserts (`report_id`, `report_type`, `file_name`,
`generated_at`, `sheet_names`) is present in your printed manifest with the same shape.

## Part 4 — Envelope imports: why result types live in business modules, not `contracts.py`

Open [`src/report_export.py`](../../../src/report_export.py) lines 21–24:

```python
from src.contracts import ReportManifest
from src.inventory_allocation import InventoryAllocationResult
from src.order_validation import OrderValidationResult
from src.payment_aging import PaymentAgingResult
```

Four `TypedDict` imports, from four different modules — only `ReportManifest` comes from
`contracts.py`. `explanation.md` records this as a real mistake caught during development, not
a decision that was obviously correct from the start: the first draft of this module imported
all four types from `src.contracts`, and the test suite failed at collection time with
`ImportError: cannot import name 'InventoryAllocationResult' from 'src.contracts'`, because
that type has never lived there. Tutorials 03, 04, and 05 each established this independently,
one module at a time: `contracts.py` only holds the shared, spec-defined row/summary shapes
(`ValidationSummary`, `PaymentAgingRow`, and so on) — the *envelope* type that bundles a
module's own shapes together (`OrderValidationResult`, `InventoryAllocationResult`,
`PaymentAgingResult`) is defined locally, once per business module, because it isn't a new
business-facing shape at all, just that one function's return-value packaging.

`report_export.py` is the first module in this codebase to actually *feel* that decision from
the outside — it's the one place that needs all three envelope types simultaneously, so its
import block is the first place a reader sees the "envelopes live with their modules" rule
written out three times in a row rather than once in isolation. The fix, per `explanation.md`,
was a three-line import split matching exactly what's shown above: one line for the shared
`ReportManifest`, one per business module for its own envelope.

**Checkpoint:** The `ImportError` happened because envelope types live in each business
module, not in `contracts.py`. If a fourth business module were added to this project later,
how would you decide whether its envelope type belongs in that new module or should finally
get promoted into `contracts.py`?

<details>
<summary>Reveal answer</summary>

The same tell Tutorial 03 Part 1 named applies here, sharpened by what this specific module
reveals: the envelope stays local as long as it's purely a bundle of that module's own
already-defined `contracts.py` shapes, with nothing new of its own — true of all three
envelopes today, each with a genuinely different field count and no field overlap. It would be
worth promoting into `contracts.py` only if either (a) the fourth envelope turned out to be
*structurally identical* to one of the existing three (unlikely, given how different
`OrderValidationResult`'s two-list shape is from `PaymentAgingResult`'s three-list-plus-nested
one), or (b) `report_export.py` itself — the one module that already imports every envelope
type at once — started needing to treat envelopes *polymorphically* (e.g., a single generic
loop that writes a Summary sheet from any `result["summary"]` regardless of which module
produced it, rather than one hand-written `export_<x>_report` function per module). That second
condition is the one actually worth watching for in this specific module: it's the first place
in the codebase where cross-envelope duplication, if it ever emerged, would show up first —
and today it hasn't (each `export_*_report` function stays fully explicit about its own
envelope's fields).

</details>

**Try it yourself:** Run
`uv run python -c "from src.contracts import OrderValidationResult" 2>&1 | tail -1`
and confirm it raises the same `ImportError` `explanation.md` describes — then run
`uv run python -c "from src.order_validation import OrderValidationResult; print('ok')"`
and confirm the correct import path succeeds.

## Part 5 — Explicit sheet/header constants instead of deriving from row data

Open [`src/report_export.py`](../../../src/report_export.py) lines 31–44 and 128–135:

```python
VALIDATION_ERROR_COLUMNS = ["row_number", "order_id", "sku", "error_code", "error_message", "severity"]
VALID_ORDER_COLUMNS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_region",
    "sku",
    "product_name",
    "quantity",
    "requested_delivery_date",
    "priority",
    "payment_terms",
    "sales_owner",
]
```

```python
def _write_detail_sheet(wb: Workbook, sheet_name: str, rows: list[dict], columns: list[str]) -> Worksheet:
    ws = wb.create_sheet(sheet_name)
    ws.append(columns)
    for row in rows:
        ws.append([_safe_cell_value(row.get(col, "")) for col in columns])
    _style_header_row(ws, len(columns))
    _autosize_columns(ws, columns)
    return ws
```

An early, less-defensive instinct for `_write_detail_sheet` would derive the header row from
whatever the first row's keys happen to be — `list(rows[0].keys())` — less code, and for a
non-empty list of uniform rows, identical output to an explicit constant. `explanation.md`
names two real scenarios the test suite deliberately exercises that rule this out.

First, an empty list has no "first row" to derive keys from at all.
`tests/test_report_export.py:116–123` is the proof:

```python
def test_order_validation_report_empty_errors_sheet_has_header_only():
    workbook_bytes, _ = export_order_validation_report(
        _order_validation_result(errors=[]), pd.DataFrame(), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Validation Errors"]
    assert ws.max_row == 1
    assert _headers(ws) == VALIDATION_ERROR_COLUMNS
```

A validation run that found zero errors still produces a `Validation Errors` sheet with a real,
correctly-labeled header row and zero data rows — `ws.max_row == 1` means exactly one row
exists, and it's the header. Deriving from `rows[0]` has no row to read here; the explicit
`VALIDATION_ERROR_COLUMNS` constant needs no special case for this — it's a plain Python list
that exists whether or not `rows` is empty.

Second, `NotRequired` fields (Tutorial 01 Part 5, Tutorial 03 Part 1) mean two rows of the
*same* `TypedDict` type can legitimately have different keys present.
`tests/test_report_export.py:155–170` constructs a `ValidationErrorRow` missing both
`NotRequired` fields entirely — not blank, *absent*:

```python
def test_order_validation_report_missing_notrequired_field_renders_blank():
    error_without_sku = {
        "row_number": 3,
        "error_code": "OV-001",
        "error_message": "Customer name is missing",
        "severity": "Error",
    }
    workbook_bytes, _ = export_order_validation_report(
        _order_validation_result(errors=[error_without_sku]), pd.DataFrame(), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Validation Errors"]
    row = dict(zip(VALIDATION_ERROR_COLUMNS, [c.value for c in ws[2]]))
    # openpyxl round-trips a written "" as a genuinely blank cell -> None on reload.
    assert row["sku"] is None
    assert row["order_id"] is None
```

If a report ever had one row with `sku` present and another without it, and headers were
derived from "whichever row happens to be at index 0," the rendered column *set* would depend
on data ordering — not a property a report a human reads and files away should have. The
chosen solution — `row.get(col, "")` for every column in the constant, on every row — makes
the header row a property of the *contract*, not of whatever data happens to be present;
`error_without_sku` simply gets `""` (cleaned to a blank cell by `_safe_cell_value`, Part 6)
for the two keys it never had, in the exact same column position every other row uses.

**Checkpoint:** `_write_detail_sheet` uses `row.get(col, "")` against an explicit column list.
What happens — concretely, cell by cell — if a `TypedDict` row is passed with a key that isn't
in the corresponding column constant at all (e.g., a typo'd field name)? Is that failure mode
acceptable, or would you want it to raise instead?

<details>
<summary>Reveal answer</summary>

Nothing happens — silently. `_write_detail_sheet` only ever iterates `columns` (the explicit
constant), never `row.keys()`, so a key present in the row dict but absent from the constant is
simply never read, never written to any cell, and leaves no trace anywhere in the output
workbook. If a future edit to a business module renamed a field (say, `error_message` →
`message_text` inside `ValidationErrorRow`) without updating `VALIDATION_ERROR_COLUMNS` to
match, every row would silently render a blank `error_message` column (falling through to the
`.get(col, "")` default) while the real message data sat unread under the new key. Whether
that's acceptable is a real trade-off: it fails *safe* in the sense that nothing crashes and no
wrong data appears — but it also fails *silently*, with no test or runtime signal pointing at
the mismatch unless a test specifically asserts that field's value (as
`test_order_validation_report_representative_row_values`, `tests/test_report_export.py:101-114`,
does for a few key fields, though not exhaustively for every column). A stricter version could
assert `set(row.keys()) <= set(columns)` and raise on an unrecognized key — nothing in this
codebase does that today, which is a real, named gap rather than a considered decision to leave
it unguarded.

</details>

**Checkpoint:** The explicit-constants approach ties every sheet's headers to `contracts.py`'s
`TypedDict` field-declaration order for `VALID_ORDER_COLUMNS`, `VALIDATION_ERROR_COLUMNS`, and
so on. If a field's order in a `TypedDict` definition were changed (with no other code change),
would you expect that to be a breaking change for `report_export.py`, a silent behavior change,
or a no-op?

<details>
<summary>Reveal answer</summary>

A no-op. `VALID_ORDER_COLUMNS` and its siblings are separately declared, literal Python lists
inside `report_export.py` — they happen to match each `TypedDict`'s field order today because
that's how they were written, but nothing in this module reads a `TypedDict`'s
`__annotations__` (or any other runtime reflection of field-declaration order) to build them.
Reordering fields in a `TypedDict`'s class body in `contracts.py` changes nothing about how
`row.get(col, "")` reads a dict — dictionary key lookup by name doesn't care what order a class
body declared its type annotations in. The *only* way a reorder would actually change this
module's output is if a human also, separately, chose to reorder `VALID_ORDER_COLUMNS` itself
to match — at which point it's a deliberate presentation decision (Excel column order), not a
side effect of the contract change.

</details>

**Checkpoint:** `BackorderRow(AllocationResultRow)` is a subclass with no new fields —
`Backorders` and `Allocation Results` share the same `ALLOCATION_RESULT_COLUMNS` constant
(both `_write_detail_sheet` calls in `export_inventory_allocation_report` pass it). If
`BackorderRow` ever gained a field `AllocationResultRow` doesn't have (say, a
backorder-specific ETA), what would need to change, and where would that decision need to be
made first — in `contracts.py`, in `inventory_allocation.py`, or in `report_export.py`?

<details>
<summary>Reveal answer</summary>

`contracts.py` first — `BackorderRow`'s `TypedDict` definition would need the new field added,
which is itself a Field Scope Boundary decision requiring the originating spec to actually
define what an "ETA" means for a backorder line, not something to add casually. Then
`inventory_allocation.py` — wherever backorder rows are actually built would need to compute
and populate the new field, since data has to come from somewhere real; `report_export.py`
cannot invent it. Only then would `report_export.py` change, and the change would be real: a
new `BACKORDER_COLUMNS` constant, separate from `ALLOCATION_RESULT_COLUMNS`, would replace the
shared constant currently used for the `Backorders` sheet — because `Allocation Results` rows
(plain `AllocationResultRow`, not the `BackorderRow` subtype) wouldn't have the new field, and
`ALLOCATION_RESULT_COLUMNS` is shared by both sheets today specifically because both currently
have identical fields. Making the `report_export.py` change *first* — adding an ETA column to
`ALLOCATION_RESULT_COLUMNS` before the data exists anywhere — would be exactly the mistake
Part 1's failure mode warns about in miniature: a presentation-layer field with nothing real
behind it.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k "empty_errors_sheet or missing_notrequired_field" -v`
and read both test names and bodies — confirm one tests the *zero-rows* edge case and the other
tests the *inconsistent-keys-across-rows* edge case, the two scenarios this Part names as
exactly what `rows[0].keys()` would have gotten wrong.

## Part 6 — `_safe_cell_value` and the `openpyxl` empty-string/`None` round trip

Open [`src/report_export.py`](../../../src/report_export.py) lines 87–98:

```python
def _safe_cell_value(value: Any) -> Any:
    """Normalize None/NaN/NaT/pd.NA to an empty string for a clean Excel cell."""
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return value
```

Three checks, each catching a different runtime shape of "nothing here." `value is None`
catches Python's own null — the shape a `NotRequired` field's `.get(col, "")` default, or an
explicit `None` value, produces. `isinstance(value, float) and math.isnan(value)` catches a
genuine `float('nan')` — the shape a pandas `DataFrame` produces when a mixed-type numeric
column gets upcast (Part 7). The `pd.isna(value)` fallback, wrapped in `try/except` because it
raises on some non-scalar inputs, catches `pd.NaT` and `pd.NA` similarly. Without this
function, any of these three "nothing" representations reaching `ws.append()` directly would
either write the literal text `"None"` into a cell a human reads, or write a raw NaN float that
risks Excel flagging the workbook as containing invalid numeric content — the "writing raw
`NaN`, `NaT`, `pd.NA`, or `None` into cells" failure mode this Part exists to prevent.

> **Design patterns — Boundary-normalizing adapter:** `_safe_cell_value` is a single, shared
> function every cell value passes through before reaching `openpyxl`, absorbing every
> different in-Python representation of "nothing" into one consistent output. This is the
> general shape of an adapter at a serialization boundary: the code on one side (this project's
> business modules and pandas) can keep using whatever "nothing" representation is natural for
> it, and the code on the other side (an Excel cell) only ever has to handle one. The
> alternative — every call site independently checking `if value is None or (isinstance(value,
> float) and math.isnan(value))` — risks exactly the drift Concept 3's pre-study names: two call
> sites, two slightly different definitions of "blank," agreeing today by coincidence and
> silently disagreeing the moment one of them is edited without the other.

Now the part of this function's story that looks like a bug but isn't. `explanation.md`
records that the first draft of the tests asserted `_safe_cell_value`'s behavior literally:
write `None`, expect to read back `""`. Three tests failed with an unexpected diff —
`None != ''` — even though `_safe_cell_value` was working exactly as designed. A four-line
reproduction (write `''` to a cell, save to `BytesIO`, reload with `load_workbook`, print the
value) confirmed the mechanism: `openpyxl` does not preserve a written empty string as a
distinct value through a save/reload round trip. An empty-string cell has no meaningful XML
representation in the `.xlsx` format distinct from "no value here," so on reload it comes back
as a genuinely blank cell — `None`, not `""`. Every test written after this discovery expects
`None` post-round-trip, with a one-line comment (visible in both excerpts above from Part 5)
explaining why, so a future reader doesn't mistake the `None` for evidence the cleaning didn't
happen.

**Failure mode — trusting in-memory workbook values without save/load round-trip
verification:** if this project's tests inspected the in-memory `Workbook` object directly
(reading `ws.cell(row=2, column=3).value` right after `_write_detail_sheet` runs, before any
`save()`/`load_workbook()` round trip), every one of them would see the literal string `""`
`_safe_cell_value` actually wrote — passing cleanly, and proving nothing at all about what a
real user opening the downloaded `.xlsx` file in Excel would actually see. Every test in
`tests/test_report_export.py` goes through `_load()` (`load_workbook(io.BytesIO(workbook_bytes))`,
lines 49–50) specifically because the in-memory object and the saved-and-reloaded file are
observably different artifacts for this exact reason.

**Checkpoint:** `_safe_cell_value` writes `""` for missing values, but reading a
saved-and-reloaded workbook shows `None` instead. If a future test asserted `cell.value == ""`
against an in-memory `Workbook` object that was never saved and reloaded, would that test still
be trustworthy? What's actually different between inspecting an unsaved `Workbook` and one that
went through `save()` → `load_workbook()`?

<details>
<summary>Reveal answer</summary>

Not trustworthy, even though it would pass. An in-memory, never-saved `Workbook` object still
holds exactly what Python assigned to each cell — the literal `""` `_safe_cell_value` returned
— because nothing has yet forced that value through `.xlsx`'s actual on-disk (or in-buffer)
representation. `save()` is where the empty string genuinely disappears: `openpyxl` serializes
the workbook into the real `.xlsx` XML structure, which has no distinct encoding for "an empty
string" separate from "an absent cell," so the information is lost at serialization time, not
at read time. `load_workbook()` then reads that same structure back and correctly reports
`None`, because that's what's actually stored. A test against the unsaved object is testing
"did Python assign the value I expected" — true but uninteresting; a test against the
saved-and-reloaded object is testing "what will a real person opening this file in Excel
actually see," which is the only version of the question this module's tests should care about.

</details>

**Checkpoint:** The bug (or non-bug) was found by writing a four-line reproduction script
isolated from the rest of the test suite, rather than by staring at the failing assertion diff.
What made this the right next step here, versus just adjusting the assertion and moving on
without confirming *why* it needed adjusting?

<details>
<summary>Reveal answer</summary>

A failing assertion diff (`None != ''`) only tells you *that* two values disagree, not *which
one is wrong* — adjusting the assertion to match whatever the test actually observed would have
"fixed" the failure while leaving open whether `_safe_cell_value` had a real defect (e.g.,
somehow writing `None` back out instead of `""`) or whether the disagreement was expected
`openpyxl` behavior nobody had accounted for yet. The four-line reproduction isolated exactly
one variable — does a written `""` survive a save/reload round trip at all, independent of this
project's own code — and answered a factual question about a third-party library's behavior
that no amount of staring at this module's own source could have settled. Only after confirming
the *cause* (a genuine `openpyxl`/`.xlsx` format limitation, not a bug in `_safe_cell_value`)
was it safe to update the test's expected value with confidence, rather than blindly matching
whatever the code happened to currently produce.

</details>

**Checkpoint:** `_safe_cell_value`'s own test coverage, and the `_write_raw_dataframe_sheet`
path (Part 7), both rely on constructing a deliberately awkward input to prove a cleanup branch
actually fires. What other places in this codebase might have a similar "the test needs to
inject a deliberately awkward value to prove the cleanup logic actually cleans" pattern worth
noticing?

<details>
<summary>Reveal answer</summary>

Two direct matches. First, `_safe_cell_value` itself has two structurally different
"nothing"-catching branches (`isinstance(value, float) and math.isnan(value)` vs. the
`pd.isna(value)` fallback) — a test asserting the NaN branch actually fires needs to construct a
genuine `float('nan')`, not just `None`, since `None` alone would only ever exercise the first
branch and never prove the second one works. Second, and named directly in `explanation.md` #4:
`test_order_validation_report_original_orders_mirrors_input_dataframe`
(`tests/test_report_export.py:126-141`) deliberately constructs a DataFrame with one row's
`quantity` as `15` and another's as `None` in the *same* column — this is what actually forces
pandas to upcast that column to `float64`, turning `15` into `15.0` and `None` into
`float('nan')`, the exact runtime representation a real uploaded spreadsheet with one blank
quantity cell would produce. A test using an all-`None` or all-numeric column would never
exercise this specific type-upcasting behavior at all, only the cleaner, easier case.

</details>

**Try it yourself:** Run this four-line reproduction yourself —
`uv run python -c "import io; from openpyxl import Workbook, load_workbook; wb = Workbook(); wb.active['A1'] = ''; buf = io.BytesIO(); wb.save(buf); print(load_workbook(buf).active['A1'].value)"`
— and confirm it prints `None`, not `''`, exactly the round-trip behavior this Part's whole
discovery depends on.

## Part 7 — Raw DataFrame sheet handling for `Original Orders`

Open [`src/report_export.py`](../../../src/report_export.py) lines 168–182 and 204–215:

```python
def _write_raw_dataframe_sheet(wb: Workbook, sheet_name: str, df: pd.DataFrame | None) -> Worksheet:
    ws = wb.create_sheet(sheet_name)
    if df is None or df.empty:
        columns = list(df.columns) if df is not None else []
        if columns:
            ws.append(columns)
            _style_header_row(ws, len(columns))
        return ws
    columns = list(df.columns)
    ws.append(columns)
    for _, row in df.iterrows():
        ws.append([_safe_cell_value(value) for value in row.tolist()])
    _style_header_row(ws, len(columns))
    _autosize_columns(ws, [str(c) for c in columns])
    return ws
```

`Original Orders` is the one sheet in this whole module whose data doesn't come from any
envelope at all. `OrderValidationResult` — Tutorial 03's `validate_orders()` return value —
contains exactly `summary`, `valid_orders`, and `errors`; nothing in Phase 3's scope called for
retaining the raw, as-uploaded rows. But the *report's* `Original Orders` sheet (fixed as the
fourth sheet in `REPORT_MANIFEST_FIXTURES`'s `order_validation` entry) comes from a different
part of the same spec — the Downloadable Output section, written with the report in mind, not
the validation function. `export_order_validation_report` resolves this with a second,
independent parameter — `original_orders_df: pd.DataFrame | None = None` — entirely separate
from `result`, which keeps `OrderValidationResult`'s own contract untouched: no `raw_orders`
field was ever added to it.

`_write_raw_dataframe_sheet` handles a raw `DataFrame`, not a list of `TypedDict` rows, so its
column list comes from `df.columns` (whatever the uploaded file's own header row happened to
be) rather than one of Part 5's fixed constants — the one sheet in this module where the
"never derive headers from data" rule doesn't apply, because there's no contract-defined shape
to derive headers *from*; the original spreadsheet's own columns are the entire point of this
sheet.

The sheet is **always created**, whether or not `original_orders_df` is provided.
`tests/test_report_export.py:144–152` proves the `None` case renders a valid, header-only sheet
rather than a workbook missing that sheet entirely:

```python
def test_order_validation_report_original_orders_empty_when_none():
    workbook_bytes, manifest = export_order_validation_report(
        _order_validation_result(), None, generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    assert "Original Orders" in wb.sheetnames
    ws = wb["Original Orders"]
    assert ws.max_row == 1
    assert manifest["sheet_names"] == _sheet_names_for("order_validation")
```

`assert "Original Orders" in wb.sheetnames` and the final `manifest["sheet_names"]` assertion
together prove the sheet count never depends on whether a caller happened to supply a real
DataFrame — several structural tests in this file pass `None` or `pd.DataFrame()` specifically
because they're testing the *other* three sheets and don't need real orders data, and none of
them accidentally shrink the workbook's sheet count by doing so.

**Failure mode — conditionally omitting `Original Orders`:** if `export_order_validation_report`
instead only called `_write_raw_dataframe_sheet` when `original_orders_df is not None`, the
workbook's sheet *count* would depend on an implementation detail of whichever caller happened
to invoke this function — a caller that legitimately has no original-orders data (say, a future
route that regenerates a report from a persisted result without the source file) would produce
a workbook with three sheets instead of four, silently breaking the `REPORT_MANIFEST_FIXTURES`
contract this module's own tests already lock down, and handing a user a file that doesn't
match what the manifest — or any other report of the same type — promises to contain.

**Checkpoint:** Every other sheet in this module derives its column headers from a fixed,
contract-tied constant (`VALID_ORDER_COLUMNS`, etc.), per Part 5's rule. `Original Orders`
derives its headers from `df.columns` instead — whatever the uploaded file's own header row
happened to contain. Does this sheet violate Part 5's "never derive headers from data" rule, or
is it a genuinely different situation the rule was never meant to cover?

<details>
<summary>Reveal answer</summary>

A genuinely different situation, not a violation. Part 5's rule protects against headers that
should be *contract-defined* (a `TypedDict`'s known, fixed field set) accidentally being
derived from whatever data happens to be present instead — the failure mode is a report's
column *set* silently varying based on data, when the contract says it shouldn't. `Original
Orders` has no such contract to violate: its entire purpose is to preserve the *original*,
as-uploaded spreadsheet, whose column set is unknown at the time this module is written and
*supposed* to vary — a different customer's orders file with a different set of extra columns
should produce a different `Original Orders` header row, because that's what "original" means.
Deriving from `df.columns` here is the correct behavior for a fundamentally different kind of
sheet (a raw mirror) than the other four (contract-shaped detail sheets).

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k original_orders -v` and read all three
`Original Orders`-related test names — confirm one passes a real, populated DataFrame, one
passes `None`, and note which of the two asserts something about `manifest["sheet_names"]`
specifically (tying this Part's discussion back to Part 3's).

## Part 8 — `Follow-up List` as the one derived presentation sheet, using an allow-list

Open [`src/report_export.py`](../../../src/report_export.py) lines 84 and 246–260:

```python
FOLLOW_UP_PRIORITIES = {"High", "Medium", "Low", "Watch"}
```

```python
def export_payment_aging_report(
    result: PaymentAgingResult,
    generated_at: datetime | None = None,
) -> tuple[bytes, ReportManifest]:
    """Build payment_aging_report.xlsx from an already-computed PaymentAgingResult."""
    effective_generated_at = generated_at or datetime.now()
    follow_up_rows = [
        row for row in result["aging_rows"] if row["follow_up_priority"] in FOLLOW_UP_PRIORITIES
    ]

    wb = _new_workbook()
    _write_summary_sheet(wb, "Aging Summary", result["summary"])
    _write_detail_sheet(wb, "Follow-up List", follow_up_rows, PAYMENT_AGING_ROW_COLUMNS)
    _write_detail_sheet(wb, "All Invoices with Aging", result["aging_rows"], PAYMENT_AGING_ROW_COLUMNS)
```

Every sheet this module writes, in every report, is a direct pass-through of a list already
sitting in an envelope — `Backorders` writes `result["backorders"]` as-is, because
`inventory_allocation.py` already filtered it (Part 1). `Follow-up List` is the single
exception: `PaymentAgingResult` has no precomputed field matching it, so
`export_payment_aging_report` builds the filtered list itself, right here, by filtering
`result["aging_rows"]`.

The filter — `row["follow_up_priority"] in FOLLOW_UP_PRIORITIES` — is deliberately an
allow-list, not the equivalent-*today* exclusion `row["follow_up_priority"] != "None"`. For
every row `payment_aging.py` actually produces, which only ever emits one of exactly five known
priority strings (Tutorial 05 Part 5–6), the two versions produce identical output.
`tests/test_report_export.py:281–299` proves this for all four included tiers plus the
excluded `"None"` tier in one pass:

```python
def test_payment_aging_report_follow_up_list_includes_watch_high_medium_low():
    aging_rows = [
        {**PAYMENT_AGING_ROW_FIXTURE, "invoice_id": "INV-WATCH", "follow_up_priority": "Watch"},
        {**PAYMENT_AGING_ROW_FIXTURE, "invoice_id": "INV-HIGH", "follow_up_priority": "High"},
        {**PAYMENT_AGING_ROW_FIXTURE, "invoice_id": "INV-MEDIUM", "follow_up_priority": "Medium"},
        {**PAYMENT_AGING_ROW_FIXTURE, "invoice_id": "INV-LOW", "follow_up_priority": "Low"},
        {**PAYMENT_AGING_ROW_FIXTURE, "invoice_id": "INV-NONE", "follow_up_priority": "None"},
    ]
    workbook_bytes, _ = export_payment_aging_report(
        _payment_aging_result(aging_rows=aging_rows), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Follow-up List"]
    invoice_ids = [row[0].value for row in ws.iter_rows(min_row=2)]
    assert invoice_ids == ["INV-WATCH", "INV-HIGH", "INV-MEDIUM", "INV-LOW"]

    all_invoices_ws = wb["All Invoices with Aging"]
    all_invoice_ids = [row[0].value for row in all_invoices_ws.iter_rows(min_row=2)]
    assert all_invoice_ids == ["INV-WATCH", "INV-HIGH", "INV-MEDIUM", "INV-LOW", "INV-NONE"]
```

`INV-NONE` is present in `All Invoices with Aging` (every row, unfiltered — Tutorial 05 Part 4's
"Paid invoices stay visible" invariant reappears here at the report layer) but absent from
`Follow-up List`. The reason for the *stricter* allow-list version, rather than the
equivalent-today exclusion, is exactly what
`test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string`
(`tests/test_report_export.py:302–309`) exists to prove:

```python
def test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string():
    aging_rows = [{**PAYMENT_AGING_ROW_FIXTURE, "follow_up_priority": "Unexpected"}]
    workbook_bytes, _ = export_payment_aging_report(
        _payment_aging_result(aging_rows=aging_rows), generated_at=GENERATED_AT
    )
    wb = _load(workbook_bytes)
    ws = wb["Follow-up List"]
    assert ws.max_row == 1
```

A row with a priority string `payment_aging.py` never actually produces does *not* appear in
`Follow-up List`. This is presentation-layer defense-in-depth over a module `report_export.py`
deliberately never revalidates (Part 1): if `payment_aging.py` ever changed in a way that
produced an unanticipated priority string, an allow-list means that row silently doesn't show
up in the "needs attention" sheet — the safer direction, since a human might miss a row, but no
wrong-looking row ever appears there. The rejected exclusion version (`!= "None"`) would
silently *include* it instead — the less safe direction, since a report a sales rep acts on
*now contains* an entry with a priority value the code never anticipated or vetted.

> **Data structures — Set membership as an allow-list:** `FOLLOW_UP_PRIORITIES` is a Python
> `set`, and `in` against a set is an average O(1) membership check — the same data structure
> Tutorial 03 Part 1 used for `invalid_row_numbers`, here applied to implement a *safety*
> pattern rather than a deduplication one. The choice of `set` over, say, a `list` isn't about
> performance at this scale (four strings); it's the idiomatic Python container for "does this
> value belong to this fixed collection of known-good values," which is exactly what an
> allow-list *is* — a named set of acceptable members.

**Checkpoint:** The allow-list and the equivalent exclusion (`!= "None"`) produce identical
output for every row `payment_aging.py` currently emits. Is it worth adding a code comment
explaining *why* the stricter version was chosen, given nothing currently exercises the
difference in production — or does the dedicated test
(`test_payment_aging_report_follow_up_list_excludes_unexpected_priority_string`) already serve
that documentation purpose on its own?

<details>
<summary>Reveal answer</summary>

The test already carries the reasoning as an *executable*, permanently-verified explanation — a
comment can rot silently, since nothing forces it to stay accurate as the code around it
changes, while this test fails loudly the moment the allow-list behavior regresses (e.g., if a
future edit "simplified" the filter back to `!= "None"`). That said, a short comment at the
`FOLLOW_UP_PRIORITIES` declaration is still worth having alongside the test, for a different
reader: someone skimming `report_export.py` itself, not running the test suite, benefits from
the one-line "why" without having to go find and read the dedicated test first. The two aren't
redundant — the test is the proof; the comment is the pointer to *why the test exists at all*
for a reader who hasn't gone looking for it yet.

</details>

**Checkpoint:** `report_export.py`'s stated design principle is "trust the envelope, don't
revalidate" (Part 1). Does the allow-list choice violate that principle in spirit, or is
filtering-with-a-safe-default a different category of thing from revalidation?

<details>
<summary>Reveal answer</summary>

A different category. Revalidation would mean `report_export.py` re-deciding *whether* a row's
priority is correct — recomputing `follow_up_priority` from `outstanding_amount` and
`days_overdue` the way `payment_aging.py`'s own `_follow_up_priority` does (Tutorial 05 Part
6). The allow-list does none of that: it never touches or second-guesses the *value* of
`follow_up_priority` on any row. Every row — Watch, Unexpected, whatever — still appears
completely unmodified in `All Invoices with Aging`; only *membership in a derived, filtered
view* is being decided, never the value itself. The distinction is "not revalidating the field"
(true — `report_export.py` never recomputes it) versus "displaying every field's value
identically on every sheet with no judgment about which sheet it belongs on" (false — deciding
which rows belong on a "needs attention" view is exactly the kind of presentation decision a
presentation layer exists to make, the same way a UI table filter or search box doesn't
"revalidate" the underlying data it's filtering).

</details>

**Checkpoint:** If `payment_aging.py` legitimately added a sixth priority tier in a future
phase, the allow-list version would silently exclude every row with that tier from
`Follow-up List` until someone updated `FOLLOW_UP_PRIORITIES` — with no error, no warning, just
quietly missing rows. Is silent omission an acceptable failure mode here, or should there be
some signal (a test, a runtime check) that fires when a priority string not in the allow-list
appears?

<details>
<summary>Reveal answer</summary>

Acceptable *for now*, on the same "fails safer" reasoning that motivated choosing the allow-list
in the first place — a human reviewer cross-checking "All Invoices with Aging" against
"Follow-up List" row counts would eventually notice a discrepancy, and the two sheets can never
show a *wrong-looking* row together, only a *missing* one. But it stops being acceptable as a
permanent design the moment `payment_aging.py`'s priority vocabulary is expected to change on a
release cadence independent of `report_export.py`'s own — at that point, a dedicated test
asserting that every row payment aging actually produces has a `follow_up_priority` drawn from a
known, shared vocabulary (living in `payment_aging.py`, not duplicated here) would convert "a
human eventually notices a soft data drift" into "the test suite fails immediately the moment
the two modules' vocabularies diverge" — strictly better than relying on silent omission plus
someone's peripheral vigilance.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k follow_up_list -v` and read both `Follow-up List`
test names — confirm one proves the *inclusion* side (four real priority tiers, one excluded)
and the other proves the *exclusion-of-the-unanticipated* side, the two halves of an allow-list
claim that a single test could never fully prove alone.

## Part 9 — Deterministic timestamps, report IDs, and no hidden global state

Open [`src/report_export.py`](../../../src/report_export.py) lines 185–195 again, alongside
line 210:

```python
    report_id = f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"
```

```python
    effective_generated_at = generated_at or datetime.now()
```

`report_id` is a pure function of two inputs the call already has — `report_type` and
`generated_at` — with no module-level counter, no database lookup, nothing that persists
between calls. `tests/contract_fixtures.py`'s hand-authored `REPORT_MANIFEST_FIXTURES` end
their `report_id` values in `-001` (e.g. `"rpt-order_validation-20260709091500"` is followed
conceptually by what *reads* like a sequential index) — but nothing in this project has a
report registry to count against, and building one (even a simple in-memory dict mapping
`report_type` to a running count) would be exactly the "hidden global state"
`context/code-standards.md` prohibits, plus it would make report generation order-dependent in
a way tests would have to carefully control (Tutorial 03's "why error ordering is a tested
contract, not an accident" reasoning, applied here to a whole module's worth of call ordering
instead of one list's sort key). A timestamp-based ID sidesteps this entirely — two calls in
the same second for the same report type would collide, an acceptable, named risk for a
portfolio demo with no concurrent-request scenario.

`effective_generated_at = generated_at or datetime.now()` follows the exact `None`-sentinel
pattern Tutorial 05 Part 3 established for `as_of_date`: a default argument value is evaluated
exactly once, at `def` time — `def f(generated_at: datetime = datetime.now()):` would freeze
`generated_at` to whatever moment the interpreter first imported this module, silently stale
for the rest of a long-running process. Resolving it inside the function body, on every call,
means "call time" and "resolution time" are always the same moment. This pattern now appears a
third time in this codebase (`generate_invoices`'s `reference_date`, Tutorial 02; `as_of_date`,
Tutorial 05; `generated_at`, here) — and appears three separate times *within this one module*,
once per `export_*_report` function, each with its own local `effective_generated_at` variable.

The one addition beyond the `as_of_date` precedent: `generated_at.isoformat(timespec="seconds")`,
not a bare `.isoformat()`. Without `timespec="seconds"`, the ISO string would include
microseconds. `tests/test_report_export.py:42` deliberately constructs
`GENERATED_AT = datetime(2026, 7, 9, 9, 15, 0, 123456)` — a nonzero microsecond component — and
`test_payment_aging_report_report_id_format` (`tests/test_report_export.py:396–399`) proves the
truncation actually happens, not merely that the test picked a round number that happened to
have no microseconds to lose:

```python
def test_payment_aging_report_report_id_format():
    workbook_bytes, manifest = export_payment_aging_report(_payment_aging_result(), generated_at=GENERATED_AT)
    assert manifest["report_id"] == "rpt-payment_aging-20260709091500"
    assert manifest["generated_at"] == "2026-07-09T09:15:00"
```

`GENERATED_AT` has `123456` microseconds; `manifest["generated_at"]` reads exactly
`"2026-07-09T09:15:00"`, with nothing after the seconds. `report_id`'s own
`%Y%m%d%H%M%S` format string independently drops microseconds too (`strftime` simply never
includes them unless `%f` is explicitly requested), so both fields agree on "seconds is the
finest precision this project's reports need," proven with an input specifically chosen to
distinguish "the code truncates" from "there was nothing to truncate."

**Failure mode — adding a global report counter and introducing hidden state:** if a future
edit "improved" `report_id` uniqueness with a module-level `_report_counter = 0` incremented on
every call, two problems would appear at once. First, it's exactly the hidden global state
`context/code-standards.md` prohibits — the "no hidden global state" rule Tutorial 03's
pre-study connected to deterministic, side-effect-free functions now has a concrete, specific
violation to point at. Second, it would make `report_export.py`'s output order-dependent in a
way nothing about this module's *design* otherwise is: two identical calls to
`export_order_validation_report`, run in a different order relative to other report-generation
calls elsewhere in the process, would now produce different `report_id` values — a test
asserting an exact `report_id` (as `test_payment_aging_report_report_id_format` does above)
would become fragile to test *execution order*, not just to its own inputs.

**Checkpoint:** `report_id`'s timestamp-based scheme can collide if the same report type is
generated twice within the same second. Given this project has no concurrent-request scenario
yet, is that an acceptable risk to leave unaddressed, or would you fix it now? If you'd fix it,
what's the simplest change that doesn't reintroduce the hidden-state problem a counter would
bring back?

<details>
<summary>Reveal answer</summary>

Acceptable to leave unaddressed today — per `explanation.md`, this project's actual call
pattern (a synchronous FastAPI request calling one export function once) has no scenario where
two reports of the same type are genuinely generated within the same wall-clock second by the
same process. If it needed fixing without reintroducing a counter, the simplest change would be
appending a short random suffix generated fresh at call time (e.g., `uuid4().hex[:6]`) — this
preserves "no state persists between calls" exactly, because a random value needs no memory of
any previous call's output, unlike a counter, which requires remembering how many reports of
this type have already been generated somewhere that survives across calls.

</details>

**Checkpoint:** `generated_at`'s injectable-parameter pattern (`datetime | None = None`,
resolved inside the function body) now exactly mirrors `payment_aging.py`'s `as_of_date` and
`sample_data.py`'s `reference_date`. Now that this pattern has been used three times, is it
worth extracting into a shared helper (e.g., a small `resolve_now(explicit: T | None, factory:
Callable[[], T]) -> T` utility), or does the one-line inline resolution (`x or
default_factory()`) not carry enough duplication to justify the abstraction?

<details>
<summary>Reveal answer</summary>

Not yet worth it. The duplication is genuinely tiny — one line, `x or default_factory()` — and
even within this module alone it repeats three times (once per `export_*_report` function) with
zero variation in shape. A generic `resolve_now` helper would need its own `Callable[[], T]`
type parameter and its own small test, for a savings of a few characters removed per call site
— exactly the "three similar lines is better than a premature abstraction" guidance this
project follows: the pattern is instantly recognizable in place to anyone who's seen it once,
and a wrapper function adds a layer of indirection a reader has to look up, for no real
reduction in the risk of getting it wrong (there's nothing subtle enough about `x or
default_factory()` for a shared helper to actually protect against). It would become worth
extracting only if a fourth, genuinely different default-resolution rule appeared — one with
real complexity (e.g., timezone-aware resolution) where getting it right independently in three
separate places actually risked drift.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k generated_at_defaults -v` and read
`test_order_validation_report_generated_at_defaults_when_omitted`
(`tests/test_report_export.py:173–176`) — confirm it calls
`export_order_validation_report` with no `generated_at` argument at all and only asserts a
*relationship* (`manifest["generated_at"] != ""`, `report_id.startswith(...)`), never a literal
timestamp — the same technique Tutorial 05 Part 3 used for `as_of_date`'s default branch.

## Part 10 — Presentation-only formatting: header styles, autosize, and draft-message wrapping

Open [`src/report_export.py`](../../../src/report_export.py) lines 107–125 and 138–146:

```python
def _style_header_row(ws: Worksheet, num_columns: int) -> None:
    fill = PatternFill(start_color=HEADER_FILL_COLOR, end_color=HEADER_FILL_COLOR, fill_type="solid")
    font = Font(bold=HEADER_FONT_BOLD)
    for col_index in range(1, num_columns + 1):
        cell = ws.cell(row=1, column=col_index)
        cell.font = font
        cell.fill = fill
    ws.freeze_panes = "A2"


def _autosize_columns(ws: Worksheet, headers: list[str]) -> None:
    for col_index, header in enumerate(headers, start=1):
        column_letter = ws.cell(row=1, column=col_index).column_letter
        max_length = len(str(header))
        for row in ws.iter_rows(min_row=2, min_col=col_index, max_col=col_index):
            cell_value = row[0].value
            if cell_value is not None:
                max_length = max(max_length, len(str(cell_value)))
        ws.column_dimensions[column_letter].width = min(max_length + 2, 60)
```

Both functions are used by *every* sheet-writer in this module — `_write_detail_sheet`,
`_write_summary_sheet`, and `_write_raw_dataframe_sheet` each call `_style_header_row` and
`_autosize_columns` after building their rows, regardless of which report or sheet type is
calling them. `_style_header_row` bolds row 1 and applies `HEADER_FILL_COLOR` (a literal hex
string, `"D9E1F2"` — `explanation.md` names this directly as workbook-styling territory
distinct from this project's Next.js/Tailwind semantic-token rule, since `openpyxl`'s
`PatternFill` API has no token equivalent to call instead), then freezes row 1 so it stays
visible while a reader scrolls a long sheet. `_autosize_columns` walks every cell in a column
once, tracking the longest stringified value seen, and sets a column width from that — capped
at 60 characters so one unusually long cell can't blow out an entire sheet's readability.

One sheet needs something neither generic function provides: `Draft Messages`'
`message_text` column holds real, multi-paragraph reminder text (`DRAFT_MESSAGE_ROW_FIXTURE`'s
own value has two embedded blank lines, Tutorial 05 Part 10) — squashed onto `_autosize_columns`'
one-line-tall row logic, that text would render as a single unreadable line trailing off the
visible sheet. Open [`src/report_export.py`](../../../src/report_export.py) lines 138–146 and
261–262:

```python
def _apply_wrap_text_to_column(ws: Worksheet, column_index: int, width: int = 80, row_height: float = 90) -> None:
    """Wrap long multi-line text (e.g. Draft Messages' message_text) instead of squashing
    it onto one unreadable line — used only for the one column that needs it."""
    column_letter = ws.cell(row=1, column=column_index).column_letter
    ws.column_dimensions[column_letter].width = width
    for row in ws.iter_rows(min_row=2, min_col=column_index, max_col=column_index):
        cell = row[0]
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[cell.row].height = row_height
```

```python
    draft_messages_ws = _write_detail_sheet(wb, "Draft Messages", result["draft_messages"], DRAFT_MESSAGE_COLUMNS)
    _apply_wrap_text_to_column(draft_messages_ws, DRAFT_MESSAGE_COLUMNS.index("message_text") + 1)
```

`_apply_wrap_text_to_column` is called *after* `_write_detail_sheet` has already run — it takes
the already-built `Worksheet` this generic call returned and applies one additional, targeted
formatting pass to exactly one column, identified by `DRAFT_MESSAGE_COLUMNS.index("message_text")
+ 1` (`openpyxl` columns are 1-indexed). `plan.md`'s invariant 12 names why this stays a
separate function rather than folding into `_write_detail_sheet` itself: an earlier draft
apparently lacked this dedicated helper and the multi-paragraph text rendered unreadably,
caught and fixed via `/project-review`. Keeping `_write_detail_sheet` free of any
single-sheet-specific formatting knowledge means every other detail sheet this module ever
writes (five report types' worth, today and in the future) stays untouched by a formatting rule
that only one column, on one sheet, in one report, actually needs.

`tests/test_report_export.py:381–393` proves every piece of this — the *content* survives
unmodified, and the *formatting* is genuinely applied, not merely intended:

```python
def test_payment_aging_report_draft_message_cell_wraps_text():
    # DRAFT_MESSAGE_ROW_FIXTURE.message_text is a real multi-paragraph string with
    # embedded \n — must be readable when opened in Excel, not squashed onto one line.
    workbook_bytes, _ = export_payment_aging_report(_payment_aging_result(), generated_at=GENERATED_AT)
    wb = _load(workbook_bytes)
    ws = wb["Draft Messages"]
    message_text_col = DRAFT_MESSAGE_COLUMNS.index("message_text") + 1  # 1-indexed
    cell = ws.cell(row=2, column=message_text_col)
    assert cell.value == DRAFT_MESSAGE_ROW_FIXTURE["message_text"]
    assert cell.alignment.wrap_text is True
    assert cell.alignment.vertical == "top"
    column_letter = cell.column_letter
    assert ws.column_dimensions[column_letter].width > 60
```

`cell.value == DRAFT_MESSAGE_ROW_FIXTURE["message_text"]` — the embedded `\n` characters and
full multi-paragraph text survive the save/reload round trip completely unmodified;
`_apply_wrap_text_to_column` only ever changes *alignment* and *dimensions*, never the cell's
actual string content. `column_dimensions[...].width > 60` is the concrete proof this column
escaped `_autosize_columns`' 60-character cap (Part 10's opening excerpt) — the one column in
this entire module deliberately allowed to be wider than every other sheet's columns ever get.

**Failure mode — folding draft-message wrapping into generic detail-sheet logic:** if
`_write_detail_sheet` instead carried an `if sheet_name == "Draft Messages":` branch internally
to apply wrapping inline, every future sheet this generic function ever writes would carry the
latent knowledge of one specific report's one specific column — a maintenance hazard that
compounds with every new sheet type added later, and exactly the kind of single-sheet
formatting leak `_write_detail_sheet`'s genericity (Part 5, Part 6) is otherwise carefully kept
free of.

**Checkpoint:** `_style_header_row` and `_autosize_columns` run identically for every sheet in
every report this module produces — including `Original Orders`, whose column set isn't known
until a real DataFrame is passed in (Part 7). Is there a risk that generic, sheet-agnostic
formatting logic like this could behave *incorrectly* for a sheet type its authors weren't
specifically thinking about when they wrote it, the way `Draft Messages` needed a dedicated
exception?

<details>
<summary>Reveal answer</summary>

The risk is real in principle but doesn't currently materialize, because both functions are
written against `Worksheet`'s actual structure (row 1, column count, cell values) rather than
against any assumption about *what kind* of sheet they're formatting — `_autosize_columns`
doesn't need to know whether it's sizing `VALID_ORDER_COLUMNS` or a raw DataFrame's own
`df.columns`, only that row 1 holds headers and every row below holds one value per column,
which is true of every sheet this module writes, `Original Orders` included. The one place this
genuinely broke down — `Draft Messages`' `message_text` — didn't break because the generic
functions were *wrong* for that sheet; it broke because a single-column value's *content shape*
(genuinely multi-paragraph, meant to be read as a paragraph, not a short label) needed a
formatting decision (wrap instead of truncate-and-widen) the generic 60-character-cap logic was
never designed to make for *any* sheet, draft messages included. The fix was additive — one more
targeted pass, called after the generic one — rather than a change to the generic functions
themselves, which is exactly why they remain safe to reuse for whatever sheet type comes next.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_report_export.py -k draft_message_cell_wraps -v` and then, in
`src/report_export.py`, temporarily comment out the `_apply_wrap_text_to_column(...)` call
inside `export_payment_aging_report` (line 262). Re-run the same test and read exactly which
assertion fails first — confirm it's the alignment/width assertions that break, not
`cell.value`, proving the wrap-text helper only ever affects *formatting*, never the underlying
message content. Revert the change afterward.

## Full data flow: one `PaymentAgingResult` traced through `export_payment_aging_report`

Take a single, concrete `PaymentAgingRow` — `PAYMENT_AGING_ROW_FIXTURE` from
[`tests/contract_fixtures.py:128–140`](../../../tests/contract_fixtures.py) — through the
entire export function, alongside its matching `DRAFT_MESSAGE_ROW_FIXTURE`
(lines 150–162):

```python
PAYMENT_AGING_ROW_FIXTURE: PaymentAgingRow = {
    "invoice_id": "INV-2026-001",
    "customer_name": "Bright Medical Trading Ltd",
    "invoice_date": "2026-03-31",
    "due_date": "2026-04-30",
    "invoice_amount": 58000.00,
    "paid_amount": 0.0,
    "outstanding_amount": 58000.00,
    "days_overdue": 70,
    "aging_bucket": "61-90 Days",
    "follow_up_priority": "High",
    "suggested_action": "Call or email customer urgently",
}
```

1. **`export_payment_aging_report(result, generated_at=GENERATED_AT)` entry** (line 246–251).
   `result["aging_rows"]` is `[PAYMENT_AGING_ROW_FIXTURE]`. `effective_generated_at =
   GENERATED_AT or datetime.now()` resolves to the explicitly-passed
   `datetime(2026, 7, 9, 9, 15, 0, 123456)` — the `or` never reaches `datetime.now()` (Part 9).
2. **`follow_up_rows` filter** (lines 252–254). `row["follow_up_priority"] in
   FOLLOW_UP_PRIORITIES` — `"High" in {"High", "Medium", "Low", "Watch"}` is `True`. This one
   row survives into `follow_up_rows` (Part 8).
3. **`_new_workbook()`** (line 256). A fresh `Workbook()` with its default `"Sheet"` already
   removed (Part 2).
4. **`_write_summary_sheet(wb, "Aging Summary", result["summary"])`** (line 257). Iterates
   `PAYMENT_AGING_SUMMARY_FIXTURE`'s keys, flattening `aging_bucket_counts` into several rows
   (Part 2) — this row's own data doesn't feed the summary sheet directly, since summaries are
   pre-aggregated by `payment_aging.py`, not recomputed here.
5. **`_write_detail_sheet(wb, "Follow-up List", follow_up_rows, PAYMENT_AGING_ROW_COLUMNS)`**
   (line 258). `ws.append(PAYMENT_AGING_ROW_COLUMNS)` writes the header row. Then, for this one
   row: `[_safe_cell_value(row.get(col, "")) for col in PAYMENT_AGING_ROW_COLUMNS]` — every
   field (`invoice_id`, `customer_name`, ..., `suggested_action`) is present, so
   `_safe_cell_value` passes each value through unchanged (none are `None`/NaN) (Part 5, Part
   6). `"INV-2026-001"` lands in row 2 of `Follow-up List`.
6. **`_write_detail_sheet(wb, "All Invoices with Aging", result["aging_rows"], ...)`**
   (line 259). The identical row is written a second time, into a second sheet — the same fixed
   `PAYMENT_AGING_ROW_COLUMNS` constant, the same unmodified values. `"INV-2026-001"` now
   appears in two sheets, unfiltered in one and filtered-but-included in the other, because
   `"High"` genuinely belongs in both.
7. **`_write_detail_sheet(wb, "Data Issues", result["data_issues"], ...)`** (line 260). Not
   this row's path — `result["data_issues"]` is a separate list this fixture-driven example
   leaves as whatever the caller supplied (Part 7's "always create the sheet" rule from Tutorial
   05's guard-clause partitioning means a row is never in both `aging_rows` and `data_issues`
   simultaneously).
8. **`draft_messages_ws = _write_detail_sheet(wb, "Draft Messages", result["draft_messages"],
   DRAFT_MESSAGE_COLUMNS)`** (line 261). `DRAFT_MESSAGE_ROW_FIXTURE`'s
   `"invoice_id": "INV-2026-001"` matches the same invoice — its full multi-paragraph
   `message_text` (with embedded `\n\n` line breaks) is written into row 2's last column,
   unmodified.
9. **Wrap-text helper** (line 262). `_apply_wrap_text_to_column(draft_messages_ws,
   DRAFT_MESSAGE_COLUMNS.index("message_text") + 1)` resolves to column index 5 (`message_text`
   is the fifth entry in `DRAFT_MESSAGE_COLUMNS`), widens that column past 60 characters, and
   sets `wrap_text=True`/`vertical="top"` alignment on row 2's cell (Part 10).
10. **`sheet_names = wb.sheetnames`** (line 264). Reads the five real sheets just created, in
    creation order: `["Aging Summary", "Follow-up List", "All Invoices with Aging",
    "Data Issues", "Draft Messages"]` (Part 3).
11. **`_save_workbook_bytes(wb)`** (line 265). `io.BytesIO()` → `wb.save(buffer)` →
    `buffer.getvalue()` — the entire workbook, including both appearances of `"INV-2026-001"`
    and its wrapped draft message, becomes one immutable `bytes` object (Part 2).
12. **`_build_manifest("payment_aging", "payment_aging_report.xlsx", sheet_names,
    effective_generated_at)`** (lines 266–268). `report_id = "rpt-payment_aging-20260709091500"`;
    `generated_at = "2026-07-09T09:15:00"` (microseconds truncated, Part 9);
    `sheet_names` is the exact list read in step 10.
13. **Return `(workbook_bytes, manifest)`** (line 269). Both values travel back together —
    nothing downstream ever needs to reconstruct one from the other.

## A second, shorter trace: `export_order_validation_report()` and why `Original Orders` is separate

`export_order_validation_report(result, original_orders_df, generated_at)` follows the same
four-step shape, but its third parameter deserves its own trace, because it's the one place
this report's data *doesn't* come from `result` at all.

1. **`result: OrderValidationResult`** contains exactly `{summary, valid_orders, errors}` —
   whatever `validate_orders()` computed in Phase 3. It was designed entirely around
   `01_demo_order_validation.md`'s *validation rules*; nothing in that scope called for
   retaining every raw uploaded row (Part 7).
2. **`original_orders_df: pd.DataFrame | None`** is a second, independent parameter — the raw
   `orders.xlsx` DataFrame a caller happens to have on hand (e.g., a future API route that still
   holds the uploaded file in memory alongside the `validate_orders()` result it just computed).
3. **Why not add a field to `OrderValidationResult` instead:** doing so would mean every future
   caller of `validate_orders()` — including ones that only care about validation, never about
   generating a report — would carry a `raw_orders`-shaped payload they never asked for and
   `contracts.py` never specified as part of validation's own output. Keeping the parameter
   separate means `OrderValidationResult`'s contract stays exactly what Tutorial 03 defined it
   as, untouched by Phase 6's presentation-layer needs.
4. **`_write_raw_dataframe_sheet(wb, "Original Orders", original_orders_df)`** (line 215) is the
   only line in `export_order_validation_report` that ever reads `original_orders_df` — every
   other line reads `result`. If `original_orders_df` is `None` (a caller with nothing to
   supply), the sheet still gets created, header-only (Part 7) — the workbook's sheet *count*
   never depends on which parameter a particular caller happened to have data for.
5. **The two data sources never merge.** `Valid Orders` and `Validation Errors` are built purely
   from `result`; `Original Orders` is built purely from `original_orders_df`. No row from one
   is ever cross-referenced against, filtered by, or written into the other — they're two
   genuinely independent sheets that happen to describe overlapping data (the same order rows,
   before and after validation), assembled into one workbook for a human's convenience, not
   because the code treats them as one combined dataset.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Open
`tests/test_report_export.py:155-170`
(`test_order_validation_report_missing_notrequired_field_renders_blank`). Before reading the
assertions, use Part 5 and Part 6 to predict, cell by cell, what row 2 of the `Validation
Errors` sheet looks like for `error_without_sku` (which the test constructs with `sku` and
`order_id` both entirely absent from the dict, not blank). Write out, for each of the six
`VALIDATION_ERROR_COLUMNS` entries, what value you expect `row.get(col, "")` to produce
*before* `_safe_cell_value` runs, and what you expect the cell to hold *after* a
save/reload round trip. Then run the test and check your work.

<details>
<summary>Hint</summary>

`row_number`, `error_code`, `error_message`, and `severity` are present in `error_without_sku`
— those four should match your straightforward prediction. `sku` and `order_id` are the two
you need Part 5's `.get(col, "")` default *and* Part 6's save/reload discovery for — predict
what `.get(col, "")` returns before the round trip, then predict what that same cell shows
*after* one.
</details>

**Challenge 2 — Extend** (20–30 min): Add a new sheet, `High Priority Follow-up`, to
`export_payment_aging_report` — a further-filtered view of `Follow-up List` containing only
rows where `follow_up_priority == "High"`. Follow the exact pattern Part 8 established: define
the filter as its own named constant (not an inline string comparison), build the filtered list
the same way `follow_up_rows` is built, add one new `_write_detail_sheet` call using the
existing `PAYMENT_AGING_ROW_COLUMNS` constant (no new column shape needed — this sheet has the
exact same row shape as `Follow-up List`), and update the `payment_aging` entry in
`REPORT_MANIFEST_FIXTURES` (`tests/contract_fixtures.py:185-197`) to include the new sheet name
in the correct position. Then write one new test proving the new sheet excludes Medium/Low/Watch
rows the way `Follow-up List` includes them.

<details>
<summary>Hint</summary>

Adding the sheet without updating `REPORT_MANIFEST_FIXTURES` will make every existing
`sheet_names_match_manifest_fixture`-style test fail immediately (Part 3) — that failure is
itself proof the manifest-fixture contract is doing its job, not a bug in your new code. Decide
where in the sheet order the new sheet belongs *before* writing the fixture update; sheet order
is part of the contract, not an afterthought.
</details>

**Challenge 3 — Break and fix** (30–45 min): Temporarily rewrite `_build_manifest`'s call sites
so that, instead of `sheet_names = wb.sheetnames`, each `export_*_report` function passes a
manually-typed-out literal list of sheet names (copy the correct list from
`REPORT_MANIFEST_FIXTURES` for each report type). Run the full test suite — predict, before
running, whether anything fails. Then, still using the hardcoded lists, delete one
`_write_detail_sheet(...)` call from `export_inventory_allocation_report` (say, the
`Supplier Follow-up` sheet) without updating your hardcoded manifest list to match. Run the
tests again. Explain in one paragraph, referencing Part 3's checkpoint, exactly which test
catches this drift and why the original `wb.sheetnames`-derived design makes this specific bug
impossible to introduce by accident in the first place. Revert both changes afterward.

<details>
<summary>Hint</summary>

Your first prediction should be "nothing fails" — a hardcoded list that's initially copied
correctly from the real sheet order is indistinguishable from the derived version, by design,
until something changes. The second step is where the two designs diverge: with `wb.sheetnames`,
deleting a sheet-writing call automatically shrinks the manifest to match (nothing to keep in
sync); with a hardcoded list, deleting the call silently leaves a phantom sheet name in the
manifest that no longer corresponds to any real sheet in the workbook — find the exact
assertion in `tests/test_report_export.py` that would catch this, and the exact assertion (if
any) that would happen to catch it even *without* a test written specifically to catch drift.
</details>

For deeper exploration, `docs/plan/phase-6-excel-report-export/ai-discussion-topics.md` has 14
prompts covering module-boundary decisions if a fourth business module appeared, the
`openpyxl` empty-string/`None` round-trip discovery process itself, and how far the
allow-list's "defense-in-depth over a module we deliberately never revalidate" reasoning should
extend. Feed them to an LLM *after* forming your own answer first — the gap between what you
thought and what you learn is where understanding lands.
