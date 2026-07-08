# Code Standards

## Engineering Rules

- Read the context files before implementation.
- Build the Python business-rule core before polished UI.
- Keep V1 scoped to fictional Excel automation for order validation, inventory allocation, payment aging, and report export.
- Do not add auth, database persistence, AI features, email sending, or ERP workflows unless the context is updated first.
- Use fictional data only.
- Keep business logic visible, testable, and explainable.
- Separate spreadsheet I/O, business rules, report export, future API adapters, and future UI components.

## Scope Control

Before implementing any rule or module from the specs, apply the scope gate in `context/architecture.md`.

Mechanical check:

- In-scope: rules in `01_demo_order_validation.md`, `02_demo_inventory_allocation.md`, and `03_demo_payment_aging.md` that are labeled V1 or not version-labeled.
- Out of scope: any rule marked `Optional`, `V1.5`, or `V2`.
- Out of scope: all of `04_optional_crm_cleaner.md`.
- Required to change scope: a new ADR that explicitly names the rule/module being added and why it is worth expanding V1.

Do not implement V2 rules just because they are trivial. The current project values a finished, explainable V1 over extra features.

## Python

- Target Python 3.12, pinned via `.python-version`. Dependencies managed with `pyproject.toml` + `uv` (`uv sync`, `uv run pytest`) — no `requirements.txt`, no pip/poetry (see `docs/adr/0004-phase-1-python-tooling.md`).
- Prefer clear, explicit functions over clever abstractions.
- Use type hints for public functions.
- Keep business-rule functions deterministic where practical.
- Return DataFrames or JSON-serializable dictionaries consistently per module.
- Do not print from business logic; return structured errors or results.
- Convert technical parsing issues into business-readable messages at module/API boundaries.
- Avoid hidden global state.

## Python Module Boundaries

| Module | Owns |
| --- | --- |
| `excel_io.py` | Loading Excel files, validating required columns, shared normalization helpers |
| `order_validation.py` | Order validation rules and validation output |
| `inventory_allocation.py` | Allocation ordering, stock depletion, backorder and supplier follow-up output |
| `payment_aging.py` | Outstanding amount, aging buckets, follow-up priority, draft reminders |
| `report_export.py` | Excel workbook generation from already-computed outputs |
| `sample_data.py` | Fictional sample workbook generation |

Do not put UI code, FastAPI route logic, or React concepts in these modules.

## pytest

- Config lives in `pyproject.toml` under `[tool.pytest.ini_options]` — no separate `pytest.ini` (see `docs/adr/0004-phase-1-python-tooling.md`).
- Function-based tests only; no test classes unless a later module has a real shared-state reason.
- Files named `test_*.py`, mirroring the `src/` module they cover; test functions named `test_<behavior>`.
- Add tests alongside each business module.
- Test the rules from the spec files directly.
- Prefer small DataFrame fixtures defined inline in test files for rule coverage.
- Include missing-column and invalid-data cases.
- Test that inventory never goes negative.
- Test Excel export sheet names and basic workbook structure.
- Exhaustive rule/edge-case coverage lives in pytest DataFrame fixtures, not in `sample_data/*.xlsx`. Sample workbooks are demo fixtures: plausible and mostly clean, with a small number of realistic imperfections, so they read as a believable sales-ops day rather than a disguised test matrix.
- No `pytest-cov` / coverage threshold until after Phases 3-5 have real rule logic to measure, or during Phase 6 hardening.

## Data Contracts

The Python outputs should become the source of truth for later TypeScript contracts.

Rules:

- Use stable, business-readable field names.
- Preserve source row references for validation/data issues.
- Include both summary metrics and detail rows.
- Keep statuses as controlled strings.
- Keep error messages user-facing and non-technical.

## Future TypeScript

When the Next.js phase begins:

- Strict TypeScript only.
- No `any`; use `unknown` and narrow when needed.
- Prefer `type` for data shapes and unions.
- Use named exports for components.
- Define component prop types near the component.
- Keep shared app contracts in `types/index.ts`.
- Derive mock frontend data from Python output examples.

## Future Next.js

- App Router only.
- Server Components by default.
- Add `"use client"` only for state, effects, browser APIs, event listeners, or client-only libraries.
- Pages compose data and sections; they should not contain large reusable component implementations.
- UI components should not contain spreadsheet parsing or business-rule calculations.

Important: this repo warns that installed Next.js APIs may differ from training data. Before implementing real Next.js code, read relevant docs under `node_modules/next/dist/docs/` if dependencies are installed.

## Future Component Structure

```tsx
// External imports
import { ReactNode } from "react";

// Internal imports
import { StatusBadge } from "@/components/workflow/StatusBadge";

// Types
type MetricCardProps = {
  title: string;
  value: string;
};

// Component
export function MetricCard({ title, value }: MetricCardProps) {
  return <section>{value}</section>;
}
```

Rules:

- One reusable component per file.
- No default exports for project components.
- No hardcoded hex colors in components.
- No raw Tailwind color classes in components.
- Prefer project tokens from `ui-tokens.md`.

## Future API Boundary

FastAPI should wrap tested Python modules. Route handlers should not duplicate business rules.

Expected route-handler responsibilities:

- Receive uploaded files.
- Call Excel I/O helpers.
- Call business modules.
- Return JSON matching output contracts.
- Return report files.
- Convert exceptions into business-readable responses.

## Accessibility for Future UI

- Buttons must have clear labels.
- Status cannot rely on color only.
- Tables must have headers.
- Form controls must have labels.
- Focus states must be visible.
- Desktop and tablet layouts must not clip primary actions.

## Feature Completion

After each feature:

- Update `context/progress-tracker.md`.
- If UI components are built, update `context/ui-registry.md`.
- Create `docs/plan/<feature-slug>/plan.md`.
- Create `docs/plan/<feature-slug>/explanation.md`.
- Create `docs/plan/<feature-slug>/ai-discussion-topics.md`.
