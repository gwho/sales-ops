# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Phase 12 (Postgres-Backed Latest-Session Dashboard) is complete. The project now includes the tested Python business-rule core, generated fictional Excel sample data, Excel report exports, a polished Next.js dashboard/workflow UI, a stateless-by-default FastAPI backend that live-wires the three workflow pages, and — as of Phase 12 — a narrow, best-effort Postgres persistence layer (Neon) that lets the dashboard reflect each anonymous visitor's own latest saved results, falling back to sample data per workflow when none exist. Check `context/progress-tracker.md` for the authoritative current status before starting work; this file is operational guidance and should stay aligned with that tracker.

Current implementation summary:

- Python core: `src/order_validation.py`, `src/inventory_allocation.py`, `src/payment_aging.py`, `src/report_export.py`, `src/excel_io.py`, `src/contracts.py` (now also holds `CONTRACT_SCHEMA_VERSIONS`), and `src/sample_data.py`.
- Sample data: committed fictional `.xlsx` files under `sample_data/`, plus `sample_data/README_sample_data.md`; `sample_customers.xlsx` is reference-only and not used by live workflows.
- Frontend: Next.js App Router routes for `/dashboard`, `/order-validation`, `/inventory-allocation`, `/payment-aging`, and `/reports`, with reusable components recorded in `context/ui-registry.md`.
- Backend: `backend/` FastAPI package with the three workflow/report endpoints, allowlisted sample-file downloads, and (Phase 12) a Postgres-backed `workflow_results` store plus `GET /api/dashboard`.
- Data flow: workflow pages process user-uploaded or sample `.xlsx` files through FastAPI, which also makes a best-effort save (`X-Persisted` header) keyed by a browser-local Anonymous Session ID. `/dashboard` now shows that session's latest saved result per workflow, falling back to sample data independently for any workflow not yet run; `/reports` remains a curated sample-data view.
- Last known verification from memory: `uv run pytest` 212 passing / 7 skipped (skips are `@pytest.mark.db` tests requiring `TEST_DATABASE_URL`, fully hermetic without it); `npm run typecheck`, `npm run lint`, and `npm run build` clean. Re-run checks before relying on this in a new session.

Known local loose ends from the last saved session:

- Re-check live PR merge status before assuming the stacked PR state.
- `memory.md` may be modified locally and is intentionally not committed.
- Local dev servers were left running against the Neon `dev` branch at the end of the Phase 12 session (FastAPI `:8000`, Next.js `:3000`) — safe to leave running or restart.
- `git stash@{0}` still holds the paused SQLite reporting work, unaffected by and superseded (for dashboard purposes) by Phase 12 — its fate (delete vs. keep as historical reference) is still an open question.
- Whether/when to merge the stacked PR chain remains the user's call, unchanged across every phase since Phase 4.

**Sales Admin Automation Toolkit** is a portfolio project simulating Excel-based sales administration workflows: order validation, inventory allocation, payment aging, and report export. It is explicitly **not** a full ERP/CRM/WMS/accounting system, and uses fictional data only — never real customer, order, invoice, or product data.

## Required reading order before implementing anything

Per `AGENTS.md`, read these in order before writing code:

1. `context/project-overview.md`
2. `context/architecture.md`
3. `context/ui-tokens.md`
4. `context/ui-rules.md`
5. `context/ui-registry.md`
6. `context/code-standards.md`
7. `context/library-docs.md`
8. `context/build-plan.md`
9. `context/progress-tracker.md`

`CONTEXT.md` at the repo root is the project glossary — business terms (Order, SKU, Allocatable Quantity, Aging Bucket) plus process terms resolved during planning (Output Contract, Contract Fixture, Field Scope Boundary, Scope Gate, V1/V2). Check it before using any of these terms loosely.

## Build sequence — Python core before UI, now completed through Phase 12

The active architecture decision (see `docs/adr/0003-python-core-before-polished-ui.md`) is: **build and test the Python business-rule core first, then build the polished Next.js dashboard on top of stable output contracts.** Two earlier ADRs (0001, 0002) proposed UI-first approaches and are superseded — do not follow them.

That sequencing has now been carried out through Phase 12:

- Phases 1-6 built and tested the Python/Excel core.
- Phase 7 planned UI contracts and page mappings.
- Phases 8-9.1 built the Next.js foundation, reusable components, static pages, and visual alignment fixes.
- Phase 10 added the stateless FastAPI layer and live-wired the three workflow pages.
- Phase 10.2 was a token-only visual/hierarchy polish pass (dark sidebar, compact KPI tiles, paired dashboard sections, chart-card interactivity, button hierarchy) — no backend/API/contract changes.
- Phase 11 deployed the app to a public URL (Vercel + Render), plus a later, non-phase-numbered mobile nav/shell responsiveness fix.
- Phase 12 added a narrow, best-effort Postgres persistence layer (Neon) — see `docs/adr/0007-session-scoped-workflow-result-persistence.md` — so `/dashboard` reflects each anonymous visitor's own latest saved results, per workflow, falling back to sample data independently for anything not yet run. This amends ADR 0006's statelessness for the three JSON workflow endpoints only; report endpoints remain fully stateless and unaffected.

