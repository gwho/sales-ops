# Resolution: Use the literal IPv4 loopback address, not the ambiguous hostname

## Root cause

`lib/api-client.ts` hardcoded its fallback backend URL as `http://localhost:8000`. `localhost` is not a single address — on this machine (and most systems), it resolves to both `127.0.0.1` (IPv4) and `::1` (IPv6). The FastAPI dev server (`fastapi dev backend/main.py`, no explicit `--host` flag) binds only to the IPv4 loopback. Any client that tries the IPv6 address first — which real browsers commonly do — gets a connection failure that never reaches the application, indistinguishable at the `fetch()` layer from "the server isn't running at all."

## The fix

One line in `lib/api-client.ts`:

```ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
```

(previously `"http://localhost:8000"`), with a comment explaining why the literal address matters. No backend change, no CORS change — `allow_origins` governs which page *origin* is allowed to call in, which is unaffected by which address that origin's JavaScript uses to call out.

## What was discarded

Two earlier hypotheses, both disproven with direct evidence before landing on this one:
1. Backend not running — disproven by `lsof`/`curl` showing it up and healthy.
2. Wrong browser port — disproven by the user confirming their address bar read `:3000`.
3. Stale client-side cache — disproven by a hard refresh not changing the outcome.

None of these were wasted effort exactly — each was the correct, cheapest thing to check first, in order of how often it's actually the cause (backend-down was the literal cause of a near-identical symptom minutes earlier in the same session). But per the diagnosis discipline, two wrong hypotheses in a row is the signal to stop pattern-matching on symptom text and instead look for a mechanism that explains *why this environment differs from a working one* — which is what round 4 did.

## What the session learned that wasn't known before

`localhost` is not safe to hardcode as a fallback URL in a project running two separate local dev servers, specifically because the two servers can silently disagree about which IP family they're listening on. `uv run fastapi dev` (via `fastapi-cli`) defaults to `127.0.0.1` with no `--host` flag; nothing in this project's setup ever explicitly decided that as a deliberate choice — it was just the CLI default, never revisited. The fix addresses the *symptom* (frontend now targets the address the backend definitely listens on) rather than the *asymmetry itself* (the backend could also be told to bind to `::` or `0.0.0.0` to accept both families) — the frontend-side fix was chosen as the minimal, single-file, most targeted change matching what was actually broken, without touching the documented `fastapi dev backend/main.py` run command or requiring a corresponding `context/library-docs.md` update.

## Regression test: none applies

Same category as the earlier `docs/diagnosing-bugs/phase-10-backend-not-running-after-cleanup/` finding — this is an environment/network-configuration issue, not a code-logic defect. No `TestClient`-based or component-level test can exercise real OS-level DNS/loopback resolution behavior. The fix is verified by the thing that actually matters: the user's real browser, which is the only environment that ever exhibited the bug.
