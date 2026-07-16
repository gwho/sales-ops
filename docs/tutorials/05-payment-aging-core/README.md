# Tutorial 05 — Payment Aging Core: One Pass, Three Outputs, No Shared State

**After completing this tutorial you will understand:** why `calculate_payment_aging()` reads
`invoices.xlsx` directly instead of consuming another module's output, why keeping `days_overdue`
signed instead of flooring it at zero is what makes the Watch window expressible at all, why a
Paid invoice stays visible in `aging_rows` while being excluded from *follow-up*, why
`follow_up_priority` can fire High on an invoice that isn't even due yet while draft messages
deliberately never do, why `invoice_amount` and `paid_amount` — two numbers governed by the same
rule family — get genuinely different validation treatment, why `total_invoices` and the aging
bucket counts can legitimately disagree, and why a hand-authored Phase 2 fixture turned out to be
wrong in two different ways once Phase 5 actually computed against it.

> [!NOTE]
> **Prerequisites:** Tutorial 04 (`04-inventory-allocation-core/README.md`) — read for the
> pattern, not the mechanism: Phase 4 established stateful, order-dependent depletion; Phase 5
> deliberately does *not* work that way, and the contrast is the fastest way to understand this
> module's shape. Tutorial 03 (`03-order-validation-core/README.md`) — result envelopes,
> row-level issues, and distinct-count summary semantics all reappear here with new twists.
> Tutorial 02 (`02-sample-data/README.md`) — date anchoring (`reference_date`/`offset()`) and
> fixture independence both come back directly in Parts 3 and 10. Open
> [`src/payment_aging.py`](../../../src/payment_aging.py),
> [`src/contracts.py`](../../../src/contracts.py), and
> [`tests/test_payment_aging.py`](../../../tests/test_payment_aging.py) alongside this tutorial.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| `None`-sentinel default resolved once, no closure needed | `effective_date = as_of_date or date.today()` | Python language |
| Clamping a value into a valid range | `outstanding_amount = max(invoice_amount - paid_amount, 0.0)` | Algorithms |
| First-match-wins conditional dispatch | `_follow_up_priority()`'s ordered `if`/`elif`-style chain | Design patterns |
| Guard clause for single-pass partitioning | `if row_issues: data_issues.extend(row_issues); continue` | Design patterns |
| Dict comprehension for guaranteed key coverage | `{bucket: 0 for bucket in _AGING_BUCKET_ORDER}` | Data structures |

## How to use an LLM before this tutorial

### Concept 1 — Single-pass classification vs. stateful multi-pass processing

> "Explain the difference between a data-processing function that classifies each input
> independently in one pass (row 5's outcome never depends on what happened to row 1) versus one
> that must process inputs in a specific order because later decisions depend on earlier ones
> (e.g., allocating limited stock by priority, where filling one order changes what's left for the
> next). Give a concrete example of a real-world task that's naturally single-pass and one that's
> naturally order-dependent. Quiz me on which category 'classify every invoice into an aging
> bucket' falls into, and why."

*What to listen for:* single-pass classification means every row's outcome is a pure function of
that row alone (plus one shared, read-only reference value like "today's date") — you could
shuffle the rows, or even process them on different machines in parallel, and get the identical
set of results back, just in a different order. Order-dependent processing has no such guarantee;
shuffle the inputs and you can get a genuinely different, equally "correct" outcome.

*Practice question:* if you ran a payment-aging calculation on the exact same invoice file twice,
once processing rows top-to-bottom and once bottom-to-top, would any individual invoice's computed
`aging_bucket` or `follow_up_priority` differ between the two runs?

### Concept 2 — Signed vs. unsigned quantities, and what each throws away

> "Explain the difference between representing a real-world quantity as a signed number
> (negative values are meaningful and preserved) versus as an unsigned or floored one (negative
> results get clamped to zero, because 'less than zero' isn't considered meaningful for this
> quantity). Give one example where flooring at zero is clearly correct, and one example where
> flooring at zero would destroy information the rest of the system actually needs. Quiz me on
> which category 'the gap between today and a due date, which might be in the future' falls into."

*What to listen for:* flooring is correct when the sign genuinely carries no further meaning past
zero (a bank balance display floored to "$0 owed" instead of showing a negative debt as a positive
credit would be confusing in a *different* way — context matters). Flooring destroys information
whenever some downstream rule needs to distinguish *how far* past the floor a value would have
gone — "3 days from now" and "300 days from now" are both "not overdue," but they are not remotely
the same fact if the rest of the system needs to answer "is this due soon."

*Practice question:* if "days until a due date" is stored as a floored `0` for every not-yet-due
invoice, can you still answer the question "which unpaid invoices are due within the next week"
using only that stored value?

### Concept 3 — First-match-wins vs. independent rule evaluation

> "In a system with several candidate labels for the same item, contrast two designs: (a) a fixed,
> ordered sequence of checks where the first one that matches wins and every later check is
> skipped, versus (b) every check running independently, with the item potentially qualifying for
> several labels at once (collected into a list). Give an example of a real classification problem
> that clearly needs (a) — exactly one final answer — and one that clearly needs (b) — multiple
> simultaneous findings are all valid at once. Quiz me on which shape fits 'assign one final
> priority label to an invoice' versus 'list every validation problem with an order row.'"

*What to listen for:* first-match-wins is the right shape whenever the output is fundamentally a
single, mutually-exclusive category (an invoice has *one* priority, not several) — order in the
chain becomes a real design decision, since a broader/earlier check can shadow a narrower/later
one entirely. Independent evaluation is right when multiple simultaneous facts can all be true
about the same item and the consumer benefits from seeing all of them (a spreadsheet row can be
missing two different required fields at once, and a user wants to know about both in one pass).

*Practice question:* if a priority-assignment chain checked "Medium" before "High" instead of
after, could an invoice that should be High priority ever be reported as Medium instead — and
would you find out by reading the individual conditions, or only by tracing execution order?

### Concept 4 — Clamping

> "Explain 'clamping' a numeric value: forcing it to stay within a valid range (e.g., never below
> some minimum) by replacing any out-of-range result with the boundary itself, using something
> like `max(value, floor)` or `min(max(value, floor), ceiling)`. Give a concrete example of a
> calculation that can mathematically go out of range (e.g., subtracting a payment larger than
> what was owed) and explain why clamping the *output* is usually preferable to preventing the
> *input* that caused it. Quiz me on what a consumer of a clamped value can and cannot conclude
> from seeing exactly the boundary value (e.g., seeing exactly `0`)."

*What to listen for:* clamping the output is simpler and more robust than trying to reject or
special-case every input combination that could produce an out-of-range result, because it handles
every current and future cause of "went past the boundary" uniformly, at one place, rather than
requiring every caller to separately guard against it. The cost: a clamped boundary value is
ambiguous about *how far* past the boundary the real computation would have gone — `0` could mean
"exactly paid in full" or "wildly overpaid," and the clamped value alone can't distinguish them.

*Practice question:* given only a clamped `outstanding_amount` of `0.0`, could you tell, from that
field alone, whether the invoice was paid exactly in full or significantly overpaid?

### Concept 5 — Guard clauses for partitioning a batch into disjoint groups

> "Explain the 'guard clause' pattern: checking a disqualifying condition early in a loop body
> and using `continue` (or `return`) to skip the rest of the processing for that one item, instead
> of wrapping the 'normal path' logic in a big `if not disqualified:` block. Explain why this
> guarantees every item ends up in exactly one of two output groups, never both and never neither.
> Quiz me on what would have to go wrong in the code for an item to accidentally end up counted in
> both groups."

*What to listen for:* a guard clause followed by `continue` makes "this item is disqualified" a
dead end in the control flow — nothing after that line can run for this item in this iteration,
which is a stronger guarantee than an `if/else` split, where a future edit could accidentally add
code after the `else` block that runs for both branches. The partition is enforced structurally,
not just by convention.

*Practice question:* in a loop that appends to `list_a` inside a guard clause's `continue` branch
and to `list_b` at the very end of the loop body, is it possible for a single iteration to append
to both lists?

## Architecture overview

Phase 4 (Tutorial 04) built a module whose entire design centers on *shared, mutating state*
across a strict processing order — one order line's outcome directly changes what the next line
sees. Phase 5 is deliberately the opposite shape. Every invoice row is classified independently,
in one linear pass, with no row's outcome depending on any other row's:

```text
                     invoices.xlsx
                          │
                          ▼
              load_invoices(file)
    (excel_io.load_excel + validate_required_columns)
                          │
                          ▼ invoices_df                    as_of_date: date | None
                          │                                        │
                          └───────────────────┬─────────────────────┘
                                               ▼
                  calculate_payment_aging(invoices_df, as_of_date)
                  effective_date = as_of_date or date.today()
                  ── ONE PASS, each row independent — no row's result
                     depends on any other row's (contrast Tutorial 04's
                     shared, mutating inventory_by_sku) ──
                                               │
                     for each row, independently, in file order:
                                               │
                       parse due_date, parse invoice_amount
                                               │
                         ┌─────────────────────┴─────────────────────┐
                    either failed?                          both parsed OK?
                  (PA-006 / PA-007)                                  │
                         │                                           ▼
                         ▼                              parse paid_amount — forgiving:
              data_issues.append(...)                    bad/blank/negative → 0.0,
                    continue ─────────┐                   never a data issue
                                       │                              │
                                       │                              ▼
                                       │            outstanding_amount = max(invoice_amount
                                       │                                  - paid_amount, 0.0)
                                       │                              │
                                       │                              ▼
                                       │            days_overdue = effective_date - due_date
                                       │                    (SIGNED — never floored)
                                       │                              │
                                       │              ┌───────────────┼────────────────┐
                                       │              ▼               ▼                ▼
                                       │       aging_bucket   follow_up_priority   suggested_action
                                       │       (5 fixed        (first-match-wins    (lookup table,
                                       │        ranges)         chain, Paid first)   keyed by priority)
                                       │                              │
                                       │                   aging_rows.append(row)
                                       │                              │
                                       │                   draft-message guard:
                                       │                   outstanding>0 AND days_overdue>0
                                       │                   AND priority in {High,Medium,Low}
                                       │                              │
                                       │                     (maybe) draft_messages.append(...)
                                       ▼                              ▼
                       ┌───────────────────────────────────────────────────────┐
                       │      after every row: _build_summary(len(invoices_df), │
                       │      aging_rows) — total_invoices counts ALL loaded    │
                       │      rows; every OTHER aggregate counts aging_rows only│
                       └───────────────────────────┬───────────────────────────┘
                                                     ▼
                                    PaymentAgingResult
                        { summary, aging_rows, data_issues, draft_messages }
```

