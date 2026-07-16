/tutorial docs/plan/phase-10-fastapi-integration

Create Tutorial 07 as Track 4 — HTTP APIs & Statelessness. This tutorial should pivot from
Tutorial 06, where Phase 6 formatted already-computed Python results into Excel workbooks, to
Phase 10, where those same tested workflows are exposed through HTTP request/response endpoints
without turning the server into a workflow-run store.

Before generating or consuming this tutorial, attend the Track 4 prerequisite lessons from
`docs/teach/ROADMAP.md`:

1. **L4.1 — HTTP basics:** request/response, GET vs POST, status codes, multipart file uploads,
   and API endpoints as URLs that return structured data or files instead of web pages.
2. **L4.2 — Statelessness and trust boundaries:** what it means for the server to forget each
   request after responding, and why the server should recompute anything it can produce itself
   rather than trusting client-submitted results.

If those lessons have not been generated yet, create them before Tutorial 07. Keep them concept
first and code-light. Tutorial 07 is the case-study checkpoint where the learner sees those ideas
in real code.

Treat the main teaching arc as:

1. Tutorials 03–05 produced trusted business result envelopes.
2. Tutorial 06 showed a presentation boundary: reports consume those envelopes without
   recalculating business logic.
3. Phase 10 adds an HTTP boundary: the browser sends source files and parameters to FastAPI, and
   FastAPI calls the already-tested Python modules.
4. The core invariant is: **workflow endpoints are thin adapters, and report endpoints recompute
   from raw files instead of trusting client-side `currentResult` JSON.**
5. Statelessness should be taught as a testable property: if an endpoint needs a previous request
   to have happened, it is not stateless.

Important current-repo caveat: the repository is now post-Phase-12, so current files contain later
session-scoped persistence additions (`X-Session-Id`, `X-Persisted`, `PersistenceNotice`,
`GET /api/dashboard`, repository code). For Tutorial 07, do not let that later Phase 12 layer take
over the lesson. Use `docs/plan/phase-10-fastapi-integration/plan.md`,
`docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`, and
`docs/grilling/phase-10-fastapi-integration/` as the Phase 10 boundary. When a current code block
contains Phase 12 additions, either choose a narrower code block that shows the Phase 10 mechanism
or explicitly label the extra lines as a later forward reference. Report endpoints remain the clean
Phase 10 stateless example because Phase 12 deliberately left them unaffected.

Before writing, read at minimum:

- `docs/teach/ROADMAP.md`
- `docs/tutorials/04-inventory-allocation-core/README.md`
- `docs/tutorials/05-payment-aging-core/README.md`
- `docs/tutorials/06-excel-report-export/README.md`
- `docs/plan/phase-10-fastapi-integration/plan.md`
- `docs/plan/phase-10-fastapi-integration/explanation.md`
- `docs/plan/phase-10-fastapi-integration/ai-discussion-topics.md`
- `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`
- `docs/grilling/phase-10-fastapi-integration/explanation.md`
- `docs/architect/phase-10-fastapi-integration/decisions.md`
- `docs/architect/phase-10-fastapi-integration/approved-plan.md`
- `context/architecture.md`
- `context/library-docs.md`
- `context/code-standards.md`
- `backend/main.py`
- `backend/errors.py`
- `backend/uploads.py`
- `backend/routers/orders.py`
- `backend/routers/inventory.py`
- `backend/routers/payments.py`
- `backend/routers/templates.py`
- `lib/api-client.ts`
- `components/workflow/UploadPanel.tsx`
- `components/ui/Button.tsx`
- `components/workflow/ReportCard.tsx`
- `app/order-validation/page.tsx`
- `app/inventory-allocation/page.tsx`
- `app/payment-aging/page.tsx`
- `app/reports/page.tsx`
- `tests/test_backend_orders.py`
- `tests/test_backend_inventory.py`
- `tests/test_backend_payments.py`
- `tests/test_backend_templates.py`
- `tests/test_backend_errors.py`
- `tests/backend_test_helpers.py`

Make Tutorial 06 the immediate prerequisite because it established report artifacts, manifests,
and "presentation without leakage." Reference Tutorials 03–05 only when explaining that FastAPI is
calling the same business modules the learner already studied. Do not re-teach validation,
allocation, payment aging, or report-export internals except to show that Phase 10 wraps them.

Recommended Part structure:

1. **HTTP as an adapter over trusted Python workflows** — show how a click becomes `FormData`,
   a `POST`, an `UploadFile`, a DataFrame, and finally a known result envelope.
2. **The stateless endpoint shape** — compare `POST .../report` with the rejected
   `GET /api/reports/{report_id}` shape from ADR 0006; make the hidden job-store requirement
   concrete.
3. **The trust-boundary reason report endpoints recompute** — explain the attack where a client
   edits `currentResult` JSON and asks the server to produce an official-looking workbook.
4. **`backend/uploads.py` as the file boundary** — extension check, loader callback, conversion
   from `src/` exceptions to HTTP `400`, and why required-column lists stay in the business
   modules.
5. **Route handlers stay thin and `src/` stays framework-free** — no FastAPI imports in `src/`,
   no business-rule duplication in routers, return real business-module `TypedDict`s directly.
6. **Inventory allocation as a chained workflow endpoint** — orders + product master must run
   through `validate_orders()` first because `allocate_inventory()` consumes valid orders, not raw
   orders.
7. **Uniform business-readable errors** — `RequestValidationError` normalization, generic `500`
   handling, `TestClient(..., raise_server_exceptions=False)`, and why the UI can safely render
   `ApiError.message`.
