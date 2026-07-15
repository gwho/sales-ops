# Tutorial 01 — Python Foundation: Contracts, Loading, and Business-Readable Errors

**After completing this tutorial you will understand:** why this project defines its JSON-boundary
shapes as `TypedDict` instead of dataclasses or Pydantic, how `from __future__ import annotations`
changes what Python does with type hints at runtime, how a raw `KeyError`-shaped failure gets
translated into a message a non-programmer can act on, why `BackorderRow` can inherit from
`AllocationResultRow` and what that buys (and risks), why `uv.lock` exists and what breaks without
it, and why Phase 1 tested contract *shape* before any business rule that fills those contracts existed.

> [!NOTE]
> **Prerequisites:** None — this is the first tutorial in the series. It covers Phase 1, the
> project's very first commit. Open [`src/excel_io.py`](../../src/excel_io.py),
> [`src/contracts.py`](../../src/contracts.py), [`tests/test_excel_io.py`](../../tests/test_excel_io.py),
> [`tests/test_contracts.py`](../../tests/test_contracts.py), and
> [`tests/contract_fixtures.py`](../../tests/contract_fixtures.py) alongside this tutorial.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Structural typing (TypedDict) | `class ValidationSummary(TypedDict): ...` in `src/contracts.py` | Type theory |
| Postponed evaluation of annotations | `from __future__ import annotations` at the top of both `src/` modules | Python language |
| Exception translation (anti-corruption layer) | `MissingColumnsError` wrapping a would-be `KeyError` in `src/excel_io.py` | Design patterns |
| Structural subtyping via inheritance | `class BackorderRow(AllocationResultRow): ...` | Type theory |
| Lockfile-based reproducible builds | `uv.lock` + `pyproject.toml` | System design |

## How to use an LLM before this tutorial

### Concept 1 — TypedDict vs. dataclass vs. Pydantic

> "I'm choosing a Python type for dict-shaped values that will be serialized to JSON and consumed
> by both a test suite and (eventually) a web API. Compare `TypedDict`, `@dataclass`, and Pydantic's
> `BaseModel` for this job — runtime cost, serialization story, and what each one actually checks at
> runtime vs. only at type-check time. Give a concrete example of a bug each option would and
> wouldn't catch. Then quiz me on which one you'd pick for a project with no runtime validation
> budget yet."

*What to listen for:* the core distinction is that `TypedDict` is **erased at runtime** — it's a
plain `dict`, so `json.dumps()` works on it for free and there's zero import or object-construction
cost — while Pydantic actively validates and coerces data when you instantiate it, and dataclasses
sit in between (real objects, but still need `.asdict()` before they're JSON-serializable).

*Practice question:* If a caller builds a `ValidationSummary` dict with a typo'd key name, at what
point (if any) does Python actually notice — at runtime, or only if a type checker is run?

### Concept 2 — Postponed evaluation of annotations

> "Explain what `from __future__ import annotations` does in Python 3.12. Specifically: without it,
> when are function/class type annotations evaluated, and what problem does that cause for forward
> references (a type that refers to a class defined later in the same file, or to itself)? Show a
> small example that fails without the import and succeeds with it. Quiz me on whether this changes
> anything about how the code runs, or only about typing tools."

*What to listen for:* annotations become strings at parse time instead of being evaluated
immediately — this is purely a typing-time convenience (lets you write `list[str] | None` on older
Pythons, and reference not-yet-defined names) and has **zero effect on runtime behavior** of the
function itself.

*Practice question:* Does removing `from __future__ import annotations` from a file ever change
what the *program* does when you run it (not what a type checker reports)?

### Concept 3 — Exception translation at a module boundary

> "In backend systems, low-level libraries raise generic exceptions (KeyError, FileNotFoundError,
> IndexError) that describe *what* failed technically but not what a human should *do* about it.
> Explain the 'exception translation' or 'anti-corruption layer' pattern: catching or preventing a
> low-level failure and re-raising a domain-specific exception with an actionable message. What's
> the risk of *not* doing this at a module boundary that faces end users? Quiz me with a scenario
> and ask me to identify where the translation should happen."

*What to listen for:* the point isn't hiding the error, it's relabeling it for the audience that
will see it — an end user uploading a spreadsheet should see "your file is missing column X," not
a Python traceback mentioning `KeyError: 'sku'`.

*Practice question:* If a function both validates input and does the "real work," and the real work
also happens to raise `KeyError` for an unrelated reason, what problem does that create for a caller
trying to catch just the validation failure?

### Concept 4 — Structural subtyping (duck typing formalized)

> "Explain structural typing (also called duck typing when informal) vs. nominal typing. In a
> structurally-typed system, if type B has the exact same fields as type A, are they considered
> compatible even if B was never declared to inherit from A? Give an example of when this
> flexibility is convenient and an example of when it silently hides a real bug. Quiz me on a
> scenario involving two unrelated types that happen to share field names."

*What to listen for:* structural typing means shape is identity — two independently-defined types
with identical fields are interchangeable to the type checker, which is powerful for duck-typed
data but means a typo that happens to match a *different* type's shape won't be caught.

*Practice question:* If two totally unrelated TypedDicts in a codebase happened to define the exact
same set of keys, would a type checker stop you from passing one where the other is expected?

