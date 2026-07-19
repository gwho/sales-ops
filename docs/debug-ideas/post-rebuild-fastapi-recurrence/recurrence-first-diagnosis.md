# Post-Rebuild FastAPI Recurrence — Diagnosis Ideas

## Why this is a separate note

This is a recurrence of the localhost symptom covered by
`docs/debug-ideas/fastapi-localhost-connectivity/local-first-diagnosis.md`, but
with a narrower boundary: it returned after rebuilding the frontend following
the landing-page evidence changes.

The landing-page pass did not change `lib/api-client.ts`, `backend/`, the Python
business-rule modules, the FastAPI routes, or the database layer. Do not assume
the rebuild introduced an API regression merely because the symptom appeared
after it.

## Evidence captured on 2026-07-19

The following checks were run before drafting this note:

```text
GET http://127.0.0.1:3000/dashboard -> 200 OK
GET http://127.0.0.1:8000/health    -> connection refused (curl exit 7)
Port 3000                           -> Node process listening
Port 8000                           -> no listening process
Compiled Next.js API target         -> http://127.0.0.1:8000
```

This is already a red-capable feedback loop for the reported boundary:

```bash
curl -fsS --max-time 3 http://127.0.0.1:8000/health
```

- **Red:** non-zero exit because the FastAPI health endpoint is unreachable.
- **Green:** `{"status":"ok"}` with HTTP 200.
- **Fast:** completes in at most three seconds.
- **Specific:** reaches the exact backend origin embedded in the rebuilt
  frontend rather than testing a different host or the production service.

The immediate cause of the browser banner is therefore known: the frontend is
available, but its configured local backend is not. What is not yet known is
why FastAPI was absent — never restarted after the rebuild, or started and then
exited during startup.

## Skills and procedures to invoke

Invoke these in order:

1. **`$diagnosing-bugs`** — keep the health-check command above as the primary
   red/green loop; reproduce before changing code.
2. **`/recover`** — invoke if one clean attempt to start FastAPI does not stay
   running or the same symptom returns again after a claimed corrective fix.
   This is already a recurrence, so do not stack speculative patches.
3. **`$browser:control-in-app-browser`** — after the backend loop is green,
   verify the dashboard request, console, CORS behavior, and one real sample
   workflow. If browser control is unavailable, record the checks as pending
   and give the developer an explicit manual checklist.
4. **`/project-review`** — report plan alignment, system integrity, and
   production readiness after the narrow fix. Do not silently fix unrelated
   findings during the review.
5. **`/architect`** — invoke only if the confirmed long-term solution changes
   local development orchestration, such as adding a single command that owns
   both Next.js and FastAPI process lifecycles. Do not use `/architect` merely
   to start a missing process.
6. **`$session-docs`** — immediately document any completed `/recover`,
   `/architect`, or `/project-review` session while its reasoning remains in
   context.

Do not invoke `$github:yeet`, commit, push, update a PR, or deploy until the
local stack is verified and the developer explicitly approves publishing.

## Scope and safety

- Preserve the dirty landing-page, teaching, memory, and documentation changes.
- Do not edit or regenerate unrelated files while diagnosing connectivity.
- Do not change `NEXT_PUBLIC_API_BASE_URL` to the Render production URL to make
  the red banner disappear locally.
- Do not point local development at the production Postgres branch.
- Never print a database connection string, token, or `.env` contents.
- Treat `DATABASE_URL` only as `set`/`unset` and, if necessary, confirm the
  branch through an approved secret-safe method.
- Do not kill a process until its PID, command, port, and ownership have been
  identified.
- If starting FastAPI fixes the issue and it remains stable, report
  **no code change required**.

## Recurrence-focused diagnosis

### Phase 1 — Confirm the two-service boundary

Run these checks independently:

```bash
curl -fsS --max-time 3 http://127.0.0.1:8000/health
curl -fsSI --max-time 3 http://127.0.0.1:3000/dashboard
```

Also inspect listeners on ports 3000 and 8000. Do not treat a successful
frontend response as evidence that FastAPI is running; `npm run dev` owns only
the Next.js process.

Before changing environment variables, confirm the effective frontend API
target from the compiled output or from a browser network request. The current
rebuilt output contains `http://127.0.0.1:8000`, so a stale production URL is
not the leading explanation for this occurrence.

### Phase 2 — Start FastAPI and capture the first terminal outcome

In a separate terminal, use the documented command:

```bash
uv run fastapi dev backend/main.py
```

Do not immediately background or restart it in a loop. Capture which of these
outcomes occurs:

1. It reaches the ready/listening state and stays alive.
2. It exits before listening because of a Python import/configuration error.
3. It retries and exits while opening the Postgres connection or applying
   migrations.
4. It cannot bind because another process owns port 8000.

Re-run the health loop as soon as the startup terminal reports ready. A green
health check after an ordinary start means the browser symptom was operational:
the backend process was absent, not broken application code.

