# Tutorial 07 — FastAPI Integration: HTTP APIs Without Breaking Statelessness

**After completing this tutorial you will understand:** why `backend/` exists purely to adapt HTTP
requests into calls on Tutorials 03–06's already-tested Python modules, never to hold new business
logic of its own; why this API has no `run_id` and no job store, and what the rejected
`GET /api/reports/{report_id}` shape would have forced into existence; why report endpoints
re-accept raw files and recompute instead of trusting a client-supplied result, and what attack
that design choice closes off; why `backend/uploads.py` is the one and only place `src/`'s
exceptions become HTTP responses; why Inventory Allocation's live endpoint runs two business
functions in one request instead of one; and why the browser's CORS model can let a request
succeed while still hiding its response headers from your own JavaScript.

> [!NOTE]
> **Prerequisites:** Tutorial 06 (`06-excel-report-export/README.md`) — the immediate
> prerequisite. It established Report Artifacts, manifests, and "presentation without leakage";
> this tutorial reuses `export_order_validation_report`/`export_inventory_allocation_report`/
> `export_payment_aging_report` completely unchanged, now called from inside an HTTP handler
> instead of a test. Tutorials 03–05 (`03-order-validation-core/`, `04-inventory-allocation-core/`,
> `05-payment-aging-core/`) — referenced only to confirm that FastAPI is calling the exact same
> `validate_orders()`/`allocate_inventory()`/`calculate_payment_aging()` you already studied, not
> re-teaching any of their internals. Two short concept-first lessons are worth reading first if
> you haven't already: `docs/teach/lessons/0022-http-request-response-and-multipart-uploads.html`
> and `docs/teach/lessons/0023-statelessness-and-trust-boundaries.html`. Open
> [`backend/main.py`](../../../backend/main.py), [`backend/errors.py`](../../../backend/errors.py),
> [`backend/uploads.py`](../../../backend/uploads.py),
> [`backend/routers/orders.py`](../../../backend/routers/orders.py),
> [`backend/routers/inventory.py`](../../../backend/routers/inventory.py),
> [`backend/routers/payments.py`](../../../backend/routers/payments.py),
> [`lib/api-client.ts`](../../../lib/api-client.ts), and
> [`app/order-validation/page.tsx`](../../../app/order-validation/page.tsx) alongside this tutorial.

> [!NOTE]
> **A caveat about the current codebase, worth stating once, up front:** this repository is now
> post-Phase-12. The real files you'll open contain a later session-scoped persistence layer
> (`X-Session-Id`, `X-Persisted`, `PersistenceNotice`, `GET /api/dashboard`, a `WorkflowResultsRepository`)
> layered on top of everything Phase 10 built. That layer is not this tutorial's subject — Phase 12
> gets its own tutorial later. Wherever a code excerpt below contains a Phase 12 addition, it's
> called out explicitly, once, in place, rather than silently edited away — you should be able to
> open the real file and recognize every line you see here.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Adapter pattern | `backend/uploads.py`'s `read_xlsx_upload(file, label, loader)` — takes the actual business-module loader as a parameter instead of owning its own column knowledge | Design patterns |
| Thin orchestration layer vs. business-rule layer | Every `backend/routers/*.py` handler — calls `src/` functions, contains zero `if`/`elif` business rules of its own | System design |
| Structural typing via a native serializer | `OrderValidationResult` (a `TypedDict`) returned directly as a route's type annotation — Pydantic v2 validates/serializes it with no parallel `BaseModel` | Type theory |
| Thread-pool offloading for blocking I/O | FastAPI running a sync `def` route handler in a worker thread automatically, so a blocking `pd.read_excel` call never stalls the single event loop | OS fundamentals |
| CORS as a browser-enforced trust boundary | `allow_origins` vs. `expose_headers` in `backend/main.py`'s `CORSMiddleware` | System design |
| Stateless request/response | Every endpoint in `backend/routers/` — no request depends on server memory of an earlier one | Distributed systems |

## How to use an LLM before this tutorial

### Concept 1 — HTTP request/response and multipart uploads

> "Explain what happens, at the HTTP level, when a browser submits a form containing both a text
> field and a file. Why does a file need a different request-body encoding
> (`multipart/form-data`) than a simple `application/x-www-form-urlencoded` text form? What
> mechanism lets the receiving server tell where one field ends and the next begins? Quiz me on
> what would go wrong if a client manually overrode the `Content-Type` header instead of letting
> the HTTP library set it."

*What to listen for:* `multipart/form-data` splits the body into named parts separated by a
boundary string, and that exact boundary has to be declared in the `Content-Type` header for the
server to parse the body at all. A client library (like the browser's `fetch()` given a `FormData`
object) generates that boundary itself and writes the header to match — overriding the header by
hand almost always loses the real boundary value, leaving the server unable to split the body into
parts at all.

*Practice question:* if a request's `Content-Type` header says `multipart/form-data` but omits
the `boundary=...` parameter, can the server parse the body?

### Concept 2 — Stateless server design vs. stored workflow runs

> "Compare two API designs for 'generate a report and let the user download it': (A) one endpoint
> that accepts input and returns the finished report in the same response, and (B) one endpoint
> that accepts input and returns an ID, plus a second endpoint that fetches the finished report by
> that ID later. Walk through exactly what new infrastructure design (B) requires that design (A)
> doesn't. Quiz me on whether design (B) can be built without adding any new storage."

*What to listen for:* design (B) requires something that outlives a single request — a place to
store either the finished bytes or enough information to regenerate them, keyed by the ID handed
back in step one. There's no version of design (B) that avoids this; the two-step shape *is* the
requirement for server-side memory, not an implementation detail bolted onto it afterward.

*Practice question:* if design (B)'s storage is never cleaned up, what grows without bound over
time that design (A) never has to think about at all?

### Concept 3 — Trust boundaries and why recomputation can be safer than accepting precomputed data

> "A server has already computed a result once and shown it to a client. The client later asks for
> a 'finalized' version of that same result (e.g., a signed document, an official report). Explain
> two different ways the server could produce that finalized version: (a) trust whatever the client
> currently has and format it, or (b) redo the original computation from the original raw input.
> What's the concrete risk with (a) that (b) closes off entirely? Quiz me on a scenario where (a)'s
> risk would be easy to miss during code review."

*What to listen for:* option (a) trusts a value that crossed a trust boundary — anything the client
holds could have been edited client-side before being sent back, and nothing about a plausible-looking
JSON payload proves it matches what the server actually computed. Option (b) never has this problem,
because the *only* input that can influence the output is the same raw input a legitimate request
would also need to supply — there's nothing precomputed left to tamper with.

*Practice question:* if a report-generation endpoint accepted a client-supplied `total_amount`
field instead of recalculating it from line items, what's the simplest way someone could get an
official-looking report showing a number that was never actually true?

### Concept 4 — Adapter/orchestrator modules vs. business-rule modules

> "Explain the difference between a module whose job is to *translate* between two systems (an
> 'adapter' or 'orchestrator' — e.g., converting an HTTP request into a function call, or a database
> row into an object) and a module whose job is to *decide* something (a 'business-rule' module —
> e.g., deciding whether a transaction is fraudulent). Why would putting a real business decision
> inside an adapter module be a design smell, even if the code technically works? Quiz me on how
> you'd tell, just by reading a function, which category it belongs to."

