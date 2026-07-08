# Memory — Repo Init + Phase 1 Tooling Grilling + Phase 1 Implementation

Last updated: 2026-07-09

## What was built

- `CLAUDE.md` at repo root (via `/init`).
- `docs/adr/0004-phase-1-python-tooling.md` — Phase 1 tooling decisions (Python version, dependency manager, pytest config location, file scope, README workflow), produced via a `/grill-with-docs` session.
- `docs/adr/0005-payment-data-issue-row-contract.md` — adds a 13th output-contract family, `PaymentDataIssueRow`, that the original required-families list was missing (spec `03_demo_payment_aging.md` PA-006/PA-007 require it; discovered while writing `contracts.py`).
- **Phase 1 implementation is done**: `.python-version` (3.12), `pyproject.toml` + `uv.lock` (deps: `pandas`, `openpyxl`; dev: `pytest`), `.gitignore`, `README.md`, `src/__init__.py`, `src/excel_io.py` (`load_excel`, `validate_required_columns`, `MissingColumnsError` with business-readable messages), `src/contracts.py` (all 13 `TypedDict` output families), `tests/test_excel_io.py`, `tests/test_contracts.py`, empty `sample_data/`. `uv run pytest` passes (7 tests).
- Registered the `remember` skill globally at `~/.claude/skills/remember/SKILL.md`.

## Decisions made

1. **ADR 0003 rationale corrected**: Python-first sequencing is about sequencing risk, not shape-invention risk (specs already define shapes in detail).
2. **Phase 1 scope**: `excel_io.py` + `contracts.py` are foundational infra, not just empty scaffolding.
3. **Sample data vs. test fixtures**: `sample_data/*.xlsx` = believable demo fixtures (mostly clean, 2-3 imperfections); pytest DataFrame fixtures = exhaustive edge-case coverage. Distinct from a "Contract Fixture" (a realistic example value proving a contract shape, built in Phase 2).
4. **Field Scope Boundary**: a contract only gets fields its originating spec explicitly defines — no cross-module symmetry additions.
5. **Two UI gates**: Phase 7 (planning) can start after Phase 2; Phase 8 (real Next.js code) is hard-gated on Phase 3-6 tests passing.
6. **Scope Gate**: only V1/unlabeled spec rules; Optional/V1.5/V2 and the CRM Cleaner module need a new ADR.
7. **Phase 1 tooling** (ADR 0004): Python 3.12 pinned via `.python-version`; `pyproject.toml` + `uv` (no `requirements.txt`, no pip/poetry), `uv.lock` committed (this is an app/demo, not a library, so a committed lockfile aids reviewer reproducibility); pytest config lives in `pyproject.toml` under `[tool.pytest.ini_options]`; function-based tests, `test_*.py`, `test_<behavior>`, no `pytest-cov` yet; Phase 1 file scope is exactly `src/__init__.py` + `excel_io.py` + `contracts.py` + their two test files — no placeholder stubs for later-phase modules; README documents only the `uv` workflow.
8. **PaymentDataIssueRow added** (ADR 0005): mirrors `ValidationErrorRow`'s shape (`invoice_id`, `customer_name`, `error_code`, `error_message`, `severity`) but stays a separate TypedDict rather than a shared generic error-row type, per the Field Scope Boundary — order validation and payment aging are different specs.
9. **BackorderRow** is defined as an empty subclass of `AllocationResultRow` (same shape — Backorders sheet is Allocation Results filtered to `status=Backordered`; no separate column table exists in the spec).
10. **SupplierFollowUpRow** and **ReportManifest** fields were inferred (no explicit column table in specs) from directly-adjacent spec facts: `SupplierFollowUpRow` from inventory.xlsx's `supplier_name`/`lead_time_days`/`reorder_point` plus computed `remaining_qty`; `ReportManifest` from the already-documented `GET /api/reports/{report_id}` endpoint (`report_id`, `report_type`, `file_name`, `generated_at`, `sheet_names`) — architecture-level plumbing, not a business-rule invention, so no ADR needed.

## Problems solved

- Phase 2 was worded as "define output contracts" after `contracts.py` moved to Phase 1 — reframed as "Sample Data and Contract Fixtures".
- Terminology (output contract, contract fixture, field scope boundary, scope gate, V1/V2) formalized as `CONTEXT.md` glossary entries.
- `requirements.txt` vs `pyproject.toml` and Python version were open questions blocking Phase 1 — resolved via ADR 0004 before writing code.
- Missing `PaymentDataIssueRow` contract family caught before it caused a silent gap in Phase 5 — resolved via ADR 0005, user chose "add it now" over deferring or reusing `ValidationErrorRow`.

## Current state

Phase 1 (Python Project Foundation) is complete and tested. All context docs reflect current decisions: `docs/adr/0003`, `0004`, `0005`; `context/build-plan.md`, `context/progress-tracker.md`, `context/code-standards.md`, `context/architecture.md`, `CONTEXT.md`, `CLAUDE.md`. `context/progress-tracker.md` Phase 1 checkboxes are all checked. No git repo initialized yet (`.gitignore` is in place for when it is).

## Next session starts with

Begin Phase 2 — Sample Data and Contract Fixtures (`context/progress-tracker.md`): generate `sample_orders.xlsx`, `sample_product_master.xlsx`, `sample_inventory.xlsx`, `sample_invoices.xlsx` (each mostly clean with the specific realistic imperfections listed in `context/build-plan.md`), then populate contract fixtures (realistic example dicts) for all 13 families in `src/contracts.py`, including the new `PaymentDataIssueRow`.

## Open questions

None outstanding. Both prior Phase 1 tooling questions (Python version, dependency tooling) are resolved per ADR 0004.