### Concept 5 — Lockfiles and reproducible builds

> "Explain what a dependency lockfile (like `uv.lock`, `package-lock.json`, or `Cargo.lock`) actually
> pins down that a manifest file (`pyproject.toml`, `package.json`) alone doesn't. What concretely
> breaks — and for whom — if a project ships the manifest but not the lockfile? Quiz me on the
> difference between 'this dependency requires pandas >= 3.0' and 'this exact environment resolved
> to pandas 3.0.3 with these exact transitive versions.'"

*What to listen for:* a manifest describes a *range* of acceptable versions; a lockfile freezes the
*one specific resolution* that was actually tested, including every transitive dependency's exact
version — without it, two people running "install the dependencies" on different days can get
different code.

*Practice question:* Why would a portfolio/demo repo commit its lockfile, while a widely-reused
library package often deliberately does *not* commit one?

## Architecture overview

Phase 1 builds no business rules yet — it builds the *shape* everything later will pour data
into, and the *loading path* every workflow will share:

```text
                     ┌─────────────────────────────┐
                     │   .xlsx file (path or        │
                     │   file-like object)          │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │  src/excel_io.py             │
                     │  load_excel(file)            │──► pandas DataFrame
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │  validate_required_columns(  │
                     │    df, required_cols, label) │
                     └──────────────┬───────────────┘
                         missing?  ╱ ╲  all present?
                                  ╱   ╲
                          ┌──────▼┐   ┌▼─────────────────┐
                          │ raise │   │ (later phases:     │
                          │Missing│   │  business rules run,│
                          │Columns│   │  producing rows      │
                          │ Error │   │  shaped like the     │
                          └───────┘   │  contracts below)   │
                                      └──────────┬──────────┘
                                                 ▼
                     ┌──────────────────────────────────────┐
                     │  src/contracts.py                    │
                     │  TypedDict shapes: ValidationSummary, │
                     │  ValidOrderRow, AllocationResultRow,  │
                     │  BackorderRow, PaymentAgingRow, ...   │
                     │  — plain dicts, JSON-serializable     │
                     │  for free, checked by mypy/pyright    │
                     │  and by tests/contract_fixtures.py    │
                     └──────────────────────────────────────┘
```

Key invariants for this phase:

1. **`excel_io.py` never contains workflow-specific rules**, and **`contracts.py` never contains
   loading logic.** Each module has exactly one job (ADR 0004).
2. **A contract's shape is proven before any business rule that fills it exists.** `tests/contract_fixtures.py` hand-authors believable example values for every `TypedDict` — this is testing that
   the shape *can hold* believable data, not that any calculation is correct (that's Phases 3–5).
3. **No stub files for later phases.** Phase 1 deliberately does not create empty
   `order_validation.py`, `report_export.py`, etc. — a phase creates its module the same day it
   implements it, so `context/progress-tracker.md` checkboxes stay honest.

## Part 1 — TypedDict as the JSON-boundary contract

Open [`src/contracts.py`](../../src/contracts.py) lines 1–24:

```python
"""JSON-serializable output-contract shapes shared across business modules and the future API/UI boundary."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class ValidationSummary(TypedDict):
    total_orders: int
    valid_orders: int
    invalid_orders: int
    duplicate_orders: int
    invalid_skus: int
    missing_field_count: int


class ValidationErrorRow(TypedDict):
    row_number: int
    order_id: NotRequired[str]
    sku: NotRequired[str]
    error_code: str
    error_message: str
    severity: str
```

Every one of these output families will eventually cross an actual process boundary: a Python
function builds one, FastAPI serializes it, and a Next.js component renders it (see `CLAUDE.md`'s
Output Contract rules). That trip through `json.dumps()` is the reason `TypedDict` won over the two
obvious alternatives.

A `@dataclass` is a real object at runtime — you'd need `dataclasses.asdict()` before `json.dumps()`
would touch it, and that conversion step is one more thing to forget at one more call site. A
Pydantic `BaseModel` actively validates and coerces values when constructed, which is valuable at a
true *external* boundary (user-uploaded data, a third-party API response) but is dead weight here:
every one of these dicts is built by code the project itself controls, so there's nothing to
validate against — and Pydantic wasn't needed anywhere else yet in Phase 1, so adding it would mean
adopting a dependency and a learning curve a month before the FastAPI layer that would actually use
it. `TypedDict` gives full `mypy`/`pyright` checking at type-check time and costs nothing at
runtime — it *is* a `dict`, so it serializes for free and needs no adapter code in test fixtures.

> **Type theory — Structural typing:** `TypedDict` is checked structurally, not nominally: a type
> checker considers a plain `dict` literal compatible with `ValidationSummary` purely because it has
> the right keys and value types, with no explicit "this is a `ValidationSummary`" declaration
> required. This is the same idea as Python's informal "duck typing" (if it walks like a duck...),
> formalized enough for a type checker to verify statically. The tradeoff shows up in Part 5.

**Checkpoint:** What are the trade-offs between `TypedDict`, `@dataclass`, and Pydantic's
`BaseModel` for JSON-boundary contracts in a Python + FastAPI project — and where would the answer
change if this project's contracts were filled from data *outside* its own control (e.g., a
third-party webhook payload) instead of from its own business-rule modules?