*What to listen for:* an adapter module's job is fully described by *where data comes from* and
*where it goes* — its correctness is about faithfully carrying data across a boundary, not about
what the data means. A business-rule module's job is fully described by *what the data means* — its
correctness is about applying the right real-world policy. The smell: if an adapter module contains
an `if` statement whose condition is about business meaning ("is this SKU active," not "did this
file arrive with the right field name"), that logic is living in the wrong layer — it should be one
function call away, inside the module that owns that decision, not spelled out again where the
translation happens.

*Practice question:* a function converts an uploaded file into a DataFrame, and also happens to
check "does this SKU exist in the product master" before returning it. Which category does the
`SKU` check actually belong to, and why might a future reader be confused if it stayed here?

### Concept 5 — Browser CORS and exposed headers

> "A cross-origin `fetch()` request succeeds — status 200, correct response body. Explain why the
> calling JavaScript might still be unable to read one of the response's headers, even though the
> header is genuinely present in the HTTP response (visible in browser devtools). What server-side
> configuration controls which response headers cross-origin JavaScript is allowed to read? Quiz me
> on the difference between a request being *blocked* by CORS versus a response header being
> *hidden* by CORS."

*What to listen for:* the browser's CORS model treats "did the request succeed" and "which response
headers can JavaScript actually read" as two separate permissions. By default, only a small
safelisted set of response headers (like `Content-Type`) is exposed to cross-origin JS — every other
header, including any custom `X-...` header, returns `null` from `response.headers.get(...)` unless
the server explicitly lists it in an `Access-Control-Expose-Headers` response header. A blocked
request fails outright (the browser refuses to even hand back a body); a hidden header lets
everything else through and only silently blanks out the one thing you needed to read.

*Practice question:* a response carries a custom `X-Report-Id` header, and the network tab in
devtools clearly shows it. `response.headers.get("x-report-id")` still returns `null` in the
calling code. What single server-side configuration line is almost certainly missing?

## Architecture overview

Tutorials 03–05 built three tested Python functions. Tutorial 06 built a fourth that formats their
output. Phase 10 adds the layer a browser can actually talk to — without adding a single new
business decision anywhere in the stack:

```text
  Browser (3 Client Component workflow pages)
        │  user selects/drops files -> page-local File state (Part 9)
        ▼
  runValidation(orders, productMaster)                              [Part 1, Part 9]
        │  FormData: "orders_file", "product_master_file"
        │  -- field names must match the backend's parameter names exactly
        ▼
  postFormData(path, formData)  --  lib/api-client.ts                [Part 1]
        │  fetch(..., { method: "POST", body: formData })
        │  NO manual Content-Type -- the browser writes the multipart
        │  boundary itself; setting it by hand breaks the boundary
        ▼
  FastAPI router  --  backend/routers/orders.py                      [Part 1, Part 5]
  Annotated[UploadFile, File()] orders_file, product_master_file
        │
        ▼
  backend/uploads.py: read_xlsx_upload(file, label, loader)          [Part 4]
  -- extension check -> loader(file.file) -> src/'s own load_* function
  -- catches MissingColumnsError / parse failures -> HTTPException(400)
        │
        ▼
  src/order_validation.py: validate_orders(orders_df, product_master_df)
  -- the EXACT tested function from Tutorial 03 -- zero FastAPI awareness [Part 5]
        │
        ▼
  OrderValidationResult (TypedDict) -- returned directly as the route's
  return type; Pydantic v2 validates/serializes it, no parallel BaseModel [Part 5]
        │
        ▼
  JSON response -> browser -> setCurrentResult(result) -> KPI/table re-render

  ─────────────────────────  a completely separate request  ─────────────────────────

  handleDownloadReport()  -- the SAME File objects, resubmitted from scratch [Part 2, Part 3]
        │
        ▼
  POST .../report  -- re-accepts raw files; NEVER a client-supplied result JSON
        │
        ▼
  recompute server-side -- the identical src/ call, run again from scratch
        │
        ▼
  export_*_report()  --  Tutorial 06's report_export.py, completely unchanged
        │
        ▼
  Response(bytes, headers: Content-Disposition, X-Report-Id, X-Generated-At) [Part 8]
        │
        ▼
  postReport() reads blob + headers -> downloadBlob() -> browser save dialog
```

Key invariants for this phase:

1. **The backend is stateless.** No `run_id`, no job store, no persisted report artifact anywhere
   in Phase 10's design. Every endpoint's full input arrives in that same request; nothing survives
   past the response (Part 2).
2. **`src/` stays framework-free.** No `fastapi` import ever enters `src/` — `backend/uploads.py`
   is the *only* place that catches `src/`'s exceptions and converts them to HTTP responses
   (Part 4, Part 5).
3. **Report endpoints (`.../report`) always recompute from raw uploaded files.** They never accept
   a client-supplied result as authoritative input (Part 3).

## Part 1 — HTTP as an adapter over trusted Python workflows

Open [`lib/api-client.ts`](../../../lib/api-client.ts) lines 65–82:

```typescript
async function postFormData(path: string, formData: FormData): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body: formData,
      headers: sessionHeaders(),
    });
  } catch {
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorDetail(response));
  }

  return response;
}
```

Notice what's *absent*: no `"Content-Type": "multipart/form-data"` header anywhere in this call.
When `fetch()`'s `body` is a real `FormData` instance, the browser builds the multipart body and
writes the `Content-Type` header itself — including the exact boundary string it chose while
constructing that body. `headers: sessionHeaders()` (a Phase 12 addition — Part 9's checkpoint
revisits this) only ever adds `X-Session-Id`, never `Content-Type`.

**Failure mode — manually setting `Content-Type` for `FormData` and breaking multipart
boundaries:** if a developer "helpfully" added `"Content-Type": "multipart/form-data"` to this
call's headers, the request would ship without the `boundary=...` parameter the browser would
otherwise have included — the server would receive a body it has no way to split into named parts,
because the one piece of information that tells it where one part ends and the next begins is
gone. This is exactly Concept 1's practice question, now with the real file and line number behind
it.

Now open [`backend/routers/orders.py`](../../../backend/routers/orders.py) lines 41–48:

```python
def _load_and_validate(
    orders_file: UploadFile, product_master_file: UploadFile
) -> tuple[OrderValidationResult, pd.DataFrame]:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    return validate_orders(orders_df, product_master_df), orders_df
```

`_load_and_validate` is the whole adapter, compressed into four lines: two calls into
`backend/uploads.py` (Part 4) to turn raw uploaded bytes into DataFrames, then one call into
`validate_orders()` — the exact function Tutorial 03 already tested exhaustively. Nothing about
*what makes an order valid* lives here; this function only knows how to get data from an HTTP
request into the shape `validate_orders()` already expects.

The route handler that actually connects an HTTP method and URL to this helper is
lines 51–61:

```python
@router.post("/validate")
def validate_orders_endpoint(
    response: Response,
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
    session_id: Annotated[uuid.UUID | None, Depends(get_session_id)],
    repo: Annotated[WorkflowResultsRepository, Depends(get_workflow_results_repository)],
) -> OrderValidationResult:
    result, _orders_df = _load_and_validate(orders_file, product_master_file)
    persist_workflow_result(response, repo, session_id, _WORKFLOW_TYPE, result)
    return result
```

> Later Phase 12 deliberately adds best-effort persistence to workflow JSON endpoints — the
> `session_id`, `repo` parameters and the `persist_workflow_result(...)` call are that addition.
> That is not the Track 4 lesson. The Track 4 invariant still survives in the report endpoints: the
> report request re-accepts raw files, recomputes server-side, returns bytes, and stores no report
> artifact (Part 2, Part 3).

Strip those two parameters and that one line mentally, and what's left is pure Phase 10:
`orders_file: Annotated[UploadFile, File()]` and `product_master_file: Annotated[UploadFile,
File()]` — the parameter *names* `orders_file` and `product_master_file`. Nothing else connects
them to the frontend's `formData.set("orders_file", orders)` call (`app/order-validation/page.tsx`
line 178) except that both sides independently agree on the same two strings. FastAPI reads the
incoming multipart body, finds a part named `"orders_file"`, and binds it to the parameter of the
same name — there's no schema file, no shared constant, no compiler check linking them. If either
side's name drifted, the request would still complete a full round trip, but the field FastAPI was
expecting would simply never arrive.

**Checkpoint:** Walk through exactly what happens, function call by function call, between a user
clicking "Run Validation" (with both files already selected) and the KPI tiles on the page
re-rendering with real numbers.

<details>
<summary>Reveal answer</summary>

`handleRunValidation()` guards on `canSubmit` and calls `runValidation(ordersFile,
productMasterFile)`. `runValidation` sets `status = "submitting"`, builds a `FormData` with
`orders_file`/`product_master_file` keys, and calls `postJSON<OrderValidationResult>("/api/orders/validate",
formData)`. `postJSON` calls `postFormData`, which does the actual `fetch()` POST with no manual
`Content-Type`. On the server, `validate_orders_endpoint` receives the two `UploadFile`s, calls
`_load_and_validate`, which runs both files through `read_xlsx_upload` (Part 4) and then
`validate_orders()` — the identical tested function from Tutorial 03. The route returns the
resulting `OrderValidationResult` `TypedDict` directly; FastAPI/Pydantic serializes it to JSON
(Part 5). Back in the browser, `postJSON` resolves with the parsed JSON, `runValidation` calls
`setCurrentResult(result)` and `setStatus("succeeded")`, and the page's Summary/Validation
Errors/Valid Orders sections re-render from `currentResult` — a React state update, not a page
reload. See the "Full data flow" trace later in this tutorial for the same walk with real sample
data and real numbers.

