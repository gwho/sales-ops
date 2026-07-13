# Discussion Topics — Phase 12: Postgres-Backed Latest-Session Dashboard

Grouped by concept. Use these to test whether the reasoning in `explanation.md` actually transferred, not just the conclusions in `session.md`.

## Session identity & cross-origin architecture

1. Why does a cross-site cookie require `SameSite=None; Secure` specifically, and what would actually happen in the browser if that cookie were set as `SameSite=Lax` (the common default) instead, on a request from Vercel to Render?
2. The design explicitly rejects cookies partly because "there's no security property being protected." What would have to be true about this app for that argument to *not* hold — i.e., under what circumstances would the anonymous-identity mechanism need the properties only a cookie (specifically `HttpOnly`) can provide?
3. `get_session_id` validates via `uuid.UUID(value)`, accepting any RFC4122 version rather than requiring v4 specifically (which is what `crypto.randomUUID()` always produces). What's the argument for that leniency, and can you construct a value that a stricter v4-only check would reject but this check accepts?
4. Why must the frontend *omit* `X-Session-Id` entirely when no ID is available, rather than sending `X-Session-Id: ""`? Trace exactly what `get_session_id` does with each of those two inputs and where the divergent behavior matters downstream.

## The Q1 → Q8 coupling (session identity vs. rendering strategy)

5. Explain, in your own words, why an async Server Component fetching `GET /api/dashboard` would produce a plausible-looking but silently wrong dashboard, rather than an obvious error. What would you have to specifically test to catch this bug if it had shipped?
6. If Q1 had gone the other way (a cross-site cookie), would `app/dashboard/page.tsx` have been able to stay a Server Component? Walk through what would still need to change and what wouldn't.
7. `DashboardLiveSections` fetches on mount inside a `useEffect`. What's the very first thing rendered before that fetch resolves, and why was "render sample data immediately, then swap to live data" explicitly rejected as an alternative?

## Best-effort persistence & failure semantics

8. `X-Persisted` has three states (`true`/`false`/`skipped`), not two. Why is `skipped` (no session at all) treated as meaningfully different from `false` (a session was supplied, but the save failed) rather than being folded into the same "not saved" bucket?
9. The repository's `save()` method promises never to raise. The router layer *also* wraps the call in a `try/except` via `persist_workflow_result()`. Is this redundant? Under what future change to the codebase would the router-level guard be the only thing standing between a repository bug and a broken user-facing request?
10. Why does persistence happen inside the existing `POST /api/orders/validate` endpoint rather than as a separate `POST /api/dashboard/save` endpoint called by the frontend afterward? What specific problem would the separate-endpoint design have, given ADR 0006's "never trust a client-supplied result" principle?
11. `POST /api/inventory/allocate` computes a full `OrderValidationResult` internally (to get valid orders to allocate) but never persists it. What's the argument against persisting it as a convenience, and what would break about the `X-Persisted` contract if it tried to?

## Storage schema design

12. The paused SQLite plan normalized data into per-row tables; Phase 12 stores one JSONB blob per workflow result. What's the actual query Phase 12's `GET /api/dashboard` needs to run, and why does that specific query pattern make normalization unnecessary here even though it was the right call for the SQLite design?
13. `result_schema_version` exists even though the JSONB approach already avoids *schema* drift (no SQL columns to keep in sync). What's the *different* kind of drift it protects against, and why doesn't storing verbatim JSON automatically solve that one too?
14. The version constant lives inside `src/contracts.py`, physically next to the TypedDicts it versions, rather than in a separate config file. What failure mode is that placement specifically trying to reduce the odds of, and why is it only a mitigation rather than a guarantee?

## Migration safety

15. Why does batching all pending migrations into a single transaction (rather than one transaction per file) matter specifically for the advisory lock's effectiveness? What's the concrete bad scenario a per-file-transaction design would allow that the single-transaction design doesn't?
16. What problem does recording a checksum for each applied migration solve that recording just the migration's *name/version* would not?
17. The bounded connection retry at startup is capped to stay under Render's own health-check timeout. What happens if that retry window is set *longer* than Render's timeout — walk through the actual failure sequence.

## The three database states

18. The design distinguishes three states: `DATABASE_URL` unset, `DATABASE_URL` set-but-unreachable-at-boot, and a post-startup runtime outage. Which HTTP behavior does each one produce from `GET /api/dashboard`, and why would collapsing the first and third into "always return `200` all-null" be dishonest rather than just simpler?
19. An early draft of the verification plan tried to simulate the runtime `503` case by pointing `DATABASE_URL` at an unreachable host *before* starting the app. Why does that actually test a completely different code path? What's the correct way to simulate a genuine post-startup outage instead?

## Testing strategy

20. The route-orchestration tests use a hand-written fake repository rather than mocking individual methods with a mocking library. What specific test in this suite (verifying a raising repository call still returns 200) would be awkward or impossible to write cleanly against a real Postgres connection, and why is a fake object well-suited to it?
21. `TEST_DATABASE_URL` is a separate environment variable from `DATABASE_URL`, even though both ultimately point at Neon Postgres. What concrete mistake does that separation prevent that careful code review alone would not reliably catch?
22. Why does hitting a real Neon branch in the repository test layer actually verify something a mocked-repository test structurally cannot, even in principle?

## Data lifecycle (TTL / Display Expiry)

23. "Display expiry" is explicitly described as not a deletion guarantee. What's the actual difference in system state between a TTL-expired row and a genuinely deleted row, and what would need to change about this design before it *could* honestly be called a privacy/deletion feature?
24. The design defers building active deletion, citing the bounded-per-session row count as the reason there's no real storage problem yet. What would have to change about this app's usage pattern for that reasoning to stop holding?
