# AI Discussion Topics: Phase 10 Architect Session

## Repo Location Decisions

1. Why did checking `context/architecture.md` before answering "where should the backend live" save an entire round of debate that otherwise looked open-ended?
2. What's the risk of an agent (human or AI) inventing a new directory convention when one is already implied elsewhere in a project's docs, even if the new one is arguably just as good?

## Dev Server Topology & CORS

3. What does CORS actually prevent, and — just as importantly — what does it *not* prevent? (Hint: think about what a `curl` request can do that a browser `fetch()` cannot.)
4. Why doesn't setting `allow_origins` alone let browser JavaScript read custom response headers like `X-Report-Id`? What specifically does `expose_headers` add that `allow_origins` doesn't cover?
5. What would break, concretely, if `allow_origins=["*"]` had been used instead of the specific localhost origin, in a demo project like this one? Is the risk different for a `GET` vs. a `POST` endpoint?
6. What's the argument for two independent dev servers over a Next.js `rewrites()` proxy, beyond "it's simpler to set up"?

## Response Typing Strategy

7. Why does Pydantic v2's ability to validate a `TypedDict` directly change the FastAPI response-model calculus compared to Pydantic v1, where this wasn't possible?
8. Describe a concrete scenario where `response_model` (declaring a *different* type than what the function returns) would be necessary — one that doesn't apply to this project's TypedDict-return approach.
9. If a parallel Pydantic `BaseModel` mirroring `OrderValidationResult` had been introduced instead, trace the exact mechanism by which it could silently drift out of sync with the TypedDict over time. What would have to happen for nobody to notice?

## Frontend State Boundaries

10. Why is "share the low-level fetch mechanics, not a shared state hook" a meaningfully different design than either extreme (fully duplicate all logic three times, vs. build one big configurable hook)?
11. What signal, once real page code exists, would tell you it's time to extract a shared `useWorkflowRequest` hook after all — i.e., what would you look for in the three pages' actual implementations to know the "premature abstraction" call was wrong?
12. Why does page-local state make a cross-page feature (like a live dashboard aggregating all three workflows) structurally impossible without introducing a new architectural layer, rather than just "harder"?

## Decision Blast Radius

13. The `/reports` page wasn't one of the four original planning questions but got swept up by the "no global store" decision anyway. What's a systematic way to check a decision's full blast radius across a codebase before finalizing a plan, rather than discovering consequences one at a time?
14. Are there other places in this codebase that might be quietly affected by "page-local state, no global store" that weren't discussed in this session? How would you go looking for them?

## Plan Review & Revision

15. Why did the `ExitPlanMode` rejection round catch specific issues (CORS headers, dependency consolidation) that the original planning conversation didn't surface? What's different about reviewing a written plan artifact versus having lived through the conversation that produced it?
16. `fastapi[standard]` bundles `python-multipart`, `uvicorn[standard]`, `httpx`, and `jinja2` as one dependency. What's the trade-off of depending on a bundled "extra" versus pinning each transitive dependency explicitly yourself?
17. Why is "`src/` stays framework-free, `backend/uploads.py` is the sole conversion boundary" worth stating explicitly in a written plan, rather than trusting it as an obvious consequence of the project's existing module-boundary rules?

## Documentation Timing

18. Why is running `/feature-docs` against a plan (before any code exists) a category error, not just premature? What specifically can only be known *after* implementation that a plan can't capture?
19. What's the actual risk of a documentation artifact that was written to be plausible rather than checked against reality — who does it mislead, and how would they find out it was wrong?
