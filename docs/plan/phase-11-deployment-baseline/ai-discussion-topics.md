# AI Discussion Topics — Feature phase-11-deployment-baseline: Deployment Baseline

## Phase sequencing and the paused SQLite work

1. Walk through exactly what would need to happen to bring the stashed SQLite reporting work (`stash@{0}`) back into the working tree today, given that `backend/main.py` has since diverged. Would `git stash pop` succeed cleanly, or conflict?
2. Why was the SQLite work preserved in a stash instead of a branch? What would be different about discoverability or safety if it had been committed to a throwaway branch instead?
3. The plan says Phase 12 will target Postgres "instead of SQLite" — what specifically about the stashed schema/queries would need to change to move from SQLite to Postgres, versus what would carry over unchanged?
4. What breaks, or silently becomes stale, if a future session pops the stash without first re-reading this document and the Phase 11 pivot section of `memory.md`?

## CORS and environment configuration

5. `_cors_origins()` reads the env var once at app-construction time. If Render's dashboard shows a "successful save" after editing the env var but the old CORS behavior persists, what's the first thing to check, and why wouldn't restarting the frontend help?
6. Walk through exactly why a trailing slash on a `CORS_ALLOWED_ORIGINS` entry causes a silent failure rather than an error — what does the browser send, what does `CORSMiddleware` compare it against, and where specifically does the mismatch happen?
7. If `CORS_ALLOWED_ORIGINS` were left unset entirely on the deployed Render instance, what would actually happen when the deployed Vercel frontend tried to call it? Trace it through `_cors_origins()`'s default.
8. Why does `allow_methods=["GET", "POST"]` (unchanged from before this phase) matter for `/health`, which is only ever called with GET? Is there a hidden coupling here worth naming, or is it genuinely irrelevant to this endpoint?

## `.gitignore` and the `.env.example` fix

9. The negation pattern `!.env.example` was placed directly after the `.env*` line. What would happen if a future contributor reordered `.gitignore` and moved that negation above the blanket rule instead? Walk through gitignore's pattern evaluation order.
10. Is there a real scenario where the current `.env*` / `!.env.example` combination could still accidentally let a secret-bearing file get committed? What filename would have to look like to slip through both rules?

## Health check design

11. `GET /health` is described as deliberately checking nothing. Argue the other side: what's a concrete scenario in this app's current (Phase 11) state where a zero-dependency health check gives a false "healthy" signal that a slightly smarter check would have caught?
12. If Phase 12 adds a database, what would the tradeoffs be of adding a DB ping to `/health` versus adding a *separate* `/health/deep` endpoint and leaving `/health` as-is for Render's prober?

## Deploy sequencing and host choice

13. The deploy order is Render → Vercel → Render again. Is there a way to avoid the second Render redeploy, and if so what would it cost in terms of security or flexibility (hint: consider a wildcard or permissive CORS origin as an alternative)?
14. The plan rejected a single-container deployment in favor of mirroring the local two-service dev topology. Construct the strongest argument for the single-container approach anyway — what would it have simplified, and what would it have cost?
15. Render's free-tier cold start is "accepted," not engineered around. What's the simplest change (still within a free/low-cost budget) that would meaningfully reduce the user-facing impact of a cold start, without adding a permanent keep-alive job?
