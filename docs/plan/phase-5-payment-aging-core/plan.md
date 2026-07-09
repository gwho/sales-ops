# Phase 5: Payment Aging Core — Plan

## What was built

| Artifact | Purpose |
|---|---|
| `src/payment_aging.py` | `load_invoices`, `calculate_payment_aging`, and the local `PaymentAgingResult` envelope. Implements every rule in `03_demo_payment_aging.md` (PA-001–PA-007). |
| `tests/test_payment_aging.py` | Every spec §12 test case plus edge cases resolved during `/architect`: overpayment clamping, invalid `paid_amount` degrading silently, a row carrying both PA-006 and PA-007, the Watch window at the 0/-7 day boundary, aging-bucket/priority boundaries at day 30/31/60/61/90/91, `aging_bucket_counts` always exposing all five keys, draft-message scoping, currency-aware message formatting, and loader column-vs-value tests. |
| `tests/contract_fixtures.py` | `DRAFT_MESSAGE_ROW_FIXTURE.message_text` corrected from a hardcoded `$58,000.00` to the currency-aware `HKD 58,000.00`; `PAYMENT_AGING_ROW_FIXTURE.invoice_date`/`due_date` corrected by one day to match the real `sample_invoices.xlsx` output field-for-field. |
| `context/progress-tracker.md` | Phase 5 checklist marked complete, decision log entry added, current phase advanced to Phase 6. |

`uv run pytest` passes — 127 tests (93 from Phases 1–4, 34 new).

## Schema changes

None. No fields were added to `src/contracts.py` — `PaymentAgingSummary`, `PaymentAgingRow`, `PaymentDataIssueRow`, and `DraftMessageRow` are used exactly as already defined (the latter three families were already established in Phase 1/2).

## Why this order

`context/build-plan.md` Phase 5 is the third business-rule module. Unlike Phase 4, it does not consume another module's output — it reads `invoices.xlsx` directly, so it has no dependency on `order_validation.py` or `inventory_allocation.py`. It depends only on Phase 1's `excel_io.py`/`contracts.py` and Phase 2's proof (`PAYMENT_AGING_*_FIXTURE`, `generate_invoices()`) that the contract shapes hold real demo data. No UI, FastAPI, or report export logic is included — those stay out of scope per the Scope Gate. No rule in `03_demo_payment_aging.md` carries a version label, so all of PA-001–PA-007 are in scope.

Before starting Phase 5, substantial uncommitted Phase 4 hardening work (found already sitting in the working tree — see `docs/plan/phase-4-inventory-allocation-core/`) was committed to PR #3 first, per user instruction, so Phase 5 branches from a clean, fully-tested Phase 4 tip rather than carrying unrelated uncommitted changes forward.

## Key decisions (resolved via `/architect` before implementation)

1. **Result envelope, not a tuple**: `calculate_payment_aging()` returns a single `PaymentAgingResult` dict (`{"summary", "aging_rows", "data_issues", "draft_messages"}`), defined locally in `payment_aging.py` rather than added to `src/contracts.py` — mirrors Phase 3/4's envelope pattern rather than the spec's suggested three-function, DataFrame-tuple-returning shape (`calculate_payment_aging() -> tuple[df, df]` plus a separate `create_follow_up_messages()`).
2. **Paid invoices stay in the aging table**: `outstanding_amount` is clamped to `max(0, invoice_amount - paid_amount)`, and a Paid invoice (`outstanding_amount == 0`) still appears in `aging_rows` with `follow_up_priority="None"` and `suggested_action="No action required"` — PA-002 only excludes it from *overdue follow-up*, not from the aging table itself.
3. **`total_invoices` counts every loaded row, aggregates don't**: `PaymentAgingSummary.total_invoices` includes PA-006/PA-007 data-issue rows; `aging_bucket_counts`, `total_outstanding_amount`, `overdue_amount`, and `high_priority_count` are computed only from `aging_rows` — mirrors Phase 3's `ValidationSummary.total_orders` semantics (all loaded rows, valid or not).
4. **`as_of_date: date | None = None`**, resolved via `effective_date = as_of_date or date.today()` inside the function body, never a literal default argument — matches the Phase 2 `sample_data.py` `reference_date` convention, and keeps the parameter name aligned with the spec's own UI-facing `as_of_date` date selector (§9).
5. **`days_overdue` is the raw signed value**, not floored at 0: `effective_date - due_date` in days, so a due date five days out reports `days_overdue = -5`. This lets Watch be derived directly as `-7 <= days_overdue <= 0`, and keeps the contract's plain `int` field mathematically honest for every row, not just overdue ones.
6. **Draft reminders only for active overdue follow-up**: generated when `outstanding_amount > 0 and days_overdue > 0 and follow_up_priority in {"High", "Medium", "Low"}` — never for Watch, Current, Paid, or data-issue rows, matching spec §8's literal "a draft message for each overdue customer."
7. **Invalid `paid_amount` degrades silently; invalid `invoice_amount` doesn't**: blank, non-numeric, or negative `paid_amount` all default to `0.0` with no data issue raised, since PA-001 only documents "missing → 0" and PA-007 names `invoice_amount` specifically. Only `invoice_amount` missing/non-numeric/negative triggers a PA-007 `PaymentDataIssueRow`, and a row can independently carry both a PA-006 (missing due date) and PA-007 issue.
8. **Draft message amounts are currency-aware**: formatted as `f"{currency} {amount:,.2f}"` when the invoice's `currency` column is present (e.g. `"HKD 58,000.00"`), falling back to a bare `f"{amount:,.2f}"` when blank — not the literal `$` the original hand-authored `DRAFT_MESSAGE_ROW_FIXTURE` used, since `currency` isn't part of any output contract (Field Scope Boundary) and a bare `$` misrepresents the HKD/SGD/TWD sample invoices.
9. **`PaymentDataIssueRow` never surfaces a row index**: the per-row loop position is used only internally (nothing in the contract has a `row_number` field, unlike `ValidationErrorRow`), so `error_message` text stays plain business language (`"Due date is missing."`) with no `contracts.py` change.
10. **Aging bucket boundaries are inclusive at both ends**: `<=0` Current, `1–30`, `31–60`, `61–90`, `>90` → `90+ Days`. Priority evaluation order (first match wins): Paid → High (`days_overdue > 60 or outstanding_amount >= 50000`, can override the bucket) → Medium → Low → Watch (`-7 <= days_overdue <= 0`) → None.

## Scope boundary held

- No order validation, inventory allocation, report export, FastAPI, or UI code touched (beyond fixing the pre-existing `DRAFT_MESSAGE_ROW_FIXTURE`/`PAYMENT_AGING_ROW_FIXTURE` values in `tests/contract_fixtures.py`).
- Every rule implemented is unlabeled in `03_demo_payment_aging.md` — no V1.5/V2/Optional rule exists in this spec, so nothing was excluded on scope grounds.
- Exhaustive rule/edge-case coverage lives entirely in `tests/test_payment_aging.py`'s inline DataFrame fixtures, not in `sample_data/sample_invoices.xlsx`, per `context/code-standards.md`.
- Manually verified against `sample_data/sample_invoices.xlsx` (`as_of_date=2026-07-09`) — `INV-2026-001`'s computed row matches the corrected `PAYMENT_AGING_ROW_FIXTURE` field-for-field; `INV-2026-009` (missing due date) appears only in `data_issues`.
