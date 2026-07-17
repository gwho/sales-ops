# Discussion — Portfolio Landing Page

This is the full reasoning trail behind the portfolio landing page integration — not a
summary, but why each choice was made, what alternatives were considered, and what would
have gone wrong with a different call.

## Starting point: a private prototype, a public boundary

The request was to integrate a Figma Make export (`career_os/demo_landing/demo-landing`)
into the real app. That export lived inside `career_os/`, a directory the project's own
`.gitignore` already excluded (`career_os/` alongside `Resume/`) because it holds the
user's private career/job-search materials — resumes, target job lists, drafts. The
critical framing for the whole session was: **the prototype is visual/structural
reference only; its file tree, its content, and its dependency stack are not automatically
safe to bring into the public repo.**

Before any design decision, the actual prototype code was read in full: `App.tsx` (hero,
workflow cards, business value, role fit, boundary note, tech tags, closing CTA — all as
hardcoded arrays with inline SVG icons and `--font-mono`/`--font-display` CSS variables
that don't exist anywhere in this project's real token set), plus each of its seven
component files (`ProjectHero`, `WorkflowCard`, `BusinessValueItem`, `RoleFitRow`,
`TechTag`, `BoundaryNote`, `DemoCTA`). This mattered because the instructions explicitly
called out several things *not* to copy — the Vite setup, Tailwind 4 config, undefined CSS
variables, inline SVGs, placeholder links, hardcoded content — and each of those had to be
verified as actually present before treating the warning as satisfied.

## Language alignment

Before any decision-making, three terms were pinned down explicitly with the user:

- **"Visual reference only"** — rebuild as new components on this project's real stack
  (Tailwind 3.4, Lucide, existing tokens); never import the prototype's own files.
- **"Portfolio case-study landing page"** — a single scrolling page: hero → workflows →
  business value → tech stack → scope/boundary note → closing CTA.
- **"Public-safe content file"** — tracked in the *main* repo, sourced only from the
  prototype's already-generic copy, never from anything else in `career_os/`.

This alignment step caught a real ambiguity early: the prototype's copy was written
*inside* a directory whose broader purpose is private career materials. Confirming that
the specific copy in `App.tsx` was itself generic case-study language (not, say, drawn
from resume wording) was a factual check, not an assumption — done by reading the actual
strings before deciding they were safe to adapt.

## Round 1 — four decisions, each with a stated recommendation

**Decision: landing visual identity.** Match the dashboard's `Card` style, or introduce a
distinct editorial look scoped to the new page? The recommendation was the distinct
look — reasoning: this is fundamentally a different kind of page (read once, top to
bottom, versus a repeatedly-used operational tool), and the two already differ in *purpose*
before they differ in styling; forcing one style onto both would either flatten the
prototype's intended feel or quietly fork the dashboard's `Card` semantics. The user chose
this option, with an explicit condition: both surfaces must still share typography, colors,
and interaction states — the split is in composition, not in the token palette.

**Decision: root layout chrome.** Should `/` render inside the existing `AppShell`
(sidebar + top header), or get a separate minimal layout? Recommended and chosen: separate,
via Next.js route groups — `(public)` and `(workspace)`. The reasoning: a portfolio
visitor's very first impression of the project is `/`; showing them internal app
navigation before they've opened the demo undercuts the "this is a polished case study"
framing the whole exercise was for.

**Decision: content format.** JSON or Markdown for the externalized copy? Recommended and
chosen: JSON, because the content is fundamentally structured data (parallel arrays of
title/description/icon triples) rather than prose, matching how `lib/mock-data.ts` already
feeds typed data into the dashboard.

**Decision: Role Fit section.** Keep it (it's not confidential — no target companies,
resume text, or job listings named) or drop it? The recommendation was to *keep* it, on
the reasoning that it's generic portfolio-positioning language, exactly the kind of
framing a case study should have. **The user overruled this recommendation** and chose to
drop it, with a sharper distinction than the recommendation had drawn: Role Fit isn't just
"not confidential," it's *actively* private positioning logic — used to tailor resumes and
interview prep — and belongs in `career_os/`, full stop, with no public replacement. This
is a good example of a recommendation being reasonable on its own terms but still wrong
relative to context the user held that hadn't been fully surfaced yet (the depth of
private, job-search-specific reasoning already invested in that exact framing, later fully
visible in the `career-os/memory.md` migrated content).

## Round 2 — four corrections after the first plan was reviewed

The user's review of the first "Blueprint ready" plan produced four specific corrections,
each demonstrating a different kind of gap:

