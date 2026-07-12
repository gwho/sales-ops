# AI Discussion Topics: Phase 10 Grilling Session

## Statelessness & Architecture

1. Why does a two-phase "generate report, get an ID, fetch it later" API design require server-side persistence, even if that persistence is just an in-memory dict that resets on restart?
2. What's the minimum change you'd need to make to this codebase to support "revisit a report I generated 10 minutes ago"? Sketch it, and identify which of today's decisions it would have to reverse.
3. `ReportManifest.report_id` is `f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"`. Why is a *deterministic* ID (as opposed to a random UUID) a giveaway that no real lookup table was ever intended?
4. What's the actual difference between "the client holds the latest result in its own state" (Current Result) and "the server holds session state"? Why does only one of these count as a stateless architecture?

## Trust Boundaries

5. Why is "recompute from source instead of trusting client JSON" a security-relevant decision, not just a style preference?
6. Describe a concrete scenario where trusting a client-supplied Workflow Result as report input would let someone produce a misleading "official" artifact.
7. What's the general principle being applied here ("don't accept as authoritative anything you couldn't have produced yourself"), and where else in a typical web app does that principle show up?
8. The session accepted a duplicate-upload cost as a trade-off for this trust boundary. Under what conditions (file size, compute cost, request volume) would that trade-off stop being acceptable, and what alternative would you reach for instead?

## FastAPI Error Handling

9. Why does FastAPI's default validation-error response shape (`{"detail": [...]}` for missing fields) conflict with a single `{"detail": "string"}` contract? What frontend code would break if you didn't normalize it?
10. What's the actual runtime difference between a sync `def` route handler and an `async def` one, when the handler body calls blocking pandas/openpyxl code? Why can marking a handler `async def` make performance *worse*, not better?
11. Why should unexpected exceptions return a generic message instead of `str(exception)`? Give a concrete example of what a raw exception string could leak.

## Naming & Domain Modeling

12. Why did "Workflow Run" get retired entirely rather than just redefined more precisely?
13. What's the practical difference between a "Sample Template" and a "Sample File," and why does the distinction matter more in a demo/portfolio context than it might in an internal admin tool?
14. Try defining "Report Artifact" without using the word "generate" or "return." What's the essential property left over?

## ADR Discipline

15. Apply the three-part ADR test (hard to reverse / surprising / real trade-off) to "as_of_date is required and client-supplied, not optional with a server default." Does it pass all three? Why did it end up in `library-docs.md` instead of getting its own ADR?
16. What's the cost of writing an ADR for every decision made in a planning session, even ones that pass the test only weakly? What signal gets lost as the number of ADRs grows?
17. If a future phase wanted to add persisted workflow runs, would ADR 0006 need to be superseded or extended? What's the practical difference between those two outcomes for someone reading the ADR log later?

## `ReportLifecycleState` vs. Live Failures

18. Why does keeping `ReportLifecycleState` at 4 states (no `Error`) push failure-handling responsibility to a different layer? Where does it go instead, and why is that a better home for it?
19. What would start going wrong if every stateful UI concept in this codebase grew its own `Error` variant instead of composing with a shared `BusinessErrorMessage`?