<details>
<summary>Reveal answer</summary>

`TypedDict` wins when the producer is trusted code you control and the only jobs are (a) type-check
the shape at dev time and (b) serialize it for free at runtime — which describes every contract in
this project, since order validation, allocation, and payment aging are all internal calculations,
not external input parsing. `@dataclass` earns its place when you want real methods/`__post_init__`
behavior on the object, not just a labeled bag of fields — irrelevant here since these are pure data
handoffs. Pydantic earns its place specifically at a boundary where the *input* itself is untrusted
and needs active validation/coercion (e.g., if this project ever accepted a raw JSON payload from an
external webhook instead of an Excel file it built its own DataFrame from) — the moment the producer
of the dict is not this codebase, "checked structurally by a type checker" stops being enough, and
you want runtime enforcement. That's a different problem than what Phase 1 solves.
</details>

**Checkpoint:** Should output contracts be defined in a single `contracts.py`, or co-located with
the module that produces them (e.g., `AllocationResultRow` defined inside `inventory_allocation.py`)?

<details>
<summary>Reveal answer</summary>

A single `contracts.py` makes the *set of all JSON-boundary shapes* discoverable in one place —
anyone building the FastAPI layer or the Next.js types can read one file and see every shape they'll
ever receive, without hunting through five business-rule modules. The cost is that `contracts.py`
has no natural single owner once five phases are all adding to it, and it can't enforce that a
module only touches its own contracts. Co-location trades that discoverability for tighter
ownership — you'd know `AllocationResultRow` changed the moment you touched
`inventory_allocation.py`, because they're the same diff. This project chose the single-file
approach because the contracts *are* the primary artifact the API/frontend depend on (per the
Output Contract definition in `CONTEXT.md`) — centralizing them mirrors that they're a shared
boundary, not private to one module.
</details>

**Try it yourself:** Run `uv run python -c "from src.contracts import ValidationSummary; import json; print(json.dumps({'total_orders': 5, 'valid_orders': 5, 'invalid_orders': 0, 'duplicate_orders': 0, 'invalid_skus': 0, 'missing_field_count': 0}))"` — notice `ValidationSummary` is imported but never called; a `TypedDict` is only ever a type-check-time construct, the actual value passed to `json.dumps` is just a `dict` literal.

## Part 2 — Postponed annotations and the `Iterable`/`NotRequired` imports

Open the top of [`src/excel_io.py`](../../src/excel_io.py) and [`src/contracts.py`](../../src/contracts.py):

```python
from __future__ import annotations
```

Both files open with this line before anything else. Without it, Python evaluates every type
annotation *immediately*, at function/class definition time — which means a hint like `int | str`
(Python 3.10+ union syntax) or a reference to a class defined further down the same file would need
to already be a valid, fully-resolved expression the instant the interpreter reaches that line. With
`from __future__ import annotations`, every annotation in the file is instead stored as an
**unevaluated string** and only turned into a real type by tools that ask for it — `mypy`, `pyright`,
or `typing.get_type_hints()` — not by the interpreter running the program.

Look at `load_excel`'s signature in `src/excel_io.py`:

```python
def load_excel(file, sheet_name: int | str = 0) -> pd.DataFrame:
```

`int | str` reads naturally, but it's worth knowing this line does exactly the same thing whether or
not the `__future__` import is present at the top of *this particular* file, on Python 3.12 — 3.10+
supports `X | Y` union syntax natively at runtime. The import earns its keep elsewhere: in
`contracts.py`, `NotRequired[str]` and forward-referencing structures like `BackorderRow` inheriting
from `AllocationResultRow` (Part 5) benefit from annotations not being force-evaluated at class-body
execution time. It's a cheap, project-wide habit that removes a whole category of "it works until
you add one more class" bugs, at zero runtime cost.

> **Python language — Postponed evaluation of annotations:** This is PEP 563 behavior, stabilized
> as a `__future__` import rather than default behavior even in Python 3.12. It only affects what
> annotations *are* (strings vs. evaluated objects) to tools that read them — it changes nothing
> about what the function does when called. This is a language-level idiom worth recognizing on
> sight: it signals "this file's authors are being deliberate about type-hint compatibility," not a
> runtime behavior change.

**Checkpoint:** Does removing `from __future__ import annotations` from `src/contracts.py` change
what `uv run pytest tests/test_contracts.py` actually does when it runs?

<details>
<summary>Reveal answer</summary>

No — not for this specific file's current contents, on Python 3.12. The test suite constructs plain
dict literals and checks their keys; it never calls something like `typing.get_type_hints()` on the
`TypedDict` classes that would force annotation evaluation. The import is defensive/consistency
tooling — it protects against a *future* addition (e.g., a class referencing a type defined later in
the file, or a hint incompatible with a lower Python version) breaking at import time, not something
the current file's behavior depends on today. This is exactly the kind of forward-looking convention
ADR 0004 locks in once, early, so every later phase inherits it without re-deciding.
</details>

**Try it yourself:** Temporarily delete the `from __future__ import annotations` line from
`src/contracts.py`, then run `uv run pytest tests/test_contracts.py`. Confirm it still passes —
this proves the import isn't gating today's runtime behavior, only future-proofing the type hints.
Put the line back before moving on.