Key invariants for this phase:

1. **Every row is classified independently, in one linear pass.** No row's `aging_bucket`,
   `follow_up_priority`, or membership in `data_issues` depends on any other row — unlike
   Tutorial 04's `allocate_inventory`, there is no shared, mutating state between iterations
   (Part 5, Part 6).
2. **A row lands in exactly one of two places: `aging_rows` or `data_issues`, never both, never
   neither.** The guard clause in the main loop enforces this structurally (Part 8).
3. **`total_invoices` counts every loaded row; every other summary aggregate counts only
   `aging_rows`.** The two numbers are allowed to disagree, on purpose (Part 9).

## Part 1 — Result envelope: one payment-aging result, not three caller-stitched outputs

Open [`sales_admin_automation_toolkit_specs/03_demo_payment_aging.md`](../../../sales_admin_automation_toolkit_specs/03_demo_payment_aging.md)
§11's suggested functions:

```python
def calculate_payment_aging(invoices_df: pd.DataFrame, as_of_date: date) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return aging_df and data_issues_df."""


def create_follow_up_messages(aging_df: pd.DataFrame) -> pd.DataFrame:
    """Generate draft follow-up messages for overdue invoices."""
```

The spec suggests two separate functions, called in sequence, with the caller responsible for
stitching `calculate_payment_aging()`'s two-DataFrame return together with a second call to
`create_follow_up_messages()`. Now open
[`src/payment_aging.py`](../../../src/payment_aging.py) lines 46–50:

```python
class PaymentAgingResult(TypedDict):
    summary: PaymentAgingSummary
    aging_rows: list[PaymentAgingRow]
    data_issues: list[PaymentDataIssueRow]
    draft_messages: list[DraftMessageRow]
```

This mirrors Tutorial 03's `OrderValidationResult` and Tutorial 04's `InventoryAllocationResult`
exactly: one `TypedDict` envelope, defined locally rather than added to `src/contracts.py`, one
function call, one JSON-serializable return value. `explanation.md` names the concrete cost of the
spec's literal suggestion directly: splitting into two functions would mean the module has no
single "the payment aging result" object — a future FastAPI route handler would need to know to
call two functions in the right order and merge their outputs manually, which is exactly the kind
of route-layer business logic `CLAUDE.md`'s Python Module Boundaries table forbids. Instead,
`calculate_payment_aging()` computes aging, spots data issues, and builds draft messages together,
in the same single pass over `invoices_df` — three output families from one loop, not three
separate traversals.

`load_invoices()` stays a separate, thin loader (lines 53–57) — that part of the spec's suggested
shape already matches the established Phase 3/4 convention, so there was nothing to collapse
there.

**Checkpoint:** `PaymentAgingResult`'s field names (`aging_rows`, `data_issues`,
`draft_messages`) don't share a naming pattern with Phase 3's (`valid_orders`, `errors`) or
Phase 4's (`allocation_results`, `backorders`, `remaining_inventory`, `supplier_follow_ups`) — each
module picked names that read well for its own domain. When `report_export.py` needs to pull from
all three envelopes to build sheets, does that naming inconsistency create any real friction, or is
it a non-issue since each envelope is only ever destructured by key, never iterated generically?

<details>
<summary>Reveal answer</summary>

It's a non-issue in practice, precisely because of how these envelopes get consumed:
`report_export.py`'s job (per `CLAUDE.md`'s module-boundary table) is to format
*already-computed* results into named Excel sheets — it will always destructure each envelope by
its own specific keys (`result["aging_rows"]`, `result["backorders"]`, etc.), never loop over
"every list-valued field in this dict" generically across modules. Generic iteration is exactly
where inconsistent naming would bite — a function written to work identically across all three
envelopes by reflecting over their keys would need to special-case each one anyway, defeating the
point of genericity. Since nothing in this codebase's design calls for that kind of
envelope-agnostic code (each report sheet is hand-mapped to a specific field, per workflow), the
naming inconsistency stays a readability choice — clearer per-domain names — with no real coupling
cost. It would become a real problem only if a future feature wanted to treat "any output envelope"
polymorphically, which nothing in the current scope asks for.
</details>

**Checkpoint:** Why does `calculate_payment_aging()` compute `aging_rows`, `data_issues`, and
`draft_messages` all inside the same loop over `invoices_df`, rather than three separate loops —
one per output family — the way the spec's two-function suggestion implies?

<details>
<summary>Reveal answer</summary>

A separate loop per output would mean re-parsing and re-deriving the same per-row facts
(`due_date_parsed`, `invoice_amount`, `outstanding_amount`, `days_overdue`) multiple times — once
to build `aging_rows`, again to decide `data_issues`, again to decide `draft_messages` — since
`draft_messages` and the aging classification both depend on the exact same derived values
(`outstanding_amount`, `days_overdue`, `follow_up_priority`). Doing it in one pass means every
value is computed exactly once per row and reused for every decision that needs it, which is both
simpler (no risk of the three passes silently disagreeing on how they parse the same cell) and
cheaper (one iteration over the DataFrame instead of three).
</details>

**Try it yourself:** Run
`uv run python -c "from src.payment_aging import calculate_payment_aging; import pandas as pd; from datetime import date; df = pd.DataFrame([{'invoice_id':'INV-1','customer_name':'Test','invoice_date':date(2026,6,1),'due_date':date(2026,6,1),'invoice_amount':1000.0,'paid_amount':0.0}]); r = calculate_payment_aging(df, as_of_date=date(2026,7,1)); print(r.keys())"`
and confirm the four keys printed match `PaymentAgingResult` exactly — one call, one envelope, no
manual stitching.

## Part 2 — Loader boundary and required invoice columns

Open [`src/payment_aging.py`](../../../src/payment_aging.py) lines 22–28 and 53–57:

```python
INVOICES_REQUIRED_COLUMNS = [
    "invoice_id",
    "customer_name",
    "invoice_date",
    "due_date",
    "invoice_amount",
]
```

```python
def load_invoices(file) -> pd.DataFrame:
    """Load invoices.xlsx into a DataFrame, raising MissingColumnsError if required columns are absent."""
    df = load_excel(file)
    validate_required_columns(df, INVOICES_REQUIRED_COLUMNS, "invoices file")
    return df
```

This is the same loader shape Tutorial 03 and Tutorial 04 both used — `load_excel` plus
`validate_required_columns`, reused unchanged from `excel_io.py`. `paid_amount` is deliberately
absent from `INVOICES_REQUIRED_COLUMNS`, matching the spec's own `Optional` label on that column
(§4) — `test_load_invoices_succeeds_when_paid_amount_column_absent`
(`tests/test_payment_aging.py:355-362`) proves a file missing that column entirely still loads.

Here is a genuine difference from Tutorial 04, worth noticing precisely because it's easy to miss:
`allocate_inventory()` (Phase 4) re-validates required columns itself, independent of whether a
caller went through its loaders first — because its realistic input, `valid_orders_df`, typically
comes from Phase 3's own `validate_orders()` output, which never passes through `load_valid_orders`
at all. Search `calculate_payment_aging()` (lines 193–272) for a call to
`validate_required_columns` — there isn't one. Phase 5 has no equivalent bypass scenario: nothing
in this repo produces an `invoices_df`-shaped DataFrame except `load_invoices()` reading a real
`invoices.xlsx` file, so there's no realistic caller that reaches `calculate_payment_aging()`
without having already gone through the one loader that checks columns. Re-validating defensively
inside `calculate_payment_aging()` would be dead code for any call path this module actually
supports — Phase 4's defensive re-check earns its keep from a real, demonstrated caller pattern
(Tutorial 04 Part 2); Phase 5 doesn't have that caller pattern, so it doesn't carry the same
defense.

**Checkpoint:** Given that Phase 4's `allocate_inventory()` re-validates required columns
internally and Phase 5's `calculate_payment_aging()` doesn't, is Phase 5 less defensively coded, or
is this a correctly different decision for a genuinely different situation?

<details>
<summary>Reveal answer</summary>

It's a correctly different decision, not a lapse. The re-validation in Phase 4 exists because a
*specific, real* call path bypasses `load_valid_orders()` — Phase 3's `validate_orders()` output is
the actual, expected way `valid_orders_df` gets built in this codebase, and that path never touches
a loader. Phase 5 has no analogous path: every `invoices_df` this module will ever realistically
receive was built by `load_invoices()`, because nothing else in the codebase produces one. Adding a
defensive re-check here would be guarding against a scenario that cannot currently happen — code
written for a threat model the codebase doesn't have. If a future feature introduced a second way
to build an `invoices_df` (say, a Phase 5-consuming module the way Phase 4 consumes Phase 3), *that*
would be the moment to reconsider, following the same reasoning Tutorial 04 Part 2 already
established for exactly this kind of call.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k "missing_column or paid_amount_column_absent" -v`
and read both test names — confirm one drops a *required* column (`due_date`) and raises
`MissingColumnsError`, while the other drops the *optional* `paid_amount` column and loads
successfully, the same required-vs-optional loader distinction Tutorial 04 Part 2 covered for
inventory columns.

## Part 3 — `as_of_date` and date anchoring: avoiding time-dependent default arguments

Open [`src/payment_aging.py`](../../../src/payment_aging.py) line 193 and 195:

```python
def calculate_payment_aging(invoices_df: pd.DataFrame, as_of_date: date | None = None) -> PaymentAgingResult:
    """Compute aging, data issues, and draft reminders for every invoice row."""
    effective_date = as_of_date or date.today()
