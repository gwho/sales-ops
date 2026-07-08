# ADR 0005 - Add PaymentDataIssueRow Output Contract

## Status

Accepted

## Context

While building `src/contracts.py` in Phase 1, the required output-family list in `context/architecture.md` and `CLAUDE.md` (`ValidationSummary`, `ValidationErrorRow`, `ValidOrderRow`, `AllocationSummary`, `AllocationResultRow`, `BackorderRow`, `RemainingInventoryRow`, `SupplierFollowUpRow`, `PaymentAgingSummary`, `PaymentAgingRow`, `DraftMessageRow`, `ReportManifest`) turned out to have no family for the payment-aging **Data Issues** output.

`sales_admin_automation_toolkit_specs/03_demo_payment_aging.md` requires this output explicitly:
- Rule PA-006 — missing due date must be flagged as an error and excluded from aging.
- Rule PA-007 — missing/negative invoice amount must be flagged as an error.
- `calculate_payment_aging()` returns `(aging_df, data_issues_df)`.
- The downloadable report has a `Data Issues` sheet.
- The screen error state says: "If due dates or amounts are invalid, show them in a `Data Issues` section."

Order validation has the equivalent shape already (`ValidationErrorRow`). Payment aging had no matching contract — an oversight in the original family list, not a deliberate scope exclusion, since the spec unambiguously requires the output.

## Decision

Add a 13th output family, **`PaymentDataIssueRow`**, to the required contracts list and to `src/contracts.py`:

| Field | Description |
|---|---|
| `invoice_id` | Invoice ID if available (may be present even when other fields are invalid) |
| `customer_name` | Customer name if available |
| `error_code` | Rule ID, e.g. `PA-006`, `PA-007` |
| `error_message` | Human-readable error |
| `severity` | `Error` / `Warning` (both PA-006 and PA-007 are `Error` per the spec's exclude-from-aging behavior) |

This mirrors `ValidationErrorRow`'s shape deliberately (same field names/roles) since both are "a row failed structural validation before business rules could run" — but they stay separate TypedDicts rather than one shared generic error-row type, per the Field Scope Boundary: order validation and payment aging are different specs, and collapsing them into one shared contract would make a future spec-driven field addition to one silently show up on the other.

## Consequences

- `context/architecture.md`'s required output-family list and `CLAUDE.md`'s output-contracts list both need `PaymentDataIssueRow` added.
- Phase 1's `contracts.py` includes `PaymentDataIssueRow` alongside the other 12 families.
- Phase 5 (Payment Aging Core) implements the rule logic (`PA-006`, `PA-007`) that actually populates this contract — the contract exists before the logic, consistent with Phase 1's contracts-before-implementation ordering for the other 11 families.
