# Phase 2 /architect Session — Decisions

Session: `/architect` run in plan mode, scoped to Phase 2 (Sample Data and Contract Fixtures) of
the Sales Admin Automation Toolkit. Explicitly excluded from scope: Python tooling, Python-first
architecture, business-rule implementation, UI work, report export. Two decisions were surfaced
via `AskUserQuestion` before any plan was written; a third (the `None`-sentinel fix) and several
smaller corrections came from the user's review of the first plan draft, which was rejected once
before being approved.

---

## 1. Reference-date anchoring for `sample_invoices.xlsx`

**What it is:** `sample_invoices.xlsx` due dates are computed as offsets from a `reference_date`
parameter, not hardcoded calendar dates. `sample_orders.xlsx` and `sample_inventory.xlsx` use
plain fixed dates.

**Why this and not the alternative:** Payment-aging rules (`03_demo_payment_aging.md` PA-003/
PA-004) compute `days_overdue = today − due_date` and bucket invoices by how large that gap is —
Current, 1-30 Days, 31-60 Days, 61-90 Days, 90+ Days. A hardcoded `due_date` like `2026-06-01` is
only "20 days overdue" on the day it was written; a year later it reads as "400+ days overdue."
The specific failure mode this decision prevents: the sample workbook's "Current, not yet due"
example — the one meant to demonstrate an invoice that *hasn't* aged into a bucket yet — would
silently flip into the 90+ Days bucket the first time someone reopens this portfolio project after
enough real time has passed, and nobody editing `sample_data.py` would notice, because the code
wouldn't have changed.

**Why orders and inventory don't get the same treatment:** Order validation (`OV-005`) only
compares `requested_delivery_date` against `order_date` — both fields live *inside the same row*
of the same file. Inventory allocation never references a clock at all. Neither has a "today"
dependency, so a fixed 2026-07 date is permanently correct for those two files. Applying the
reference-date pattern there too would have been unnecessary generality — solving a staleness
problem that doesn't exist for that data.

**The scope this decision was confined to:** only `generate_invoices()` and the top-level
`write_sample_workbooks()` wrapper take `reference_date`. `generate_orders()` and
`generate_inventory()` do not.

---

## 2. Contract fixture location: `tests/contract_fixtures.py`

