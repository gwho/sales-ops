# ADR 0001 - Build Next.js V2 First

## Status

Superseded by [ADR 0003](0003-python-core-before-polished-ui.md)

## Context

The sales toolkit specs originally recommend a simple Python/Streamlit path as the fastest working demo. The current project direction prioritizes a polished portfolio dashboard and modern UI presentation for hiring-manager impact.

The workspace also contains extensive UI and Figma/MCP planning material for a professional B2B dashboard.

## Original Decision

Build the first implementation target as a Next.js App Router dashboard using TypeScript, Tailwind CSS 3.4, shadcn/ui, tables, charts, and mock data.

Streamlit is not the active V1 path for this repo.

## Supersession Note

The project still targets a polished Next.js dashboard, but the first implementation milestone is now the Python business-rule core and data contracts. This avoids building a visually polished UI around unstable or invented outputs.

## Original Consequences

- The first milestone emphasizes visual polish, reusable components, and stable frontend contracts.
- Python spreadsheet logic is postponed until after the UI and contracts are stable.
- The implementation must actively avoid expanding into full ERP scope.
- Context files must guide future agents toward Next.js dashboard work, not Streamlit-first work.

These consequences are no longer active after ADR 0003.
