# Memory — Phase 2: Sample Data and Contract Fixtures

Last updated: 2026-07-09

## What was built

- `src/sample_data.py` — 4 generator functions (`generate_product_master`, `generate_orders`, `generate_inventory`, `generate_invoices`) plus `write_sample_workbooks()`. `generate_invoices`/`write_sample_workbooks` take `reference_date: date | None = None`, resolved to `date.today()` inside the function body.
- `sample_data/*.xlsx` (committed, generated once and checked in): `sample_orders.xlsx` (12 lines, 1 duplicate `order_id` = `SO-2026-005`, 1 unknown SKU `MED-LENS-999` on `SO-2026-009`), `sample_product_master.xlsx` (8 SKUs, 1 inactive = `ELEC-CABLE-008`), `sample_inventory.xlsx` (2 warehouses; `MED-LENS-001` scarce — HK 20 units, SG 5 units with `reorder_point=6` so SG already sits below reorder point as a static fact; total `MED-LENS-001` demand 35 vs supply 25, by design, to force partial allocation once Phase 4 exists), `sample_invoices.xlsx` (10 invoices; `INV-2026-001` is the designated high-priority overdue example — `reference_date - 70 days` due date, $58,000 outstanding; `INV-2026-009` has a missing due date as the one data-issue row).
- `tests/contract_fixtures.py` — 13 hand-authored fixture constants, one per `src/contracts.py` output family (12 single dicts + `REPORT_MANIFEST_FIXTURES` as a list of 3, one per required Phase 6 report).
- `tests/test_sample_data.py` (new) and `tests/test_contracts.py` (extended) — column/imperfection-count/round-trip tests. `uv run pytest` passes: 32 tests total (7 from Phase 1, 25 new).
- `docs/plan/phase-2-sample-data/` — `plan.md`, `explanation.md`, `ai-discussion-topics.md`.
- `context/progress-tracker.md` updated: Phase 2 checked off, current phase now Phase 3.
- Fixed stale "Project state" section and the "Planned Python scaffold (not yet created)" table in root `CLAUDE.md` — both said no app code existed / Phase 1 was next, which was out of date after Phase 1 and now Phase 2 completed.

## Decisions made

1. **Date anchoring**: only `sample_invoices.xlsx` uses `reference_date`-relative dates (payment aging depends on "today"); `sample_orders.xlsx`/`sample_inventory.xlsx` use fixed 2026-07 dates since order/allocation rules never compare against "today".
2. **`reference_date: date | None = None`, not `= date.today()`** — a literal default is evaluated once at import time and freezes; the `None`-sentinel resolves it per call.
3. **Contract fixtures live in `tests/contract_fixtures.py`**, not inline in tests and not a new `src/` module — `context/architecture.md`'s module-boundary table doesn't name a fixtures module, and Phase 7 (UI planning) needs to read these values directly.
4. **`REPORT_MANIFEST_FIXTURES` is the one list-of-3 exception** to "one fixture per family" — a single manifest wouldn't show the family's real reuse pattern (one per required Phase 6 report: order_validation, inventory_allocation, payment_aging).
5. Fixtures are explicitly documented as hand-authored, not computed by `sample_data.py` or any business-rule module (those don't exist until Phases 3-5) — a fixture proves a shape can hold a believable value, not that a rule is correctly implemented.
6. The "SKU near reorder point" imperfection is authored as a static fact in the raw inventory data (`available_qty < reorder_point` as written for `MED-LENS-001` SG Warehouse), not simulated via allocation math — keeps Phase 2 tests from reimplementing Phase 4/5 logic early.
7. Both `/architect` decisions (date anchoring, fixture location) were made via `AskUserQuestion` during a plan-mode `/architect` session before any code was written; the resulting plan was saved to `~/.claude/plans/phase-2-sample-magical-mango.md` and approved with 5 user-requested edits (the `None`-sentinel fix, avoid reimplementing Phase 5 aging logic in tests, add optional source columns for realism, add explicit "not business output" boundary note to fixtures, fix stale `CLAUDE.md`).

## Problems solved

- Avoided a live default-argument bug (`date.today()` as literal default) before it was ever written, via user's Step-1 review feedback on the plan.
- Balanced "prove the data will force partial allocation in Phase 4" against "don't reimplement Phase 4 in a Phase 2 test" by using a static below-reorder-point fact instead of computing allocation outcomes; `test_generate_inventory_has_at_least_one_sku_below_reorder_point` checks this directly with plain arithmetic, no sorting/warehouse-choice logic.
- Root `CLAUDE.md` had drifted out of sync with `context/progress-tracker.md` after Phase 1 completed (still said "no app code exists yet... next is Phase 1") — now both agree.

## Current state

Phase 2 complete and tested (`uv run pytest` → 32 passed). All context docs in sync: `context/progress-tracker.md`, root `CLAUDE.md`. No git repo initialized yet in this project (still no `git init` run — `.gitignore` has been in place since Phase 1).

## Next session starts with

Begin Phase 3 — Order Validation Core (`context/progress-tracker.md`): implement `src/order_validation.py` covering every rule in `sales_admin_automation_toolkit_specs/01_demo_order_validation.md` (OV-001 through OV-007) plus `tests/test_order_validation.py` with small inline DataFrame fixtures for exhaustive edge-case coverage (not `sample_data/*.xlsx`, which stays believable-but-mostly-clean per Phase 2's design). Phase 7 (UI/TypeScript planning, docs-only) may also start in parallel now that Phase 2 contract fixtures exist, if the user wants to run it alongside Phase 3.

## Open questions

None outstanding. Both Phase 2 architecture decisions (date anchoring, fixture location) are resolved and implemented.