## Part 3 — Loading is dumb on purpose

Open [`src/excel_io.py`](../../src/excel_io.py) lines 24–26:

```python
def load_excel(file, sheet_name: int | str = 0) -> pd.DataFrame:
    """Load an Excel file (path or file-like object) into a DataFrame."""
    return pd.read_excel(file, sheet_name=sheet_name)
```

This function does exactly one thing: hand a path or file-like object to `pandas` and return
whatever DataFrame comes back. It doesn't know what columns *should* exist, what a valid `order_id`
looks like, or which sheet a given workflow expects by convention — none of that is `excel_io.py`'s
job. `CLAUDE.md`'s module-boundary rule states this explicitly: `excel_io.py` never contains
workflow-specific rules. Order validation, inventory allocation, and payment aging (Phases 3–5) will
each call `load_excel`, then immediately hand the result to their *own* required-column list — the
loading step stays identical across all three, and only the "what does this workflow need" step
differs per caller.

`file` accepts either a path or a file-like object (note there's no type hint on that parameter) —
because `pandas.read_excel` already accepts both, and a FastAPI upload arrives as a file-like object,
not a path on disk. Deciding this now, even before FastAPI exists in the project (that's Phase 10),
avoids a rewrite later: the function signature that will eventually receive an uploaded file is
already correct.

**Checkpoint:** `test_load_excel_reads_rows_and_columns` (`tests/test_excel_io.py:7-16`) writes a
DataFrame to a real temporary `.xlsx` file, then reads it back with `load_excel`. Why test against a
real file round-trip instead of mocking `pandas.read_excel` to return a canned DataFrame directly?

<details>
<summary>Reveal answer</summary>

A mock would only prove the test author's *assumption* about what `pd.read_excel` returns — it
tells you nothing about whether `load_excel` actually works against a real `.xlsx` file on disk,
which is the only thing that matters once real uploaded spreadsheets arrive. Writing a real file with
`.to_excel()` and reading it back with the function under test exercises the actual `openpyxl`
engine underneath pandas, catching real serialization quirks (column ordering, dtype surprises) that
a mock can never surface. `tmp_path` (a built-in pytest fixture) makes this cheap and hermetic — no
cleanup code needed, no shared state between test runs.
</details>

**Try it yourself:** Run `uv run pytest tests/test_excel_io.py -v` and read the two passing test
names. Then open a Python shell and run `import pandas as pd; help(pd.read_excel)` — find the
`sheet_name` parameter's default value and confirm it matches `load_excel`'s default (`0`, the
first sheet).

## Part 4 — Turning a `KeyError` into a business-readable error

Open [`src/excel_io.py`](../../src/excel_io.py) lines 10–35:

```python
class MissingColumnsError(Exception):
    """Business-readable error for an uploaded file missing required columns."""

    def __init__(self, file_label: str, missing_columns: list[str]) -> None:
        self.file_label = file_label
        self.missing_columns = missing_columns
        column_list = ", ".join(missing_columns)
        message = (
            f"The uploaded {file_label} is missing required columns: {column_list}. "
            "Please check the sample file."
        )
        super().__init__(message)


def validate_required_columns(
    df: pd.DataFrame, required_columns: Iterable[str], file_label: str
) -> None:
    """Raise MissingColumnsError if any required column is absent from df."""
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise MissingColumnsError(file_label, missing)
```

If this function didn't exist, the very next line of code that assumed a column was present —
`df["sku"]` — would raise a plain `KeyError: 'sku'` the first time someone uploaded a file missing
that column. That's a technically accurate error and a useless one: it names a pandas internal
concept ("key"), not what the *user* did wrong or what to do about it. `validate_required_columns`
checks for every missing column up front, in one pass, and `MissingColumnsError` builds a sentence a
non-programmer can act on — naming the file (`file_label`), every missing column at once (not just
the first `KeyError` hit), and a next step ("check the sample file").

Note that `MissingColumnsError` stores `missing_columns` as a real attribute (line 15), *separately*
from folding it into the human-readable `message` string. This is deliberate redundancy: the string
is for a person reading a log or a UI toast; the list is for calling code (or a future FastAPI
handler) that wants to program against *which* columns were missing without parsing a sentence back
apart. `tests/test_excel_io.py:28-33` asserts on both — the substring check proves the message reads
right, `excinfo.value.missing_columns == ["sku"]` proves the structured data is intact.

> **Design patterns — Exception translation:** Catching or preventing a low-level, technical failure
> and re-raising a domain-specific exception with an actionable message is sometimes called an
> anti-corruption layer at a module boundary. The general failure mode this avoids: a caller three
> layers up catching a bare `KeyError` can't tell a missing-column problem apart from an unrelated
> dict-lookup bug elsewhere in the same `try` block. A named exception type (`MissingColumnsError`)
> lets callers catch *exactly* this failure mode and nothing else — the same principle behind
> `requests.HTTPError` wrapping a raw socket error, or Django's `ObjectDoesNotExist` wrapping a SQL
> "0 rows returned."

**Checkpoint:** What's the difference between a technical exception (`KeyError`,
`FileNotFoundError`) and a business-readable error? How do you enforce that distinction at module
boundaries?

<details>
<summary>Reveal answer</summary>

A technical exception describes a failure in terms of the implementation (a dict lookup failed, a
file wasn't found on disk) — accurate, but meaningless to whoever is supposed to fix the underlying
problem, especially when that person is an end user, not a developer. A business-readable error
describes the failure in terms of the *domain* — "your uploaded orders file is missing the sku
column" — using vocabulary the person reading it actually has. Enforcing the distinction at a module
boundary means: never let a low-level exception cross out of the module uncaught/untranslated; catch
it (or, as here, prevent it by checking first) and raise a purpose-built exception type instead, with
a message written for the boundary's actual audience.
</details>

**Checkpoint:** `validate_required_columns` raises `MissingColumnsError` rather than returning an
error dict or `None`/error-tuple. When is raising the right call, and when would returning an error
value be better instead?

<details>
<summary>Reveal answer</summary>

Raising is right here because a missing required column is not a value the caller should be
expected to routinely check for and branch around inline — it's an exceptional, stop-the-workflow
condition, and Python's exception machinery (unwind the stack, `pytest.raises` in tests, a FastAPI
exception handler translating it to an HTTP 4xx later) is built for exactly that. Returning an error
value earns its keep when failure is a *routine*, expected outcome the caller is meant to branch on
every single call — e.g., a lookup function where "not found" is a normal, frequent result rather
than a rare, workflow-halting one. Order/inventory/payment file uploads missing a required column is
closer to the former: rare, and correctly ends the request rather than continuing with partial data.
</details>

**Try it yourself:** In a Python shell, run
`from src.excel_io import validate_required_columns; import pandas as pd; validate_required_columns(pd.DataFrame({"order_id": ["SO-1"]}), ["order_id", "sku", "quantity"], "orders file")`
and read the exact exception message. Confirm it lists *both* missing columns in one sentence, not
just the first one found.

## Part 5 — Reusing a contract's shape through inheritance

Open [`src/contracts.py`](../../src/contracts.py) lines 48–64:

```python
class AllocationResultRow(TypedDict):
    order_id: str
    customer_name: str
    sku: str
    product_name: NotRequired[str]
    requested_qty: int
    allocated_qty: int
    backorder_qty: int
    warehouse: str
    status: str
    priority: str
    requested_delivery_date: str


class BackorderRow(AllocationResultRow):
    """Same shape as AllocationResultRow — the Backorders sheet is that table filtered to status=Backordered."""
```

`BackorderRow` adds no new fields — it inherits every one from `AllocationResultRow` and exists
purely so the *name* in code matches the *name* of a real output ("the Backorders sheet"), even
though the underlying dict shape is identical. `tests/test_contracts.py:56-71` proves this directly:
it builds an `AllocationResultRow` dict, wraps it with `dict(allocation_row)` typed as
`BackorderRow`, and asserts the two are equal — same keys, same values, different label.

This is where structural typing (Part 1) has a real cost as well as a benefit. Because `TypedDict`
compatibility is checked by shape, not declared ancestry, a type checker would accept *any* dict with
`AllocationResultRow`'s exact fields as a valid `BackorderRow` — even one that never went near this
inheritance relationship, built from an entirely unrelated code path that happened to produce the
same keys. That's convenient here, where the relationship is intentional and documented in the
class's own docstring. It would be a silent bug magnet if two *unrelated* contracts (say,
`ValidOrderRow` and some future customer-record type) accidentally ended up with the same field
names for unrelated reasons — a type checker would wave both through as interchangeable, and nothing
at runtime would ever catch the mixup, since `TypedDict` performs no runtime validation at all.