</details>

**Checkpoint:** Why does `FormData`'s field name (`orders_file`) have to match the backend's
`Annotated[UploadFile, File()]` parameter name exactly? What actually connects them?

<details>
<summary>Reveal answer</summary>

Nothing connects them except that both sides were written to agree — there's no compiler, no
schema, no import shared between `app/order-validation/page.tsx` and
`backend/routers/orders.py`. FastAPI's `Annotated[UploadFile, File()]` parameter binding works by
name: it looks at the incoming multipart body for a part whose name matches the Python parameter's
name (`orders_file`), and if the frontend used a different string, FastAPI simply never finds a
matching part for that parameter. This is a real, if narrow, coupling between two files in
different languages that nothing in either language's own tooling enforces — the only thing
keeping them in sync is a human (or an agent) reading both sides.

</details>

**Checkpoint:** What would happen if the frontend sent `orders_file` as a JSON string field
instead of a real file inside the `FormData`? Where would that fail, and with what error?

<details>
<summary>Reveal answer</summary>

`FormData.set("orders_file", someJsonString)` would still produce a valid multipart part named
`orders_file` — but FastAPI's `Annotated[UploadFile, File()]` annotation specifically expects that
part to be a *file* part (carrying a filename and content-type), not a plain text field. FastAPI's
own request-validation machinery (Part 7) would reject the request before any route-handler code
ran at all, producing FastAPI's default list-shaped validation error — which
`backend/errors.py`'s `RequestValidationError` handler (Part 7) normalizes into the same
`{"detail": "<string>"}` shape every other `400` uses, rather than a confusing type mismatch deep
inside `read_xlsx_upload`.

</details>

**Try it yourself:** Run
`uv run fastapi dev backend/main.py` in one terminal, then in another:
`curl -s -X POST http://127.0.0.1:8000/api/orders/validate -F "orders_file=not-a-real-file" -F "product_master_file=@sample_data/sample_product_master.xlsx" | python3 -m json.tool`
and read the `detail` field — confirm it's a single business-readable string, not FastAPI's raw
list-shaped validation error, proving `backend/errors.py`'s normalization (Part 7) already applies
to this exact scenario.

## Part 2 — The stateless endpoint shape

Open [`docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`](../../../docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md)'s
Context section — the endpoint list this project *almost* shipped:

```text
POST /api/orders/validate
POST /api/inventory/allocate
POST /api/payments/aging
GET  /api/reports/{report_id}
```

`GET /api/reports/{report_id}` reads as a completely ordinary REST endpoint. Walk through what has
to be true for it to actually work: a client calls something to *generate* a report, gets an ID
back, and later calls `GET /api/reports/{id}` to *fetch* it. Between those two calls, something has
to remember what that ID points to — either the real `.xlsx` bytes, or enough information to
regenerate them on demand. That "something" is a job store or a file store, full stop — there is no
version of this endpoint shape that avoids needing one.

The actual, shipped shape replaces it with three per-workflow `POST .../report` endpoints. Open
[`backend/routers/orders.py`](../../../backend/routers/orders.py) lines 64–81 —
`validate_orders_report_endpoint`, genuinely untouched by Phase 12:

```python
@router.post("/validate/report")
def validate_orders_report_endpoint(
    orders_file: Annotated[UploadFile, File()],
    product_master_file: Annotated[UploadFile, File()],
) -> Response:
    result, orders_df = _load_and_validate(orders_file, product_master_file)
    workbook_bytes, manifest = export_order_validation_report(
        result, original_orders_df=orders_df, generated_at=datetime.now()
    )
    return Response(
        content=workbook_bytes,
        media_type=_XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{manifest["file_name"]}"',
            "X-Report-Id": manifest["report_id"],
            "X-Generated-At": manifest["generated_at"],
        },
    )
```

This endpoint re-accepts the *same two files* `POST /validate` takes — not a report ID, not a
previous result. It calls `_load_and_validate` again, from scratch, and hands the fresh result
straight to `export_order_validation_report` (Tutorial 06, completely unchanged). No step here
requires the server to remember anything about a previous request. `docs/grilling/phase-10-fastapi-integration/explanation.md`
names the tell precisely: `ReportManifest.report_id` was already a deterministic string built from
`report_type` and a timestamp (Tutorial 06 Part 9) — not a randomly generated lookup key. Nothing
in `src/report_export.py` was ever built to support fetching by that ID; the field exists for
display purposes only. Reading the actual code before accepting the documented endpoint list is
what surfaced this mismatch.

**Failure mode — adding `GET /api/reports/{report_id}` without admitting it requires stored server
state:** the danger isn't that this endpoint shape is impossible — it's that it *looks* so
ordinary that a team can add it without consciously deciding to take on a job store, an identity
scheme for "which report is this," an expiry policy, and a plan for what happens when the process
restarts and the store is empty. The two-phase shape smuggles in a real architectural commitment
disguised as a routine REST endpoint.

**Checkpoint:** Why does `POST /api/inventory/allocate/report` re-run `validate_orders` internally
instead of accepting the already-known valid orders from a prior `POST /api/inventory/allocate`
call?

<details>
<summary>Reveal answer</summary>

Because the server has no way to know a prior call ever happened — statelessness means exactly
this. There is no session, no stored "last known valid orders for this client" anywhere in Phase
10's design; every request carries its own complete input. `allocate_inventory_report_endpoint`
(Part 6) can only produce a correct result by redoing the same two-step chain
(`validate_orders()` then `allocate_inventory()`) that `POST /allocate` already did, using the
files resubmitted in *this* request.

</details>

**Checkpoint:** What would have to change in this codebase to support "download the report I just
generated 5 minutes ago" without re-uploading? What's the minimum viable version of that?

<details>
<summary>Reveal answer</summary>

At minimum: a way to persist either the generated `.xlsx` bytes or the raw inputs/result needed to
regenerate them, keyed by some identifier; a way to hand that identifier back to the client after
the first request; a `GET`-style endpoint that looks the identifier up and returns the stored
artifact (or a `404` if it's gone); and a decision about how long to keep it and how to clean it
up. The minimum viable version might be an in-memory dict mapping a UUID to bytes with a short TTL
— still a real new architectural surface (in-memory state that vanishes on restart, doesn't scale
past one server process, and needs its own eviction logic), not a small tweak to the current
design. This is precisely why ADR 0006 frames the decision as something a *future* architectural
decision would need to reopen, not something to bolt on quietly.

</details>

**Try it yourself:** Run
`grep -rn "report_id" src/report_export.py` and confirm `report_id` is only ever *constructed*
(via an f-string built from `report_type` and a timestamp), never *looked up* — there's no
dictionary, no database call, nothing anywhere in `src/` that reads a `report_id` back in to
retrieve something. This is the concrete evidence behind the grilling session's tell.

## Part 3 — The trust-boundary reason report endpoints recompute

The previous Part explained *what* the rejected design would have required. This Part explains
*why* trusting a client-supplied result — even without the job-store problem — would be a genuine
security mistake, not just an architectural inconvenience.

Imagine, instead of `validate_orders_report_endpoint`'s actual body, a version that accepted the
already-computed result as its input:

```python
# Not real code -- the rejected shape, for illustration only.
@router.post("/validate/report")
def validate_orders_report_endpoint(result: OrderValidationResult) -> Response:
    workbook_bytes, manifest = export_order_validation_report(result, ...)
    return Response(content=workbook_bytes, ...)
```

Nothing here re-derives `result` from anything the server can verify — it's just formatted and
handed back as an official-looking `.xlsx` file. A client (not necessarily the real frontend; any
program that can send an HTTP request) could hand-edit `summary.valid_orders`, delete an entry
from `errors`, or invent an order row that was never actually validated, and receive back a
download that's visually indistinguishable from a genuine report. `docs/grilling/phase-10-fastapi-integration/explanation.md`
states the general principle this closes off: **a system should not accept as authoritative
anything it could not have produced itself.**

The real endpoint (Part 2) never has this problem, because it never accepts a result at all — only
raw files. The *only* way to influence what the report shows is to change the same raw input that
would have influenced the on-screen result too, which is exactly as hard (or easy) as it should
be.

**Failure mode — accepting client-submitted result JSON and letting the browser forge
official-looking reports:** the concrete cost of getting this wrong isn't abstract. A viewer of a
"Download Report" button reasonably assumes the downloaded file reflects real validation of a real
file — that's the entire point of a report. A design that trusts client JSON quietly breaks that
assumption for anyone willing to open devtools and edit a request body before it's sent.

> **System design — Trust boundary:** the line between "data this server computed and verified
> itself" and "data that arrived from outside and could say anything" is a trust boundary. Every
> `POST .../report` endpoint in this project sits entirely on the safe side of that line: its only
> external input is the same raw file a legitimate request needs anyway, never a claim about what
> the result of processing that file should be.

**Checkpoint:** If a report endpoint accepted a client-supplied `currentResult` instead of raw
files, what specific attack would become possible? Walk through it concretely.

<details>
<summary>Reveal answer</summary>

Open browser devtools, run "Run Validation" normally to get a real `currentResult` in memory,
then before clicking "Download Report," use the console to mutate `currentResult` — say, flipping
one `ValidationErrorRow`'s `severity` from `"Error"` to `"Warning"`, or deleting a row from
`errors` entirely, or bumping `summary.valid_orders` upward. If the report endpoint trusted that
mutated object as its input, the downloaded `.xlsx` would show a cleaner, more favorable picture
than the file that was actually uploaded — indistinguishable from a genuine report to anyone who
opens it, with the discrepancy invisible unless someone happens to re-run validation on the
original file and compares by hand.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_backend_orders.py -k report -v` and read
`test_validate_orders_report_returns_xlsx_with_headers` — notice the test submits the *same two raw
files* the happy-path test submits, never a JSON result, and asserts on the returned bytes/headers
directly. There is no test anywhere in this suite that constructs a report from a hand-built
result dict, because the real endpoint has no code path that would accept one.

## Part 4 — `backend/uploads.py` as the file boundary

Open [`backend/uploads.py`](../../../backend/uploads.py) lines 20–57:

```python
def read_xlsx_upload(
    file: UploadFile, label: str, loader: Callable[[object], pd.DataFrame]
) -> pd.DataFrame:
    """Validate an uploaded file's type, then load it via a business module's load_* helper.

    `loader` is one of load_orders/load_product_master/load_inventory/load_invoices --
    required-column lists stay owned by their business module, not duplicated here.
    """
    if not file.filename:
        raise HTTPException(
            status_code=400, detail=f"Please upload the required {label} and try again."
        )

    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail=f"Please upload a .xlsx Excel file for {label}.")

    try:
        return loader(file.file)
    except MissingColumnsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                f"The uploaded {label} could not be read as a valid .xlsx workbook. "
                "Please use the sample file and try again."
            ),
        ) from exc