```

Tutorial 02 Part 1 covered why `src/sample_data.py`'s `generate_invoices(reference_date: date |
None = None)` resolves its date inside the function body instead of as a literal default
argument: a default argument expression is evaluated exactly once, at `def` time, so
`def f(x: date = date.today())` would freeze `x` to whatever "today" happened to be the moment the
module was first imported — silently stale for the rest of a long-running process. `as_of_date`
here follows the identical rule, resolved fresh on every call.

The one difference from `generate_invoices()`: there, the resolved `reference_date` needed to be
captured by a nested `offset()` closure, because dozens of row literals each called `offset(days)`
using that one resolved value. Here, `effective_date` is used directly, inline, at the one line
that needs it (line 236, Part 5) — no closure is needed because there's no repeated helper function
capturing the value across many call sites, just a single local variable read wherever the date
arithmetic happens.

Notice also the exact form: `as_of_date or date.today()`, not the more explicit
`as_of_date if as_of_date is not None else date.today()`. Both are safe here specifically because a
`date` object is always truthy in Python — there's no valid `date` value that Python would treat as
falsy, unlike, say, an integer `0` or an empty string, where `x or default` would incorrectly
replace a legitimately falsy-but-valid value with the default. `as_of_date or date.today()` is
concise *and* correct here; the same pattern would be a real bug if `as_of_date`'s type could ever
legitimately be a falsy value the caller intended to keep.

> **Python language — `None`-sentinel resolved without a closure:** The `None`-sentinel default
> pattern from Tutorial 02 reappears here in its simplest form — no nested function needed, because
> the resolved value has exactly one consumer instead of many. This is worth recognizing as the
> same underlying idiom scaled down: the closure in `generate_invoices()` wasn't part of the
> `None`-sentinel pattern itself, it was a separate consequence of that function needing to share
> one resolved value across many row-building call sites.

**Checkpoint:** `test_as_of_date_defaults_to_today_when_not_provided`
(`tests/test_payment_aging.py:337-339`) calls `calculate_payment_aging()` with no `as_of_date` at
all, using a `due_date` of `date.today()`, and asserts `days_overdue == 0` — never a fixed literal
date. Why does this test have to be written this way, rather than asserting a specific
`days_overdue` value?

<details>
<summary>Reveal answer</summary>

A test asserting a literal, hardcoded expected value (e.g. "when run on 2026-07-09, `days_overdue`
should be exactly some fixed number") would only be true on the one day it was written — every
other day the test suite runs, `date.today()` would have moved on and the assertion would be
comparing against a stale expectation. By constructing the invoice's own `due_date` as
`date.today()` at test-run time and asserting a *relationship* (a due date of exactly today
produces `days_overdue == 0`, regardless of what today's actual calendar date is), the test stays
correct on every future day it's ever run — exactly the same technique Tutorial 02 Part 1's
`test_generate_invoices_dates_shift_with_reference_date` used to test the default-resolution branch
without hardcoding a date.
</details>

**Try it yourself:** Run
`uv run python -c "from src.payment_aging import calculate_payment_aging; import pandas as pd; from datetime import date; df = pd.DataFrame([{'invoice_id':'INV-1','customer_name':'T','invoice_date':date(2026,1,1),'due_date':date(2026,1,1),'invoice_amount':100.0,'paid_amount':0.0}]); print(calculate_payment_aging(df, as_of_date=date(2026,2,1))['aging_rows'][0]['days_overdue']); print(calculate_payment_aging(df, as_of_date=date(2026,3,1))['aging_rows'][0]['days_overdue'])"`
and confirm the two printed values differ, both correctly reflecting the gap between the invoice's
fixed `due_date` and each different `as_of_date` — proof `effective_date` is genuinely recomputed
per call, not frozen.

## Part 4 — Paid invoices stay in `aging_rows`, but leave overdue follow-up

Open [`src/payment_aging.py`](../../../src/payment_aging.py) line 234 and lines 128–131:

```python
        # PA-001/PA-002 — outstanding amount can't be sensibly negative; overpayment clamps to 0.
        outstanding_amount = max(invoice_amount - paid_amount, 0.0)
```

```python
def _follow_up_priority(outstanding_amount: float, days_overdue: int) -> str:
    """PA-005 — evaluated in order: Paid, then High (can override bucket), Medium, Low, Watch, None."""
    if outstanding_amount <= 0:
        return "None"
```

PA-002's exact text is "If `outstanding_amount <= 0`, mark invoice as `Paid` and exclude it from
overdue follow-up" — but nothing in that sentence says a Paid invoice should be excluded from the
*aging table itself*. `explanation.md` names three independent signals that resolve this ambiguity
the same way: §6's aging-output-columns table has no carve-out for Paid rows; the downloadable
workbook's sheet 3 is literally named "All Invoices with Aging," a name that only makes sense if
paid invoices are still present; and §7's suggested-actions table has an explicit
`Paid → "No action required"` row, which only has anywhere to live if Paid rows exist in the output
at all. `_follow_up_priority()` checks `outstanding_amount <= 0` *first*, before any day-count
branch runs, returning `"None"` immediately — a Paid invoice can never fall through into Watch or
High even if its due date happens to be far in the past or near-future. The row still gets built
and appended to `aging_rows` normally; only its `follow_up_priority` and `suggested_action` reflect
"nothing to do."

The clamp on line 234 is the other half of this Part: PA-001's formula
(`invoice_amount - paid_amount`) has no explicit floor, so an overpaid invoice
(`paid_amount > invoice_amount`) would mathematically produce a negative `outstanding_amount`.
`explanation.md` reads PA-002's `<=` (not `==`) as a hint the spec's author anticipated this. Rather
than carry a negative "remaining unpaid amount" into the contract — is `-50` a $50 credit, or a
bug? — `max(invoice_amount - paid_amount, 0.0)` clamps it to `0.0`, the same outcome as an exact
payment. `test_overpayment_clamps_outstanding_to_zero`
(`tests/test_payment_aging.py:142-151`) locks this in:

```python
def test_overpayment_clamps_outstanding_to_zero():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=100.0, paid_amount=150.0, due_date=_due(20))),
        as_of_date=AS_OF,
    )
    row = result["aging_rows"][0]
    assert row["outstanding_amount"] == 0.0
    assert row["follow_up_priority"] == "None"
    assert row["suggested_action"] == "No action required"
    assert result["draft_messages"] == []
```

An invoice that's 20 days overdue by due date, but overpaid, still gets `follow_up_priority ==
"None"` — the clamp feeds directly into the same `outstanding_amount <= 0` check, so overpayment
and exact payment are indistinguishable to every rule downstream of `outstanding_amount`, by
design.

> **Algorithms — Clamping:** `max(invoice_amount - paid_amount, 0.0)` is the standard technique for
> forcing a computed value to stay within a valid range — here, "never negative." Clamping the
> *output* of the subtraction, rather than trying to reject or special-case overpayment as an input
> problem, means every current and future cause of a negative result (a typo'd overpayment, a
> genuine partial refund recorded oddly, anything else) is handled uniformly at one place, instead
> of needing a guard at every call site that might produce one.

**Checkpoint:** The decision to keep Paid invoices in `aging_rows` was inferred entirely from three
indirect signals — a sheet name, a suggested-actions table row, and the absence of a carve-out —
none of which is a direct instruction. How confident should an implementation be when a decision
rests entirely on naming and table-shape inference rather than an explicit sentence in the spec?

<details>
<summary>Reveal answer</summary>

Reasonably confident, but for a specific reason: it's not *one* weak signal, it's three
*independent* signals that all point the same direction, from three different parts of the spec
(a sheet name, an output-columns table's silence, and a suggested-actions table's content) that
weren't written with this exact question in mind and would be an odd coincidence to all agree by
chance. A single ambiguous phrase would warrant much lower confidence and probably a documented
open question rather than a silent implementation choice. The right posture matches what actually
happened here: implement the reading three independent signals converge on, but write down the
reasoning explicitly (as `explanation.md` does) so a future domain expert reading it has something
concrete to correct if their real intent diverges — the same posture Tutorial 04 Part 6 used for
the `BACKORDER_ROW_FIXTURE` inference, and Part 10 of this tutorial revisits why that kind of
inference isn't infallible.
</details>

**Failure mode — filtering Paid invoices out of the aging table entirely:** if `_follow_up_priority`
weren't reached at all for Paid rows (say, an early `continue` in the main loop dropped them before
`aging_rows.append(aging_row)` ran), the "All Invoices with Aging" sheet in a future Phase 6 report
would silently become "all *unpaid* invoices," and a customer who fully settled an invoice would
simply vanish from the report a sales admin is reviewing — indistinguishable from an invoice that
was never uploaded at all.

**Try it yourself:** Run `uv run pytest tests/test_payment_aging.py -k paid -v` and read
`test_fully_paid_invoice_marked_paid_no_follow_up` (`tests/test_payment_aging.py:47-56`) — confirm
it asserts the row *exists* in `aging_rows` (`result["aging_rows"][0]`) with a `"None"` priority,
rather than asserting the row is absent.

## Part 5 — Signed `days_overdue` and the Watch window

Open [`src/payment_aging.py`](../../../src/payment_aging.py) line 236 and lines 115–140:

```python
        # PA-003 — signed day count; positive when overdue, negative when due in the future.
        days_overdue = (effective_date - due_date_parsed.date()).days
