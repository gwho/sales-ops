# Tutorial 02 — Sample Data and Contract Fixtures: Data That Doesn't Expire

**After completing this tutorial you will understand:** why time-dependent demo data uses a
`None`-sentinel default argument instead of a literal default, how a closure captures a
resolved value across an entire function call, why this project keeps hand-authored contract
fixtures and generated sample workbooks as two deliberately separate mechanisms, why a
reorder-point scenario is authored as a static fact instead of simulated by an algorithm that
doesn't exist yet, and why tests over generated demo data assert *invariants* ("exactly one
duplicate") rather than literal values.

> [!NOTE]
> **Prerequisites:** Tutorial 01 (`01-python-foundation/README.md`) — this tutorial reuses
> `load_excel`/`validate_required_columns` from `src/excel_io.py` and the `TypedDict` contracts
> from `src/contracts.py` without re-explaining them. Open
> [`src/sample_data.py`](../../src/sample_data.py),
> [`tests/test_sample_data.py`](../../tests/test_sample_data.py), and
> [`tests/contract_fixtures.py`](../../tests/contract_fixtures.py) alongside this tutorial.

A note on scope: `docs/plan/phase-2-sample-data/plan.md` describes the original Phase 2 shipment
(8 SKUs, 12 order lines, 10 invoices, no customer file). The code below reflects a later,
non-phase-numbered enrichment (`docs/plan/sample-data-enrichment/`) that expanded the row counts,
rethemed the fictional company, and added `generate_customers()`. Every pattern this tutorial
teaches — the date-anchoring trick, the fixture/generator split, the static reorder-point fact —
is exactly what Phase 2 established; only the volume and theme of the fictional data changed
afterward.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| `None`-sentinel default + closure over a resolved value | `generate_invoices(reference_date=None)` and its nested `offset()` in `src/sample_data.py` | Python language |
| Functional core, imperative shell | pure `generate_*()` functions vs. I/O-performing `write_sample_workbooks()` | System design |
| Fixture/generator separation (avoiding self-validating circularity) | `tests/contract_fixtures.py` hand-authored dicts vs. `src/sample_data.py` generated DataFrames | Design patterns |
| Authored invariant vs. simulated derivation | `DIAG-TONO-007`'s reorder-point row, `PART-CAL-015`'s missing inventory row | System design |
| Invariant/property assertions over generated data | `test_generate_orders_has_exactly_one_duplicate_order_id` and similar in `tests/test_sample_data.py` | Algorithms |

## How to use an LLM before this tutorial

### Concept 1 — Mutable and time-dependent default arguments

> "Explain why, in Python, `def f(x=some_expression()):` only ever evaluates `some_expression()`
> once — at the moment the `def` statement runs, not on every call. Show a concrete example where
> this causes a real bug (the classic `def f(items=[]):` case, and a time-dependent one using
> `datetime.now()`). Then explain the standard fix and why it works. Quiz me at the end with a new
> example and ask me to predict the bug before you reveal it."

*What to listen for:* the root cause is that a `def` statement is executed exactly once (at
import/definition time), and the default value expression is evaluated *then*, and the resulting
object is reused on every subsequent call that doesn't override it — this is true for any mutable
object default (`[]`, `{}`) and equally true for any *time-dependent* call like `date.today()`,
even though a fresh date object isn't literally mutated the way a list is.

*Practice question:* If a function is defined once when a Python process starts and then called
many times over the following three days, what value would `def f(x=date.today())` return for `x`
on day 3, assuming the caller never passes `x` explicitly?

### Concept 2 — Closures

> "Explain what a closure is in Python: a function defined inside another function that references
> a variable from the enclosing function's scope, even after the outer function's other local setup
> has finished running. Give a small example with a counter or accumulator. Explain what 'the inner
> function captures the variable, not just its value at definition time' means in practice. Quiz me
> on what happens if the captured variable is reassigned *after* the inner function is defined but
> *before* it's called."

*What to listen for:* a closure captures the enclosing *variable* (a reference to a name in that
scope), not a frozen snapshot of its value at the moment the inner function was defined — so if the
outer variable is reassigned before the inner function is actually called, the inner function sees
the new value, not the old one.

*Practice question:* if an outer function resolves a variable from a `None` sentinel to a real value
*before* defining an inner helper function that uses that variable, does the helper need its own
parameter for that value, or can it just reference the outer variable directly?

### Concept 3 — Functional core, imperative shell

> "Explain the 'functional core, imperative shell' system design pattern: keeping the part of a
> system that computes/transforms data free of side effects (no I/O, no mutation of outside state),
> and pushing all side effects (file writes, network calls, database writes) to a thin outer layer
> that calls into the pure core. What's the testing benefit of this split? Give an example of a
> codebase structure that violates it, and what gets harder to test as a result. Quiz me on which of
> two given functions is the 'core' and which is the 'shell.'"

*What to listen for:* pure functions can be tested by calling them directly and asserting on their
return value, with no setup/teardown, no temp files, no mocking — the imperative shell is what
actually has to be integration-tested (real file I/O, real temp directories), and keeping it thin
minimizes how much of the system needs that heavier kind of test.

*Practice question:* if a single function both computes a result *and* writes it to disk in the
same function body, what does a test of "does the computation logic work" have to do that it
wouldn't have to do if computation and writing were separate functions?

### Concept 4 — Property/invariant-based assertions

