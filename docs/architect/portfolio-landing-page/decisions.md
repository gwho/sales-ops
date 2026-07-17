# Decisions — Portfolio Landing Page

Each section is one architectural decision made during the `/architect` session for
integrating a Figma-generated visual prototype (`career_os/demo_landing/demo-landing`,
a private, gitignored Vite/React export) into a new public landing page at `/`, while
keeping `/dashboard` as the operational workspace.

## 1. Distinct editorial visual identity, scoped to `components/landing/`

**What it is:** The landing page uses a flat, bordered, no-shadow visual style (`Section`,
`SectionLabel`, `SectionHeading` in `components/landing/Section.tsx`) — sharp corners,
`border-border` dividers, no `rounded-xl`/`shadow-sm`. This is visually distinct from
the dashboard's `Card` primitive (`rounded-xl border border-border bg-surface shadow-sm`).

**Why this over reusing `Card` everywhere:** The prototype's case-study aesthetic (flat,
editorial, magazine-like) doesn't map onto the dashboard's card-heavy operational look
without either flattening the dashboard's established style or fighting the prototype's
intent. The two are different *kinds* of page — a portfolio case study read top-to-bottom
once, versus a dense operational tool used repeatedly — so a small, deliberately-scoped
second visual style was accepted, on the condition that both surfaces still share the
same underlying tokens (`border-border`, `bg-surface`, `text-text-primary`, etc.), colors,
and interaction states. Nothing new was added to `context/ui-tokens.md` — the distinction
is purely in composition (radius, shadow, dividers), not in the token palette itself.

**Cost of the alternative:** Forcing the landing page into `Card` would have meant either
diluting the prototype's editorial feel to match the dashboard, or introducing a second,
undocumented radius/shadow convention inside `Card` itself — silently forking a primitive
used across five other routes for the sake of one new page.

## 2. Route groups: `(public)` and `(workspace)`, not a shared `AppShell`

**What it is:** `app/(public)/layout.tsx` renders a minimal `PublicHeader`/`PublicFooter`
around `/`. `app/(workspace)/layout.tsx` renders the existing `AppShell` (sidebar +
top header) around `/dashboard` and the three workflow pages + `/reports`. The root
`app/layout.tsx` was trimmed to only global providers (font, `<html>`/`<body>`).

**Why this over keeping `AppShell` everywhere:** A portfolio visitor landing on `/`
should not see operational app chrome (a sidebar built for repeated internal use) before
they've even opened the demo. Next.js route groups (`(public)`, `(workspace)`) let each
route family own its own layout without changing the URL shape — `/dashboard` is still
`/dashboard`, not `/workspace/dashboard`.

**Consequence accepted:** Existing route folders (`dashboard/`, `order-validation/`,
`inventory-allocation/`, `payment-aging/`, `reports/`) had to move under `(workspace)/`.
This is a pure file-move (`git mv`), not a URL change, and Next's route groups guarantee
client-side navigation between `/` and `/dashboard` stays a single-page-app transition,
not a full reload — because both routes still share one root layout.

## 3. Public content externalized to JSON, not hardcoded in `page.tsx`

**What it is:** `content/portfolio/sales-admin-automation-toolkit.json` holds hero copy,
workflow blurbs, business values, tech tags, boundary/scope note, and a `workflowSequence`
array — loaded via `lib/content/portfolio.ts` and typed by `types/portfolio-content.ts`.

**Why JSON over Markdown or inline TS objects:** The content is arrays of small, uniformly
shaped objects (title/description/icon per workflow, heading/body per value) — closer to
data than prose. This matches the existing precedent of `lib/mock-data.ts` feeding typed
JSON into components, and avoids a Markdown-to-structured-data parsing step that would be
needed to turn prose back into the typed shape each landing component expects.

**A real type-safety gap, and how it was resolved:** TypeScript widens JSON-imported string
fields to plain `string` — it cannot infer a literal union like `PortfolioIconName` from a
`.json` file. A direct `const x: PortfolioContent = rawJson` annotation therefore fails to
typecheck. The fix was a documented type assertion instead:

```ts
// lib/content/portfolio.ts
export const portfolioContent = rawContent as PortfolioContent;
```

This was deliberately *not* solved with a runtime schema validator (e.g. zod) — the file
is small, hand-authored, and code-reviewed, and every consumer of `portfolioContent` still
gets the narrow, exhaustively-checked types. A validator would be justified for
user-submitted or third-party JSON, not for a checked-in content file the same people who
write the components also edit.

## 4. Icon names as a string union + exhaustive `Record` lookup, not inline JSX in content

**What it is:** `types/portfolio-content.ts` defines `PortfolioIconName` as a union of
string literals (`"clipboard-check" | "package-check" | ...`). `components/landing/icon-map.tsx`
maps each name to a real `lucide-react` component via `Record<PortfolioIconName, LucideIcon>`.

**Why:** JSON can't hold a JSX element, so icons have to be referenced by name. Using a
`Record` typed over the *exhaustive* union (not `Record<string, LucideIcon | undefined>`)
means adding a new icon name to the union without adding it to the map is a **compile-time
error**, not a runtime `undefined` crash when the component tries to render `<Icon />`.

## 5. Role Fit section dropped entirely, not replaced

**What it is:** The prototype's "Role Fit" section (mapping the project to specific hiring
roles — Sales Administrator, Operations Executive, etc.) was excluded from the public
landing page content and not replaced with an alternative hiring-focused section.

**Why:** That content is private positioning logic — tailored to specific job
applications — that belongs in the user's separate, gitignored `career_os/` workspace
(later migrated out of this repo entirely; see the workspace-migration session docs).
The landing page demonstrates relevance *indirectly*, through real workflows, business
value, and explicit scope boundaries, rather than naming target job titles publicly.

## 6. `/dashboard` loses two long prose sections, gains one accurate compact notice

**What it is:** `app/(workspace)/dashboard/page.tsx` previously had a "How the Workflows
Connect" flow-diagram section and a "How This Demo Works" multi-paragraph guide. Both were
removed. In their place: a single `<p>` with the accurate sentence:

> "Workflow results are stored under an anonymous session associated with this browser.
> Sections labelled "Sample data" show fictional fallback records until that workflow has
> been run."

**Why this exact wording, not "saved to this browser only":** The original draft notice
said results are saved "to this browser only (no account, no login)." That's wrong for
this app's actual architecture (Phase 12): the Anonymous Session *ID* lives in
`localStorage`, but the saved workflow *results* live in Postgres (Neon), keyed by that
ID. Saying results live "in this browser" overstates what's true and could mislead a
visitor about where their data actually goes. The corrected sentence describes the
session mechanism accurately without getting into implementation detail the dashboard
notice doesn't need.

**Where the removed content went:** The conceptual "how workflows connect" diagram moved
to the landing page as `WorkflowSequence`, driven by the same `workflowSequence` JSON
field — content-driven instead of hardcoded, but visually the same icon-chip + arrow
pattern the dashboard already used (`Upload → Order Validation → Valid Orders`, etc.).
General project-scope explanation moved to the landing page's `BoundaryNote` component.
