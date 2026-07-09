# Phase 7 — UI Contract and Wireframe Planning: Decisions

## 1. TypeScript interfaces are literal `.ts` code blocks in a planning doc

**What it is:** `context/ui-contract-plan.md` contains real TypeScript `type` syntax — full field lists, string-literal unions, optional markers — copy-pasteable into `types/index.ts` once Phase 8 starts. It is not a real `.ts` file anywhere in the repo, and not a prose mapping table.

**How it works:** Every one of the 13 `src/contracts.py` TypedDicts and the 3 locally-defined result envelopes (`OrderValidationResult`, `InventoryAllocationResult`, `PaymentAgingResult`) gets a matching `type`. Fields keep their Python snake_case names verbatim (`order_id`, not `orderId`) because `CLAUDE.md` already commits to snake_case JSON at the API boundary — inventing a camelCase adapter now would be deciding something not yet asked for.

```ts
export type ValidOrderRow = {
  order_id: string;
  order_date: string; // ISO date
  customer_name: string;
  customer_region: string;
  sku: string;
  product_name?: string;
  quantity: number;
  requested_delivery_date: string;
  priority: "High" | "Normal" | "Low";
  payment_terms: string;
  sales_owner?: string;
};
```

**Why this over the alternatives:**
- *A field-mapping table only* (Python field → TS field → TS type, no real syntax) was considered but rejected — it's lighter to write but not directly usable in Phase 8; someone still has to transcribe it into real TypeScript later, which is exactly the kind of drift this phase exists to prevent (see decision 6 below for what that drift looks like in practice).
- *A draft `.ts` file outside `app/`/`lib`/`types`* was rejected because Phase 7 is explicitly docs-only per `build-plan.md` ("This phase must not create production frontend code") — a `.ts` file, even a clearly-marked draft one, blurs that line in a way a markdown code block does not.

**Cost of the alternative:** the mapping-table approach defers the highest-error-rate step (hand-translating a table into syntax) to whoever starts Phase 8, instead of doing it once, now, while the contract definitions are freshly re-read from source.

## 2. Status Badges section rewritten for all 4 workflow groups, not just the 2 flagged first

**What it is:** `context/ui-rules.md`'s Status Badges section previously listed vocabularies for Order Validation, Inventory Allocation, Payment Aging, and Reports. Research found Order Validation and Reports badges didn't correspond to any real Python field at all. The first draft of this plan corrected only those two and left Inventory Allocation and Payment Aging as "already correct." The user rejected that: those two groups were *also* wrong, just less obviously — they mixed real controlled-vocabulary fields with unexplained derived labels in the same flat list, with no way to tell which was which.

**How it works:** every group now gets the same explicit split:

```
Order Validation
  direct   (ValidationErrorRow.severity): Error, Warning
  derived  (list membership):             Valid, Has Errors, Has Warnings

Inventory Allocation
  direct        (AllocationResultRow.status):        Fully Allocated, Partially Allocated, Backordered
  direct/derived (RemainingInventoryRow.reorder_alert "Yes"/"No"): "Below Reorder Point" is a display
                  label for reorder_alert === "Yes", not a separate vocabulary
  derived       (list membership in supplier_follow_ups): Supplier Follow-up

Payment Aging
  direct (PaymentAgingRow.aging_bucket):        5 buckets
  direct (PaymentAgingRow.follow_up_priority):  High, Medium, Low, Watch, None
  (old ad hoc labels Overdue/Due Soon/High Priority/Paid removed — undefined derivation)

Reports
  derived only, 4-state client lifecycle (see decision 3)
```

**Why this over "fix what's visibly broken":** a badge list that's *partially* accurate is more dangerous than one that's *obviously* wrong — a wrong-but-obvious badge (e.g. "Needs Review" mapping to nothing) gets questioned; a mostly-right list with one unexplained label ("Paid" silently invented) gets copied into Phase 8 code without anyone re-checking it, because the other four labels in the same list did check out.

**Cost of the alternative:** shipping `ui-rules.md` with an internally inconsistent badge list — some entries backed by a real field, others invented — defeats the entire point of Phase 7, which is to make every UI surface traceable to a contract.

## 3. `/dashboard` scoped as a read-only aggregate, no persisted cross-workflow state

**What it is:** the dashboard route pulls KPI tiles from all three workflow `Summary` types plus the three `ReportManifest`s, when they exist in the current session. It does not introduce a combined backend contract, a stored "session" concept, or any field the Python core doesn't already produce.

**How it works:** each KPI section (Order Validation, Inventory Allocation, Payment Aging) renders independently — if that workflow hasn't run yet this session, that section shows its own empty state rather than blocking the whole page.

**Why this over inventing a combined contract:** the only spec-level source for a dashboard/overview page (`05_integration_and_app_flow.md` §5) is Streamlit-era and pre-dates the current output contracts. Building a "global health score" or "unified operations queue" on top of it would be inventing a business outcome the Python core was never asked to produce — a direct Field Scope Boundary violation. Composing the page from three already-existing summaries, independently empty-stated, needs zero new backend work.