> **Type theory — Structural subtyping in practice:** `BackorderRow(AllocationResultRow)` is
> declared nominally (an explicit `class X(Y)`), but *checked* structurally — a type checker doesn't
> care that the inheritance was declared; it would accept the substitution even without it, purely
> from matching fields. This dual nature — you can *choose* to declare a structural relationship
> for readability/intent, even though the type system would allow it either way — is specific to
> structurally-typed systems and doesn't exist in purely nominal type systems (like Java's
> interfaces), where declaring `implements`/`extends` is the *only* way to establish compatibility.

**Checkpoint:** `TypedDict` is structurally typed — two dicts with the same keys are compatible even
if they came from types with no declared relationship at all. When does this cause real problems,
and how do you guard against it?

<details>
<summary>Reveal answer</summary>

It causes problems when two contracts *should* be treated as distinct — different meanings, subject
to independent change — but happen to share a field set, whether by coincidence or because one was
copy-pasted from the other early on. A type checker offers zero protection here: it will accept
either one wherever the other is expected, because shape is all it checks. The guard isn't a type
system feature — `TypedDict` doesn't have one — it's process discipline: `CLAUDE.md`'s Field Scope
Boundary rule (a contract may only contain fields its originating spec explicitly defines) is exactly
this guard. It forces each contract's fields to be justified by its own spec, not by "well, it
already matches this other shape," which is what keeps accidental structural overlap from becoming
a real substitution bug. `BackorderRow` is the *sanctioned* version of structural overlap — declared
explicitly, in one place, because the relationship is real (same table, different filter), not
coincidental.
</details>

