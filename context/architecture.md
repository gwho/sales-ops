# Architecture

## Current Target

The active architecture is **Python business logic first, polished Next.js dashboard second**.

The repo is currently a planning/spec workspace. The next implementation should create the Python package, sample data, and tests before scaffolding the Next.js UI.

## Stack

| Layer | Tool | Purpose |
| --- | --- | --- |
| Business logic | Python | Order validation, inventory allocation, payment aging |
| Tabular data | pandas | Spreadsheet-like transformations and calculations |
| Excel I/O | openpyxl | Read/write `.xlsx` reports where pandas alone is insufficient |
| Tests | pytest | Business-rule regression coverage |
| API | FastAPI | Thin HTTP wrapper around tested Python modules |
| Persistence (Phase 12) | Postgres (Neon) via `psycopg` 3 | Session-scoped latest-workflow-result store — see "Persistence" section below |
| Future frontend | Next.js App Router | Polished portfolio dashboard |
| Future UI language | TypeScript strict | Typed UI contracts and components |
| Future styling | Tailwind CSS 3.4 | Token-based styling |
| Future components | shadcn/ui | Dashboard primitives where useful |
| Future tables/charts | TanStack Table, Recharts | Operations tables and simple business charts |

## First Scaffold Shape

```text
/
├── src/
│   ├── __init__.py
│   ├── excel_io.py
│   ├── order_validation.py
│   ├── inventory_allocation.py
│   ├── payment_aging.py
│   ├── report_export.py
│   └── sample_data.py
├── tests/
│   ├── test_order_validation.py
│   ├── test_inventory_allocation.py
│   ├── test_payment_aging.py
│   └── test_report_export.py
├── sample_data/
│   ├── sample_orders.xlsx
│   ├── sample_product_master.xlsx
│   ├── sample_inventory.xlsx
│   └── sample_invoices.xlsx
├── docs/
└── context/
```

## Future Frontend Shape

Plan this after Phase 2 contract fixtures are stable. Build it only after Phases 3-6 pass their test gates:

```text
/
├── app/
│   ├── dashboard/page.tsx
│   ├── order-validation/page.tsx
│   ├── inventory-allocation/page.tsx
│   ├── payment-aging/page.tsx
│   └── reports/page.tsx
├── components/
│   ├── layout/
│   ├── workflow/
│   ├── tables/
│   ├── feedback/
│   └── ui/
├── lib/
│   ├── api-client.ts
│   ├── mock-data.ts
│   └── formatters.ts
└── types/
    └── index.ts
```

## System Boundaries

| Area | Owns | Must not own |
| --- | --- | --- |
| `src/order_validation.py` | Order validation rules and validation result output | UI labels beyond business-readable messages |
| `src/inventory_allocation.py` | Allocation sorting, stock depletion, backorder and supplier follow-up outputs | Excel formatting or React concerns |
| `src/payment_aging.py` | Outstanding amount, aging buckets, follow-up priority, draft reminders | Email sending or accounting-system behavior |
| `src/report_export.py` | Excel workbook generation from result data | Business-rule calculations |
| `src/excel_io.py` | Loading and required-column validation helpers | Workflow-specific rules |
| `tests/` | Regression coverage for business rules | Snapshotting UI |
| `backend/` | FastAPI orchestration over tested modules | Duplicated business logic |
| Future `app/` and `components/` | UI composition and reusable dashboard components | Spreadsheet parsing or business-rule calculations |

## Python Output Contracts

The Python modules should return JSON-serializable structures that can later map cleanly to TypeScript.

Required output families:

- `ValidationSummary`
- `ValidationErrorRow`
- `ValidOrderRow`
- `AllocationSummary`
- `AllocationResultRow`
- `BackorderRow`
- `RemainingInventoryRow`
- `SupplierFollowUpRow`
- `PaymentAgingSummary`
- `PaymentAgingRow`
- `PaymentDataIssueRow` (added by `docs/adr/0005-payment-data-issue-row-contract.md` — the payment-aging Data Issues sheet required by `03_demo_payment_aging.md` PA-006/PA-007 had no matching contract)
- `DraftMessageRow`
- `ReportManifest`

Use snake_case keys in Python. Future TypeScript can either preserve API snake_case or map at the adapter boundary. Do not decide that mapping inside Python modules.

### Field scope boundary

Python owns fields explicitly specified by each workflow spec in `sales_admin_automation_toolkit_specs/`. UI may derive display copy from existing fields, but must not invent new business outcomes. Contracts are allowed to be asymmetric across output families when their specs are asymmetric.

Example: `PaymentAgingRow` includes `suggested_action` because `03_demo_payment_aging.md` §6-7 explicitly defines it as a deterministic output of the aging/priority rules. `AllocationResultRow` does not include `suggested_action` because `02_demo_inventory_allocation.md` never specifies one — allocation's `status`, `backorder_qty`, `warehouse`, and supplier follow-up fields are sufficient, and the future UI can derive display copy from `status` without a new contract field. Do not add a field to a contract for cross-module consistency alone; add it only when the corresponding spec is amended.

