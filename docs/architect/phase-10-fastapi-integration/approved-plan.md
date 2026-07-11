# Implementation Plan — Phase 10: FastAPI Integration

Verbatim copy of the plan approved via `ExitPlanMode` (originally written to `/Users/jessejames/.claude/plans/phase-10-fastapi-integration-spicy-engelbart.md`), preserved here for permanent record alongside the rest of the Phase 10 planning-session docs. Includes the four corrections from the plan-review round (`fastapi[standard]`, CORS `expose_headers`, "sample file" wording propagated into `src/`, and the explicit `src/`-stays-framework-free statement) that were folded in before approval.

## Context

Phases 1–9 built and tested the Python business core (`src/order_validation.py`, `src/inventory_allocation.py`, `src/payment_aging.py`, `src/report_export.py`) and a static Next.js showcase UI reading from committed mock JSON. Phase 10 is the hard-gated milestone that connects them: a thin FastAPI layer wrapping the tested Python modules, and live-wiring the three workflow pages (Order Validation, Inventory Allocation, Payment Aging) plus their report downloads to real uploads and real computed results, replacing static mock-data reads where appropriate.

A `/grilling` planning session (this same session, before `/architect` was invoked) already resolved the architecturally significant questions and recorded them in `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`, `CONTEXT.md`, `context/library-docs.md`, and `context/build-plan.md`. This `/architect` pass resolves the remaining implementation-shape questions (file layout, dev-server topology, response typing, frontend state management, dashboard/reports scope) needed before writing code.

## Language we agreed on

- **Workflow Request / Workflow Result / Current Result** — one stateless API request with uploaded file(s) + params → JSON result; the client may hold that result as local page state, the server never does. (`CONTEXT.md`)
- **Report Export Request / Report Artifact** — a request that re-accepts source files, recomputes server-side, and returns `.xlsx` bytes directly; never stored, never fetched later by ID. (`CONTEXT.md`, ADR 0006)
- **Sample File** — one of the committed `sample_data/*.xlsx` demo workbooks served for download; not a blank template. (`CONTEXT.md`)
- **Business Error** — a business-readable failure (`{"detail": "..."}`, 400) distinct from an unexpected technical failure (generic 500).
- **`ReportLifecycleState`** (existing, unchanged) — `"Needs Input" | "Not Generated" | "Processing" | "Ready"`, used only by the static `ReportCard` on `/dashboard` and `/reports`.
- **`ReportRequestState`** (new, this plan) — `"idle" | "processing" | "failed"`, the live per-page report-download button state on the 3 workflow pages. Distinct concept from `ReportLifecycleState`: a live download either succeeds (browser saves the file, no persisted "Ready" state to show) or it doesn't.
- **`RequestStatus`** (new, this plan) — `"idle" | "submitting" | "succeeded" | "failed"`, the live per-page workflow-request state (upload → run → result) on the 3 workflow pages.

## Decisions made

1. **Backend location: `backend/`** at repo root, sibling to `src/`, importing it directly (`from src.order_validation import validate_orders`, etc.) — matches the location `context/architecture.md` already named for this layer.
2. **Two independent dev servers**, not a Next.js proxy. FastAPI on `:8000` (`uv run fastapi dev backend/main.py`), Next.js on `:3000` (`npm run dev`). CORS middleware allows only the local Next.js origin, not `*`:
   ```python
   allow_origins=["http://localhost:3000"]
   allow_methods=["GET", "POST"]
   allow_headers=["*"]
   expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At"]
   ```
   `expose_headers` matters: without it, cross-origin JS can't read the report-download headers even though the response includes them. Frontend reads `process.env.NEXT_PUBLIC_API_BASE_URL`, falling back to `http://localhost:8000` in code (no committed `.env` file needed — `.gitignore` already blanket-ignores `.env*`).
