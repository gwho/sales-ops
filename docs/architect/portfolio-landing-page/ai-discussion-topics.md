# AI Discussion Topics — Portfolio Landing Page

## Route groups and layout composition

1. Why do Next.js route groups (`(public)`, `(workspace)`) not change the URL, and what
   would break if they did? What's the actual mechanism that keeps `/dashboard` at
   `/dashboard` instead of `/workspace/dashboard`?
2. The root `app/layout.tsx` was trimmed to "global providers only." What specifically
   counts as something that must live in the root layout versus something that can move
   into a route group's own layout? What would go wrong if `<AppShell>` had stayed in the
   root layout instead of moving into `(workspace)/layout.tsx`?
3. Why does keeping one shared root layout (rather than two fully separate app trees)
   guarantee client-side navigation between `/` and `/dashboard`, instead of a full page
   reload?

## Visual identity and design-system boundaries

4. What's the actual risk of letting one page introduce its own visual sub-style (flat,
   no shadows) inside a project that otherwise has one consistent `Card` primitive? Under
   what conditions does that become a maintenance problem instead of a reasonable scoped
   choice?
5. The decision explicitly separated "shared tokens" from "shared composition" (radius,
   shadow, dividers). Why is that distinction the right place to draw the line, rather
   than either forcing full visual consistency or allowing a fully independent design
   system for the new page?

## Type safety at the JSON/TypeScript boundary

6. Why can't TypeScript infer a string-literal union from a `.json` import, even when
   every string in the file happens to match one of the union's members?
7. Compare the three options considered for the icon-name typing problem: duplicating
   content as a `.ts` file with `as const`, adding a runtime validator (e.g. zod), or a
   documented type assertion. What real-world scenario would tip the decision toward the
   validator instead of the assertion?
8. The exhaustive `Record<PortfolioIconName, LucideIcon>` pattern turns a missing icon
   mapping into a compile-time error. What would the failure mode look like if this had
   instead been written as `Record<string, LucideIcon | undefined>`, and where would that
   failure actually surface — build time, or a live user's browser?
9. What's the actual difference in guarantee between "the JSON content is type-asserted"
   and "every consumer of `portfolioContent` gets full narrow types"? Why can both of
   those be true at once?

## Content governance and copy accuracy

10. Why does describing a system's data-persistence behavior in UI copy carry the same
    accuracy bar as a code comment? What's a concrete way a developer could verify a
    sentence like "results are stored under an anonymous session" is actually true, rather
    than just plausible-sounding?
11. The plan added a standing rule — "copy is draft until reviewed for public accuracy" —
    rather than fixing two specific phrases. Why is a standing rule more durable than a
    one-time fix here, and what would you expect to happen if the rule weren't written
    down and only the two phrases were corrected?
12. What's the difference between "this project doesn't actually do X" and "this phrase
    overstates what X accomplishes," and why did both count as accuracy problems in this
    session even though only one is technically false?

## Privacy boundaries and scope discipline

13. The Role Fit section was dropped rather than reworded into something "safer." Why is
    "drop entirely, no replacement" sometimes the correct response to a scope-boundary
    problem, instead of trying to salvage a sanitized version of the same content?
14. What made the `tsconfig.json` exclude fix (adding `career_os` to `exclude`) an
    in-scope, immediate fix rather than an out-of-scope addition to a task that was
    ostensibly "build a landing page"? What's the general principle for telling those two
    situations apart?
15. If a stray import somewhere in the app had referenced a file inside `career_os/`,
    what specific build or type-check step would have caught it, and what would the
    failure have looked like?

## Process and self-correction

16. An inline SVG was written by mistake despite the instruction explicitly forbidding it,
    and was only caught on immediate re-inspection of the new component. What practice
    would catch this kind of slip *before* it's written, rather than relying on catching
    it right after?
17. Why is "moves to X" in an implementation plan not the same as "actually happens" until
    a concrete destination component/field exists? What's a way to write a plan so that
    kind of gap is harder to miss during review?
