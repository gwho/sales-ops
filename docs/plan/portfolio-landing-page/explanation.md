# Explanation — Feature portfolio-landing-page: Portfolio Landing Page

## 1. The end-to-end data flow, from a visitor hitting `/` to rendered HTML

A request to `/` is served by `app/(public)/page.tsx`, wrapped by `app/(public)/layout.tsx`,
both of which sit inside the trimmed root `app/layout.tsx`. Next.js's App Router resolves
route groups — the parenthesized `(public)` and `(workspace)` segments — purely as a
filesystem organizing device; they never appear in the URL, so `/` still resolves to `/`
and `/dashboard` still resolves to `/dashboard`, even though the files that implement them
now live under different parenthesized folders. The root layout renders only global
providers (the Inter font variable, `<html>`/`<body>`, `suppressHydrationWarning`) and then
`{children}` — it has no opinion about sidebar-vs-no-sidebar chrome at all. That decision
belongs entirely to whichever route group's own `layout.tsx` wraps the page: `(public)`
supplies `PublicHeader` + `PublicFooter`, `(workspace)` supplies the pre-existing `AppShell`
(sidebar + top header, unchanged).

`app/(public)/page.tsx` itself is a Server Component with no interactivity — it imports
`portfolioContent` from `lib/content/portfolio.ts` (a synchronous, build-time JSON import,
not a fetch) and passes slices of it as props into each landing section component
(`Hero`, `WorkflowsSection`, `WorkflowSequence`, `ValueSection`, `BoundaryNote`,
`TechSection`, `ClosingCta`). Every one of those components is itself a Server Component —
there's no client-side state, no `"use client"` boundary anywhere in `components/landing/`,
because nothing on this page is interactive beyond native browser behavior (anchor
scrolling, link navigation). This is why the page renders as fully static content: `next
build`'s static generation step (confirmed in this feature's own verification run) prerenders
`/` at build time, the same as the workspace routes that don't fetch live data.

## 2. Why route groups instead of keeping one shared `AppShell`

Before this feature, every route in the app — including the bare root redirect — rendered
inside `AppShell`, which owns the sidebar navigation, the mobile drawer, and the top header.
That's appropriate chrome for an operational tool a user returns to repeatedly, but wrong
for a portfolio visitor's very first impression of the project: showing internal
app-navigation chrome before someone has even opened the demo undercuts the "this is a
polished case study" framing the whole page exists to create.

Next.js route groups solve this cleanly because they let two sibling route trees each own
a different layout without duplicating the URL structure or introducing any client-side
routing logic. The alternative — a single shared layout with conditional rendering based on
`usePathname()` — was not used, and for good reason: that would force `AppShell` to become
aware of a page type it has no other reason to know about, and would require a Client
Component check (`usePathname` only works in Client Components or via `next/navigation`'s
Server Component equivalent with more ceremony) purely to decide whether to render a
sidebar. Route groups make the decision structural instead: which folder a page's
`page.tsx` lives in *is* the decision, resolved entirely by the framework's own routing
convention, with zero runtime branching.

The practical consequence was moving five existing route folders (`dashboard/`,
`order-validation/`, `inventory-allocation/`, `payment-aging/`, `reports/`) with `git mv`
into `app/(workspace)/`. This is a pure rename from git's perspective — no page content
changed as part of the move itself (the dashboard's content changes, described in §7, were
a separate edit layered on top) — and Next.js's routing continues to resolve
`/order-validation` exactly as before, since route groups are invisible to the URL.

## 3. Why JSON for content, and the real TypeScript limitation it ran into

The landing page's copy — hero text, four workflow blurbs, four business-value entries, a
tech-tag list, three boundary-note bullets, and a four-row workflow-sequence diagram — is
externalized to `content/portfolio/sales-admin-automation-toolkit.json` rather than
hardcoded inside `app/(public)/page.tsx` or written as prose in a Markdown file. The
reasoning: this content is structurally uniform data (arrays of objects with the same
shape per array), not free-flowing prose that would need a Markdown-to-structured-data
parsing step to become usable by typed React components. This mirrors an existing project
precedent — `lib/mock-data.ts` already feeds typed JSON-shaped data into dashboard
components — so the landing page's content-loading pattern isn't a new idea being
introduced, it's the same idea applied to marketing copy instead of workflow results.

While wiring `lib/content/portfolio.ts`, a genuine TypeScript limitation surfaced. The
first attempt used a direct type annotation:

```ts
import rawContent from "@/content/portfolio/sales-admin-automation-toolkit.json";
import type { PortfolioContent } from "@/types/portfolio-content";

export const portfolioContent: PortfolioContent = rawContent;
```

