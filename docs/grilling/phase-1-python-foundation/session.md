# Grilling Session: Phase 1 Python Foundation Plan

## Scope

This session stress-tested the plan for Phase 1 of the Sales Admin Automation Toolkit before any implementation started. The project was at "Phase 0 complete, Phase 1 not started" — `context/build-plan.md` and `context/progress-tracker.md` already described a Python-first sequence (per ADR 0003), but the plan had not been interrogated for gaps.

The session worked through six focus areas, one question at a time, each with a recommendation and reason offered before the user confirmed, amended, or redirected:

1. Whether the Python-first sequence is actually correct
2. Exact Phase 1 scope
3. Sample Excel file design
4. Output contracts for validation, allocation, payment aging, and reports
5. What must be tested before UI work starts
6. What to exclude to avoid ERP overbuilding

The `domain-modeling` skill was used inline partway through (after focus area 4) to formalize terminology that had been used loosely — "output contract," "contract fixture," "field scope boundary" — by adding definitions to `CONTEXT.md`. It surfaced again naturally for "Scope Gate," "V1," and "V2" during focus area 6.

## Resolved decisions, in order

### 1. Python-first sequencing — kept, but rationale corrected

Kept the Python-core-before-UI sequence, but replaced the reason. The original ADR 0003 justified it as "avoid building UI around invented data shapes." That's not actually the risk — the specs in `sales_admin_automation_toolkit_specs/` already define input columns, rules, and output columns in detail. The real risk is **sequencing**: building polished UI first could consume the available time before the substantive automation (the actual portfolio payload) exists.

### 2. Phase 1 scope — expanded beyond empty scaffolding

Phase 1 now includes, in addition to project/package scaffolding:
- `src/excel_io.py` — load helper, required-column validation, consistent missing-column error shape
- `src/contracts.py` — `TypedDict` definitions for every output family (dict-shaped, not dataclasses)

Reason: both are cross-cutting infrastructure shared by every business module. Defining them once in Phase 1 stops Phases 3–5 from each inventing slightly different field names or error shapes before a UI consumer exists to catch the drift.

Phase 1 explicitly excludes: order validation/allocation/payment-aging rules, sample workbook generation beyond stubs, report export logic, FastAPI, and UI work.

### 3. Sample Excel files vs. pytest fixtures — split by job

- **pytest DataFrame fixtures** own exhaustive rule/edge-case coverage — one rule per tiny fixture, per `context/code-standards.md`.
- **`sample_data/*.xlsx`** own demo believability — mostly clean, with a small number of realistic imperfections (one duplicate order ID, one inactive SKU, limited stock on 1–2 SKUs, one SKU near reorder point, one high-priority overdue invoice, at most one data-issue row).

Reason: an exhaustive "dirty workbook" is hard to maintain (one row often triggers multiple rules) and reads as a disguised test matrix rather than a believable sales-ops snapshot, which is the opposite of what an interviewer needs to trust the demo.

### 4. Output contract field scope — asymmetric, spec-bounded

Contracts only contain fields their originating spec explicitly defines. Cross-module symmetry is not a valid reason to add a field. Concrete example resolved: `PaymentAgingRow.suggested_action` stays (explicitly defined in `03_demo_payment_aging.md` §6–7); `AllocationResultRow` does **not** get a matching `suggested_action` field (not in `02_demo_inventory_allocation.md` — `status` is enough, and the UI can derive display copy from it).

This produced a "Field Scope Boundary" rule, now recorded in `context/architecture.md`, and matching glossary entries in `CONTEXT.md`.

### 5. UI readiness — two separate gates, not one

- **Planning gate (Phase 7):** can start right after Phase 2 (contract fixtures exist), and may run in parallel with Phases 3–6. Docs/wireframes/TypeScript-interface planning only — no production frontend code.
- **Implementation gate (Phase 8):** hard-gated on every spec-listed test case passing (`01_demo_order_validation.md` §12, `02_demo_inventory_allocation.md` §11, `03_demo_payment_aging.md` §12) plus Phase 6's Excel report structure tests.

Side effect surfaced during this discussion: Phase 6 (Excel report export) was named as a standalone fallback demo milestone — tested Python logic plus professional `.xlsx` reports are interview-ready on their own, even if Next.js never gets built.

### 6. Scope Gate — mechanical rule against ERP creep

The existing "Non-Goals for V1" list in `context/architecture.md` named categories to avoid (auth, DB persistence, AI forecasting, etc.) but didn't cover **in-spec-but-out-of-scope** creep: Rule IA-007 in `02_demo_inventory_allocation.md` includes an optional V2 warehouse-region-matching rule sitting right next to the V1 rule in the same file, and `04_optional_crm_cleaner.md` is a fully-specified optional module sitting in the specs folder indistinguishable at a glance from the three in-scope demos.

New rule: only V1 or unlabeled rules from in-scope specs may be implemented. Anything marked Optional/V1.5/V2, and all of CRM Cleaner, requires a new ADR before implementation — regardless of how trivial the addition looks. The user explicitly rejected a "trivial V2 rules are fine" carve-out, since that's the exact creep path the gate exists to close.

## Files changed this session

- `docs/adr/0003-python-core-before-polished-ui.md` — amended rationale
- `context/build-plan.md` — Phase 1 scope, Phase 2 reframed as "Sample Data and Contract Fixtures," Phase 6 fallback-milestone note, Phase 7/8 gate split
- `context/progress-tracker.md` — matching checklist updates for Phases 1, 2, 7, 8; gate note added to Current Status
- `context/code-standards.md` — pytest-vs-sample-data fixture split; new "Scope Control" section (mechanical Scope Gate check)
- `context/architecture.md` — "Field scope boundary" subsection under Python Output Contracts; UI Design Input Workflow updated for the two-gate split
- `CONTEXT.md` — new glossary entries: Output Contract, Contract Fixture, Field Scope Boundary, V1, V2, Scope Gate
- `docs/plan/python-first-sequence/plan.md` and `ai-discussion-topics.md` — updated by the user alongside the ADR change
- `CLAUDE.md` — synced at the end of the session to reflect all six resolved decisions (Phase 1 scope, demo-vs-test fixture split, two-gate UI split, field scope boundary, Scope Gate)

## Terminology added to CONTEXT.md

| Term | Definition |
|---|---|
| Output Contract | A stable, spec-derived field shape for a workflow output, defined once in the shared Python contract layer, populated by Python modules, reused later by API/frontend. |
| Contract Fixture | A realistic example value for an Output Contract, proving the shape holds believable demo data — distinct from small pytest fixtures used for isolated rule coverage. |
| Field Scope Boundary | An Output Contract may contain only fields explicitly defined by its originating spec; cross-module symmetry alone is not a reason to add a field. |
| V1 | The active portfolio build scope: order validation, inventory allocation, payment aging, and report export using fictional Excel data. |
| V2 | Postponed expansion work; explicitly out of the active V1 build unless a new ADR reopens scope. |
| Scope Gate | Only V1 or unlabeled items from in-scope specs may be implemented; Optional/V1.5/V2/CRM Cleaner work requires a new ADR. |
