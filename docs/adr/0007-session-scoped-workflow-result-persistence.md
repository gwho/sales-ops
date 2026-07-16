# ADR 0007 - Session-Scoped Workflow Result Persistence in Postgres

## Status

Accepted

## Context

`context/build-plan.md` and `memory.md` both point at a "future Postgres-backed dashboard phase" as the intended successor to the paused SQLite "Demo Reporting Database" work (`git stash@{0}`). That stash was never followed by an ADR — the `0007` filename slot was referenced only as a forward pointer in code comments and was never written. This ADR fills that slot with the design this phase implements, which supersedes the stashed direction rather than completing it: the stashed work was a disposable, rebuilt-from-sample-data SQLite store for SQL-driven demo reporting across a fixed dataset; this phase is real, session-specific persistence of live visitor results, with a materially different storage shape (a single JSONB latest-result table, not normalized per-row SQL-reporting tables). The stash is not reused and remains untouched.

ADR 0006 established that the three workflow endpoints (`validate`, `allocate`, `aging`) and their `.../report` counterparts are fully stateless — each request processed and forgotten. This ADR amends that for the three JSON-returning workflow endpoints only. Report endpoints are explicitly unchanged (see Decision).

## Decision

### Session identity

An Anonymous Session ID is a UUID generated once in the browser via `crypto.randomUUID()`, stored in `localStorage`, and sent as the `X-Session-Id` header by `lib/api-client.ts` on every workflow and report request. No cookies are used. This carries no authentication — it identifies a browser profile only, chosen specifically because Vercel (frontend) and Render (backend) are separate origins, and a cross-site cookie would require `SameSite=None; Secure`, `allow_credentials=True` on CORS, and `credentials: 'include'` on every fetch — meaningful complexity this anonymous-only use case doesn't need.

A shared FastAPI dependency (`get_session_id`) is the single place `X-Session-Id` is parsed, using Python's `uuid.UUID(value)` constructor as the sole validity predicate (any RFC4122 version, not narrowed to v4). It returns `None` if the header is absent, raises `HTTPException(400)` if present but unparseable, and otherwise returns the parsed `uuid.UUID` object — never the raw string — which is what every query binds, so normalization happens once and Postgres's native `UUID` column type provides a second, independent layer of canonicalization. This same dependency backs both the write-path endpoints and `GET /api/dashboard`, so "malformed" means exactly one thing everywhere.

The frontend must **omit** the `X-Session-Id` header entirely when no ID is available yet — never send `X-Session-Id: ""`. `lib/session-id.ts` always returns a valid UUID once called (creating one on first use if absent), but `lib/api-client.ts` must attach the header conditionally regardless, since an empty string is not the same as an absent header server-side: `get_session_id` sees a present-but-unparseable value and returns `400`, not the `skipped` behavior intended for "no identity yet."

### Write path (the three workflow endpoints only)

Persistence is a side effect folded directly into `POST /api/orders/validate`, `POST /api/inventory/allocate`, `POST /api/payments/aging` — not a separate save endpoint. A separate endpoint would have to either trust a client-resubmitted result (violating the "never trust client-supplied result" principle ADR 0006 already established for report exports) or force a redundant third file re-upload. Behavior:

| `X-Session-Id` | Computation | Response |
|---|---|---|
| Absent | Runs normally | `200`, result body, `X-Persisted: skipped` |
| Malformed | Not attempted | `400`, before any file processing |
| Valid, save succeeds | Runs normally | `200`, result body, `X-Persisted: true` |
| Valid, save fails (DB hiccup) | Runs normally | `200`, result body, `X-Persisted: false` |

Persistence failure never fails the request: the business computation is the deliverable being demoed and has already succeeded before the DB write is attempted, and Neon/Render free-tier cold starts or transient connection issues are exactly the kind of ancillary infra hiccup that shouldn't turn a valid uploaded spreadsheet into a `500`. But the outcome is always reported via `X-Persisted`, never silent — a `200` must not look identical whether the save landed or not. `X-Persisted` is added to `backend/main.py`'s CORS `expose_headers` (alongside `Content-Disposition`/`X-Report-Id`/`X-Generated-At`), the same cross-origin gotcha already caught once during the Phase 10 plan review. The write attempt runs with its own short timeout so a hanging connection can never stall an already-successful response; every failed save is logged server-side with session ID and workflow type.

