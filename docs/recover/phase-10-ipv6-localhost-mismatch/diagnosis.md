# Diagnosis: "Could not reach the API server" persisting after a real backend was up and working

## What broke

`/order-validation`'s "Run sample data" (and, by the same code path, every other live workflow action) showed `lib/api-client.ts`'s network-failure message — *"Could not reach the API server. Make sure the FastAPI backend is running and try again."* — even after the backend was confirmed running, correctly configured, and reachable.

## Failure mode: Isolated bug (not session pollution, not wrong foundation)

The symptom was specific to one request path, the rest of the app worked, and the underlying architecture (two dev servers + CORS, stateless FastAPI, `lib/api-client.ts`'s fetch wrapper) was never in question — every check confirmed it was correctly built. What made this diagnosis unusually hard wasn't the failure mode classification (that was clear from the start); it was that the obvious checks all came back green, requiring three successive hypotheses before finding the one that matched the evidence.

## How the diagnosis was reached — three rounds

**Round 1 — hypothesis: backend not running.** This was the correct diagnosis for an *earlier*, textually-identical error message a few turns before this session (documented separately in `docs/diagnosing-bugs/phase-10-backend-not-running-after-cleanup/`). Checked first because it was the known-precedent cause. Ruled out immediately: `lsof -i :8000` showed the backend listening, `curl` returned `200`.

**Round 2 — hypothesis: wrong port.** `lsof` revealed six *other* stray Next.js dev-server instances of the same app running on other ports (`3010`–`3051`), left over from earlier verification passes in the same long session. Backend CORS is deliberately scoped to `http://localhost:3000` only, so a browser tab on any other port would be silently blocked and produce this exact symptom. Asked the user to confirm their address bar — they were genuinely on `:3000`. Ruled out.

**Round 3 — hypothesis: stale client-side state.** A fresh headless-browser repro against `http://localhost:3000/order-validation` succeeded completely — every request `200`, real computed results, zero console errors. Since the user's *own* browser was also on `:3000` and still failing, the working hypothesis became "your tab is showing a leftover error from before recent fixes landed." Proposed a hard refresh. The user tried it — **still failed.** This ruled out the hypothesis and was the signal to stop pattern-matching against "identical error text" and instead explain the specific mechanism.

**Round 4 — the actual cause, found via direct evidence, not further guessing.** The key realization: a fresh *headless Chromium* repro succeeding while the user's *real desktop browser* failed, on the identical URL, is itself a data point — it means something about network resolution differs between the two environments, not that the app is broken. Checked `/etc/hosts`: `localhost` resolves to both `127.0.0.1` and `::1` (standard macOS default). Checked what the backend actually binds to: `lsof` showed `127.0.0.1:8000` only — IPv4, no IPv6 listener. Directly tested `curl http://[::1]:8000/...` — connection failure. This is a complete, mechanistic explanation: real browsers commonly implement Happy Eyeballs (RFC 8305) and may attempt the IPv6 loopback address first for a hostname that resolves to both; when nothing listens there, the request fails before ever reaching the backend — invisible to `curl` (which in this test environment's shell defaulted to IPv4) and invisible to the headless test browser (whose network stack, running in a different environment, apparently resolved or raced the addresses differently).
