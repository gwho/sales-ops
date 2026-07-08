# Context Reset Plan

## What Changed

The project context was reset from the old JobPilot domain to Sales Admin Automation Toolkit.

The active target was initially reset toward a polished Next.js dashboard with mock data first. That sequence has now been superseded by ADR 0003: Python business-rule core first, polished Next.js dashboard second.

## Why

Future agents need one clear source of truth. The existing `context/` files described an unrelated job-hunting app and would cause incorrect architecture, UI, events, and backend choices.

## Files Updated

- `context/project-overview.md`
- `context/architecture.md`
- `context/ui-tokens.md`
- `context/ui-rules.md`
- `context/ui-registry.md`
- `context/code-standards.md`
- `context/library-docs.md`
- `context/build-plan.md`
- `context/progress-tracker.md`
- `context/designs/README.md`
- `CONTEXT.md`
- `docs/adr/0001-nextjs-v2-first.md`
- `docs/adr/0002-static-mock-ui-before-python-fastapi.md`
- `docs/adr/0003-python-core-before-polished-ui.md`

Removed from active context:

- `context/jobsdb-apify-plan.md`

## Scope

This feature updates planning, domain language, UI workflow, and build guidance only. It does not scaffold the Python project, Next.js app, or UI components yet.
