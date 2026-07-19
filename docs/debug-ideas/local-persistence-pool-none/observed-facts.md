# Local Persistence Not Saving — Observed Facts

## Why this is a separate note

Found as a side effect of verifying the fix in
`docs/debug-ideas/post-rebuild-fastapi-recurrence/recurrence-first-diagnosis.md`
(FastAPI backend unreachable, resolved as an operational restart, no code
change). This is a **different, unrelated boundary** — local Postgres
persistence, not backend reachability — and was deliberately **not**
diagnosed in that session, per its own scope limits. Do not assume the two
are connected.

## What was observed

A real workflow request against the freshly started local FastAPI:

```bash
SID="00000000-0000-4000-8000-000000000000"
curl -fsS --max-time 10 -X POST http://127.0.0.1:8000/api/orders/validate \
  -H "X-Session-Id: $SID" \
  -F "orders_file=@/tmp/orders.xlsx" \
  -F "product_master_file=@/tmp/product-master.xlsx"
```

Response: `HTTP/1.1 200 OK`, `X-Persisted: false`, with a correct, fully
computed `summary` body (`total_orders: 36`, `invalid_orders: 8`, etc.) — the
workflow computation itself succeeded; only the best-effort save did not.

A follow-up `GET /api/dashboard` with the same `X-Session-Id` confirmed
`order_validation` stayed `null` — the result was genuinely not saved, not
just omitted from that one response.

`DATABASE_URL` was confirmed **set** in `.env` (checked as set/unset only,
value never printed, per this project's secret-handling convention).

`backend/repositories/workflow_results.py`'s `WorkflowResultsRepository.save()`
(lines ~70-93) has exactly one silent, no-exception, no-log early return:

```python
if self._pool is None:
    return False
```

No `logger.exception`/`logger.warning` output appeared anywhere in the
FastAPI startup or request log for this run — ruling out the two other
documented failure paths in the same method (non-finite JSON values;
a raised exception during the `INSERT`). The pool itself was apparently
never constructed for this repository instance.

`backend/db.py`'s own startup logging (`logger.info("DATABASE_URL is not set
-- persistence disabled for this run.")`, line ~126) did **not** appear
either — consistent with `DATABASE_URL` being recognized as set, which rules
out the simplest explanation (unset env var) without explaining why the pool
ended up `None` anyway.

## Suggested next session

Invoke `$diagnosing-bugs` fresh, with its own red/green loop — do not reuse
or extend the connectivity diagnosis for this. A plausible starting loop:

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/orders/validate \
  -H "X-Session-Id: 00000000-0000-4000-8000-000000000000" \
  -F "orders_file=@sample_data/sample_orders.xlsx" \
  -F "product_master_file=@sample_data/sample_product_master.xlsx" \
  -D - -o /dev/null | grep -i x-persisted
# red: X-Persisted: false   green: X-Persisted: true
```

Candidate hypotheses to rank (not yet tested):

1. The pool is created in a FastAPI lifespan hook that didn't run for this
   process (e.g. `fastapi dev`'s reloader/watcher subprocess model creating
   two processes, only one of which completed startup).
2. The pool creation itself failed silently — worth checking whether
   `backend/db.py`'s pool-construction path has its own try/except that
   could swallow a connection failure without reaching either of the two
   log lines already ruled out above.
3. A local Neon `dev`-branch connectivity or credential issue distinct from
   "unset" (e.g. expired credential, wrong branch, network access) — would
   need to be investigated without ever printing the connection string.

## Scope and safety (carried forward)

- Never print `DATABASE_URL`'s value, contents of `.env`, or any credential.
- Do not point local development at the production Postgres branch to make
  this pass.
- This is a *local development* persistence gap — confirm it doesn't affect
  the deployed Render backend before treating it as urgent.
