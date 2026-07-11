# Grilling Session: Phase 10 FastAPI Integration Plan

## Scope

This session stress-tested the shape of Phase 10 (FastAPI Integration) before any implementation started, and before `/architect` ran. Phases 1-9 had already produced a tested Python business core and a static Next.js showcase reading from committed mock JSON; `context/build-plan.md` had a Phase 10 endpoint list, but it had never been interrogated against the actual shape of the Python modules it would wrap.

Invoked via `/grill-with-docs`, which runs `/grilling` using the `/domain-modeling` skill for vocabulary and ADR discipline. The session worked through six areas in order, each with a recommendation and reasoning offered before the developer confirmed, amended, or redirected:

1. Whether a "Workflow Run" should be a persisted server-side entity
2. Whether the documented `GET /api/reports/{report_id}` endpoint still fits
3. Whether the report endpoint should recompute from source or trust a client-supplied result
4. Whether Payment Aging's `as_of_date` should be required or optional-with-default
5. The shape of the Business Error contract, and whether `ReportLifecycleState` needs an `Error` state
6. What "Sample Template" actually serves, and how uploaded files get validated

`domain-modeling` was used at the end to record the session's outcome: seven new `CONTEXT.md` terms and one ADR (`docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`), following this repo's existing `### Term` glossary format rather than the skill's generic default.

## Resolved decisions, in order

### 1. "Workflow Run" rejected as a term; no server-side run identity

Checked the actual Python modules first: `validate_orders`, `allocate_inventory`, `calculate_payment_aging` are pure functions — input DataFrame(s) in, a `TypedDict` result out, nothing written to disk, no IDs generated. There is no persistence layer anywhere in `src/`.

Decision: a "Workflow Run" is not a server-side entity in Phase 10. Each request is parsed, processed, and forgotten once the response is sent. The developer supplied the final vocabulary: **Workflow Request** (one submitted API request), **Workflow Result** (the JSON it returns), **Current Result** (the client's own copy, held in page state, never mirrored server-side). `run_id` was explicitly rejected as a term — it implies persistence, job state, revisitability, cancellation, and expiry, none of which exist.

### 2. `GET /api/reports/{report_id}` replaced with per-workflow `POST .../report`

`context/build-plan.md` documented `GET /api/reports/{report_id}`, which implies a two-phase flow: generate, get an ID back, fetch the file later by that ID. That requires persisting either the bytes or enough state to regenerate them — exactly what decision 1 ruled out. A concrete tell: `ReportManifest.report_id` is already a deterministic string (`f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"`), not a random key generated for a lookup table — nothing in the codebase was ever built to support "fetch by ID."

Decision: three workflow-specific endpoints — `POST /api/orders/validate/report`, `POST /api/inventory/allocate/report`, `POST /api/payments/aging/report` — each a single round trip returning `.xlsx` bytes directly. Rejected a single unified `/api/reports/export` endpoint with a `report_type` discriminator, to keep route boundaries aligned with the existing workflow modules and avoid one endpoint validating several unrelated input shapes.

### 3. Report endpoints recompute from raw files; never trust a client-supplied result

Two options were on the table for what a report endpoint accepts: the raw source file(s) (recompute), or the already-computed Workflow Result JSON the client already has. Chose recompute. Reasoning: trusting client JSON as authoritative report input would let a client hand-edit a "result" and get the server to notarize it into an official-looking workbook — the server should stay the sole source of truth for anything it certifies as output. Recomputing also naturally covers Order Validation's optional "Original Orders" raw sheet (`export_order_validation_report`'s `original_orders_df` parameter) without inventing a way to resend a DataFrame-shaped payload. Inventory Allocation's report endpoint therefore runs the full chain internally — `validate_orders` first, then `allocate_inventory` on the resulting valid orders — because `allocate_inventory` requires already-valid orders, matching what the UI workflow actually means by "allocate."

