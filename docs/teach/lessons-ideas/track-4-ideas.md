/teach to build or extend Track 4 — HTTP APIs & Statelessness as a companion course to
Tutorial 07, not a rewrite of it.

Track 4 already has its two roadmap prerequisite lessons:

- `0022-http-request-response-and-multipart-uploads.html`
- `0023-statelessness-and-trust-boundaries.html`

Do not overwrite those. If the goal is only to satisfy the roadmap, Track 4 is already ready for
Tutorial 07. If the goal is deeper retention after Tutorial 07, create the optional reinforcement
lessons below starting at the next available lesson number after `0023`, unless newer lessons have
already claimed those numbers.

Read first:

- `docs/teach/MISSION.md`
- `docs/teach/ROADMAP.md`
- `docs/teach/NOTES.md`
- `docs/teach/RESOURCES.md`
- `docs/teach/assets/style.css`
- `docs/teach/assets/quiz.js`
- `docs/teach/lessons/0022-http-request-response-and-multipart-uploads.html`
- `docs/teach/lessons/0023-statelessness-and-trust-boundaries.html`
- `docs/teach/reference/*.html`
- `docs/tutorials/07-fastapi-integration/README.md`
- `docs/tutorials/06-excel-report-export/README.md`
- `docs/plan/phase-10-fastapi-integration/{plan.md,explanation.md,ai-discussion-topics.md}`
- `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`
- `docs/grilling/phase-10-fastapi-integration/explanation.md`
- `docs/architect/phase-10-fastapi-integration/decisions.md`
- `backend/main.py`
- `backend/errors.py`
- `backend/uploads.py`
- `backend/routers/orders.py`
- `backend/routers/inventory.py`
- `backend/routers/payments.py`
- `backend/routers/templates.py`
- `lib/api-client.ts`
- `app/order-validation/page.tsx`
- `app/inventory-allocation/page.tsx`
- `app/payment-aging/page.tsx`
- `tests/test_backend_orders.py`
- `tests/test_backend_inventory.py`
- `tests/test_backend_payments.py`
- `tests/test_backend_templates.py`
- `tests/test_backend_errors.py`

Goal:
Move the learner from "I read that the API is stateless" to "I can trace one upload/report
request from browser to FastAPI to Python and explain why every boundary exists." The learner
should finish Track 4 able to explain, from memory, why Phase 10 has no `run_id`, why report
endpoints re-accept files, why `backend/` must stay thin, and why browser details like multipart
boundaries and CORS exposed headers are not trivia.

Existing lesson coverage:

1. `0022-http-request-response-and-multipart-uploads.html`
   Covers the vocabulary: request/response, GET vs POST, 200/400/404/500, API endpoint, and
   multipart file upload basics.

2. `0023-statelessness-and-trust-boundaries.html`
   Covers the design principle: a stateless request cannot depend on server memory of a previous
   request, and a server should not treat client-held result JSON as authoritative when it can
   recompute from raw input.

Tutorial 07 then supplies the code-depth case study. The optional lessons below should be shorter
than Tutorial 07 and should make the learner rehearse one concept at a time.

Recommended optional reinforcement sequence:

1. `0024-api-endpoint-map-and-route-boundaries.html`
   Teach how to read the Phase 10 endpoint map as a business workflow map:
   `POST /api/orders/validate`, `POST /api/orders/validate/report`, and the parallel inventory
   and payment endpoints. Make the learner classify each endpoint as JSON result, report artifact,
   or sample-file download. Failure mode: treating every endpoint as "just another URL" and
   missing the difference between a workflow request and a report export request.

2. `0025-formdata-uploadfile-and-loader-callbacks.html`
   Teach the exact bridge from browser `FormData` keys to FastAPI
   `Annotated[UploadFile, File()]` parameters to `read_xlsx_upload(file, label, loader)`.
   Use `backend/uploads.py`, `backend/routers/orders.py`, and `lib/api-client.ts`. Failure mode:
   duplicating required-column lists in `backend/` instead of delegating to the `load_*` functions
   owned by the business modules.

3. `0026-api-error-contracts-and-business-readable-failures.html`
   Teach the uniform `{"detail": "string"}` error contract. Contrast known input/business
   failures (`400`) with unexpected server failures (`500`). Use `backend/errors.py` and
   `tests/test_backend_errors.py`, especially `raise_server_exceptions=False`. Failure mode:
   letting FastAPI's default list-shaped validation errors or raw Python tracebacks leak into the
   UI.

