# AI Discussion Topics: Backend-Not-Running Diagnosis

## The Failure Mode

1. Why does `curl` return an HTTP status code of `000` when nothing is listening on the target port, instead of a normal `4xx`/`5xx`? What's actually happening at the TCP layer?
2. `fetch()` in the browser throws (rejects the promise) rather than resolving with an error `Response` in this scenario. What specific class of failures makes `fetch()` throw versus resolve with a non-`ok` response? Where's the line?
3. If CORS had *also* been misconfigured at the same time as the backend being down, would the reported error message have looked any different? Why or why not?

## The Diagnostic Process

4. Why was `curl -sf .../api/templates/orders` chosen as the loop instead of, say, trying to reproduce the bug in a browser first?
5. What did checking `lsof -i :3000` in addition to `:8000` actually rule out? What would a diagnosis that skipped this check have risked getting wrong?
6. The resolution used a second, more elaborate `curl` chain (fetch two templates, then POST them with an `Origin` header) after the first simple check already went green. Was this second check necessary, or was the first one sufficient? Argue both sides.
7. Suppose the first `curl` check had returned `HTTP 500` instead of connection failure. What would that have implied instead, and how would the next diagnostic step have differed?

## Regression Testing (or the Lack of It)

8. The `diagnosing-bugs` skill says "if no correct seam exists, that itself is the finding." Why can't a `TestClient`-based pytest test ever catch "someone forgot to start the dev server"? What would have to be true about the test for it to catch this class of bug?
9. Is there *any* automated way to prevent this specific class of bug (an agent tearing down infrastructure a human then relies on) — not a unit test, but some other mechanism? What would it look like?

## Process Lessons

10. Why did this bug surface specifically right after live-browser verification, rather than at some other point in the session? What does that timing tell you about when this kind of gap is most likely to appear?
11. The resolution suggests two alternatives going forward: leave dev servers running after verification, or explicitly announce that they were stopped. What are the trade-offs of each? Is there a third option?
12. This diagnosis took a handful of commands and a few minutes. What made it fast? Which specific discipline from the `diagnosing-bugs` skill (tight loop first, no theorizing before reproduction, etc.) contributed most directly to the speed here?