**Try it yourself:** Search `src/contracts.py` for every other `NotRequired[...]` field (there are
several, e.g. `ValidOrderRow.product_name`, `RemainingInventoryRow.reorder_point`). For each, form a
guess at why that specific field — and not some other one on the same contract — was made optional,
then check your guess against the corresponding spec file mentioned in `CLAUDE.md`'s Field Scope
Boundary section.

## Part 6 — Testing a contract's shape before any rule fills it

Open [`tests/contract_fixtures.py`](../../tests/contract_fixtures.py) lines 1–7 and
[`tests/test_contracts.py`](../../tests/test_contracts.py) lines 84–93:

```python
"""Realistic example values for each Phase 1 output-contract family (Contract Fixtures).

Hand-authored, not computed by src/sample_data.py or any business-rule module —
order_validation.py, inventory_allocation.py, and payment_aging.py don't exist
until Phases 3-5. These only prove the contract shapes can hold believable demo
data; they are not evidence that any business rule is implemented correctly.
"""
```

```python
def test_validation_summary_fixture_has_all_required_keys():
    assert isinstance(VALIDATION_SUMMARY_FIXTURE, dict)
    assert set(VALIDATION_SUMMARY_FIXTURE.keys()) == {
        "total_orders",
        "valid_orders",
        "invalid_orders",
        "duplicate_orders",
        "invalid_skus",
        "missing_field_count",
    }
```

At the point Phase 1 was built, `order_validation.py` didn't exist — there was no function anywhere
in the codebase that could *compute* a real `ValidationSummary`. So what is there to test? The
docstring says it plainly: these fixtures are hand-typed, plausible-looking example values,
authored purely to prove the `TypedDict` shape can hold believable data — not evidence any
calculation is correct, because no calculation exists yet to be correct or incorrect.

This is a narrower, cheaper kind of test than end-to-end rule coverage, and it's deliberately scoped
that way. It catches a specific, real class of bug early: a contract shape that looks fine in
isolation but turns out to be awkward or wrong once you try to imagine a realistic row of data in
it — a missing field nobody noticed, a type that doesn't fit a real value (e.g. discovering
`invoice_amount` needs to be `float`, not `int`, the moment you try to write `58000.00` into a
fixture). Waiting until Phases 3–5's real business logic existed to discover that would mean
reworking both the contract *and* whatever code already depended on its old shape.

Notice the two different assertion styles across `test_contracts.py`: some contracts assert
`set(...) == {...}` (the *exact* key set, no more, no less — used for contracts with no
`NotRequired` fields, like `ValidationSummary`), while others assert `{...} <= fixture.keys()`
(a *subset* check — used for contracts like `ValidOrderRow` that have optional fields the fixture
may or may not include). The subset check is what actually respects `NotRequired` at the test level;
an exact-match check on a contract with optional fields would break the moment a fixture legitimately
omitted one.

**Checkpoint:** Why is it valuable to test a contract's shape before the business rule that produces
real values for it exists at all?

<details>
<summary>Reveal answer</summary>

Because the contract shape is the thing every later phase — the business rule module, the FastAPI
route, the Next.js type, the UI component — will build against. If the shape is wrong (a field
that's the wrong type, a field nobody actually needs, a required field that should have been
optional), discovering that *before* four other things depend on it means fixing one file. Discover
it after Phase 5's `payment_aging.py`, Phase 10's FastAPI route, and a Next.js component all assume
the old shape, and now it's a coordinated multi-file rewrite. Testing shape first is cheap insurance
against exactly that ordering risk — it's the same reason ADR 0003 sequenced "stable output
contracts" (step 4) *before* "polished Next.js dashboard" (step 6).
</details>

**Checkpoint:** What's the difference between a test fixture (a minimal DataFrame built inline for
one specific edge case, like the ones in `tests/test_excel_io.py`) and a demo fixture
(`sample_data/*.xlsx`, deferred to Phase 2)? Why does this distinction matter for a portfolio project?

<details>
<summary>Reveal answer</summary>

A test fixture is minimal and adversarial on purpose — it exists to isolate one behavior (one
missing column, one edge case), stripped of anything not needed to trigger that exact code path. A
demo fixture is the opposite: a *believable*, realistic-looking spreadsheet a human reviewer would
recognize as "a plausible sales order file," intentionally including messy real-world imperfections.
Conflating the two would weaken both — a test fixture cluttered with realistic noise makes it harder
to see which one line of data is actually being tested; a demo fixture pared down to only the
minimum needed to pass tests would look obviously fake to anyone reviewing the portfolio. `CONTEXT.md`
and `CLAUDE.md` keep this distinction explicit specifically because this project's whole value
proposition is being *evaluated* by a human reader who needs the demo data to look credible.
</details>

**Try it yourself:** Run `uv run pytest tests/test_contracts.py -v` and count how many tests pass.
Then open `tests/contract_fixtures.py` and delete one required key (not a `NotRequired` one) from
`VALIDATION_SUMMARY_FIXTURE`. Re-run the test and read which assertion fails and why.

## Part 7 — Deferred scope and the Python-first sequencing decision

Open [`docs/adr/0004-phase-1-python-tooling.md`](../adr/0004-phase-1-python-tooling.md) point 4:

