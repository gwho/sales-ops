# Plan — Feature phase-10-fastapi-integration: FastAPI Integration

## What was built

**New — `backend/` (FastAPI package):**
- `backend/main.py` — `FastAPI()` app instance, CORS middleware (scoped to `http://localhost:3000`, explicit `allow_methods`/`allow_headers`/`expose_headers`), exception handlers registered, all four routers included.
- `backend/errors.py` — `RequestValidationError` handler (normalizes FastAPI's list-shaped validation errors into `{"detail": "string"}`) and a catch-all `Exception` handler (generic `500`, never leaks the raw exception).
- `backend/uploads.py` — `read_xlsx_upload(file, label, loader)`: extension check, delegates parsing to the caller's business-module `load_*` function, converts `MissingColumnsError` and any other parse failure into `HTTPException(400, ...)`.
- `backend/routers/orders.py` — `POST /api/orders/validate`, `POST /api/orders/validate/report`.
- `backend/routers/inventory.py` — `POST /api/inventory/allocate`, `POST /api/inventory/allocate/report` (both run `validate_orders` internally before `allocate_inventory`).
- `backend/routers/payments.py` — `POST /api/payments/aging`, `POST /api/payments/aging/report` (both require an `as_of_date` form field).
- `backend/routers/templates.py` — `GET /api/templates/{template_name}`, allowlisted `sample_data/*.xlsx` downloads.

**New — frontend:**
- `lib/api-client.ts` — `postJSON`, `postReport`, `downloadBlob`, `fetchSampleFile`, `getSampleFileUrl`, `ApiError` class. Low-level fetch/error/blob mechanics only.

**New — tests:**
- `tests/backend_test_helpers.py`, `tests/test_backend_orders.py`, `tests/test_backend_inventory.py`, `tests/test_backend_payments.py`, `tests/test_backend_templates.py`, `tests/test_backend_errors.py` — 22 tests total, using FastAPI's `TestClient` against the real committed `sample_data/*.xlsx` files.

**New — docs:**
- `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`
- `docs/grilling/phase-10-fastapi-integration/`, `docs/architect/phase-10-fastapi-integration/` (planning-session docs, written before implementation)

**Modified:**
- `app/order-validation/page.tsx`, `app/inventory-allocation/page.tsx`, `app/payment-aging/page.tsx` — replaced static `lib/mock-data.ts` reads with live page-local state (`RequestStatus`, `currentResult`, `errorDetail`, `ReportRequestState`), an explicit "Run" button, a "Run sample data" button, and live report downloads.
- `app/reports/page.tsx` — reframed as "Sample Report Overview"; `ReportCard`s link to their workflow page instead of a disabled download button.
- `components/workflow/UploadPanel.tsx` — added `onFileChange`/`sampleFileName` props; "Sample Template" renamed to "Sample File," now a real `<a download>` link.
- `components/ui/Button.tsx` — exported `buttonVariants` (was previously module-private).
- `components/workflow/ReportCard.tsx` — added optional `workflowHref` prop on the `Ready` variant.
- `src/excel_io.py`, `src/inventory_allocation.py` — "sample template" → "sample file" in `MissingColumnsError`/`InvalidInventoryDataError`/`InvalidOrderDataError` messages.
- `pyproject.toml` — added `fastapi[standard]` dependency, `[tool.fastapi]` entrypoint.
- `CONTEXT.md` — 7 new terms (Workflow Request, Workflow Result, Current Result, Report Export Request, Report Artifact, Sample File, Business Error).
- `context/architecture.md`, `context/build-plan.md`, `context/library-docs.md`, `context/ui-contract-plan.md`, `context/ui-rules.md`, `context/progress-tracker.md`, `context/ui-registry.md` — endpoint lists and wording corrected to match; Phase 10 marked complete.

## Schema changes

None. No database, no persisted storage of any kind — this phase is explicitly stateless (see Key Invariants).

## Key invariants

- **The backend is stateless.** No `run_id`, no job store, no persisted report artifact. Every endpoint's full input arrives in that same request; nothing survives past the response. Do not add server-side caching of a "latest result" keyed by session/cookie/anything — that would silently violate `docs/adr/0006`.
- **Report endpoints (`.../report`) always recompute from raw uploaded files.** They never accept a client-supplied Workflow Result JSON as authoritative input. If a future change wants to skip recomputation for performance, that is a new architectural decision (new ADR), not a quick optimization.
- **`src/` stays framework-free.** No `fastapi` import may ever appear under `src/`. `backend/uploads.py` is the *only* place that catches `src/`'s exceptions (`MissingColumnsError`, `InvalidInventoryDataError`, `InvalidOrderDataError`, and generic parse failures) and converts them to `HTTPException`.
- **Every API error response is `{"detail": "<string>"}`.** Never a list, never a raw traceback. `backend/errors.py`'s `RequestValidationError` handler exists specifically to normalize FastAPI's own default (list-shaped) validation errors into this same shape — do not remove it, and do not add a new error path that bypasses it.
- **Route handlers return the real `src/`-module TypedDicts directly** (`OrderValidationResult` from `src/order_validation.py`, `InventoryAllocationResult` from `src/inventory_allocation.py`, `PaymentAgingResult` from `src/payment_aging.py`) as their return-type annotation. Do not introduce a parallel Pydantic `BaseModel` for these — that would create a second schema that can drift from the TypedDict source of truth.
- **CORS `allow_origins` must stay scoped to the actual dev frontend origin** (`http://localhost:3000`), never `"*"`. If `X-Report-Id`/`X-Generated-At`/`Content-Disposition` ever need to be read by new frontend code, they must stay listed in `expose_headers` — omitting a header here means the browser silently hides it from JS even though it's present on the wire.
- **`ReportLifecycleState` (4 states: Needs Input/Not Generated/Processing/Ready) and `ReportRequestState` (3 states: idle/processing/failed) are two separate, unrelated types.** `ReportLifecycleState`/`ReportCard` belong only to the static `/dashboard` and `/reports` pages. The 3 live workflow pages' download buttons use `ReportRequestState` and plain `Button`s, never `ReportCard`. Do not merge these.
- **`sample_customers.xlsx` is never exposed via `GET /api/templates/{name}`** and never read by any `src/` loader — it stays reference-only.
- **Frontend state is page-local, not shared.** No global store, no React Context, no `sessionStorage` for workflow state. `lib/api-client.ts` holds only stateless helper functions — adding React state to it would violate this.