4. `0027-cors-exposed-headers-and-browser-downloads.html`
   Teach the difference between a request being allowed and a response header being readable by
   JavaScript. Use `backend/main.py`'s CORS config, `postReport()`, `downloadBlob()`,
   `Content-Disposition`, `X-Report-Id`, and `X-Generated-At`. Failure mode: seeing a correct
   header in DevTools but getting `null` from `response.headers.get()` because
   `expose_headers` is missing.

5. `0028-thin-api-adapters-and-framework-free-business-core.html`
   Teach `backend/` as an adapter/orchestrator layer and `src/` as the business-rule layer.
   Use all three routers plus one business module already covered in Tutorials 03-05. Failure
   mode: adding business rules to FastAPI route handlers or importing FastAPI into `src/`.

6. `0029-client-state-vs-server-state-current-result-vs-report-request.html`
   Teach the distinction between page-local browser state (`currentResult`, `RequestStatus`,
   `ReportRequestState`) and server-side persisted state. Keep Phase 12 as a forward reference,
   not the main lesson. Failure mode: assuming the server remembers the result just because the
   browser still has it on screen.

7. `0030-track-4-guided-api-trace.html`
   Capstone rehearsal lesson. Trace two real operations from memory, then reveal:
   - "Run Validation": `UploadPanel` → `File` state → `FormData` → `postJSON()` →
     `validate_orders_endpoint()` → `read_xlsx_upload()` → `validate_orders()` → JSON response →
     KPI/table re-render.
   - "Download Inventory Allocation Report": same source files resubmitted →
     `POST /api/inventory/allocate/report` → `_run_allocation()` → `export_inventory_allocation_report()` →
     `.xlsx` `Response` → `postReport()` → `downloadBlob()`.

Each optional lesson must:

- Be a short, self-contained HTML file using `../assets/style.css` and `../assets/quiz.js`.
- Link to Tutorial 07 and the exact source/test files it prepares the learner to read.
- Include 2-3 retrieval checks using the existing quiz component.
- Include one tiny exercise in a real file.
- Use real snippets sparingly; keep the lesson concept-first and leave the full code walk to
  Tutorial 07.
- Name the failure mode explicitly.
- Avoid teaching Phase 12 in depth. Mention it only as "later, deliberate persistence" when
  contrasting browser-held `currentResult` with server-side state.
- Do not create learning records unless the learner has actually completed exercises or answered
  questions.

Suggested new reference docs, only if the optional lessons are generated:

- `docs/teach/reference/http-api-glossary.html`
- `docs/teach/reference/statelessness-trust-boundary-checklist.html`
- `docs/teach/reference/api-error-contract-pattern.html`
- `docs/teach/reference/cors-and-downloads-cheat-sheet.html`
- `docs/teach/reference/thin-api-adapter-pattern.html`

Suggested topics beyond the current roadmap/docs:

- **Multipart boundary failure:** why manually setting `Content-Type` for `FormData` breaks file
  uploads even when the code "looks right."
- **HTTP contract testing:** how backend tests prove endpoint shape, status code, headers, and
  response body, not just business results.
- **Browser-owned state vs. server-owned state:** a pre-Phase-12 concept bridge that prevents the
  learner from thinking `currentResult` is server memory.
- **Headers as part of the API contract:** `Content-Disposition`, `X-Report-Id`,
  `X-Generated-At`, and later `X-Persisted` are not incidental implementation details.
- **Interview explanation drill:** answer in under 90 seconds: "Why not generate a report once,
  save it, and fetch it later by ID?" The answer must mention storage, cleanup/expiry, identity,
  and the trust boundary.
- **Fourth workflow design rehearsal:** design, without implementing, the minimum backend +
  frontend shape for a hypothetical fourth Excel workflow that follows Phase 10's pattern.

Do not update `MISSION.md` unless the learner explicitly changes the learning mission. Do not
update `ROADMAP.md` unless these optional lessons are actually generated; if they are generated,
mark them as optional Track 4 reinforcement rather than changing the settled L4.1/L4.2 prerequisite
shape.
