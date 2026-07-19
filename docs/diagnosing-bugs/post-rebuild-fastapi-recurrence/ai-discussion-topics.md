# AI Discussion Topics — Post-Rebuild FastAPI Recurrence

## Group 1 — Feedback loops and evidence

1. The diagnosis note pre-built the Phase 1 feedback loop before the session started. What would this diagnosis have looked like if that command had to be discovered from scratch — what would the first three things tried have been?
2. Why does `curl -fsS --max-time 3 http://127.0.0.1:8000/health` count as "specific" rather than just "fast"? What would a *non*-specific version of this same check look like, and what could it wrongly call green?
3. The listener check (`lsof -iTCP:8000 -sTCP:LISTEN`) was run *before* starting FastAPI. What would that same check have shown under hypothesis 2 (crashed during DB init) versus hypothesis 1 (never started)? Could the listener check alone have distinguished those two?

## Group 2 — Hypothesis discipline

4. Hypotheses 2 and 4 were "ranked but not yet tested" before the single start attempt. What made the start attempt itself sufficient to falsify both, rather than requiring two separate tests?
5. Why generate 5 ranked hypotheses when the listener evidence already strongly favored one? What's the risk of skipping straight to the top-ranked hypothesis without stating the others?
6. If the FastAPI start attempt had instead shown outcome 3 (retries and exits during Postgres connection), which of the original 5 hypotheses would have been confirmed, and what would the very next command to run have been?

## Group 3 — The persistence side-finding

7. Walk through exactly how `if self._pool is None: return False` was identified as the cause of `X-Persisted: false` without running a debugger or adding a single log line. What made the *absence* of certain log lines as informative as their presence would have been?
8. Why was it correct to stop investigating once the pool-is-None line was found, rather than immediately asking "why is the pool None"? What's the actual boundary between "found the proximate cause" and "found the root cause," and which one was reached here?
9. The developer chose to leave the persistence gap uninvestigated in this session. What's the cost of chasing it anyway, and what's the cost of deferring it? Was recording the observed facts in a separate note a reasonable middle ground?

## Group 4 — Scope and process discipline

10. The note explicitly listed several "false fixes" not to apply (retry loops, changing `127.0.0.1` back to `localhost`, weakening CORS). For each one, what evidence would have made it look tempting if the diagnosis had been done less carefully?
11. Why did `/recover` correctly not fire, even though the note's own title calls this a "recurrence"? What's the precise difference between a symptom recurring across sessions and a fix failing within one session?
12. The three "prevention options" (documentation-only, preflight-only, combined orchestration) were presented to the developer rather than chosen automatically. Why does the note insist prevention must be chosen only *after* the cause is proven, and what could go wrong if a "combined orchestration" tool had been built before this session confirmed the cause was simply "never started"?
13. This diagnosis produced a clean "no code change required" outcome. What would change about the required verification gates (per the note's own "Verification gates" section) if a real code change *had* been necessary instead?
