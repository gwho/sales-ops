# Python-First Sequence Explanation

## Reasoning

The first UI-first plan optimized for visual polish. That is useful, but it could produce a portfolio demo that looks good while the actual sales admin automation remains unproven.

The reason for Python-first is not that the output shapes are unknown. The specs already define inputs, rules, outputs, and suggested functions. The reason is that the business logic is the actual deliverable for this portfolio's audience.

The revised sequence optimizes for credibility:

- Python modules prove the business rules.
- pytest tests prove edge cases and prevent regressions.
- sample Excel files show realistic workflow inputs.
- report exports show usable operational outputs.
- the later Next.js UI can map every table, KPI, chart, and status badge to real outputs.

## UI Impact

UI design does not stop. It moves earlier only as planning:

- wireframes
- component inventory
- table column mapping
- Figma/MCP critique
- TypeScript interface planning

This planning can begin after Phase 2 because it needs field shapes and example values, not finished rule implementations.

Final screen implementation waits until the concrete implementation gate is satisfied: all spec-listed business-rule tests and Excel report structure tests pass.

## Fallback Demo

Phase 6 is valuable even without Next.js. Tested Python modules plus professional Excel reports are a complete interview artifact: the reports can be opened, screenshotted, and explained as practical sales/admin automation.

## Architecture Impact

The future Next.js and FastAPI layers become adapters over the Python core, not places where business rules are invented. FastAPI routes stay thin, and React components stay presentational.