> Phase 1 file scope: only `src/__init__.py`, `src/excel_io.py`, `src/contracts.py`,
> `tests/test_excel_io.py`, `tests/test_contracts.py`. No placeholder/stub files for
> `order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, `report_export.py`, or
> `sample_data.py` — those are created in the phase that actually implements them.

This is a narrower rule than it sounds: it would have been easy to scaffold empty stub modules for
every phase up front, "so the shape of the project is visible early." ADR 0004 explicitly rejects
that — an empty `order_validation.py` would add no executable behavior, and worse, it would go stale
(wrong function signature, wrong imports) long before Phase 3 actually needed it, silently lying
about how "done" the project is. `context/progress-tracker.md`'s checkboxes mean *implemented*, not
*stubbed* — a distinction only enforceable if stubs are banned outright.

This scoping discipline is the concrete, file-level expression of ADR 0003's larger bet: build and
prove the Python core before spending effort on the polished UI. The risk ADR 0003 names directly is
sequencing risk — a project that starts with a polished dashboard risks spending its available time
on presentation before the substantive payload (tested automation rules, believable sample data,
real report output) exists at all. For a portfolio audience specifically, presentation without
payload reads as thin; payload without presentation still reads as a demonstrated, credible skill.

> **System design — Reproducible builds via lockfiles:** unrelated to the sequencing decision above,
> but locked in the same ADR: `uv.lock` is committed alongside `pyproject.toml`. `pyproject.toml`
> states *ranges* ("pandas>=3.0.3"); `uv.lock` freezes the *exact resolution* — every transitive
> dependency's exact version — that was actually tested. Without the lockfile, `uv sync` run by a
> different reviewer on a different day could resolve a different, untested set of versions.
> Committing it trades away a library's usual "let consumers pick their own resolution" flexibility
> for "every reviewer runs the exact bytes this was built and tested against" — the right trade for
> an application, wrong for a package other projects import.

**Checkpoint:** ADR 0003 chose Python-core-before-UI specifically to avoid spending the first
milestone on polish before the portfolio payload exists. What's the general principle here, and when
would you reverse it?

<details>
<summary>Reveal answer</summary>

The general principle: sequence work so the *highest-risk, hardest-to-fake* part of a deliverable
gets built and proven first, even if it's the least visually impressive part — because a reviewer
(or a later version of yourself) can always tell the difference between "the hard part works" and
"the hard part is hidden behind a good-looking shell." You'd reverse this when the risk is inverted —
e.g., a client-facing prototype whose entire purpose is validating *whether users want this at all*
before investing in real backend logic; there, a fake, UI-only prototype (sometimes literally
backed by a human typing responses, a "Wizard of Oz" prototype) is the correct sequencing, because
the business logic would be wasted effort if the UI concept itself is rejected. This project's ADR
0003 explicitly reasons about *this* audience (interviewers evaluating sales-ops domain competence)
to justify the opposite choice.
</details>

**Checkpoint:** The Phase 8 gate this project defines is hard: every test case in three spec files
must pass before any Next.js code is written. What are the risks of a hard gate like this versus a
softer "good enough" gate?

<details>
<summary>Reveal answer</summary>

A hard gate's risk is time: if the last few edge cases in the spec are disproportionately hard or
ambiguous, the whole project stalls waiting on 100% before any visible UI progress happens at all —
demotivating on a solo project, and risky against any real deadline. A soft "good enough" gate's risk
is exactly what ADR 0003 is designed to prevent: without a hard line, "good enough" quietly slides
earlier and earlier under time pressure, and the UI ends up built on top of rules that were never
actually finished, which is much harder to notice from the UI side than from a red test in CI. This
project's phase structure (1 through 6 are all Python, with Phase 8 as the explicit gate) accepts the
first risk deliberately in order to eliminate the second, because the second risk is the one ADR 0003
identifies as fatal specifically for a *portfolio* audience — an interviewer can't easily tell
"finished rules" from "rules that look finished in the demo," but a full green test suite is
unambiguous proof either way.
</details>

**Checkpoint:** This project is a portfolio piece simulating Excel-based sales-ops workflows. What
makes a good portfolio project for a sales-ops / data-engineering-adjacent role, and how does the
Python-first decision serve that specifically?

<details>
<summary>Reveal answer</summary>

A good portfolio project for this kind of role needs to demonstrate credible domain judgment
(does the candidate understand what "aging bucket" or "allocatable quantity" actually mean
operationally?), not just UI competence — most sales-ops/data hiring conversations probe "walk me
through how you handled X edge case," which only a tested rules engine with real edge-case coverage
can answer convincingly. A slick dashboard over hardcoded or unvalidated data invites exactly the
follow-up question it can't survive: "what happens if two orders have the same ID?" The Python-first
decision serves this directly — by the time any UI exists, there's already a tested, documented
answer to every edge case a reviewer might ask about, because ADR 0003 forced those answers to exist
*before* there was anything else to show.
</details>

## Full data flow: an uploaded orders file with a missing column, from disk to a business-readable message

1. A caller has a path or file-like object representing an uploaded orders spreadsheet and calls
   `load_excel(file)` — [`src/excel_io.py:24-26`](../../src/excel_io.py#L24-L26). This returns a
   plain pandas `DataFrame`, no validation performed yet.
2. The caller (in Phase 1, this is a test; in later phases, a workflow module) calls
   `validate_required_columns(df, required_columns, file_label)` —
   [`src/excel_io.py:29-35`](../../src/excel_io.py#L29-L35) — passing in the specific columns *this*
   workflow needs and a human-readable label for the file (e.g. `"orders file"`).
3. Inside the function, a list comprehension (`src/excel_io.py:33`) walks `required_columns` and
   keeps only the ones **not** in `df.columns` — a single pass that finds *every* missing column at
   once, not just the first.
4. If `missing` is non-empty, `raise MissingColumnsError(file_label, missing)` executes
   (`src/excel_io.py:35`), constructing the exception.
5. `MissingColumnsError.__init__` (`src/excel_io.py:13-21`) stores `file_label` and
   `missing_columns` as plain attributes, joins the missing list into a comma-separated string, and
   builds a full sentence naming the file and every missing column, ending with a next step
   ("Please check the sample file.") — then calls `super().__init__(message)` so the exception's
   string representation *is* that sentence.
6. `tests/test_excel_io.py:28-33` catches this with `pytest.raises(MissingColumnsError)` and asserts
   on three things independently: that `"orders file"` appears in the message (right file named),
   that `"sku"` appears in the message (right column named), and that
   `excinfo.value.missing_columns == ["sku"]` (the structured data survived intact, for any future
   caller that wants to program against it rather than parse a sentence).

Nothing here yet converts this into an HTTP response — that arrives in Phase 10, when a thin FastAPI
route handler catches `MissingColumnsError` and turns it into a 4xx JSON error body. Phase 1 only
needs to prove the exception itself carries the right information; the transport layer is a
different phase's job entirely, consistent with the module-boundary rule that `excel_io.py` doesn't
know FastAPI exists.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Open `tests/test_contracts.py` and find every assertion that
uses `set(fixture.keys()) == {...}` (exact match) versus every assertion that uses
`{...} <= fixture.keys()` (subset match). For each contract tested, cross-reference
`src/contracts.py` to confirm: does the exact-match style only ever appear on contracts with *zero*
`NotRequired` fields? Write down any contract where this correlation doesn't hold, and explain why
(hint: check whether the fixture itself happens to include every optional field even though the
contract technically doesn't require it).

<details>
<summary>Hint</summary>

Look closely at `PaymentAgingRow` and `PaymentAgingSummary` (`test_contracts.py:170-196`) — both use
exact-match `==` even though `src/contracts.py` shows neither has a `NotRequired` field at all. Now
compare to `ValidationErrorRow` and `ValidOrderRow`, which do have `NotRequired` fields and correctly
use the subset check.
</details>

**Challenge 2 — Extend** (20–30 min): `MissingColumnsError` currently reports *which* columns are
missing but not what columns *are* present, which would help someone debugging a header-row typo
(e.g. `"Order_ID"` instead of `"order_id"`). Add an optional `present_columns: list[str] | None`
parameter to `MissingColumnsError.__init__`, thread it through from `validate_required_columns`
(which already has `df.columns` on hand), and extend the message to include it only when provided
(don't break the existing message shape or the two current tests). Add a new test in
`tests/test_excel_io.py` that asserts the new information appears when passed, and that the existing
two tests still pass unmodified — proving the extension is backward compatible.

<details>
<summary>Hint</summary>

Keep `present_columns` optional with a default of `None`, and only add the extra sentence to the
message when it's not `None` / not empty — this is the same "only assert what you can guarantee"
discipline as `NotRequired` fields in `contracts.py`. Don't change the signature of
`validate_required_columns` in a way that breaks its two existing call sites in
`tests/test_excel_io.py`.
</details>

**Challenge 3 — Break and fix / Design** (30–45 min): `TypedDict` performs zero runtime validation —
nothing stops a bare `dict` with an extra, unexpected key (e.g. `"internal_notes": "..."` accidentally
left in `VALIDATION_SUMMARY_FIXTURE`) from being treated as a valid `ValidationSummary` by both
Python and the current test suite. Design (don't necessarily implement, unless you want to) a runtime
check that *would* catch a stray extra key — think about where such a check should live (a helper in
`test_contracts.py`? A `contracts.py` utility function used by every fixture test?) and what its
performance/maintenance cost is versus the bug class it prevents. Then write one concrete test case
using your design that would fail on today's codebase if someone added a stray key to any fixture,
and explain in one paragraph why `TypedDict` itself can never provide this guarantee no matter how
the code is organized.

<details>
<summary>Hint</summary>

Revisit Part 5's discussion of structural typing's blind spot — the same reason `TypedDict` can't
catch two *different* types accidentally sharing a shape is the same reason it can't catch one
fixture accidentally growing an *extra*, unsanctioned key: shape-checking only verifies the fields
it knows to look for exist with the right types; it has no concept of "and nothing else." A runtime
check would need to explicitly compare `set(fixture.keys())` against the `TypedDict`'s own declared
keys (available via `SomeTypedDict.__required_keys__` and `__optional_keys__` at runtime) — something
none of today's tests currently do.
</details>

For deeper exploration, `docs/plan/phase-1-python-foundation/ai-discussion-topics.md` has 10 prompts
covering TypedDict/contract design, error handling at module boundaries, the Python-first sequencing
decision, and testing strategy. Feed them to an LLM *after* forming your own answer first — the gap
between what you thought and what you learn is where understanding lands.
