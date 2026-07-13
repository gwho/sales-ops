# Explanation — Phase 12: Postgres-Backed Latest-Session Dashboard

This is the deep-reasoning record: for each major decision, what the alternatives actually cost, and how the decisions chain into each other. Read `session.md` first for the factual sequence — this document exists to teach the *why* behind each answer, not repeat *what* was decided.

## 1. Why `localStorage` + header, not cookies — and why that choice ripples through the whole design

The very first fork was how an anonymous visitor's identity gets carried on each request. Two real options existed:

- **A cookie**, set by the server, sent automatically by the browser on every request to that origin.
- **A client-generated UUID in `localStorage`**, attached manually as a header on every fetch.

Cookies feel like the "normal" way to do session identity, and in a same-origin app they would be. But this app's frontend (Vercel) and backend (Render) are **different origins**. A cross-origin cookie requires:

- `SameSite=None; Secure` on the cookie itself (without this, most browsers won't send it cross-site at all).
- `Access-Control-Allow-Credentials: true` on the CORS response.
- `credentials: 'include'` on every single `fetch()` call on the frontend.
- Awareness that some browsers (Safari's ITP, Firefox's Enhanced Tracking Protection, various privacy modes) actively degrade or block third-party-style cookies even with all of the above configured correctly.

None of that complexity buys anything here, because there's no security property being protected — this is not authentication, there's no session to hijack that matters, and the "identity" is disposable by design (clearing storage just starts a new one). The localStorage+header approach sidesteps the entire cross-site cookie problem class, at the cost of one thing: the frontend has to explicitly attach the header on every request, and — critically — **cannot get that header value anywhere a Server Component render happens**, because `localStorage` is a browser-only API.

That last clause is not a footnote. It is the reason Q8 exists at all.

## 2. The Q1 → Q8 coupling: why the dashboard couldn't stay a Server Component

Q7 settled the shape of `GET /api/dashboard` and, almost as an aside, described the frontend consuming it as "an async Server Component with `force-dynamic`." That framing wasn't examined critically in the moment — it was inherited from the *old*, paused SQLite plan, where the dashboard query was global and non-session-scoped (there was no session concept in that design at all; the whole point was a disposable, rebuilt-every-startup demo database everyone saw the same version of).

Q8 caught the mismatch: a Next.js Server Component's `fetch()` call executes **on Vercel's server**, during the render that produces the HTML sent to the browser. That server-side code has no access to the browser's `localStorage` — there's no session ID to attach, and (per Q1) no cookie to fall back on either. An RSC fetch to `/api/dashboard` would therefore *always* look like a brand-new, sessionless visitor, no matter how many times a real visitor had actually run a workflow. The dashboard would silently never show anyone's real data — a bug that would be invisible in casual testing (the page still renders, still shows sample data, looks completely normal) and would only surface as "wait, why doesn't my dashboard ever update?"

The fix follows directly from where the identity actually lives: the fetch has to happen **in the browser, after the page has hydrated**, which means a **Client Component**. This isn't a new pattern for this codebase — the three workflow pages already do exactly this shape (client-side fetch triggered by user action, with `RequestStatus` state). The dashboard's version triggers on mount instead of on a button click, but it's the same idiom, not an exception to it.

The teaching point: **a session-identity decision and a data-fetching-architecture decision are not independent.** Choosing `localStorage` over cookies wasn't just "simpler CORS" — it structurally forced the read side into a specific rendering strategy. A design review that only looks at the read path in isolation (as Q7 initially did) will miss this; you have to trace where the data the read path depends on actually lives.

## 3. Why persistence is best-effort, not required — and why the outcome still can't be silent

The write path had two live tensions to resolve simultaneously:

**Should a DB failure fail the request?** No — and the reasoning is about what's actually being demoed. The three workflow endpoints exist to prove a real, tested business computation (validate orders, allocate inventory, age payments). That computation is *already complete and correct* by the time persistence is even attempted. Free-tier infrastructure (Neon, Render) has real, expected transient hiccups — cold starts, connection pool exhaustion, brief network blips. If a save failure turned a perfectly valid, correctly computed result into a `500`, the user-visible failure mode would be "upload a good spreadsheet, get an error" — which is a *worse* bug than the dashboard occasionally being one run stale. The persistence feature's failure mode should never leak backward into the feature it's layered on top of.

**But should the outcome be invisible?** Also no, for the opposite reason: a `200` response that looks identical whether or not the save landed is a *silent data-loss trap*. A user would have no way to know their dashboard might not reflect this run. That's why `X-Persisted` exists as a separate, mandatory signal — not folded into the JSON body (which is a governed Output Contract that shouldn't carry transport metadata), but as a response header, checked by the frontend and surfaced (only on `false`) via `PersistenceNotice`.