1. **A section was silently deleted, not moved.** The plan said "How the Workflows
   Connect" moves to the landing page, but no landing section actually carried it — it
   would have simply vanished. Fix: add an explicit `workflowSequence` field to the
   content contract and a real `WorkflowSequence` component, reusing the dashboard's
   existing icon-chip-plus-arrow visual pattern, just content-driven instead of hardcoded.
   **Lesson:** "moves to X" in a plan is a claim that needs a literal destination, not an
   assumption that saying it happened makes it happen.

2. **Copy accuracy needs an explicit gate, not implicit trust.** Phrases straight from the
   prototype — "no post-processing required," "removing manual judgement calls" — read as
   measured outcome claims the actual Python-first architecture doesn't demonstrate. The
   fix wasn't to individually edit those two phrases; it was to add a standing rule to the
   plan: extracted copy is *draft until reviewed for public accuracy*, and the
   implementation may reformat but must never introduce claimed capabilities beyond what
   the app actually does. That rule then did the toning-down work during content authoring
   (see `content/portfolio/sales-admin-automation-toolkit.json`'s business-value entries,
   which read as process descriptions — "aiming to reduce rework" — not outcome claims).

3. **The dashboard notice's wording was subtly wrong about the system it described.**
   "Saved to this browser only (no account, no login)" is a description of a *simpler*
   architecture (pure `localStorage`) than what Phase 12 actually built (a session ID in
   `localStorage`, results in Postgres). The correction supplied the exact accurate
   sentence to use instead. **Lesson:** UI copy describing system behavior is a factual
   claim about the codebase, not just tone — it needs the same accuracy bar as a code
   comment, checked against the actual architecture doc (`context/architecture.md`'s
   "Persistence (Phase 12)" section), not against what sounds plausible.

4. **Verification scope was too narrow.** The original plan's checks leaned on workspace
   routes; the correction added: landing page at both viewport widths, public header/nav
   behavior, keyboard focus order and heading hierarchy, browser console cleanliness, and
   — specifically — a check that no `career_os` content or imports leak into the
   production build. That last item ties directly back to the whole reason this was being
   built carefully in the first place.

## Implementation: a real type-system gap surfaced mid-build

While wiring the typed JSON loader, `lib/content/portfolio.ts`, a concrete TypeScript
limitation surfaced: importing a `.json` file and assigning it to a type with string
*literal unions* (`PortfolioIconName`) does not typecheck, because TypeScript infers plain
`string` for JSON string fields — it has no way to know the JSON author intended one of a
fixed set of literals. The first attempt (`const x: PortfolioContent = rawJson`) failed
`tsc --noEmit` with a real type error, not a false alarm.

Two ways to actually fix this exist: (a) duplicate the content as a `.ts` file with
`as const` literals instead of `.json`, gaining full structural checking at the cost of
losing the JSON-content-file decision already made; or (b) add a runtime schema validator
(zod, etc.) that narrows the type at the boundary. Neither was taken. Instead, a documented
type assertion (`rawContent as PortfolioContent`) was used, with the reasoning made
explicit in a code comment: this file is small, hand-authored, and reviewed by the same
people who write the consuming components — the risk profile that justifies a runtime
validator (adversarial or unpredictable input) doesn't apply here. Every *consumer* of
`portfolioContent` downstream still gets the full narrow, exhaustively-checked types; only
the JSON-import boundary itself loses static verification, and that gap is covered by
manual review instead.

## An inline-SVG mistake, caught and self-corrected mid-build

While writing `ValueSection.tsx`, an inline `<svg>` checkmark was used for the business-value
bullet icon — directly violating the "no inline SVG icons" instruction from the original
task, and only noticed on review of the component right after writing it. The fix was
immediate: swap in `lucide-react`'s `Check` icon, matching every other icon in the landing
components. This is worth recording because it's the kind of small, easy-to-miss slip that
happens even when the constraint is explicit and top-of-mind — worth double-checking new
components against the literal list of "don't copy X, Y, Z from the prototype" rather than
trusting memory of the rule while writing.

## Verification: typecheck caught a second, unrelated pre-existing gap

Running `npm run typecheck` after the route-group restructuring surfaced errors that had
nothing to do with the landing page: `career_os/` — including its own separate,
unrelated sub-projects with their own `vite.config.ts`, `resume/` React components, and
missing-module errors — was being pulled into `tsc`'s type-checking scope, because
`tsconfig.json`'s `include` glob (`**/*.ts`, `**/*.tsx`) has no matching `exclude` for it.
This was a real, pre-existing gap in the project's own privacy boundary — nothing stopped
a stray import or a bundler's file-tracing step from touching `career_os/` even though
`.gitignore` already excluded it from *version control*. The fix (`"exclude": ["node_modules",
"career_os"]` added to `tsconfig.json`) directly serves the same goal this whole feature's
privacy requirement was built around, so it was applied immediately rather than filed as a
follow-up — a one-line, narrowly-scoped, clearly-justified config change is different from
scope creep.
