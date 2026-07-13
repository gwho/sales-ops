# Phase 12: Postgres-Backed Latest-Session Dashboard

## Context

The dashboard (`app/dashboard/page.tsx`) has been a static showcase since Phase 9 — every KPI, chart, and table reads from build-time-generated mock JSON (`lib/mock-data/*.json`, derived from `sample_data/*.xlsx`), never from anything a visitor actually does. Phase 10 made the three workflow pages (order validation, inventory allocation, payment aging) genuinely live against a stateless FastAPI backend (ADR 0006), but a visitor's real result vanishes the moment they navigate away — there was never a way for the dashboard to reflect what someone actually ran.

An earlier attempt at fixing this (the paused "Phase 11: SQL Reporting" work, preserved in `git stash@{0}`) took a different shape: a disposable SQLite database rebuilt from the same fixed `sample_data/*.xlsx` seed on every startup, purely for SQL-driven *demo* reporting — never session-specific, never real visitor data. That work was paused in favor of shipping the deployment baseline first, with an explicit note that it might inform "a future Postgres-backed dashboard phase." This plan is that phase, but it does not reuse the stashed design: this is genuinely session-specific persistence of real computed results, not a reseeded demo database, and the storage shape (JSONB latest-result store, not normalized SQL-reporting tables) is deliberately different. The stash remains untouched, unreferenced, historical.

Intended outcome: a visitor who runs one or more of the three workflows sees their own latest results reflected on the dashboard on their next visit (same browser), with any workflow they haven't run yet still showing today's sample data — never a broken or empty section.

This plan is the output of an extensive `/grilling` session (13 resolved decision points, recorded in full in the conversation transcript) plus a `/domain-modeling` pass. It should be read together with **ADR 0007** and the **CONTEXT.md amendments** below, which this plan creates/applies as its first implementation step.

## Architecture Decisions (ADR 0007 — to be written to `docs/adr/0007-session-scoped-workflow-result-persistence.md`)

```markdown
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
- Any section resolved from the static sample fallback shows the existing "Sample data" chip (from Q7/domain discussion — confirms which sections are the visitor's own vs. seeded demo content, important for a hiring-manager viewer to be able to tell the difference).
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
- `GET /api/dashboard` returning `503` on a genuine database outage (rather than quietly falling back to sample data like the "nothing saved yet" case does) is a deliberate departure from "the dashboard is never broken or empty" — chosen because silently presenting sample data as if it were simply "no session results" during a real outage would misrepresent what's happening. `DATABASE_URL` being unset entirely is explicitly not this case (see ADR body) and still resolves to a clean `200` all-sample response.
- This is the first genuinely persistent, non-disposable data store in the project (distinct from the disposable, rebuilt-every-startup "Demo Reporting Database" concept from the paused SQLite work) and the first external network dependency (Neon) the backend has beyond its own process.
- No user-facing history, audit trail, or multi-run comparison is introduced — only "latest," per session, per workflow type. Anything beyond that (real history, cross-session analytics, authenticated accounts) is new scope requiring its own ADR.
- Saved results are hidden after their TTL but not deleted — this is a display rule, not a privacy/deletion guarantee, and must be described that way in any user-facing or documentation copy.
- The paused SQLite stash (`stash@{0}`) is now formally superseded for dashboard purposes; its fate (delete vs. keep as unrelated historical reference) remains an open question, unaffected by this ADR.
```

## CONTEXT.md amendments

Add these terms (alphabetized into the existing list at implementation time):

