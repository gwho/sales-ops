# Diagnosis — Post-Rebuild FastAPI Recurrence

## Symptom reported

`/dashboard` showed **"Could not reach the API server"** after the frontend was
rebuilt following the landing-page evidence changes. This was a recurrence of
a previously documented symptom (`docs/debug-ideas/fastapi-localhost-connectivity/local-first-diagnosis.md`),
but scoped narrowly to this specific occurrence per
`docs/debug-ideas/post-rebuild-fastapi-recurrence/recurrence-first-diagnosis.md`.

## Phase 1 — Feedback loop

Command (already run, output captured):

```bash
curl -fsS --max-time 3 http://127.0.0.1:8000/health
```

Result: `curl: (7) Failed to connect to 127.0.0.1 port 8000` — non-zero exit,
red on the exact reported symptom. Red-capable, deterministic, fast (≤3s),
agent-runnable — met all four Phase 1 completion criteria without modification.

## Phase 1b — Boundary confirmation

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN   # -> node PID 86915, LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN   # -> no output, nothing listening
```

Effective frontend API target confirmed via `lib/api-client.ts:23`
(`process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"`) and `.env`
(key absent, so the code default applies) — ruled out a stale production URL
before touching anything else.

## Hypotheses (ranked before testing)

1. **Only Next.js was restarted; FastAPI never started this session.** *(leading)*
2. FastAPI attempted to start but exited during database initialization.
3. Port 8000 intermittently owned by another process.
4. Frontend/backend using different local origins (CORS).
5. Stale public env value compiled into the frontend.

## Phase 2 — Single start attempt, outcome captured

```bash
uv run fastapi dev backend/main.py
```

Log tail: `Uvicorn running on http://127.0.0.1:8000` → `Application startup
complete.` — outcome 1 from the note's list (reaches listening state, stays
alive). No retry loop, no backgrounding-and-forgetting — one attempt, output
read in full.

## Re-verification

```bash
curl -fsS --max-time 3 http://127.0.0.1:8000/health   # {"status":"ok"}, exit 0
lsof -nP -iTCP:8000 -sTCP:LISTEN                        # still listening, 3s later
```

Log line `INFO: 127.0.0.1:50616 - "GET /health HTTP/1.1" 200 OK` confirms a
real, served request — not just a bound socket with a dead app behind it.

## Hypothesis 1 confirmed; 2–5 ruled out or deferred

- **#1 confirmed:** ordinary start, zero code change, immediate green.
- **#2 ruled out:** no crash occurred; startup log shows no Postgres/migration
  error at all.
- **#3 ruled out:** the earlier listener check showed nothing on port 8000
  before this start — no competing owner.
- **#4 checked and green:** CORS preflight from `http://localhost:3000`
  returned matching `access-control-allow-origin`.
- **#5 already ruled out** in Phase 1b.

## Extended verification (curl, in place of unavailable browser tool)

- `GET /api/dashboard` with a synthetic `X-Session-Id` → `200`, all-`null` body
  (expected for an unknown session).
- Real sample-file workflow request (`POST /api/orders/validate` using the
  actual `/api/templates/orders` + `/api/templates/product-master` downloads)
  → `200`, correct computed summary (`total_orders: 36`, `invalid_orders: 8`,
  matching the same real fixture cited in the landing-page evidence feature).

## Outcome

**No code change required.** The backend process was absent, not broken
application code — confirmed, not assumed, by a clean single start that
stayed alive and served real traffic. `/recover` was correctly not invoked
(its trigger condition — a claimed fix not staying up, or the symptom
returning after a fix — never occurred).

## Side-finding, deliberately not chased

The real workflow POST returned `X-Persisted: false` despite `DATABASE_URL`
being set. Traced read-only to `WorkflowResultsRepository.save()`'s
`if self._pool is None: return False` early return
(`backend/repositories/workflow_results.py:81-82`) — no exception, no log
line, so none of the method's other two documented failure paths applied.
This is a different boundary (local persistence, not reachability) and was
deliberately left uninvestigated per the diagnosis note's scope limits;
recorded for a future session in
`docs/debug-ideas/local-persistence-pool-none/observed-facts.md`.

## Prevention chosen

Documentation-only, per explicit developer choice (asked directly rather than
assumed, per the note's own instruction not to pick a prevention mechanism
before the cause was proven). `README.md` gained a "Local development"
section documenting the two-terminal model and the exact health-check command
to run before assuming a "no backend" banner means something is broken.
