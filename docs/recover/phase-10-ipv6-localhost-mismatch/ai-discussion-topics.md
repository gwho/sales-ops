# AI Discussion Topics: IPv6/localhost Loopback Mismatch

## The Failure Mode

1. Why does `localhost` resolving to two different addresses (`127.0.0.1` and `::1`) only become a problem when the two communicating processes disagree about which one to use — what would have to be true for it to never matter?
2. What is "Happy Eyeballs" (RFC 8305), and why do some network stacks implement it while others (like the headless test browser used during diagnosis) apparently didn't exhibit the same behavior?
3. Why did `curl` in this diagnosis session not hit the same bug that the user's real browser did? What does that tell you about relying on `curl` as a stand-in for "does this work in a browser"?

## Diagnostic Process

4. The session tried three hypotheses (backend down, wrong port, stale cache) before finding the real cause. Each one was individually reasonable to check first. What ordering principle made each one worth trying before the eventual real answer?
5. What was the specific piece of evidence that shifted the diagnosis from "keep checking plausible causes" to "look for a mechanism that explains an environment difference"? Could that shift have happened one hypothesis earlier?
6. A fresh headless-browser repro succeeding while the user's real browser failed, on the identical URL, was itself treated as a clue rather than a dead end. Why is "my test can't reproduce it, but the report is real" often more informative than either "it reproduces" or "it doesn't" alone?

## The Fix

7. Why was the fix applied on the frontend (`lib/api-client.ts`'s target URL) rather than the backend (making uvicorn bind to `::` or `0.0.0.0` to accept both address families)? What would the backend-side fix have cost that the frontend-side fix didn't?
8. What's a scenario where the backend-side fix (bind to both families) would actually be the more correct choice, despite being more invasive here?
9. Why doesn't this fix require any change to the CORS `allow_origins` configuration? What's the precise difference between "the origin a request comes from" and "the address a request is sent to"?

## Prevention

10. `fastapi dev backend/main.py` was run with no explicit `--host` flag, silently defaulting to IPv4-only. What would it look like to make that choice deliberate and documented, rather than an accidental default nobody revisited?
11. If this project later adds a `.env.local` or deployment config with a different `NEXT_PUBLIC_API_BASE_URL`, could this exact bug resurface in a different form? What would need to be true of that value to avoid it?
