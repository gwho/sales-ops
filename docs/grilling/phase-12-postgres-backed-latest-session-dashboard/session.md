# Session Record — Phase 12: Postgres-Backed Latest-Session Dashboard

## Context

Phase 11 (Deployment Baseline) had shipped and the app was live on Vercel + Render. `context/build-plan.md` and `memory.md` both pointed at "a future Postgres-backed dashboard phase" as the intended successor to an earlier, paused SQLite-based "SQL Reporting and Active Sample Dashboard" idea (partially implemented, then paused mid-build in favor of shipping the deployment baseline first; the working code was left in `git stash@{0}`). That paused work had never gotten its own ADR — the `0007` filename slot was referenced only as a forward pointer in code comments and was never actually written.

This session picked that thread back up as **Phase 12**, invoked via `/grill-with-docs <scope>`, with an explicit scope brief from the developer:

- Replace the old SQLite sample-dashboard idea with a product-relevant persistence layer.
- Store computed workflow outputs in Postgres after each run.
- Use anonymous browser/session identity if needed.
- Dashboard should show the latest saved workflow results for that session.
- Fall back to sample data when no session results exist.
- Do not store raw uploaded files unless explicitly decided.
- Keep FastAPI as the business logic boundary and expose JSON APIs to the frontend.
- Consider DuckDB only as a later analytics/export learning phase, not part of Phase 12.
- **Do not implement until the new architecture decisions are confirmed.**

## Skill sequence

1. **`/grill-with-docs`** loaded, which itself instructed: "Run a `/grilling` session, using the `/domain-modeling` skill."
2. **Two `Explore` agents ran in parallel** before any questions were asked, per the grilling skill's own instruction ("if a question can be answered by exploring the codebase, explore the codebase instead"):
   - Agent 1 pulled the stashed SQLite schema/queries, the full `src/contracts.py` Output Contract field lists, ADR 0006 and the (never-written) ADR 0007's forward-pointer comments, and the relevant `CONTEXT.md` glossary terms.
   - Agent 2 pulled `backend/main.py`, all three workflow router bodies, `backend/uploads.py`/`errors.py`, a grep confirming **zero existing session/cookie/UUID infrastructure anywhere in the repo**, `pyproject.toml`'s dependencies (no DB driver yet), the Render/Vercel deployment env-var shape, `lib/api-client.ts`, and `app/dashboard/page.tsx`'s exact current data-fetching pattern (static `mock-data.ts` imports).
3. **The `/grilling` interview ran one question at a time**, each with a stated recommendation, across 13 resolved decision points (Q1–Q11 below, plus two follow-up "residual" rounds after the developer signaled "more to grill first" twice).
4. **Domain-modeling was folded in inline** (no separate `Skill(domain-modeling)` call) — CONTEXT.md amendments and the full ADR 0007 text were drafted directly as part of assembling the final plan.
5. **Plan Mode**: the full design was written to a plan file, `ExitPlanMode` was called, and the developer **rejected it twice** with substantive corrections (see "Post-approval review rounds" below) before approving on the third attempt.
6. **Implementation** followed immediately in the same session — full backend/frontend build-out, two-layer test suite, live-Neon smoke tests, real-browser Playwright verification, and doc updates.

## The 13 resolved decisions

| # | Decision | Resolution |
|---|---|---|
| Q1 | Session identity mechanism | Client-generated UUID in `localStorage`, sent as `X-Session-Id` header. No cookies — avoids `SameSite=None`/`allow_credentials` cross-site-cookie complexity between Vercel and Render. |
| Q2 | Persistence trigger point + malformed-header semantics | Folded into the existing three workflow endpoints (not a separate save endpoint). Header absent → compute normally, skip save. Header malformed → `400` before any file processing. Header valid → compute, persist, report outcome. |
| Q3 | Storage shape | One table, `workflow_results`, one JSONB row per `(session_id, workflow_type)`, upserted latest-wins, plus a `result_schema_version` column — not a normalized SQL-reporting schema like the paused SQLite design. |
| Q4 | DB access layer | `psycopg` 3, hand-written parameterized SQL, no ORM — routes are sync, matching this project's existing no-ORM precedent. |
| Q5 | Migration execution trigger | Automatic, in the FastAPI lifespan startup hook — not a Render Pre-Deploy Command — for local/production parity. |
| Q6 | Write-path failure semantics | Best-effort: a DB write failure never fails the request. Outcome always reported via `X-Persisted: true/false/skipped`, never silent. |
| Q7 | Read/dashboard endpoint shape | One combined `GET /api/dashboard`, per-workflow-type independent sample-data fallback (not all-or-nothing). Envelope type lives in the backend's dashboard module, not `src/contracts.py`. |
| Q8 | Frontend read boundary | **Reopened and corrected a gap in Q7's own answer**: since session identity lives only in `localStorage`, the dashboard fetch must happen in a Client Component on mount, not an async Server Component fetch — a direct, coupled consequence of Q1. |
| Q9 | Local/test Postgres strategy | Neon branching (`main`/`dev`/`test`), two-layer test suite: mocked-repository route-orchestration tests (always run) + real-Neon repository/SQL tests (`@pytest.mark.db`, skip without `TEST_DATABASE_URL`). |
| Q10 | Data retention | Read-time "display expiry" via TTL (30-day default) — rows hidden from the dashboard, never actively deleted in Phase 12. Funnels through the same "row resolves to null" mechanism as schema-version incompatibility. |
| Q11 | Write-side UI surfacing | `X-Persisted: false` gets a small non-blocking inline note; `true`/`skipped` render nothing — matches the app's existing no-success-chrome convention. |

