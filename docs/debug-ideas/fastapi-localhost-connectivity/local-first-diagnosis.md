# Local-First FastAPI Connectivity Diagnosis

## Skills and procedures to invoke

Invoke these in order:

1. `$diagnosing-bugs` — reproduce and identify the local API failure before editing.
2. `$browser:control-in-app-browser` — verify the repaired app at localhost, including console and network requests.
3. `/project-review` — run the repository's report-only verification after the fix.
4. `/recover` — invoke only if the same failure remains after one corrective attempt.
5. Do not invoke `$github:yeet`, commit, push, or deploy until local verification passes and the developer explicitly approves publishing.

## Companion instruction

Diagnose and fix the localhost FastAPI connectivity failure shown on `/dashboard`.

### Scope and safety

- Work only in the current local branch and dirty working tree.
- Do not commit, push, open or update a PR, modify `deploy/portfolio-demo`, or trigger Vercel or Render deployment.
- Do not alter the working production deployment at `https://sales-ops-gamma.vercel.app/`.
- Preserve all unrelated landing-page, documentation, tutorial, and sample-data changes.
- Never write credentials or connection strings to `.env.example`, logs, documentation, or command output.
- Treat the screenshot as a symptom, not proof of the root cause.

First read the project context files in the mandatory `AGENTS.md` order. Because this is diagnosis rather than a new feature, do not run `/architect` unless the confirmed fix requires a material architectural redesign.

Invoke `$diagnosing-bugs` and establish a fast red/green feedback loop before proposing a fix:

1. Inspect the current process and port state without killing unrelated processes.
2. Start FastAPI using the documented local command: `uv run fastapi dev backend/main.py`.
3. Confirm `GET http://127.0.0.1:8000/health` returns `200 {"status":"ok"}`.
4. Call `GET http://127.0.0.1:8000/api/dashboard` with a valid UUID in `X-Session-Id` and capture the exact response.
5. Start Next.js with `npm run dev` on an available local port.
6. Determine the effective `NEXT_PUBLIC_API_BASE_URL`. The local default should be `http://127.0.0.1:8000`; do not hardcode a different URL merely to hide the failure.
7. Check the localhost CORS preflight using the frontend's actual origin. Confirm `X-Session-Id` is allowed and the origin exactly matches, with no trailing-slash mismatch.
8. Inspect FastAPI startup logs, browser console output, and the failed `/api/dashboard` network request.

Rank and test at least these hypotheses:

- FastAPI is not running or failed during startup.
- Port 8000 is occupied by another process.
- The frontend is using a stale or incorrect `NEXT_PUBLIC_API_BASE_URL`.
- Next.js was not restarted after an environment-variable change.
- The browser is using `localhost` while FastAPI is bound to IPv4 `127.0.0.1`.
- Local CORS origin configuration does not match the frontend origin.
- Database initialization is preventing FastAPI startup.

Change one variable at a time. State the confirmed root cause before editing. If the issue is operational—for example, FastAPI simply was not running—do not manufacture a code change.

### Local browser verification

After applying the narrowest fix, invoke `$browser:control-in-app-browser` and verify:

- `/dashboard` loads without the red API error.
- The dashboard request returns `200`.
- Sample-data fallback renders correctly when local persistence is disabled.
- The browser console has no relevant errors.
- One workflow can run using its sample files.
- If `DATABASE_URL` is already configured, it points only to the Neon `dev` branch; confirm the workflow returns the expected persistence outcome and the dashboard reflects it after reload.
- Never use Neon `main`, the production Render database, or `TEST_DATABASE_URL` for ordinary local verification.

### Automated verification

Run:

```bash
uv run pytest
npm run typecheck
npm run lint
npm run build
```

Then invoke `/project-review` and report:

- The confirmed root cause.
- The exact files changed, or `no code change required`.
- Local API and browser verification results.
- Test and build results.
- Any remaining limitations.

Stop before any commit, push, PR update, or deployment and wait for developer approval. If the same symptom remains after one corrective attempt, stop and invoke `/recover` rather than stacking additional fixes.

## Acceptance detail

`GET /api/dashboard` returning `200` with all workflow fields set to `null` is valid when local persistence is disabled. The frontend should then show sample data, not the red **Could not reach the API server** banner.