```

`read_xlsx_upload` takes `loader` — the actual `load_orders`/`load_product_master`/`load_inventory`/
`load_invoices` function from the relevant `src/` module — as a parameter, rather than owning its
own copy of which columns each file type requires. It only ever checks two things itself: is there
a filename at all, and does it end in `.xlsx`. Everything about *which columns are required* stays
inside whichever `load_*` function this call was handed.

> **Design patterns — Adapter:** `read_xlsx_upload` adapts *any* of the four business-module
> loaders to one uniform HTTP-facing shape (raise `HTTPException(400, ...)` on failure) without
> knowing anything about what each loader specifically checks. This is the adapter pattern in its
> plainest form — one function translating between two interfaces (an `UploadFile` and a business
> module's own loading contract) by delegating the parts it doesn't need to own.

**Failure mode — duplicating required-column lists in `backend/` instead of delegating to `load_*`
functions:** the rejected alternative would hardcode `ORDERS_REQUIRED_COLUMNS`,
`INVENTORY_REQUIRED_COLUMNS`, and so on, a second time inside `backend/`. `src/order_validation.py`
and `src/inventory_allocation.py` already own these lists (Tutorials 03–04); a second copy could
silently drift the moment someone adds a required column to the Python core and forgets the
FastAPI-side list exists — producing a confusing "missing column" message that doesn't match what
the loader itself actually checks.

**Checkpoint:** The `read_xlsx_upload(file, label, loader)` design takes a business-module function
as a parameter. What testing benefit (if any) does this give beyond the DRY argument in the
explanation?

<details>
<summary>Reveal answer</summary>

It means `backend/uploads.py`'s own tests never need to know about orders/inventory/product-master
column requirements at all — a test can pass in *any* callable (including a fake one built purely
for the test) and assert only on the generic behavior (extension check, exception-to-`HTTPException`
conversion), completely decoupled from which real workflow is calling it. Conversely, `src/`'s own
`load_orders`/`load_inventory` tests (Tutorials 03–04) never need to know `backend/` exists at all
— they test the loader as a plain function, no `UploadFile`, no `HTTPException`. Each side's test
suite stays scoped to exactly what that side owns, matching the module-boundary table in
`context/architecture.md`.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_backend_orders.py -k wrong_extension -v` and read
`test_validate_orders_wrong_extension_returns_business_readable_400`
(`tests/test_backend_orders.py:64-77`) — it submits a `.csv`-named file into the `orders_file`
slot and asserts the response names both "orders file" (the `label` parameter) and `.xlsx` in its
message. Confirm this test never touches `load_orders` at all — the failure happens entirely
inside `read_xlsx_upload`, before any business-module code runs.

## Part 5 — Route handlers stay thin, and `src/` stays framework-free

Open [`context/architecture.md`](../../../context/architecture.md)'s System Boundaries table:
`backend/` **owns** "FastAPI orchestration over tested modules" and **must not own** "duplicated
business logic." This isn't a new rule invented for Phase 10 — it's the same module-boundary
discipline Tutorials 01–06 already established for `src/`'s own internal boundaries, applied one
layer outward to the new HTTP surface.

Two concrete disciplines make this real, not aspirational. First: no `import fastapi` (or
`from fastapi import ...`) appears anywhere under `src/`. Second: every route handler's return-type
annotation is a real `src/`-module `TypedDict`, never a parallel Pydantic `BaseModel`. Open
[`backend/routers/orders.py`](../../../backend/routers/orders.py) line 58 again:

```python
) -> OrderValidationResult:
```

`OrderValidationResult` is imported directly from `src.order_validation` (Tutorial 03) — not
redefined, not wrapped, not subsetted. `docs/plan/phase-10-fastapi-integration/explanation.md` §3
records that this is only safe because Pydantic v2 (confirmed installed:
`pydantic==2.13.4`) can build a `TypeAdapter` for a `TypedDict` and validate/serialize it
natively — a capability verified with a real `TestClient` round trip against
`sample_data/sample_orders.xlsx` before committing to the pattern across all three routers, not
assumed from documentation alone.

> **Type theory — Structural typing via a native serializer:** a `TypedDict` has no runtime
> identity of its own — Python sees it as a plain `dict` with static-only field/type hints
> (Tutorial 01). Pydantic v2 serializing a `TypedDict` return value works by inspecting its
> declared shape structurally, not by checking that the returned object is an *instance* of some
> class Pydantic itself defined. This is why no parallel `BaseModel` is needed: the `TypedDict`
> already *is* the schema, and defining a second, hand-maintained Pydantic model would create a
> second schema that could drift from the first the moment one of them changed and the other
> didn't.

The alternative — a second `class OrderValidationResultModel(BaseModel): ...` living in
`backend/` — would duplicate every field Tutorial 03 already defined once, with no mechanism
forcing the two definitions to agree if `OrderValidationResult` ever gained a field.

> **OS fundamentals — Thread-pool offloading for blocking I/O:** every route handler in this
> codebase is a sync `def`, never `async def`. FastAPI runs a sync handler in a worker thread pool
> automatically, so a blocking call like `pd.read_excel` (inside `load_orders`) doesn't block the
> single event loop also serving every other concurrent request. Marking the same handler
> `async def` without actually `await`-ing anything non-blocking inside it would *remove* that
> automatic offloading — the blocking pandas call would then run directly on the event loop,
> stalling every other in-flight request for its duration. "Async" isn't automatically faster; it's
> only faster when the work inside is genuinely non-blocking, and pandas/openpyxl calls aren't.

**Failure mode — importing FastAPI into `src/` and polluting the business modules with framework
concerns:** the moment `src/order_validation.py` imported anything from `fastapi`, every direct
caller of `validate_orders()` — every existing test in `tests/test_order_validation.py`, any future
non-HTTP consumer — would carry a dependency on a web framework it never needed. Tutorial 03's
entire test suite runs with zero HTTP machinery involved; that stays true only because `src/` never
imports it.

**Failure mode — putting validation/allocation/payment rules directly into route handlers:** a
route handler that reimplemented even one OV-rule or IA-rule inline would create a second place
that rule could live — and, per every earlier tutorial's recurring lesson, two copies of the same
business fact are two copies that can silently disagree. Every router in this codebase calls into
`src/` for every real decision; the router itself never branches on business meaning.