**What it is:** The 13 hand-authored example values (one per `src/contracts.py` `TypedDict`
family) live in a new plain-data module, `tests/contract_fixtures.py` — not inline inside test
function bodies (Phase 1's pattern in `test_contracts.py`), and not a new `src/` module.

**Why not inline (Phase 1's existing style):** `context/build-plan.md`'s Phase 7 entry says UI
planning will explicitly reuse "Phase 2 contract fixtures" for TypeScript/wireframe planning.
A dict built inline inside a `def test_valid_order_row_fixture_has_required_keys(): row = {...}`
function body isn't importable or readable outside a test run — Phase 7 would have to go digging
through test source to find an example `PaymentAgingRow`. That defeats the point of Phase 2
existing as a named phase that Phase 7 depends on.

**Why not a new `src/` module:** `context/architecture.md`'s module-boundary table names exactly
six `src/` modules (`excel_io.py`, `order_validation.py`, `inventory_allocation.py`,
`payment_aging.py`, `report_export.py`, `sample_data.py`) and none of them is "fixtures." Contract
fixtures aren't business logic and aren't consumed by any of those modules — putting them in
`src/` would mean either inventing a seventh module the architecture doesn't name, or bolting them
onto an existing module that owns something unrelated. `tests/` is the correct home structurally
(it mirrors how `test_contracts.py` already exists there) and semantically (fixtures prove a
contract shape holds real-looking data, which is a testing concern even when the file itself isn't
`test_*.py`).

**The one exception carved out, and why:** `REPORT_MANIFEST_FIXTURES` is a `list[ReportManifest]`
of 3 entries (one per required Phase 6 report: order validation, inventory allocation, payment
aging) rather than a single dict like every other fixture. `CONTEXT.md`'s own definition of
Contract Fixture is singular ("a realistic example value"), but a single manifest example
wouldn't demonstrate how the family is actually used — Phase 7 will render multiple report cards
side by side, and a lone manifest gives no sense of that. The user confirmed this exception
explicitly when reviewing the plan rather than treating "singular" as a hard rule.

---

## 3. `reference_date: date | None = None`, not `reference_date: date = date.today()`

**What it is:** Both `generate_invoices()` and `write_sample_workbooks()` take
`reference_date: date | None = None` and resolve it inside the function body:

```python
def generate_invoices(reference_date: date | None = None) -> pd.DataFrame:
    if reference_date is None:
        reference_date = date.today()
```

**Why the first draft was wrong:** The initial plan (before the user's review) specified
`reference_date: date = date.today()` as a literal default. Python evaluates default argument
values exactly once, when the `def` statement executes — at module import time, not per call. A
literal `date.today()` default freezes to whatever date happened to be current when
`sample_data.py` was first imported in that process. Every later call in the same process
(a long-running notebook kernel, or eventually a FastAPI worker) would keep returning that frozen
date, defeating the entire point of decision #1 above — the invoices would still go stale, just on
a per-process basis instead of a per-commit basis. This is the canonical Python "mutable default
argument" trap, generalized to any time-dependent (not just mutable) default.

**Why the `None`-sentinel form fixes it:** Resolving `reference_date` inside the function body
means `date.today()` runs fresh on every call. The parameter can still be overridden explicitly —
which the test suite does, passing a fixed `date(2026, 7, 9)` so day-count assertions stay
deterministic across runs.

---

## 4. Test-scope boundary: assert data shape, not business-rule outcomes

**What it is:** `tests/test_sample_data.py`'s invoice tests assert the raw `due_date`/
`invoice_date` offsets from `reference_date`, and that exactly one row is unambiguously
`> 60` days before `reference_date` with `outstanding >= 50000`. They never compute or assert
`days_overdue`, `aging_bucket`, or `follow_up_priority`.

**Why this line was drawn where it was:** `payment_aging.py` — the module that owns aging-bucket
and priority logic — doesn't exist until Phase 5. The user's review feedback flagged that the
first plan draft was at risk of quietly reimplementing that logic inside a Phase 2 test just to
prove the "high-priority overdue" sample invoice was correctly categorized. Computing
`aging_bucket` from a `due_date` requires the same bucket-boundary logic (`1-30`, `31-60`, `61-90`,
`90+`) that Phase 5 is supposed to define and own — writing it early in a test file means that
logic now exists twice: once (implicitly, ungoverned by spec-derived tests) in
`test_sample_data.py`, and again for real in `payment_aging.py`, with no guarantee they agree.

**The alternative that was rejected, and its cost:** compute `days_overdue` in the test via
`(reference_date - due_date).days`, then assert it falls in a specific bucket range. This reads as
more "complete" test coverage, but it's coverage of logic that hasn't been designed yet — if Phase
5 later chooses different bucket boundaries (say, inclusive/exclusive edge handling that differs
from a hasty test-file guess), this test would need to change for reasons that have nothing to do
with `sample_data.py` itself. The chosen approach only asserts facts `generate_invoices()` is
actually responsible for: the arithmetic offset it was told to apply.

---

## 5. Optional source-file columns included for realism

**What it is:** Generated workbooks populate optional columns the specs don't require, not just
the required ones: `product_name`/`sales_owner` on orders, `reserved_qty`/`supplier_name`/
`lead_time_days` on inventory, `currency`/`payment_status`/`sales_owner`/`remarks` on invoices.

**Why:** `tests/test_sample_data.py` only validates required columns (via
`validate_required_columns` from `src/excel_io.py`), so omitting optional columns would still pass
every test. But the whole point of Phase 2's sample data — per `context/build-plan.md` — is to
read as "a believable sales-ops day," not a minimal schema-conformance fixture. A real orders
export from a sales team almost always carries `sales_owner`; leaving it out to save a few lines
of dict literal would make the demo data look more synthetic than it needs to, for no test benefit.

---

## 6. Explicit "not business output" boundary note in `contract_fixtures.py`

**What it is:** The fixtures module carries a module docstring plus an inline comment stating the
values are hand-authored, not produced by `sample_data.py`, and not evidence that
`order_validation.py`/`inventory_allocation.py`/`payment_aging.py` are implemented or correct.

**Why this needed to be written down, not just true:** `PAYMENT_AGING_ROW_FIXTURE` looks exactly
like what `payment_aging.py` will eventually produce — same keys, plausible values, internally
consistent numbers (`outstanding_amount = invoice_amount - paid_amount` checks out, `days_overdue`
matches the stated `aging_bucket`). Without an explicit disclaimer, a future reader (including a
future agent working on Phase 5) could reasonably mistake "this fixture exists and looks right" for
"this behavior has been validated," when in fact no code computed these values — a person typed
them by hand to match what the `TypedDict` shape expects.

---

## 7. Housekeeping: fix stale `CLAUDE.md` project-state text

**What it is:** The repo-root `CLAUDE.md`'s "Project state" section said "no application code
exists yet... Phase 0 planning reset is done; next is Phase 1" — true when originally written,
false after Phase 1 completed. The plan's final step rewrites that section (and a related
"Planned Python scaffold (not yet created)" table further down) to reflect Phase 1 and Phase 2 as
complete.

**Why this belongs in a Phase 2 plan at all:** The user flagged it as a real risk, not cosmetic
cleanup — `CLAUDE.md` is the first file any future agent (or the user, cold) reads before touching
this repo, per its own "Required reading order" section. A stale claim that "no `src/`, no
`pyproject.toml`" exists would actively mislead whoever reads it next into re-deriving decisions
that are already locked (Python 3.12, `uv`, the contract shapes), or worse, second-guessing
already-completed work. This is the kind of drift that compounds silently if it isn't caught at
the same time the underlying state changes.