This is a specific instance of a general pattern worth internalizing: **"best effort" and "silent" are not the same thing, and conflating them is how systems develop invisible reliability gaps.** Best-effort means "don't let this dependency's failure become your failure." It does not mean "don't tell anyone this dependency failed."

### The gap the tests found: best-effort has to be enforced at every layer that claims it

The repository (`WorkflowResultsRepository.save()`) was written to catch its own exceptions and return `False` rather than raise — a correct, self-contained implementation of "never raises." The routers were originally written to trust that contract completely: call `repo.save(...)`, use the return value, no `try/except` at the call site.

While writing the *route-orchestration* tests — specifically the one verifying "a raising repo call still returns 200" — this broke, because a test double that raises on purpose bypasses the real repository's own internal guarantee entirely. The route had nothing defending it if the repository it was calling ever regressed (or, in tests, was deliberately swapped for something that doesn't uphold the contract).

The fix was to extract a shared `persist_workflow_result()` helper with its *own* `try/except`, used by all three routers. This is defense in depth applied correctly: the repository still promises never to raise (so its direct callers in production don't need to think defensively about it), but the router layer *also* doesn't bet the whole request on that promise holding forever. Two independent layers enforcing the same invariant is not redundant — it's what makes the invariant actually load-bearing instead of aspirational. This is also a nice concrete example of tests changing a design *after* the design was "approved" — the plan didn't call for this helper; the act of writing a test for a stated behavior ("a raising repo call still returns 200") revealed that the code as planned didn't actually satisfy it.

## 4. Why one JSONB table, not a normalized schema like the paused SQLite plan

The earlier, paused SQLite design normalized each Output Contract row family into its own table (`valid_order_lines`, `allocation_results`, `aging_rows`, etc.), because its job was fundamentally different: it seeded a **fixed, rebuilt-every-startup demo dataset** and needed to support arbitrary SQL reporting queries (`GROUP BY`, `SUM`, business-order `CASE` sorts) across that dataset, to genuinely demonstrate SQL fluency as a portfolio skill.

Phase 12's actual read pattern is "give me the one latest full result for this session and this workflow type." There is no cross-row, cross-session, or aggregate query anywhere in the design. Given that, normalizing into per-row tables would recreate a real cost with no matching benefit: **every field in every Output Contract would now need to be mirrored as a SQL column**, and any time an Output Contract's shape changed (a field added, renamed, or removed in `src/contracts.py`), someone would need to remember to change the SQL schema too — exactly the kind of dual-source-of-truth drift this project's own "Field Scope Boundary" discipline exists to prevent for the Python contracts themselves. Storing the contract's own JSON verbatim in a `JSONB` column sidesteps that duplication entirely: there is only ever one shape definition (`src/contracts.py`), and Postgres just holds whatever that shape produced.

The tradeoff being accepted: you give up the ability to write arbitrary SQL analytics over the stored data (e.g., "average outstanding amount across all sessions" is not a query this schema supports well). That's fine, because Phase 12 was never trying to be that — a future phase that actually wants cross-session analytics is a different problem with different requirements, and should design its own schema for it rather than overloading this one.

## 5. `result_schema_version`: why a version integer matters even with JSONB

Storing verbatim JSON avoids *schema* drift (the SQL columns can't get out of sync with the contract, because there are no SQL columns mirroring the fields). It does **not** avoid *data* drift: a row saved six months ago, under an older version of `OrderValidationResult`, is still sitting in Postgres exactly as it was written. If a field gets added to that contract later, the *old* row is still missing it — and naively serving that old row to a frontend now built against the new shape is a real, unhandled-null-style runtime error waiting to happen.

`result_schema_version` is the mechanism that prevents that: every save records which version of the contract shape it was saved under, and the read path checks that recorded version against the *current* version (from `CONTRACT_SCHEMA_VERSIONS` in `src/contracts.py`) before trusting the row. A mismatch is treated exactly like a missing row — fall back to sample data for that one workflow type.

The mechanism only works if the version number actually gets bumped when it should, though — and that's a discipline problem, not a code problem. Nothing *forces* a developer editing `OrderValidationResult`'s fields to remember to bump `CONTRACT_SCHEMA_VERSIONS["order_validation"]`. This is the same class of problem this project had already learned once before, in a completely different context: "regenerate mock-data after any sample-data change" is a similarly unenforced-but-critical discipline rule recorded in this project's history. The mitigating design choice here was to put the version constant *physically next to* the TypedDicts it governs, inside `src/contracts.py` itself, so a developer editing a contract's fields is looking directly at the version dict in the same file — maximizing the odds they notice, without pretending code alone can guarantee it.

## 6. Migrations: why single-transaction batching, why an advisory lock, why checksums, why a bounded retry

Each piece here defends against a different, specific failure mode — worth separating them out:

- **Single transaction for the whole batch, not one per file.** `pg_advisory_xact_lock` is transaction-scoped — it releases automatically when its transaction ends. If each migration file got its own transaction (and thus its own lock acquire/release), there would be a window *between* files where the lock is not held, during which another process (e.g., two Render instances briefly overlapping during a deploy) could interleave and apply migrations out of order or concurrently. Wrapping the whole batch in one transaction means the lock is held continuously from the first pending file to the last.

- **`schema_migrations` owned by the runner, never by a migration file.** This is a separation-of-concerns question: `schema_migrations` is *bookkeeping about migrations*, not *application schema*. If a numbered migration file were responsible for creating it, you'd have a chicken-and-egg problem (how do you know if *that* migration has run, before the table that tracks that exists?) and a conceptual muddle (is `schema_migrations` versioned by itself?). Keeping it entirely outside the versioned-file system avoids both.

- **Checksums on already-applied files.** Without this, someone could edit an old migration file's contents after it's already been applied elsewhere (locally, or in production), and the runner would have no way to detect that the file it's looking at no longer matches what was actually run. Recording a SHA-256 of each file's content at apply time, and comparing it on every subsequent boot, turns "someone silently edited history" into a loud startup failure instead of a silent, hard-to-diagnose schema mismatch.

- **Bounded retry on the initial connection, capped under Render's health-check timeout.** This one is about tolerating a *known, expected* failure mode rather than a bug: Neon's free tier can suspend compute after inactivity and take a moment to wake on the next connection. Treating the very first connection attempt as pass/fail with no tolerance would make an ordinary cold start indistinguishable from a genuinely broken database — both would fail startup. A short, bounded retry (not infinite — a database that's *actually* down should still fail closed) absorbs the expected case without weakening the guarantee for the unexpected one. The "must stay under Render's own timeout" constraint is what stops this retry from trading one failure mode for a different one: a retry loop that runs *longer* than Render's own patience would make Render kill the deploy anyway, just with a more confusing error.

## 7. The three startup/runtime database states, and why conflating any two of them is wrong

This is the single most refined piece of reasoning from the Plan Mode review rounds, because the first draft only distinguished two states and the real system has three:

1. **`DATABASE_URL` unset.** Not an error — persistence is *intentionally* off for this run. The app boots normally, workflow endpoints report `X-Persisted: false` (accurately — no save was attempted), and `GET /api/dashboard` returns `200` with everything `null` (also accurate — there's nothing to have saved). This is what keeps local development and the test suite hermetic with zero configuration.
2. **`DATABASE_URL` set but unreachable at boot.** This is a real failure, but a *startup*-time one — the migration runner's own connection attempt is what fails (after the bounded retry above exhausts). The correct response is fail-closed startup: don't serve any traffic at all, rather than serving a partially-working app.
3. **`DATABASE_URL` set, app already running, then the database becomes unreachable.** This is a genuine *runtime* failure, and it's the one and only case that should produce `GET /api/dashboard`'s `503`.

The reason it matters to name all three separately: states 1 and 3 produce superficially similar symptoms from the read path's perspective ("no data available"), but they mean completely different things and deserve different HTTP semantics. Collapsing 1 and 3 into "always `200` all-null" would hide a real outage behind a response that looks identical to "you just haven't tried anything yet" — dishonest to anyone trying to understand what's actually happening. Collapsing 2 and 3 (as an early verification-recipe draft accidentally did, by simulating "outage" with an unreachable `DATABASE_URL` from the very start) tests the wrong code path entirely — you can't get a running server's `503` from a server that never finished booting.

## 8. Testing strategy: why two layers, and why the split is exactly where it is

The two-layer test suite (mocked-repository route-orchestration tests vs. real-Neon repository/SQL tests) isn't just "some tests are fast and some are slow" — it's drawn at a specific, principled boundary: **what's actually being verified**.

The route-orchestration layer answers "does the *endpoint* do the right thing given a repository that behaves a certain way?" — 400 on malformed header, `X-Persisted` set correctly for each of the three save outcomes, a raising repo call still yielding 200. None of that depends on real SQL semantics at all; a hand-written fake object that returns configured values is not just adequate here, it's *more precise*, because it can trivially simulate cases (like "the repository raises") that would be awkward or slow to provoke against a real database on demand.

The repository layer answers "does the *SQL* actually do what it claims?" — does the upsert really overwrite and really advance `saved_at`, does the JSONB round-trip survive real values without silent coercion, does the checksum-mismatch path really refuse to proceed, does the advisory lock really apply. None of that can be verified by a mock, almost by definition — a mock of the repository can't tell you whether the SQL *inside* the repository is correct, because the mock has no SQL in it at all. This layer has to hit something that speaks real Postgres, and since Neon's `test` branch already *is* real Postgres, there's no meaningful correctness gap left for a Docker-based alternative to close — only provider-parity concerns (connection behavior, SSL, pooling) that a deploy-time smoke check addresses better than a unit suite would anyway.

The `TEST_DATABASE_URL` vs. `DATABASE_URL` split exists for a narrower, sharper reason than "organization": a rollback-based or cleanup-based test suite that shared an env var with the app's own connection string would be one copy-paste or one forgotten local override away from running destructive test operations against `dev` or, worse, `main`. Making it a structurally different variable name means that mistake is no longer possible by accident — it would require actively setting `TEST_DATABASE_URL` to a production string on purpose.

## 9. Display Expiry: a deliberately narrow claim, not a privacy feature in disguise

The TTL mechanism (default 30 days) intentionally does exactly one thing: it makes `GET /api/dashboard` stop returning a row once it's stale, funneled through the *same* "is this row usable?" predicate that already handles schema-version mismatches. It deliberately does **not** delete the row. The reasoning for accepting "hidden but not deleted" rather than building real deletion:

- The bounded-per-session row count (at most 3 rows, ever, per anonymous visitor, because every save is an upsert on a fixed primary key) means storage growth tracks unique visitors, not runs — a real capacity concern that active deletion would solve doesn't actually exist yet at this project's scale.
- Building deletion machinery (even the lightweight "opportunistic delete-on-write" version that was named as the future upgrade path) is complexity spent solving a problem that isn't there yet, which cuts against this project's stated preference for not building speculative infrastructure.

The part worth internalizing as a general principle: it would have been easy to describe this feature loosely as "old data gets cleaned up" and let a reader infer a privacy/deletion guarantee that isn't actually true. The ADR is deliberately explicit that this is *display* expiry, not deletion — naming the limitation precisely, rather than letting a vaguer description imply something stronger than what was actually built.