**Checkpoint:** `OrderValidationResult` is a `TypedDict`, not a `BaseModel`. What's the actual
mechanism (in Pydantic v2) that lets FastAPI serialize it correctly without a `BaseModel`?

<details>
<summary>Reveal answer</summary>

Pydantic v2 can construct a `TypeAdapter` for any type it understands structurally, including a
`TypedDict` — this is what FastAPI actually uses under the hood when a route's return-type
annotation isn't a `BaseModel` subclass. The `TypeAdapter` validates and serializes based on the
`TypedDict`'s declared field names and types, the same static shape Tutorial 01 introduced, without
needing the returned object to be an instance of any Pydantic-specific base class. This is a
genuinely different mechanism from Pydantic v1, which leaned much more heavily on `BaseModel`
inheritance — which is exactly why this repo's implementation confirmed the installed Pydantic
major version with a live round trip before trusting the pattern, rather than assuming it from
older documentation or training knowledge.

</details>

**Try it yourself:** Run
`grep -rn "^import fastapi\|^from fastapi" src/` and confirm it returns nothing — zero matches,
across every file in `src/`. Then run the same search against `backend/` and confirm the opposite:
every router file imports from `fastapi` freely, because that's exactly the layer whose job is to
know about HTTP.

## Part 6 — Inventory allocation as a chained workflow endpoint

Open [`backend/routers/inventory.py`](../../../backend/routers/inventory.py) lines 48–66:

```python
def _run_allocation(
    orders_file: UploadFile, product_master_file: UploadFile, inventory_file: UploadFile
) -> InventoryAllocationResult:
    orders_df = read_xlsx_upload(orders_file, "orders file", load_orders)
    product_master_df = read_xlsx_upload(
        product_master_file, "product master file", load_product_master
    )
    inventory_df = read_xlsx_upload(inventory_file, "inventory file", load_inventory)

    validation_result = validate_orders(orders_df, product_master_df)
    valid_orders_df = pd.DataFrame(validation_result["valid_orders"])
    try:
        return allocate_inventory(valid_orders_df, inventory_df)
    except (MissingColumnsError, InvalidOrderDataError, InvalidInventoryDataError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

`POST /api/inventory/allocate` takes **three** files, even though `allocate_inventory()`'s own
signature (Tutorial 04) only takes two DataFrames. The reason isn't a UI accident — it's a direct
consequence of what `allocate_inventory()` actually requires: `valid_orders_df`, a DataFrame of
orders that have *already passed validation*, not raw uploaded orders. There is no way to satisfy
that from a single raw orders file; something has to run `validate_orders()` first. `_run_allocation`
does exactly that, converting `validation_result["valid_orders"]` (a `list[ValidOrderRow]`, Tutorial
03) into the DataFrame `allocate_inventory()` expects with one `pd.DataFrame(...)` call — the
identical pattern `scripts/generate_mock_data.py` already used to build this project's committed
mock JSON before any live endpoint existed.

Note the `try`/`except` here is new compared to `_load_and_validate` in Part 1: `allocate_inventory()`
can itself raise `InvalidOrderDataError`/`InvalidInventoryDataError` (Tutorial 04's fail-fast rule
for required inventory fields) — a business/input failure, not a server failure, so it's caught
here and converted to the same `400` shape everything else uses, rather than surfacing as an
uncaught exception that would hit the generic `500` handler (Part 7).

**Checkpoint:** `allocate_inventory_endpoint` and `allocate_inventory_report_endpoint` both call
`_run_allocation`, which itself calls `validate_orders()` internally. Given Part 2 already
established that report endpoints recompute rather than trust a prior call — is there anything
*extra* going on here, or is this the exact same statelessness principle applied to a two-step
business pipeline instead of a one-step one?

<details>
<summary>Reveal answer</summary>

The exact same principle, just visibly chained. `_run_allocation` doesn't treat "the orders were
already validated in an earlier request" as a fact it can rely on — it re-validates from the raw
files every single call, whether that call came from `POST /allocate` or
`POST /allocate/report`. The two-function chain (`validate_orders()` then `allocate_inventory()`)
happening *inside one stateless request* is what makes this workflow possible at all without a
server-side memory of "which orders were already validated" — the chaining and the statelessness
are the same design decision, not two separate ones.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_backend_inventory.py -v` and read the test names — confirm at least one
test asserts that a file with zero valid orders (e.g., every row fails OV-001) still returns a
clean `200` with an empty-but-valid `InventoryAllocationResult`, rather than an error — proving
`_run_allocation` treats "nothing to allocate" as a legitimate business outcome, not a failure.

## Part 7 — Uniform business-readable errors

Open [`backend/errors.py`](../../../backend/errors.py) lines 24–39:

```python
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": _VALIDATION_MESSAGE},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": _GENERIC_MESSAGE},
        )
```

Two handlers, covering the two failure shapes that would otherwise break this API's own contract.
`HTTPException`s raised inside `read_xlsx_upload` or a router already produce `{"detail":
"<string>"}` via FastAPI's own default handling — no extra code needed there. What's missing
without these two: FastAPI's *own* validation machinery (the thing that fires automatically when a
required `File()`/`Form()` field is entirely absent, as Part 1's "JSON string instead of a file"
checkpoint showed) returns `detail` as a **list** of structured error objects, not a string — a
different shape than every other error this API produces.

**Failure mode — treating FastAPI's default list-shaped validation errors as compatible with the
UI's string-shaped `BusinessErrorMessage`:** `<BusinessErrorMessage message={errorDetail} />`
expects a plain string. If `handle_validation_error` didn't exist, a request missing a required
file would return `detail` as a list, and frontend code assuming `error.message` is always a string
would either render `"[object Object]"` or crash outright — a completely different, worse failure
than the clean business message every other error path produces.

### Testing this boundary: a genuine `TestClient` gotcha

Open [`tests/test_backend_errors.py`](../../../tests/test_backend_errors.py) in full:

```python
def test_completely_missing_multipart_body_returns_normalized_string_detail():
    response = client.post("/api/orders/validate")

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "upload the required files" in detail


def test_unexpected_exception_returns_generic_500_without_leaking_message(monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError("super secret internal stack trace detail")

    monkeypatch.setattr("backend.routers.orders.validate_orders", _boom)

    error_client = TestClient(app, raise_server_exceptions=False)

    with (
        (SAMPLE_DATA_DIR / "sample_orders.xlsx").open("rb") as orders,
        (SAMPLE_DATA_DIR / "sample_product_master.xlsx").open("rb") as product_master,
    ):
        response = error_client.post(
            "/api/orders/validate",
            files={
                "orders_file": upload_file("sample_orders.xlsx", orders),
                "product_master_file": upload_file("sample_product_master.xlsx", product_master),
            },
        )

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "super secret internal stack trace detail" not in detail
    assert detail == "Something went wrong processing this request. Please try again."
```

The second test's `error_client = TestClient(app, raise_server_exceptions=False)` is the whole
lesson. Starlette's `TestClient` defaults to `raise_server_exceptions=True` — deliberately designed
to re-raise an unhandled exception straight into the test process, for debugging convenience while
writing tests — even when the app has a registered handler (`handle_unexpected_error`) that would
have converted that exception into a real `500` response under production `uvicorn`. The first
version of this test failed with the raw `RuntimeError` propagating into pytest as an uncaught
exception instead of a clean assertion failure, because the *default* client bypassed the very
handler under test.

**Failure mode — forgetting `raise_server_exceptions=False` and failing to test the real generic-500
response:** without this flag, a test can never actually observe what a real client would see for
an unexpected server error — it only observes pytest's own exception-propagation behavior, which
tells you nothing about whether `handle_unexpected_error` is registered correctly or produces the
right response shape.

**Checkpoint:** Why did `TestClient`'s default `raise_server_exceptions=True` cause the
generic-500-handler test to fail with an uncaught exception instead of a clean assertion failure?
What is that setting actually for?

<details>
<summary>Reveal answer</summary>

`raise_server_exceptions=True` exists to make test-writing convenient in the common case: if your
route handler has a genuine bug, you generally *want* pytest to show you the real traceback
immediately, not a generic `500` JSON body that hides exactly where the bug is. The trade-off is
that this same behavior bypasses any registered exception handler that exists specifically to
*convert* an exception into a response — which is precisely the behavior this one test needs to
observe. The setting isn't wrong; it's tuned for the 95% case (debugging a real bug) at the cost of
the 5% case (testing the error-handling machinery itself), which is why this one test deliberately
opts out with its own dedicated client instance.