```markdown
### Anonymous Session ID

A UUID generated once in the browser via `crypto.randomUUID()` and stored in `localStorage`, sent as the `X-Session-Id` header on Workflow Requests and Report Export Requests. It identifies a browser profile only — no authentication, no user account, nothing server-side treats it as a login. Clearing browser storage creates a new, unrelated Anonymous Session ID.
_Avoid_: User ID, Account ID — these imply authenticated identity, which this project does not have.

### Saved Workflow Result

The most recent Workflow Result for a given Anonymous Session ID and workflow type, persisted to Postgres as a best-effort side effect of a Workflow Request. Saving a new one for the same session and workflow type overwrites the previous one — there is no history, only the latest.
_Avoid_: Workflow Run, Run History — these imply a persisted, browsable sequence of past requests, which this project does not keep.

### Workflow Results Store

The single Postgres table (`workflow_results`) holding every session's Saved Workflow Results, keyed by (Anonymous Session ID, workflow type). Unlike the Demo Reporting Database, it is not rebuilt from `sample_data/*.xlsx` on startup — it holds real, session-specific results from real Workflow Requests, and is the first genuinely persistent, non-disposable data store in this project.
_Avoid_: Demo Reporting Database — that term names a different, disposable, SQLite-based concept from the paused Phase 11 SQL-reporting design, not this one.

### Persistence Outcome

The `X-Persisted` response header on a Workflow Request, reporting whether the Workflow Result was saved as that session's Saved Workflow Result: `true` (saved), `false` (a valid Anonymous Session ID was supplied but the save failed — a transient infrastructure issue, not a data problem), or `skipped` (no Anonymous Session ID was supplied — standalone API use). It never appears on Report Export Request responses, which never persist.

### Dashboard Latest Results

The response shape of `GET /api/dashboard`: one field per workflow type, each either that session's Saved Workflow Result or `null` if none exists, is TTL-expired, or is Result Schema Version-incompatible. A dashboard-module aggregate type, not an Output Contract — it lives in the backend's dashboard module, not `src/contracts.py`, since Field Scope Boundary governs spec-derived contracts, not read-side aggregates over them.

### Result Schema Version

An integer stored alongside every Saved Workflow Result, identifying which version of its workflow type's Output Contract shape it was saved under. Bumped whenever a persisted Output Contract's fields change — the same mental checklist as editing `src/contracts.py` itself. `GET /api/dashboard` treats a stored result with a non-current version as unusable, the same as if it didn't exist.

### Display Expiry

The rule that a Saved Workflow Result older than a fixed TTL (default 30 days) is treated as unusable by `GET /api/dashboard` — the same as a missing or Result Schema Version-incompatible result — even though the row is not physically deleted. A visibility rule, not a data-deletion guarantee; physical cleanup is deferred out of Phase 12 scope.
```

Amend two existing terms:

- **Workflow Request** — the sentence "It carries no server-side identity — the server processes it against the corresponding tested Python module and forgets it once the response is returned" becomes: "The server always processes it against the corresponding tested Python module and returns its result the same way regardless of session identity — computation itself remains stateless and pure. As of Phase 12, if the request carries a valid Anonymous Session ID, the server also makes a best-effort attempt to persist the result as that session's Saved Workflow Result, reported via the `X-Persisted` header — a side effect, not a change to how the result is computed or returned." Update the `_Avoid_` line's reasoning to reference "a single best-effort latest-result save, never a history, retry queue, or resumable job" instead of "Phase 10 deliberately does not introduce."
- **Current Result** — append: "Independent from this, Phase 12 may also produce a Saved Workflow Result for the same request — a separate, best-effort, server-side latest-result cache for dashboard display. It does not change what Current Result means: purely client-side, ephemeral, discarded on navigation."

## Implementation

### Database (Neon)

1. Create the Neon project (or confirm existing) with three branches: `main`, `dev`, `test`. Record connection strings — `main`'s goes into Render's environment as `DATABASE_URL`, a secret only; `dev`'s goes into a local `.env` as `DATABASE_URL`; `test`'s goes into a local `.env` (and any future CI config) as `TEST_DATABASE_URL`. Neither local var is committed — `.env.example` gets new blank `DATABASE_URL=` and `TEST_DATABASE_URL=` lines, following the existing `!.env.example` negation pattern in `.gitignore`.
2. `backend/migrations/0001_create_workflow_results.sql` — **only** the `workflow_results` DDL from ADR 0007. `schema_migrations` is never created here — it's owned exclusively by the runner (step 3).
3. `backend/db.py` (new) — `run_migrations(admin_conn)` (single transaction: advisory lock → ensure `schema_migrations` → checksum-verify applied entries → apply pending files in order → commit once, or roll back the whole batch on any failure) and `open_pool() -> ConnectionPool | None` (returns `None`, skipping migrations entirely, when `DATABASE_URL` is unset). Both called from `backend/main.py`'s lifespan.

### Backend

4. `pyproject.toml` — add via `uv add "psycopg[binary,pool]"` (quoted — unquoted brackets are interpreted by the shell).
5. `src/contracts.py` — add a small `CONTRACT_SCHEMA_VERSIONS` dict (`order_validation`, `inventory_allocation`, `payment_aging` → current int versions), colocated with the TypedDicts it governs.
6. `backend/session.py` (new) — `get_session_id` FastAPI dependency, per ADR 0007 (absent → `None`; malformed, including empty string → `400`; valid → parsed `uuid.UUID`).
7. `backend/repositories/workflow_results.py` (new) — `save_workflow_result(pool, session_id, workflow_type, result, schema_version) -> bool` (best-effort: serializes with `json.dumps(..., allow_nan=False)`, catches/logs any failure including a `None` pool from missing `DATABASE_URL`, never raises to the caller) and `get_latest_results(pool, session_id) -> DashboardLatestResults | Literal["unavailable"]` (fetches ≤3 rows by `session_id`, applies the shared `is_usable(row)` schema-version + TTL predicate in Python, distinguishes "no usable rows" from "query genuinely failed" for the 503 case, and returns an all-`null` envelope directly — without querying — when the pool is `None`). Exposed as a FastAPI dependency (`app.dependency_overrides`-friendly), not a bare module function.
8. `backend/routers/orders.py`, `inventory.py`, `payments.py` — inject `get_session_id` and the repository dependency, call `save_workflow_result` after computing each result, set `X-Persisted` via an injected `Response` param. `inventory.py`'s `_run_allocation` persists only `inventory_allocation`, never the internal validation byproduct. The three `.../report` handlers are untouched.
9. `backend/routers/dashboard.py` (new) — `GET /api/dashboard`: `200` + all-`null`/partial-live envelope for "no usable rows" or "no `DATABASE_URL`", `503` for a genuine query/connection failure, per ADR 0007's read path.
10. `backend/main.py` — add the `lifespan` context manager (skip-if-no-`DATABASE_URL`-else-migrate → open pool or `None` → store on `app.state` → close on shutdown if opened), register the new dashboard router, add `X-Persisted` to `expose_headers`.

### Frontend

11. `lib/session-id.ts` (new) — `getOrCreateSessionId()`, `localStorage` + `crypto.randomUUID()`, browser-only, always returns a non-empty string once called.
12. `lib/api-client.ts` — attach `X-Session-Id` **conditionally** (omit the header entirely if no ID string is available — never send an empty-string header) on every workflow/report call; add a JSON-GET helper for `/api/dashboard` that also surfaces a `503` distinctly from a parsed body; surface the `X-Persisted` response header alongside the parsed body (not folded into it).
13. `types/dashboard.ts` (new) — `DashboardLatestResults`, `PersistenceOutcome` (`"true" | "false" | "skipped"`).
14. `components/feedback/PersistenceNotice.tsx` (new) — the non-blocking `X-Persisted: false` note, token-compliant per `context/ui-tokens.md`.
15. `app/order-validation/page.tsx`, `inventory-allocation/page.tsx`, `payment-aging/page.tsx` — render `PersistenceNotice` only when `X-Persisted === "false"`.
16. `components/dashboard/DashboardLiveSections.tsx` (new, Client Component) — session id on mount, fetch `/api/dashboard`, per-workflow live-or-sample resolution, loading skeleton via existing `LoadingState`, error via existing `BusinessErrorMessage`, "Sample data" chip per fallback section. Migrate the existing derivation logic (`orderValidationResult.summary`, `supplier_follow_ups`, `aging_rows` filtering, `amountByAgingBucket`, etc.) from `app/dashboard/page.tsx` into this component largely unchanged — only the source of the three top-level values changes.
17. `app/dashboard/page.tsx` — trim to the static shell (nav cards, infographic, guide copy, Reports section) plus `<DashboardLiveSections />`.

### Docs (after implementation, not before)

18. `context/architecture.md`, `context/build-plan.md` (new Phase 12 section), `context/progress-tracker.md`, `CLAUDE.md` (Project State + Candidate next scope), `context/ui-registry.md` (new components, via `/imprint`).
19. `docs/plan/phase-12-postgres-session-dashboard/` via `/feature-docs` once built.
20. Note for the current session: this `/grilling` + `/domain-modeling` transcript is a natural candidate for `/session-docs` once Plan Mode exits, matching the Phase 10/11 precedent (`docs/grilling/phase-12-.../`).

## Verification

- `uv run pytest` on a fresh clone with **neither** `DATABASE_URL` nor `TEST_DATABASE_URL` set — full suite green, including the route-orchestration tests exercising the real lifespan hook (confirms the app boots with persistence cleanly disabled, not by accident), `@pytest.mark.db` tests skipped (not failed/errored). Confirm a valid-session-id workflow call in this mode returns `X-Persisted: false` and `GET /api/dashboard` returns `200` all-`null`.
- `uv run pytest -m db` with `TEST_DATABASE_URL` pointed at the Neon `test` branch (and `DATABASE_URL` left unset, to confirm the two are genuinely decoupled) — repository/migration tests green; confirm `test` branch stays empty after the run (rollback isolation held) and that `dev`/`main` were never touched.
- JSONB round-trip check (part of the repository test layer): save and re-read all three of the actual `sample_data/*.xlsx`-derived results end-to-end with no field loss or type coercion surprises; separately, construct a result containing a `NaN` (e.g. a genuinely missing numeric field) and confirm the `allow_nan=False` guard fails that one save loudly (surfacing as `X-Persisted: false` at the route layer) rather than silently.
- Local manual check against the Neon `dev` branch: start FastAPI, confirm `schema_migrations` shows the applied migration (single row, single transaction); run each workflow twice with the same valid `X-Session-Id`, confirm `X-Persisted: true` both times and that the row's `saved_at` advances on the second run, not just the first (directly verifies the upsert's explicit `saved_at = now()`); `GET /api/dashboard` with the same header returns the live results; a fresh/never-used session id returns all-`null` and the frontend falls back to sample data per section with the chip visible.
- `curl` a malformed `X-Session-Id` (including an explicitly empty-string header) against both a workflow endpoint and `GET /api/dashboard` — both `400` before any DB work.
- Simulate a genuine **post-startup** outage — boot successfully against the reachable Neon `dev` branch, then cut connectivity (e.g. pause the branch, or block the connection at the network level) without restarting the app — and confirm `GET /api/dashboard` returns `503` with `BusinessErrorMessage` rendered. Pointing `DATABASE_URL` at an unreachable host *before* startup is a different case (fail-closed startup, per the ADR's bounded-retry-then-fail rule) and does not exercise this path — the server never finishes booting, so there's no running instance to return a `503` from. Separately confirm the unset-`DATABASE_URL` case stays a clean `200`.
- `curl -X OPTIONS` preflight from the deployed Vercel origin against the Render backend — confirm `X-Persisted` appears in the exposed-headers response, same style of check used to verify CORS during the Phase 11 deployment session.
- `npm run typecheck && npm run lint && npm run build` clean.
- Live-browser pass (throwaway Playwright install, per established project practice — install, verify, uninstall, confirm no trace in `package.json`): fresh `localStorage` shows sample data + chip on all three dashboard sections; running each workflow once and reloading the dashboard shows that section live with no chip, other sections still sample+chip; a workflow run's `X-Persisted: false` path (simulate by temporarily pointing `DATABASE_URL` at an unreachable host) still returns the correct result plus the new inline note, and does not block or error the page.
