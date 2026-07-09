# Phase 3 /architect Session — Decisions

Session: `/architect` invoked directly (not via plan mode) for Phase 3 (Order Validation Core) of
the Sales Admin Automation Toolkit, scoped explicitly to planning `src/order_validation.py` and
`tests/test_order_validation.py` only — no UI, FastAPI, report export, or allocation logic. The
session opened with a required-reading pass (`context/project-overview.md`, `architecture.md`,
`code-standards.md`, `build-plan.md`, `progress-tracker.md`, `01_demo_order_validation.md`,
`CONTEXT.md`, plus the existing `src/contracts.py`, `src/excel_io.py`, `tests/contract_fixtures.py`,
`src/sample_data.py`) before any question was asked. Seven decisions were surfaced via
`AskUserQuestion`; the resulting plan was then corrected with six more refinements during the
user's review, all accepted without a rejected draft.

---

## 1. Valid Order / severity / duplicate / row-number vocabulary

**What it is:** Before any implementation decision, four terms were pinned down: "Valid Order"
means an order *line* (no order-header concept — each row is independent); a row is valid only if
it has zero **Error**-severity violations (Warning-only rows still count as valid, unless a later
decision says otherwise); a duplicate `order_id` flags **every** row sharing that ID, not just the
2nd occurrence onward; `row_number` means the **visible Excel row number** (header = row 1, first
data row = row 2), not a 0-indexed DataFrame position.

**Why this and not the alternatives:** "Only the 2nd+ occurrence is a duplicate" was explicitly
rejected because neither row is safely identifiable as the canonical original without an external
source of truth — flagging only one row would imply the other is trustworthy, which isn't a claim
the data supports. A 0-indexed `row_number` was rejected because the field exists specifically so
an operations user can find and fix the row in the Excel file they're looking at; internal
DataFrame indexing is an implementation detail that would force the user to do arithmetic to find
their own data.

---

## 2. OV-003 splits into `UNKNOWN_SKU` and `INACTIVE_SKU`

**What it is:** The spec files "SKU not found" and "SKU found but inactive" under one rule number
(OV-003) with one generic example message. These were treated as two distinct real-world problems
and given separate codes: `OV-003-UNKNOWN_SKU` ("SKU does not exist in product master.") and
`OV-003-INACTIVE_SKU` ("SKU exists but is marked inactive in product master."). A third case
discovered later in the session — an unparseable/unrecognized `active` value — got its own code too:
`OV-003-INVALID_ACTIVE_FLAG`.

**Why:** "SKU doesn't exist" and "SKU exists but was deliberately discontinued" call for different
operational responses — the first might mean a typo in the order, the second might mean the
customer is ordering something the company stopped selling. A single generic message can't
distinguish these for the person fixing the row.

---

## 3. Multiple validation errors per row, with field-level OV-001 granularity

**What it is:** Every rule (OV-001 through OV-007) is evaluated independently against every row.
A single row can accumulate multiple `ValidationErrorRow` entries — the same `row_number` can
appear more than once in the errors table. For OV-001 specifically, one error is emitted **per
missing required field**, not one combined "some fields are missing" message:

```
Customer name is missing.
Requested delivery date is missing.
Quantity is missing.
```

**Why this and not "first failure wins":** "First failure wins" — stopping at the first violated
rule per row — was explicitly considered and rejected. It hides useful repair information and
forces a sales-admin user into multiple upload/fix cycles: fix the one reported error, re-upload,
discover a second error that was silently suppressed the first time, fix that, re-upload again. The
chosen approach costs a longer error table in exchange for a user being able to fix a row completely
in one pass.

---

## 4. Result envelope: named dict, not a positional tuple — defined locally, not in `contracts.py`

**What it is:** `validate_orders()` returns a single dict with named keys, not a positional tuple:

```python
class OrderValidationResult(TypedDict):
    summary: ValidationSummary
    valid_orders: list[ValidOrderRow]
    errors: list[ValidationErrorRow]

def validate_orders(
    orders_df: pd.DataFrame,
    product_master_df: pd.DataFrame,
) -> OrderValidationResult: ...
```

`OrderValidationResult` itself is defined **inside `order_validation.py`**, not added as a 14th
family to `src/contracts.py`.

**Why a dict over a tuple:** The spec's own §11 sketch (`tuple[pd.DataFrame, pd.DataFrame]`) was
considered and rejected. A positional 3-tuple is harder to misuse-proof — `result[0]` vs. `result[1]`
carries no self-documentation, and a future caller could easily transpose `valid_orders` and `errors`
without a type error. `result["summary"]`/`result["valid_orders"]`/`result["errors"]` reads correctly
at every call site.

**Why local, not in `contracts.py`:** `src/contracts.py`'s 13 families are described in
`context/architecture.md` as "table shapes" — each one maps directly to a future UI
table/KPI/chart, per the Field Scope Boundary. `OrderValidationResult` isn't a table shape; it's a
bundling envelope composed entirely of existing contract types, with no new business-facing fields
of its own. Adding it to `contracts.py` would start diluting that file's meaning from "stable output
families" into "anything a module happens to return." This also sets an explicit precedent: Phase 4
(`inventory_allocation.py`) and Phase 5 (`payment_aging.py`) are expected to define their own local
result envelopes the same way, rather than accumulating wrapper types in `contracts.py`.

---

## 5. Malformed quantity and date values convert to business-readable errors, never raise