## Residual rounds (after the main 13)

The developer twice said "more to grill first" when asked if the design tree was resolved, surfacing four more real gaps:

1. **Does `POST /api/inventory/allocate` persist the internal `validate_orders()` byproduct too?** Resolved: no — only `inventory_allocation` is saved; the internal validation is a business-rule dependency, not a workflow the user invoked or received in the response.
2. **Do the three `.../report` endpoints persist?** Resolved: no, explicitly — they remain entirely unchanged from ADR 0006's original stateless design.
3. **What exactly counts as "malformed" `X-Session-Id`, and is the predicate shared between write and read paths?** Resolved: `uuid.UUID(value)` (any RFC4122 version), applied via one shared FastAPI dependency, with the parsed `uuid.UUID` object (not the raw string) bound directly in every query for double normalization (app layer + Postgres's native `UUID` type).
4. **Two documentation-only residuals**, folded straight into the ADR without further discussion: the `result_schema_version` bump discipline needs a named trigger rule, and payment aging results are `as_of_date` snapshots (a fact worth naming explicitly so a future reader doesn't mistake unchanging aging buckets for a bug).

## Post-approval review rounds (Plan Mode)

The developer rejected the first `ExitPlanMode` attempt with a long, structured correction citing "their" review (an external/parallel review pass not visible in this transcript) synthesized against the assistant's own draft. Real corrections folded in:

- Migration batching had to be a **single transaction** for the whole pending-file batch, not one transaction per file (closes a lock-release gap between files during a deploy).
- `schema_migrations` must be **runner-owned**, never bootstrapped inside a numbered migration file.
- The upsert's `saved_at` **must be set explicitly in the `DO UPDATE SET` clause** — a column `DEFAULT now()` only fires on `INSERT`, which would silently break Display Expiry for returning visitors.
- A **`json.dumps(..., allow_nan=False)` guard** was needed before writing to JSONB, since Postgres rejects `NaN`/`Infinity` but `json.dumps` emits them by default and pandas produces them easily.
- **Missing `DATABASE_URL` must not fail app startup or any test** — required for `uv run pytest` to stay hermetic, since the lifespan hook runs even under `TestClient`.
- **`TEST_DATABASE_URL` as a separate env var from `DATABASE_URL`** — closes the risk of a misconfigured environment pointing a cleanup/rollback-driven test at `dev` or `main`.
- **Two distinct `GET /api/dashboard` outcomes**: `200` all-`null` for "nothing saved yet" vs. `503` for a genuine database outage — previously conflated.
- Minor: the frontend must **omit** `X-Session-Id` entirely when unavailable, never send an empty string (which the backend would treat as malformed, not absent).
- Minor: the repository should be injectable as a FastAPI dependency for clean test overrides.

The second rejection was smaller: two wording fixes (avoid "the design that actually shipped" language before anything had shipped; quote the `uv add` command since unquoted brackets are shell metacharacters), plus one real reconciliation — the `503` verification recipe as originally drafted actually exercised **startup failure**, not the runtime `503` path, because pointing `DATABASE_URL` at an unreachable host *before* boot triggers migration failure (fail-closed startup), not a running server that later returns `503`. This surfaced a **third startup state** that the ADR hadn't named: `DATABASE_URL` set but unreachable at boot, resolved with a bounded cold-start retry (to tolerate ordinary Neon cold-start latency) before falling back to fail-closed startup.

A third, tiny round added one more sentence: the retry window must stay under Render's own health-check timeout, so a slow cold start reads as "still booting" to Render rather than tripping a deploy failure.

## Outcome

- `docs/adr/0007-session-scoped-workflow-result-persistence.md` — full design, written after approval.
- 7 new/amended `CONTEXT.md` terms: Anonymous Session ID, Saved Workflow Result, Workflow Results Store, Persistence Outcome, Dashboard Latest Results, Result Schema Version, Display Expiry (plus amendments to the existing Workflow Request and Current Result terms).
- `docs/archive/phase-11-sql-reporting-sqlite-plan.md` — the paused SQLite plan archived for future study, with a note explaining it was superseded, not completed, by ADR 0007.
- Full implementation: 6 new backend modules, 5 new/changed frontend files, 23 new tests (15 mocked route-orchestration + 8 real-Neon integration), `uv run pytest` 212 passing / 7 skipped hermetically.
- Live-verified against the real Neon `dev` branch and via a real-browser Playwright pass.
- One real incident caught mid-implementation, unrelated to the design itself: real Neon credentials were briefly pasted into the tracked `.env.example` instead of the gitignored `.env` — caught before anything was staged, fixed immediately.
