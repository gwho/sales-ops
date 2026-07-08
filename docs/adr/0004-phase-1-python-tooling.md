# ADR 0004 - Phase 1 Python Tooling and Scaffolding Conventions

## Status

Accepted

## Context

ADR 0003 locked the Python-first build sequence but left several implementation-level questions open. `context/build-plan.md` explicitly listed `requirements.txt` or `pyproject.toml` as an undecided choice, and no context file specified a Python version, a dependency manager, pytest's config location, or whether Phase 1 should stub out modules owned by later phases.

These aren't architectural questions — they don't reopen ADR 0003 — but they do lock conventions that every later phase (2 through 6) will build on, so resolving them once now avoids drift.

## Decision

1. **Python version:** 3.12, pinned via a `.python-version` file at the repo root.
2. **Dependency tooling:** `pyproject.toml` + `uv`. `uv sync` creates the venv and installs dependencies per `pyproject.toml` / `uv.lock`; `uv run pytest` runs tests without manual venv activation. No `requirements.txt`, no pip/poetry. `uv.lock` is committed — this repo is a portfolio demo application, not a reusable library, so a committed lockfile buys reviewer setup reproducibility rather than fighting a consumer's own dependency resolution.
   - Phase 1 runtime deps: `pandas`, `openpyxl`. Dev deps (`[dependency-groups].dev`): `pytest`. Nothing else until a later phase actually needs it.
3. **pytest configuration:** lives in `pyproject.toml` under `[tool.pytest.ini_options]` (no separate `pytest.ini`):
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["."]
   addopts = "-q"
   ```
   Conventions: function-based tests only (no test classes unless a later module has a real shared-state reason), files named `test_*.py`, test functions named `test_<behavior>`, small DataFrame fixtures defined inline in test files. No `pytest-cov` / coverage threshold in Phase 1 — revisit after Phases 3-5 have real rule logic to measure, or during Phase 6 hardening.
4. **Phase 1 file scope:** only `src/__init__.py`, `src/excel_io.py`, `src/contracts.py`, `tests/test_excel_io.py`, `tests/test_contracts.py`. No placeholder/stub files for `order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, `report_export.py`, or `sample_data.py` — those are created in the phase that actually implements them (Phase 2 for `sample_data.py`, Phase 3-5 for the rule modules, Phase 6 for `report_export.py`). The "planned modules" block in `CLAUDE.md` / `context/build-plan.md` already documents the target shape; empty files would add no executable behavior and would go stale before their real phase arrives.
5. **README setup notes:** document the `uv` workflow only (`uv sync`, `uv run pytest`) — no manual `python -m venv` / `pip install -r requirements.txt` fallback instructions.

## Consequences

- `context/build-plan.md`'s Phase 1 checklist item "`requirements.txt` or `pyproject.toml`" is resolved — always `pyproject.toml`.
- Every later phase adds its business module and its test file in the same phase, not before — keeps `progress-tracker.md` checkboxes honest (checked means implemented, not stubbed).
- Coverage enforcement is deferred; if a future phase wants it, that's a small addition to `pyproject.toml`, not a new ADR.
- Reviewers/interviewers need `uv` installed to run the project locally; no pip fallback path is documented.
