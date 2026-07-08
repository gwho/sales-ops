# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Phase 1 (Python Project Foundation) and Phase 2 (Sample Data and Contract Fixtures) are complete: `pyproject.toml`/`uv`, `src/excel_io.py`, `src/contracts.py` (13 output-contract `TypedDict` families), `src/sample_data.py`, committed `sample_data/*.xlsx`, and `tests/` (32 passing). No business-rule logic exists yet — `order_validation.py`, `inventory_allocation.py`, `payment_aging.py`, and `report_export.py` are still unwritten. Next up is Phase 3 (Order Validation Core); Phase 7 (UI planning, docs-only) may also start in parallel now that Phase 2's contract fixtures exist. Check `context/progress-tracker.md` for the authoritative current phase status before starting work.

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

## Build sequence — Python core before UI

The active architecture decision (see `docs/adr/0003-python-core-before-polished-ui.md`) is: **build and test the Python business-rule core first, then build the polished Next.js dashboard on top of stable output contracts.** Two earlier ADRs (0001, 0002) proposed UI-first approaches and are superseded — do not follow them.

The reason is sequencing risk, not shape ambiguity: the functional specs in `sales_admin_automation_toolkit_specs/` already define input columns, rules, and output columns in enough detail that output shapes aren't the risk. The risk is spending the first implementation milestone on UI polish before the substantive automation — the actual portfolio payload — exists.

`context/build-plan.md` defines the full phase sequence (Phase 0 planning reset is done; next is Phase 1: Python project foundation). Check `context/progress-tracker.md` for current phase status before starting work, and update it after completing any phase item.

### Phase 1 scope (current phase)

Phase 1 is more than empty scaffolding — it includes the cross-cutting infrastructure every later phase depends on, so Phases 3–5 don't each invent slightly different field names before a UI consumer exists to catch the drift:

- Python project config, `src/`, `tests/`, `sample_data/` folders, pytest config
- `src/excel_io.py` — load helper, required-column validation, consistent missing-column error shape
- `src/contracts.py` — `TypedDict` definitions for every output family (dict-shaped, not dataclasses, since the eventual FastAPI/Next.js boundary is JSON)

Phase 1 explicitly excludes all business rules (validation/allocation/aging), sample workbook *generation* (stubs only), report export logic, and any FastAPI/UI work — those come in Phases 2–6.

### Python scaffold — built vs. still planned

```
src/
  __init__.py             # done (Phase 1)
  excel_io.py             # done (Phase 1) — Excel loading, required-column validation, normalization helpers
  contracts.py            # done (Phase 1) — TypedDict output contracts
  sample_data.py          # done (Phase 2) — fictional sample workbook generation
  order_validation.py     # planned (Phase 3) — order validation rules and output
  inventory_allocation.py # planned (Phase 4) — allocation ordering, stock depletion, backorder/supplier follow-up
  payment_aging.py        # planned (Phase 5) — outstanding amount, aging buckets, follow-up priority, draft reminders
  report_export.py        # planned (Phase 6) — Excel workbook generation from already-computed outputs
tests/
  test_excel_io.py         # done (Phase 1)
  test_contracts.py        # done (Phase 1, extended Phase 2)
  test_sample_data.py      # done (Phase 2)
  test_order_validation.py    # planned (Phase 3)
  test_inventory_allocation.py # planned (Phase 4)
  test_payment_aging.py       # planned (Phase 5)
  test_report_export.py       # planned (Phase 6)
sample_data/
  sample_orders.xlsx          # done (Phase 2)
  sample_product_master.xlsx  # done (Phase 2)
  sample_inventory.xlsx       # done (Phase 2)
  sample_invoices.xlsx        # done (Phase 2)
```

Module boundaries are strict — `excel_io.py` never contains workflow-specific rules, `report_export.py` never contains business calculations, and none of `src/` contains UI or FastAPI route logic. Stack: pandas for tabular transforms, openpyxl for `.xlsx` I/O, pytest for tests.

`sample_data/*.xlsx` are **demo fixtures, not test fixtures** — mostly clean with a small number of realistic imperfections (e.g. one duplicate order ID, one inactive SKU, one SKU near reorder point, one high-priority overdue invoice), so they read as a believable sales-ops day rather than a disguised test matrix. Exhaustive rule/edge-case coverage belongs in small pytest DataFrame fixtures instead — that's a distinct concept from a "Contract Fixture" (a realistic example value for an output contract, built in Phase 2 to prove the shape holds real demo data). See `CONTEXT.md` for both terms.