**Cost of the alternative (a minimal 3-card nav page, no KPIs):** was on the table and would have been safer, but throws away real, already-computed data (`ValidationSummary` etc. exist and are cheap to render) for no reason other than avoiding the (already-resolved) ambiguity about what "aggregate" should mean here.

## 4. Client-side derived aggregates are allowed, but must be explicitly labeled

**What it is:** some chart/KPI ideas from the guidance docs (`library-docs.md`'s Recharts list, the spec's "90+ Days Amount" KPI) require grouping or summing existing row fields — no `Summary` contract field produces the total directly.

**How it works:** each one gets a table entry naming its exact source rows, source fields, and grouping rule:

```
"90+ Days Amount" KPI
  Source: PaymentAgingResult.aging_rows
  Rule:   sum outstanding_amount where aging_bucket === "90+ Days"
```

**Why this over restricting charts to Summary-only fields:** the spec (`03_demo_payment_aging.md` §9) explicitly lists "90+ Days Amount" as a required KPI card, and it's a straightforward aggregation of data that already exists — refusing to plan it would mean either dropping a spec-required KPI or silently inventing a new Python summary field neither spec nor ADR asked for. Labeling the derivation is the boundary that keeps this from becoming scope creep: the rule is spelled out, reviewable, and traces to real fields — it just isn't persisted or computed in Python.

**Cost of the alternative:** dropping every row-level aggregation would mean roughly a third of the spec's own KPI/chart requirements (backorder-by-SKU, 90+ days amount, overdue-by-customer) become unplannable, for a boundary violation that labeling already solves.

## 5. `CONTEXT.md` is not edited this phase

**What it is:** `Status Badge` and `Derived Display Value` — the two vocabulary terms this session needed to talk precisely about the badge-correction work — are defined in `context/ui-contract-plan.md`'s glossary intro, not in the root business-domain glossary.

**Why this over adding them to `CONTEXT.md`:** `CONTEXT.md` is described in `CLAUDE.md` as "the project glossary — business terms... plus process terms resolved during planning." The first draft of this plan added both terms there. The user corrected this: these are UI-planning/process vocabulary, not business domain terms (they don't describe an Order, SKU, Aging Bucket, or any workflow concept — they describe how the *documentation itself* talks about UI). Business terms belong in the shared glossary everyone reads; UI-process terms belong scoped to the UI-planning doc that actually needs them.

**Cost of the alternative:** growing `CONTEXT.md` with every planning session's local vocabulary would eventually make it a dumping ground instead of a curated business glossary — the same failure mode as the badge list in decision 2, just at the glossary level instead of the UI-rules level.

## 6. `ReportManifest` fixture/exporter mismatch: discovered and flagged, not fixed

**What it is:** `tests/contract_fixtures.py`'s `REPORT_MANIFEST_FIXTURES` uses `report_id` values like `"rpt-order-validation-20260709-001"` (hyphenated `report_type`, date-only, fake sequence suffix). The real exporter (`src/report_export.py:188`) produces `f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"` — e.g. `"rpt-order_validation-20260709091500"` (underscored, full timestamp, no sequence). This was caught while grounding `ReportManifest` examples in the fixture file, per the original plan — and would have silently propagated a wrong format into Phase 8 mock data if not caught.

**How it works:** `ui-contract-plan.md` explicitly documents both formats and states which one is authoritative (the real exporter), and sources `ReportManifest` examples from `report_export.py`/`tests/test_report_export.py` instead of the stale fixture. The mismatch itself is called out as a discovered issue, flagged as a follow-up.

**Why not fix `tests/contract_fixtures.py` in this phase:** it's a test-data file, not a planning doc, and Phase 7's mandate (`build-plan.md`) is explicitly "must not create production frontend code" and, by the same logic the user reinforced throughout this session (Field Scope Boundary, Scope Gate), should not silently touch `src/`/`tests/` either — that's a Phase 2/6 concern for whoever picks it up next, not a Phase 7 planning-doc change.

**Cost of fixing it inline anyway:** would have meant editing test fixtures as a side effect of a UI-planning session, without dedicated review of whether `-001`-style sequence suffixes were ever intentional, whether other fixtures reference this format, or whether the fix should also cover `generated_at` precision — a scope expansion the session wasn't asked to take on.

## 7. Git preflight: push the pending Phase 6 fix before branching Phase 7

**What it is:** before any Phase 7 file changes, the session found `phase/6-excel-report-export` was 1 commit ahead of `origin` (`d21d787`, a post-review fix). The user chose to push that commit first, then branch `phase/7-ui-contract-wireframe-planning` off the now-synced tip, rather than branching locally and pushing later.

**Why this over branching immediately:** keeps PR #5 on GitHub reflecting the same code the new branch forks from, avoiding a silent divergence between "what's on GitHub" and "what Phase 7 actually branched from." Since Phase 7 doesn't depend on PR #5 merging (only on branching from the right commit), either choice was safe — this was a preference for tidiness over necessity.
