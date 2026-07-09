# AI Discussion Topics — Feature phase-8-nextjs-frontend-foundation: Next.js Frontend Foundation

## Scaffold safety & the transplant

1. `create-next-app` generated its own `AGENTS.md` and `CLAUDE.md`. If those had overwritten the real ones at the root, what specifically would have broken in later sessions — and would `git` have made it obvious, or silently staged the clobbered versions?
2. The `.gitignore` was merged by hand rather than copied. Walk through what would have gone wrong if Next's `.gitignore` had simply replaced the Python one. Which ignore rules from each side had to coexist?
3. `next-env.d.ts` is gitignored (per Next's convention) yet required for types. How is it regenerated, and why is it safe to not commit it? What generates it if a fresh clone runs `tsc` before `next dev`?
4. What is the exact list of files that were deliberately *not* transplanted from the scaffold, and why each one was excluded?

## Tailwind v3 pin & the token config

5. Why is downgrading a v4 scaffold to v3 harder than scaffolding with `--no-tailwind` and adding v3 manually? Name the concrete v4-vs-v3 differences that make it messy.
6. The verification checked "package.json AND lockfile are 3.4.x" and that `@tailwindcss/postcss` is absent. Why check the lockfile separately from `package.json` — what could `package.json` alone hide?
7. `tailwind.config.ts` uses `theme.extend.colors` rather than replacing the palette. What does that choice mean for whether `bg-blue-600` still works, and does that undermine the "no raw palette classes" rule? Where is that rule actually enforced?
8. The tokens are stored as HSL channel triples (`221 83% 53%`) and consumed as `hsl(var(--accent))`. Why store them channel-only instead of as full `hsl(...)` strings? What would break in the Tailwind config if they were stored as full color strings?

## The shadcn token collision

9. Explain the `--accent` collision precisely: what does `--accent` mean in `ui-tokens.md` versus in shadcn, and what would render wrong if both definitions landed in `colors.accent`?
10. The `tokens-no-modification` skill rule is tagged CRITICAL. Why did that rule convert "should we add shadcn primitives now?" from a judgment call into a near-mechanical "no"? What would selecting the other option have counted as?
11. Phase 9 will add shadcn primitives "reconciled to `ui-tokens.md`." Concretely, what does reconciling a shadcn `button.tsx` involve — which classes get rewritten, and to what?
12. `components.json` still declares `baseColor: slate` and `cssVariables: true`. When Phase 9 runs `shadcn add button`, what will it generate, and why is that a Phase 9 problem rather than a Phase 8 one?
13. The main `skills/tailwind/SKILL.md` was read and then disregarded. Why was it the wrong skill for this project, and what would have gone wrong if its v4 guidance had been followed?

## Mock data & the test-import boundary

14. Why is "the app must never import `tests/` at runtime" an invariant rather than a style preference? What are the two distinct problems it prevents?
15. `scripts/generate_mock_data.py` inserts the repo root on `sys.path`. Why is that necessary for a standalone script when the pytest suite imports `tests.contract_fixtures` without it?
16. The mock envelopes are described as "intentionally small." What is the source of that smallness, and what would a Phase 9 developer have to do to get a richer demo dataset without violating any invariant?
17. Walk through how sourcing `reports.json` from the fixture (rather than hand-writing it) protected against reintroducing the stale `report_id` drift that was fixed earlier in the session.
18. If `src/contracts.py` gains a new field tomorrow, what is the exact ordered sequence of edits/regenerations needed to keep `contracts.py`, `ui-contract-plan.md`, `types/index.ts`, and `lib/mock-data/*.json` consistent?

## Routing, verification & Figma

19. The stub pages use real semantic token classes instead of placeholder markup. Why was that a deliberate verification choice rather than over-engineering a stub?
20. Verification grepped the built CSS on disk for both `:root` variables and compiled utility classes. Why are both halves necessary — what failure would show up in one but not the other?
21. Root `app/page.tsx` uses `redirect("/dashboard")`. What are the trade-offs versus making `/` itself the dashboard, and does the redirect opt the route out of static prerendering?
22. The Figma prototypes put `Invalid SKU` in the allocation status column. Explain why that is contract-wrong and where an invalid SKU is actually handled in the pipeline.
23. The Figma reconciliation "changed no Phase 8 code." Why capture it now at all, and what concrete Phase 9 mistake does the documented reconciliation prevent?
24. Only the Dashboard prototype used the mandated sidebar; the others used top-nav/stepper or a bare bar. Why did the sidebar decision win uniformly, and what parts of the non-sidebar prototypes are still usable?