Phase 6 (Excel report export) is a standalone fallback demo milestone: tested Python logic plus professional `.xlsx` reports are interview-ready even if Next.js never gets built.

### UI has two separate gates — planning vs. implementation

- **Planning gate (Phase 7 — UI contract/wireframe planning):** can start as soon as Phase 2 (contract fixtures) is done, and may run in parallel with Phases 3–6. It's docs/wireframes/TypeScript-interface-planning only — no production frontend code.
- **Implementation gate (Phase 8 — actual Next.js code):** hard-gated. Cannot start until every test case listed in each spec's "Test cases" table passes (`01_demo_order_validation.md` §12, `02_demo_inventory_allocation.md` §11, `03_demo_payment_aging.md` §12) plus Phase 6's Excel report structure tests.

### Planned Next.js scaffold (build only after the Phase 8 gate is satisfied)

```
app/
  dashboard/page.tsx
  order-validation/page.tsx
  inventory-allocation/page.tsx
  payment-aging/page.tsx
  reports/page.tsx
components/
  layout/  workflow/  tables/  feedback/  ui/
lib/
  api-client.ts  mock-data.ts  formatters.ts
types/
  index.ts
```

Stack: Next.js App Router, TypeScript strict, Tailwind CSS 3.4 (do **not** upgrade to v4), shadcn/ui, TanStack Table, Recharts. Server Components by default; `"use client"` only for state/effects/browser APIs/event listeners. Route files stay thin — pages compose sections, they don't implement large reusable components.

Future API layer (FastAPI) wraps the tested Python modules — thin route handlers that call business modules and never duplicate business rules:

```
POST /api/orders/validate
POST /api/inventory/allocate
POST /api/payments/aging
GET  /api/reports/{report_id}
```

## Output contracts

Python modules must return JSON-serializable structures (snake_case keys) that later map to TypeScript. Required output families: `ValidationSummary`, `ValidationErrorRow`, `ValidOrderRow`, `AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`, `SupplierFollowUpRow`, `PaymentAgingSummary`, `PaymentAgingRow`, `PaymentDataIssueRow`, `DraftMessageRow`, `ReportManifest`. Every future UI table/KPI/chart must map to one of these — don't invent UI surfaces the Python core can't produce.

**Field scope boundary:** a contract may only contain fields its originating spec explicitly defines — contracts are allowed to be asymmetric across output families, and cross-module consistency is not a valid reason to add a field. Example: `PaymentAgingRow` has `suggested_action` because `03_demo_payment_aging.md` §6–7 defines it; `AllocationResultRow` does not, because `02_demo_inventory_allocation.md` never specifies one. Don't add fields for symmetry — only when the corresponding spec is amended via a new ADR.

## Scope Gate — avoiding ERP creep

Only implement rules labeled **V1 or unlabeled** within an in-scope spec file (`01_demo_order_validation.md`, `02_demo_inventory_allocation.md`, `03_demo_payment_aging.md`). Anything marked **Optional, V1.5, or V2** — including Rule IA-007's optional region-matching warehouse preference — and the **entirety of `04_optional_crm_cleaner.md`** are out of scope and require a new ADR before implementation, even if the change looks trivial. This is a mechanical check, not a judgment call: grep the spec for a version label before implementing a rule that isn't in the "required" `context/build-plan.md` phase lists.

## Code standards highlights

- Prefer clear, explicit functions over clever abstractions; type hints on public Python functions.
- Business logic never prints — return structured errors/results. Convert technical exceptions (e.g. `KeyError`) into business-readable messages at module/API boundaries (see "Error Messages" in `context/ui-rules.md` for the bad/good example).
- No hidden global state; deterministic business-rule functions where practical.
- Full standards reference: `context/code-standards.md` (Python, pytest, future TypeScript/Next.js/API conventions all documented there).

## UI design system (for future Next.js work)

- No hardcoded hex values, no raw Tailwind color classes (`bg-blue-600`, etc.) — always use semantic tokens defined in `context/ui-tokens.md` (`bg-accent`, `text-text-primary`, `bg-success-subtle`, etc.).
- Status must never rely on color alone — always include a text label. Controlled status vocabularies per workflow are listed in `context/ui-rules.md`.
- Visual direction: light theme, sidebar nav, white cards on soft gray background, blue accent, dense readable tables. Avoid dark/crypto styling, decorative gradients, ERP-style mega nav.
- Check `context/ui-registry.md` before building any component — it's the living registry of already-established component styles (currently empty; no components built yet).

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