3. **Response typing: return the real TypedDicts directly**, no parallel Pydantic models. `OrderValidationResult` (from `src/order_validation.py`), `InventoryAllocationResult` (from `src/inventory_allocation.py`), `PaymentAgingResult` (from `src/payment_aging.py`) become route return-type annotations; FastAPI/Pydantic v2 validates and serializes TypedDicts natively. Report endpoints return `Response`/`StreamingResponse` with `.xlsx` bytes, never a TypedDict.
4. **Frontend state is page-local**, no global store/context/session storage. Each of the 3 workflow pages owns its own `RequestStatus` + `currentResult` + `errorDetail`, and its own `ReportRequestState` for the download button. `lib/api-client.ts` holds only shared low-level mechanics (form-data POST, error-body parsing into `ApiError`, blob-download triggering, base URL) — not a shared hook or state machine.
5. **Live report downloads are plain button actions**, not `ReportCard`. Each workflow page's "Download Report" button POSTs the currently-selected raw file(s) to that workflow's `.../report` endpoint, receives `.xlsx` bytes + headers (`X-Report-Id`, `X-Generated-At`, filename via `Content-Disposition`), and triggers a browser download (object URL + hidden `<a download>`). No `ReportManifest` object is constructed client-side; failure renders `BusinessErrorMessage` near the button.
6. **`/dashboard` stays fully static/mock-derived**, unchanged from Phase 9 — no FastAPI calls, no cross-page aggregation. Explicit Phase 10 boundary, not a gap.
7. **`/reports` stays static/mock-derived too**, but its copy is reframed as a "sample report overview" rather than a live report history — cards still show static mock manifest data (sheet names etc.), but link out to the corresponding workflow page for a real download instead of a disabled "Download .xlsx" button.
8. **Inventory allocation's live endpoints run the full chain internally**: `orders_file` + `product_master_file` go through `validate_orders` first, then the resulting valid orders go through `allocate_inventory` with `inventory_file` — matching what the UI workflow actually means, and what `allocate_inventory`'s signature requires (`valid_orders_df`, not raw orders).
9. **Payment Aging's `as_of_date` is a required form field**, always sent by the client (defaults to today on page load, now editable — no longer the disabled placeholder). The Python function's `as_of_date=None` fallback stays for direct/test callers only.
10. **Uploaded files must be `.xlsx`.** Extension is mandatory-checked, content-type is advisory. Missing file, wrong extension, missing required columns, and corrupt/unreadable workbooks are all `400` with business-readable `detail`. No custom upload size cap.
11. **Uniform `{"detail": "string"}` error contract** across all endpoints, including a `RequestValidationError` handler that normalizes FastAPI's default list-shaped validation errors into a single string. Known business/input failures → `400`; unexpected failures → generic `500`; raw tracebacks never reach the client.
12. **`src/excel_io.py` and `src/*.py` stay framework-free.** `load_excel()` and the business modules keep raising their normal pandas/openpyxl/business exceptions (`MissingColumnsError`, `InvalidInventoryDataError`, `InvalidOrderDataError`) exactly as they do today for direct/test callers. `backend/uploads.py` is the only place that catches those and converts them to `HTTPException(400, detail=...)` — no FastAPI import ever enters `src/`.
13. **"Sample file" wording must be consistent everywhere, including inside `src/`.** `MissingColumnsError`, `InvalidInventoryDataError`, and `InvalidOrderDataError` currently say "Please check the sample template." / "...or check the sample template." in their generated messages (`src/excel_io.py`, `src/inventory_allocation.py`). Since "Sample File" is the agreed term (`CONTEXT.md`), these three messages get reworded to "sample file" as part of this phase, and any test asserting the old exact string gets updated alongside.

## Assumptions

- Use the `fastapi[standard]` extra rather than separate `fastapi` + `uvicorn[standard]` + `python-multipart` entries — `[standard]` already bundles `uvicorn[standard]`, `python-multipart` (needed for `File()`/`Form()` parsing), `httpx`, and `jinja2`, so no separate `python-multipart` line is needed.
- `UploadPanel` needs a new optional callback prop (e.g. `onFileChange`) so parent pages can hold the actual `File` object for submission — today it only tracks the filename internally for display.
- `WorkflowStepper`'s `currentStep` prop, currently hardcoded to the last step on all 3 pages (static-showcase artifact), should reflect real `RequestStatus` once live-wired — a natural side effect of adding real state, not a separate scope item.
- `context/architecture.md`'s "Future API Contract" section still has the stale `GET /api/reports/{report_id}` endpoint list from before ADR 0006 — this was missed when `build-plan.md` and `library-docs.md` were corrected earlier in this session, and needs the same fix.
- Existing `sample_data/*.xlsx` files (already committed, already used by `scripts/generate_mock_data.py`) double as both live upload test fixtures and the "Sample File" downloads — no new fixture files needed.

## How to build it

1. **Python dependencies**: add `fastapi[standard]` to `pyproject.toml`; add `[tool.fastapi] entrypoint = "backend.main:app"`. `uv sync`.
2. **Reword "sample template" → "sample file"** in `MissingColumnsError` (`src/excel_io.py`), `InvalidInventoryDataError`, and `InvalidOrderDataError` (`src/inventory_allocation.py`), and update any test asserting the old exact message text.
3. **`backend/` package**:
   - `backend/uploads.py` — shared `read_xlsx_upload(file, label) -> pd.DataFrame`: extension/content-type check → calls `src.excel_io.load_excel` (which stays framework-free, raising its normal pandas/openpyxl/business exceptions) → this module is what catches those and converts them to `HTTPException(400, detail=...)`. No FastAPI import ever enters `src/`.
   - `backend/errors.py` — `RequestValidationError` handler (normalize to single-string `detail`) and a catch-all `Exception` handler (generic `500`, no traceback leakage) registered on the app.
   - `backend/routers/orders.py`, `inventory.py`, `payments.py`, `templates.py` — one `APIRouter` per workflow (prefix + tags), sync `def` handlers, `Annotated[UploadFile, File()]` / `Annotated[str, Form()]` params, one HTTP operation per function, per the `fastapi` skill.
   - `backend/main.py` — `FastAPI()` instance, CORS middleware (Next.js dev origin only, explicit `allow_methods`/`allow_headers`/`expose_headers` per the Decisions section above), `include_router` for all four routers, exception handlers wired in.