`POST /api/inventory/allocate` internally calls `validate_orders()` to obtain valid orders before allocating — this produces a complete `OrderValidationResult` as a byproduct, but it is **never persisted**. Only `inventory_allocation` is saved for that request. The internal validation is a business-rule dependency (only valid orders can be allocated), not a workflow the user invoked or even received in the response body — persisting it would silently populate the dashboard's Order Validation section from a page the user never visited, and would require `X-Persisted` to report two independent outcomes with no contract for the second. A session that only ever runs Inventory Allocation will show sample data in Order Validation indefinitely; that's the honest state, matching what the sample-data chip already means elsewhere ("you haven't run this workflow").

### Report endpoints are entirely unchanged

`POST .../report` (all three) remain exactly as ADR 0006 specified: stateless, recompute-and-forget, no `X-Session-Id` reading or validation, no persistence, no `X-Persisted` header. A report download is an export of an answer already obtained (typically moments after the workflow endpoint already best-effort-saved the identical result) — writing to storage on every download would refresh a timestamp for zero new information. `lib/api-client.ts` may still attach `X-Session-Id` on report calls for consistency; the backend simply ignores it there.

### Storage shape

One table, storing the verbatim Output Contract JSON — not a second, parallel SQL schema mirroring `src/contracts.py`'s fields (that would recreate the exact schema-drift risk `src/contracts.py`'s own Field Scope Boundary discipline exists to prevent):

```sql
CREATE TABLE workflow_results (
  session_id UUID NOT NULL,
  workflow_type TEXT NOT NULL,
  result JSONB NOT NULL,
  result_schema_version INTEGER NOT NULL,
  saved_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (session_id, workflow_type),
  CHECK (workflow_type IN ('order_validation', 'inventory_allocation', 'payment_aging'))
);
```

Upsert-latest via:

```sql
INSERT INTO workflow_results (session_id, workflow_type, result, result_schema_version, saved_at)
VALUES (%(session_id)s, %(workflow_type)s, %(result)s, %(schema_version)s, now())
ON CONFLICT (session_id, workflow_type) DO UPDATE
SET result = EXCLUDED.result,
    result_schema_version = EXCLUDED.result_schema_version,
    saved_at = now();
```

**`saved_at = now()` must be explicit in the `DO UPDATE SET` clause, not left to a column `DEFAULT`** — a `DEFAULT now()` only fires on `INSERT`. Without repeating it on the update branch, a returning visitor's genuinely fresh save would keep the *original* `saved_at` from their first-ever run, and Display Expiry would measure age from that first save — silently expiring an actively-used session's latest result. Correctness requirement, not a style preference.

At most 3 rows per Anonymous Session ID, ever — growth tracks unique visitors, not re-runs. Concurrent double-submission of the same workflow from the same session (e.g. two browser tabs submitting at once) is benign under this upsert: last commit wins, no error, no duplicate rows.

Before writing, the result is serialized with `json.dumps(..., allow_nan=False)`. Postgres's `JSONB` type rejects `NaN`/`Infinity`, but plain `json.dumps` emits them by default and pandas produces them easily (e.g. a genuinely missing numeric field). `allow_nan=False` makes that fail loudly inside the already-caught, already-best-effort save attempt — surfacing as an ordinary `X-Persisted: false` for that one request — rather than silently and permanently failing to persist that session forever with no diagnostic trail.

`result_schema_version` is a small constant dict living in `src/contracts.py` itself (next to the TypedDicts it versions), not a separate file — **any change to a persisted Output Contract's field shape must bump its version**, on the same mental checklist as editing the contract. A version mismatch on read is treated exactly like a missing row (see Read path). Without this discipline the mechanism is inert: an added field on an old stored row would silently pass as "current" and reach a frontend expecting the new shape.

**Payment aging results are as-of-date snapshots.** `POST /api/payments/aging` takes `as_of_date` as input, so a `Saved Workflow Result` for payment aging is frozen as of whatever date the user chose at run time — aging buckets in that saved result do not advance as real time passes. This is correct (a saved result is a snapshot by definition) but non-obvious to a future reader wondering why a dashboard revisited a week later shows unchanged aging buckets.

### Access layer

`psycopg` 3, hand-written parameterized SQL, no ORM — consistent with the project's existing "no ORM" precedent from the paused SQLite work, and appropriate for one table and two real queries (upsert, select-by-key). Routes are sync `def` (confirmed: none of `orders.py`/`inventory.py`/`payments.py` are `async def`, since the pandas/openpyxl business logic underneath is synchronous) — so a sync driver with a sync connection pool (`psycopg_pool.ConnectionPool`) matches, with no async/sync mismatch. The pool is opened once in the FastAPI lifespan hook (not at import time) and stored on `app.state`; each repository operation borrows one connection via a context manager for explicit commit/rollback. A deliberately small pool size, appropriate for Render's free-tier service. All DB access stays inside `backend/`; `src/` remains framework- and DB-free (only the `result_schema_version` constants live there, as plain data).

