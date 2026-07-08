# ADR 0002 - Static Mock UI Before Python/FastAPI Integration

## Status

Superseded by [ADR 0003](0003-python-core-before-polished-ui.md)

## Context

The project needs both a professional UI and credible business-rule logic. Building both at once would create too many moving parts: Excel parsing, report generation, API design, dashboard layout, table behavior, and visual polish.

The UI specs and prompt packs recommend proving the interface with mock data before connecting backend workflows.

## Original Decision

Build the first dashboard milestone with local fictional mock data and stable TypeScript contracts. Add a mock API adapter boundary so future FastAPI endpoints can replace local data without rewriting UI components.

Do not implement real file parsing, Excel generation, database persistence, or backend routes during the static UI milestone.

## Supersession Note

The project will still use mock data for early UI screens, but that mock data must be derived from the Python output contracts. The Python business-rule core now comes before polished UI implementation.

## Original Consequences

- Pages can be reviewed for clarity, polish, and business fit before backend integration.
- TypeScript contracts become the shared language between future frontend and backend work.
- Python/FastAPI work can be tested later with pytest and contract tests.
- Upload panels and report downloads are visual/static placeholders until the backend phase.

These consequences are no longer active after ADR 0003.