This failed `tsc --noEmit` with a real structural type error, not a false alarm. The root
cause: TypeScript's JSON module resolution (`resolveJsonModule`, already enabled in this
project's `tsconfig.json`) infers `string` for every JSON string property — it has no
mechanism to narrow a JSON file's string values down to a literal union like
`PortfolioIconName` (`"clipboard-check" | "package-check" | ...`), even though every actual
value in the file happens to match one of those literals. The compiler error specifically
flagged `workflows[].icon: string` as not assignable to `icon: PortfolioIconName`.

Two real fixes exist for this class of problem: rewrite the content as a `.ts` file using
`as const` literals (gaining full structural checking, at the cost of abandoning the
JSON-content decision already made), or add a runtime schema validator (e.g. zod) that
narrows the type at the import boundary. Neither was used. Instead, the loader uses a
documented type assertion:

```ts
export const portfolioContent = rawContent as PortfolioContent;
```

with an inline comment explaining why this is acceptable here specifically: the file is
small, hand-authored, and reviewed by the same people who write the components that
consume it — the risk profile that would justify a runtime validator (adversarial,
unpredictable, or user-submitted input) doesn't apply to a checked-in content file. Every
downstream *consumer* of `portfolioContent` still receives the full narrow, exhaustively-
checked `PortfolioContent` type; only the JSON-import boundary itself loses static
verification of its literal values, and that specific gap is covered by the exhaustive
icon map described in §4, plus ordinary code review of the JSON file.

## 4. Exhaustive icon mapping instead of JSX inside content data

Because a `.json` file cannot contain a JSX element, `content/portfolio/sales-admin-
automation-toolkit.json` references icons by name (`"clipboard-check"`, `"upload"`, etc.)
rather than embedding a `<ClipboardCheck />` component reference. `types/portfolio-
content.ts` defines these names as the `PortfolioIconName` string-literal union, and
`components/landing/icon-map.tsx` resolves each name to a real `lucide-react` component via:

```ts
export const PORTFOLIO_ICON_MAP: Record<PortfolioIconName, LucideIcon> = {
  "clipboard-check": ClipboardCheck,
  "package-check": PackageCheck,
  // ...
};
```

The specific reason this is typed as `Record<PortfolioIconName, LucideIcon>` — over the
exhaustive union — rather than the looser `Record<string, LucideIcon | undefined>`
matters: with the exhaustive form, adding a new value to the `PortfolioIconName` union
without adding a corresponding entry to this map is a TypeScript compile error (an object
literal being checked against `Record<PortfolioIconName, LucideIcon>` must supply every
key). With the looser form, the same mistake would compile cleanly and only fail at
runtime, when some component tries to render `<Icon />` and `Icon` is `undefined` — a
blank space in production instead of a build failure a developer sees immediately.

## 5. An inline-SVG mistake, introduced and caught within the same implementation pass

The original task instructions were explicit that the Figma prototype's inline SVG icons
should not be copied into the new implementation — Lucide icons only, matching the rest of
the app's existing convention. Despite that being an active, known constraint,
`components/landing/ValueSection.tsx` was first written with an inline `<svg>` checkmark
for its business-value bullet marker, copied from habit while translating the prototype's
visual intent rather than its literal code. This was caught on the very next read-through
of the file, before moving on to the next component, and fixed by importing `Check` from
`lucide-react` in its place. The lesson this is worth recording for: an explicit "don't
copy X from the reference" instruction can still slip through during translation, even when
the constraint is fully understood — the concrete defense is re-checking each new component
against the literal list of forbidden patterns immediately after writing it, not trusting
that holding the rule in mind while writing was sufficient.

## 6. Why the Role Fit section was dropped entirely, with no replacement

The source Figma prototype (`career_os/demo_landing/demo-landing`, a private, gitignored
export) included a "Role Fit" section mapping the project to specific hiring roles (Sales
Administrator, Operations Executive, etc.), each with a short relevance blurb and a list of
capability tags. This was deliberately excluded from `content/portfolio/sales-admin-
automation-toolkit.json` and has no equivalent component under `components/landing/`. The
reasoning, reached during the `/architect` planning session and recorded in full in
`docs/architect/portfolio-landing-page/decisions.md` §5: that content is private
positioning logic — language crafted to tailor resumes and interview framing to specific
target roles — and belongs in a separate, private workspace (`career_os/`, later migrated
entirely out of this repository; see the separate workspace-migration documentation), never
in a public, deployed repository. The landing page instead demonstrates relevance
indirectly, through the real workflow descriptions, business-value copy, and explicit scope
boundaries — no hiring-role framing appears anywhere in the public app.

## 7. The dashboard content split: what moved, what was replaced, and a wording correction

