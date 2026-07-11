# Diagnosis: "Could not reach the API server" on `/order-validation`

## Reported symptom

Immediately after Phase 10 (FastAPI Integration) was implemented and live-browser-verified, the user reported: clicking "Run sample data" on `/order-validation` showed *"Could not reach the API server. Make sure the FastAPI backend is running and try again."* The Next.js UI itself rendered correctly — only the API call failed.

## Context leading up to it

Live-browser verification of Phase 10 had just finished, using a Playwright driver script against both dev servers running in the background (FastAPI on `:8000`, Next.js on `:3000`, both launched via `&` and tracked by PID files). As cleanup after verification succeeded, both background processes were killed (`kill $(cat /tmp/backend.pid)`, `kill $(cat /tmp/frontend.pid)`) and the temporary `playwright` npm install was removed. Shortly after that cleanup, the user's bug report arrived.

## Building the feedback loop

Per the `diagnosing-bugs` skill, the first move was a tight, agent-runnable, red-capable command — not reading code or theorizing:

```bash
curl -sf http://localhost:8000/api/templates/orders -o /dev/null -w "HTTP %{http_code}\n"
```

Result: `HTTP 000` (curl's code for "couldn't connect at all" — not a `4xx`/`5xx` from a server that responded, but no response whatsoever).

Two supporting checks confirmed what that meant:

```bash
lsof -i :8000 -sTCP:LISTEN   # → nothing listening
lsof -i :3000 -sTCP:LISTEN   # → a node process IS listening
```

This was already the whole diagnosis. No `4xx`/`5xx` response, no CORS preflight rejection, no route-not-found — a `000` plus an empty `lsof` for that port means literally nothing is bound to `:8000`. The `:3000` check being non-empty ruled out "both servers got killed and the user is looking at a stale browser tab" — the frontend genuinely was still serving requests, from a process distinct from the one killed as part of verification cleanup (or a restarted one — which process it was didn't matter for the diagnosis, only that *something* was up on `:3000` while *nothing* was up on `:8000`).

## Why this is exactly the reported symptom, not just "a" failure

`lib/api-client.ts`'s `postFormData()` (used by both `postJSON` and `postReport`, and `fetchSampleFile()` follows the identical pattern) wraps its `fetch()` call in a `try`/`catch`:

```ts
try {
  response = await fetch(`${API_BASE_URL}${path}`, { method: "POST", body: formData });
} catch {
  throw new ApiError(NETWORK_ERROR_MESSAGE);
}
```

`fetch()` throws (rather than resolving with an error-status `Response`) specifically when the request never reaches a server at all — connection refused, DNS failure, etc. — which is exactly what happens when nothing is listening on `:8000`. `NETWORK_ERROR_MESSAGE` is the literal string *"Could not reach the API server. Make sure the FastAPI backend is running and try again."* — the exact text the user saw. This confirms the failure happened at the `fetch()` layer itself, before any request ever reached `backend/`'s routing, CORS middleware, or exception handlers — ruling out a CORS misconfiguration, a missing route, or a startup crash as the cause, since none of those code paths were ever reached.

## Verdict

**Root cause: the FastAPI backend was not running.** It was killed as part of post-verification cleanup and never restarted. This is a process/operational issue, not a code defect — nothing in `backend/` or `lib/api-client.ts` was implicated by the loop.