> "Explain the difference between a test that asserts an exact expected value (`assert result ==
> 42`) and one that asserts a property or invariant the result must satisfy (`assert result > 0`,
> `assert len(duplicates) == 1`, `assert set(a) <= set(b)`). When is the invariant style more robust
> to change, and when does it risk being too loose to catch real bugs? Quiz me with a scenario and
> ask which style is more appropriate."

*What to listen for:* invariant-style assertions survive changes to unrelated details of the data
(add a new normal row, and a test checking "exactly one duplicate" still passes; a test hardcoding
"the 13th row is X" would break), but the same looseness that makes them resilient can let a real
bug slip through if the invariant is too weak — the skill is picking an invariant specific enough to
actually catch the bug class you care about.

*Practice question:* a test asserts `len(duplicate_order_ids) >= 1`. What kind of real bug — one
this project's actual `test_generate_orders_has_exactly_one_duplicate_order_id` is written to catch
— would this weaker version fail to catch?

### Concept 5 — Test fixtures vs. generated data as independent sources of truth

> "In testing, why would a project deliberately maintain two separate mechanisms for producing
> similar-looking example data — one hand-authored by a person, one generated by code — instead of
> deriving one from the other? What specific kind of bug does keeping them independent protect
> against, that deriving one from the other would not? Quiz me on a scenario where a generator has a
> subtle bug and ask whether hand-authored fixtures would catch it."

*What to listen for:* if fixtures were *derived from* the generator's own output, a bug in the
generator would propagate silently into "proof" that looks self-consistent — the fixture would
faithfully reproduce the generator's mistake rather than exposing it, because both sides trace back
to the same source. Independent authorship means the fixture represents someone's independent
understanding of "what correct output should look like," which can disagree with (and thus catch
bugs in) code that computes it a different way.

*Practice question:* if `ValidationErrorRow`'s hand-authored fixture and a future
`order_validation.py`'s real output disagree on a field's type, whose "fault" is more likely — and
why does that depend on which one was written by reading the spec directly?

## Architecture overview

Phase 2 adds no business rules. It adds two independent things that later phases will build
against: fictional data generated by code, and contract examples typed by hand.

```text
┌────────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│  src/sample_data.py                         │   │  tests/contract_fixtures.py               │
│                                              │   │                                            │
│  generate_product_master()  ─┐              │   │  Hand-authored dict literals, one per      │
│  generate_orders(...)        │  pure,       │   │  src/contracts.py TypedDict family —       │
│  generate_inventory(...)     │  no I/O,     │   │  NOT computed from sample_data.py, NOT     │
│  generate_invoices(...)      │  return a    │   │  proof any business rule exists yet.       │
│  generate_customers()       ─┘  DataFrame   │   │                                            │
│               │                             │   │  Independently authored so a bug in one    │
│               ▼                             │   │  side can't silently "confirm" the other.  │
│  write_sample_workbooks()                   │   └──────────────┬─────────────────────────────┘
│  (imperative shell: mkdir + .to_excel(),    │                  │
│   the only I/O in this file)                │                  ▼
└───────────────┬──────────────────────────────┘   ┌──────────────────────────────────────────┐
                │                                    │  tests/test_contracts.py                 │
                ▼                                    │  asserts fixture keys match each         │
     sample_data/*.xlsx (committed to git)            │  TypedDict's declared shape              │
                │                                    └──────────────────────────────────────────┘
                ▼
┌──────────────────────────────────────────────┐
│  tests/test_sample_data.py                    │
│  - asserts invariants over generate_*() output │
│    ("exactly one duplicate", "at least one     │
│    SKU below reorder point") — not literal     │
│    values                                      │
│  - round-trips write_sample_workbooks() output │
│    back through load_excel() +                 │
│    validate_required_columns() (Tutorial 01)   │
└────────────────────────────────────────────────┘
```

Key invariants for this phase:

1. **No business logic is written or reimplemented early.** `test_sample_data.py` never computes
   `days_overdue`, `aging_bucket`, or an allocation outcome — those are Phases 4–5's job, and a test
   that quietly encodes them now would go stale the moment the real rule is implemented differently.
2. **Contract fixtures and generated sample data are two independent representations of the same
   domain**, deliberately not derived from one another (Part 3).
3. **Every intentional imperfection in the generated data is asserted by name** (a specific
   `order_id` or `invoice_id`), not just counted — so a test failure points at exactly which row
   broke, not just that "something" did.

## Part 1 — The `None`-sentinel default and the closure that uses it

Open [`src/sample_data.py`](../../src/sample_data.py) lines 140–153:

```python
def generate_invoices(reference_date: date | None = None) -> pd.DataFrame:
    """Build invoices with due dates offset from reference_date so the mix
    stays believable (every aging bucket, Paid/Partial/Unpaid, high-priority
    by age and by amount) no matter when this is regenerated. Exactly 1
    invoice has a missing due date, exactly 1 has an invalid/negative
    amount, and exactly 1 is a deliberate overpayment (paid_amount >
    invoice_amount)."""
    if reference_date is None:
        reference_date = date.today()

    def offset(days: int) -> date | None:
        if days is None:
            return None
        return reference_date - timedelta(days=days)
```

A tempting, shorter-looking version of this signature would be
`def generate_invoices(reference_date: date = date.today()) -> pd.DataFrame:`. It would even work —
once. The bug is invisible in a quick manual test and only shows up in a long-running process: a
default argument's value is computed exactly once, when the `def` statement itself executes (import
time), not on every call. In a short-lived script that's harmless. In a long-running process — a
notebook kernel kept open for days, or (per `CLAUDE.md`) a future FastAPI worker — every call that
doesn't pass `reference_date` explicitly would keep reusing whatever date happened to be "today" the
moment the module was first imported, silently drifting further from the truth as the process stays
alive.

The `None`-sentinel pattern defers the actual `date.today()` call from *definition* time to *call*
time: `reference_date: date | None = None` is a completely inert, safe default (nothing time-
dependent is evaluated when the `def` line runs), and the real resolution happens in the function
*body*, which re-executes on every call. This is the standard fix for the entire class of "mutable
or time-dependent default argument" bugs in Python — the exact same pattern fixes
`def f(items=None): items = items if items is not None else []`.

The nested `offset()` function is what makes the resolved `reference_date` usable across the whole
row-building block below it: it's defined *after* `reference_date` has already been resolved to a
real `date`, and it references that outer variable directly — no parameter needed — because Python
closures capture the enclosing scope's variable, not just a value copied in at definition time.

> **Python language — Closures over a resolved value:** `offset()` is a closure: a function defined
> inside `generate_invoices()` that reads `reference_date` from the enclosing function's scope. Because
> the `if reference_date is None:` resolution runs *before* `offset` is defined, every call to
> `offset(days)` sees the one real, resolved date for this entire invocation — not `None`, and not a
> re-resolved "now" on each of the dozens of calls to `offset()` below it. This is the same
> mechanism behind Python idioms like a `functools.lru_cache`-wrapped inner function or a decorator
> that closes over configuration — capture once, reuse consistently, without threading an extra
> parameter through every call site.

**Checkpoint:** Why does `def f(x=some_call())` only evaluate `some_call()` once, at import time?
What other Python gotchas share this exact root cause?

<details>
<summary>Reveal answer</summary>

A `def` statement is itself executable code: Python builds the function object once, at the moment
the `def` line runs, and default argument expressions are evaluated as part of building that object
— they become part of the function object's stored defaults, not code that reruns on every call.
This is the identical mechanism behind the classic mutable-default-argument bug
(`def f(items=[]): items.append(x)` — every call without an explicit `items` shares the *same* list
object, so appends accumulate across calls that look unrelated), and behind any other
non-deterministic or resource-acquiring default (`def f(conn=open_connection())` would open exactly
one connection at import time and every caller would share it). Time-dependent calls like
`date.today()` or `datetime.now()` are a variant of the same root cause: not mutation, but staleness
— the value is correct once, then wrong forever after, silently.
</details>

**Checkpoint:** The `None`-sentinel pattern is the standard fix. Are there cases where you'd
actually *want* the frozen-at-import-time behavior instead?

<details>
<summary>Reveal answer</summary>

Yes — when the value genuinely should be fixed for the lifetime of the process, and re-resolving it
on every call would be wrong, not just wasteful. An example: a default `config` object built once
from environment variables at process startup, deliberately shared across every call so that all
requests in that process see a consistent configuration snapshot even if the environment variable
changes mid-process. The distinguishing question is whether "the value can legitimately change
between calls and callers should see the new value" (favor `None`-sentinel, re-resolve per call) or
"the value should stay pinned to whatever was true when the process started" (a literal default, or
an explicit process-startup-time constant, is correct). `reference_date` is squarely the first case:
demo data regenerated a week from now should reflect *that* week, not the week the module happened to
be first imported.
</details>

**Try it yourself:** In a Python shell, run
`from src.sample_data import generate_invoices; from datetime import date; df1 = generate_invoices(reference_date=date(2026,1,1)); df2 = generate_invoices(reference_date=date(2026,1,11)); print(df1[df1.invoice_id=="INV-2026-001"].due_date.iloc[0], df2[df2.invoice_id=="INV-2026-001"].due_date.iloc[0])`
and confirm the second date is exactly 10 days later than the first — the whole row shifted, not
just recomputed differently.

## Part 2 — Why invoice dates are relative but order/inventory dates are fixed

Open [`src/sample_data.py`](../../src/sample_data.py) — compare an order row at line 62 to an
invoice row at line 157:

```python
{"order_id": "SO-2026-001", "order_date": date(2026, 7, 1), "customer_name": "Victoria Harbour Eye Institute", "customer_region": "Hong Kong", "sku": "VIS-SLIT-001", "product_name": "Slit Lamp Examination Unit", "quantity": 3, "requested_delivery_date": date(2026, 7, 15), "priority": "High", "payment_terms": "30 days", "sales_owner": "Jesse"},
```

```python
{"invoice_id": "INV-2026-001", "customer_name": "Victoria Harbour Eye Institute", "invoice_date": offset(160), "due_date": offset(130), "invoice_amount": 68000.00, "paid_amount": 0.0, "currency": "HKD", "payment_status": "Unpaid", "sales_owner": "Jesse", "remarks": "Awaiting wire confirmation from finance", "order_id": "SO-2026-001"},
```

The order row's dates are plain literals (`date(2026, 7, 1)`); the invoice row's dates are calls to
`offset(...)`. This isn't a stylistic inconsistency — it follows directly from what each workflow's
business rules actually compare. Order validation (`01_demo_order_validation.md` rule OV-005) and
inventory allocation only ever compare dates *within the same row or file* to each other —
`requested_delivery_date` against `order_date`, for instance — never against "today." A fixed date
like `2026-07-15` stays exactly as valid an example of "delivery requested 14 days after the order"
whether the test suite runs in 2026 or five years later.

Payment aging (`03_demo_payment_aging.md` PA-003/PA-004) is different: `days_overdue = today -
due_date`, and the aging bucket depends entirely on how large that gap currently is. A hardcoded
`due_date` of `2026-06-01` would describe an invoice that's, say, 40 days overdue today — squarely a
believable "31-60 Days" bucket example — but the same literal date would describe an invoice 400+
days overdue a year later, silently sliding into the "90+ Days" bucket and breaking the deliberately
constructed believable mix across every bucket (Part 4's static-fact reasoning covers the sibling
case of inventory data, which has the same "can this rot?" question with a different answer).

**Checkpoint:** This project's invoice due dates are generated relative to `date.today()` (via
`reference_date`) so the demo doesn't "expire." What other kinds of portfolio or demo data have this
same staleness problem, and how would you detect it before an interview?

<details>
<summary>Reveal answer</summary>

Any demo data whose *meaning* depends on the gap between an embedded date and the moment it's
viewed has this problem: a dashboard screenshot showing "3 orders due this week," a resume bullet
point citing "current" metrics that were true at write time, a SaaS demo account with subscription
or trial-expiry dates baked in, or — as here — an aging-bucket example whose bucket membership is a
function of elapsed time. The general detection method: for every date-like field in demo data, ask
"does any downstream rule compute today-minus-this-date (or this-date-minus-today)?" If yes, either
anchor it to a resolved "now" the way `generate_invoices` does, or explicitly regenerate/verify the
demo shortly before it's shown, rather than trusting a value authored once and left alone.
</details>

**Checkpoint:** `generate_orders()` and `generate_inventory()` use plain fixed 2026-07 dates with no
`reference_date` parameter at all. Is this a decision that could bite the project later, or is it
provably safe given what those two workflows' rules actually check?

<details>
<summary>Reveal answer</summary>

It's provably safe given the current specs — OV-005 and the inventory allocation rules only compare
dates that live inside the same uploaded file to each other (e.g., `requested_delivery_date` vs.
`order_date`, both fixed 2026-07 literals whose *relative* gap never changes), never against
wall-clock "today." The risk would only materialize if a future rule change introduced a
today-relative comparison into order validation or inventory allocation (e.g., "flag orders whose
requested delivery date has already passed") — at that point, this same relative-offset technique
would need to be retrofitted onto those two generators, the same way it was applied to invoices from
the start once payment aging's rules were known to need it.
</details>

**Try it yourself:** Read `01_demo_order_validation.md` rule OV-005 (or search `src/` once Phase 3
exists) and confirm for yourself that it compares two dates from the *same order row*, never
`date.today()` — this is the actual justification for why `generate_orders()` gets away with fixed
literals.

## Part 3 — Why contract fixtures aren't computed from the sample workbooks

Open [`tests/contract_fixtures.py`](../../tests/contract_fixtures.py) lines 1–7 (already introduced
in Tutorial 01, revisited here for a different question):

```python
"""Realistic example values for each Phase 1 output-contract family (Contract Fixtures).

Hand-authored, not computed by src/sample_data.py or any business-rule module —
order_validation.py, inventory_allocation.py, and payment_aging.py don't exist
until Phases 3-5. These only prove the contract shapes can hold believable demo
data; they are not evidence that any business rule is implemented correctly.
"""
```

It would be technically possible, right now, to write a throwaway validation function that reads
`sample_orders.xlsx` and computes a real `ValidationErrorRow` for the `VIS-SCOPE-099` unknown-SKU
row — deriving the fixture from the generated data instead of typing it by hand. Phase 2 explicitly
rejects this. `explanation.md` names the reason directly: that throwaway function would *be* a
partial, premature implementation of `order_validation.py`'s actual job, built before Phase 3 gets to
design it properly — exactly the kind of scope creep `context/build-plan.md`'s phase boundaries exist
to prevent.

There's a second, quieter reason this separation matters even after Phases 3–5 exist: if a fixture
were *derived from* running the real business-rule module against the sample data, a bug in that
module would produce a fixture that faithfully reproduces the bug — the "proof" and the thing being
proven would trace back to the same source, so the fixture could never disagree with (and thus never
catch) a mistake in the code that generated it. `VALIDATION_ERROR_ROW_FIXTURE` cites the same
`MED-LENS-999`-style unknown-SKU scenario that's actually present in the sample orders file (an
intentional point of consistency), but its values come from someone reading the *spec* and typing
what correct output should look like — independent of whatever `order_validation.py` will eventually
compute.

> **Design patterns — Independent verification via separated fixtures:** Keeping a hand-authored
> "what should this look like" example separate from a generated "here's what the code produced"
> artifact is a general testing principle, not specific to this project — it's the same reasoning
> behind never writing a unit test by capturing and asserting on a function's *current* output
> (a "golden master" test can ossify a bug into a permanent expectation) instead of asserting what
> the spec says the output *should* be. The fixture's independence is what gives it the power to
> disagree with buggy code.

**Checkpoint:** `tests/contract_fixtures.py` fixtures are hand-authored, while `sample_data/*.xlsx`
is generated by code. Why keep those as two separate mechanisms instead of deriving the fixtures
from the generated workbooks?

<details>
<summary>Reveal answer</summary>

Deriving fixtures from the generated workbooks would require running actual business-rule logic
(order validation, allocation, or aging calculations) that doesn't exist until Phases 3-5 — building
that logic early, even in throwaway form just to populate a fixture, is the exact premature
implementation Phase 2's scope boundary exists to prevent. Separately and more durably: independent
authorship means the fixture reflects an independent read of the *spec*, not of whatever the real
implementation happens to compute — so if the real implementation ever has a bug, the fixture has a
chance of disagreeing with it (and a test built on both would then correctly fail) instead of
silently agreeing because both trace back to the same generation path.
</details>

**Checkpoint:** The Phase 2 plan explicitly avoids computing `days_overdue`/`aging_bucket` inside
`test_sample_data.py`, specifically to prevent "reimplementing Phase 5 early." What's the risk of a
test quietly encoding business logic before the module that owns that logic actually exists?

<details>
<summary>Reveal answer</summary>

If a test encodes its own copy of a business rule ahead of the real module, two independent
implementations of the same rule now exist — the test's inline version and whatever Phase 5's
`payment_aging.py` eventually implements — and they can silently diverge without either failing,
since the test only checks itself against the module it's supposed to protect. Worse, whoever writes
the real module might unconsciously look at the test's already-passing inline logic and copy its
(potentially wrong, or spec-inconsistent) assumptions rather than re-deriving the rule from
`03_demo_payment_aging.md` directly, defeating the entire purpose of having a spec-derived, tested
implementation. `test_sample_data.py:259-273`'s comment makes this explicit: it asserts only the
*data shape* an aging rule will need to consume (`days_before_reference > 60`, `outstanding >=
50000`), never the aging bucket or priority label itself.
</details>

**Try it yourself:** Search `tests/contract_fixtures.py` for `MED-LENS` — it's still there, a leftover
reference to the *original* Phase 2 product catalog that predates the later enrichment. Cross-check
against the current `src/sample_data.py`'s product master (line 25 onward) and confirm this SKU no
longer exists in the generated sample data at all — direct, hands-on evidence that these two files
really are independently maintained, for better (proven independence) and worse (now-stale
cross-references) at once.

## Part 4 — An authored fact, not a simulated one

Open [`src/sample_data.py`](../../src/sample_data.py) lines 109–137, focusing on the
`DIAG-TONO-007` rows (127–128) and the absence of any `PART-CAL-015` row:

```python
def generate_inventory(product_master_df: pd.DataFrame) -> pd.DataFrame:
    """Build inventory records across HK, China, and Europe warehouses.

    DIAG-TONO-007's HK Warehouse row is deliberately below its reorder point
    before any allocation runs and stays untouched by orders (China Warehouse
    has more allocatable stock, so IA-007's stand-in warehouse-pick rule
    routes demand there instead). PART-CAL-015 has no inventory row at all,
    guaranteeing at least one valid order fully backorders.
    """
    rows = [
        ...
        {"sku": "DIAG-TONO-007", "warehouse": "HK Warehouse", "available_qty": 2, "reserved_qty": 0, "reorder_point": 3, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 21},
        {"sku": "DIAG-TONO-007", "warehouse": "China Warehouse", "available_qty": 10, "reserved_qty": 2, "reorder_point": 4, "supplier_name": "Meridian Diagnostics Co", "lead_time_days": 15},
```

`context/build-plan.md` asks for "at least one SKU near reorder point" in the sample inventory
file. The algorithmically thorough way to satisfy that would be to actually *simulate* allocation:
run demand from `sample_orders.xlsx` against this inventory, deplete stock the way Phase 4's real
engine eventually will, and check what's left below the reorder point. Phase 2 rejects that path for
the same reason as Part 3's fixtures — that simulation *is* Phase 4's algorithm, reimplemented early
and with no guarantee of matching what Phase 4 actually builds.

Instead, `DIAG-TONO-007`'s HK Warehouse row is authored so `available_qty` (2) is already below
`reorder_point` (3) as literally written — `allocatable = available_qty - reserved_qty = 2`, `2 < 3`
— true before any allocation math runs at all. `test_generate_inventory_has_at_least_one_sku_below_
reorder_point` (`tests/test_sample_data.py:190-196`) asserts this arithmetic fact directly, not a
downstream consequence of running an allocation algorithm.

Separately — and this is the part the discussion questions probe hardest — `PART-CAL-015` has *no
inventory row anywhere in this DataFrame*, despite being referenced by an active order
(`SO-2026-019`, quantity 4, in `generate_orders()`). This isn't an oversight; the docstring calls it
out as deliberate: "guaranteeing at least one valid order fully backorders." This is
*pre-shaping* input data so that Phase 4's allocation engine, once it exists, is guaranteed to
exercise its full-backorder code path the first time someone runs the demo — without Phase 2 ever
computing, asserting, or even knowing what "backorder" means as an output field.

> **System design — Authored invariant vs. simulated derivation:** When a downstream system's
> behavior depends on an upstream data property, there are two ways to guarantee that property
> holds: compute it by actually running (a version of) the downstream system against the data, or
> author the data so the property is true by direct inspection, independent of any algorithm. The
> second approach trades a small amount of "is this realistic enough" judgment for a large reduction
> in coupling — the test asserting `available_qty - reserved_qty < reorder_point` will never break
> because Phase 4's allocation algorithm changed, because it doesn't call that algorithm at all.

**Checkpoint:** The reorder-point scenario was deliberately authored as a static fact rather than
the result of simulated allocation. What made that the right call here, and when would simulating
the real algorithm in a test be worth the coupling?

<details>
<summary>Reveal answer</summary>

It's the right call here because the algorithm being "simulated" (Phase 4's allocation engine)
doesn't exist yet at Phase 2 — there's nothing correct to couple to, only a guess at what it might
eventually do. Authoring the fact directly (`available_qty - reserved_qty < reorder_point`, checked
by arithmetic alone) guarantees the scenario is true regardless of how Phase 4 is eventually
implemented. Simulating the real algorithm becomes worth the coupling once that algorithm actually
exists and is stable — at that point, an *integration* test that runs real orders through the real
allocation engine and checks the resulting backorder list is more valuable than an authored fact,
because it's now verifying the real code path end-to-end rather than a precondition for a code path
that isn't built yet. The right tool changes as the system matures; Phase 2 correctly picks the tool
for where the system actually was at the time.
</details>

**Checkpoint:** Phase 2 pre-shapes data so that Phase 4's not-yet-written allocation engine is
guaranteed to produce a partial allocation and a full backorder once it runs (`DIAG-TONO-007`'s
scarcity, `PART-CAL-015`'s total absence). Is pre-shaping data for a not-yet-built algorithm a form
of scope creep, or is it exactly what "sample data as infrastructure" should do?

<details>
<summary>Reveal answer</summary>

It's not scope creep because nothing about *how* Phase 4 will compute a backorder is decided or
implemented here — only the *input conditions* that make a backorder scenario reachable are shaped,
which is a property of the data, not of the algorithm. Contrast this with what scope creep would
actually look like: writing a stub `allocate()` function, or hardcoding what the backorder *output*
row should contain — either of those would be implementing Phase 4 early. Shaping demand to exceed
supply for one SKU is squarely "sample data as infrastructure": the whole point of authoring
believable demo data (per `CLAUDE.md`'s fictional-data rules) is that every downstream workflow has
something interesting to show, and that requires knowing *in advance* which interesting scenarios
the data needs to support — without knowing or committing to how any future module computes them.
</details>

**Try it yourself:** Sum `PART-CAL-015`'s total ordered quantity across `generate_orders()`'s rows
(search for `PART-CAL-015` — you should find one row, `SO-2026-019`, quantity 4) and confirm there is
truly zero inventory for it anywhere in `generate_inventory()`'s output. This is the exact
"at least one active SKU with a real order and literally no stock" condition the docstring promises.

## Part 5 — The imperative shell: `write_sample_workbooks()`

Open [`src/sample_data.py`](../../src/sample_data.py) lines 218–241:

```python
def write_sample_workbooks(
    output_dir: Path = SAMPLE_DATA_DIR, reference_date: date | None = None
) -> None:
    """Generate and write all five sample workbooks to output_dir."""
    if reference_date is None:
        reference_date = date.today()

    output_dir.mkdir(parents=True, exist_ok=True)

    product_master_df = generate_product_master()
    orders_df = generate_orders(product_master_df)
    inventory_df = generate_inventory(product_master_df)
    invoices_df = generate_invoices(reference_date)
    customers_df = generate_customers()

    product_master_df.to_excel(output_dir / "sample_product_master.xlsx", index=False)
    orders_df.to_excel(output_dir / "sample_orders.xlsx", index=False)
    inventory_df.to_excel(output_dir / "sample_inventory.xlsx", index=False)
    invoices_df.to_excel(output_dir / "sample_invoices.xlsx", index=False)
    customers_df.to_excel(output_dir / "sample_customers.xlsx", index=False)


if __name__ == "__main__":
    write_sample_workbooks()
```

Every `generate_*()` function is pure: given the same arguments, it always returns the same
DataFrame, touches no filesystem, and has no observable effect beyond its return value.
`write_sample_workbooks()` is the one function in this file that does anything impure — creating a
directory, writing five files to disk — and it does so by calling the pure functions first and
performing every side effect afterward, in one place, at the bottom.

This split has a direct, checkable payoff already visible in `tests/test_sample_data.py`: every test
of a `generate_*()` function (e.g. `test_generate_orders_has_exactly_one_duplicate_order_id`,
`tests/test_sample_data.py:49-56`) calls the function directly and asserts on the returned
DataFrame — no temp directory, no file I/O, no cleanup. Only one test,
`test_write_sample_workbooks_round_trips_through_excel` (`tests/test_sample_data.py:328-344`), needs
`tmp_path` and actually touches disk — because it's the only test whose job is to verify the
*impure* half of the file. If generation and writing were fused into one function, every single test
above would need a temp directory just to check a DataFrame's contents.

The `if __name__ == "__main__":` guard at the bottom means `write_sample_workbooks()` only runs
automatically when this file is executed directly (`uv run python -m src.sample_data` or the command
in `sample_data/README_sample_data.md`), never when the module is merely *imported* — which is what
every test file above does dozens of times per test run. Without the guard, importing
`src.sample_data` anywhere (including from `test_sample_data.py`) would regenerate and overwrite the
five committed `.xlsx` files as a side effect of running the test suite.

> **System design — Functional core, imperative shell:** `generate_*()` are the functional core;
> `write_sample_workbooks()` is the imperative shell. The general principle: push side effects (I/O,
> mutation, network calls) to the thinnest possible outer layer, and keep everything that transforms
> data pure underneath it. The payoff is exactly what shows up in this file's test suite — pure
> functions are tested by calling them and checking a return value; only the thin shell needs the
> heavier machinery (temp directories, file cleanup, mocking) that impure code requires.

**Checkpoint:** What's the trade-off between committing generated files to git (as this repo does
with `sample_data/*.xlsx`) versus generating them fresh on every run? When would you choose
differently?

<details>
<summary>Reveal answer</summary>

Committing the generated `.xlsx` files means anyone who clones the repo — including a reviewer who
never runs any Python — can immediately open a real, believable spreadsheet in the demo without
running any code, and the frontend's mock-data pipeline (`npm run mock-data`, per `CLAUDE.md`) has a
stable, versioned input to work from rather than a moving target. The cost is that the committed
files can drift out of sync with the generator (as Part 3's `MED-LENS` cross-reference exercise just
showed happens to fixture files) unless someone remembers to regenerate and recommit after changing
`sample_data.py`. You'd choose *not* to commit generated output when the artifact is large, purely
derived with no independent value of its own (a build output, a compiled binary), or when
regenerating it is cheap and automatic (part of a CI or build step) rather than something a human
reviewer benefits from seeing directly in the repo without running anything.
</details>

**Checkpoint:** If `write_sample_workbooks()` fused generation and writing into a single function
(no separate `generate_*()` calls), what would `test_generate_orders_has_exactly_one_duplicate_order_id`
have to do differently to keep testing the same thing?

<details>
<summary>Reveal answer</summary>

It would have to call the fused function, which would necessarily also perform its file-writing
side effect — meaning the test would need a temp directory (`tmp_path`, as
`test_write_sample_workbooks_round_trips_through_excel` already uses) just to check a property of
in-memory data, and would need to read the file back with `load_excel()` before it could even get to
the assertion it actually cares about. Every one of the dozen-plus invariant tests in
`test_sample_data.py` would pay this cost, not just the one test whose actual job is to verify the
write path — this is the concrete, measurable cost of *not* splitting functional core from
imperative shell.
</details>

**Try it yourself:** Run `uv run python -c "from src.sample_data import generate_orders, generate_product_master; import time; t0 = time.perf_counter(); [generate_orders(generate_product_master()) for _ in range(1000)]; print(time.perf_counter() - t0)"`
and confirm 1000 calls to a pure in-memory function complete in a fraction of a second — this is the
speed a pure functional core buys a test suite, compared to 1000 rounds of real file I/O.

## Part 6 — Testing generated data by invariant, not by value

Open [`tests/test_sample_data.py`](../../tests/test_sample_data.py) lines 49–56 and 154–172:

```python
def test_generate_orders_has_exactly_one_duplicate_order_id():
    df = generate_orders(generate_product_master())

    duplicate_mask = df["order_id"].duplicated(keep=False)
    duplicated_ids = set(df.loc[duplicate_mask, "order_id"])

    assert duplicated_ids == {"SO-2026-010"}
    assert duplicate_mask.sum() == 2
```

```python
def test_generate_orders_row_count_and_issue_ratio_stay_moderate():
    df = generate_orders(generate_product_master())

    assert 30 <= len(df) <= 40

    # Rows carrying at least one intentional issue, identified by order_id
    # (the duplicate row is the second SO-2026-010 occurrence).
    issue_order_ids = {
        "SO-2026-030",
        "SO-2026-031",
        "SO-2026-032",
        "SO-2026-033",
        "SO-2026-034",
        "SO-2026-035",
    }
    issue_row_count = df["order_id"].isin(issue_order_ids).sum() + 1  # +1 for the duplicate row

    ratio = issue_row_count / len(df)
    assert 0.15 <= ratio <= 0.25
```

Neither test hardcodes "row 34 has this exact dict of values." The first computes pandas'
`.duplicated()` mask and asserts a *property* of the result (exactly one duplicated ID, and it's
specifically `SO-2026-010`) rather than comparing the whole DataFrame to a literal expected copy of
itself. The second goes further: it asserts a *ratio range* (15%-25% of rows carry an issue), not an
exact count — because the exact row count is itself allowed to drift a little (`30 <= len(df) <=
40`) as the sample data is enriched over time, and a test hardcoded to "exactly 35 rows" would break
on every future enrichment for no reason connected to correctness.

This style is deliberately looser than "assert the DataFrame equals this literal" and deliberately
tighter than "assert at least one issue exists somewhere." A test asserting only `duplicate_mask.sum()
>= 1` would still pass if a future edit to `generate_orders()` accidentally introduced a *second*,
unintended duplicate — silently doubling the very imperfection the test exists to guard the count of.
Naming the exact expected ID (`{"SO-2026-010"}`) *and* the exact expected count (`== 2`, one original
plus one duplicate) is what turns this from "some data quality issue exists" into "the one specific,
intentional imperfection this file is supposed to demonstrate is present, and no unintended one has
crept in alongside it."

> **Algorithms — Invariant/property assertions over generated data:** Asserting a property a result
> must satisfy, rather than an exact literal it must equal, is the same idea behind property-based
> testing (tools like Hypothesis generate many inputs and assert invariants that must hold for all
> of them). Here the data itself is fixed, not randomly generated, but the assertion style is the
> same: characterize correct output by the properties it must have (exactly one duplicate ID, a
> ratio within a believable range) rather than by exact equality to one frozen expected value —
> resilient to unrelated changes, but only as strong as the specificity of the properties chosen.

**Checkpoint:** `test_sample_data.py` asserts things like "exactly one duplicate order_id" and "at
least one row below reorder point" about *generated* data. Is this testing the generator, the data,
or both? What would break this test in a way that's actually useful to catch?

<details>
<summary>Reveal answer</summary>

It's testing both at once, because for a pure function the generator *is* the data — there's no
separate "the data" to inspect independently of calling `generate_orders()`. What's actually useful
to catch: a future edit to `generate_orders()` (adding a new order row, tweaking an existing one)
that accidentally introduces a second duplicate `order_id`, accidentally "fixes" the one intentional
duplicate by giving it a unique ID, or accidentally references a SKU that used to be inactive but was
edited to `active: True` — any of these would silently remove or corrupt the specific demo scenario
the sample data exists to showcase, and a hardcoded-value test would only catch it by accident, while
an invariant test asserting exactly what property must hold catches it directly.
</details>

**Checkpoint:** The Phase 2 plan explicitly avoids computing `days_overdue`/`aging_bucket` in these
tests. What's the general risk of a test quietly encoding business logic before the module that owns
that logic exists — beyond what Part 3 already covered for fixtures specifically?

<details>
<summary>Reveal answer</summary>

Beyond the "two implementations can silently diverge" risk from Part 3, there's a sequencing risk
specific to *tests*: a green test suite is usually read as a signal that "this part of the system is
done and correct." A test that inline-computes `aging_bucket` and asserts against its own computation
would be green from the moment it's written — long before `payment_aging.py` exists — creating a
false signal that payment aging logic is validated when nothing about the real rule has been
implemented or checked against the spec at all. `test_generate_invoices_span_every_aging_bucket_range`
(`tests/test_sample_data.py:275-288`) sidesteps this by computing `days_overdue` locally only to
prove the *demo data* spans every bucket's day range — a comment states outright that it "does not
compute `aging_bucket` itself," keeping the test's green status honestly scoped to what Phase 2
actually delivers.
</details>

**Try it yourself:** Temporarily edit `generate_orders()` to change `SO-2026-030`'s `sku` from the
unknown `"VIS-SCOPE-099"` to a real, active SKU like `"VIS-SLIT-001"`. Run
`uv run pytest tests/test_sample_data.py -k unknown_sku -v` and read exactly which assertion fails —
confirm it fails at `assert len(unknown_sku_rows) == 1`, not at some unrelated point, proving the test
is watching the specific property it claims to watch. Revert the change before moving on.

## Part 7 — Where fixtures live, and the one deliberate exception

Open [`tests/contract_fixtures.py`](../../tests/contract_fixtures.py) lines 164–198:

```python
REPORT_MANIFEST_FIXTURES: list[ReportManifest] = [
    {
        "report_id": "rpt-order_validation-20260709091500",
        "report_type": "order_validation",
        "file_name": "order_validation_report.xlsx",
        "generated_at": "2026-07-09T09:15:00",
        "sheet_names": ["Summary", "Valid Orders", "Validation Errors", "Original Orders"],
    },
    {
        "report_id": "rpt-inventory_allocation-20260709092000",
        ...
    },
    {
        "report_id": "rpt-payment_aging-20260709092500",
        ...
    },
]
```

Every other output family in `tests/contract_fixtures.py` gets exactly one fixture — one
`ValidationSummary`, one `PaymentAgingRow`, and so on. `REPORT_MANIFEST_FIXTURES` is a list of three,
one per required Phase 6 report type. This is the single deliberate exception to "one fixture per
family," and the reasoning is specific to what `ReportManifest` actually represents: a single example
wouldn't demonstrate that the same shape has to flex across three genuinely different sheet-name
lists (`["Summary", "Valid Orders", ...]` vs. a payment-aging report's sheet names) — the whole point
of this fixture is to prove the *family* is reused correctly across its real variation, which one
example can't show.

The location decision — `tests/contract_fixtures.py`, not inline in test functions, and not a new
`src/` module — follows from a forward-looking constraint `explanation.md` names directly:
`context/architecture.md`'s module-boundary table doesn't name a fixtures module (so `src/` isn't the
right place — it's not business logic), and Phase 7's UI/wireframe planning needs to *read these
values directly*, not just observe that a test run passed. A fixture buried inline inside a test
function's body is invisible to anyone not reading that specific test; a top-level, importable module
is something a completely different phase, working on a completely different concern (React component
props, mock JSON shapes), can import and read on its own terms.

**Checkpoint:** How does having Contract Fixtures ready *before* Phase 7 (UI planning) change what
kind of questions a frontend/TypeScript planning session can usefully ask, compared to planning
against bare `TypedDict` shapes alone?

<details>
<summary>Reveal answer</summary>

A bare `TypedDict` shape answers "what keys and types exist," which is enough to generate a
TypeScript `interface` but nothing else — it can't answer "how long does a typical
`message_text` get, so how should this table cell wrap or truncate?" or "does `aging_bucket_counts`
ever have a zero-count bucket, and should the chart still render a slice for it?" A populated,
believable fixture answers exactly those layout and edge-case questions, because it's a concrete
instance a designer or frontend engineer can look at and reason about visually — `PAYMENT_AGING_ROW_
FIXTURE`'s actual `message_text` string, multi-line and address-formatted, is a much better prompt
for "how should this render" than the bare fact that the field is typed `str`.
</details>

**Try it yourself:** Open `src/contracts.py` and find `ReportManifest`'s field list. Then look at
`REPORT_MANIFEST_FIXTURES`'s three entries and confirm every one of `ReportManifest`'s fields appears
in all three — this is what "the family is reused correctly across its real variation" means
concretely: same keys, three legitimately different `sheet_names` lists.

## Full data flow: generating and round-tripping the high-priority overdue invoice example

1. A caller (in Phase 2, `write_sample_workbooks()`; in the real README workflow, a one-line
   `uv run python` command) calls `generate_invoices(reference_date)` —
   [`src/sample_data.py:140`](../../src/sample_data.py#L140) — with a resolved `date`, never `None`,
   by the time it reaches the row-building code.
2. `reference_date is None` is `False` (a real date was passed or already resolved), so the `if`
   block at [`src/sample_data.py:147-148`](../../src/sample_data.py#L147-L148) is skipped.
3. The closure `offset(days)` ([`src/sample_data.py:150-153`](../../src/sample_data.py#L150-L153)) is
   defined, capturing `reference_date` from the enclosing scope.
4. The `INV-2026-001` row literal ([`src/sample_data.py:157`](../../src/sample_data.py#L157)) calls
   `offset(160)` for `invoice_date` and `offset(130)` for `due_date` — both resolved to real `date`
   objects relative to whatever `reference_date` this call received.
5. `generate_invoices` returns a plain `pd.DataFrame` containing this row among 26 others — no I/O
   has happened yet.
6. `write_sample_workbooks()` ([`src/sample_data.py:230`](../../src/sample_data.py#L230)) receives
   this DataFrame and calls `invoices_df.to_excel(output_dir / "sample_invoices.xlsx", index=False)`
   ([`src/sample_data.py:236`](../../src/sample_data.py#L236)) — the first and only point in this
   whole trace where a side effect (a file write) occurs.
7. `test_write_sample_workbooks_round_trips_through_excel`
   ([`tests/test_sample_data.py:328-344`](../../tests/test_sample_data.py#L328-L344)) reads the file
   straight back with `load_excel()` (Tutorial 01's function) and calls
   `validate_required_columns(invoices_df, INVOICE_REQUIRED_COLUMNS, "invoices file")` — proving the
   round trip through a real `.xlsx` file preserves every column payment aging (Phase 5) will
   eventually need, without this test knowing or asserting anything about aging buckets themselves.

Nothing in this trace computes `days_overdue` or an aging bucket — `test_generate_invoices_high_
priority_example_is_unambiguously_overdue` (`tests/test_sample_data.py:259-273`) only checks that this
row's *raw materials* (`days_before_reference > 60`, `outstanding >= 50000`) are shaped correctly for
whatever Phase 5 will eventually compute from them.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): `test_generate_invoices_dates_shift_with_reference_date`
(`tests/test_sample_data.py:291-301`) is the one test that actually exercises two *different* values
of `reference_date` and checks the relationship between their outputs. Trace through exactly which
lines of `generate_invoices()` execute differently between the `reference_a` and `reference_b` calls,
and write out, in your own words, why `row_b["due_date"] == row_a["due_date"] + timedelta(days=10)`
is a stronger assertion than just checking that the two dates are merely *different*.

<details>
<summary>Hint</summary>

Nothing about the row *literal* for `INV-2026-001` changes between the two calls — only the argument
passed into `offset()` changes, because `reference_date` is a different closure-captured value on
each call. The assertion is strong specifically because it checks the *offset relationship* is
preserved exactly (10 days difference in, 10 days difference out) rather than merely "some
difference exists" — the weaker check would pass even if the offset math had a subtle bug that
shifted dates by the wrong amount.
</details>

**Challenge 2 — Extend** (20–30 min): Add one new intentional data imperfection to `generate_orders()`
following the existing "combo issue" comment style (see lines 95–104 for examples): a row with a
missing `customer_region` (blank/`None`) combined with a `priority` value of `"Critical"` (not one of
the valid `"High"`/`"Normal"`/`"Low"` values — reusing the existing invalid-priority pattern but on a
new row). Give it a new unique `order_id` continuing the `SO-2026-0XX` sequence. Then add a new test
in `tests/test_sample_data.py`, following the exact naming and structure of
`test_generate_orders_has_exactly_one_missing_sku_row`, that asserts exactly one row has a missing
`customer_region`. Finally, check whether `test_generate_orders_row_count_and_issue_ratio_stay_moderate`
still passes with the new row counted — if it doesn't, decide whether to add your new `order_id` to
`issue_order_ids` or adjust the ratio bounds, and justify your choice in one sentence.

<details>
<summary>Hint</summary>

Look at `SO-2026-032` (line 96) for the pattern of setting a field to `None` inside the row's dict
literal, and `SO-2026-034` (line 100) for the pattern of an intentionally invalid enum-like value.
`issue_row_count` in the ratio test currently lists six specific `order_id`s by name plus `+1` for
the duplicate — your new row needs to be added to that set for the ratio to still reflect reality,
otherwise the ratio silently undercounts by one imperfection.
</details>

**Challenge 3 — Break and fix / Design** (30–45 min): Search `tests/test_sample_data.py` for every
call to `generate_invoices(...)` and `write_sample_workbooks(...)` and confirm — as this tutorial's
Part 1 asserts — that *every single one* passes an explicit `reference_date`, meaning the actual
`if reference_date is None: reference_date = date.today()` branch (line 147–148) is never executed by
the test suite at all. Design a test that *would* exercise the true default path without making the
test's result depend on which day it happens to run (a naive `assert generate_invoices().iloc[0].
invoice_date == some_hardcoded_date` would break every day). Write the actual test, run it, and
confirm it passes.

<details>
<summary>Hint</summary>

You don't need to know today's exact date inside the test — you need to assert a *relationship* that
holds regardless of what "today" is, the same technique
`test_generate_invoices_dates_shift_with_reference_date` already uses. Try calling
`generate_invoices()` with no argument at all, then separately calling
`generate_invoices(reference_date=date.today())` explicitly, and asserting the two results are
identical (`.equals()` on the DataFrames, or comparing one specific row's dates) — this proves the
`None`-sentinel branch resolves to the same thing `date.today()` would, without the test itself ever
needing to hardcode a specific date.
</details>

For deeper exploration, `docs/plan/phase-2-sample-data/ai-discussion-topics.md` has 10 prompts
covering time-dependent defaults, demo data that ages gracefully, fixtures vs. generated data vs.
business logic, and testing generated data instead of hardcoded data. Feed them to an LLM *after*
forming your own answer first — the gap between what you thought and what you learn is where
understanding lands.
