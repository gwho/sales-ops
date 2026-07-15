# Tutorial 03 — Order Validation Core: Contracts Become Business Rules

**After completing this tutorial you will understand:** why `validate_orders()` returns a single
result envelope instead of a tuple of DataFrames, why a missing *column* and a blank *cell* are
two structurally different failures handled at two different boundaries, how a genuine spec
contradiction (`payment_terms` in both OV-001 and OV-007) gets resolved and documented rather than
silently picked, why one messy input row can legitimately produce several independent errors, why
type/value rules skip blank fields instead of re-flagging them, how defensive parsing turns
whatever pandas hands back from Excel into either a clean value or a business-readable message,
why a summary count must be a distinct-row count and not a sum of category counts, why error
ordering is a tested contract instead of an implementation accident, and why the test file is the
first-class proof that every one of these decisions actually holds.

> [!NOTE]
> **Prerequisites:** Tutorial 01 (`01-python-foundation/README.md`) — this tutorial reuses
> `TypedDict` contracts from `src/contracts.py`, `load_excel`/`validate_required_columns` from
> `src/excel_io.py`, and the exception-translation pattern (`MissingColumnsError`) without
> re-explaining them. Tutorial 02 (`02-sample-data/README.md`) — not required reading, but useful
> background on why `sample_data/*.xlsx` stays a *demo* fixture while this phase's rule coverage
> lives entirely in `tests/test_order_validation.py`'s inline DataFrames. Open
> [`src/order_validation.py`](../../../src/order_validation.py),
> [`src/contracts.py`](../../../src/contracts.py),
> [`src/excel_io.py`](../../../src/excel_io.py), and
> [`tests/test_order_validation.py`](../../../tests/test_order_validation.py) alongside this
> tutorial.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Hash map lookup for O(1) reference-data joins | `_build_product_master_lookup()` — a `dict[str, dict]` keyed by `sku` | Data structures |
| Set for distinct-element deduplication | `invalid_row_numbers: set[int]` in `validate_orders()` | Data structures |
| Composite-key stable sort | `_sort_key()` returning `(row_number, rule_rank, field_rank)` fed to `.sort(key=...)` | Algorithms |
| Independent rule evaluation (rule-chain / specification pattern) | `_validate_row()`'s sequential, non-branching OV-001…OV-007 checks | Design patterns |
| Multi-exception catch as defensive type coercion | `except (ValueError, TypeError):` in `_parse_quantity()` / `_parse_date()` | Python language |

## How to use an LLM before this tutorial

### Concept 1 — Business rules vs. programming errors

> "Explain the difference between a 'business rule violation' (e.g., an order's quantity is zero,
> a required field is blank) and a 'programming error' (e.g., a `TypeError` from calling a method
> on `None`, an off-by-one index bug). Both can happen while processing the same piece of data —
> what's the test that tells you which category a given failure belongs to? Give an example of
> code that wrongly treats a business rule violation as a programming error (crashes instead of
> reporting), and one that wrongly treats a programming error as a business rule (silently
> swallows a real bug as 'just bad data'). Quiz me on a new example and ask me to classify it."

*What to listen for:* the dividing line is *whose responsibility it is to fix*. A business rule
violation is something the data's owner (a sales admin who typed the spreadsheet) can act on and
correct — it belongs in the output as a readable message. A programming error is something only a
developer can fix, because the code itself is wrong regardless of what data it received — it
should surface as a crash/traceback during development, not get silently converted into a "nice"
error message that hides a real bug.

*Practice question:* if a quantity cell contains the text `"ten"` instead of a number, is that a
business rule violation or a programming error — and what would code that gets this classification
backwards look like?

### Concept 2 — Row-level validation

> "In a batch validation system that processes many rows of tabular data (like spreadsheet rows),
> explain what it means to validate 'per row' rather than validating the whole dataset as a single
> unit. Why would a system that stops at the *first* invalid row (fail-fast) be worse for a human
> user than one that reports every invalid row from a single pass? What data structure would you
> use to carry 'here's everything wrong, and where' back to the caller? Quiz me on the trade-off
> between fail-fast and collect-everything validation."