## API Contract (Phase 10)

Resolved via a `/grilling` session and `/architect` session before implementation — see `docs/adr/0006-stateless-fastapi-workflow-and-report-exports.md`, `docs/grilling/phase-10-fastapi-integration/`, `docs/architect/phase-10-fastapi-integration/`, and `context/library-docs.md`'s "Future FastAPI" section for full detail.

```text
POST /api/orders/validate
POST /api/orders/validate/report

POST /api/inventory/allocate
POST /api/inventory/allocate/report

POST /api/payments/aging
POST /api/payments/aging/report

GET  /api/templates/{template_name}
GET  /api/dashboard
GET  /health
```

`GET /api/reports/{report_id}` was never implemented — it implied persisted report artifacts, which contradicts the stateless architecture below. Each `.../report` endpoint re-accepts its workflow's source file(s) and recomputes server-side rather than trusting a client-supplied result. `GET /health` (Phase 11) is a minimal liveness check (`{"status": "ok"}`, no database query) added for the deployed backend host's health-check config. `GET /api/dashboard` (Phase 12) is described in the "Persistence" section below.

Backend behavior:

- Process uploaded Excel files in memory only (`backend/uploads.py`); nothing is written to disk or retained after the response.
- Call the tested Python modules in `src/`, never duplicating business rules in route handlers.
- Return JSON matching the stable output contracts for the three workflow endpoints; return `.xlsx` bytes directly for the three report endpoints.
- Convert technical exceptions into business-readable `{"detail": "string"}` responses at the `backend/` boundary — `src/` itself stays framework-free.
- As of Phase 12, the three workflow endpoints (not the `.../report` endpoints) also make a best-effort attempt to persist their result — see "Persistence" below. This is layered on top of the stateless request/response model, not a replacement for it.

## Persistence (Phase 12)

Full design: `docs/adr/0007-session-scoped-workflow-result-persistence.md`. Summary:

- **Anonymous Session ID**: a UUID generated client-side (`crypto.randomUUID()`), stored in `localStorage`, sent as `X-Session-Id` on workflow/report requests (`lib/session-id.ts`, `lib/api-client.ts`). No cookies, no authentication.
- **`workflow_results` table** (Postgres, via `backend/migrations/0001_create_workflow_results.sql`): one JSONB row per `(session_id, workflow_type)`, upserted latest-wins. Holds the verbatim Output Contract JSON, not a parallel SQL schema — `src/contracts.py`'s `CONTRACT_SCHEMA_VERSIONS` guards against stale-shape rows on read.
- **Write path**: `POST /api/orders/validate`, `POST /api/inventory/allocate`, `POST /api/payments/aging` each make a best-effort save after computing their result, reported via the `X-Persisted` response header (`true`/`false`/`skipped`) — never fails the request. `POST /api/inventory/allocate` persists only `inventory_allocation`, never the internal `validate_orders()` byproduct. Report endpoints (`.../report`) are entirely unaffected.
- **Read path**: `GET /api/dashboard` returns the session's latest saved result per workflow type (`null` if none, TTL-expired, or schema-version-stale) — `200` for "nothing saved yet," `503` only for a genuine database outage.
- **Access layer**: `backend/db.py` (migration runner + `psycopg_pool.ConnectionPool`, both skipped cleanly if `DATABASE_URL` is unset), `backend/repositories/workflow_results.py` (the `WorkflowResultsRepository`, injected as a FastAPI dependency), `backend/session.py` (`get_session_id` dependency), `backend/persistence.py` (shared write-path glue).
- **Hosting**: Neon Postgres, three branches — `main` (Render's `DATABASE_URL`, secret), `dev` (local `.env`), `test` (local `.env`'s `TEST_DATABASE_URL`, used only by `@pytest.mark.db` tests, which skip — not fail — when unset).
- **Frontend**: the dashboard's session-aware sections (`components/dashboard/DashboardLiveSections.tsx`) are a Client Component fetching on mount — not a Server Component fetch — since `localStorage` doesn't exist during a Vercel-side render. `app/dashboard/page.tsx` itself stays a Server Component for the static shell.

## Deployment (Phase 11)

Planned via `/grill-with-docs` + `/architect`; see `context/build-plan.md`'s Phase 11 entry for scope and rationale. Two independently hosted services, mirroring the app's existing local dev shape (`localhost:3000` ↔ `127.0.0.1:8000` over CORS) rather than a single container:

