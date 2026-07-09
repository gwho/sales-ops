# AI Discussion Topics — Feature phase-7-ui-contract-wireframe-planning: UI Contract and Wireframe Planning

## Documentation drift and how it was caught

1. The `ui_specs` guidance folder used `requested_quantity` where the real contract field is `requested_qty`. Walk through exactly how this phase's research caught that — what was compared against what, and why would spot-checking a few fields by eye likely have missed it?
2. The automated field-name diff script found 0 mismatches across 67 TypeScript fields. What kinds of errors would this script *not* catch (e.g. a field with the right name but wrong type, or a field that exists but is documented with the wrong optionality)?
3. If a future Phase (say, a Phase 11 that adds a new contract field) forgets to update `context/ui-contract-plan.md`, how would that drift most likely be discovered — and is there a way to make that discovery automatic rather than dependent on someone noticing?

## The Status Badges rewrite

4. Explain, in your own words, why "the labels are factually correct" was not sufficient justification for calling the Inventory Allocation and Payment Aging badge lists "already correct."
5. `Below Reorder Point` is described as "direct/derived" rather than purely one or the other. What distinguishes a direct/derived hybrid from a purely derived label like `Supplier Follow-up`?
6. If someone wanted to reintroduce a `Paid` badge for Payment Aging (removed in this rewrite for having no defined derivation), what exact rule would you write, and where would it need to be documented for it to meet this project's new standard?

## The Reports lifecycle inconsistency

7. Two documents (`ui-contract-plan.md` and `ui-rules.md`) were both edited in the same session and ended up with different Reports lifecycle models before the inconsistency was caught. What review step actually caught this, and why wouldn't a per-file review (checking each file in isolation) have found it?
8. Why was `error` deliberately not added as a fifth persisted lifecycle state, even though report generation can genuinely fail? What's the tradeoff of reverting to `Not Generated` instead?
9. If Phase 8 needs to show a user "your last 3 report generation attempts," would that require a new Python contract field, or can it stay client-side? Justify your answer using the Field Scope Boundary reasoning from this phase.

## The ReportManifest fixture bug

10. The fixture/exporter `report_id` mismatch was found, documented, but not fixed in this phase. What's the argument for fixing it immediately instead of flagging it as a follow-up? What's the argument against?
11. If you were the next person to fix `tests/contract_fixtures.py`'s `REPORT_MANIFEST_FIXTURES`, what would you need to check beyond just updating the `report_id` string format (hint: think about what else in the fixture might be stale relative to `report_export.py`)?
12. This bug was only found because the plan required grounding examples in real fixture data rather than inventing plausible-looking examples. What's a general argument for why "ground every example in real data" is worth the extra friction it creates?

## Derived aggregates and scope discipline

13. Walk through the "90+ Days Amount" KPI: why is `sum(outstanding_amount) where aging_bucket === "90+ Days"` allowed as a derived aggregate, while a hypothetical "customers at risk of churn" metric computed from the same rows would not be?
14. The plan documents each derived aggregate with an explicit source-rows/source-fields/grouping-rule triple. What would be lost if a future contributor added a new chart to `ui-contract-plan.md` without following that same documentation pattern?
15. `CONTEXT.md` was deliberately not edited this phase, with `Status Badge` and `Derived Display Value` defined in `ui-contract-plan.md` instead. Design a test you could apply to any future term to decide which glossary it belongs in.