</details>

**Checkpoint:** If `raise_server_exceptions=False` had been the *default* client used throughout
`tests/test_backend_orders.py`, would any of the happy-path tests behave differently? Why or why
not?

<details>
<summary>Reveal answer</summary>

No — every happy-path test in `tests/test_backend_orders.py` exercises requests that complete
successfully or fail in an already-handled way (a `400` from `read_xlsx_upload`, for instance),
never an unhandled exception. `raise_server_exceptions` only changes behavior at the exact moment
an exception would otherwise propagate uncaught — for any request that never reaches that
situation, the flag is inert. Using it as the suite-wide default would only cost something the
moment a *real*, unanticipated bug appeared: instead of pytest surfacing the actual traceback
immediately, every test would report a generic `500` failure, and a developer would have to
manually flip the flag back off to actually see what broke. That's precisely why this project
keeps the convenient default everywhere except the one test that specifically needs to see past
it.

</details>

**Try it yourself:** Run
`uv run pytest tests/test_backend_errors.py -v` and confirm both tests pass. Then temporarily
remove `raise_server_exceptions=False` from the second test's `TestClient(...)` call and re-run —
observe pytest report the raw `RuntimeError` and its real traceback instead of a clean assertion
failure, then revert the change.

## Part 8 — Browser mechanics: CORS, exposed headers, and file downloads

Open [`backend/main.py`](../../../backend/main.py) lines 56–62:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At", "X-Persisted"],
)
```

(`X-Persisted` is a Phase 12 addition to this list — Phase 10 shipped with
`expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At"]` only.)

`allow_origins` and `expose_headers` control two genuinely different permissions. `allow_origins`
decides whether the browser lets a cross-origin request happen (and lets JavaScript read the
response body) at all. `expose_headers` decides, independently, which *response headers* — beyond
a small browser-default safelist — cross-origin JavaScript is allowed to read via
`response.headers.get(...)`. A response can be fully successful (status `200`, complete, correct
body) while a header genuinely present on the wire (visible in devtools' Network tab) still returns
`null` to `fetch()`-based code, if that header isn't explicitly listed here.

`docs/plan/phase-10-fastapi-integration/explanation.md` §7 records this as a real correction caught
during plan review: the first CORS configuration only set `allow_origins`. Without
`expose_headers`, `postReport()` (below) would have received a `200` response with a real
`.xlsx` blob, but `response.headers.get("x-report-id")` would silently return `null` — a request
that looks completely successful, quietly missing the one piece of metadata the download flow
needs.

**Failure mode — omitting CORS `expose_headers`, making report metadata invisible to frontend
JavaScript:** this is exactly the scenario Concept 5's pre-study prompt asked you to predict —
here it is with the real header names and the real file/line behind it.

Open [`lib/api-client.ts`](../../../lib/api-client.ts) lines 114–140:

```typescript
export async function postReport(
  path: string,
  formData: FormData,
  fallbackFilename: string,
): Promise<ReportDownload> {
  const response = await postFormData(path, formData);
  const blob = await response.blob();
  return {
    blob,
    filename: parseFilename(response.headers.get("content-disposition"), fallbackFilename),
    reportId: response.headers.get("x-report-id"),
    generatedAt: response.headers.get("x-generated-at"),
  };
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
```

`postReport` reads the three headers `expose_headers` explicitly allows, then converts the
response body into a `Blob` — an in-memory binary object, not yet a downloaded file.
`downloadBlob` is what actually triggers a save: `URL.createObjectURL(blob)` creates a temporary
`blob:` URL the browser can navigate to, a hidden `<a download>` element is created, clicked
programmatically, and immediately removed, and `URL.revokeObjectURL` frees the temporary URL
afterward. This whole dance exists because there's no simpler browser API for "save these
already-fetched bytes as a file" — a `Blob` isn't a URL you can just assign to `window.location`.

Contrast this with `UploadPanel`'s "Sample file" link (`components/workflow/UploadPanel.tsx` lines
88–94):

```typescript
<a
  href={getSampleFileUrl(sampleFileName)}
  download
  className={cn(buttonVariants({ variant: "dark" }), "shrink-0 whitespace-nowrap")}
>
  Sample file
</a>
```

A plain `<a href download>` never touches `fetch()`, never runs any JavaScript to make the request
— the browser itself navigates to the URL as a normal, same-mechanism-as-clicking-a-link
navigation, and the `download` attribute tells it to save rather than render the response. No CORS
configuration is involved at all, because CORS only governs what cross-origin *JavaScript* is
allowed to read — a plain navigation never hands the response back to any JavaScript to read in the
first place.

**Checkpoint:** What's the difference between what `allow_origins` controls and what
`expose_headers` controls? Could a request succeed (status 200, correct body) while still
"failing" from the frontend's perspective because of a header-exposure gap?

<details>
<summary>Reveal answer</summary>

`allow_origins` controls whether the cross-origin request is permitted at all — get this wrong and
the browser blocks the whole request, the response body included. `expose_headers` controls a
narrower, independent permission: which *response headers*, beyond the browser's small safelisted
set, cross-origin JavaScript may read via the Fetch API. Yes — this is exactly the `postReport()`
scenario above: a request can complete with a full `200` response and a correct `.xlsx` blob, while
`response.headers.get("x-report-id")` silently returns `null`, because the body and the headers are
governed by two separate CORS permissions that have to each be configured correctly.

</details>

**Checkpoint:** Why does a plain `<a href download>` element never need CORS configuration, while
`fetch()` to the same URL does?

<details>
<summary>Reveal answer</summary>

