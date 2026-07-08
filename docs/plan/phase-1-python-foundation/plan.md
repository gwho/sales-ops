# Phase 1: Python Project Foundation — Plan

## What was built

The Python project scaffold required by `context/build-plan.md` Phase 1:

| Artifact | Purpose |
|---|---|
| `pyproject.toml` | Project metadata, dependencies (pandas, openpyxl), dev deps (pytest), tool config |
| `.python-version` | Pins Python version for uv |
| `uv.lock` | Locked dependency tree |
| `src/__init__.py` | Package marker |
| `src/excel_io.py` | `load_workbook()` — loads an `.xlsx` sheet into a DataFrame with required-column validation and consistent missing-column error shapes |
| `src/contracts.py` | `TypedDict` output-contract definitions for every output family (see below) |
| `tests/test_excel_io.py` | Unit tests for `load_workbook()` happy path and missing-column errors |
| `tests/test_contracts.py` | Structural tests that verify every required key is present in each contract |
| `sample_data/.gitkeep` | Placeholder — sample workbooks generated in Phase 2 |

## Output contracts defined (src/contracts.py)

- `ValidationSummary`, `ValidationErrorRow`, `ValidOrderRow`
- `AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`, `SupplierFollowUpRow`
- `PaymentAgingSummary`, `PaymentAgingRow`, `PaymentDataIssueRow`, `DraftMessageRow`
- `ReportManifest`

All contracts are `TypedDict` (snake_case keys, JSON-serializable types) per the output-contract rules in `CLAUDE.md`.

## Why this order

ADR 0003 establishes Python-core-before-UI. ADR 0004 documents the Phase 1 tooling decisions (uv, pyproject.toml, TypedDict over dataclasses). Phase 1 is intentionally restricted to scaffold + contracts — no business rules, no sample workbook generation, no FastAPI.