Before this feature, `app/dashboard/page.tsx` (now `app/(workspace)/dashboard/page.tsx`)
carried two long static sections beyond its live data: a "How the Workflows Connect"
section rendering four icon-chip-and-arrow flow rows (hardcoded `FlowRow` calls with inline
JSX icon props), and a multi-paragraph "How This Demo Works" guide covering the project's
scope, the session/sample-data mechanism, status-tag conventions, filtering behavior, and
the Python-first build philosophy.

Both were removed. The flow-diagram content didn't disappear — it moved to the landing
page as `components/landing/WorkflowSequence.tsx`, which renders the identical icon-chip-
plus-`ArrowRight` visual pattern the dashboard used, but reads its rows from the
`workflowSequence` field in `content/portfolio/sales-admin-automation-toolkit.json` instead
of a hardcoded array — the same four flows (Orders→Validation→Valid Orders, etc.),
now data-driven. This was actually a correction made mid-implementation: an earlier draft
of the plan said the section "moves to the landing page" without any landing component
actually implementing it, which would have made the move a silent deletion. Adding the
explicit `workflowSequence` content field and the `WorkflowSequence` component was the fix.

The "How This Demo Works" guide's conceptual/scope content also moved to the landing page,
distributed across `BoundaryNote` (the project-boundary bullets) and the landing page's
general framing. What stayed on the dashboard is a single compact paragraph:

```
Workflow results are stored under an anonymous session associated with this
browser. Sections labelled "Sample data" show fictional fallback records
until that workflow has been run.
```

This replaced an earlier draft of the same notice that said results are "saved to this
browser only (no account, no login)." That phrasing was reviewed and rejected as
inaccurate: per `context/architecture.md`'s "Persistence (Phase 12)" section, the
Anonymous Session *ID* lives in `localStorage`, but the saved workflow *results* live in a
Postgres `workflow_results` table (Neon), keyed by that ID — the results are not, in fact,
confined to the browser. The corrected sentence describes the session mechanism accurately
(a session identifier associated with the browser, without claiming the data itself never
leaves it) without needing to explain the Postgres implementation detail to a dashboard
visitor.

## 8. A pre-existing gap found and fixed as a side effect: `tsconfig.json`'s unscoped `include`

Running `npm run typecheck` after the route-group restructuring surfaced a batch of errors
entirely unrelated to the landing page: missing modules, implicit `any` parameters, and
Vite-specific config errors, all originating from files under `career_os/` — a private,
gitignored directory that happens to contain several unrelated sub-projects (a Vite/React
resume-drafting tool, a separate Figma Make export, and more), none of which have anything
to do with this Next.js app.

The cause was that `tsconfig.json`'s `include` glob (`**/*.ts`, `**/*.tsx`) is unscoped to
`app/`/`components/`/etc. — it matches every TypeScript file anywhere under the project
root, and nothing in `exclude` (which listed only `node_modules` at the time) stopped it
from also matching `career_os/`. This is a real, pre-existing gap in the project's privacy
boundary: `.gitignore` already excludes `career_os/` from version control, but nothing had
been excluding it from TypeScript's own project-wide type-checking scope, meaning a stray
future import — or even just running `tsc` — could pull private, unrelated code into the
compiler's working set. The fix, `"exclude": ["node_modules", "career_os"]`, was applied
immediately as part of this feature's own verification pass rather than filed as a
follow-up, since it's a one-line, narrowly-scoped change that directly reinforces the same
privacy boundary this feature's own content-sourcing decisions were built around (see §6).

## 9. Verification: what actually passed, and an honest account of what didn't

`npm run typecheck` and `npm run lint` both ran clean against the final code. A production
build (`npm run build`) also completed successfully — total 2:49.74s (2.2 minutes to
compile, 14.9 seconds for the TypeScript check, both routes-manifest phases fast) — and
statically prerendered all seven routes: `/`, `/dashboard`, `/order-validation`,
`/inventory-allocation`, `/payment-aging`, `/reports`, and `/_not-found`. This is genuine,
compile-time proof that every route — including the new landing page — builds without
error under the project's real toolchain.

What did **not** get completed is interactive, live-browser verification: opening the dev
server and actually clicking through `/`'s anchor navigation, checking both desktop and
mobile viewport rendering, and confirming no browser console errors. This was attempted
twice and blocked both times by an unrelated environmental issue — a separate, unrelated
project's dev server was found squatting on the expected local port, and a subsequent
attempt on an alternate port stalled during Turbopack's per-route on-demand compilation for
over two minutes with no error, consistent with a disk-I/O contention issue already
diagnosed elsewhere in this same working session (see the separate workspace-migration and
build-recovery documentation) and unrelated to anything in this feature's own code. Per
this project's established diagnostic discipline, that verification step was not retried
repeatedly; it's recorded here as incomplete, not claimed as passing. The production
build's successful static generation of every route is real evidence the code itself is
correct, but it is not a substitute for having actually watched the page render in a
browser.
