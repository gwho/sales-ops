# ADR 0003 - Build Python Core Before Polished UI

## Status

Accepted

## Context

The project is a portfolio demo for sales admin and operations workflows. The strongest portfolio proof is not just a polished dashboard; it is credible automation of Excel-based order validation, inventory allocation, payment aging, and report export.

The functional specs already define input columns, business rules, output columns, and suggested function signatures in enough detail that output-shape ambiguity is not the main risk.

The main risk is sequencing. If the project starts with polished UI, it could spend the available time and energy on presentation before the substantive portfolio payload exists. For this audience, the payload is the tested Python automation: rules, edge cases, sample Excel files, and report outputs that prove the candidate understands sales/admin operations.

## Decision

Build the Python business-rule core first, then build the polished Next.js dashboard on top of the proven outputs.

The active sequence is:

1. Python modules for order validation, inventory allocation, payment aging, and report export.
2. pytest coverage for the business rules.
3. Fictional sample Excel files.
4. Stable JSON-like output contracts derived from the specs and verified by implementation.
5. Next.js UI wireframes and component contracts.
6. Polished Next.js dashboard using mock data generated from the Python output shapes.
7. FastAPI integration after both Python logic and UI contracts are stable.

## Consequences

- The project is less likely to end with polished presentation but unfinished business logic.
- The project is easier to explain in interviews because the rules, tests, sample files, and spreadsheet workflow are concrete.
- The Next.js dashboard remains important, but it is a presentation layer over proven logic.
- Figma/MCP design work should happen at wireframe and component-mapping level until the Python outputs are stable.
- Streamlit remains optional and is not the main UI target unless the project direction changes again.
