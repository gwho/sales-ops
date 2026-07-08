# Python-First Sequence Plan

## What Changed

The build order changed from static Next.js UI first to Python business-rule core first.

## Why

The project is meant to prove practical sales admin automation. The specs already define the data shapes clearly; the bigger risk is spending the first milestone on dashboard polish and running out of time before the actual automation exists.

Tested order validation, inventory allocation, payment aging, and Excel report export are the core portfolio evidence. The dashboard should present that evidence, not substitute for it.

## New Build Order

1. Scaffold Python project, tests, and sample data folders.
2. Generate fictional sample Excel files and representative fixtures that populate the Phase 1 contract TypedDicts.
3. Implement and test order validation.
4. Implement and test inventory allocation.
5. Implement and test payment aging.
6. Implement and test Excel report export.
7. Define UI contracts and wireframes from Phase 1 contracts and Phase 2 fixtures. This can run in parallel with Python implementation.
8. Build the polished Next.js dashboard only after all spec-listed Python tests and Excel report structure tests pass.
9. Add FastAPI integration.

## Files Updated

- `context/project-overview.md`
- `context/architecture.md`
- `context/build-plan.md`
- `context/code-standards.md`
- `context/library-docs.md`
- `context/ui-rules.md`
- `context/ui-registry.md`
- `context/progress-tracker.md`
- `docs/adr/0001-nextjs-v2-first.md`
- `docs/adr/0002-static-mock-ui-before-python-fastapi.md`
- `docs/adr/0003-python-core-before-polished-ui.md`