CORS is a restriction on what cross-origin *JavaScript* can read from a response — it has nothing
to do with whether a browser is *allowed to navigate* to a URL, which has always been unrestricted
(that's how hyperlinks have worked since before CORS existed). A plain `<a href download>` triggers
a normal browser navigation/download, not a JavaScript-mediated `fetch()` — no script ever receives
the response object to read headers or a body from, so there's nothing for CORS to restrict.
`fetch()`, by contrast, hands the response back to JavaScript as an object your code inspects
directly, which is exactly the situation CORS exists to govern.

</details>

**Try it yourself:** Run `uv run fastapi dev backend/main.py` and `npm run dev` together, open
`/order-validation` in a browser, upload the real sample files, click "Download Report," and watch
DevTools' Network tab. Find the `/api/orders/validate/report` request, open its Response Headers,
and confirm `X-Report-Id` and `Content-Disposition` are genuinely present on the wire — then, in
the Console, try `document.querySelector` isn't relevant here, but do confirm the download itself
completed, proving `expose_headers` is correctly configured for this exact request in the running
app, not just in the source code you already read.

## Part 9 — Frontend state and timing

Open [`app/order-validation/page.tsx`](../../../app/order-validation/page.tsx) lines 172–196:

```typescript
async function runValidation(orders: File, productMaster: File) {
  setStatus("submitting");
  setErrorDetail(null);
  setPersisted(null);
  try {
    const formData = new FormData();
    formData.set("orders_file", orders);
    formData.set("product_master_file", productMaster);
    const { data: result, persisted: persistedOutcome } = await postJSON<OrderValidationResult>(
      "/api/orders/validate",
      formData,
    );
    setCurrentResult(result);
    setPersisted(persistedOutcome);
    setStatus("succeeded");
  } catch (error) {
    setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    setStatus("failed");
  }
}

function handleRunValidation() {
  if (!ordersFile || !productMasterFile) return;
  void runValidation(ordersFile, productMasterFile);
}
```

(`setPersisted(null)`/`setPersisted(persistedOutcome)` are Phase 12 additions tracking the
`X-Persisted` outcome from Part 8's header discussion — Phase 10 shipped without them.)

`runValidation` takes `orders`/`productMaster` as **explicit function parameters**, not read from
component state (`ordersFile`/`productMasterFile`) inside its own body. `handleRunValidation` — the
actual button's `onClick` — is the thin wrapper that reads current state and passes it in. This
split exists because of a genuine React timing bug the "Run sample data" feature surfaced. Open
lines 198–217:

```typescript
async function handleRunSampleData() {
  setSampleDataLoading(true);
  setSampleDataLabel(null);
  setErrorDetail(null);
  try {
    const [orders, productMaster] = await Promise.all([
      fetchSampleFile("orders", "sample_orders.xlsx"),
      fetchSampleFile("product-master", "sample_product_master.xlsx"),
    ]);
    setOrdersFile(orders);
    setProductMasterFile(productMaster);
    setSampleDataLabel(`Using sample data: ${orders.name}, ${productMaster.name}`);
    setSampleDataLoading(false);
    await runValidation(orders, productMaster);
  } catch (error) {
    setSampleDataLoading(false);
    setErrorDetail(error instanceof ApiError ? error.message : "Something went wrong. Please try again.");
    setStatus("failed");
  }
}
```

`handleRunSampleData` calls `setOrdersFile(orders)`/`setProductMasterFile(productMaster)` purely so
the `UploadPanel`s visually update — then calls `runValidation(orders, productMaster)` directly
with the freshly-fetched `File` objects, never reading `ordersFile`/`productMasterFile` state at
all. React state updates are asynchronous and batched: calling `setOrdersFile(orders)` does not
make the `ordersFile` *variable* equal to `orders` within that same synchronous function body — it
only schedules a re-render for later. If `handleRunSampleData` had instead called
`setOrdersFile(orders); setOrdersFile(productMaster); runValidation(ordersFile, productMasterFile)`
(reading the state variables instead of the local `orders`/`productMaster` constants),
`runValidation` would see whatever `ordersFile`/`productMasterFile` held *before* this function
ran — almost certainly `null`, since nothing had been uploaded yet.

**Failure mode — reading React state immediately after `setState()` in "Run sample data":** this
is precisely the bug the explicit-parameter design avoids. A version of this code that read
component state instead of local variables would appear to work in casual manual testing (state
usually does update before a user's *next* click) and fail specifically in exactly this
same-function, immediately-after-set pattern — a subtle, hard-to-reproduce class of bug.

**Failure mode — using global store/session storage to make workflow pages feel connected before
the project has deliberately introduced persistence:** a different, tempting "fix" for keeping
pages feeling connected across navigations would be a shared Zustand/Context store, or
`sessionStorage`, holding `currentResult` globally. `docs/architect/phase-10-fastapi-integration/decisions.md`
#4 records this was considered and rejected: the three workflows have genuinely different file
requirements and result shapes, and Phase 10 explicitly scoped state to page-local
`useState`. Introducing shared state here would have been exactly the kind of persistence decision
Phase 12 later made *deliberately*, with its own ADR (0007) — smuggling in an early, undocumented
version of it during Phase 10 would have pre-empted that later, more careful decision.

**Failure mode — merging `ReportLifecycleState` and `ReportRequestState`:** `ReportLifecycleState`
(`"Needs Input" | "Not Generated" | "Processing" | "Ready"`, from Phase 9) belongs only to the
static `ReportCard` on `/dashboard` and `/reports`. The three live workflow pages' download buttons
use a separate `ReportRequestState` (`"idle" | "processing" | "failed"`) with a plain `Button` —
`docs/architect/phase-10-fastapi-integration/decisions.md` #5 explains why: a live binary download
either succeeds (the browser just saves the file, nothing to display as "Ready") or it doesn't —
there's no persisted "Ready" artifact state to represent, so reusing `ReportCard`/`ReportManifest`
here would conflate "a download attempt's outcome" with "a registry entry for a stored artifact,"
two different concepts this project keeps deliberately separate.

Now the last piece — why deriving table data needed `useMemo` at all. Open lines 236–237:

```typescript
const errors = useMemo(() => currentResult?.errors ?? [], [currentResult]);
const validOrders = useMemo(() => currentResult?.valid_orders ?? [], [currentResult]);
```

**Checkpoint:** Explain precisely why `setOrdersFile(file); runValidation(ordersFile,
productMasterFile);` (reading state right after setting it) would be a bug, using React's actual
state-update semantics.

<details>
<summary>Reveal answer</summary>

`setOrdersFile(file)` schedules a state update — it does not synchronously reassign the `ordersFile`
variable within the currently-executing function. Every reference to `ordersFile` for the rest of
that same function call still sees whatever value `ordersFile` held when this render started
(likely `null`, if no file had been uploaded through the normal path yet). `runValidation(ordersFile,
productMasterFile)`, called on the very next line, would therefore receive the *stale* pre-update
values, not the value just passed to `setOrdersFile`. This is a fundamental property of React's
state model (batched, asynchronous updates applied on the next render), not a bug specific to this
codebase — it's exactly the trap `handleRunSampleData`'s explicit-parameter design sidesteps.

</details>

**Checkpoint:** The fix was extracting `runValidation(orders, productMaster)` to take explicit
parameters. What's a different fix that *wouldn't* have worked, and why?

<details>
<summary>Reveal answer</summary>

Wrapping the call in a `useEffect` that watches `ordersFile`/`productMasterFile` and calls
`runValidation` once both are non-null would *seem* to fix the timing problem (the effect runs
after the state update commits, so it would see fresh values) — but it introduces a worse problem:
that effect would also fire on *every* future change to either file, including the user manually
re-selecting a file after already running validation once, silently re-triggering a validation run
the user didn't explicitly ask for. It conflates "state changed" with "the user clicked Run,"
two genuinely different events this page needs to keep separate (a file being selected and a
workflow being explicitly submitted are not the same action). The explicit-parameter fix avoids
this because it only ever runs in direct response to an explicit call site, never as a reaction to
state changing on its own.

</details>

**Checkpoint:** Why did `currentResult?.errors ?? []` trigger an ESLint warning but not a runtime
bug? What's the difference between "wrong value" and "wrong reference" in this context?

<details>
<summary>Reveal answer</summary>

The *value* was always correct: when `currentResult` is `null`, `errors` correctly evaluates to an
empty array every time — nothing about what the page renders is ever wrong. The problem is
*reference identity*: `?? []` constructs a brand-new array literal on every single render whenever
`currentResult` is `null`, so even though every one of those empty arrays is conceptually "the
same" value, each is a distinct object in memory. A `useMemo` (or any hook) depending on `errors`
as a dependency would see a "changed" dependency on every render (a new reference), defeating the
memoization even though the actual data never changed — a real effectiveness bug (unnecessary
recomputation), not a correctness bug (nothing renders incorrectly). Wrapping the derivation itself
in its own `useMemo(() => currentResult?.errors ?? [], [currentResult])` fixes the reference
identity, only producing a new array when `currentResult` itself actually changes.

</details>

**Try it yourself:** In `app/order-validation/page.tsx`, temporarily change
`handleRunSampleData`'s final call from `runValidation(orders, productMaster)` to
`runValidation(ordersFile!, productMasterFile!)` (reading component state instead of the local
constants). Run `npm run dev`, click "Run sample data" from a fresh page load, and observe the
request fail or submit stale/empty files — then revert the change. (If TypeScript complains about
possibly-`null` values, that complaint is itself a small piece of evidence for why the real code
reads local constants instead.)

## Full data flow: "Run Validation," from a click to re-rendered KPI tiles

1. **User selects both files.** `UploadPanel`'s native `<input type="file">` fires `onChange`,
   calling `onFileChange?.(file)` (`components/workflow/UploadPanel.tsx:77-81`) — the page's
   `setOrdersFile`/`setProductMasterFile` store the real `File` objects in component state
   (Part 9).
2. **User clicks "Run Validation."** `handleRunValidation()` checks `canSubmit` (both files
   present) and calls `runValidation(ordersFile, productMasterFile)` (Part 9).
3. **`runValidation` builds the request.** `setStatus("submitting")` flips on `LoadingState`;
   `formData.set("orders_file", orders)` and `formData.set("product_master_file", productMaster)`
   use the exact field names `backend/routers/orders.py`'s parameters expect (Part 1).
4. **`postJSON` → `postFormData` sends it.** A plain `fetch(..., { method: "POST", body: formData })`
   with no manual `Content-Type` — the browser writes the multipart boundary itself (Part 1).
5. **FastAPI receives the request.** `validate_orders_endpoint` (`backend/routers/orders.py:51-61`)
   binds `orders_file`/`product_master_file` by matching the multipart part names to the
   `Annotated[UploadFile, File()]` parameter names.
6. **`_load_and_validate` runs the adapter.** Both files go through
   `read_xlsx_upload(file, label, loader)` (Part 4) — extension check, then delegated to
   `load_orders`/`load_product_master` (Tutorial 03). Both load cleanly for the real sample files.
7. **`validate_orders(orders_df, product_master_df)` runs.** The exact tested function from
   Tutorial 03 — `test_validate_orders_happy_path_matches_real_pipeline`
   (`tests/test_backend_orders.py:12-30`) proves this call, through this exact HTTP path, produces
   `summary.total_orders == 36`, `summary.valid_orders == 28` — the same numbers
   `scripts/generate_mock_data.py` already established independently.
8. **The route returns.** `-> OrderValidationResult` is the return-type annotation; FastAPI/Pydantic
   v2 serializes the `TypedDict` to JSON with no parallel schema (Part 5).
9. **Back in the browser, `postJSON` resolves.** `postFormData`'s response is parsed as JSON;
   `runValidation` calls `setCurrentResult(result)` and `setStatus("succeeded")` (Part 9).
10. **The page re-renders.** `status === "succeeded" && currentResult` becomes true; the
    Summary/Validation Errors/Valid Orders sections read from `currentResult` — a React state
    update causing a re-render, not a page navigation. Nothing about this chain is cached, stored,
    or remembered by the server after step 8's response was sent (Part 2) — the next click re-runs
    every one of these ten steps from scratch.

## A second trace: "Download Inventory Allocation Report"

1. **User has already selected all three files** (orders, product master, inventory) — the same
   `File` objects already sitting in `app/inventory-allocation/page.tsx`'s component state.
2. **User clicks "Download Report."** `handleDownloadReport()`
   (`app/inventory-allocation/page.tsx:336-352`) checks all three files are present, sets
   `reportStatus = "processing"`.
3. **The same three files are resubmitted from scratch.** `buildFormData(orders, productMaster,
   inventory)` builds a fresh `FormData` — not a reference to whatever was submitted to
   `POST /allocate` earlier, a completely independent request (Part 2, Part 3).
4. **`postReport("/api/inventory/allocate/report", formData, ...)` sends it**, through the same
   `postFormData` mechanics as any other request (Part 1, Part 8).
5. **FastAPI's `allocate_inventory_report_endpoint` receives it**
   (`backend/routers/inventory.py:83-101`) and calls `_run_allocation(orders_file,
   product_master_file, inventory_file)`.
6. **`_run_allocation` re-runs the full chain.** `validate_orders()` runs again, from the raw
   files, producing a fresh `valid_orders_df`; `allocate_inventory(valid_orders_df, inventory_df)`
   runs against it (Part 6) — genuinely recomputed, not reused from any earlier request.
7. **`export_inventory_allocation_report(result, generated_at=datetime.now())` runs.** Tutorial
   06's report-export function, called exactly as it was in every one of its own tests — this
   endpoint is the first place in this codebase that calls it from something other than a test.
8. **The route returns raw bytes.** `Response(content=workbook_bytes, media_type=_XLSX_MEDIA_TYPE,
   headers={...})` — `Content-Disposition`, `X-Report-Id`, `X-Generated-At` (Part 8), never a
   `TypedDict`, never JSON.
9. **`postReport()` reads the blob and headers.** `response.blob()` captures the binary body;
   `response.headers.get("x-report-id")` and friends read the three headers `expose_headers`
   allows cross-origin JavaScript to see (Part 8).
10. **`downloadBlob(report.blob, report.filename)` triggers the save.** `URL.createObjectURL` →
    hidden `<a download>` → programmatic `.click()` → `URL.revokeObjectURL` — the browser's save
    dialog (or automatic download) appears, and `setReportStatus("idle")` resets the button.
    Nothing about the generated `.xlsx` is stored anywhere server-side once step 8's response was
    sent.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Follow the `orders_file` field name from `FormData` in
`app/order-validation/page.tsx` (`formData.set("orders_file", orders)`, Part 1) all the way to the
`Annotated[UploadFile, File()]` parameter of the same name in
`backend/routers/orders.py`. Write out, in your own words, every place a mismatch between the two
names could be introduced (a typo in either file, a copy-paste from a different endpoint, a
refactor that renames one side only) and what the *actual* symptom would be for each — not "it
breaks," but specifically what error, at what layer, a developer would actually see.

<details>
<summary>Hint</summary>

Revisit Part 1's third checkpoint (the "JSON string instead of a file" scenario) for the shape of
error a *type* mismatch produces. A pure *name* mismatch (right type, wrong field name) produces a
different symptom — FastAPI's validation would report a required field as simply missing, since
from FastAPI's point of view, no part named `orders_file` ever arrived at all.
</details>

**Challenge 2 — Extend** (25–35 min): Design (don't implement — no new business rules exist to
implement) the minimum set of changes for a hypothetical fourth workflow endpoint,
`POST /api/returns/process`, following Phase 10's exact pattern. List, concretely: what new router
file and what its `_load_and_process`-style helper would call; which existing or new `src/`
function it would delegate to (assume one already exists and is tested, per this repo's
Python-first sequencing — Tutorial 03's ADR 0003); what `backend/uploads.py` calls it would reuse
unchanged; what new test file and which categories of test (happy path, missing file, wrong
extension, corrupt file) it would need, mirroring `tests/test_backend_orders.py`; what new
`lib/api-client.ts` call (if any — or would it reuse existing functions unchanged?) the frontend
would make; and what new page-local state a hypothetical `/returns` page would need, following
Part 9's `RequestStatus`/`ReportRequestState` split.

<details>
<summary>Hint</summary>

Almost nothing in `backend/uploads.py` or `lib/api-client.ts` should need to change at all — both
were deliberately built generic (`read_xlsx_upload(file, label, loader)`, `postJSON`/`postReport`
taking a `path` parameter) specifically so a fourth workflow could reuse them unchanged. If your
design invents a new shared helper instead of reusing an existing one, ask whether that's solving a
real new problem or just not noticing the existing one already generalizes.
</details>

**Challenge 3 — Break and fix / Design** (30–40 min): Write out the rejected
`GET /api/reports/{report_id}` design in full, as if you were proposing it fresh. For each of the
following, state exactly what would need to be built and who/what would own it: where the
generated bytes (or enough to regenerate them) get stored; what generates the `report_id` and
guarantees it's unique; how long a stored report stays available before expiring; what happens to
a `GET` request for an ID that's expired or never existed; and whether a `report_id` needs any
authorization check (should any client with the ID be able to fetch it, or only the client that
generated it?). Then write, in one paragraph, why the actual `POST .../report` design in this
codebase needs to answer none of these five questions.

<details>
<summary>Hint</summary>

Notice how many of the five questions above are actually *the same* underlying problem
(persistence + identity + lifecycle) restated five different ways. That's not a coincidence — it's
the concrete shape of "this endpoint requires server-side memory of a past request," Part 2's test
for statelessness, applied question by question instead of stated as one abstract principle.
</details>

## Before you go: one closing question about domain language

**Checkpoint:** Why did "sample template" → "sample file" need to change **inside
`src/excel_io.py`'s own Python exception message** (`MissingColumnsError`), not just in
`UploadPanel`'s button label? What would a user actually experience if only the UI copy had been
fixed?

<details>
<summary>Reveal answer</summary>

A user would see a button that correctly says "Sample file" — but the moment their upload actually
failed (a missing column, for instance), the error message rendered by `BusinessErrorMessage`
comes straight from `MissingColumnsError`'s own generated text, which would still say "check the
sample template." That's a real, visible seam: the word a viewer sees while everything is working
would disagree with the word the system reaches for the moment something goes wrong, at exactly
the point a viewer is reading most carefully. This is the same lesson Tutorial 05/06 already
taught about business-readable messages living in the layer that raises them, not the layer that
displays them (Tutorial 05 Part 5's `days_overdue` UI-wording discussion) — fixing only the
UI-facing copy while leaving the Python-facing copy stale is a partial fix that looks complete
until the failure path actually runs.

</details>

**Failure mode — calling committed sample workbooks "templates" when they are realistic sample
files with known data-quality issues:** "Sample Template" implies a blank, clean starting point.
The real committed `sample_data/*.xlsx` files are full realistic datasets carrying the same
intentional errors the business rules exist to catch (Tutorial 02) — calling them "templates"
anywhere, UI or Python, quietly misleads a viewer about what they're about to open.

For deeper exploration, `docs/plan/phase-10-fastapi-integration/ai-discussion-topics.md` has 19
prompts — including three specifically about the Playwright verification tooling this tutorial
didn't cover in depth: why the driver script had to live inside the project directory, not the
scratchpad, due to Node's ESM vs. CommonJS module resolution; how to tell a flaky test-script
assertion from a real intermittent product bug; and whether a permanent project run-skill would
have been worth generating up front. Feed the rest of the prompts to an LLM *after* forming your
own answer first — the gap between what you thought and what you learn is where understanding
lands.
