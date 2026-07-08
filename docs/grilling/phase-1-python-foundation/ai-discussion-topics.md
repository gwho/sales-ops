# Discussion Topics: Phase 1 Python Foundation Grilling Session

Fifteen questions across six groups, matching the session's focus areas. Each probes a "why," an edge, or a "what if this assumption breaks."

## Group 1 — Sequencing rationale

1. The session replaced "avoid invented data shapes" with "avoid time spent on UI before the payload exists" as the reason for Python-first. Under what circumstances would the *original* shape-risk argument actually be the correct one to cite — i.e., when is shape ambiguity the real threat instead of sequencing?
2. If a future spec revision changed the output columns for one workflow mid-Phase-4, would that be evidence the original ADR reasoning was right after all, or does the corrected "sequencing risk" reasoning survive that scenario unchanged? Why?
3. The corrected rationale leans on "the audience wants tested logic more than polish." What would have to be true about the audience for a UI-first sequence to actually be the stronger portfolio choice?

## Group 2 — Phase 1 scope

4. `excel_io.py` and `contracts.py` were pulled into Phase 1 because they're shared across modules. What's the test for deciding whether a *new* piece of code belongs in Phase 1 versus inside the specific business module that first needs it?
5. Suppose Phase 3 (order validation) discovers it needs a helper that Phase 1 didn't anticipate, and that helper turns out to also be needed by Phase 4. Does it retroactively move to `excel_io.py`, or stay local until a third consumer appears? What's the tradeoff either way?
6. `contracts.py` was deliberately built as `TypedDict`, not `dataclass`, because "the eventual FastAPI/Next.js boundary is JSON." What would change about this reasoning if the project later added a persistence layer that needed to store these objects, not just serialize them over HTTP?

## Group 3 — Sample data vs. test fixtures

7. The session argued that a "30-row dirty workbook" is hard to maintain because one row often triggers multiple rules. Construct a concrete example: design one order row that would simultaneously trigger two of the seven validation rules in `01_demo_order_validation.md`, and explain why that's a problem for a test fixture but not necessarily for a demo fixture.
8. `sample_data/*.xlsx` is meant to look like "a believable sales-ops day." What's the risk if it's *too* clean — no imperfections at all? Why does the plan insist on a few, rather than zero or many?
9. If someone later wanted a script that regenerates `sample_data/*.xlsx` deterministically (per `context/library-docs.md`'s "keep sample data generation deterministic" rule), would the imperfections need to be hardcoded, or could they be randomly seeded? What breaks if they're random?

## Group 4 — Output contracts and field scope

10. The Field Scope Boundary rule says contracts may only contain fields their spec explicitly defines. Suppose the UI planning phase (Phase 7) discovers it genuinely needs a field no spec defines — what's the correct next step, and why does it route through an ADR rather than just adding the field?
11. `PaymentAgingRow.suggested_action` is populated by a deterministic lookup from `follow_up_priority`. Is that logic allowed to live in `payment_aging.py`, or does it belong somewhere else per the module boundaries in `context/code-standards.md`? What's the argument either way?
12. The session treated "Field Scope Boundary" and "Scope Gate" as the same principle at different granularities. Is there a case where they'd actually give different answers — i.e., a change that passes the Scope Gate (rule-level) but should still fail the Field Scope Boundary (field-level), or vice versa?

## Group 5 — UI gates

13. Phase 7 (planning) is allowed to run in parallel with Phases 3–6 because it only needs shapes, not logic. What's a concrete planning decision from `context/build-plan.md`'s Phase 7 list (TypeScript interfaces, route structure, KPI mapping, etc.) that actually *does* depend on the business logic being correct, not just the shape being defined — and would therefore be premature to lock in during Phase 7?
14. The Phase 8 gate requires every spec-listed test case to pass, plus Phase 6's Excel structure tests. Is there a rule in the specs' test-case tables that's *impossible* to fully verify with a deterministic pytest assertion (e.g., something date-relative like `days_overdue`)? How should the gate handle that case?

## Group 6 — Scope Gate

15. Rule IA-007's optional region-matching variant and the entire CRM Cleaner module were both named as concrete out-of-scope items. Read through `02_demo_inventory_allocation.md` and `03_demo_payment_aging.md` again — is there another "Optional" or unflagged-but-clearly-extra rule the session didn't catch that the Scope Gate should also name explicitly?