Accepted cost: a duplicate upload when downloading a report after already viewing results on screen. Judged acceptable at this project's demo scale.

### 4. `as_of_date` is required and client-editable, not optional-with-server-default

`calculate_payment_aging(invoices_df, as_of_date=None)` already defaults to `date.today()` server-side. The question was whether the live UI should rely on that default (omit the field) or always send an explicit value.

Decision: required and always sent. The Payment Aging page's `<input type="date">` — previously disabled, prefilled from mock data — becomes enabled, defaults to today on load, and its value is sent on every aging and aging-report request. Reasoning: turns a decorative placeholder into a genuine interactive demo control (pick a past date, watch buckets/priorities recompute), avoids hidden server-date/timezone surprises, and makes a downloaded report reproducible against the exact date the user chose. The Python function's `None` fallback stays for direct/test callers only.

### 5. Uniform Business Error contract; `ReportLifecycleState` stays at 4 states

Settled the error envelope: `{"detail": "<business-readable message>"}` everywhere, reusing FastAPI's default `HTTPException` shape rather than inventing a custom one. Known business/input failures (missing columns, invalid data, malformed `as_of_date`, bad upload) return `400`; unexpected failures return a generic `500` message, never the raw exception. `MissingColumnsError`, `InvalidInventoryDataError`, and `InvalidOrderDataError` already build business-readable messages, so no reformatting is needed for those three — `str(exc)` is the `detail`.

A follow-up correction (via the `fastapi` skill, pulled in mid-session): FastAPI's own validation errors produce a list-shaped `detail`, which would silently violate the "every response has `{detail: string}}`" contract for missing files/form fields. Added: a `RequestValidationError` handler that normalizes those into a single string; sync `def` route handlers (not `async def`) since the handlers call blocking pandas/openpyxl code; `Annotated[UploadFile, File()]` / `Annotated[str, Form()]` parameter style.

`ReportLifecycleState` (`"Needs Input" | "Not Generated" | "Processing" | "Ready"`) does **not** gain an `Error` state. A failed report request instead renders `BusinessErrorMessage` in the same slot, at the page level — keeping the lifecycle type scoped to "how far along is artifact generation," not "did this HTTP request succeed."

### 6. "Sample Template" renamed to "Sample File"; upload validation minimal

The existing `sample_data/*.xlsx` files are full fictional demo datasets with intentional data-quality issues (duplicate order ID, inactive SKU, etc.) baked in — not blank starting points. Calling the download button "Sample Template" was decided to be misleading; renamed to "Sample File" throughout (UI copy and the underlying error messages in `src/excel_io.py`/`src/inventory_allocation.py` that said "check the sample template").

Decision: reuse the existing `sample_data/*.xlsx` files as-is via an allowlisted `GET /api/templates/{template_name}` endpoint (name → path mapping, never a raw filesystem path) — no separate minimal/clean template generator. `sample_customers.xlsx` is excluded (reference-only, unused by any live workflow).

Upload validation: `.xlsx` extension mandatory-checked, content-type advisory only. Missing file, wrong extension, missing required columns, and corrupt/unreadable workbooks all return `400` with a specific business message — including corrupt-but-correctly-named files, which a first draft would have let fall through to a generic `500` (corrected mid-session: still user input failure, not server failure). No custom upload size cap in Phase 10 — judged out of scope for a demo-scale portfolio project.

## ADR synthesis

Ran every decision above through the three-part ADR test (hard to reverse / surprising without context / result of a real trade-off). Only **decision 1+2 combined** (no persisted Workflow Run, `GET /api/reports/{report_id}` replaced by stateless `POST .../report`) passed all three — recorded as `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`. Everything else (the error contract shape, upload validation rules, Sample File serving, `as_of_date` handling) was judged reversible-enough and unsurprising-enough to live as ordinary implementation guidance in `context/library-docs.md` and `context/build-plan.md` instead of a second ADR.