The repository (`save_workflow_result` / `get_latest_results`) is exposed as a FastAPI dependency, not called as a bare module-level function — the same idiom as `get_session_id`. This lets route-orchestration tests override it via `app.dependency_overrides` instead of monkeypatching a module global, and keeps the injection style consistent across the one new subsystem.

### Migrations

Hand-written, ordered SQL migration files (no Alembic — not justified at one-table scale), applied automatically in the FastAPI lifespan startup hook, before the request-serving pool opens. The whole batch runs as **one transaction**, not one transaction per file:

1. Open a single admin-connection transaction and acquire a fixed `pg_advisory_xact_lock` at its start (transaction-scoped — released automatically on commit or rollback, so it can't outlive the batch or leak across a crashed startup).
2. Inside that same transaction, ensure `schema_migrations` exists. **`schema_migrations` is owned by the runner, not by any migration file** — it is never created by `0001_create_workflow_results.sql` or any other versioned file, keeping migration bookkeeping separate from application schema.
3. Read applied migration versions and checksums.
4. Apply every not-yet-applied migration file in order, recording each version + checksum, all still inside the one transaction.
5. If an already-applied file's checksum has changed, **fail startup** (roll back, never silently re-apply or ignore a changed migration).
6. If any migration fails, roll back the whole batch and fail startup — do not serve traffic.
7. Commit once, only after every pending file has applied cleanly. Only then does the normal serving `ConnectionPool` open.

Single-transaction batching closes a gap a per-file-transaction design would have: `pg_advisory_xact_lock` only lives as long as its transaction, so locking per file would let another process interleave between files during a deploy. Caveat, acceptable at this project's one-table scale: batching means one long-held lock and transaction for the whole batch, worth revisiting if migrations ever become numerous, slow, or non-transactional (e.g. `CREATE INDEX CONCURRENTLY`, which cannot run inside a transaction at all) — not a concern for the single migration Phase 12 ships with.

**If `DATABASE_URL` is unset, migrations are skipped entirely and no pool is opened** — see "Missing `DATABASE_URL`" under Read path; this is what keeps the app, and the test suite running against it, hermetic on a fresh clone.

This runs identically in local dev (`uv run fastapi dev` against the Neon `dev` branch) and in Render production — no Render-specific Pre-Deploy Command, preserving this project's existing local/production symmetry. Render production **must** set `DATABASE_URL`; this is a deploy invariant, not optional configuration.

### Read path

`GET /api/dashboard` reads the same `get_session_id` dependency (absent → all three fields `null`; malformed → `400` before any DB work, same rule as the write path). For a valid ID, it queries up to three rows and returns:

```ts
type DashboardLatestResults = {
  order_validation: OrderValidationResult | null;
  inventory_allocation: InventoryAllocationResult | null;
  payment_aging: PaymentAgingResult | null;
};
```

This envelope type lives with the backend's dashboard module, **not** `src/contracts.py` — the three values inside are verbatim Output Contracts; the wrapper around them is a dashboard-read aggregate, not a spec-derived contract, the same boundary the paused SQLite design already drew.

For a valid ID, the query fetches at most 3 rows by `session_id` alone — no `WHERE` on version or TTL, since the current schema version is Python-side data (`CONTRACT_SCHEMA_VERSIONS` in `src/contracts.py`), not something SQL can compare against directly. Each fetched row is then run through one shared `is_usable(row)` Python predicate inside `get_latest_results`, checking **both**:
- `result_schema_version` matches the current version for that workflow type, and
- `saved_at` is within a TTL (backend constant/env value, default 30 days).

A row failing either check resolves to `null` through that same predicate — the dashboard never learns *why* a workflow came back `null`, only falls back to sample data for that section independently. TTL enforcement is **display expiry, not deletion**: a stale row is not physically removed, only excluded from what the predicate accepts.

**Two distinct `GET /api/dashboard` outcomes must not be conflated:**
- No usable rows for a session (none ever saved, all TTL-expired, all version-mismatched) is a normal, expected state → `200`, all three fields `null` → per-section sample fallback + "Sample data" chip, exactly as above.
- The database genuinely being unreachable (a live connection/query attempt fails) is a different, real failure → `503`, and the frontend renders the existing `BusinessErrorMessage` rather than silently showing sample data as if nothing were saved. Deliberate tradeoff: it would sit closer to the "dashboard is never broken or empty" ethos to show sample data either way, but conflating "the database is down" with "you haven't run anything yet" is dishonest to a viewer trying to understand the app, and hides a real operational problem. `BusinessErrorMessage`'s copy for this case should invite a retry (e.g. reload), not imply the whole demo is broken.

**Missing `DATABASE_URL` is a third, separate case — not a `503`.** If `DATABASE_URL` is unset at startup, persistence is intentionally disabled for that run: migrations are skipped, no pool is opened, and this is not treated as an outage.
- Workflow endpoints still compute and return results normally; a valid `X-Session-Id` gets `X-Persisted: false` (the save was genuinely not attempted, so `false` is accurate — no separate header value needed for this case).
- `GET /api/dashboard` returns `200` with all three fields `null` (→ full sample fallback) — the same shape as "no usable rows," since the read path has no configured database to be down in the first place.
- This is what lets the app, and `TestClient`-driven route-orchestration tests (which exercise the same lifespan hook), boot and run cleanly with zero configuration on a fresh clone. Render production is still required to set `DATABASE_URL` regardless — this fallback exists for local/test hermeticity, not as a supported production mode.

**A third, distinct state: `DATABASE_URL` set but unreachable at boot.** This is not the runtime `503` case (that requires the app to have finished starting) and not the unset case above — it falls under the Migrations section's existing "if any migration fails, fail startup and do not serve traffic" rule, since the migration step's own initial connection attempt is what fails. Given Neon free-tier compute can cold-start after inactivity (the same class of cold-start latency already accepted for Render's free-tier backend in the Phase 11 deployment), a bare all-or-nothing fail on the first connection attempt would be needlessly brittle against ordinary, recoverable cold-start delay. The migration runner's initial admin connection therefore retries with a short bounded backoff (a handful of attempts over roughly 10-15 seconds) before treating the database as genuinely unreachable and failing startup. A database still unreachable after that window is a real failure, and fail-closed startup remains correct — this is a tolerance window for expected latency, not a general retry-forever policy. This window must stay comfortably under Render's own service start/health-check timeout, so an ordinary slow cold start reads as "still booting" to Render rather than tripping a deploy failure on top of the retry itself.

If Neon storage ever becomes a real concern, the designated no-new-infrastructure upgrade is opportunistic deletion piggybacked on the write path (`DELETE ... WHERE saved_at < now() - <TTL>` in the same transaction as the upsert) — not a cron job or scheduled worker. Not built in Phase 12; the bounded-per-session row count means it isn't solving a problem that exists yet.

### Frontend read boundary — coupled to the session-identity decision

Because Anonymous Session ID lives only in `localStorage`, a Next.js Server Component's render-time fetch (which runs on Vercel's server) has no way to read it and no automatic cookie to carry it — it would always call `GET /api/dashboard` with no session header and see the all-`null` case, even for a visitor with real saved results. This is not a separate design choice; it is a direct consequence of the `localStorage`-over-cookies decision:

- `app/dashboard/page.tsx` stays a Server Component, rendering only the static shell (nav cards, "How the Workflows Connect" infographic, "How This Demo Works" copy, Reports overview) — none of that needs session identity.
- A new Client Component, `components/dashboard/DashboardLiveSections.tsx`, owns everything that does: it reads/creates the Anonymous Session ID on mount, fetches `GET /api/dashboard`, and — independently per workflow — uses the live result if present or the existing static `mock-data.ts` import if not.
- First paint is a loading skeleton (reusing the existing `LoadingState` component), not sample-then-swap — showing sample values immediately and replacing them on fetch return would cause a visible content flash and blur "is this real or sample?" A failed `GET /api/dashboard` itself renders via the existing `BusinessErrorMessage`, matching the three workflow pages' pattern.
- Any section resolved from the static sample fallback shows the existing "Sample data" chip — confirms which sections are the visitor's own vs. seeded demo content, important for a hiring-manager viewer to be able to tell the difference.
- The old "async Server Component with `force-dynamic`" framing from the *paused, superseded* Phase 11 SQLite plan is retired — it assumed a global, non-session-scoped dashboard query, which is no longer the design. Anywhere that assumption is still written down (old plan file, stale docs) should be corrected, not carried forward.

### Write-side UI surfacing

`X-Persisted` is surfaced only when actionable, matching this project's existing convention (no success toasts exist anywhere today; status elements appear only when there's something to act on):

