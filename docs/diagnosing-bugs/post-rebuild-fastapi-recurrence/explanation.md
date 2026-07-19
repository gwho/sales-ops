# Explanation — Post-Rebuild FastAPI Recurrence

## 1. Why the feedback loop needed zero construction

The diagnosing-bugs skill normally spends its most disproportionate effort on
Phase 1 — building a feedback loop from scratch is usually the hard part. Here
it wasn't, because the diagnosis note itself (`recurrence-first-diagnosis.md`)
had already done that work: it named the exact command
(`curl -fsS --max-time 3 http://127.0.0.1:8000/health`), stated why it was
red-capable/deterministic/fast/specific, and had already run it once with
captured output before the session even started. This is worth noticing as a
pattern: a well-written diagnosis note can front-load Phase 1 entirely, and
the executing session's job becomes re-verifying that loop still reproduces
(it did — same exit code 7) rather than inventing one. That re-verification
step still mattered, though — the note's captured evidence was from an
earlier moment, and the executing session confirmed it was still true *right
now*, not just historically true.

## 2. Why "one start attempt, don't loop" was the right instruction

The note's Phase 2 explicitly said: "Do not immediately background or restart
it in a loop." This might look like unnecessary caution for something as
simple as starting a dev server, but it encodes a real debugging principle:
if you background-and-forget a process, you never actually observe its first
few seconds of behavior — which is exactly the window where outcome 2 (exits
during import), outcome 3 (exits during DB init), or outcome 4 (can't bind)
would show themselves. A loop that restarts on failure without a human (or
agent) reading the output between attempts turns a diagnostic signal into
noise — you'd just see "it's down" repeatedly without ever learning why. The
actual execution here used `nohup ... &` but then explicitly `sleep 5` and
read the full log before doing anything else, and re-checked again 3 seconds
later — satisfying the spirit of "one attempt, fully observed" while still
running it non-interactively.

## 3. Why hypotheses were ranked even though the answer seemed obvious

Before starting FastAPI, the listener check already showed port 8000 with
*zero* processes bound to it — about as strong a piece of evidence as exists
for "nothing is running here." It would have been easy to skip straight to
"just start it" without formally ranking hypotheses 2 through 5. The
diagnosing-bugs skill's Phase 3 requires generating 3-5 ranked, falsifiable
hypotheses specifically to prevent anchoring on the first plausible idea — and
in this case, doing so wasn't wasted effort: hypothesis 4 (CORS/origin
mismatch) and hypothesis 2 (DB-startup crash) were both real possibilities
that the listener check alone didn't rule out. Only after the actual start
attempt succeeded *and* a CORS preflight came back correct *and* a real
workflow request round-tripped successfully were hypotheses 2 and 4 actually
falsified, not just assumed away.

## 4. How the persistence side-finding was discovered without touching code

The `X-Persisted: false` header on an otherwise-successful workflow POST could
easily have been ignored — the reported symptom (backend unreachable) was
already fixed by that point, and this was a passing verification check, not
the thing being debugged. It surfaced because the note's own verification
checklist (item 5: "if local persistence is enabled, confirm... the dashboard
reflects the saved workflow result after reload") was followed literally: a
`GET /api/dashboard` after the workflow POST showed `order_validation` was
still `null`, which is the concrete, falsifiable signal that "best-effort"
didn't just skip logging a success — it genuinely didn't save. From there, the
investigation stayed strictly read-only: grepping `persistence.py` and
`workflow_results.py` for `logger`/`except` calls, reading the exact lines
around each `return False`, and cross-referencing which log lines *did* and
*didn't* appear in the captured startup/request log. The absence of specific,
already-known log lines (`"DATABASE_URL is not set..."`, `logger.exception(...)`
inside `save()`) was itself the evidence that narrowed the cause to the one
remaining silent path (`if self._pool is None: return False`) — without ever
running a debugger, adding instrumentation, or touching a single line of
application code. This is a good example of Phase 4's "targeted logs at the
boundaries that distinguish hypotheses" principle applied to *reading existing
logs* rather than adding new ones — the code's existing logging discipline
(one log line per distinct failure path) was thorough enough that the process
of elimination worked without any new instrumentation at all.

## 5. Why this stayed a side-finding instead of becoming a second investigation

It would have been reasonable to keep pulling this thread — the pool-is-None
path was found in minutes, and the next question ("why is the pool None") felt
close. Two things stopped that: the diagnosis note's own explicit scope
("with a narrower boundary... do not change Python business rules... without
evidence that they cause startup failure" — this gap doesn't cause startup
failure, it's a separate write-path issue), and, more directly, asking the
developer which of the two flagged items to prioritize rather than deciding
unilaterally. The answer — leave it, record the facts, diagnose separately —
matches the diagnosing-bugs skill's own boundary discipline: a feedback loop
built for one bug shouldn't quietly absorb a second, unrelated bug just
because it was noticed along the way. Mixing the two would also have made the
regression story for *this* fix murkier — "no code change required" is a
clean, verifiable claim; "no code change required, except for this other
thing I also poked at" is not.

## 6. Why `/recover` correctly never fired despite the note's title calling this a "recurrence"

The note's title and framing ("Post-Rebuild FastAPI Recurrence") describe the
*symptom* recurring — the same browser-visible banner appeared again, as it
had before in `fastapi-localhost-connectivity/`. That is not the same as the
diagnosing-bugs/`recover` trigger condition, which is about a *fix* recurring
to fail: "one clean attempt to start FastAPI does not stay running, or the
same symptom returns again after a claimed corrective fix." No corrective
attempt was made and then failed here — the very first, only start attempt
worked and stayed up. The note anticipated this distinction explicitly
("This is already a recurrence, so do not stack speculative patches") as a
caution against a *different* failure mode (someone panic-patching code
without diagnosing first) — not as a mandate to invoke `/recover` regardless
of outcome. Recognizing that a symptom recurring across sessions and a fix
failing within a session are different things is the actual judgment call
this step required.