### Phase 3 — Minimise only if startup fails

If FastAPI exits, use its first real traceback as the failure signal. Do not
jump to CORS, frontend environment variables, or landing-page components;
those cannot prevent the backend from binding to port 8000.

If the traceback points to database startup, run one isolated probe with
persistence disabled for that subprocess only, without editing `.env`:

```bash
DATABASE_URL= uv run fastapi dev backend/main.py
```

Interpretation:

- **Starts with an empty `DATABASE_URL`:** the HTTP app is healthy; database
  initialization or the configured Neon connection is the failing boundary.
- **Still exits:** database initialization is not the cause; continue with the
  exact import, bind, or runtime error shown.

This probe is diagnostic only. It is not permission to remove the local Neon
development configuration permanently.

### Phase 4 — Rank hypotheses only after the startup outcome is captured

Test one prediction at a time:

1. **Only Next.js was restarted after the build.**
   Prediction: FastAPI starts normally and the health loop immediately turns
   green, with no code or environment change.
2. **FastAPI attempted to start but exited during database initialization.**
   Prediction: the normal start shows a Postgres/migration failure, while the
   empty-`DATABASE_URL` probe reaches the listening state.
3. **Port 8000 is intermittently owned or released by another process.**
   Prediction: listener/PID inspection shows a competing owner or a bind error
   in the FastAPI terminal.
4. **The frontend and backend use different local origins after both start.**
   Prediction: `/health` is green, but the browser request fails at CORS and a
   preflight using the frontend's exact origin reproduces it.
5. **A stale public environment value was compiled into Next.js.**
   Prediction: the browser network request or compiled bundle targets a URL
   other than `http://127.0.0.1:8000`. Current bundle inspection makes this a
   low-ranked hypothesis for this occurrence.

Show the ranked list and captured startup outcome before editing code.

## Do not apply these false fixes

- Do not add retry loops to `DashboardLiveSections` to hide a missing backend.
- Do not change the API fallback from `127.0.0.1` back to `localhost`.
- Do not make the frontend fall back to Render when local FastAPI is absent.
- Do not weaken CORS before a request is actually reaching FastAPI.
- Do not change Python business rules, landing components, persistence
  contracts, or database migrations without evidence that they cause startup
  failure.
- Do not add a process manager merely because one terminal was not started.

## Recurrence-prevention options after root cause confirmation

If the confirmed cause is simply that only Next.js was restarted, choose one
of these intentionally:

1. **Documentation-only:** keep the two-terminal model and add an explicit
   local-stack startup checklist to the README.
2. **Preflight-only:** add a small local-stack health-check command that reports
   which service is missing before browser testing.
3. **Combined orchestration:** add one developer command that starts and owns
   both services, including signal handling and clean shutdown. This changes
   development infrastructure and should go through `/architect` before
   implementation; avoid adding a dependency until the desired cross-platform
   behavior is decided.

Do not choose a prevention mechanism before proving the cause. A combined dev
command will not fix a genuine database-startup failure; it would only make the
failure easier to observe.

## Browser and CORS verification after health is green

With both services running:

1. Open the frontend using one explicit origin, preferably
   `http://localhost:3000` to match the backend's default local CORS origin.
2. Confirm `GET /api/dashboard` returns HTTP 200 with a valid
   `X-Session-Id`.
3. Confirm an all-`null` dashboard response is accepted when persistence is
   intentionally disabled and that the UI shows fictional sample fallback.
4. Run one workflow using its sample files and confirm the JSON request works.
5. If local persistence is enabled, confirm it uses only the Neon `dev` branch
   and that the dashboard reflects the saved workflow result after reload.
6. Confirm no relevant browser console or hydration errors.

If the frontend is opened at `http://127.0.0.1:3000` instead, use that exact
origin in the CORS preflight and configuration. `localhost` and `127.0.0.1`
are different origins.

## Verification gates

For an operational restart with no code change:

- Health loop green.
- Dashboard endpoint returns 200.
- Browser/manual workflow check passes.
- Report `no code change required`; do not run a performative full build merely
  to justify a process restart.

For any actual code or configuration change:

```bash
uv run pytest
npm run typecheck
npm run lint
npm run build
```

Then re-run the original health loop and the browser verification. Invoke
`/project-review` and stop before commit, push, PR, or deployment.

## Acceptance criteria

- The red/green health command returns `200 {"status":"ok"}`.
- The reason FastAPI was absent is stated with evidence: never started, exited
  during a named startup boundary, or could not bind to the port.
- `/dashboard` no longer shows **Could not reach the API server**.
- The effective frontend API base remains intentional and documented.
- No production service, database, secret, or deployment branch was changed.
- If no source change was necessary, the diagnosis says so explicitly.
- If the failure returns after one corrective attempt, work stops and
  `/recover` is invoked rather than applying a second speculative patch.
