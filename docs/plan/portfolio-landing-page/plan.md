# Plan — Feature portfolio-landing-page: Portfolio Landing Page

## What was built

- **`app/layout.tsx`** — trimmed to global providers only (font variable, `<html>`/`<body>`, metadata). No longer renders `AppShell` directly.
- **`app/(public)/layout.tsx`** (new) — public route group layout: `PublicHeader` + `<main>` + `PublicFooter`, no sidebar.
- **`app/(public)/page.tsx`** (new) — the landing page itself. Composes `Hero`, `WorkflowsSection`, `WorkflowSequence` (inside a bare `Section`), `ValueSection`, `BoundaryNote`, `TechSection`, `ClosingCta`, all fed from `portfolioContent`. Exports its own `metadata` (`"Sales Admin Automation Toolkit | Portfolio Case Study"`).
- **`app/page.tsx`** (deleted) — previously did `redirect("/dashboard")`; superseded by `app/(public)/page.tsx` serving `/` directly.
- **`app/(workspace)/layout.tsx`** (new) — workspace route group layout: renders `AppShell` (unchanged component) around its children.
- **`app/(workspace)/dashboard/page.tsx`, `app/(workspace)/order-validation/page.tsx`, `app/(workspace)/inventory-allocation/page.tsx`, `app/(workspace)/payment-aging/page.tsx`, `app/(workspace)/reports/page.tsx`** — moved (`git mv`) from their old top-level `app/` locations into the `(workspace)` route group. URLs unchanged.
- **`app/(workspace)/dashboard/page.tsx`** (content edit, in addition to the move) — removed the "How the Workflows Connect" flow-diagram section and the multi-paragraph "How This Demo Works" guide section (and their supporting `FlowRow` helper + now-unused icon imports). Replaced with a single compact `<p>` notice describing the session/sample-data mechanism.
- **`app/globals.css`** — added a `@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }` rule, for the landing page's in-page anchor navigation.
- **`content/portfolio/sales-admin-automation-toolkit.json`** (new) — the externalized public landing-page copy: `hero`, `workflows[]`, `workflowSequence[]`, `businessValues[]`, `techTags[]`, `boundaryPoints[]`.
- **`types/portfolio-content.ts`** (new) — the content contract: `PortfolioIconName` (string-literal union), `PortfolioHero`, `PortfolioWorkflow`, `PortfolioWorkflowSequenceStep`, `PortfolioWorkflowSequenceRow`, `PortfolioBusinessValue`, `PortfolioContent`.
- **`lib/content/portfolio.ts`** (new) — loads and type-asserts the JSON import as `PortfolioContent`, exported as `portfolioContent`.
- **`components/landing/icon-map.tsx`** (new) — `PORTFOLIO_ICON_MAP: Record<PortfolioIconName, LucideIcon>`, exhaustive.
- **`components/landing/Section.tsx`** (new) — `Section`, `SectionLabel`, `SectionHeading` structural primitives shared by every landing section.
- **`components/landing/Hero.tsx`** (new) — hero banner; primary CTA is a real `next/link` to `/dashboard`, secondary CTA is a native anchor to `#workflows`.
- **`components/landing/WorkflowsSection.tsx`** (new) — 4-card workflow grid, icons via `PORTFOLIO_ICON_MAP`.
- **`components/landing/WorkflowSequence.tsx`** (new) — icon-chip + arrow flow-diagram rows, content-driven from `workflowSequence`.
- **`components/landing/ValueSection.tsx`** (new) — business-value list with a `lucide-react` `Check` icon (not inline SVG).
- **`components/landing/TechSection.tsx`** (new) — tech-tag pill list.
- **`components/landing/BoundaryNote.tsx`** (new) — scope/boundary callout with a `lucide-react` `Info` icon.
- **`components/landing/ClosingCta.tsx`** (new) — closing CTA row; all links are real `next/link`s to `/dashboard`, `/inventory-allocation`, `/payment-aging` (no `href="#"` placeholders).
- **`components/landing/PublicHeader.tsx`** (new) — sticky header for the `(public)` layout: brand label, `#workflows`/`#value`/`#tech` anchor nav, "Open Dashboard" CTA link.
- **`components/landing/PublicFooter.tsx`** (new) — minimal footer, no external links.
- **`tsconfig.json`** — added `"career_os"` to `exclude` (alongside `"node_modules"`). Unrelated to the landing page's own logic, but discovered and fixed via this feature's own `tsc --noEmit` verification pass.
- **`context/ui-registry.md`** — new "Landing (`components/landing/`)" section (all 11 components above) and a new "Page composition notes (Portfolio Landing Page)" section; corrected a stale cross-reference in the existing Phase 12 notes.

## Schema changes

None. No database, migration, or API contract changes — this feature is Next.js frontend routing, static content, and UI components only.

## Key invariants

- **`components/landing/` is the only place the flat/bordered/no-shadow editorial visual style is used.** Every other route in the app uses the `Card`-based (`rounded-xl border border-border bg-surface shadow-sm`) operational style. Do not introduce the landing style elsewhere, and do not retrofit `Card`'s style into `components/landing/` — they are deliberately different, see `context/ui-registry.md`'s "Landing" section header note.
- **`portfolioContent` (from `lib/content/portfolio.ts`) is the only source of landing-page copy.** No component under `components/landing/` may hardcode hero/workflow/value/tech/boundary text — if new copy is needed, it goes into `content/portfolio/sales-admin-automation-toolkit.json` and the corresponding type in `types/portfolio-content.ts`.
- **Every icon referenced by content data must exist in both `PortfolioIconName` (types/portfolio-content.ts`) and `PORTFOLIO_ICON_MAP` (`components/landing/icon-map.tsx`).** Adding a name to one without the other is either a TypeScript compile error (JSON has a value not in the type — caught at the `as PortfolioContent` assertion boundary only if something re-validates it, in practice caught by `PORTFOLIO_ICON_MAP` failing to compile as `Record<PortfolioIconName, LucideIcon>` if a union member is unmapped) or an unreachable value. Keep both in sync.
- **No inline SVG anywhere under `components/landing/`.** Icons are `lucide-react` only, resolved through `PORTFOLIO_ICON_MAP`. This was violated once during implementation (`ValueSection.tsx`) and corrected immediately — see `explanation.md` §5.
- **The landing page has no "Role Fit" section, and none should be added without a new explicit decision.** That content (mapping the project to specific hiring roles) is private positioning logic that belongs outside this repo entirely — see `docs/architect/portfolio-landing-page/decisions.md` §5.
- **`app/(workspace)/dashboard/page.tsx` must not regain long-form conceptual/how-it-works prose.** That content now lives on the landing page (`WorkflowSequence`, `BoundaryNote`). The dashboard keeps exactly one compact, accurate session/sample-data notice — do not re-expand it.
- **The dashboard's session/sample-data notice text must stay mechanically accurate to Phase 12's actual architecture** (session ID in `localStorage`, saved results in Postgres) — not simplified to "saved to this browser," which is a factual misstatement of the real design (`context/architecture.md`'s "Persistence (Phase 12)" section is the source of truth).
- **`tsconfig.json`'s `exclude: ["node_modules", "career_os"]` must be preserved.** `career_os` is a private, sensitive directory boundary (see the separate workspace-migration documentation); do not remove this entry even after any future repo relocation, since it's a permanent guardrail, not a temporary fix.
