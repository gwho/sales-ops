# Phase 7 — UI Contract and Wireframe Planning: Discussion

## Why this session started with research, not questions

Most `/architect` sessions open by asking the developer what they want. This one opened with three parallel Explore agents instead, because the actual shape of Phase 7's output wasn't a design choice — it was already fixed by `build-plan.md` (the exact 7 bullet points: TS interfaces, routes, table columns, KPI cards, status badges, report cards, empty/loading/error states) and by `src/contracts.py` (13 TypedDicts that already exist and can't be renamed or reshaped without an ADR). The open question wasn't "what should Phase 7 produce" — it was "where does the already-written planning material (three guidance folders, `ui-rules.md`, the specs) disagree with the ground truth that didn't exist when those docs were written."

That's a research question, not a design question, and it's why the session read `context/ui-rules.md`, `src/contracts.py`, and the three guidance folders in parallel before asking the user anything. The payoff was concrete: the research immediately surfaced that `ui_specs`' table-column plan used `requested_quantity` where the real contract field is `requested_qty`, and that `ui-rules.md`'s Order Validation/Reports badge vocabularies didn't correspond to any Python field. Neither of those would have surfaced from asking "how do you want the UI to look" — they only surface from diffing planning prose against source code.

## The core tension: Field Scope Boundary applied to *presentation*, not just contracts

`CLAUDE.md` already has a Field Scope Boundary rule for the Python contracts themselves — `PaymentAgingRow` gets `suggested_action` because its spec defines it, `AllocationResultRow` doesn't get one for symmetry's sake alone. Phase 7's real work was recognizing that the *same* rule applies one layer up, to UI presentation: a status badge is a promise to the eventual Next.js developer that "this label exists because this field/rule exists." Break that promise once — one invented label sitting next to four real ones — and every badge in the list becomes suspect, because there's no longer a way to tell, without going back to `contracts.py`, which labels are real.

This is why the user's correction on decision 2 (rewrite *all four* badge groups, not just the two visibly broken ones) mattered more than it might look. The original draft's mistake wasn't factually wrong about Inventory Allocation/Payment Aging — `Fully Allocated`/`Partially Allocated`/`Backordered` genuinely are `AllocationResultRow.status` values. The mistake was *epistemic*: those correct labels sat in the same undifferentiated list as `Below Reorder Point` (a derived display label) and `Supplier Follow-up` (a derived list-membership label), with nothing distinguishing which kind each one was. "Already correct" was true about the label text and false about the list's trustworthiness as a spec.

The fix — direct vs. derived, spelled out per label — is the same pattern used everywhere else in this project's docs (V1 vs. V1.5 vs. V2 labels on spec rules, NotRequired vs. required fields on contracts). Phase 7 just extended that labeling discipline to the UI layer, where it hadn't been applied before.

## Why "Reports" status can never be direct, and what that implies

Every other workflow's badges eventually bottom out in a real field, because Python computes and returns a result. Reports are structurally different: `ReportManifest` is the *output* of a successful export call, not a status flag on some persisted entity. There is no Python code path that returns "not generated yet" or "processing" — those states only exist in the gap between a user clicking a button and a `tuple[bytes, ReportManifest]` coming back.

This matters because it's a preview of a mistake Phase 8 could make if this weren't spelled out now: naively modeling `ReportManifest | null` as "the report's status" would work for `Ready` (manifest present) but has no way to distinguish `Needs Input` from `Not Generated` from `Processing` — all three are just "manifest is null." The 4-state client lifecycle documented in `ui-contract-plan.md` exists specifically because a single nullable field can't carry it; Phase 8 needs actual client state (a `useState` or equivalent), not a field read off the envelope.

The deeper principle: not every UI need maps to *adding* a Python field. Sometimes the right answer is "this is UI session state and always will be" — forcing it into the contract layer (e.g. adding a `report_status` field to `ReportManifest` that Python would have to track) would violate the Field Scope Boundary in the other direction, inventing backend state to serve a purely client-side concern.

## Derived aggregates: where the line actually is

The fourth confirmed decision (allow derived aggregates, e.g. summing `backorder_qty` grouped by `sku`) could look, on the surface, like it contradicts the Field Scope Boundary — isn't "SKU-level backorder total" a new business fact?

The distinguishing test the session settled on: does producing this value require *interpreting* the data (a judgment call, a threshold, a weighting) or does it only require *aggregating* fields that already exist, verbatim, with a rule anyone could re-derive by reading the row data themselves? `sum(backorder_qty) group by sku` is arithmetic over already-true numbers — every input is already something Python emitted, and the operation carries no hidden business judgment. A "backorder risk score" would fail this test even if it also only referenced existing fields, because "risk" implies a weighting or threshold that isn't captured in the contract — that's new business logic wearing an aggregation costume.

This is why every derived-aggregate entry in `ui-contract-plan.md` is written as an explicit rule (source rows, source fields, grouping/filter clause) rather than just a chart title. The rule *is* the audit trail — if someone later needs to check whether a chart snuck in business logic, the rule spells out exactly what arithmetic happened and nothing else.

## Why `CONTEXT.md` stayed untouched — a boundary about *audiences*, not just content

The original plan draft treated "define `Status Badge` and `Derived Display Value` somewhere so future sessions don't re-litigate this" as sufficient justification for putting them in `CONTEXT.md`. The user's correction reframes the question: `CONTEXT.md` isn't "wherever useful definitions go" — it's the shared vocabulary for a specific audience (anyone reasoning about the *business domain*: Orders, SKUs, Aging Buckets, the Scope Gate). `Status Badge` and `Derived Display Value` are vocabulary for a narrower audience (whoever is doing UI planning), and belong scoped to the doc that audience actually reads.

The generalizable lesson: "this term needs a definition somewhere" doesn't imply "the most prominent glossary is the right place." A term's home should match the term's actual readership, not just its usefulness.

## The Figma question: absence handled explicitly instead of silently

The mid-session interruption ("why didn't you ask me for a Figma link") is worth separating from the badge/dashboard corrections above — it wasn't a mistake in the plan's content, it was a gap in the plan's *transparency*. The reasoning for skipping Figma (no connector available, `build-plan.md` marks it "if useful" not required) was sound, but it lived only in the assistant's internal reasoning, not anywhere the user could see or object to it before work proceeded.

The resolution — add an explicit "Figma reference deferred" guardrail, with the exact reconciliation procedure for when a link *does* show up later (inspect, classify V1/V1.5/V2/out-of-scope, reconcile against the contracts) — converts a silent skip into a stated, revisitable decision. This mirrors the Scope Gate's own mechanical-check philosophy: don't quietly decide something is out of scope; write down that it's deferred and why, so the next person (or session) doesn't have to rediscover the reasoning from scratch.

## What this session did *not* resolve

Two things were explicitly deferred rather than decided:

1. **snake_case vs. camelCase at the TS boundary.** The decision was "preserve snake_case verbatim for this first draft," but whether Phase 8 eventually wants a camelCase adapter layer at the API boundary (a common Next.js/React convention) was explicitly not decided — flagged as a future decision, not resolved by default.
2. **Whether `Overdue`/`Due Soon`/`Paid`-style shorthand badges are wanted at all.** The session removed the undefined versions from `ui-rules.md` but didn't decide whether to reintroduce them with an explicit derivation rule (e.g. `Paid` when `outstanding_amount <= 0`) — that's left as an open question for whoever next touches Payment Aging's UI badges.

Both are documented as open items rather than guessed at, consistent with the session's overall pattern: prefer an explicit "not decided yet" over an implicit default.