- `true` or `skipped` → no new UI; the workflow result renders exactly as it does today.
- `false` → a small, non-blocking inline note near the result (not `BusinessErrorMessage` — this is a caveat, not an error, and the result the user came for is completely fine): *"Result calculated, but it wasn't saved to the dashboard. The dashboard may still show your last saved result. Run again to retry saving."* New component: `components/feedback/PersistenceNotice.tsx`, token-compliant, not styled as an alert.

In practice `skipped` is close to unreachable from the real frontend (the real client always attaches the header once `lib/session-id.ts` exists) — it's the curl/Swagger/cleared-storage path. `false` is the only outcome a real user is likely to ever see, which is exactly the "appears only when actionable" shape intended. Feature discoverability (the fact that runs feed the dashboard at all) lives in the dashboard's own "How This Demo Works" copy, not in per-run success chrome on the three workflow pages.

### Testing and environments

Neon branching: `main` (production, Render's `DATABASE_URL`), `dev` (local development, local `.env`'s `DATABASE_URL`), `test` (automated `pytest` persistence tests, its own **`TEST_DATABASE_URL`** — deliberately a separate env var from `DATABASE_URL`, not a reused/overloaded one, so a misconfigured or copy-pasted environment can never point a cleanup/rollback-driven test at the `dev` or `main` branch by accident). The suite is now two layers:

