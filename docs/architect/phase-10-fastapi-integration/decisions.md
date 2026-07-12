# Architectural Decisions: Phase 10 FastAPI Integration

This session ran after the `/grilling` session recorded in `docs/grilling/phase-10-fastapi-integration/`, which had already settled *what* the stateless architecture and terminology should be (see ADR 0006). This `/architect` session settled *how* to actually build it: file layout, dev-server topology, response typing, frontend state management, and the scope boundary between live and static pages. It produced the approved plan at `/Users/jessejames/.claude/plans/phase-10-fastapi-integration-spicy-engelbart.md`, revised once after an initial rejection with four concrete corrections.

## 1. Backend location: `backend/` at repo root

**Decision:** Create `backend/` as a sibling to `src/`, importing it directly (`from src.order_validation import validate_orders`), not `api/`, not `src/api/`.

**Why over the alternatives:** This wasn't actually an open decision — `context/architecture.md`'s System Boundaries table already named `backend/` as the future FastAPI location ("Future `backend/` | FastAPI orchestration over tested modules | Duplicated business logic"). Reading the existing docs before treating file layout as a fresh question avoided a pointless debate between `api/`, `src/api/`, and `backend/` that the project had already resolved, just not yet acted on.

**Cost of the alternative:** Picking a different name (`api/`) would have created a second, conflicting convention the next contributor would have to reconcile against the documented one.

## 2. Two independent dev servers, not a Next.js proxy — with explicit CORS

**Decision:** FastAPI runs standalone on `:8000` (`uv run fastapi dev backend/main.py`), Next.js runs standalone on `:3000` (`npm run dev`). The frontend calls FastAPI directly via `NEXT_PUBLIC_API_BASE_URL` (falling back to `http://localhost:8000` in code). CORS middleware explicitly allows only the local Next.js origin:

```python
allow_origins=["http://localhost:3000"]
allow_methods=["GET", "POST"]
allow_headers=["*"]
expose_headers=["Content-Disposition", "X-Report-Id", "X-Generated-At"]
```

**Why over the alternative:** A Next.js `rewrites()` proxy would make calls same-origin and remove the need for CORS entirely — but it also hides that this is a real two-service system behind Next.js config, and adds a proxy layer whose only job is to work around a problem (cross-origin calls) that CORS already solves directly. Keeping FastAPI genuinely standalone keeps the architecture honest: it's a real backend a client happens to call, not a detail Next.js papers over. It also keeps frontend and backend deployable independently later.

**Correction from plan review:** The first draft of this decision only specified `allow_origins`. Without `expose_headers`, the browser's CORS policy silently strips `Content-Disposition`, `X-Report-Id`, and `X-Generated-At` from what cross-origin JavaScript can read — the response would still *contain* those headers, but `fetch()`'s `response.headers.get(...)` would return `null` for all three. This was caught during plan-approval review, not during the original design conversation.

## 3. Response typing: return the real TypedDicts directly

**Decision:** Route handlers return the actual result types already defined in the business modules — `OrderValidationResult` (`src/order_validation.py`), `InventoryAllocationResult` (`src/inventory_allocation.py`), `PaymentAgingResult` (`src/payment_aging.py`) — as their return-type annotation. No parallel Pydantic `BaseModel`s are defined in `backend/`. Report endpoints return `Response` with raw bytes, never a TypedDict.

**Why over the alternative:** Pydantic v2 (which this FastAPI version uses) validates and serializes `TypedDict` return types natively — confirmed by an actual `TestClient` smoke test against `/api/orders/validate` before committing to the approach, not just assumed from documentation. Defining separate Pydantic models would duplicate every field already defined once in the TypedDicts, and duplicated schemas drift: a field added to `OrderValidationResult` wouldn't automatically appear in a hand-maintained parallel Pydantic model, and nothing would fail loudly when that happened.

**Note surfaced during the session:** these three result types are *not* all centralized in `src/contracts.py` — they're defined locally in their own business modules (`contracts.py` holds the sub-row types like `ValidationErrorRow`, `AllocationResultRow`, etc., which the local result TypedDicts then compose). Route return-type annotations had to import from the correct per-module location, not assume everything lives in `contracts.py`.

## 4. Frontend state: page-local, no global store

