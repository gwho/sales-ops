# AI Discussion Topics — Feature portfolio-landing-page: Portfolio Landing Page

## Route groups and layout composition

1. Why does moving five route folders into `app/(workspace)/` with `git mv` not change any
   of their URLs? What specifically in Next.js's routing convention makes the parenthesized
   segment invisible to the resolved path?
2. The root `app/layout.tsx` renders only global providers, with no sidebar-vs-no-sidebar
   decision at all. Walk through exactly what would break, or what would need to change,
   if `AppShell` were moved back into the root layout instead of `(workspace)/layout.tsx`.
3. Why was a `usePathname()`-based conditional layout considered and rejected in favor of
   route groups? What would that alternative have cost in terms of Client Component
   boundaries that route groups avoid entirely?
4. What is actually different between `(public)` and `(workspace)` at the type/file level
   — is there anything enforcing that a page can only exist in one group, or could a route
   accidentally end up reachable from both?

## The JSON/TypeScript boundary

5. Walk through exactly why `tsc --noEmit` failed on `const portfolioContent:
   PortfolioContent = rawContent` — what specific type does TypeScript infer for
   `workflows[].icon` from the JSON import, and why can't it narrow that to
   `PortfolioIconName` even though every actual value matches?
6. Of the three options considered for this problem (duplicate as a `.ts` file with `as
   const`, add a runtime validator, or use a type assertion), what's a concrete scenario
   where the runtime-validator option would clearly be the correct choice instead?
7. The code comment says the type assertion is "safe on that basis" — hand-authored,
   reviewed content. What would have to change about this content's origin (who writes it,
   how it gets into the file) for that safety argument to stop holding?
8. `PORTFOLIO_ICON_MAP` is typed as `Record<PortfolioIconName, LucideIcon>` rather than
   `Record<string, LucideIcon | undefined>`. Trace through what happens, step by step, at
   compile time and at runtime, for each of those two typings if a new icon name is added
   to the JSON content but the corresponding map entry is forgotten.

## Content externalization and privacy boundaries

9. Why does this feature's content live in a `.json` file rather than as inline arrays in
   `app/(public)/page.tsx`, given that `lib/mock-data.ts` already exists as a precedent for
   typed data files in this project? What would have to be true about the content for
   inlining it to actually be the better choice?
10. The Role Fit section was dropped with no public replacement, rather than rewritten into
    a "safer" version. Why might "drop entirely" be the correct response to a privacy
    boundary problem in general, instead of trying to sanitize the same content?
11. What made the `tsconfig.json` `exclude` fix an in-scope change to make immediately,
    rather than something to flag and leave for a separate task? What's the general rule
    for telling those two situations apart?
12. If a future contributor added a new landing-page component that imported something
    from `career_os/` by mistake, what specific tool or command would catch it, and at
    what point in the build/dev pipeline?

## The dashboard content split

13. The dashboard's session-notice wording was corrected from "saved to this browser only"
    to a more accurate sentence. Trace through the actual Phase 12 architecture (session ID
    vs. saved results) and explain precisely which part of the original sentence was false,
    not just imprecise.
14. Why does UI copy describing a system's data-persistence behavior deserve the same
    accuracy bar as a code comment or a test assertion? Give a concrete way a reader could
    have verified the corrected sentence was true before it shipped.
15. The `workflowSequence` content field and `WorkflowSequence` component were added after
    an earlier plan draft said the flow diagram "moves to the landing page" without any
    component actually implementing it. What's a way to write or review an implementation
    plan so this kind of gap — a claimed action with no actual destination — is easier to
    catch before code is written?

## Process and verification

16. The production build succeeded (all 7 routes, ~2:49 total) but interactive dev-server
    verification was never completed. Why is "the build succeeded" not the same claim as
    "the feature works," and what specifically would live-browser verification have caught
    that a successful build could not?
17. An inline SVG was written by mistake in `ValueSection.tsx` despite an explicit
    instruction not to, and was only caught on the next read-through. What's a concrete
    habit or check that would catch this kind of slip *before* it's written, rather than
    relying on catching it immediately after?