*What to listen for:* collect-everything (report every row's every problem in one pass) trades a
small amount of extra computation for a dramatically better user experience — someone fixing a
50-row spreadsheet wants one list of every problem, not fifty separate rounds of "fix one thing,
re-upload, discover the next problem." The natural data structure is a flat list of error records,
each carrying enough context (which row, which field, what's wrong) to act on independently.

*Practice question:* if a validator stops at the first invalid row it finds, what does a user with
three separately-broken rows in their file experience when they try to fix their spreadsheet?

### Concept 3 — Defensive parsing at a boundary

> "A function receives a value that's *supposed* to be a positive whole number, but the actual
> caller is a spreadsheet library that might hand back an `int`, a `float`, a boxed numeric type
> from a numeric computing library, or literal text like 'N/A'. Explain what 'defensive parsing'
> means in this context: attempting to interpret whatever arrives as the intended type, and
> producing a clear failure signal (not a crash) when it can't. What's the difference between
> defensive parsing and just wrapping the whole function body in a blanket try/except? Quiz me on
> why a defensive parser should still let unrelated/unexpected exceptions propagate."

*What to listen for:* defensive parsing narrows the exception types it catches to exactly the
ones the parsing operation itself can raise (e.g., `ValueError`/`TypeError` from a failed numeric
conversion) — a blanket `except Exception` would also silently swallow a genuine bug elsewhere in
the same code path, turning a crash that should get fixed into a confusing, wrong "data quality"
error message instead.

*Practice question:* why would catching `except (ValueError, TypeError):` around a numeric
conversion be safer than catching bare `except:`?

### Concept 4 — Distinct-count summaries vs. summed category counts

> "You're computing a summary count: 'how many rows in this dataset have at least one problem?'
> Some rows have exactly one problem; a few unlucky rows have two or three different problems at
> once. Explain why summing 'count of problem type A' + 'count of problem type B' + 'count of
> problem type C' produces the wrong answer for 'how many rows have at least one problem,' and what
> data structure correctly answers that question instead. Quiz me with a concrete small example
> (a handful of rows, a few overlapping problems) and ask me to compute both the (wrong) summed
> total and the (right) distinct count by hand."

*What to listen for:* summing per-category counts double-counts (or triple-counts) any row that
happens to trigger more than one category — the fix is to collect the *set* of row identifiers
that have at least one problem, then take that set's size, since a set can never contain the same
row identifier twice no matter how many different problems that row had.

*Practice question:* five rows have a missing field, three rows have an invalid value, and one
row has *both* problems at once. How many distinct invalid rows are there, and how does that
differ from `5 + 3`?

### Concept 5 — Deterministic output ordering

> "Explain why a function that returns a list of records (e.g., validation errors, log lines,
> search results) might deliberately sort that list by an explicit key, even when the order it
> would naturally come out in (e.g., following iteration order) already happens to look right in
> casual testing. What breaks — for automated tests, and for a future UI — if the output order is
> only an accident of implementation rather than a guaranteed, tested contract? Quiz me on what
> kind of unrelated code change could silently reorder 'accidental' output without anyone
> intending it to."

*What to listen for:* an order that emerges by accident (e.g., "rules happen to run in this
sequence today") is not documented anywhere and isn't protected by anything — a future refactor
that reorders internal logic for an unrelated reason (say, performance) can silently change output
order with no test catching it, breaking any test written with `assert result == [...]` in a
specific sequence, and producing a flickering, inconsistent-feeling UI table for end users.

*Practice question:* if a list's current order is never explicitly sorted, just "however the loop
happened to produce it," what has to remain true elsewhere in the code forever for that order to
stay stable?

## Architecture overview

Phases 1–2 built shapes (`src/contracts.py`) and believable fictional data
(`src/sample_data.py`). Phase 3 is the first module that actually *computes* something — it takes
two DataFrames and a set of business rules and produces a decision, per row, about whether that
row is usable:

```text
              orders.xlsx                    product_master.xlsx
                   │                                  │
                   ▼                                  ▼
       ┌─────────────────────┐          ┌─────────────────────────┐
       │  load_orders(file)   │          │ load_product_master(file)│
       │  (excel_io.load_excel│          │ (same pattern)            │
       │  + validate_required_│          │                            │
       │  columns — raises     │          │                            │
       │  MissingColumnsError  │          │                            │
       │  if a COLUMN is gone) │          │                            │
       └──────────┬────────────┘          └────────────┬──────────────┘
                   │ pandas DataFrame                    │ pandas DataFrame
                   ▼                                     ▼
       ┌───────────────────────────────────────────────────────────┐
       │                    validate_orders(orders_df,               │
       │                                    product_master_df)       │
       │                                                               │
       │  1. _find_duplicate_order_ids()   — set of dup order_ids     │
       │  2. _build_product_master_lookup()— dict[sku -> row]         │
       │  3. for each row:                                             │
       │       _validate_row()  → list[ValidationErrorRow]            │
       │       any "Error" severity?                                   │
       │         yes → row_number added to invalid_row_numbers (set)  │
       │         no  → _build_valid_order_row() → ValidOrderRow       │
       │  4. all_errors.sort(key=_sort_key)  — deterministic order    │
       │  5. compute ValidationSummary from all_errors + the set      │
       └──────────────────────────────┬────────────────────────────┘
                                       ▼
                     OrderValidationResult
                     { summary, valid_orders, errors }
```

Key invariants for this phase:

1. **A row's *presence* (all required columns exist) and a row's *content* (a cell is blank or
   malformed) are validated at two different boundaries** — the loader raises for the first, rule
   OV-001 (or a type/value rule) reports the second as data (Part 2).
2. **Every rule is evaluated independently, every time.** No rule's result depends on whether an
   earlier rule already fired for the same row — a row can and does end up with multiple error
   records (Part 4).
3. **Nothing in this module raises for malformed *data*.** A non-numeric quantity or an
   unparseable date becomes a `ValidationErrorRow`, never an uncaught exception (Part 6).

## Part 1 — A result envelope, not a tuple

The spec's own suggested signature (`01_demo_order_validation.md` §11) is
`validate_orders(...) -> tuple[pd.DataFrame, pd.DataFrame]` — two DataFrames, valid and invalid.
The actual implementation does something different. Open
[`src/order_validation.py`](../../../src/order_validation.py) lines 65–69:

```python
class OrderValidationResult(TypedDict):
    summary: ValidationSummary
    valid_orders: list[ValidOrderRow]
    errors: list[ValidationErrorRow]
```

and the function that returns it, lines 387–424:

```python
def validate_orders(orders_df: pd.DataFrame, product_master_df: pd.DataFrame) -> OrderValidationResult:
    """Validate order lines against every OV-001..OV-007 rule and return the full result envelope."""
    duplicate_order_ids = _find_duplicate_order_ids(orders_df)
    product_master_lookup = _build_product_master_lookup(product_master_df)

    all_errors: list[ValidationErrorRow] = []
    valid_orders: list[ValidOrderRow] = []
    invalid_row_numbers: set[int] = set()

    for position, (_, row) in enumerate(orders_df.iterrows()):
        row_number = position + 2
        row_errors = _validate_row(row, row_number, duplicate_order_ids, product_master_lookup)
        all_errors.extend(row_errors)

        has_error_severity = any(error["severity"] == "Error" for error in row_errors)
        if has_error_severity:
            invalid_row_numbers.add(row_number)
        else:
            valid_orders.append(_build_valid_order_row(row, product_master_lookup))

    all_errors.sort(key=_sort_key)

    total_orders = len(orders_df)
    invalid_orders = len(invalid_row_numbers)
    duplicate_orders = sum(1 for error in all_errors if error["error_code"] == "OV-002")
    invalid_skus = sum(1 for error in all_errors if error["error_code"].startswith("OV-003"))
    missing_field_count = sum(1 for error in all_errors if error["error_code"] == "OV-001")

    summary: ValidationSummary = {
        "total_orders": total_orders,
        "valid_orders": total_orders - invalid_orders,
        "invalid_orders": invalid_orders,
        "duplicate_orders": duplicate_orders,
        "invalid_skus": invalid_skus,
        "missing_field_count": missing_field_count,
    }

    return {"summary": summary, "valid_orders": valid_orders, "errors": all_errors}
```

A `tuple[pd.DataFrame, pd.DataFrame]` would return valid rows and error rows, but nowhere to put
the summary counts (`total_orders`, `duplicate_orders`, and so on) without recomputing them a
second time from whichever DataFrame the caller happens to have — and pandas DataFrames aren't
what any downstream consumer (a test, a future FastAPI route, a future Next.js component) actually
wants: they want the exact JSON-shaped `TypedDict` contracts already defined in `src/contracts.py`.
A single `OrderValidationResult` dict bundles the three things every caller of `validate_orders`
needs in one already-JSON-serializable value, with a name for each piece instead of a positional
tuple where "which DataFrame was `[0]` again?" is a real source of bugs.

Notice `OrderValidationResult` is defined *inside* `order_validation.py`, not added to
`src/contracts.py` alongside `ValidationSummary`, `ValidationErrorRow`, and `ValidOrderRow`. This
is a deliberate distinction from Tutorial 01's discussion of why `contracts.py` centralizes
output-contract shapes: `contracts.py` holds shapes a spec explicitly defines as *business-facing*
output (per `CLAUDE.md`'s Output Contract rules and the Field Scope Boundary) — `ValidationSummary`
and `ValidationErrorRow` are each named and specified in `01_demo_order_validation.md` §7–8.
`OrderValidationResult` is not a new business-facing shape at all; it's a *transport envelope* that
bundles three already-defined contracts together for this one function's return type. Promoting it
into `contracts.py` would blur "shapes the spec defines" with "how one particular function happens
to package its return value."

**Checkpoint:** `ValidOrderRow.payment_terms` is typed as required (`str`, not `NotRequired[str]`)
in `src/contracts.py`, yet a row with a blank `payment_terms` (an OV-007 Warning) still ends up
in `valid_orders`. Look at `_build_valid_order_row` (`src/order_validation.py:365-366`) — how is
that contradiction resolved?

<details>
<summary>Reveal answer</summary>

`payment_terms` is normalized to the empty string `""` rather than omitted:
`payment_terms_str = "" if _is_blank(payment_terms) else _to_trimmed_str(payment_terms)`. The
contract's `str` type is satisfied — the key is always present with a string value — while the
*business* fact "payment terms weren't actually provided" is preserved by that value being empty
rather than some placeholder like `"N/A"`. This is a smaller-scale version of the same
Field-Scope-Boundary discipline as Tutorial 01's `NotRequired` fields: the contract's shape isn't
renegotiated per-call just because one particular row happens to have a Warning instead of full
data; the *value* absorbs that instead.
</details>

**Checkpoint:** `src/order_validation.py:358-363` fills `product_name` from
`product_master_df` only when the order row's own `product_name` is blank — a fallback the spec
never explicitly describes; it was inferred from "the product master is the reference file for
product data." Is this the kind of small, reasonable inference that's fine to make without a new
ADR, or does it cross into the "don't invent business outcomes" territory the Field Scope Boundary
warns about for UI work?

<details>
<summary>Reveal answer</summary>

It's on the safe side of that line, but only because of what it does *not* do: it never invents a
new field, never changes what `product_name` means, and never overrides a value the order row
itself supplies — it only fills in a value the row already has a slot for, using the one reference
file the spec explicitly names for exactly that purpose (`01_demo_order_validation.md` §5,
`product_master.xlsx`'s `product_name` column). The Field Scope Boundary's actual concern is adding
a field a spec never defined, or inventing a business *outcome* (e.g., deciding what "high
priority" means when the spec never said). Filling an existing, spec-defined field from the one
reference table the spec names for that field is closer to "correctly reading the input the spec
already described" than to invention — but this is a judgment call worth naming explicitly in
`explanation.md` (as Phase 3's did) rather than assuming silently, precisely because a future
reader could reasonably ask the question this checkpoint just asked.
</details>

This is not a claim left to argue in prose alone — `tests/test_order_validation.py`'s
`# --- Optional field handling: product_name fill-from-master, sales_owner ---` section
(lines 313–331) is the executable proof, and it locks down both directions of the fallback plus a
second, unrelated optional field in the same breath:

```python
def test_blank_product_name_fills_from_product_master():
    result = validate_orders(_orders_df(_order_row(product_name="")), _product_master_df())
    assert result["valid_orders"][0]["product_name"] == "Optical Lens Kit"


def test_present_product_name_is_not_overridden_by_master():
    result = validate_orders(
        _orders_df(_order_row(product_name="Custom Label")), _product_master_df()
    )
    assert result["valid_orders"][0]["product_name"] == "Custom Label"


def test_blank_sales_owner_is_omitted_from_valid_order_row():
    result = validate_orders(_orders_df(_order_row(sales_owner="")), _product_master_df())
    assert "sales_owner" not in result["valid_orders"][0]
```

The first two tests are a matched pair, not one test in isolation — proving only the blank case
fills from the master would leave open whether the fallback *also* clobbers a value the order row
legitimately supplied. The second test asserts the opposite direction: a present `product_name` is
never overridden, even though the master has its own value for the same SKU. `sales_owner` gets a
different treatment entirely — rather than filling from anywhere, a blank one is simply omitted
from the `ValidOrderRow` dict, consistent with `sales_owner: NotRequired[str]` in `src/contracts.py`
(Tutorial 01, Part 1) — this is `NotRequired` actually being exercised at the value level, not just
declared in the type.

**Checkpoint:** Now that Phase 3 is done and Phases 4/5 (`inventory_allocation.py`,
`payment_aging.py`) are on the horizon with their own result envelopes, what would have to be true
for the "local `TypedDict`, not `contracts.py`" precedent to still make sense — and what would be
the tell that a shared "module result wrapper" belongs in `contracts.py` after all?

<details>
<summary>Reveal answer</summary>

The precedent holds as long as each module's envelope is *purely* a bundle of that module's own
already-defined contracts, with no new fields of its own — `OrderValidationResult` adds nothing
beyond `{summary, valid_orders, errors}`, three names for three existing shapes. It would stop
making sense the moment two or more envelopes needed literally the same shape (e.g., if
`InventoryAllocationResult` and `PaymentAgingResult` both turned out to need an identical
`{summary, rows, issues}` shape with no module-specific differences) — at that point, defining the
same structural shape three separate times, once per module, is the kind of duplication that
argues for a single shared wrapper type. The tell isn't "there are now three envelopes"; it's
"the three envelopes are structurally identical," which hasn't happened yet — `PaymentAgingResult`
will likely need a `draft_messages` field this shape doesn't have.
</details>

**Try it yourself:** Run
`uv run python -c "from src.order_validation import validate_orders; import pandas as pd; from datetime import date; orders = pd.DataFrame([{'order_id': 'SO-1', 'order_date': date(2026,7,1), 'customer_name': 'Test Co', 'customer_region': 'HK', 'sku': 'X-1', 'quantity': 5, 'requested_delivery_date': date(2026,7,10), 'priority': 'High', 'payment_terms': '30 days'}]); master = pd.DataFrame([{'sku': 'X-1', 'product_name': 'Widget', 'active': True}]); result = validate_orders(orders, master); print(result.keys())"`
and confirm the three top-level keys printed are exactly `summary`, `valid_orders`, `errors` — the
envelope, not a tuple.

## Part 2 — Loader boundary vs. row-rule boundary

Before any rule runs, a **business rule** is a condition a domain expert (not a programmer) would
recognize as "this order is wrong" — a blank customer name, a duplicate order number, a quantity
of zero. **Validation** is the general act of checking data against those rules and reporting
which pieces pass and which fail. A **row-level error** is a validation failure scoped to exactly
one input row, carrying enough context (which row, which field, what's wrong) that a person can go
fix that one row without re-reading every other row in the file.

Order validation has *two* different kinds of "something's missing," handled at two different
places in the code, and conflating them would be a real design mistake. Open
[`src/order_validation.py`](../../../src/order_validation.py) lines 71–82:

```python
def load_orders(file) -> pd.DataFrame:
    """Load orders.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, ORDERS_REQUIRED_COLUMNS, "orders file")
    return df


def load_product_master(file) -> pd.DataFrame:
    """Load product_master.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, PRODUCT_MASTER_REQUIRED_COLUMNS, "product master file")
    return df
```

`load_orders` reuses Tutorial 01's `load_excel` and `validate_required_columns` unchanged — no new
loading logic exists in this module, exactly as the module-boundary rule requires
(`excel_io.py` owns loading; `order_validation.py` owns rules). If the uploaded workbook is
missing an entire `payment_terms` *column* — the header row itself never had that column — this
raises `MissingColumnsError` and the request stops immediately: there is no row-by-row data to
even look at yet, because the file itself doesn't match the shape this workflow requires.

Contrast that with a file that *has* every required column, but where some cell in the
`payment_terms` column is empty for one particular row. That's not a loader problem at all — the
column exists, `load_orders` succeeds, and the DataFrame comes back with a normal `payment_terms`
column that merely has a blank value on one row. That's `_is_blank`'s job, line 85–93:

```python
def _is_blank(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False
```

`_is_blank` is the row-rule boundary's equivalent of `validate_required_columns` — but it checks
one *cell's* content instead of a DataFrame's *column list*. It's called throughout `_validate_row`
(Part 4) to decide, per field, whether OV-001 should fire. `tests/test_order_validation.py:336-353`
proves the two boundaries are genuinely independent: dropping the `payment_terms` column entirely
raises `MissingColumnsError` (`test_load_orders_raises_when_payment_terms_column_missing`), while
keeping the column but leaving every cell in it blank loads successfully with no exception at all
(`test_load_orders_succeeds_when_payment_terms_column_present_but_blank`) — the blank-cell case is
left entirely to `validate_orders`'s row-level rules to report. A third test,
`test_load_product_master_raises_when_active_column_missing` (`tests/test_order_validation.py:356-363`),
proves the identical loader-boundary discipline holds for `load_product_master` too, not just
`load_orders` — the same `MissingColumnsError`/`validate_required_columns` pairing from Tutorial 01
is exercised against `PRODUCT_MASTER_REQUIRED_COLUMNS` rather than `ORDERS_REQUIRED_COLUMNS`, and
the test file bothers to prove it separately rather than assuming the pattern generalizes.

**Checkpoint:** Why does a missing *column* deserve to stop the whole request (an exception), while
a missing *value* in a column that does exist gets folded into the normal per-row error list
instead?

<details>
<summary>Reveal answer</summary>

A missing column means the uploaded file doesn't match the shape this workflow was told to expect
at all — there's no reliable way to process *any* row, because the code that reads `row["sku"]"`
would raise a `KeyError` on literally every row, not just a data-quality issue on some of them.
That's a structural mismatch, correctly modeled as an exception that halts processing before any
row-level work starts. A blank cell in a column that *does* exist is a per-row data-quality fact —
99 other rows in the same file might have a perfectly valid `payment_terms` value, so there's no
reason to treat one row's blank cell as reason to stop processing the other 99. Folding it into the
row-level error list (rather than raising) is what lets `validate_orders` report every row's
problems in one pass, per the row-level-validation concept covered in this tutorial's pre-study.
</details>

**Checkpoint:** `_is_blank` treats `None`, an empty/whitespace-only string, and any pandas
"not-a-number" value (`pd.isna`) as blank — but wraps the `pd.isna` call in a
`try/except (TypeError, ValueError)` that returns `False` on failure. What kind of value would
reach that `except` branch, and why is `False` (not blank) the safe fallback rather than re-raising?

<details>
<summary>Reveal answer</summary>

`pd.isna()` expects a scalar or array-like value; it can raise `TypeError` or `ValueError` on a
handful of unusual objects it doesn't know how to evaluate (this is defensive against the exact
same category of "pandas can hand back a surprising type" problem Part 6 covers in more depth for
`_parse_quantity` and `_normalize_active`). Returning `False` — "not blank" — rather than
re-raising means an unusual, un-checkable value falls through to whichever downstream rule was
about to inspect it (e.g., OV-004's quantity parser), which is exactly designed to turn an
unparseable value into its own business-readable error message. Re-raising here would crash the
whole request over a single cell; letting the value flow onward to a rule built to handle "this
doesn't parse" produces a much more useful outcome for the same underlying problem.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_order_validation.py -k "missing_column or blank_payment_terms" -v` and
read both test names and their outcomes — confirm one raises and the other doesn't, for what looks
like "the same" missing `payment_terms`, and match each to the boundary it's testing.

## Part 3 — Resolving the OV-001 vs. OV-007 contradiction

Open [`sales_admin_automation_toolkit_specs/01_demo_order_validation.md`](../../../sales_admin_automation_toolkit_specs/01_demo_order_validation.md)
§6, and read Rule OV-001's required-field list (lines 66–78) next to Rule OV-007 (lines 104–106):

> **Rule OV-001 — Required fields** — The following fields must not be empty: `order_id`,
> `order_date`, `customer_name`, `customer_region`, `sku`, `quantity`, `requested_delivery_date`,
> `priority`, `payment_terms`.
>
> **Rule OV-007 — Payment terms must be provided** — Payment terms should not be blank. V1 does
> not need to validate complex payment terms, but missing values should be flagged.

The spec's §8 example table lists `OV-001` as an `Error` in every one of its examples, and lists
`OV-007` as a `Warning` explicitly. Both rules cover the exact same fact — a blank
`payment_terms` cell — but assign it two different severities. Followed literally, a row with only
a blank `payment_terms` would get *both* an OV-001 Error and an OV-007 Warning simultaneously.
That's not just redundant — it actively breaks a separate decision this project makes ("a row with
only Warnings stays in `valid_orders`"), because the row would also carry an Error from OV-001 and
therefore get excluded, contradicting OV-007's own explicit `Warning` severity for the identical
condition.

Open [`src/order_validation.py`](../../../src/order_validation.py) lines 26–40 and lines 330–334:

```python
# OV-001 required fields in fixed column order. payment_terms is intentionally
# excluded — a blank payment_terms is exclusively an OV-007 Warning, not an
# OV-001 Error (the spec's own required-fields list and its OV-007 rule
# conflict on this field; resolved in favor of OV-007 so "Warning never
# disqualifies a row" stays internally consistent).
OV001_REQUIRED_FIELDS = [
    ("order_id", "Order ID"),
    ("order_date", "Order date"),
    ("customer_name", "Customer name"),
    ("customer_region", "Customer region"),
    ("sku", "SKU"),
    ("quantity", "Quantity"),
    ("requested_delivery_date", "Requested delivery date"),
    ("priority", "Priority"),
]
```

```python
    # OV-007 — payment terms missing is a Warning only, and is the exclusive rule for this field.
    if _is_blank(row.get("payment_terms")):
        errors.append(
            _make_error(row_number, "OV-007", "Payment terms are missing.", "Warning", order_id, sku)
        )
```

`payment_terms` is removed from `OV001_REQUIRED_FIELDS` entirely — not conditionally skipped, not
special-cased at check time, simply absent from the list OV-001 iterates over. OV-007 becomes the
field's sole owner. The resolution favors OV-007 over OV-001 for two concrete reasons named in
`explanation.md`: OV-007 is the *more specific*, deliberately-authored rule — it has its own
number, its own dedicated explanation, and an explicit non-Error severity stated directly in the
spec's example table — while OV-001's required-fields list reads like a generic, likely
block-copied list where a field that already had its own dedicated rule was probably included by
oversight, not by deliberate double-coverage.

**Checkpoint:** What signals were used to decide OV-007 should win (the more specific rule with an
explicit severity) rather than OV-001 (the more generic, earlier-listed rule)? When would the
opposite resolution — the earlier/broader rule wins — be the more defensible call?

<details>
<summary>Reveal answer</summary>

The signals favoring OV-007: it's the *more specific* rule (one field, one dedicated explanation)
versus OV-001's *general* required-field sweep; it has an *explicit, stated severity* (`Warning`)
in the spec's own example table, while OV-001's severity for this field is only implied by pattern
("every OV-001 example is `Error`"); and choosing OV-007 keeps a separate, already-decided
invariant ("Warning-only rows stay valid") internally consistent, while choosing OV-001 would
break it. The opposite resolution — broader rule wins — would be more defensible if the *general*
rule were the one with explicit intent behind the specific field (e.g., if the spec's prose
explicitly said "payment_terms must always disqualify a row, full stop, regardless of any other
rule text") — i.e., when the specificity and the explicitness point the *other* way. Here, both
signals agree: OV-007 is both more specific and more explicit.
</details>

**Checkpoint:** This conflict was caught by working through a concrete "which fields does OV-001
actually check" question during planning, not by reading the spec start to finish. What's a
systematic way to find every place a source-of-truth document contradicts itself before code
depends on the wrong interpretation?

<details>
<summary>Reveal answer</summary>

One systematic approach: build the *inverse index* before implementing anything — for every field
name that appears in the spec, list every rule that mentions it, not just the rule you're
currently implementing. `payment_terms` shows up in both OV-001's list and OV-007's dedicated
section; building that field-to-rules index surfaces the overlap mechanically, without relying on
noticing it during a single linear read-through. More generally: any time a spec defines both a
general list (OV-001's "these fields must not be empty") and a specific rule about one of the same
items (OV-007), that's exactly the shape of place contradictions hide — general/specific overlaps
are worth grep-checking systematically (search every general list's items against every other
rule's subject) rather than trusting a first read to catch them.
</details>

**Try it yourself:** Run `uv run pytest tests/test_order_validation.py -k payment_terms -v` and
read `test_missing_payment_terms_is_warning_only_and_row_stays_valid`
(`tests/test_order_validation.py:254-264`) line by line — confirm it asserts *both* halves of the
resolution: `_errors_by_code(result, "OV-001") == []` (OV-001 never fires for this field) and
`ov007_errors[0]["severity"] == "Warning"` (OV-007 does, and stays a Warning).

## Part 4 — One row can produce multiple errors

Open [`src/order_validation.py`](../../../src/order_validation.py) lines 204–210, the first block
inside `_validate_row`:

```python
    # OV-001 — required fields, one error per missing field, fixed field order.
    for field, label in OV001_REQUIRED_FIELDS:
        if _is_blank(row.get(field)):
            errors.append(
                _make_error(row_number, "OV-001", f"{label} is missing.", "Error", order_id, sku)
            )
```

This loop doesn't stop after the first missing field — it checks all eight OV-001 fields every
time and appends one `ValidationErrorRow` per blank field. A row with both a blank `customer_name`
and a blank `priority` gets *two* OV-001 errors, not one combined message like "customer_name,
priority are missing." The rest of `_validate_row` (Part 5 and Part 6) follows the same pattern for
every other rule: OV-002 through OV-007 each independently decide whether to append their own
error, with no rule's decision depending on whether an earlier rule already fired for this row.
`tests/test_order_validation.py:126-133` proves a row can trigger completely unrelated rules at
once:

```python
def test_row_can_emit_multiple_errors_across_rules():
    result = validate_orders(
        _orders_df(_order_row(customer_name="", quantity=-1)), _product_master_df()
    )
    codes = {error["error_code"] for error in result["errors"]}
    assert "OV-001" in codes
    assert "OV-004" in codes
    assert result["valid_orders"] == []
```

The alternative — one combined error message per row, or stopping at the first violation — would
throw away exactly the information a person fixing the spreadsheet needs most: knowing *every*
problem with a row in one pass, rather than fixing one thing, re-running validation, and
discovering the next problem. This is the row-level-validation principle from this tutorial's
pre-study, applied at field granularity within a single rule rather than just across rules.

> **Design patterns — Independent rule evaluation (rule-chain / specification pattern):**
> `_validate_row` reads as a flat sequence of independent checks — no `if`/`elif` chain, no early
> `return` after the first match. Each rule block asks "does my specific condition hold?" and
> appends its own error if so, oblivious to what any other block decided. This is the same shape as
> the specification pattern from domain-driven design (a set of independently composable predicate
> objects, each answering one yes/no question about the same input) or a validation-chain library
> like Django's form validators, which likewise runs every field validator and collects every
> failure rather than short-circuiting on the first one. The alternative — an `if`/`elif` chain that
> stops at the first matching rule — is the right shape when exactly one outcome can apply (e.g., a
> priority-ordered dispatch table); it's the wrong shape here, because the whole point is that
> *multiple, independent* facts about the same row can all be true simultaneously.

**Checkpoint:** The decision to emit one `ValidationErrorRow` per missing OV-001 field (instead of
one combined message per row) trades a longer error table for more actionable repair information.
What's the threshold where "one row, N errors" becomes too noisy for a human reviewing a table, and
how would you redesign the UI (not the data) to manage that instead of coarsening the data?

<details>
<summary>Reveal answer</summary>

The noise threshold is really about *table density*, not data correctness — a row with 2-3 errors
reads fine as 2-3 rows in an error table; a row with 8 errors (theoretically possible if every
OV-001 field were blank at once) starts to visually dominate the table and bury other rows' single
errors. The fix belongs in presentation, not in the data: group the error table by `row_number`
(a collapsible section per row, "Row 5 — 3 issues" as a header that expands to the individual
messages) rather than flattening every error into one undifferentiated list. Coarsening the
*data* — going back to one combined message per row — would lose the field-level structure a future
UI needs to, for example, highlight the exact broken cell in a rendered spreadsheet view; that
capability is worth keeping even if the raw error *count* looks noisy in a naive flat table.
</details>

**Checkpoint:** A blank `customer_name` and a blank `priority` on the same row each get their own
`ValidationErrorRow`, in the fixed order `OV001_REQUIRED_FIELDS` defines (`customer_name` before
`priority`). What breaks for a test asserting exact output order if that list's order were changed
later?

<details>
<summary>Reveal answer</summary>

`_OV001_FIELD_ORDER` (`src/order_validation.py:62`) is built directly from
`OV001_REQUIRED_FIELDS`'s position, and `_sort_key` (Part 8) uses that field order as the final
tiebreaker within OV-001 errors on the same row. Reordering `OV001_REQUIRED_FIELDS` would silently
change which OV-001 message comes first for any row with multiple blank fields — any test asserting
a specific message sequence (like `test_ov001_emits_one_error_per_missing_field_in_fixed_order`,
`tests/test_order_validation.py:136-145`) would then fail, correctly, because the deterministic
ordering contract (Part 8) explicitly ties itself to this list's declared order.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_order_validation.py -k ov001_emits_one_error -v -s` and then temporarily
swap the order of `"customer_name"` and `"priority"` inside `OV001_REQUIRED_FIELDS`
(`src/order_validation.py:34-35`). Re-run the same test and observe it fail — read the assertion
diff to see exactly which two messages swapped places. Revert the change before moving on.

## Part 5 — The blank-field skip rule

If OV-001 already reports "quantity is missing" for a blank `quantity` cell, what should OV-004
("quantity must be a positive whole number") do with that same blank cell? Open
[`src/order_validation.py`](../../../src/order_validation.py) lines 211–217 and 264–269:

```python
    blank_order_id = _is_blank(order_id)
    blank_sku = _is_blank(sku)
    blank_quantity = _is_blank(row.get("quantity"))
    blank_order_date = _is_blank(row.get("order_date"))
    blank_delivery_date = _is_blank(row.get("requested_delivery_date"))
    blank_priority = _is_blank(row.get("priority"))
```

```python
    # OV-004 — quantity must be a positive whole number (skipped when blank; OV-001 already covers that).
    quantity_value = None
    if not blank_quantity:
        quantity_value, quantity_error = _parse_quantity(row.get("quantity"))
        if quantity_error is not None:
            errors.append(_make_error(row_number, "OV-004", quantity_error, "Error", order_id, sku))
```

Every field-blank flag is computed once, up front, and every "value quality" rule (OV-002 through
OV-006) checks its own blank flag before doing any real work. An empty `quantity` cell is not also
"not a positive whole number" as far as OV-004 is concerned — OV-004 simply never runs for that
row. Without this guard, a blank `priority` cell would be an empty string, and `"" not in
{"High", "Normal", "Low"}` is `True` — so OV-006 would *also* fire, reporting "Priority must be
High, Normal, or Low" for a cell that's actually just empty, not filled with a wrong value. That's
not two independent facts about the row (unlike Part 4's genuinely-independent multi-rule case) —
it's the *same* underlying problem ("this cell is empty") surfacing under two different rule
numbers, which is noise, not more information. The user needs to know the cell is empty exactly
once.

The same logic extends to OV-002 (a blank `order_id` has nothing to compare for duplicates —
`blank_order_id` guards it) and OV-003/OV-005 (blank `sku` or blank dates skip their respective
value checks). `tests/test_order_validation.py:151-164` proves this for two of the six guarded
rules:

```python
def test_blank_order_id_does_not_trigger_duplicate_check():
    df = _orders_df(_order_row(order_id=""), _order_row(order_id=""))
    result = validate_orders(df, _product_master_df())
    assert _errors_by_code(result, "OV-002") == []
    ov001_messages = [error["error_message"] for error in _errors_by_code(result, "OV-001")]
    assert ov001_messages.count("Order ID is missing.") == 2
```

The guard this tutorial's own code excerpt opened with — `blank_quantity` — has its own dedicated
proof too, `tests/test_order_validation.py:225-229`:

```python
def test_blank_quantity_raises_ov001_not_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=None)), _product_master_df())
    assert _errors_by_code(result, "OV-004") == []
    ov001_errors = _errors_by_code(result, "OV-001")
    assert any(error["error_message"] == "Quantity is missing." for error in ov001_errors)
```

Same shape as the `order_id` test above, deliberately: assert the *skipped* rule produced nothing
(`OV-004 == []`), and assert OV-001 fired instead — proving the redirect, not just the silence.

**Checkpoint:** Before this decision, an empty `priority` cell could produce *two* errors: OV-001
("Priority is missing") and OV-006 ("Priority must be High, Normal, or Low"). Explain in one
sentence why that's noise rather than more actionable information, in contrast to Part 4's
"multiple errors per row from *different* rules" case.

<details>
<summary>Reveal answer</summary>

Part 4's multi-rule case (blank `customer_name` *and* negative `quantity`) reports two genuinely
independent facts about the row — fixing one doesn't fix the other. The blank-`priority`
double-report describes the *same single fact* (the cell is empty) under two different rule
labels — fixing the one real problem (filling in the cell) makes both messages disappear at once,
so reporting both never gave the user two separate things to do; it only made one thing to do look
like two.
</details>

**Checkpoint:** OV-002 (duplicate `order_id`) is guarded by `blank_order_id`, but the guard
variable itself is computed from `_is_blank(order_id)` where `order_id = row.get("order_id")` —
the *raw* cell value, before any trimming. If a row's `order_id` cell contained only whitespace
(`"   "`), would OV-002's duplicate check run?

<details>
<summary>Reveal answer</summary>

No. `_is_blank`'s string branch is `value.strip() == ""` (Part 2) — a whitespace-only string
strips down to an empty string and counts as blank, exactly the same as a truly empty cell. So a
row with `order_id = "   "` skips OV-002 entirely (and instead reports OV-001, since the same
`_is_blank` check gates the required-field loop) rather than being treated as a real, comparable
`order_id` value that just happens to look odd. This consistency — the same `_is_blank` predicate
used everywhere a "is this field present" decision is made — is what keeps the blank-field skip
rule behaving identically across all six guarded rules instead of each rule reinventing its own
notion of "blank."
</details>

**Try it yourself:** Run
`uv run pytest tests/test_order_validation.py -k "blank_priority_does_not_trigger" -v` and read the
test's two assertions — confirm it checks *both* that OV-006 didn't fire *and* that OV-001 did,
proving the skip rule redirects the report rather than silencing it entirely.

## Part 6 — Defensive parsing at the module boundary

A cell that pandas reads back from an Excel file is not guaranteed to be the Python type you'd
expect just from looking at the spreadsheet. Tutorial 01 covered turning a missing-*column*
`KeyError` into `MissingColumnsError` — this is the same "translate a technical surprise into a
business-readable message" idea, but applied to a *value's type*, not a column's presence, and
resolved by returning a message rather than raising at all (following Part 2's boundary split:
this is squarely row-rule territory, not loader territory).

Open [`src/order_validation.py`](../../../src/order_validation.py) lines 113–133:

```python
def _parse_quantity(value: object) -> tuple[int | None, str | None]:
    """Return (quantity, error_message). error_message is None when quantity is a valid positive whole number."""
    if isinstance(value, bool):
        return None, "Quantity must be a valid whole number."
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not value.is_integer():
            return None, "Quantity must be a valid whole number."
        quantity = int(value)
        if quantity <= 0:
            return None, "Quantity must be greater than zero."
        return quantity, None
    try:
        numeric = float(str(value).strip())
    except (ValueError, TypeError):
        return None, "Quantity must be a valid whole number."
    if not numeric.is_integer():
        return None, "Quantity must be a valid whole number."
    quantity = int(numeric)
    if quantity <= 0:
        return None, "Quantity must be greater than zero."
    return quantity, None
```

A genuinely numeric Excel column reads back through `pandas.read_excel` as `numpy.int64` or
`numpy.float64` — but `_validate_row` iterates rows with `orders_df.iterrows()`, and each row
becomes an `object`-dtype `pandas.Series` spanning every differently-typed column at once. A boxed
numeric scalar pulled out of an `object`-dtype `Series` doesn't always cleanly match
`isinstance(value, (int, float))`. Rather than special-case every numpy scalar type (which would
mean importing numpy just for `isinstance` checks), `_parse_quantity` falls through to
`float(str(value).strip())` as a single catch-all: this handles `numpy.int64`, `numpy.float64`,
and genuine text like `"ten"` (which fails to parse, correctly reporting "must be a valid whole
number") through the exact same code path.

`_normalize_active` (lines 136–147) faces the identical problem for booleans specifically, because
`numpy.bool_` is *not* a subtype of Python's `bool`:

```python
def _normalize_active(value: object) -> bool | None:
    """Return True/False, or None if the active flag is unrecognized/blank."""
    if isinstance(value, bool):
        return value
    if _is_blank(value):
        return None
    text = str(value).strip().lower()
    if text in _ACTIVE_TRUE_STRINGS:
        return True
    if text in _ACTIVE_FALSE_STRINGS:
        return False
    return None
```

`isinstance(value, bool)` silently fails to catch a `numpy.bool_(True)` value read back from a
genuinely boolean Excel column. Rather than importing numpy just to also check
`isinstance(value, np.bool_)`, the function falls through to the same string-matching branch used
for literal `"TRUE"`/`"FALSE"` text cells — `str(numpy.bool_(True))` renders as `"True"`, which
lowercases to `"true"` and matches `_ACTIVE_TRUE_STRINGS`. One code path ends up handling real
Python `bool`, `numpy.bool_`, and spec-allowed strings identically, without a numpy import
anywhere in this file.

This is also where OV-003 and OV-005 each split into multiple sub-codes not named in the original
spec — `_normalize_active` returning `None` (an unrecognized active flag, not `True` or `False`)
produces `OV-003-INVALID_ACTIVE_FLAG`, a genuinely different fact from `OV-003-INACTIVE_SKU`
(recognized, but `False`). `_parse_date` (lines 100–110) returning `None` on either the order date
or the delivery date produces `OV-005-INVALID_ORDER_DATE` / `OV-005-INVALID_DELIVERY_DATE`,
distinct from `OV-005-DELIVERY_BEFORE_ORDER` (both dates parsed fine, but their *order* is wrong):

```python
def _parse_date(value: object) -> pd.Timestamp | None:
    """Return a normalized Timestamp, or None if value cannot be parsed as a date."""
    if isinstance(value, pd.Timestamp):
        return value
    try:
        parsed = pd.to_datetime(value)
    except (ValueError, TypeError):
        return None
    if pd.isna(parsed):
        return None
    return parsed
```

### Proof, not just prose: the tests behind all three parsers

Everything above is implementation and reasoning — `tests/test_order_validation.py` is what actually
pins each parser's behavior down, in three dedicated sections. Skipping straight to the callout
below without reading these would leave every claim in this Part resting on trust rather than
evidence.

`# --- OV-004 quantity type handling ---` (lines 204–229) proves `_parse_quantity` across every
type pandas can hand back, not just the clean-integer case already covered in Part 4/5:

```python
def test_non_numeric_quantity_raises_ov004_whole_number_message():
    result = validate_orders(_orders_df(_order_row(quantity="ten")), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert errors[0]["error_message"] == "Quantity must be a valid whole number."


def test_whole_number_float_quantity_is_accepted():
    result = validate_orders(_orders_df(_order_row(quantity=10.0)), _product_master_df())
    assert result["errors"] == []
    assert result["valid_orders"][0]["quantity"] == 10


def test_non_whole_float_quantity_raises_ov004():
    result = validate_orders(_orders_df(_order_row(quantity=10.5)), _product_master_df())
    errors = _errors_by_code(result, "OV-004")
    assert errors[0]["error_message"] == "Quantity must be a valid whole number."
```

Three genuinely different inputs, three different required outcomes: `"ten"` is text that will
never parse (falls through to the `float(str(value).strip())` branch and raises `ValueError`);
`10.0` is a whole-number float that *should* be accepted and silently coerced to the Python `int`
`10` (proving `_build_valid_order_row` stores a real `int`, not a lingering `float`); `10.5` is a
float that parses fine numerically but fails the `is_integer()` check. Without the middle test, a
future edit could "fix" `_parse_quantity` to reject *all* floats — technically simpler, but wrong,
since `pandas.read_excel` reads a genuinely whole-number Excel cell back as a `float` by default
whenever the column has no `NaN` values forcing an integer dtype.

`# --- OV-003 SKU sub-cases ---` (lines 166–201) is `_normalize_active`'s proof, and it's the one
section that most directly exercises the numpy-boxing problem this Part's main text describes:

```python
def test_inactive_sku_raises_ov003_inactive_sku():
    result = validate_orders(_orders_df(_order_row(sku="OFF-CHAIR-006")), _product_master_df())
    errors = _errors_by_code(result, "OV-003-INACTIVE_SKU")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "SKU exists but is marked inactive in product master."
    assert result["valid_orders"] == []


def test_invalid_active_flag_raises_ov003_invalid_active_flag():
    result = validate_orders(_orders_df(_order_row(sku="OFF-DESK-007")), _product_master_df())
    errors = _errors_by_code(result, "OV-003-INVALID_ACTIVE_FLAG")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "SKU active status is not valid in product master."


def test_active_flag_string_true_false_normalize_correctly():
    product_master = pd.DataFrame(
        [
            {"sku": "A-001", "product_name": "Widget A", "category": "Test", "active": "TRUE"},
            {"sku": "B-002", "product_name": "Widget B", "category": "Test", "active": "FALSE"},
        ]
    )
    result = validate_orders(
        _orders_df(
            _order_row(order_id="SO-2026-001", sku="A-001"),
            _order_row(order_id="SO-2026-002", sku="B-002"),
        ),
        product_master,
    )
    assert _errors_by_code(result, "OV-003-INACTIVE_SKU") == [
        error for error in result["errors"] if error["row_number"] == 3
    ]
    assert len(result["valid_orders"]) == 1
```

Look back at this test file's own `_product_master_df()` helper (near the top of the file,
`tests/test_order_validation.py:16-24`) — `"OFF-DESK-007"` is seeded there with
`"active": "maybe"`, a string that's neither a recognized true-string nor false-string. That's not
incidental test data; it's the fixture deliberately carrying the exact input
`test_invalid_active_flag_raises_ov003_invalid_active_flag` needs, so `_normalize_active` falls
through every branch and returns `None`. The third test is the one that actually exercises this
Part's numpy-boxing discussion end to end: a genuinely string-typed Excel column (`"TRUE"`/`"FALSE"`
text, the same shape a real spreadsheet author might type) has to normalize to real booleans for
row 2 (`A-001`) to end up valid and row 3 (`B-002`) to end up `OV-003-INACTIVE_SKU` — proving the
string-matching fallback branch, not just the `isinstance(value, bool)` fast path.

`# --- OV-005 date parseability ---` (lines 232–248) closes out the set, covering `_parse_date`:

```python
def test_unparseable_order_date_raises_ov005_invalid_order_date():
    result = validate_orders(_orders_df(_order_row(order_date="not a date")), _product_master_df())
    errors = _errors_by_code(result, "OV-005-INVALID_ORDER_DATE")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Order date is not a valid date."


def test_unparseable_delivery_date_raises_ov005_invalid_delivery_date():
    result = validate_orders(
        _orders_df(_order_row(requested_delivery_date="not a date")), _product_master_df()
    )
    errors = _errors_by_code(result, "OV-005-INVALID_DELIVERY_DATE")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Requested delivery date is not a valid date."
```

These two are a deliberately parallel pair, not one test doing double duty — `order_date` and
`requested_delivery_date` are parsed by the exact same `_parse_date` function, but each field has
its own sub-code (`OV-005-INVALID_ORDER_DATE` vs. `OV-005-INVALID_DELIVERY_DATE`) and its own
message. A single shared test could only prove the function parses *a* date field; testing both
separately proves the caller wires the *correct* sub-code to each field, which is a fact about
`_validate_row`'s call sites, not about `_parse_date` itself.

> **Python language — Multi-exception catch as defensive coercion:** `except (ValueError,
> TypeError):` names exactly the two exception types a failed numeric or date conversion can
> raise — nothing broader. A bare `except:` (or `except Exception:`) would also silently swallow
> an unrelated bug elsewhere in the same `try` block (a typo'd variable name inside the block would
> raise `NameError`, and a blanket catch would misreport that as "bad quantity data" instead of
> letting it surface as the programming error it actually is). Naming the exact exception types is
> what keeps this function's defensiveness scoped to "the conversion itself failed" — the same
> discipline behind Tutorial 01's `MissingColumnsError`, applied here to catching narrowly instead
> of raising narrowly.

**Checkpoint:** `_parse_quantity` and `_normalize_active` both use "convert to string and
pattern-match" as a fallback for types that don't cleanly match `isinstance` checks. Is this an
elegant unification or a code smell masking a type-system gap? What would the numpy-aware version
look like, and is it worth the added import/coupling?

<details>
<summary>Reveal answer</summary>

It's a defensible unification, not a smell, specifically because the string-conversion fallback
handles the numpy-scalar case and the genuinely-malformed-text case (`"ten"`, an unrecognized
active string) through the *same* logic rather than as two separate branches — there's no
duplicated "numpy path" and "string path" to keep in sync. The numpy-aware version would add
`import numpy as np` and extra `isinstance(value, (np.integer, np.floating))` /
`isinstance(value, np.bool_)` branches before the fallback — more explicit about *why* the
fallback exists, but adds a dependency this file otherwise doesn't need (pandas already transitively
depends on numpy, so there's no new install, but it's still a new coupling point this module would
carry for a case the string fallback already handles correctly). It's worth doing only if the
string-conversion path ever turned out to mis-handle some numpy edge case the isinstance check
wouldn't have — nothing in `tests/test_order_validation.py` currently demonstrates that gap.
</details>

**Checkpoint:** Malformed quantity and malformed dates both convert to business-readable errors
instead of raising. What's the actual boundary between "this is data quality the business user
needs to fix" (return a `ValidationErrorRow`) and "this is a programming bug" (let it raise) — and
does that boundary hold if the input file format changes (e.g., CSV instead of `.xlsx`)?

<details>
<summary>Reveal answer</summary>

The boundary is: *input the module is designed to receive, in a shape it should expect to see
regularly* (a cell with unexpected but plausible content — text where a number was expected, an
unparseable date string) is data quality, handled by returning an error message; *anything that
indicates the code's own logic is wrong* (an `AttributeError` from calling a method that doesn't
exist, an `IndexError` from an off-by-one) is a programming bug, left to raise and crash loudly so
it gets fixed. This boundary is about the *nature of the failure*, not the file format — a CSV
source would still hand back Python-native strings/numbers/`None` for every cell (no numpy-scalar
boxing issue specific to Excel/pandas `object`-dtype rows), so `_parse_quantity`'s numpy fallback
branch might simply never trigger with CSV input, but its "convert to string, try to parse, catch
`ValueError`/`TypeError`" logic would still correctly classify genuinely malformed text as a data
error either way. The classification boundary is format-independent; only *which* code path within
the defensive parser actually gets exercised would shift.
</details>

**Checkpoint:** OV-003 and OV-005 were each split into sub-codes
(`OV-003-UNKNOWN_SKU`/`OV-003-INACTIVE_SKU`/`OV-003-INVALID_ACTIVE_FLAG`; three `OV-005-*`
variants) that don't exist in the original spec's rule numbering. Is inventing sub-codes a
deviation from the spec, or a legitimate refinement of it?

<details>
<summary>Reveal answer</summary>

It's a legitimate refinement, not a deviation, because every sub-code still maps back to exactly
one spec-named rule (OV-003 or OV-005) and none of them changes what triggers an error or what
severity it carries — the spec itself already distinguishes "SKU does not exist" from an
active/inactive distinction in its own product-master column description ("active: boolean/string"
in §5), which is the seed this split grew from. What would make a future reviewer trust this
versus see it as scope drift: the sub-codes are all still `Error` severity (matching the spec's
own OV-003/OV-005 table entries), none of them introduces a *new* business outcome the spec never
described, and `error_message` text stays business-readable and specific rather than adding
information the spec didn't authorize. A genuine deviation would look different — e.g., inventing
an `OV-003-DISCONTINUED` sub-code with its own new severity or business meaning the spec never
mentioned at all.
</details>

**Try it yourself:** In a Python shell, run
`from src.order_validation import _parse_quantity; import numpy as np; print(_parse_quantity(np.float64(10.0))); print(_parse_quantity(np.int64(5))); print(_parse_quantity("ten"))`
and confirm all three go through the same fallback branch to produce a correct result (or a correct
error) — none of them hit the `isinstance(value, (int, float))` branch directly, since numpy
scalars aren't Python `int`/`float` instances.

## Part 7 — Summary counts and double-counting

Open [`src/order_validation.py`](../../../src/order_validation.py) lines 396–411 again, focused
this time on the counting logic:

```python
    invalid_row_numbers: set[int] = set()

    for position, (_, row) in enumerate(orders_df.iterrows()):
        row_number = position + 2
        row_errors = _validate_row(row, row_number, duplicate_order_ids, product_master_lookup)
        all_errors.extend(row_errors)

        has_error_severity = any(error["severity"] == "Error" for error in row_errors)
        if has_error_severity:
            invalid_row_numbers.add(row_number)
        else:
            valid_orders.append(_build_valid_order_row(row, product_master_lookup))
    ...
    total_orders = len(orders_df)
    invalid_orders = len(invalid_row_numbers)
    duplicate_orders = sum(1 for error in all_errors if error["error_code"] == "OV-002")
    invalid_skus = sum(1 for error in all_errors if error["error_code"].startswith("OV-003"))
```

`duplicate_orders`, `invalid_skus`, and `missing_field_count` are each simple counts of matching
`ValidationErrorRow` entries — straightforward `sum(1 for error in ... if ...)` expressions. But
`invalid_orders` is computed completely differently: it's `len(invalid_row_numbers)`, the size of a
`set` built during the per-row loop, one entry added per row that has *at least one* Error-severity
finding — never a sum of the category counts above it.

This isn't a stylistic choice; summing categories would produce the wrong number whenever a single
row triggers more than one rule. `tests/test_order_validation.py:270-284` constructs exactly that
overlap:

```python
def test_invalid_orders_counts_distinct_rows_not_sum_of_categories():
    df = _orders_df(
        # one row with BOTH a duplicate order_id AND an unknown SKU
        _order_row(order_id="SO-DUP", sku="UNKNOWN-SKU"),
        _order_row(order_id="SO-DUP", customer_name="Other Customer"),
        _order_row(),  # clean row
    )
    result = validate_orders(df, _product_master_df())
    # 2 rows share order_id SO-DUP (both invalid); the unknown SKU is on one of them already
    assert result["summary"]["total_orders"] == 3
    assert result["summary"]["invalid_orders"] == 2
    assert result["summary"]["valid_orders"] == 1
    assert result["summary"]["duplicate_orders"] == 2
    assert result["summary"]["invalid_skus"] == 1
```

Row 1 has both a duplicate `order_id` (OV-002) and an unknown SKU (OV-003) — two separate error
records. If `invalid_orders` were computed as `duplicate_orders + invalid_skus` (`2 + 1 = 3`), the
summary would claim 3 invalid rows out of only 3 total rows, leaving zero valid — but the test's
third row is genuinely clean. The correct answer, `2`, comes from asking "how many *distinct*
`row_number`s have at least one Error," which the `set` naturally answers regardless of how many
different rules any one of those rows happens to violate.

> **Data structures — Set for distinct-element deduplication:** A Python `set` can never contain
> the same value twice — adding `row_number` 2 to a set that already contains 2 is a no-op, not a
> second entry. That property is exactly what "count of distinct rows with at least one problem"
> needs: add every offending row number to a set as you find problems (regardless of how many
> problems that row has), then take the set's size at the end. This is the standard tool for "how
> many unique X are there across possibly-overlapping groups," the same shape as counting unique
> visitors across multiple page-view events, or unique users across multiple error log lines.

**Checkpoint:** `invalid_orders` is deliberately computed as a distinct-row count rather than
summed from `duplicate_orders + invalid_skus + missing_field_count`, specifically to avoid
double-counting a row that fails multiple rules. What other summary/KPI fields in this project
(`AllocationSummary`, `PaymentAgingSummary`) might have the same double-counting risk once Phase
4/5 are implemented, and how would you audit for it systematically instead of catching it ad hoc?

<details>
<summary>Reveal answer</summary>

Any summary field described as "count of X that have *at least one* Y" is a double-counting
candidate whenever a single X can have multiple Y's. Looking at `src/contracts.py`:
`AllocationSummary.low_stock_sku_count` ("how many SKUs are low on stock") is safe only if a SKU
can't be "low stock" more than once per computation — likely fine, since it's a per-SKU state, not
a per-event count. `PaymentAgingSummary.high_priority_count` is a closer call: if a future
`payment_aging.py` computes priority from *multiple* independent signals (e.g., both "very overdue"
and "very large amount" could each independently suggest high priority), counting invoices that
satisfy *either* signal needs the same distinct-set treatment `invalid_orders` uses, not a sum of
"count meeting signal A" + "count meeting signal B." A systematic audit: for every summary field,
ask "can the underlying detail rows this field summarizes share a many-to-one relationship with
whatever this field is nominally counting?" — if yes, verify the implementation uses a distinct-set
count, not a per-category sum, the same check this checkpoint just walked through for
`invalid_orders`.
</details>

**Try it yourself:** Run `uv run pytest tests/test_order_validation.py -k double_counting -v` (no
match — the test function is actually named
`test_invalid_orders_counts_distinct_rows_not_sum_of_categories`; run
`uv run pytest tests/test_order_validation.py -k distinct_rows_not_sum -v` instead) and read the
assertion that would fail if `invalid_orders` were computed as a naive sum: work out by hand what
`duplicate_orders + invalid_skus + missing_field_count` would equal for this test's data, and
confirm it's different from the correct `invalid_orders` value the test asserts.

## Part 8 — Deterministic error ordering

Open [`src/order_validation.py`](../../../src/order_validation.py) lines 47–63 and 339–348:

```python
# Fixed rule ordering used to sort the final error list deterministically.
_RULE_ORDER = {
    "OV-001": 0,
    "OV-002": 1,
    "OV-003-UNKNOWN_SKU": 2,
    "OV-003-INACTIVE_SKU": 2,
    "OV-003-INVALID_ACTIVE_FLAG": 2,
    "OV-004": 3,
    "OV-005-INVALID_ORDER_DATE": 4,
    "OV-005-INVALID_DELIVERY_DATE": 4,
    "OV-005-DELIVERY_BEFORE_ORDER": 4,
    "OV-006": 5,
    "OV-007": 6,
}

_OV001_FIELD_ORDER = {field: index for index, (field, _label) in enumerate(OV001_REQUIRED_FIELDS)}
```

```python
def _sort_key(error: ValidationErrorRow) -> tuple[int, int, int]:
    rule_rank = _RULE_ORDER.get(error["error_code"], len(_RULE_ORDER))
    field_rank = 0
    if error["error_code"] == "OV-001":
        field = next(
            (f for f, label in OV001_REQUIRED_FIELDS if error["error_message"].startswith(label)),
            None,
        )
        field_rank = _OV001_FIELD_ORDER.get(field, len(OV001_REQUIRED_FIELDS))
    return (error["row_number"], rule_rank, field_rank)
```

`_validate_row` already evaluates rules OV-001 through OV-007 in source order, top to bottom, so
`all_errors` mostly comes out in the right order *by accident* — building the list row by row,
rule by rule, in the sequence the code happens to be written. `validate_orders` doesn't trust that
accident: `all_errors.sort(key=_sort_key)` (line 407) is an explicit final pass that guarantees the
order regardless of how `_validate_row`'s internals are structured.

`_sort_key` returns a 3-element tuple — `(row_number, rule_rank, field_rank)` — and Python sorts
tuples lexicographically: first by `row_number`, and only for ties on `row_number` does it look at
`rule_rank`, and only for ties on *both* does it fall back to `field_rank` (which only matters
within OV-001, where multiple missing fields on the same row need their own stable sub-order,
tying directly back to Part 4's fixed-field-order decision).

> **Algorithms — Composite-key stable sort:** Sorting by a tuple of several fields, most-significant
> first, is the standard technique for "sort by A, then by B only when A ties, then by C only when
> both tie" — the same idea as an `ORDER BY row_number, rule_rank, field_rank` clause in SQL, or a
> multi-column sort in a spreadsheet. Python's `list.sort()` (and `sorted()`) is guaranteed
> *stable* — elements that compare equal keep their original relative order — which matters here:
> two different OV-003 sub-codes both map to the same `rule_rank` (`2`), so their relative order
> when both apply to the same row is left to whatever order `_validate_row` originally produced
> them in, not scrambled by the sort.

**Checkpoint:** `test_errors_are_ordered_by_row_then_rule_then_field` locks in an ordering that
wasn't explicitly required by the spec — it emerged from wanting stable test assertions and a
predictable future UI table. Is testing an implementation choice like this (rather than a
spec-mandated rule) good practice or over-specification? What would you lose if this test were
deleted?

<details>
<summary>Reveal answer</summary>

It's good practice, not over-specification, because the alternative isn't "no order" — a list has
*some* order no matter what, and the only question is whether that order is a documented, tested
guarantee or an unexamined accident of implementation. `context/code-standards.md` doesn't mandate
a specific ordering, but it does implicitly need *some* deterministic ordering for every other test
in the file that asserts on `result["errors"]` by position or by filtering — those tests are only
reliable because the order is guaranteed, not incidental. Deleting this specific test wouldn't
break anything today (the `_sort_key`/`.sort()` call would still run), but it would remove the one
piece of proof that a future refactor of `_validate_row`'s internal rule sequence — done for an
unrelated reason, like reorganizing code for readability — can't silently change output order
without a test catching it. That's exactly the risk this tutorial's pre-study primer named:
ordering that's "however the loop happened to produce it" is invisible until something downstream
(a UI snapshot test, a flaky assertion) breaks for a reason nobody can immediately explain.
</details>

**Try it yourself:** Run `uv run pytest tests/test_order_validation.py -k ordered -v` and read
`test_errors_are_ordered_by_row_then_rule_then_field` (`tests/test_order_validation.py:299-310`).
Then, in a Python shell, manually construct two `ValidationErrorRow` dicts with the same
`row_number` but error codes `"OV-006"` and `"OV-002"` (in that order in a list), call
`_sort_key` on each, and confirm sorting the list by `_sort_key` reorders them to `OV-002` first —
proving the sort, not source order, controls the final sequence.

## Part 9 — Tests as rule documentation

`01_demo_order_validation.md` §12 lists eight test cases as its own minimum bar. Open
[`tests/test_order_validation.py`](../../../tests/test_order_validation.py) and compare its section
comments to that table:

```python
# --- Spec section 12 test cases -----------------------------------------


def test_missing_customer_name_raises_ov001():
    result = validate_orders(_orders_df(_order_row(customer_name="")), _product_master_df())
    errors = _errors_by_code(result, "OV-001")
    assert len(errors) == 1
    assert errors[0]["error_message"] == "Customer name is missing."
    assert errors[0]["severity"] == "Error"
    assert result["valid_orders"] == []


def test_duplicate_order_id_flags_every_row():
    df = _orders_df(
        _order_row(order_id="SO-2026-005"),
        _order_row(order_id="SO-2026-005", customer_name="Formosa Industrial Group"),
    )
    result = validate_orders(df, _product_master_df())
    errors = _errors_by_code(result, "OV-002")
    assert {error["row_number"] for error in errors} == {2, 3}
    assert result["summary"]["duplicate_orders"] == 2
    assert result["valid_orders"] == []
```

The first eight test functions map one-to-one onto the spec's own §12 table — every row in that
table has a corresponding, identically-scoped test. Notice `test_duplicate_order_id_flags_every_row`
asserts `{error["row_number"] for error in errors} == {2, 3}` — *both* rows sharing the duplicate ID
get flagged, not just the second one to appear, which is itself a small design decision the spec's
prose doesn't spell out (a duplicate is a fact about the *pair*, not a property of whichever row
happened to arrive second). But the file has far more than eight tests
(31 total), organized into named sections that each correspond to one of the decisions this
tutorial has walked through: `# --- Multiple errors per row / field-level OV-001 ---` (Part 4),
`# --- Blank-field skip rule extends to OV-002 and OV-006 ---` (Part 5), `# --- Summary counting
semantics, including overlapping violations ---` (Part 7), `# --- Deterministic error ordering
---` (Part 8), and so on. Each section exists because a decision was made during `/architect`
planning that the spec itself doesn't fully settle — and the test is the artifact that proves the
decision actually holds in the running code, not just in `explanation.md`'s prose.

This makes the test file a genuinely different kind of document than `explanation.md`:
`explanation.md` argues *why* a decision was made; the test *proves* the decision is implemented
correctly, and will keep proving it on every future change. A reader who wants to know "does OV-007
really stay a Warning and never disqualify a row?" doesn't have to trust the explanation prose —
`test_missing_payment_terms_is_warning_only_and_row_stays_valid` is executable, falsifiable
evidence, re-checked every time `uv run pytest` runs.

**Checkpoint:** `tests/test_order_validation.py` is organized into commented sections that mirror
this tutorial's Parts, not just the spec's §12 table. What does a test suite that documents
*decisions* (not just *requirements*) buy a future contributor that a suite testing only the
spec's own listed cases wouldn't?

<details>
<summary>Reveal answer</summary>

The spec's §12 table only proves the eight cases it explicitly names — it says nothing about
whether a row can have multiple errors, whether blank fields double-report, or how ties in
summary counts resolve, because the spec text itself never fully resolves those questions (that's
exactly why `/architect` planning had to make and record a decision for each one). A test suite
limited to §12 would leave every one of those decisions undocumented-in-code — a future
contributor could "fix" the blank-field skip rule into a double-report, or resum `invalid_orders`
from category counts, and nothing would fail, because nothing tests the decision that was actually
made. Organizing tests by decision (with a comment naming the decision, mirroring `explanation.md`'s
own structure) means every non-obvious design choice has a permanent, executable guard — the test
suite becomes the single place a future reader can trust to answer "is this specific behavior
intentional, and is it still true?"
</details>

**Try it yourself:** Run `uv run pytest tests/test_order_validation.py -v` and count the total
number of tests reported. Then count how many test function names correspond directly to a
`01_demo_order_validation.md` §12 row versus how many exist purely to lock in a decision from
`explanation.md`. The ratio is itself evidence for how much of this module's real complexity lives
in resolving spec ambiguity, not in the spec's literal text.

## Full data flow: one deliberately messy order row, start to finish

Trace a single row built to hit almost every rule at once — not from the existing test suite
verbatim, but constructed the same way `_order_row(**overrides)` in
`tests/test_order_validation.py:27-42` builds test rows:

```python
{
    "order_id": "SO-2026-050",
    "order_date": date(2026, 7, 10),
    "customer_name": "",                          # blank
    "customer_region": "Hong Kong",
    "sku": "MED-LENS-999",                         # not in product master
    "quantity": "ten",                             # non-numeric
    "requested_delivery_date": date(2026, 7, 5),   # earlier than order_date
    "priority": "Urgent",                          # not a controlled value
    "payment_terms": "",                           # blank
}
```

1. **Loader column check.** `load_orders(file)` (`src/order_validation.py:71-75`) calls
   `load_excel` then `validate_required_columns(df, ORDERS_REQUIRED_COLUMNS, "orders file")`. Every
   required column is present in this row's file — only *values* are wrong, not the shape — so
   loading succeeds and returns a normal DataFrame (Part 2).
2. **Row normalization begins.** `validate_orders` (`src/order_validation.py:396-397`) enters its
   loop; this row lands at `position=0`, so `row_number = 2` (Excel's 1-indexed header row is row
   1; the first data row is row 2, matching what a spreadsheet user would actually see). This exact
   `+2` offset — not `+1`, not raw zero-based `position` — is what
   `test_row_number_is_excel_visible_row_starting_at_two` (`tests/test_order_validation.py:289-293`)
   locks in: two consecutive bad rows must report `row_number` 2 and 3, never 0 and 1, or a person
   fixing the spreadsheet would be sent to the wrong physical row every time.
3. **`_validate_row` runs OV-001** (`src/order_validation.py:204-209`): iterating
   `OV001_REQUIRED_FIELDS`, only `customer_name` is blank among the eight required fields
   (`quantity` is `"ten"`, not blank — a *type* problem, not a *presence* problem, so OV-001
   doesn't flag it; that's Part 5's blank-field skip rule cutting the other way — a non-blank
   but malformed value skips OV-001 and falls to its own type rule instead). One error appends:
   `{"row_number": 2, "error_code": "OV-001", "error_message": "Customer name is missing.",
   "severity": "Error", ...}`.
4. **OV-002** (`src/order_validation.py:219-222`): `order_id` `"SO-2026-050"` isn't blank and isn't
   in `duplicate_order_ids` (a single-row example has no duplicates) — no error.
5. **OV-003** (`src/order_validation.py:225-262`): `sku` isn't blank, so the lookup runs.
   `"MED-LENS-999"` isn't a key in `product_master_lookup` — `product is None` — appending
   `OV-003-UNKNOWN_SKU`: `"SKU does not exist in product master."`.
6. **OV-004** (`src/order_validation.py:264-269`): `quantity` isn't blank, so `_parse_quantity("ten")`
   runs (Part 6). It's not `bool`, not `int`/`float`, so it falls to `float(str("ten").strip())`,
   which raises `ValueError`, caught and converted to `(None, "Quantity must be a valid whole
   number.")`. That message becomes an `OV-004` error.
7. **OV-005** (`src/order_validation.py:271-313`): neither date is blank. `_parse_date(date(2026,
   7, 10))` and `_parse_date(date(2026, 7, 5))` both succeed (they're already `date`/`Timestamp`-
   compatible values, not malformed text) — no `INVALID_ORDER_DATE`/`INVALID_DELIVERY_DATE` errors.
   But `delivery_date_value (2026-07-05) < order_date_value (2026-07-10)` is `True`, so
   `OV-005-DELIVERY_BEFORE_ORDER` appends: `"Requested delivery date is earlier than order date."`.
8. **OV-006** (`src/order_validation.py:316-328`): `priority` isn't blank. `"Urgent"` is not in
   `VALID_PRIORITIES` (`{"High", "Normal", "Low"}`), so `OV-006` appends: `"Priority must be High,
   Normal, or Low."`.
9. **OV-007** (`src/order_validation.py:330-334`): `payment_terms` is blank — appends a `Warning`:
   `"Payment terms are missing."`. Unlike every error above, this one's `severity` is `"Warning"`,
   not `"Error"`.
10. **Back in `validate_orders`** (`src/order_validation.py:401-405`): `row_errors` now has 6
    entries — 5 `Error`, 1 `Warning`. `any(error["severity"] == "Error" for error in row_errors)`
    is `True`, so `row_number = 2` is added to `invalid_row_numbers`; `_build_valid_order_row` is
    never called for this row — it produces no `ValidOrderRow` at all.
11. **Summary counts.** After every row is processed, `invalid_orders = len(invalid_row_numbers)`
    includes this row exactly once, regardless of its 5 Error-severity findings (Part 7).
    `duplicate_orders` doesn't count it (no `OV-002`); `invalid_skus` counts it once (its one
    `OV-003-UNKNOWN_SKU` entry); `missing_field_count` counts it once (its one `OV-001` entry).
12. **Deterministic ordering.** `all_errors.sort(key=_sort_key)` (Part 8) places this row's six
    errors in the order `OV-001, OV-003-UNKNOWN_SKU, OV-004, OV-005-DELIVERY_BEFORE_ORDER, OV-006,
    OV-007` — exactly `_RULE_ORDER`'s declared rank sequence (`0, 2, 3, 4, 5, 6`), regardless of
    which order `_validate_row`'s internal checks happened to run in.
13. **Final envelope.** `validate_orders` returns
    `{"summary": {...}, "valid_orders": [], "errors": [six error dicts]}` — this row contributes
    nothing to `valid_orders`, six entries to `errors`, and exactly `+1` to `invalid_orders`
    (never `+5`).

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Open `tests/test_order_validation.py:299-310`
(`test_errors_are_ordered_by_row_then_rule_then_field`). Before reading the assertion, look only at
the two input rows it constructs (`_order_row(order_id="SO-2026-100", priority="Urgent",
customer_name="")` and `_order_row(order_id="SO-2026-101", quantity=0)`) and write down, from
memory of Parts 1–8, every error you predict each row will produce, in what order. Then read
`ordered_pairs`'s expected value and check your prediction.

<details>
<summary>Hint</summary>

Row 1 has two problems (blank `customer_name`, invalid `priority`) — walk both through OV-001 and
OV-006 the way the full end-to-end trace above did. Row 2 has one problem (`quantity=0`, which
`_parse_quantity` treats differently from a non-numeric value — check the `quantity <= 0` branch,
not the `float()`-parse-failure branch). Use `_RULE_ORDER`'s rank numbers to predict the final
sequence across both rows.
</details>

**Challenge 2 — Extend** (20–30 min): Design (don't implement) a new rule, `OV-008`, that flags an
order line whose `sku` is valid and active but whose `quantity` exceeds some large sanity-check
threshold (e.g., 10,000 units) — a plausible "did someone add an extra zero" data-quality check not
in the current spec. Write out: the exact `error_code` string and whether it needs sub-codes; the
`severity` (Error or Warning, and why); which blank-field guard(s) it needs, following Part 5's
pattern; whether it changes any `ValidationSummary` field, and if so, whether that field needs a
distinct-count or a simple sum (Part 7); and the names (not the bodies) of at least three tests it
would need, following the section-comment convention from Part 9.

<details>
<summary>Hint</summary>

Think about where in `_validate_row`'s sequence this check would run relative to OV-004 (it needs
`quantity_value`, which OV-004's block already parses) — does it need to be a completely separate
check, or could it reasonably extend OV-004 instead of becoming a new rule number? Either answer is
defensible; the challenge is arguing for one and naming the failure mode of the other.
</details>

**Challenge 3 — Break and fix** (30–45 min): Imagine `invalid_orders` were computed as
`duplicate_orders + invalid_skus + missing_field_count` instead of
`len(invalid_row_numbers)`. Explain, in your own words, exactly which test in
`tests/test_order_validation.py` would fail first, and predict the *specific wrong number* it
would compute for that test's fixture (don't just say "it would be wrong" — compute the actual
value the buggy formula would produce). Then check your prediction by temporarily making that
change in `src/order_validation.py`, running `uv run pytest tests/test_order_validation.py -v`,
and comparing the actual failure output to your prediction. Revert the change afterward.

<details>
<summary>Hint</summary>

`test_invalid_orders_counts_distinct_rows_not_sum_of_categories`
(`tests/test_order_validation.py:270-284`) is built specifically to catch this bug — walk through
its three-row fixture and compute `duplicate_orders + invalid_skus + missing_field_count` by hand
before running anything, the same way Part 7 walked through why `2 + 1 = 3` is wrong when the
correct answer is `2`.
</details>

For deeper exploration, `docs/plan/phase-3-order-validation-core/ai-discussion-topics.md` has 10
prompts covering spec-contradiction resolution, rule granularity, defensive parsing trade-offs,
summary statistics, and testing philosophy. Feed them to an LLM *after* forming your own answer
first — the gap between what you thought and what you learn is where understanding lands.
