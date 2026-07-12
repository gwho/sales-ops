# Plan — Feature phase-11-deployment-baseline: Deployment Baseline

## What was built

- `backend/main.py` — replaced the hardcoded `allow_origins=["http://localhost:3000"]` CORS config with `_cors_origins()`, which reads `CORS_ALLOWED_ORIGINS` from the environment (comma-separated, trimmed, empty entries dropped, defaulting to `http://localhost:3000` when unset), and registered the new `health` router.
- `backend/routers/health.py` — new. `GET /health` returns `{"status": "ok"}`, no database or dependency check.
- `.env.example` — new. Documents the two plain, non-secret config vars (`NEXT_PUBLIC_API_BASE_URL`, `CORS_ALLOWED_ORIGINS`) and their local-dev fallback defaults. Committed with empty values; real deployed values live only in the Vercel/Render dashboard configs.
- `.gitignore` — added `!.env.example` immediately after the existing blanket `.env*` rule, which had been silently excluding `.env.example` from every `git add`.
- `README.md` — new "Live Demo" section: the two live URLs, a one-paragraph usage walkthrough ("Run sample data" on any workflow page), and a note about Render free-tier cold starts (~1 minute after ~15 minutes idle).
- `context/architecture.md` — added `GET /health` to the endpoint list; new "Deployment (Phase 11)" section documenting the two-service host table, env var contract, deploy sequencing, and the cold-start trade-off.
- `context/build-plan.md` — new "Phase 11 - Deployment Baseline" section (scope, service list, branch strategy, accepted trade-off) plus a note on the retired SQLite-reporting Phase 11 scope and where its code now lives.
- `CLAUDE.md` — "Candidate next scope" section rewritten to point at Phase 12 (Postgres-backed dashboard) instead of the paused SQLite plan; build-plan pointer corrected to say Phase 11 is Deployment Baseline.
- `deploy/portfolio-demo` (git branch, not a file) — created, fast-forwarded to each verified commit on `phase/10-fastapi-integration`. Currently at `974b348`.
- No `src/`, `tests/`, `app/`, `components/`, or `types/` files changed. Phase 10.2's UI polish work (already-uncommitted at session start) was committed in the same session, ahead of the deployment-prep commit, but is documented separately under `docs/plan/phase-10.2-portfolio-ui-polish/`.

## Schema changes

None. No database, no migrations, no persisted state introduced in this phase.

## Key invariants

- **`CORS_ALLOWED_ORIGINS` is read once, at `app` construction time in `backend/main.py`.** `CORSMiddleware` is configured via `add_middleware()`, which runs once at import/startup, not per-request. Changing the env var on Render requires a redeploy (or at minimum a process restart) to take effect — editing it in the Render dashboard alone does nothing until the service restarts.
- **`GET /health` must stay a pure liveness check with no database or dependent-service query.** It exists solely so Render's health-check prober gets a fast, always-succeeding response as long as the process is up. If a future phase adds a database, do not fold a DB ping into this endpoint without deciding that deliberately — a slow or failing dependency check here can cause the host to kill and restart an otherwise-healthy process.
- **`.env.example` must never be committed with real values filled in.** It is the one place `!.env.example` punches a hole through the blanket `.env*` gitignore rule — any other `.env*` file (including a locally-filled copy of this one) stays gitignored. Real deployed values live only in the Vercel/Render dashboard configs and in `README.md`'s Live Demo section (URLs only, never secrets — there are none in this app).
- **`deploy/portfolio-demo` is fast-forward-only from a verified commit on the active implementation branch.** It is never committed to directly, never merged into, and never used as a place to push unverified work. Both hosts point at this branch, so anything pushed there goes live.
- **Deploy order is Render (backend) before Vercel (frontend) before Render again**, because of a circular URL dependency: the frontend's `NEXT_PUBLIC_API_BASE_URL` needs Render's URL, and Render's `CORS_ALLOWED_ORIGINS` needs Vercel's URL. Skipping or reordering this sequence produces either a frontend that can't reach any API or a backend that rejects the frontend's requests with a CORS error.
- **The `Origin` header a browser sends never has a trailing slash.** Any URL placed into `CORS_ALLOWED_ORIGINS` must be entered without one, or the string comparison inside `CORSMiddleware` silently fails to match and every cross-origin request gets rejected. `_cors_origins()` only trims whitespace and commas — it does not strip trailing slashes.
