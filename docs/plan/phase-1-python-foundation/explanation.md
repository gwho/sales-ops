# Phase 1: Python Project Foundation — Technical Explanation

## Why TypedDict instead of dataclasses or Pydantic?

The output contracts will cross a JSON boundary (FastAPI → Next.js). TypedDict gives:

- Zero runtime overhead — it's a plain dict at runtime, invisible to `json.dumps`
- Full mypy/pyright type-checking at the boundary
- No import cost in test fixtures

Dataclasses require `.asdict()` before serialisation; Pydantic adds a dependency and a learning curve that isn't needed until the API layer. TypedDict is the minimum viable type safety for a dict-shaped contract. See ADR 0004 for the full decision.

## Why pandas + openpyxl, not xlrd or polars?

- `openpyxl` is the only engine that handles `.xlsx` read/write (xlrd dropped xlsx support in v2)
- `pandas` is the lingua franca of tabular Python — interviewers recognise it immediately
- `polars` would be faster but adds an unfamiliar API with no portfolio benefit for this project size

## Why uv instead of pip + venv?

`uv` gives deterministic installs via `uv.lock` (equivalent to `package-lock.json`), parallel resolution, and a single command (`uv sync`) to reproduce the environment. It's become the modern standard for Python packaging in 2025–2026.

## How required-column validation works in excel_io.py

`load_workbook(path, sheet, required_cols)` raises a `ValueError` with a structured message listing every missing column name. This is a **business-readable error**, not a raw `KeyError`. The error shape is: `"Missing required columns: col_a, col_b"`. Tests assert on both the exception type and the message content to ensure the contract holds.

## Why sample_data/*.xlsx are deferred to Phase 2

`CLAUDE.md` defines a distinction between *demo fixtures* (believable sample workbooks) and *test fixtures* (minimal DataFrames in pytest). Phase 1 only needs the latter — a sample workbook with meaningful data requires knowing the exact column set each module will consume, which solidifies in Phase 2 as the first business-rule module (`order_validation.py`) is built.

## Module boundary enforcement

`excel_io.py` may not contain workflow-specific rules. `contracts.py` may not contain loading logic. This mirrors the single-responsibility principle and makes it easy to test each module in isolation — `test_excel_io.py` never imports `contracts.py`, and vice versa.