```

```python
def _aging_bucket(days_overdue: int) -> str:
    """PA-004 — aging bucket from a signed days_overdue value."""
    if days_overdue <= 0:
        return "Current"
    if days_overdue <= 30:
        return "1-30 Days"
    if days_overdue <= 60:
        return "31-60 Days"
    if days_overdue <= 90:
        return "61-90 Days"
    return "90+ Days"


def _follow_up_priority(outstanding_amount: float, days_overdue: int) -> str:
    """PA-005 — evaluated in order: Paid, then High (can override bucket), Medium, Low, Watch, None."""
    if outstanding_amount <= 0:
        return "None"
    if days_overdue > 60 or outstanding_amount >= 50000:
        return "High"
    if 31 <= days_overdue <= 60:
        return "Medium"
    if 1 <= days_overdue <= 30:
        return "Low"
    if -7 <= days_overdue <= 0:
        return "Watch"
    return "None"
```

PA-003's formula is `days_overdue = today_date - due_date`, with a separate sentence — "If
`days_overdue <= 0`, the invoice is not overdue" — describing what to *do* with a non-positive
value, not redefining the value itself. `days_overdue` is never floored: an invoice due five days
from now reports `days_overdue = -5`, not `0`. `explanation.md` names the concrete reason flooring
was rejected: PA-005's Watch rule ("not overdue but due within 7 days") cannot be expressed as a
simple range check on a floored value — a floored `0` collapses "due in 2 days" and "due in 200
days" into the identical number, which would force a second, hidden `days_until_due` calculation
that never surfaces anywhere in the contract. Keeping the signed value means Watch is exactly one
condition, `-7 <= days_overdue <= 0`, using the same field every other rule already computed —
`test_watch_priority_due_within_seven_days` and `test_due_today_is_current_and_watch`
(`tests/test_payment_aging.py:190-203`) both exercise this boundary directly.

The tradeoff: `PaymentAgingRow.days_overdue` can be negative in the JSON contract a future
Next.js UI would consume — a field named "days overdue" that sometimes holds a negative number is
exactly the kind of surprise `plan.md`'s key decisions call out explicitly, so it isn't
rediscovered as a UI bug later.

**Checkpoint:** Flooring `days_overdue` at 0 for non-overdue rows was rejected because it would
collapse "due in 2 days" and "due in 200 days" into the same value, breaking Watch's `-7..0`
window. Is there a comparably clean way to express Watch without a signed field, or was flooring
genuinely a dead end here?

<details>
<summary>Reveal answer</summary>

Genuinely a dead end for a *single*-field design. The only way to preserve Watch's information
need with a floored `days_overdue` would be to introduce a second field (something like
`days_until_due`, populated only for not-yet-due invoices) — which trades one honest signed field
for two fields that are only ever meaningful in mutually exclusive situations, adds a
`PaymentAgingRow` contract field the spec never names (a Field Scope Boundary violation), and still
requires the *consumer* to know which of the two fields to check depending on the row's status.
The signed single-field design is strictly simpler: one field, one meaning ("gap between due date
and today, sign included"), usable by every downstream rule without a second lookup.
</details>

**Checkpoint:** `PaymentAgingRow.days_overdue: int` can now be negative in the JSON contract a
future Next.js UI consumes. What's the risk that a naive frontend renders a negative value as
literal text ("-5 days overdue") instead of translating it to "due in 5 days," and whose job is it
to prevent that — the Python layer, the API layer, or the UI layer?

<details>
<summary>Reveal answer</summary>

The risk is real and specifically a *UI-layer* responsibility, not something Python or the API
should paper over. `days_overdue` is deliberately kept as the mathematically honest signed value
all the way through the contract — per `CLAUDE.md`'s Output Contract rules, business-readable
*phrasing* decisions belong to the presentation layer, not the data layer; Python's job is to
compute the correct number, and a UI component's job is to decide how to *word* a negative one
("due in 5 days" vs. a raw "-5"). Pushing that translation into Python (e.g., returning a
pre-formatted string instead of a signed int) would mean the field is no longer usable for sorting,
filtering, or arithmetic by any future consumer — exactly the same reasoning behind Tutorial 03's
rule that business-readable *error messages* belong in the contract while formatting-for-display
does not. The concrete guard: a future UI component rendering this field needs a conditional
("if negative, phrase as due-in-N-days") — that component simply doesn't exist yet in this
project's current scope, so this is a named, deliberate gap, not an oversight.
</details>

**Failure mode — flooring `days_overdue` at 0 breaks Watch:** if a future refactor "cleaned up" the
signed value into `max(days_overdue, 0)`, every invoice due within the next 7 days would silently
collapse into the same `0` as an invoice due in 6 months — `_follow_up_priority`'s
`-7 <= days_overdue <= 0` check would still technically run, but every not-yet-due invoice would
report exactly `0`, so *every* invoice with any future due date would incorrectly read as "due
today" and get flagged Watch, rather than only the ones genuinely within the 7-day window.

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k "watch or current_invoice_future" -v` and read
`test_current_invoice_future_due_date_is_current_bucket`
(`tests/test_payment_aging.py:68-75`), which uses a due date 30 days in the future — confirm its
`follow_up_priority` is `"None"`, not `"Watch"`, proving the 7-day boundary is a real cutoff, not
"any future date."

## Part 6 — Bucket calculation vs. priority calculation, including amount-driven High priority

Re-read `_aging_bucket()` and `_follow_up_priority()` from Part 5 side by side. They both take
`days_overdue` (and `_follow_up_priority` additionally takes `outstanding_amount`), but they are
two genuinely independent calculations, not one derived from the other — a row's `aging_bucket` and
`follow_up_priority` can disagree, and the spec's own §12 test table has a standalone case proving
it's meant to: `test_75_days_overdue_is_61_90_days_but_high_priority`
(`tests/test_payment_aging.py:94-99`):

```python
def test_75_days_overdue_is_61_90_days_but_high_priority():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(75))), as_of_date=AS_OF)
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "61-90 Days"
    assert row["follow_up_priority"] == "High"
```

`_aging_bucket` places 75 days overdue in the `"61-90 Days"` bucket — a purely descriptive,
duration-based classification. `_follow_up_priority`'s `days_overdue > 60` branch independently
returns `"High"` for the same row — the two functions happen to agree here, but only because 75
crosses both thresholds. PA-005's High condition — `days_overdue > 60 or outstanding_amount >=
50000` — is an unconditional `or`, with no accompanying "and is overdue" clause at all.
`test_large_outstanding_amount_forces_high_priority_at_low_day_count`
(`tests/test_payment_aging.py:109-115`) proves the two functions can genuinely diverge:

```python
def test_large_outstanding_amount_forces_high_priority_at_low_day_count():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=_due(5), invoice_amount=60000.0)), as_of_date=AS_OF
    )
    row = result["aging_rows"][0]
    assert row["aging_bucket"] == "1-30 Days"
    assert row["follow_up_priority"] == "High"
```

An invoice only 5 days overdue lands in the `"1-30 Days"` bucket by `_aging_bucket`'s purely
duration-based rule, but `_follow_up_priority`'s `outstanding_amount >= 50000` branch fires
independent of the day count, producing `"High"` anyway. Combined with Part 5's signed
`days_overdue`, this goes further still: an invoice not yet even due (`days_overdue` negative,
`aging_bucket = "Current"`) with a large enough `outstanding_amount` evaluates to `follow_up_priority
= "High"`. `explanation.md` treats this as intentional, not an oversight to "fix" by adding an
implicit "and overdue" clause — the spec's §12 test table lists the amount trigger as its own
standalone case, independent of every days-overdue test case, which is the same kind of signal
Part 4 used to justify keeping Paid rows visible: read literally, and trust the pattern in how the
spec's own test cases are organized.

> **Design patterns — First-match-wins dispatch, contrasted with Tutorial 03's independent rule
> evaluation:** `_follow_up_priority`'s `if`/`elif`-shaped chain returns on the *first* matching
> condition and never evaluates the rest — the opposite shape from Tutorial 03's `_validate_row`,
> where every OV rule runs independently and a row can accumulate several simultaneous findings.
> The difference isn't arbitrary: `follow_up_priority` is fundamentally a single, mutually-exclusive
> label (an invoice has exactly one priority), so chain order becomes a real design decision — Paid
> is checked before High specifically so a Paid invoice's large `outstanding_amount` (impossible by
> construction, since Paid means `outstanding_amount <= 0`, but the ordering still documents intent)
> can never override "nothing to follow up on." Order validation's errors are the opposite shape
> because a row genuinely *can* have several independent problems at once, and collapsing them to
> "the first one found" would throw away real information (Tutorial 03 Part 4).

**Checkpoint:** High priority can fire from `outstanding_amount >= 50000` alone, completely
independent of `days_overdue` — including on an invoice that isn't due yet (`aging_bucket =
"Current"`, `follow_up_priority = "High"`). If a domain expert looked at a "Current, High priority"
row in the report, would that read as intentional urgency or as a bug — and does the literal-spec-
reading defense actually survive that reaction?

<details>
<summary>Reveal answer</summary>

It would very plausibly read as a bug to someone seeing it cold, which is exactly why this decision
is worth flagging explicitly rather than assuming the literal reading is self-evidently correct
(as `explanation.md` does, in writing, rather than silently). The literal-reading defense survives
on the *evidence* — an independent, standalone test case in the spec's own §12 table — but it
doesn't survive on *intuition alone*, and intuition is exactly what a domain expert reviewing the
report would apply. This is a case where "implemented correctly per the spec" and "obviously
correct to a first-time reader" diverge, which argues for a UI-level affordance eventually (e.g., a
tooltip or a distinct visual treatment explaining *why* a Current invoice is High priority) rather
than for silently softening the rule to require `days_overdue > 0` — that would be quietly
overriding a signal the spec's own test table provides, on the theory that the surface reading
"feels wrong," which is a weaker basis than the spec's own explicit standalone case.
</details>

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k "aging_bucket_and_priority_boundaries" -v` and read
the six parametrized cases (`tests/test_payment_aging.py:214-231`) — for each, note whether
`aging_bucket` and `follow_up_priority` land on the "same" threshold day or a different one, and
confirm every boundary (30/31, 60/61, 90/91) is tested on both sides.