**What it is:** Input that fails to match the expected type doesn't crash the module — it becomes a
specific `ValidationErrorRow`:

- Blank/`NaN` quantity → `OV-001` ("Quantity is missing.")
- Present but non-numeric quantity (e.g. `"ten"`) → `OV-004` ("Quantity must be a valid whole
  number.")
- Zero, negative, or non-whole quantity → `OV-004` (distinct messages for "must be greater than
  zero" vs. "must be a valid whole number")
- Whole-valued floats (`10.0`) are accepted and coerced to `int`
- Blank date → `OV-001`; present-but-unparseable date (e.g. `"n/a"`, `"July"`) → a new `OV-005-*`
  sub-code with a message distinct from the delivery-before-order comparison

**Why:** `context/code-standards.md` requires technical parsing issues to convert into
business-readable messages at the module boundary — this was treated as a hard requirement, not a
nice-to-have, even though the spec's own §12 test cases never mention malformed strings. The
alternative ("assume Excel input is always clean, let a bad value raise") was explicitly rejected:
real spreadsheet data will have `"ten"`-style entry mistakes, and letting the module crash on them
would violate the boundary rule for the sake of narrower initial scope.

---

## 6. `active` column normalized permissively (real `bool` or common truthy/falsy strings)

**What it is:** The product master's `active` column, spec'd as "boolean/string," is normalized
case-insensitively: `True`/`"true"`/`"yes"`/`"y"`/`"1"` → active; `False`/`"false"`/`"no"`/`"n"`/`"0"`
→ inactive. Anything else (blank, `"maybe"`, unrecognized text) is **not** defaulted to active — it
raises `OV-003-INVALID_ACTIVE_FLAG` instead.

**Why not "assume real Python `bool` only":** The narrower alternative — trusting pandas always
reads the column as proper `bool` dtype, matching how the project's own `sample_data.py` currently
writes it — was rejected because the spec explicitly documents the column as possibly-text, and a
real-world `product_master.xlsx` (not just this project's generated sample) could have the column
formatted as text in Excel. **Why not default unrecognized values to active:** defaulting to active
would silently hide a real product-master data-quality problem behind an SKU that looks fine to
downstream validation — the whole point of a validation tool is to surface exactly this kind of
ambiguity, not paper over it.

---

## 7. Resolving a real contradiction in the spec: OV-001 vs. OV-007 on `payment_terms`

**What it is:** Rule OV-001's required-fields list includes `payment_terms` (implying Error
severity, since every other OV-001 example is `Error`). Rule OV-007 separately covers the *same*
blank-`payment_terms` case with its own code and an explicit `Warning` severity in the spec's own
example table. Resolved by removing `payment_terms` from OV-001's field set entirely — a blank
`payment_terms` produces exactly **one** error: `OV-007`, severity `Warning`, message "Payment
terms are missing." It is never also an `OV-001` Error.

**Why this and not "follow both rules literally":** Emitting both an `OV-001` Error and an `OV-007`
Warning for the same blank cell was explicitly considered and rejected, because it's internally
contradictory given the earlier decision (#1) that Warning-only rows stay in `valid_orders`. A row
with only a blank `payment_terms` would be simultaneously "valid" (per the Warning-doesn't-disqualify
rule) and "invalid" (per OV-001's Error severity) — the same row can't be both. OV-007 was kept as
the exclusive owner of this field because it's the more specific, deliberately-authored rule (its
own number, its own worked example, an explicit non-Error severity), while OV-001's required-fields
list reads as the more generic, likely-copy-pasted list where the conflict actually originated.

---

## 8. Plan-review refinements (accepted without a rejected draft)

The plan was presented once and approved with six specific additions rather than being rejected and
rewritten:

1. **Blank-field skip extended to OV-002 and OV-006.** The original plan only specified this skip
   for OV-003/004/005; the review caught that a blank `order_id` would otherwise still trigger a
   duplicate check, and a blank `priority` would otherwise still fail the controlled-value check —
   both already covered by OV-001, so flagging them again under a second rule number is redundant
   noise, not additional information.
2. **Deterministic error ordering** — `errors` sorted by `(row_number, rule_order,
   ov001_field_order)` — added explicitly so tests and the future UI table get stable output,
   rather than depending on whatever order the per-row rule evaluation happens to produce.
3. **`ValidOrderRow.payment_terms` normalized to `""`, not omitted**, for Warning-only rows — because
   the contract declares `payment_terms: str` (not `NotRequired`), so a Warning-only row still must
   supply *some* string value to satisfy the contract shape.
4. **`product_name` fill-from-master rule made explicit**: only fills from `product_master_df` when
   the order row's own `product_name` is blank; the order row's value always wins when present,
   because the order is what the customer/salesperson actually submitted and the product master is
   the fallback reference, not an override authority.
5. **New loader test distinguishing missing column from blank value**: `load_orders` must raise
   `MissingColumnsError` when the `payment_terms` *column* itself is absent, which is a structurally
   different problem from a present-but-blank cell (only an OV-007 Warning) — the plan hadn't
   explicitly called out that these two failure modes needed separate test coverage.
6. **Git-state check before implementation** — the review flagged that `git status` showed Phase 2
   files as uncommitted while saved memory claimed they were already committed; this was checked and
   confirmed already resolved (Phase 2 had, in fact, been committed and pushed earlier in the same
   session) rather than requiring new action.
