# Context Reset Explanation

## Domain Reset

The old context described JobPilot, a job-hunting assistant. That domain conflicted with the new sales admin automation specs. The reset makes Sales Admin Automation Toolkit the only active project in the context folder.

The old JobsDB/Apify plan was removed from active context because it was entirely tied to JobPilot job discovery. Legacy image assets remain under `context/designs/`, but the new README marks them as archived and not valid Sales Admin UI references.

## Build Strategy

The docs now reflect the revised selected path: Python business-rule core first, with the polished Next.js dashboard built after the output contracts are stable.

This change was made because the strongest portfolio proof is tested Excel automation for sales admin workflows. The UI should present real validation, allocation, aging, and report outputs rather than inventing dashboard data before the rules exist.

## UI Workflow

The Figma and MCP prompt packs were incorporated as optional workflow guidance. They are useful for design inspection, critique, component mapping, and scope control, but they are not treated as final product requirements.

## Domain Modeling

`CONTEXT.md` now defines business terms such as Order Line, Validation Error, Allocation Result, Backorder, Aging Bucket, Follow-up Priority, and Report Pack. This gives future planning and implementation sessions a stable vocabulary.

## ADRs

Three decisions were recorded because they are meaningful tradeoffs:

- Next.js V2 first instead of Streamlit V1.
- Static mock UI before Python/FastAPI integration.
- Python core before polished UI.

ADR 0003 supersedes the first sequencing decisions. Next.js remains the polished UI target, but it is no longer the first implementation milestone.