## Part 7 — Draft-message eligibility diverges from priority

Open [`src/payment_aging.py`](../../../src/payment_aging.py) lines 257–263:

```python
        # Draft reminders only for invoices that are actually overdue with an active follow-up.
        if outstanding_amount > 0 and days_overdue > 0 and follow_up_priority in ("High", "Medium", "Low"):
            draft_messages.append(
                _build_draft_message(
                    invoice_id, customer_name, outstanding_amount, days_overdue, row.get("currency")
                )
            )
```

Part 6 established that `follow_up_priority` can be `"High"` on an invoice that isn't overdue at
all (`days_overdue <= 0`, triggered by amount alone). This guard is where that literal reading
stops being allowed to propagate further: a draft message requires *all three* conditions —
`outstanding_amount > 0` (excludes Paid), `days_overdue > 0` (excludes Watch and Current — the
one condition `follow_up_priority` itself never required), and `follow_up_priority in ("High",
"Medium", "Low")` (excludes Watch and None explicitly by value, even though Watch already fails the
`days_overdue > 0` check on its own). Spec §8's exact words are "a draft message for each *overdue*
customer" — an unambiguous, single condition this guard enforces directly, even though PA-005's
priority rule itself carries no such restriction.

`test_draft_message_generated_only_for_overdue_high_medium_low`
(`tests/test_payment_aging.py:247-259`) exercises every excluded category in one batch:

```python
def test_draft_message_generated_only_for_overdue_high_medium_low():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(invoice_id="INV-PAID", invoice_amount=100.0, paid_amount=100.0, due_date=_due(20)),
            _invoice_row(invoice_id="INV-CURRENT", due_date=_due(-30)),
            _invoice_row(invoice_id="INV-WATCH", due_date=_due(-5)),
            _invoice_row(invoice_id="INV-ISSUE", due_date=None),
            _invoice_row(invoice_id="INV-LOW", due_date=_due(20)),
        ),
        as_of_date=AS_OF,
    )
    assert len(result["draft_messages"]) == 1
    assert result["draft_messages"][0]["invoice_id"] == "INV-LOW"
```

Five rows, five different reasons to be excluded except the last: Paid (`outstanding_amount <= 0`),
Current (`days_overdue <= 0`, no urgency), Watch (`days_overdue <= 0`, technically not yet overdue),
a data-issue row (never reaches `aging_rows` at all — Part 8), and only `INV-LOW`, genuinely
overdue with a Low priority, produces a message.

**Checkpoint:** Draft messages deliberately don't follow the same "amount alone triggers it" logic
as priority — a High-priority-by-amount, not-yet-due invoice gets no draft reminder, because
section 8 only describes reminders "for each overdue customer." Now that priority and
reminder-eligibility diverge on purpose, is there a risk a future feature (e.g. a "Follow-up List"
UI view) accidentally uses `follow_up_priority == "High"` as its filter and pulls in a not-yet-due
invoice that was never meant to appear there?

<details>
<summary>Reveal answer</summary>

Yes, and it's a real, concrete risk rather than a hypothetical one — precisely because
`follow_up_priority == "High"` is a single, easy-to-reach-for filter condition that reads as
obviously correct ("show me the high-priority ones"), while the *actual* eligibility rule this
module encodes is a three-part condition (`outstanding_amount > 0 and days_overdue > 0 and
follow_up_priority in {...}`) that only exists inside `_build_draft_message`'s call-site guard, not
as a queryable field anywhere in `PaymentAgingRow` itself. A future UI or report feature filtering
on priority alone would silently resurface the exact "Current, High priority" row Part 6's
checkpoint just discussed, in a context (a follow-up action list) where its presence is far more
likely to read as a bug than in the raw aging table. The safest guard against this: any future
consumer that wants "who should get a reminder" should re-derive or reuse this exact three-part
condition, not assume `follow_up_priority` alone answers that question — worth calling out
explicitly in this module's docstring or a future `CONTEXT.md` glossary entry distinguishing
"Follow-up Priority" from "Reminder Eligibility" as genuinely different concepts, exactly the kind
of naming clarity `CONTEXT.md`'s existing glossary entries (`Anonymous Session ID` vs. `User ID`,
etc.) already practice elsewhere in this project.
</details>

**Failure mode — treating High priority as equivalent to draft-message eligibility:** if a future
route handler or UI generated a reminder for every `follow_up_priority == "High"` row without also
checking `days_overdue > 0`, a customer whose invoice isn't due for another three weeks — but
happens to be large — would receive a reminder about money that isn't even late yet, which reads as
a real customer-relations mistake, not a cosmetic UI bug.

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k draft_message_generated -v -s` and manually verify,
for each of the five constructed rows in the test, which of the three guard conditions
(`outstanding_amount > 0`, `days_overdue > 0`, `follow_up_priority in {...}`) it fails — confirm
`INV-CURRENT` and `INV-WATCH` both fail specifically on `days_overdue > 0`, the one condition
`follow_up_priority` itself never enforces.

## Part 8 — Data issues: PA-006/PA-007 soft failures, invalid `invoice_amount`, and forgiving `paid_amount`

Open [`src/payment_aging.py`](../../../src/payment_aging.py) lines 208–223 and 88–97:

```python
        # PA-006 / PA-007 — evaluated independently; a row can have both issues.
        row_issues: list[PaymentDataIssueRow] = []
        if due_date_parsed is None:
            row_issues.append(
                _build_data_issue(invoice_id_value, customer_name_value, "PA-006", "Due date is missing.")
            )
        if invoice_amount is None or invoice_amount < 0:
            row_issues.append(
                _build_data_issue(
                    invoice_id_value, customer_name_value, "PA-007", "Invoice amount is missing or invalid."
                )
            )

        if row_issues:
            data_issues.extend(row_issues)
            continue
```

```python
def _parse_amount(value: object) -> float | None:
    """Return a float amount, or None if the value is blank, non-numeric, or a bool."""
    if _is_blank(value) or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None
```

This is Tutorial 04 Part 2's "no contract, so raise instead" situation resolved the opposite way.
`docs/adr/0005-payment-data-issue-row-contract.md` exists specifically because Phase 1's original
output-family list had no equivalent for payment-aging data issues — an oversight the ADR calls out
directly, not a deliberate scope exclusion, since the spec unambiguously requires this output
(PA-006, PA-007, a `Data Issues` sheet, and an explicit error-state UI description all name it).
With `PaymentDataIssueRow` available, a row that fails PA-006 and/or PA-007 doesn't raise — it's
soft-collected into `data_issues` and the loop moves on via `continue`, never reaching
`aging_rows.append(...)`. `row_issues` is built as a small list, not a single check, specifically
because PA-006 (missing due date) and PA-007 (invalid amount) are evaluated independently — the same
"one row, multiple simultaneous findings" shape Tutorial 03 Part 4 established for OV-001,
applied here at the two-rule scale instead of eight:

```python
def test_row_with_missing_due_date_and_invalid_amount_produces_two_data_issues():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(due_date=None, invoice_amount=-10.0)), as_of_date=AS_OF
    )
    assert result["aging_rows"] == []
    codes = {issue["error_code"] for issue in result["data_issues"]}
    assert codes == {"PA-006", "PA-007"}
    assert len(result["data_issues"]) == 2
```

> **Design patterns — Guard clause for single-pass partitioning:** `if row_issues:
> data_issues.extend(row_issues); continue` is a guard clause — the disqualifying condition is
> checked early, and `continue` makes "this row is a data issue" a dead end for the rest of that
> iteration. Nothing after this line can run for a disqualified row in this pass, which is what
> guarantees every row lands in exactly one of `aging_rows` or `data_issues`: there's no `if/else`
> split where a future edit could accidentally add shared code that runs for both branches.

Now the asymmetry the Part's title promises: `invoice_amount` and `paid_amount` are both governed
by PA-001's rule family, and both get parsed through the identical `_parse_amount()` helper — but
only `invoice_amount`'s failure produces a `PaymentDataIssueRow`. `paid_amount`'s failure degrades
silently, at line 230–231:

```python
        # PA-001 — paid_amount is optional; missing/non-numeric/negative all default to 0.
        paid_amount_parsed = _parse_amount(row.get("paid_amount"))
        paid_amount = paid_amount_parsed if paid_amount_parsed is not None and paid_amount_parsed >= 0 else 0.0
```

PA-007's text names one field explicitly: "If invoice amount is missing or less than 0, flag as
error." PA-001 only documents one `paid_amount` failure mode — "If `paid_amount` is missing, treat
it as 0" — with no equivalent "and if invalid, flag as error" clause. Two tests exist specifically
to lock this asymmetry in and stop a future "tightening":

```python
def test_invalid_paid_amount_degrades_to_zero_no_data_issue():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=1000.0, paid_amount="abc")), as_of_date=AS_OF
    )
    assert result["data_issues"] == []
    row = result["aging_rows"][0]
    assert row["paid_amount"] == 0.0
    assert row["outstanding_amount"] == 1000.0
