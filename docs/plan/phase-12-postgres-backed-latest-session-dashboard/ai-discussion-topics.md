# AI Discussion Topics — Feature phase-12-postgres-backed-latest-session-dashboard: Postgres-Backed Latest-Session Dashboard

## Data flow and request lifecycle

1. Walk through exactly what happens, function by function, from the moment a user clicks "Run Validation" to the moment `X-Persisted` shows up as a response header — name every file and function involved.
2. `get_session_id` is declared as a dependency on both the three workflow endpoints and `GET /api/dashboard`. What would change about the app's behavior if each endpoint instead implemented its own inline header parsing instead of sharing this one dependency?
3. `WorkflowResultsRepository.save()` never calls `conn.commit()` explicitly, yet the smoke tests confirm writes really persist. Where does the commit actually happen, and what would happen to a write if an exception were raised *inside* the `with self._pool.connection() as conn:` block, after the `INSERT` but before the block exits normally?

## The `app.state.db_pool` bug

4. Why did the pre-existing backend tests (written long before Phase 12) start failing the moment `backend/main.py` gained a `lifespan` hook, even though those tests never touch anything Phase 12 added?
5. `TestClient(app)` at module scope vs. `with TestClient(app) as client:` — what's the actual difference in what Starlette runs in each case? Could this same class of bug appear again if a future feature adds a second thing to the `lifespan` hook?
6. The fix was a one-line default (`app.state.db_pool = None`) rather than rewriting the existing test files to use the context-manager form. What's the argument for preferring the one-line fix here, and when would rewriting the tests instead have been the better call?

## The `persist_workflow_result` gap

7. `WorkflowResultsRepository.save()` documents itself as "never raises." The router code originally trusted that fully, with no `try/except`. Was that original code wrong, given the documented contract? What specifically proved it was still worth defending against?
8. Describe the exact test that exposed this gap, and explain why that specific test could only be written *after* deciding to test the "repository raises" scenario — why wouldn't the happy-path tests (`X-Persisted: true`, `X-Persisted: false` via a return value) have caught it?
9. Now that `persist_workflow_result` exists as a shared helper with its own `try/except`, is `WorkflowResultsRepository.save()`'s own internal `try/except` still necessary, or is it now redundant? Argue both sides.

## Env var and shell-quoting errors

10. Explain precisely why `uv add psycopg[binary,pool]` (unquoted) fails at the shell level, and why the exact same failure would happen with any other Python package that has an extras specifier, in any shell command, not just `uv add`.
11. `source .env` failed on an unquoted Neon connection string containing `&`. Would the app itself (reading `os.environ["DATABASE_URL"]` inside Python) have had any problem with that same unquoted value, if it had somehow gotten into the environment some other way? What does that tell you about where this class of bug actually lives?

## Design boundaries worth re-deriving

12. `POST /api/inventory/allocate` computes a full, correct `OrderValidationResult` internally but never saves it. If a future developer "fixed" this by also persisting it under `"order_validation"`, what would break about the `X-Persisted` header contract, and what would a user see on `/order-validation` that they never actually ran?
13. Why does `GET /api/dashboard` need to distinguish "no `X-Session-Id` header at all" from "a valid but never-used `X-Session-Id`"? Do these two cases actually produce different responses today — check the code and explain why or why not.
14. `.env.example` and `.env` look almost interchangeable by name. What's the one-sentence rule that determines which real values are allowed to go in which file, and what specifically would go wrong (not just "it's against convention") if that rule were violated and the repo were pushed?

## Verification methodology

15. The Playwright script's own locator bug produced a false failure. What two independent pieces of evidence were used to conclude "the product is correct, the test script is wrong," rather than the other way around? Would a single piece of evidence (either one alone) have been sufficient?
16. `test_workflow_results_repository.py`'s tests each clean up their own rows in a `finally` block rather than relying on a rolled-back transaction. Given that `WorkflowResultsRepository.save()` commits internally on every call, could a rollback-based isolation strategy have worked here at all? Why or why not?
