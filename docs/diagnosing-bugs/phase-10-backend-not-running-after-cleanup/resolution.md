# Resolution: Restart the backend; no code changed

## The fix

```bash
uv run fastapi dev backend/main.py --port 8000
```

Confirmed green with the same loop from diagnosis:

```bash
curl -sf http://localhost:8000/api/templates/orders -o /dev/null -w "HTTP %{http_code}\n"
# → HTTP 200
```

## Confirming the actual user-facing symptom, not just the loop

The diagnostic loop (`GET /api/templates/orders`) proves the server is up, but the reported bug was specifically about "Run sample data" on `/order-validation`, which is a longer chain: fetch two sample templates, then POST both to `/api/orders/validate`. To close the loop against the *exact* reported flow rather than a proxy for it, that full chain was reproduced with `curl`, including the header a real cross-origin browser request would send:

```bash
curl -sf http://localhost:8000/api/templates/orders -o /tmp/ro.xlsx
curl -sf http://localhost:8000/api/templates/product-master -o /tmp/rpm.xlsx
curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "Origin: http://localhost:3000" \
  -F "orders_file=@/tmp/ro.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  -F "product_master_file=@/tmp/rpm.xlsx;type=application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  http://localhost:8000/api/orders/validate
# → HTTP 200
```

This matters because a narrower check (just confirming the port is open) could miss a *different* failure further down the same chain — e.g., if CORS had also been broken, the templates endpoint might succeed while the POST failed on a preflight rejection. Reproducing the literal sequence "Run sample data" performs, with the `Origin` header a browser actually sends, rules that out too.

## What was NOT changed

No file in `backend/`, `lib/api-client.ts`, or anywhere else in the codebase was touched. The four constraints given at the start of the diagnosing-bugs session — don't change the architecture, don't add a Next.js proxy, keep two independent dev servers plus CORS, don't alter the stateless endpoint design — were all trivially respected, because none of them were ever implicated. The loop pointed directly at a process-lifecycle fact (server not running), not at any design decision.

## Regression test: none applies

Per the `diagnosing-bugs` skill's own explicit provision — "if no correct seam exists, that itself is the finding" — no test was added. There is no code-level seam for "the developer forgot to restart the dev server after killing it." A `TestClient`-based test would spin up the FastAPI app in-process and would never be able to distinguish "server not running" from "server running," since the whole point of `TestClient` is that it never needs a real running process. Writing a test here would not lock down anything real; it would just be motion.

## What the session actually learned

The learning isn't about the codebase — it's about verification hygiene. Live-browser verification necessarily starts background processes to drive a real browser against a real server pair. Once verification finishes, killing those processes as "cleanup" is reasonable in isolation, but it silently assumes nobody needs the app to keep running afterward. In this session, the user picked up manual testing of the same feature immediately after automated verification finished — a natural thing to do right after a feature ships — and hit exactly the gap that cleanup created. The fix going forward isn't a code change; it's a process note: after live-browser verification of a feature the user is likely to keep exploring by hand, either leave the dev servers running, or explicitly tell the user they were stopped as part of cleanup so the gap is visible rather than silently discovered via a confusing error message.
