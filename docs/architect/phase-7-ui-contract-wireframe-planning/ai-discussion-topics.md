# Phase 7 — UI Contract and Wireframe Planning: Discussion Topics

## Field Scope Boundary at the UI layer

1. Why does a status badge count as a "UI surface" subject to the Field Scope Boundary, the same as a table column or KPI card? What would go wrong if badges were treated as exempt (just presentation, not data)?
2. The session distinguished "direct" badges (verbatim from a contract field) from "derived" badges (computed from list membership or a display transform). Is there a third category this taxonomy misses — and if so, what would it be?
3. `RemainingInventoryRow.reorder_alert` is `"Yes"`/`"No"`, but its badge renders as `"Below Reorder Point"` only when `"Yes"`. Why is this "direct/derived" rather than purely direct or purely derived? What's the general rule for when a field needs a display transform versus rendering verbatim?
4. Why was it wrong to say Inventory Allocation and Payment Aging badges were "already correct" when their direct-vocabulary labels were, in fact, accurate? What made the *list* wrong even though most *entries* were right?

## Derived display-only values

5. The session's test for an allowed derived aggregate was "aggregation, not interpretation." Where exactly is the line? Is `count(rows) group by status` aggregation? Is `average(days_overdue)` aggregation? Is `average(days_overdue) where follow_up_priority = "High"` still aggregation, or does filtering by a derived-looking condition cross into interpretation?
6. "90+ Days Amount" is explicitly required by the spec (`03_demo_payment_aging.md` §9) but has no direct contract field. If a *different* chart idea appeared in a guidance folder but wasn't spec-required, should the same derived-aggregate allowance apply, or does spec-required status change the analysis?
7. Suppose a derived aggregate needs a business threshold to be useful (e.g. "SKUs at critical risk" = backorder_qty > some cutoff). Walk through why this fails the aggregation-vs-interpretation test, and what the correct process would be to add it for real (ADR? spec amendment? something else?).

## Report lifecycle and UI-only state

8. Why can't `ReportManifest | null` alone represent the Reports page's 4-state lifecycle (`Needs Input` → `Not Generated` → `Processing` → `Ready`)? What's the minimum extra state Phase 8 will need to track client-side?
9. If Phase 8 later wants to persist "which reports were generated" across a page refresh (not just within one session), what would that require — and would it cross the Field Scope Boundary?
10. The lifecycle model reverts an export failure back to `Not Generated` rather than adding an `Error` state. What's the tradeoff of collapsing failure into an existing state versus giving it its own?

## Documentation placement and audience

11. `Status Badge` and `Derived Display Value` were defined in `context/ui-contract-plan.md` instead of `CONTEXT.md`. What test would you apply to decide whether a new term belongs in the shared business glossary versus a narrower planning doc?
12. If a term starts as UI-planning vocabulary but later gets referenced by a business spec (e.g. if "Derived Display Value" started appearing in a future ADR about a business rule), should it migrate to `CONTEXT.md`? What would trigger that migration?
13. The `tests/contract_fixtures.py` / `report_export.py` `report_id` mismatch was flagged but not fixed, because fixing it would mean editing test data during a docs-only phase. Was that the right call? What would change your answer?

## Scope discipline and the git preflight

14. The plan's guardrail says "if a term or boundary turns out to be ambiguous... stop and run grill-with-docs/domain-modeling." What's the practical difference between resolving ambiguity via `AskUserQuestion` (as this session mostly did) versus escalating to a dedicated domain-modeling session? When does each apply?
15. Why did branching Phase 7 off the *pushed* tip of `phase/6-excel-report-export` matter, given Phase 7 doesn't depend on PR #5 merging? What failure mode does syncing-before-branching actually prevent?
16. The Figma question was resolved by adding an explicit "deferred" guardrail rather than either blocking on it or silently proceeding. What made silent proceeding the wrong choice here, given the underlying reasoning (no connector available) was already sound?

## Route and dashboard scope

17. `/dashboard` was scoped as "read-only aggregate, no persisted cross-workflow state." What's a concrete feature request that would sound reasonable but actually require crossing that line (e.g. "remember which workflow I looked at last")?
18. The dashboard's per-workflow KPI sections show independent empty states. What would change if the business wanted a single unified empty state instead ("run at least one workflow to see anything")? Which is more consistent with how the individual workflow pages already behave?
19. Compare the `/dashboard` decision to the `05_integration_and_app_flow.md` §5 "Overview page" it was loosely based on. What survived from that Streamlit-era suggestion, and what was deliberately left out?

## Process and research method

20. This session opened with 3 parallel Explore agents before asking the user anything. What made that the right call here, versus a session that should open with direct questions?
21. The user's rejection of the first `ExitPlanMode` attempt included 5 specific, itemized corrections rather than a general "this needs work." How did having itemized corrections change how efficiently the plan could be fixed, compared to a vaguer rejection?
22. Contrast this session's TypeScript-interfaces-as-markdown-code-blocks decision with the alternative of writing a real (but unused) `.ts` file. Both are "not production code" — why does one still feel meaningfully more docs-only than the other?