```

`explanation.md` connects this directly to Tutorial 04's required-vs-optional inventory field split
(`sku`/`warehouse`/`available_qty` raise; `reserved_qty`/`reorder_point`/`lead_time_days` degrade) —
the same asymmetry principle, one level softer here, since Phase 5 has a contract to report the
required-field failure *softly* where Phase 4 had to raise a hard exception.

**Checkpoint:** This mirrors Phase 4's required-vs-optional field split, but Phase 5 has a
`PaymentDataIssueRow` contract to report failures softly where Phase 4 had to raise a hard
exception. Does having a soft-failure contract available change what "should" happen to an invalid
optional field like `paid_amount`, or is "the spec never says to flag it" still the right bar
regardless of whether flagging it would be easy?

<details>
<summary>Reveal answer</summary>

"The spec never says to flag it" stays the right bar, and the existence of an easy mechanism to do
so doesn't change that — the Field Scope Boundary and Scope Gate principles this project applies
elsewhere are explicit that *capability* to implement something isn't the same as *authorization*
to implement it. If having `PaymentDataIssueRow` available made every optional field a candidate for
soft-flagging "since it's easy now," that would be scope creep flowing from implementation
convenience rather than from the spec — the same failure mode the Scope Gate exists to prevent for
V1.5/V2 rules, just arriving from a different direction (an available contract, not a tempting
adjacent rule). The bar for *when* to flag a field stays "the spec says to," independent of how
cheap flagging would be to add.
</details>

**Checkpoint:** Two explicit tests (`test_invalid_paid_amount_degrades_to_zero_no_data_issue`,
`test_negative_paid_amount_degrades_to_zero_no_data_issue`) exist specifically to stop a future
agent from "tightening" this behavior to match `invoice_amount`'s. Is a named regression test
actually a strong enough guardrail against scope creep, compared to, say, a comment at the
validation site itself?

<details>
<summary>Reveal answer</summary>

They're complementary, not substitutes, and this codebase actually uses both — line 229's comment
("`paid_amount` is optional; missing/non-numeric/negative all default to 0") documents intent at
the point of decision, while the two named tests are what actually *fails loudly* if someone
changes the behavior without reading the comment first. A comment alone is advisory — nothing stops
a future edit from changing the code while leaving a now-inaccurate comment untouched. A test alone
states a fact about current behavior but, without the comment, doesn't explain *why* that behavior
is deliberate rather than an oversight worth "fixing" — someone could see the test, correctly
conclude it needs updating, and update both the code and the assertion together, unaware they just
implemented unauthorized scope. The comment supplies the "why" a bare test can't; the test supplies
the enforcement a bare comment can't. Test names this explicit about their own purpose
(`_no_data_issue`, not just `_degrades_to_zero`) are doing some of a comment's explanatory work
themselves, which is a reasonable middle ground.
</details>

**Failure mode — flagging invalid `paid_amount` as PA-007 despite the spec only naming
`invoice_amount`:** if a future edit changed line 231's fallback to instead raise a
`PaymentDataIssueRow` for any unparseable `paid_amount`, every invoice with a blank `paid_amount`
cell — which the sample data and any realistic upload will have plenty of, since it's genuinely
optional — would incorrectly vanish from `aging_rows` into `data_issues`, silently shrinking the
aging table for a condition (a blank optional field) PA-001 explicitly says should just mean "0,"
not "error."

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k "invalid_paid_amount or negative_paid_amount" -v`
and confirm both pass with `data_issues == []` — then temporarily change line 231 to
`paid_amount = paid_amount_parsed if paid_amount_parsed is not None else 0.0` (dropping the
`>= 0` check) and re-run just `test_negative_paid_amount_degrades_to_zero_no_data_issue` — confirm
it still passes (a negative `paid_amount_parsed` still isn't `None`), then check whether
`row["paid_amount"]` in the test's assertion still holds — this exposes exactly what the `>= 0`
guard is protecting against. Revert the change afterward.

## Part 9 — Summary semantics: total loaded rows vs. aggregates over valid aging rows

Open [`src/payment_aging.py`](../../../src/payment_aging.py) lines 170–190 and line 265:

```python
def _build_summary(total_invoices: int, aging_rows: list[PaymentAgingRow]) -> PaymentAgingSummary:
    aging_bucket_counts = {bucket: 0 for bucket in _AGING_BUCKET_ORDER}
    total_outstanding_amount = 0.0
    overdue_amount = 0.0
    high_priority_count = 0

    for row in aging_rows:
        aging_bucket_counts[row["aging_bucket"]] += 1
        total_outstanding_amount += row["outstanding_amount"]
        if row["days_overdue"] > 0:
            overdue_amount += row["outstanding_amount"]
        if row["follow_up_priority"] == "High":
            high_priority_count += 1

    return {
        "total_invoices": total_invoices,
        "total_outstanding_amount": total_outstanding_amount,
        "overdue_amount": overdue_amount,
        "high_priority_count": high_priority_count,
        "aging_bucket_counts": aging_bucket_counts,
    }
```

```python
    summary = _build_summary(len(invoices_df), aging_rows)
```

`total_invoices` is passed in as `len(invoices_df)` — the raw row count of the *entire loaded
file*, before any PA-006/PA-007 filtering happens. Every other field in `PaymentAgingSummary` is
computed exclusively from `aging_rows`, the post-filter list. This mirrors Tutorial 03 Part 7's
`invalid_orders` semantics precisely: `ValidationSummary.total_orders` also counts every loaded
row, valid or not, while `duplicate_orders`/`invalid_skus`/`missing_field_count` are all derived
from the (also complete) `errors` list — but Phase 5 pushes the same idea one step further, because
here an *entire category of rows* (anything in `data_issues`) is structurally absent from every
aggregate except `total_invoices` itself, not just undercounted within one summary field the way
Tutorial 03's distinct-count fix addressed a double-counting risk *within* a single list.

`_AGING_BUCKET_ORDER` (line 32) is `["Current", "1-30 Days", "31-60 Days", "61-90 Days", "90+
Days"]`, and `aging_bucket_counts = {bucket: 0 for bucket in _AGING_BUCKET_ORDER}` seeds every one
of those five keys to `0` *before* the loop over `aging_rows` runs. This guarantees
`aging_bucket_counts` always exposes all five keys, even when a bucket has zero rows in it —
`test_aging_bucket_counts_always_has_all_five_keys` (`tests/test_payment_aging.py:234-244`) checks
exactly this:

```python
def test_aging_bucket_counts_always_has_all_five_keys():
    result = calculate_payment_aging(_invoices_df(_invoice_row(due_date=_due(20))), as_of_date=AS_OF)
    assert set(result["summary"]["aging_bucket_counts"].keys()) == {
        "Current",
        "1-30 Days",
        "31-60 Days",
        "61-90 Days",
        "90+ Days",
    }
    assert result["summary"]["aging_bucket_counts"]["1-30 Days"] == 1
    assert result["summary"]["aging_bucket_counts"]["90+ Days"] == 0
```

Without the pre-seeded dict comprehension, a batch with no invoice in, say, the `"90+ Days"` bucket
would simply omit that key entirely — forcing any future chart or KPI card to defensively handle a
missing key instead of trusting the shape is always complete, exactly the kind of "and nothing
else" guarantee a future UI needs but a naive `{}`-then-`setdefault`-as-you-go approach wouldn't
provide up front.

> **Data structures — Dict comprehension for guaranteed key coverage:** Seeding every expected key
> to a default value *before* populating from real data (`{k: 0 for k in fixed_keys}`, then
> incrementing) is the standard technique whenever a consumer needs a complete, predictable shape
> regardless of what the input data actually contains — the alternative, building the dict
> incrementally only as keys are encountered, would produce a dict whose *shape itself* varies with
> the data, which is a much harder contract for a chart component (needing five bars, not "however
> many buckets happened to have rows") to consume safely.

`test_total_invoices_counts_all_rows_including_data_issues`
(`tests/test_payment_aging.py:293-303`) proves the split directly:

```python
def test_total_invoices_counts_all_rows_including_data_issues():
    result = calculate_payment_aging(
        _invoices_df(
            _invoice_row(invoice_id="INV-VALID", due_date=_due(10)),
            _invoice_row(invoice_id="INV-ISSUE", due_date=None),
        ),
        as_of_date=AS_OF,
    )
    assert result["summary"]["total_invoices"] == 2
    assert len(result["aging_rows"]) == 1
    assert sum(result["summary"]["aging_bucket_counts"].values()) == 1
```

`total_invoices == 2`, but the bucket counts sum to `1` — the row with the missing due date
contributes to the first number and not the second, on purpose.

**Checkpoint:** `total_invoices` counts every loaded row including data-issue rows, but
`aging_bucket_counts` only counts `aging_rows`. A screen showing "10 total invoices" next to a
bucket breakdown that sums to 8 could read as a bug to someone unfamiliar with the PA-006/PA-007
exclusion. Is that a UI-labeling problem to solve later (e.g. an explicit "2 invoices need
attention" callout), or should the Python summary itself expose a reconciling count?

<details>
<summary>Reveal answer</summary>

It's a UI-labeling problem, not a data-shape problem, and the reconciling count already exists —
it's simply `total_invoices - sum(aging_bucket_counts.values())`, or equivalently
`len(data_issues)`, both trivially derivable by any consumer that already has the full
`PaymentAgingResult` in hand. Adding a redundant `reconciled_count` or `issues_count` field
directly to `PaymentAgingSummary` would be adding a contract field the spec never defines purely
for UI convenience — exactly the kind of "add a field for symmetry/convenience" the Field Scope
Boundary warns against, when the same information is one subtraction away from data the consumer
already has. The right fix lives in the presentation layer: a future dashboard should surface *why*
the two numbers differ (e.g., a small "2 invoices need attention" callout linking to
`data_issues`), the same "presentation vs. business logic" boundary Tutorial 04's report-export
discussion in `context/code-standards.md` already draws — Python's job stops at producing correct,
complete numbers; explaining their relationship to a human is a UI concern.
</details>

**Failure mode — bucket breakdowns appearing inconsistent with `total_invoices` without explaining
data-issue exclusion:** if a future dashboard displayed "Total Invoices: 10" directly above a bucket
chart whose bars visibly sum to 8, with no visible link to the 2 excluded rows, a reviewer would
reasonably suspect a counting bug in the Python layer rather than correctly inferring "2 rows have
data issues" — the gap is real and intentional, but silent about *why* unless the UI actively
surfaces it.

**Try it yourself:** Run
`uv run pytest tests/test_payment_aging.py -k "total_invoices_counts_all_rows" -v` and then, in a
Python shell, compute `result["summary"]["total_invoices"] - sum(result["summary"]
["aging_bucket_counts"].values())` for the same two-row batch — confirm it equals
`len(result["data_issues"])` exactly, proving the "missing" count is always recoverable from data
already in the envelope.

## Part 10 — Fixture correction: currency-aware message text and a one-day sample-data mismatch

Open [`src/payment_aging.py`](../../../src/payment_aging.py) lines 143–146:

```python
def _format_amount(amount: float, currency_value: object) -> str:
    if not _is_blank(currency_value):
        return f"{_to_trimmed_str(currency_value)} {amount:,.2f}"
    return f"{amount:,.2f}"
```

`tests/contract_fixtures.py`'s `DRAFT_MESSAGE_ROW_FIXTURE` was hand-authored in Phase 2, before
`payment_aging.py` existed, and originally rendered its `message_text` with a hardcoded `$58,000.00`
— but the invoice it describes (`INV-2026-001`) is generated by
[`src/sample_data.py`](../../../src/sample_data.py)'s `generate_invoices()` with `"currency":
"HKD"` (line 157). Nobody had implemented the aging module yet to catch the mismatch; the fixture's
`$` was simply wrong for its own example row from the moment it was written. `DraftMessageRow`'s
contract fields don't include `currency` as a structured field — adding one would violate the Field
Scope Boundary, since §8 of the spec never defines a `currency` output field, only a
`[Outstanding Amount]` placeholder in free-form message text. `_format_amount()` reads the
invoice's own `currency` input column — already in hand, since `calculate_payment_aging()` iterates
the same row that carries it — and prefixes it onto the formatted number, falling back to a bare
number when `currency` is blank:

```python
def test_draft_message_currency_formatting_without_currency():
    result = calculate_payment_aging(
        _invoices_df(_invoice_row(invoice_amount=5000.0, paid_amount=0.0, due_date=_due(10), currency=None)),
        as_of_date=AS_OF,
    )
    message = result["draft_messages"][0]["message_text"]
    assert "5,000.00" in message
    assert "$" not in message
```

The fixture was corrected to match — `tests/contract_fixtures.py`'s current
`DRAFT_MESSAGE_ROW_FIXTURE.message_text` reads "...outstanding amount of HKD 58,000.00...", not
`$58,000.00`.

A second, independent mismatch surfaced the same way. Running `calculate_payment_aging()` against
the real, committed `sample_data/sample_invoices.xlsx` with `as_of_date=date(2026, 7, 9)` — the
date `generate_invoices()` was actually run with — reproduced every *computed* value in
`PAYMENT_AGING_ROW_FIXTURE` exactly (`days_overdue=70`, `outstanding_amount=58000.0`,
`aging_bucket="61-90 Days"`, `follow_up_priority="High"`, `suggested_action="Call or email
customer urgently"`), but `invoice_date` and `due_date` were each off by one calendar day —
`"2026-04-01"`/`"2026-05-01"` in the original fixture versus the real, computed
`"2026-03-31"`/`"2026-04-30"`. Every value that depended on *business logic* matched field-for-
field; only the two literal date strings, which the fixture's author had to type out by hand before
`generate_invoices()`'s exact offset arithmetic existed, were wrong. Both strings were corrected in
`tests/contract_fixtures.py` — the fix was to the fixture, not to `payment_aging.py`'s date math.

This is the same category of check Tutorial 04 Part 6 performed with `BACKORDER_ROW_FIXTURE` — a
hand-authored Phase 2 fixture used as an independent sanity check against real business logic —
except this time the check *caught a pre-existing mistake* in the fixture rather than confirming a
clean match immediately. Tutorial 04 treated `BACKORDER_ROW_FIXTURE`'s populated `warehouse` field
on a zero-allocation row as trustworthy evidence for an ambiguous design decision (the fixture
"won" because nothing contradicted it). This Part is the counter-example: the same category of
artifact, from the same phase, turned out to be simply wrong, twice, in ways nothing caught until a
later phase's implementation ran a real computation against it.

**Checkpoint:** Phase 2's `DRAFT_MESSAGE_ROW_FIXTURE` hardcoded a `$` symbol for an invoice that's
actually HKD — a mistake that existed, uncaught, from Phase 2 until Phase 5's implementation and
sanity check surfaced it. Tutorial 04 treated a similar pre-existing fixture (`BACKORDER_ROW_
FIXTURE`) as authoritative evidence for an ambiguous design decision. Given that fixtures can
themselves be wrong, what should change about how much weight a hand-authored Phase 2 fixture gets
when it conflicts with, or is used to resolve, a Phase 3+ implementation decision?

<details>
<summary>Reveal answer</summary>

The weight a fixture deserves should scale with what kind of claim it's making, not with the mere
fact that it predates the implementation. `BACKORDER_ROW_FIXTURE`'s populated `warehouse` field was
evidence about a *structural* decision — what shape the data should take, a decision with no
"correct" computed answer to check against, only intent — and a hand-authored example genuinely is
the best available evidence for that kind of question, precisely because a human had to think about
what the row *should* contain. `DRAFT_MESSAGE_ROW_FIXTURE`'s `$` symbol and the one-day-off dates,
by contrast, are claims about a *computable* fact — what a specific currency code or offset
arithmetic actually produces — and those are exactly the kind of claim a fixture can get simply
wrong by typo, independent of any design intent at all. The practical rule: trust a Phase 2 fixture
as strong evidence for "what was this module supposed to produce, when the spec itself doesn't
fully say" (structural/intentional questions), but treat it as a *hypothesis to verify*, not a
ground truth, for anything that's actually computable from inputs the fixture also specifies —
verify it the same way Phase 5's sanity check did, by actually running the real function and
diffing.
</details>

**Checkpoint:** The `invoice_date`/`due_date` one-day discrepancy was caught only because the
sanity check happened to compare the *exact* real sample file's output against the fixture. If
that manual check weren't run, would the mismatch have been caught by anything in
`tests/test_contracts.py` or `tests/test_payment_aging.py`, or does it reveal a gap in what the
automated suite actually verifies?

<details>
<summary>Reveal answer</summary>

No automated test in either file would have caught it, and this does reveal a real, specific gap.
`tests/test_contracts.py` only checks that `PAYMENT_AGING_ROW_FIXTURE`'s *keys* match
`PaymentAgingRow`'s declared shape (Tutorial 01 Part 6) — it has no concept of whether the
*values* are internally consistent with each other or with any real data source, since fixture-
shape testing is explicitly scoped to "can this TypedDict hold believable data," not "is this
specific example correct." `tests/test_payment_aging.py`'s inline DataFrame fixtures are entirely
independent of `PAYMENT_AGING_ROW_FIXTURE` — per Tutorial 02 Part 3's fixture/generator
independence principle, they're deliberately never derived from or compared against it, so a wrong
value in one has no path to ever surface through the other. The gap this reveals: nothing in the
automated suite cross-checks a hand-authored contract-fixture example against what the real,
computed pipeline actually produces for the same real input — that check only exists as a manual,
one-off verification step recorded in `plan.md`'s "Scope boundary held" section, not as a
repeatable, automated test. A `test_payment_aging_row_fixture_matches_real_sample_data` test that
runs `calculate_payment_aging()` against the committed `sample_data/sample_invoices.xlsx` and diffs
`INV-2026-001`'s row against `PAYMENT_AGING_ROW_FIXTURE` would close exactly this gap — and would
have caught both mistakes automatically, on every future `uv run pytest`, instead of relying on
someone remembering to check by hand again.
</details>

**Failure mode — trusting Phase 2 fixtures blindly after Phase 5 proved some fixture values were
wrong:** if a future phase (Phase 6's report export, or a UI mock-data pipeline) copied field
values directly out of `PAYMENT_AGING_ROW_FIXTURE` or `DRAFT_MESSAGE_ROW_FIXTURE` *before* Phase
5's corrections landed, it would have propagated both the wrong currency symbol and the wrong dates
into a second location — exactly the "two independent implementations can silently diverge" risk
Tutorial 02 Part 3 named for fixtures derived from each other, except here the risk runs through
copy-paste of a fixture's *literal values* into new code, not through one fixture computing from
another.

**Try it yourself:** Open [`tests/contract_fixtures.py`](../../../tests/contract_fixtures.py) and
find `PAYMENT_AGING_ROW_FIXTURE` and `DRAFT_MESSAGE_ROW_FIXTURE` — confirm `invoice_date` reads
`"2026-03-31"` (not `"2026-04-01"`) and `message_text` contains `"HKD 58,000.00"` (not
`"$58,000.00"`) in the current file. Then run
`uv run python -c "from src.payment_aging import calculate_payment_aging; from src.excel_io import load_excel; from datetime import date; df = load_excel('sample_data/sample_invoices.xlsx'); r = calculate_payment_aging(df, as_of_date=date(2026,7,9)); row = next(x for x in r['aging_rows'] if x['invoice_id']=='INV-2026-001'); print(row['invoice_date'], row['due_date'])"`
and confirm the printed dates match the corrected fixture, not the original typo'd one.

## Full data flow: one overdue invoice, start to finish

Trace `INV-2026-777` (built the same way `_invoice_row(**overrides)` constructs test rows,
matching `test_draft_message_currency_formatting_with_currency`,
`tests/test_payment_aging.py:262-280`) through every stage:

```python
{
    "invoice_id": "INV-2026-777",
    "customer_name": "Acme Co",
    "invoice_date": date(2026, 6, 1),
    "due_date": _due(20),          # 20 days before AS_OF = date(2026, 7, 9)
    "invoice_amount": 12345.67,
    "paid_amount": 0.0,
    "currency": "SGD",
}
```

1. **`load_invoices()`.** In a real workflow, `load_invoices(file)`
   (`src/payment_aging.py:53-57`) loads `invoices.xlsx` and validates
   `INVOICES_REQUIRED_COLUMNS` are present. This row has every required column, so loading
   succeeds unremarkably (Part 2).
2. **`calculate_payment_aging()` entry.** `effective_date = as_of_date or date.today()`
   (line 195) resolves to `AS_OF = date(2026, 7, 9)`, the value explicitly passed in this trace
   (Part 3).
3. **Date/amount parsing.** `_parse_date(row.get("due_date"))` (line 205) succeeds —
   `due_date_parsed` is a valid `Timestamp`. `_parse_amount(row.get("invoice_amount"))`
   (line 206) succeeds — `invoice_amount = 12345.67`.
4. **PA-006/PA-007 issue gate.** `due_date_parsed is None` is `False`; `invoice_amount is None or
   invoice_amount < 0` is `False`. `row_issues` stays empty — the guard clause's `if row_issues:`
   (line 221) is not taken; this row proceeds (Part 8).
5. **`paid_amount` parsing.** `_parse_amount(row.get("paid_amount"))` (line 230) returns `0.0`
   — a valid, non-negative float, so `paid_amount = 0.0` directly, no fallback triggered.
6. **Outstanding amount clamp.** `outstanding_amount = max(12345.67 - 0.0, 0.0) = 12345.67`
   (line 234) — no clamping actually occurs here since the result is already non-negative
   (Part 4).
7. **Signed `days_overdue`.** `days_overdue = (date(2026, 7, 9) - date(2026, 6, 19)).days = 20`
   (line 236) — `_due(20)` constructs a `due_date` exactly 20 days before `AS_OF` (Part 5).
8. **Aging bucket.** `_aging_bucket(20)` (lines 115-125): `20 <= 0`? No. `20 <= 30`? Yes —
   returns `"1-30 Days"`.
9. **Follow-up priority.** `_follow_up_priority(12345.67, 20)` (lines 128-140):
   `outstanding_amount <= 0`? No. `days_overdue > 60 or outstanding_amount >= 50000`? No
   (`20 > 60` false, `12345.67 >= 50000` false). `31 <= 20 <= 60`? No. `1 <= 20 <= 30`? Yes —
   returns `"Low"` (Part 6).
10. **Suggested action.** `_SUGGESTED_ACTION["Low"]` (line 40) = `"Include in regular follow-up
    list"`.
11. **`aging_row` built and appended** (lines 242-255): `{"invoice_id": "INV-2026-777",
    "customer_name": "Acme Co", "invoice_date": "2026-06-01", "due_date": "2026-06-19",
    "invoice_amount": 12345.67, "paid_amount": 0.0, "outstanding_amount": 12345.67,
    "days_overdue": 20, "aging_bucket": "1-30 Days", "follow_up_priority": "Low",
    "suggested_action": "Include in regular follow-up list"}`.
12. **Draft-message guard.** `outstanding_amount > 0` (True) `and days_overdue > 0` (True) `and
    follow_up_priority in ("High", "Medium", "Low")` (True — Part 7) — all three conditions hold.
13. **Draft message built.** `_build_draft_message("INV-2026-777", "Acme Co", 12345.67, 20,
    "SGD")` (line 260) calls `_format_amount(12345.67, "SGD")` (line 143), which returns
    `"SGD 12,345.67"` since `currency_value` isn't blank — the message text reads "...outstanding
    amount of SGD 12,345.67, which is currently 20 days overdue..." (Part 10).
14. **Summary aggregation.** After every row in the batch is processed, `_build_summary`
    (lines 170-190) increments `aging_bucket_counts["1-30 Days"]`, adds `12345.67` to
    `total_outstanding_amount` and (since `days_overdue > 0`) to `overdue_amount`, and leaves
    `high_priority_count` unchanged (`follow_up_priority == "Low"`, not `"High"`) (Part 9).

## A second, short trace: an invoice that never reaches `aging_rows`

Take `INV-2026-025` from the real sample data (`generate_invoices()`,
[`src/sample_data.py:183`](../../../src/sample_data.py#L183)) — a deliberate negative-amount
imperfection: `invoice_amount: -500.00`, `due_date` present and valid.

1. **`_parse_date`** succeeds on `due_date` — `due_date_parsed` is a valid `Timestamp`.
2. **`_parse_amount`** on `invoice_amount = -500.00`: not blank, not a `bool`, is a `float` —
   returns `-500.0` directly (line 92-93 of `_parse_amount` — negative values parse fine, the
   *sign check* happens at the call site, not inside the parser).
3. **PA-006 check.** `due_date_parsed is None`? No — no PA-006 issue.
4. **PA-007 check.** `invoice_amount is None or invoice_amount < 0`? `-500.0 < 0` is `True` — a
   `PA-007` `PaymentDataIssueRow` is appended to `row_issues`: `{"invoice_id": "INV-2026-025",
   "customer_name": "Bund Optical Partners", "error_code": "PA-007", "error_message": "Invoice
   amount is missing or invalid.", "severity": "Error"}` (via `_build_data_issue`, lines 100-112).
5. **Guard clause fires.** `row_issues` is non-empty — `data_issues.extend(row_issues)` runs,
   then `continue` (lines 221-223). Nothing from lines 225 onward (trimming `invoice_id`,
   parsing `paid_amount`, computing `outstanding_amount`/`days_overdue`/`aging_bucket`/
   `follow_up_priority`) ever executes for this row.
6. **Never reaches `aging_rows`.** This invoice contributes zero entries to `aging_rows`, zero to
   `draft_messages`, and exactly one to `data_issues`.
7. **Summary impact.** `total_invoices` (Part 9) still counts this row, since it's computed from
   `len(invoices_df)` before any filtering — but `aging_bucket_counts`, `total_outstanding_amount`,
   `overdue_amount`, and `high_priority_count` are all computed only from `aging_rows`, so this
   row contributes to none of them.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Open `tests/test_payment_aging.py:306-318`
(`test_summary_aggregates_total_outstanding_overdue_and_high_priority`). Before reading the
assertions, use Parts 4, 5, 6, and 9 to predict, for each of the three constructed invoices
(`INV-A`, `INV-B`, `INV-C`): its `aging_bucket`, `follow_up_priority`, and whether its
`outstanding_amount` counts toward `overdue_amount`. Then compute the expected
`total_outstanding_amount`, `overdue_amount`, and `high_priority_count` by hand, and check your
work against the test's actual assertions.

<details>
<summary>Hint</summary>

`INV-B`'s `due_date=_due(70)` crosses the `days_overdue > 60` threshold in `_follow_up_priority`
(Part 6) — work out which single invoice that makes `high_priority_count == 1`. For
`overdue_amount`, re-check Part 9's condition: it's not "every outstanding amount," only rows
where `days_overdue > 0` — one of the three invoices here has a *future* due date and must be
excluded from that sum even though its `outstanding_amount` is still counted in
`total_outstanding_amount`.
</details>

**Challenge 2 — Extend** (20–30 min): Design (don't implement — this would need a new ADR, since
it changes `PaymentAgingSummary`'s contract) a `distinct_customers_needing_attention` summary field
that counts *distinct customers* with at least one High or Medium priority invoice, rather than
counting invoices. Write out: why this is structurally the same class of bug Tutorial 04 Part 8
named for `low_stock_sku_count` vs. `len(supplier_follow_ups)` (a customer with two separate
High-priority invoices should count once, not twice); what data structure `_build_summary` would
need (a `set`, following the exact precedent from Tutorial 03 Part 7 and Tutorial 04 Part 8); and
the name and assertion of one new test that would fail today if this field were computed naively
as `sum(1 for row in aging_rows if row["follow_up_priority"] in ("High", "Medium"))` instead.

<details>
<summary>Hint</summary>

Re-read Tutorial 04 Part 8's `low_stock_skus: set[str]` pattern directly — the mechanical shape is
identical, just keyed on `customer_name` instead of `sku`. Your new test needs at least one
customer with two separate invoice rows, each independently qualifying as High or Medium priority,
to actually distinguish the correct distinct-count answer from the naive summed one.
</details>

**Challenge 3 — Break and fix** (30–45 min): Imagine the guard clause in Part 8
(`if row_issues: data_issues.extend(row_issues); continue`) were rewritten as an `if/else` —
`if row_issues: data_issues.extend(row_issues)` followed by an `else:` block wrapping everything
from `invoice_id = ...` (line 225) through `draft_messages.append(...)` (line 259), *without* the
`continue`. Before changing any code, predict: would any existing test actually fail from this
change, given that the `else` block's logic is unreachable when `row_issues` is non-empty either
way? Then predict what *would* go wrong if a future edit inserted new code between the `if
row_issues:` block and the `else:` — code intended to run for *every* row, issue or not. Make the
rewrite, run `uv run pytest tests/test_payment_aging.py -v` to confirm your first prediction, then
explain in one paragraph why the guard-clause form is more robust against the second scenario even
though both forms currently produce identical output.

<details>
<summary>Hint</summary>

Your first prediction should be "no tests fail" — `if/else` and `guard-clause-plus-continue` are
behaviorally identical *as currently written*, which is exactly what makes this a subtle exercise
rather than an obvious break. The real risk is structural, not behavioral yet: revisit this
tutorial's Concept 5 pre-study prompt about what could go wrong if future code were added *between*
the two branches of an `if/else` split, expecting to run for both cases.
</details>

For deeper exploration, `docs/plan/phase-5-payment-aging-core/ai-discussion-topics.md` has 11
prompts covering priority rules that override their own bucket, signed vs. floored quantities,
asymmetric field validation, and what fixtures can and can't be trusted for. Feed them to an LLM
*after* forming your own answer first — the gap between what you thought and what you learn is
where understanding lands.
