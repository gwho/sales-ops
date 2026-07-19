# Findings — Post-Rebuild FastAPI Recurrence Fix

## Finding 1: Local persistence save fails silently (`X-Persisted: false`) with `DATABASE_URL` set

**What the problem is:** a real, successful workflow computation (`POST
/api/orders/validate` against the actual sample files) returns a correct
`200` with a fully computed result, but the best-effort save behind it
reports `X-Persisted: false`. `WorkflowResultsRepository.save()`
(`backend/repositories/workflow_results.py:81-82`) has three distinct
failure paths — non-finite JSON values, an exception during the `INSERT`,
and `self._pool is None` — and only the third produces no log line at all.
That third path is what fired here, confirmed by the complete absence of
either of the other two paths' `logger.exception` calls in the captured
startup/request log, and the absence of `backend/db.py`'s
"`DATABASE_URL is not set`" log line (which would fire if the env var were
genuinely unset, and didn't).

**Why this matters beyond this one request:** the project's own architecture
docs (`context/architecture.md`'s "Persistence" section) describe this as a
best-effort layer specifically designed to *never* fail the surrounding
request — which is working exactly as designed here (the workflow request
still succeeded). But "never fails loudly" and "silently broken" are two
different things, and this repository currently can't distinguish between
them from the outside without reading source code and cross-referencing log
output by hand, the way this review did. A developer relying on the `/dashboard`
"latest results" feature locally would see stale/sample data indefinitely
with no error surfaced anywhere in the UI, the API response, or (in this
case) even the server log.

**What the correct pattern would look like:** at minimum, the silent
`if self._pool is None: return False` branch should log something —
even at `debug`/`info` level — distinguishing "never configured a pool" from
"configured but failed to save this specific record," so a future
investigation doesn't have to reconstruct that distinction by process of
elimination the way this review did. This wasn't fixed in this session (see
`docs/debug-ideas/local-persistence-pool-none/observed-facts.md` for why and
what's recorded for next time) — noted here as the standards-level gap, not
as something silently patched.

## Finding 2: "Verified" must mean what was actually checked, not what the fix is expected to have accomplished

**What the problem is:** this diagnosis fixed a browser-visible symptom
without ever using a browser. Every check that curl could perform (health,
dashboard JSON shape, CORS preflight headers, a full sample-file workflow
round-trip) was run and confirmed green. But several things curl cannot
observe — a JavaScript console error, a hydration mismatch, whether the
literal banner text actually disappears from the rendered page, keyboard
focus behavior — were not checked, because no browser-control tool was
available in this session.

**Why this matters beyond this one fix:** it would have been easy, and not
obviously wrong to a casual reader, to write "fix verified" and move on,
since every automatable check passed and the root cause (absent process) is
about as unambiguous as root causes get. The discipline that matters here is
narrower and more useful: state exactly which checks were run and which
weren't, rather than letting a high-confidence diagnosis quietly stand in
for a claim of full verification. This same discipline already exists
elsewhere in this project — the Landing Page Evidence and Technical
Credibility feature's own `/project-review` (see
`docs/plan/landing-page-evidence-and-technical-credibility/`) flagged its
own pending live-browser checklist the same way, for the same underlying
reason (no browser tool available in that session either). This finding is
really a confirmation that the pattern held a second time, not a new
discovery — worth naming explicitly so it's recognized as this project's
established convention, not a one-off caveat.

## Finding 3: no local-development instructions existed in `README.md` before this session

**What the problem was:** `README.md` documented `uv sync`/`uv run pytest`
and the deployed production URLs, but had no section at all describing how
to run the app locally — not `npm run dev`, not the FastAPI start command,
not the fact that they're two independent processes. This is very likely
why the symptom in this diagnosis occurred in the first place: there was no
written checklist anywhere prompting "start both services," so a developer
(or an agent session) starting only the frontend for a quick check had no
documented reminder that the backend needed its own terminal.

**Why this matters beyond this one incident:** the project's architecture
has been a genuinely two-service local setup since Phase 10
(`context/architecture.md`'s "Current development shape" note), but the
README never caught up to describe that reality for a new developer
encountering the repo. This is the kind of gap that's easy to miss because
each individual session's author already knows how to run the stack from
memory — the gap only becomes visible when someone hits the exact symptom
this diagnosis addressed. The fix (documentation-only, per explicit
developer choice) directly closes this specific gap; it does not address
the deeper pattern of "does every architecturally significant local-dev
requirement have a corresponding README entry," which would be a reasonable
question for a future, broader documentation audit.
