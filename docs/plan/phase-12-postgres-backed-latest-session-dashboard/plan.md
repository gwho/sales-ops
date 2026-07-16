# Plan — Feature phase-12-postgres-backed-latest-session-dashboard: Postgres-Backed Latest-Session Dashboard

## What was built

### Backend — new files

- `backend/db.py` — Postgres connection pool + migration runner. `open_pool()` reads `DATABASE_URL` at call time; returns `None` (persistence disabled, no error) if unset. Runs all pending migrations in one transaction, guarded by `pg_advisory_xact_lock`, with a bounded connection retry (5 attempts, 2.5s backoff) to tolerate Neon cold starts.
- `backend/migrations/0001_create_workflow_results.sql` — DDL for the `workflow_results` table only (no `schema_migrations` bootstrap — that's runner-owned).
- `backend/session.py` — `get_session_id` FastAPI dependency. Parses `X-Session-Id`: absent → `None`, malformed → `HTTPException(400)`, valid → parsed `uuid.UUID`.
- `backend/repositories/workflow_results.py` — `WorkflowResultsRepository` class (`save`, `get_latest`), `DashboardLatestResults` TypedDict, `get_workflow_results_repository` FastAPI dependency provider.
- `backend/persistence.py` — `persist_workflow_result(response, repo, session_id, workflow_type, result)`, the shared write-path glue used by all three workflow routers. Sets `X-Persisted`; never raises.
- `backend/routers/dashboard.py` — `GET /api/dashboard`.

### Backend — modified files

- `backend/main.py` — added `lifespan` context manager (`open_pool()`/`close_pool()`), `app.state.db_pool = None` default (so a bare `TestClient(app)` with no lifespan still works), `X-Persisted` added to CORS `expose_headers`, `dashboard` router registered.
- `backend/routers/orders.py`, `backend/routers/inventory.py`, `backend/routers/payments.py` — each endpoint now takes `session_id`/`repo` dependencies and calls `persist_workflow_result(...)` after computing its result. `inventory.py` persists only `inventory_allocation`, never the internal `validate_orders()` byproduct. The three `.../report` endpoints are unmodified.
- `src/contracts.py` — added `CONTRACT_SCHEMA_VERSIONS: dict[str, int]`.
- `pyproject.toml` — added `psycopg[binary,pool]` dependency; registered the `db` pytest marker.

### Frontend — new files

- `lib/session-id.ts` — `getOrCreateSessionId()`. Browser-only; returns `null` server-side or on storage failure.
- `types/dashboard.ts` — `DashboardLatestResults`, `PersistenceOutcome`.
- `components/feedback/PersistenceNotice.tsx` — the `X-Persisted: false` inline note.
- `components/dashboard/DashboardLiveSections.tsx` — Client Component; fetches `GET /api/dashboard` on mount, resolves each of the three workflow results to live-or-sample independently, renders the Overview row, both chart cards, both tables.

### Frontend — modified files

- `lib/api-client.ts` — `postFormData` attaches `X-Session-Id` via `sessionHeaders()` (omits the header entirely if no ID, never sends an empty string); `postJSON` now returns `{ data, persisted }` instead of the bare result; new `getDashboardResults()`.
- `app/order-validation/page.tsx`, `app/inventory-allocation/page.tsx`, `app/payment-aging/page.tsx` — new `persisted` state, updated `postJSON` call sites (destructure `{ data, persisted }`), render `<PersistenceNotice />` when `persisted === "false"`.
- `app/dashboard/page.tsx` — trimmed to the static shell (header, Reports, Workflow nav cards, "How the Workflows Connect", "How This Demo Works") plus `<DashboardLiveSections />`. No longer imports `orderValidationResult`/`inventoryAllocationResult`/`paymentAgingResult`/`amountByAgingBucket`, `MetricCard`, chart components, `StatusBadge`, or `Table*` components — all moved into `DashboardLiveSections`.
- `components/workflow/MetricCard.tsx` — new optional `sample?: boolean` prop; renders a small `Badge tone="neutral" dot={false}` "Sample data" label when true. Existing call sites unaffected (defaults to `false`).

### Tests — new files

- `tests/test_backend_persistence_routing.py` — 15 tests. Mocks `WorkflowResultsRepository` via `app.dependency_overrides[get_workflow_results_repository]`. Covers: `X-Persisted` for all three outcomes on all three workflow endpoints, `400` on malformed header, that `inventory.py` only ever calls `save()` with `"inventory_allocation"`, that report endpoints never set `X-Persisted`, and all four `GET /api/dashboard` response shapes (absent/malformed/valid/unavailable).
- `tests/test_workflow_results_repository.py` — 8 tests, `@pytest.mark.db`. Real Neon `test` branch via `TEST_DATABASE_URL`. Covers save/read round-trip, upsert-latest-wins + `saved_at` advancing, the `allow_nan=False` guard, schema-version and TTL usability gates, migration idempotency, and checksum-mismatch failure. Skips (doesn't fail) when `TEST_DATABASE_URL` is unset.

### Docs

- `docs/adr/0007-session-scoped-workflow-result-persistence.md` (new).
- `CONTEXT.md` — 5 new terms (Anonymous Session ID, Saved Workflow Result, Workflow Results Store, Persistence Outcome, Dashboard Latest Results, Result Schema Version, Display Expiry — 7 total including the two below), 2 amended terms (Workflow Request, Current Result).
- `docs/archive/phase-11-sql-reporting-sqlite-plan.md` (new) — the paused SQLite plan, archived with a note explaining it was superseded, not completed, by ADR 0007.
- `context/architecture.md`, `context/build-plan.md`, `context/progress-tracker.md`, `context/ui-registry.md`, `CLAUDE.md` — all updated for Phase 12 (see each file's own diff for specifics).
- `.env.example` — added blank `DATABASE_URL`/`TEST_DATABASE_URL` template lines.

## Schema changes

- **`workflow_results`** (new table): `session_id UUID`, `workflow_type TEXT` (CHECK constrained to `order_validation`/`inventory_allocation`/`payment_aging`), `result JSONB`, `result_schema_version INTEGER`, `saved_at TIMESTAMPTZ DEFAULT now()`. `PRIMARY KEY (session_id, workflow_type)`.
- **`schema_migrations`** (new table, created by `backend/db.py`'s `run_migrations`, not by any numbered migration file): `version TEXT PRIMARY KEY`, `checksum TEXT`, `applied_at TIMESTAMPTZ DEFAULT now()`.
- Both tables exist on Neon's `main`, `dev`, and `test` branches (migrations run automatically on every app boot when `DATABASE_URL` is set).

## Key invariants

1. **`CONTRACT_SCHEMA_VERSIONS` (`src/contracts.py`) must be bumped whenever the corresponding Output Contract's field shape changes.** Nothing enforces this automatically — a stale, un-bumped version means an old stored row silently passes the read-path's usability check as "current" and reaches a frontend built for a newer shape.
2. **`schema_migrations` is created and written only by `backend/db.py`'s `run_migrations`.** No migration file under `backend/migrations/` may create or reference it.
3. **A migration file, once applied anywhere, must never be edited.** The checksum check will fail startup on any content change to an already-applied file. A change to behavior requires a new, additional migration file.
4. **The `workflow_results` upsert must always set `saved_at = now()` explicitly inside the `DO UPDATE SET` clause.** The column's `DEFAULT now()` only fires on `INSERT`; omitting it from the update branch would freeze `saved_at` at a row's first-ever save.
5. **`POST /api/*/…/report` endpoints must never read, validate, or persist based on `X-Session-Id`.** This is a deliberate ADR 0006/0007 boundary, not an oversight — report endpoints stay fully stateless.
6. **`POST /api/inventory/allocate` must only ever call `persist_workflow_result(..., "inventory_allocation", ...)`.** It must never also persist the `OrderValidationResult` it computes internally as a dependency of allocation.
7. **The frontend must never send an empty-string `X-Session-Id` header.** `lib/api-client.ts`'s `sessionHeaders()` must omit the header key entirely when no ID is available — an empty string is treated as malformed (`400`) by `get_session_id`, not as absent.
8. **Any code reading the Anonymous Session ID must run in a Client Component, never a Server Component render.** `localStorage` does not exist during a Next.js Server Component's render on Vercel.
9. **`TEST_DATABASE_URL` must never point at the `dev` or `main` Neon branch.** The `@pytest.mark.db` tests run real `INSERT`/`UPDATE`/`DELETE` statements and rely on this variable being scoped to the disposable `test` branch.
10. **`X-Persisted` is set only by `backend/persistence.py`'s `persist_workflow_result`.** Router code must not set this header directly — the shared helper is what guarantees the defensive `try/except` around the repository call.