4. **Template allowlist**: `TEMPLATE_FILES = {"orders": ..., "product-master": ..., "inventory": ..., "invoices": ...}` mapping name → `sample_data/*.xlsx` path (no `sample_customers.xlsx`, no raw path access); `GET /api/templates/{template_name}` returns `FileResponse` or `400` for an unknown name.
5. **`lib/api-client.ts`**: `NEXT_PUBLIC_API_BASE_URL` constant with fallback, `ApiError` class, `postJSON<T>(path, formData): Promise<T>`, `postReport(path, formData): Promise<{ blob, filename, reportId, generatedAt }>`, `downloadBlob(blob, filename)`.
6. **`UploadPanel`**: add `onFileChange?: (file: File | null) => void`, call it alongside the existing internal `fileName` state update. Re-enable the "Sample file" button, pointed at `GET /api/templates/{name}` (label already needs the earlier-agreed "Sample file" wording fix).
7. **Live-wire the 3 workflow pages** (`order-validation`, `inventory-allocation`, `payment-aging`): replace static mock-data reads with page-local `RequestStatus`/`currentResult`/`errorDetail` state; add an explicit "Run" action per page; wire `WorkflowStepper`'s `currentStep` to real state; add the report-download button with its own `ReportRequestState`; render `BusinessErrorMessage` on failure; Payment Aging's date input becomes enabled and required.
8. **`/reports`**: copy/label pass only — reframe as a sample overview, link cards to their workflow page instead of a disabled download button. No data-fetching change.
9. **Fix stale docs**: correct `context/architecture.md`'s "Future API Contract" endpoint list to match ADR 0006 (same fix already applied to `build-plan.md`/`library-docs.md`).
10. **Tests**: `tests/test_backend_orders.py`, `test_backend_inventory.py`, `test_backend_payments.py`, `test_backend_templates.py` using FastAPI's `TestClient` against the real `sample_data/*.xlsx` fixtures — happy path plus every documented 400/500 case per endpoint. Update `tests/test_excel_io.py`/`tests/test_inventory_allocation.py` for the "sample file" wording change (step 2).
11. **Post-build housekeeping** (per `AGENTS.md`/`CLAUDE.md` non-negotiables): update `context/progress-tracker.md`, `context/ui-registry.md` (any new inline error/loading treatment), and `docs/plan/phase-10-fastapi-integration/{plan.md,explanation.md,ai-discussion-topics.md}`.

## Files expected to change

**New:** `backend/__init__.py`, `backend/main.py`, `backend/errors.py`, `backend/uploads.py`, `backend/routers/{__init__.py,orders.py,inventory.py,payments.py,templates.py}`, `lib/api-client.ts`, `tests/test_backend_{orders,inventory,payments,templates}.py`.

**Modified:** `pyproject.toml`, `src/excel_io.py`, `src/inventory_allocation.py` (both just the "sample template" → "sample file" wording), `tests/test_excel_io.py`, `tests/test_inventory_allocation.py` (matching wording), `context/architecture.md`, `components/workflow/UploadPanel.tsx`, `app/order-validation/page.tsx`, `app/inventory-allocation/page.tsx`, `app/payment-aging/page.tsx`, `app/reports/page.tsx`, `context/progress-tracker.md`, `context/ui-registry.md` (if needed).

## Verification plan

- **Backend**: `uv run pytest` — existing 172 tests unchanged/passing, plus new `TestClient`-based backend tests covering every endpoint's happy path and its documented 400/500 cases.
- **Frontend**: `npm run typecheck`, `npm run lint`, `npm run build` all clean. Build must not require a running backend (the 3 workflow pages stay Client Components with no build-time fetch; `/dashboard` and `/reports` stay static).
- **Live-browser** (per `CLAUDE.md`'s UI-change mandate): run `uv run fastapi dev backend/main.py` and `npm run dev` together; upload the real committed `sample_data/*.xlsx` files through all 3 pages and confirm results match `scripts/generate_mock_data.py`'s output; download and open a report from each page; deliberately trigger a `400` (e.g. wrong file in a slot) and confirm `BusinessErrorMessage` renders correct copy; confirm no CORS errors in the console; confirm `/dashboard` and `/reports` remain visually unchanged from Phase 9.

---

**Note on implementation deviations from this plan:** during actual implementation, one feature was added that isn't in this plan — an explicit "Run sample data" action per workflow page (fetches the allowlisted sample files and runs the workflow on them through the same submission path as a manual upload), added mid-session at the user's request after this plan was approved and initial implementation was underway. See `docs/plan/phase-10-fastapi-integration/plan.md` and `explanation.md` for what was actually built, including this addition.
