# Phase 3: Order Validation Core — Plan

## What was built

| Artifact | Purpose |
|---|---|
| `src/order_validation.py` | `load_orders`, `load_product_master`, `validate_orders`, and the local `OrderValidationResult` envelope. Implements every rule in `01_demo_order_validation.md` (OV-001–OV-007). |
| `tests/test_order_validation.py` | Every spec §12 test case plus edge cases resolved during `/architect`: multiple errors per row, per-field OV-001, blank-field skip rule, OV-003 SKU sub-cases, OV-004 quantity type handling, OV-005 date parseability, OV-007 vs OV-001 conflict, summary counting with overlapping violations, deterministic error ordering, optional-field handling, and loader column-vs-value tests. |

`uv run pytest` passes — 63 tests (32 from Phases 1–2, 31 new).

## Why this order

`context/build-plan.md` Phase 3 is the first business-rule module. It depends on Phase 1's `excel_io.py`/`contracts.py` and Phase 2's proof that the contract shapes hold real demo data, but does not depend on allocation or payment aging. No UI, FastAPI, report export, or allocation logic is included — those stay out of scope per the Scope Gate.

## Key decisions (resolved via `/architect` before implementation)

1. **Result envelope, not a tuple**: `validate_orders()` returns a single `OrderValidationResult` dict (`{"summary", "valid_orders", "errors"}`), defined locally in `order_validation.py` rather than added to `src/contracts.py` — it's a transport shape composed of existing families, not a new business-facing output family. Sets the pattern for Phase 4/5's own local result envelopes.
2. **Multiple errors per row, field-level OV-001**: every rule is evaluated independently per row; a row can appear multiple times in `errors`. OV-001 emits one error per missing required field (fixed column order), not a combined message.
3. **OV-001 / OV-007 conflict resolved**: the spec's own text has `payment_terms` in both OV-001's required-field list (Error) and OV-007's dedicated rule (Warning). Resolved in favor of OV-007 — `payment_terms` is excluded from OV-001 entirely, so a blank `payment_terms` produces exactly one Warning, never an Error. This keeps "Warning-only rows stay valid" internally consistent.
4. **Blank-field skip rule**: OV-002 (duplicate), OV-003 (SKU), OV-004 (quantity), OV-005 (dates), and OV-006 (priority) all skip their own check when the underlying field is blank — OV-001 already owns that case, avoiding redundant double-flagging.
5. **OV-003 splits into three codes**: `OV-003-UNKNOWN_SKU`, `OV-003-INACTIVE_SKU`, `OV-003-INVALID_ACTIVE_FLAG` — same rule family, distinct business-readable messages, mirroring the spec's own "boolean/string" `active` column note.
6. **OV-005 splits into three codes**: `OV-005-INVALID_ORDER_DATE`, `OV-005-INVALID_DELIVERY_DATE`, `OV-005-DELIVERY_BEFORE_ORDER` — malformed dates get a distinct message from the date-ordering comparison.
7. **Malformed data never raises**: non-numeric quantity, non-whole floats, and unparseable dates all convert to business-readable `ValidationErrorRow` entries at the module boundary, per `context/code-standards.md`.
8. **`active` column normalized permissively**: real `bool`, or common truthy/falsy strings (`"true"/"yes"/"y"/"1"`, `"false"/"no"/"n"/"0"`, case-insensitive); unrecognized/blank values are a distinct data-quality error, never defaulted to active.
9. **Deterministic error ordering**: `errors` is sorted by `(row_number, rule_order, ov001_field_order)` so tests and the future UI get stable output.
10. **`ValidOrderRow.payment_terms`** is normalized to `""` for Warning-only rows (the contract requires `str`, not `NotRequired`), rather than omitted.
11. **`product_name` fill-from-master**: only fills from `product_master_df` when the order row's own `product_name` is blank; an order-row value always wins when present. `sales_owner` has no reference-file fallback — included only when present/non-blank.
12. **Loader vs. rule distinction**: `load_orders`/`load_product_master` raise `MissingColumnsError` when a required *column* is absent (e.g. `payment_terms` column missing entirely) — a structurally different problem from a present-but-blank cell, which is a per-row OV-001/OV-007 concern.

## Scope boundary held

- No inventory allocation, payment aging, report export, FastAPI, or UI code touched.
- Only V1/unlabeled rules from `01_demo_order_validation.md` implemented — no rule from that spec is marked Optional/V1.5/V2, so nothing was excluded on scope grounds.
- Exhaustive rule/edge-case coverage lives entirely in `tests/test_order_validation.py`'s inline DataFrame fixtures, not in `sample_data/sample_orders.xlsx`, per `context/code-standards.md`.