**Decision:** Each of the three workflow pages owns its own `RequestStatus` (`"idle" | "submitting" | "succeeded" | "failed"`), `currentResult`, and `errorDetail` as local `useState`. No Zustand/Redux/Context/`sessionStorage`. `lib/api-client.ts` holds only shared low-level mechanics — form-data POST, error-body parsing, blob-download triggering, base URL — not a shared state hook.

**Why over the alternatives:** A shared `useWorkflowRequest` hook was the initial recommendation, but the developer redirected to something narrower: the three workflows have genuinely different file requirements (2 files, 3 files, 1 file + a date field) and different result shapes, so a hook trying to unify all three would either need generics that add complexity for three call sites, or leak workflow-specific concerns back into a "shared" abstraction. What *is* identical across all three — POSTing `FormData`, parsing a `{detail: string}` error body, triggering a blob download — stays shared at the API-client level, where it's genuinely the same code, not just superficially similar.

## 5. Live report downloads are plain button actions, not `ReportCard`

**Decision:** Each workflow page's "Download Report" button directly POSTs the currently-selected raw files to that workflow's `.../report` endpoint, receives `.xlsx` bytes + headers, and triggers a browser download (object URL + hidden `<a download>`). No `ReportManifest` object is constructed client-side. A separate `ReportRequestState` (`"idle" | "processing" | "failed"`) tracks just the button, distinct from `ReportLifecycleState`.

**Why over the alternative:** Extending `ReportManifest` (making `sheet_names` optional, or adding an `X-Sheet-Names` header) would let `ReportCard` drive the live download path too — more visually consistent with Phase 9, but it reopens a contract decision already settled in the grilling session (`sheet_names` isn't forced into headers because the UI doesn't need it there) and conflates two different concepts: "a binary download either succeeded or it didn't" is not the same as "here's a registry entry for an artifact," which is what `ReportCard`/`ReportManifest` actually model.

## 6. `/dashboard` and `/reports` both stay static — with `/reports` reframed

**Decision:** `/dashboard` stays fully static/mock-derived, unchanged from Phase 9 — no FastAPI calls, explicit Phase 10 boundary. `/reports` also stays static/mock-derived, but its copy is reframed as a "sample report overview" (not a live report history), with cards linking out to the corresponding workflow page for an actual download instead of a disabled button.

**Why over the alternatives:** `/dashboard`'s case was decided first and was straightforward — it aggregates "this session's results" across all three workflows, which needs a shared cross-page store that decision 4 explicitly ruled out; live-wiring it would mean building new architectural surface Phase 10 never asked for. `/reports` surfaced as a *consequence* of that same reasoning, not as one of the four original planning questions — it uses the identical `ReportCard`/`reportManifests` pattern as the dashboard, so the same "no cross-page store" constraint applies to it too. The refinement (reframe copy rather than leave it silently unchanged) came from a direct correction: leaving `/reports` showing `Ready` cards with no live backing risks misleading a viewer into thinking those represent live-generated artifacts, when nothing produced them this session.

## 7. `fastapi[standard]`, not separate `fastapi` + `uvicorn[standard]` + `python-multipart`

**Decision:** `pyproject.toml` declares `fastapi[standard]` as a single dependency.

**Why:** The `[standard]` extra already bundles `uvicorn[standard]`, `python-multipart` (required for `File()`/`Form()` parsing), `httpx`, and `jinja2`. Declaring them separately would be redundant and risks version skew between the pieces. Caught during plan review — the original draft listed all three as separate dependencies.

## 8. `src/` stays framework-free; `backend/uploads.py` is the sole conversion boundary

**Decision:** `src/excel_io.py` and the business modules keep raising their normal pandas/openpyxl/business exceptions exactly as they do for direct/test callers today. No FastAPI import ever enters `src/`. `backend/uploads.py` is the only place that catches those exceptions and converts them to `HTTPException`.

**Why:** This isn't a new rule — it's the existing module-boundary rule (`context/architecture.md`'s System Boundaries table: `src/` "must not own" API/UI concerns) applied explicitly to the new integration point, stated outright in the plan rather than left as an assumed consequence. Making it explicit in the plan text, rather than trusting it to be obvious, was a direct correction during plan review.