- **Route-orchestration tests** (existing `tests/test_backend_{orders,inventory,payments}.py`, extended) — mock the repository layer via `app.dependency_overrides`. Verify control flow only: `400` on malformed header, `X-Persisted: skipped` on absent header, `X-Persisted: true`/`false` depending on a stubbed repo call succeeding or raising, and that a raising repo call still returns `200` with the full result. Fast, offline, no real Postgres touched — and now guaranteed to run even with no `DATABASE_URL` at all, since the lifespan hook itself no longer requires it (see Read path's "Missing `DATABASE_URL`" case).
- **Repository/SQL integration tests** (new, `tests/test_workflow_results_repository.py` or similar) — real Neon `test` branch via `TEST_DATABASE_URL`. Cover the upsert/`ON CONFLICT` semantics (including the `saved_at`-on-update requirement), JSONB round-tripping (including the `allow_nan=False` guard), `result_schema_version` and TTL usability-gate logic, migration application, checksum-mismatch failure, and the advisory lock. Marked `@pytest.mark.db`, **skipped (not failed) when `TEST_DATABASE_URL` is unset**, so `uv run pytest` on a fresh clone stays fully hermetic and green with zero external services and zero configuration — exactly as it is today. Isolation is rollback-first (wrap each test in a transaction rolled back in teardown); the migration/advisory-lock tests, which manage their own transactions, fall back to UUID-scoped rows and explicit cleanup instead. Tests never target the `main` (production) branch, and cannot even by accident given the separate env var.

Docker Postgres was considered and rejected: it would add infrastructure this project has never needed, and since Neon is already Postgres, Docker buys no additional SQL-correctness confidence over the `test` branch — only provider-parity concerns (SSL, pooling, cold starts) that a deploy-time smoke check covers better than a unit suite would anyway.

## Consequences

- The three workflow endpoints are no longer purely stateless in the ADR 0006 sense — they now make a best-effort attempt at a narrow, latest-only, session-scoped side effect. Computation itself remains pure and unchanged; only a best-effort persistence step is added after it. Report endpoints, and the computation logic in `src/`, remain exactly as stateless as ADR 0006 originally specified.
- `GET /api/dashboard` returning `503` on a genuine database outage (rather than quietly falling back to sample data like the "nothing saved yet" case does) is a deliberate departure from "the dashboard is never broken or empty" — chosen because silently presenting sample data as if it were simply "no session results" during a real outage would misrepresent what's happening. `DATABASE_URL` being unset entirely is explicitly not this case (see Decision) and still resolves to a clean `200` all-sample response.
- This is the first genuinely persistent, non-disposable data store in the project (distinct from the disposable, rebuilt-every-startup "Demo Reporting Database" concept from the paused SQLite work) and the first external network dependency (Neon) the backend has beyond its own process.
- No user-facing history, audit trail, or multi-run comparison is introduced — only "latest," per session, per workflow type. Anything beyond that (real history, cross-session analytics, authenticated accounts) is new scope requiring its own ADR.
- Saved results are hidden after their TTL but not deleted — this is a display rule, not a privacy/deletion guarantee, and must be described that way in any user-facing or documentation copy.
- The paused SQLite stash (`stash@{0}`) is now formally superseded for dashboard purposes; its fate (delete vs. keep as unrelated historical reference) remains an open question, unaffected by this ADR.