8. **Browser mechanics: CORS, exposed headers, and file downloads** — `allow_origins` vs
   `expose_headers`, `postReport()`, `Content-Disposition`, `X-Report-Id`, object URLs, and why
   a plain sample-file link differs from `fetch()`.
9. **Frontend state and timing** — page-local `RequestStatus`, `ReportRequestState`,
   `currentResult`, explicit `File` parameters for "Run sample data," and the
   `currentResult?.x ?? []` reference-stability issue.

For every Part, include verbatim code from the current codebase, but keep the teaching focus on the
Phase 10 decision. Prefer these code locations:

- `backend/routers/orders.py` — `_load_and_validate()`, `validate_orders_report_endpoint()`
- `backend/routers/inventory.py` — `_run_allocation()`, `allocate_inventory_report_endpoint()`
- `backend/routers/payments.py` — `_parse_as_of_date()`, `calculate_payment_aging_report_endpoint()`
- `backend/uploads.py` — `read_xlsx_upload()`
- `backend/errors.py` — both exception handlers
- `backend/main.py` — CORS middleware and router inclusion
- `lib/api-client.ts` — `postFormData()`, `postJSON()`, `postReport()`, `downloadBlob()`,
  `fetchSampleFile()`
- one workflow page's `run*`, `handleRunSampleData`, and `handleDownloadReport` functions
- `tests/test_backend_errors.py` — the generic-500 `TestClient` test
- one happy-path backend test and one wrong-extension/missing-file/corrupt-file test

When current code contains Phase 12 persistence lines in a workflow endpoint, explain them in one
short note only:

> Later Phase 12 deliberately adds best-effort persistence to workflow JSON endpoints. That is not
> the Track 4 lesson. The Track 4 invariant still survives in the report endpoints: the report
> request re-accepts raw files, recomputes server-side, returns bytes, and stores no report artifact.

The end-to-end trace should follow "Run Validation" first:

`UploadPanel` file input → page-local `File` state → `runValidation(orders, productMaster)` →
`FormData` field names → `postJSON("/api/orders/validate", formData)` → FastAPI
`validate_orders_endpoint` → `read_xlsx_upload(..., load_orders)` and
`read_xlsx_upload(..., load_product_master)` → `validate_orders()` → JSON response →
`setCurrentResult()` and KPI/table re-render.

Then include a second trace for "Download Inventory Allocation Report":

workflow page `handleDownloadReport()` → same source files submitted again →
`POST /api/inventory/allocate/report` → `_run_allocation()` re-runs validation and allocation →
`export_inventory_allocation_report()` → `Response` with `.xlsx` bytes and report headers →
`postReport()` reads blob + headers → `downloadBlob()` creates object URL and clicks a hidden
download link.

Weave all 19 questions from `ai-discussion-topics.md` into the Parts as checkpoints with
collapsible answers. Do not create a separate quiz section. Suggested mapping:

- Questions 1–4: Parts 1 and 5
- Questions 5–7: Parts 2 and 3
- Questions 8–10: Parts 4 and 7
- Questions 11–13: Part 9
- Questions 14–15: Part 8
- Questions 16–18: verification/tooling note near the end or a Part 7 testing subsection
- Question 19: closing domain-language checkpoint tied to "Sample File" wording

Name failure modes explicitly:

- adding `GET /api/reports/{report_id}` without admitting it requires stored server state
- accepting client-submitted result JSON and letting the browser forge official-looking reports
- duplicating required-column lists in `backend/` instead of delegating to `load_*` functions
- importing FastAPI into `src/` and polluting the business modules with framework concerns
- putting validation/allocation/payment rules directly into route handlers
- treating FastAPI's default list-shaped validation errors as compatible with the UI's
  string-shaped `BusinessErrorMessage`
- forgetting `raise_server_exceptions=False` and failing to test the real generic-500 response
- manually setting `Content-Type` for `FormData` and breaking multipart boundaries
- omitting CORS `expose_headers`, making report metadata invisible to frontend JavaScript
- using global store/session storage to make workflow pages feel connected before the project has
  deliberately introduced persistence
- reading React state immediately after `setState()` in "Run sample data"
- merging `ReportLifecycleState` and `ReportRequestState`
- calling committed sample workbooks "templates" when they are realistic sample files with known
  data-quality issues

Add these LLM pre-study concepts before the code sections:

1. HTTP request/response and multipart uploads.
2. Stateless server design vs. stored workflow runs.
3. Trust boundaries and why recomputation can be safer than accepting precomputed client data.
4. Adapter/orchestrator modules vs. business-rule modules.
5. Browser CORS, exposed headers, and why downloads are not just "getting bytes."

Suggested challenges:

**Challenge 1 — Trace:** Follow the `orders_file` field name from `FormData` in the frontend to
the `Annotated[UploadFile, File()]` parameter in `backend/routers/orders.py`. Explain what breaks
if the frontend sends a different field name.

**Challenge 2 — Extend:** Design the minimum code changes for a new fourth workflow endpoint that
follows Phase 10's pattern. Do not implement new business rules; describe the router, upload
boundary, tests, API-client call, and page-local state needed.

**Challenge 3 — Break and fix:** Deliberately propose the rejected `GET /api/reports/{report_id}`
design and list every new piece of state, storage, identity, expiry, and trust validation it would
force into the project. Compare that with the chosen recompute-on-report design.

Write the tutorial to:
`docs/tutorials/07-fastapi-integration/README.md`

Do not update `progress-tracker.md` or `ui-registry.md` when generating the tutorial. Those were
already updated when Phase 10 was implemented; a tutorial is learning material, not a new feature.