| Service | Host | Notes |
| --- | --- | --- |
| Frontend (Next.js) | Vercel, Hobby tier | Zero config — `package.json` sits at repo root, Vercel auto-detects and builds normally alongside the unrelated `backend/`/`src/`/`sample_data/` directories. |
| Backend (FastAPI) | Render, Free Web Service | Python runtime (matches `.python-version`'s `3.12`). Build: `python -m pip install uv && uv sync --frozen --no-dev`. Start: `uv run fastapi run backend/main.py --host 0.0.0.0 --port $PORT`. Health Check Path: `/health`. |

Both are deployed from a dedicated `deploy/portfolio-demo` branch, fast-forwarded from the active implementation branch after each verified change — not `main` (the PR-stack merge decision stays a separate, deferred call) and not an active feature branch (which keeps receiving unrelated WIP).

Env vars, both plain config strings, no secrets involved:

- `NEXT_PUBLIC_API_BASE_URL` (Vercel) — the deployed Render URL. Falls back to `http://127.0.0.1:8000` locally if unset (`lib/api-client.ts`).
- `CORS_ALLOWED_ORIGINS` (Render) — the deployed Vercel URL, comma-separated if more than one origin is ever needed. Falls back to `http://localhost:3000` locally if unset (`backend/main.py`). Read once at app construction (`CORSMiddleware` is configured at `add_middleware()` time, not per-request) — changing this env var on Render requires a redeploy, not just a dashboard save.
- `DATABASE_URL` (Render, Phase 12) — a Neon Postgres connection string, set as a **secret**, not a plain config string like the two above. Unset locally by default; persistence is then cleanly disabled rather than erroring (see "Persistence" section). Render production is expected to always set this.

Deploy sequencing resolves the circular URL dependency: Render first (get its URL) → Vercel with `NEXT_PUBLIC_API_BASE_URL` set to it (get its URL) → `CORS_ALLOWED_ORIGINS` on Render set to the Vercel URL → redeploy Render.

Accepted trade-off: Render's free tier sleeps after ~15 minutes idle; the first request after that can take up to ~1 minute to wake. Mitigated with a `README.md` note, not a keep-alive job or a paid tier — see `README.md`'s "Live Demo" section.

`sample_data/*.xlsx` needs no special deployment packaging — it's already committed and read via paths relative to the repo (`backend/routers/templates.py`, the `load_*` functions), so it's simply present once Render builds from the real repo root.

## UI Design Input Workflow

The folders `ui_reference_to_figma_workflow/` and `ui_prompts_for_agents_mcp/` are guidance inputs, not final product truth.

Use them during UI contract and wireframe planning. This planning may begin after Phase 2 and can run in parallel with Python business-rule implementation.

1. Inspect references or Figma frames through MCP when available.
2. Produce screen inventory, component mapping, data requirements, and scope-control notes.
3. Check that each UI table and KPI maps to a real Python output.
4. Implement polished UI only after all spec-listed Python tests and Excel report structure tests pass.

If Figma MCP is unavailable, use screenshots and written specs as fallback.

## Scope Gate

Use this mechanical rule before implementing any spec item:

- Implement only rules from in-scope spec files that are labeled V1 or not labeled with a version.
- Do not implement any rule explicitly marked `Optional`, `V1.5`, or `V2` without a new ADR reopening scope.
- Do not implement `sales_admin_automation_toolkit_specs/04_optional_crm_cleaner.md` without a new ADR. The whole CRM Cleaner module is outside the active build even though it has detailed specs.
- Do not implement adjacent enterprise features just because they are small or easy. Ease of implementation is not enough to move a feature into scope.

Concrete examples:

- `02_demo_inventory_allocation.md` Rule IA-007 V1 warehouse choice is in scope: allocate from the warehouse with the highest available quantity for that SKU.
- `02_demo_inventory_allocation.md` Rule IA-007 Optional V2 region-matching preference is out of scope until an ADR explicitly adds it.
- `04_optional_crm_cleaner.md` is out of scope in full until an ADR explicitly adds it.

## V1 vs V2

In this repo:

- **V1** means the active portfolio build: Python-first Excel automation for order validation, inventory allocation, payment aging, and report export, followed by a polished Next.js presentation layer only after test gates pass.
- **V1.5** means a small candidate extension that may be useful after V1 is complete, but is not part of the current build.
- **V2** means deliberately postponed expansion work. It may be reasonable later, but it must not be implemented during V1 without an ADR.

V1/V2 labels are still necessary because the specs intentionally contain future ideas beside current rules. The labels stop future agents from treating every nearby idea as approved scope.

## Non-Goals for V1

- Authentication or user accounts
- Database persistence beyond the narrow, anonymous, latest-result-only Workflow Results Store added in Phase 12 (see "Persistence" above) — no history, no cross-session analytics, no accounts
- Role-based permissions
- Production file storage
- Realtime collaboration
- AI forecasting or risk scoring
- Email sending
- Real customer, employer, supplier, order, invoice, or product data
- Full ERP/accounting/WMS/CRM replacement