`context/build-plan.md` currently ends at Phase 12 — see that file for full scope of every phase. An earlier "SQL Reporting + Active Sample Dashboard" Phase 11 (SQLite-based) was planned and partially implemented, then paused in favor of deploying first; that work is preserved in a git stash and archived at `docs/archive/phase-11-sql-reporting-sqlite-plan.md` (see `context/build-plan.md`'s Phase 11 entry) — it was formally superseded, not completed, by Phase 12's materially different Postgres design. No phase is currently planned beyond Phase 12. Any new work needs its own planning pass before implementation.

### Current Python and backend shape

```text
src/
  __init__.py
  excel_io.py
  contracts.py
  sample_data.py
  order_validation.py
  inventory_allocation.py
  payment_aging.py
  report_export.py
backend/
  main.py
  errors.py
  uploads.py
  db.py
  session.py
  persistence.py
  migrations/
    0001_create_workflow_results.sql
  repositories/
    workflow_results.py
  routers/
    orders.py
    inventory.py
    payments.py
    templates.py
    dashboard.py
```

Module boundaries are strict — `excel_io.py` never contains workflow-specific rules, `report_export.py` never contains business calculations, and none of `src/` contains UI or FastAPI route logic. Stack: pandas for tabular transforms, openpyxl for `.xlsx` I/O, pytest for tests, `psycopg` 3 (Phase 12) for the Postgres persistence layer — hand-written SQL, no ORM.

`sample_data/*.xlsx` are **demo fixtures, not test fixtures** — plausible fictional sample files with intentional imperfections. Exhaustive rule/edge-case coverage belongs in small pytest DataFrame fixtures instead. The committed UI mock JSON is generated from these sample Excel files via `npm run mock-data`, not from `tests/contract_fixtures.py`.

### Current frontend shape

```text
app/
  dashboard/page.tsx
  order-validation/page.tsx
  inventory-allocation/page.tsx
  payment-aging/page.tsx
  reports/page.tsx
components/
  layout/  workflow/  tables/  feedback/  ui/  dashboard/
lib/
  api-client.ts  mock-data.ts  formatters.ts  session-id.ts
types/
  index.ts  dashboard.ts
```

`components/dashboard/DashboardLiveSections.tsx` (Phase 12) is a Client Component — the only place in the app that reads the Anonymous Session ID (`lib/session-id.ts`) and fetches `GET /api/dashboard`. `app/dashboard/page.tsx` itself stays a Server Component for the static shell; a Server Component render has no access to `localStorage`, so the session-aware fetch cannot happen there.

Stack: Next.js App Router, TypeScript strict, Tailwind CSS 3.4 (do **not** upgrade to v4), hand-written token-compliant UI primitives, and page-level workflow state. Server Components remain the default, but workflow pages that define `DataTable` column render functions or manage upload/request state are Client Components.

### Current API contract

FastAPI wraps the tested Python modules — thin route handlers call business modules and never duplicate business rules:

```text
POST /api/orders/validate
POST /api/orders/validate/report

POST /api/inventory/allocate
POST /api/inventory/allocate/report

POST /api/payments/aging
POST /api/payments/aging/report

GET  /api/templates/{template_name}
GET  /api/dashboard
GET  /health
```

`GET /api/reports/{report_id}` is intentionally not implemented. The three JSON workflow endpoints and their `.../report` counterparts are stateless per `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`: no persisted Workflow Run, no `run_id`, no report artifact store, and report endpoints always re-accept source files and recompute server-side. As of Phase 12 (`docs/adr/0007-session-scoped-workflow-result-persistence.md`), the three JSON workflow endpoints *also* make a best-effort attempt to save their result — reported via `X-Persisted` (`true`/`false`/`skipped`), never failing the request — when a valid `X-Session-Id` header is supplied. This does not extend to the `.../report` endpoints, which remain entirely stateless and session-unaware. `GET /api/dashboard` returns that session's latest saved result per workflow (`null` per workflow if none/stale/unsaved), independently falling back to sample data on the frontend.

Current development shape is two independent servers: FastAPI on `127.0.0.1:8000` and Next.js on `localhost:3000`, with explicit CORS (`X-Persisted` is in `expose_headers`). The frontend fallback API base URL is pinned to `http://127.0.0.1:8000` to avoid browser-side IPv6 `localhost` failures on machines where `localhost` resolves to both `127.0.0.1` and `::1`. Persistence needs a Postgres connection: `DATABASE_URL` (app) and `TEST_DATABASE_URL` (pytest's `@pytest.mark.db` tests only) point at separate Neon branches (`dev`/`test`; `main` is Render's, a secret) — both are optional locally, since the app and the full non-`db` test suite run cleanly with neither set.

### Candidate next scope

No phase is currently planned. Phase 12 was the last-scoped item in `context/build-plan.md`; anything beyond it (e.g. real cross-session history, authenticated accounts, physical deletion of expired rows) is new scope requiring its own planning pass, not an assumed next phase.

## Output contracts

Python modules return JSON-serializable structures (snake_case keys) that map directly to TypeScript. Required output families: `ValidationSummary`, `ValidationErrorRow`, `ValidOrderRow`, `AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`, `SupplierFollowUpRow`, `PaymentAgingSummary`, `PaymentAgingRow`, `PaymentDataIssueRow`, `DraftMessageRow`, `ReportManifest`. Every UI table/KPI/chart must map to one of these or to a documented derived display value — don't invent UI surfaces the Python core can't produce.

**Field scope boundary:** a contract may only contain fields its originating spec explicitly defines — contracts are allowed to be asymmetric across output families, and cross-module consistency is not a valid reason to add a field. Example: `PaymentAgingRow` has `suggested_action` because `03_demo_payment_aging.md` §6–7 defines it; `AllocationResultRow` does not, because `02_demo_inventory_allocation.md` never specifies one. Don't add fields for symmetry — only when the corresponding spec is amended via a new ADR.

## Scope Gate — avoiding ERP creep

Only implement rules labeled **V1 or unlabeled** within an in-scope spec file (`01_demo_order_validation.md`, `02_demo_inventory_allocation.md`, `03_demo_payment_aging.md`). Anything marked **Optional, V1.5, or V2** — including Rule IA-007's optional region-matching warehouse preference — and the **entirety of `04_optional_crm_cleaner.md`** are out of scope and require a new ADR before implementation, even if the change looks trivial. This is a mechanical check, not a judgment call: grep the spec for a version label before implementing a rule that isn't in the "required" `context/build-plan.md` phase lists.

## Code standards highlights

- Prefer clear, explicit functions over clever abstractions; type hints on public Python functions.
- Business logic never prints — return structured errors/results. Convert technical exceptions (e.g. `KeyError`) into business-readable messages at module/API boundaries (see "Error Messages" in `context/ui-rules.md` for the bad/good example).
- No hidden global state; deterministic business-rule functions where practical.
- FastAPI route handlers stay thin and framework-specific; `src/` remains framework-free.
- Frontend state stays page-local unless a new planning decision introduces a broader state model.
- Full standards reference: `context/code-standards.md` (Python, pytest, future TypeScript/Next.js/API conventions all documented there).

## UI design system

- No hardcoded hex values, no raw Tailwind color classes (`bg-blue-600`, etc.) — always use semantic tokens defined in `context/ui-tokens.md` (`bg-accent`, `text-text-primary`, `bg-success-subtle`, etc.).
- Status must never rely on color alone — always include a text label. Controlled status vocabularies per workflow are listed in `context/ui-rules.md`.
- Visual direction: light theme, sidebar nav, white cards on soft gray background, blue accent, dense readable tables. Avoid dark/crypto styling, decorative gradients, ERP-style mega nav.
- Check `context/ui-registry.md` before building any component — it's the living registry of established component styles and page-composition notes.

## Skill-driven workflow

`AGENTS.md` defines a set of workflow procedures, implemented as skills under `skills/` (referenced there as `.claude/commands/` / `.agents/skills/`):

| Skill | When to run |
|---|---|
| `/architect` | Before any complex feature — think and confirm a plan before writing code |
| `/imprint` | After building any UI component — capture its styling into `ui-registry.md` |
| `/project-review` | Before a demo, or when something feels off — 3-layer report (plan alignment, system integrity, production readiness), report only, don't auto-fix |
| `/recover` | When something breaks after one failed correction attempt — diagnoses failure mode before touching code |
| `/remember save` / `/remember restore` | End/start of a session that spans multiple sessions |

Full procedure definitions are in `AGENTS.md` and mirrored in `skills/<name>/SKILL.md`.

### Non-negotiable rules from AGENTS.md

- Never use hardcoded hex values or raw Tailwind color classes.
- Update `context/progress-tracker.md` and `context/ui-registry.md` after every feature.
- After every feature, create `docs/plan/<feature-slug>/` with `plan.md`, `explanation.md`, and `ai-discussion-topics.md` (see `docs/plan/context-reset/` and `docs/plan/python-first-sequence/` for examples of this format).
- Before using any third-party library, load its skill first, then check `context/library-docs.md` for project-specific rules.
- If the same problem persists after one corrective prompt, stop and run `/recover` instead of continuing to retry.

## Reference material (guidance, not source of truth)

`ui_reference_to_figma_workflow/`, `ui_prompts_for_agents_mcp/`, and `sales_admin_automation_toolkit_ui_specs/` contain Figma/MCP-driven UI planning workflows and prompt packs. These are inputs for wireframe/component planning, not final product scope — every UI element must still map back to a real Python output contract. `sales_admin_automation_toolkit_specs/` contains the original business-rule specs (order validation, inventory allocation, payment aging, optional CRM cleaner) that the Python phases (3–5) must satisfy test coverage against.

Note: the specs' original recommended V1 stack (Streamlit) is **not** the active path — see ADR 0003.
