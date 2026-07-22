# Sales Admin Automation Toolkit — Resources

Curated for a learner with **zero assumed prior knowledge** of any of these technologies. Grouped by Concept Track (see `ROADMAP.md`). Every entry is an official or clearly-canonical source — no marketing-dressed-as-education.

## Prequel — Files, Folders, and the Terminal

- [Software Carpentry — The Unix Shell: Introducing the Shell](https://swcarpentry.github.io/shell-novice/01-intro.html)
  Free, official, written for people who have never used a command line before. Use for: Lesson 0 (files, folders, paths, what a terminal/command is).
- [Software Carpentry — The Unix Shell: Navigating Files and Directories](https://swcarpentry.github.io/shell-novice/02-filedir.html)
  Direct follow-on episode with more hands-on practice than Lesson 0 covers. Use for: reinforcement after Lesson 0, if `ls`/paths still feel shaky.

## Track 1 — Python, Data-as-Tables, Contracts

- [The Python Tutorial (official)](https://docs.python.org/3/tutorial/)
  Absolute-beginner-safe, from the language's own maintainers. Use for: L1.1 (modules, functions, basic syntax).
- [pytest — Get Started](https://docs.pytest.org/en/stable/getting-started.html)
  Official docs, minimal working example first. Use for: L1.1 ("what does pytest do, how do I read a test file").
- [uv — Getting Started](https://docs.astral.sh/uv/getting-started/)
  Official docs for the tool this repo's `pyproject.toml`/`uv.lock` are built around. Use for: L1.1.
- [pandas — 10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
  Official quickstart, exactly the "rows/columns/DataFrame" mental model needed for L1.2 — nothing more.
- [PEP 589 — TypedDict](https://peps.python.org/pep-0589/)
  The actual language proposal that defines what `TypedDict` is. Use for: L1.3, once dict basics are solid — this is a reference, not a first read.

## Track 2 — Business Rules & Testing

- [pytest — How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
  Use for: `0008`/`0009`, concretely connecting "business rule" to "assertion."
- [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
  Official docs for pytest's *real* fixture mechanism (`@pytest.fixture`) — cited in `0010` and
  `test-reading-patterns.html` specifically to distinguish it from this repo's own plain
  builder-helper-function pattern (`_order_row`, `_invoices_df`, etc.), which is *not* the same
  thing and shouldn't be called a "fixture" when describing this repo's tests.
- [Python — datetime (official docs)](https://docs.python.org/3/library/datetime.html)
  Use for: `0013`, specifically the `timedelta` section — what subtracting two `date` objects
  actually produces, before that value becomes `days_overdue`.
- No dedicated external resource for `0012` (priority-ordered/greedy processing) — this is still
  best taught directly against this repo's own spec file
  (`sales_admin_automation_toolkit_specs/02_demo_inventory_allocation.md`, Rule IA-001), which is
  already the primary source. Matches the Gaps note below — unchanged after a Track 2 search pass.

## Track 3 — Presentation Without Leakage

- [openpyxl documentation](https://openpyxl.readthedocs.io/en/stable/)
  Official docs for the library `report_export.py` is built on. Use for: Lesson 17's
  workbook/sheet/cell vocabulary, and Lesson 18's `_safe_cell_value`/save-reload discussion.
  Verified live 2026-07-15 by domain/HTTP response (readthedocs rate-limited a direct content
  fetch with a 429 during this check, not a 404 or DNS failure — the same URL was already cited
  here from an earlier, successfully-verified session).
- [Python — io.BytesIO](https://docs.python.org/3/library/io.html#io.BytesIO)
  Official docs, confirmed live 2026-07-15. Use for: Lesson 18 — the in-memory buffer that lets
  `_save_workbook_bytes` produce real `.xlsx` bytes without ever touching a disk path.

## Track 4 — HTTP APIs & Statelessness

- [MDN — An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
  Vendor-neutral, widely regarded as the best plain-language HTTP primer. Use for: L4.1 (`0022`).
  URL updated 2026-07-16 — MDN moved this page under `/Guides/`; the old `/Web/HTTP/Overview` URL
  still 301-redirects here, confirmed live via `curl -L`, not just assumed.
- [FastAPI — Tutorial (official)](https://fastapi.tiangolo.com/tutorial/)
  Written by the framework's own author; the project's `context/library-docs.md` already tracks
  project-specific deviations from it. Use for: pairing with Tutorial 7. Confirmed live (200)
  2026-07-16.
- [MDN — HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)
  Reference for L4.1's "200/400/404/500" vocabulary. URL updated 2026-07-16 — MDN moved this page
  under `/Reference/`; the old `/Web/HTTP/Status` URL still 301-redirects here, confirmed live via
  `curl -L`.

## Track 5 — UI Components & Next.js

- [React — Learn React (official)](https://react.dev/learn)
  The canonical modern React tutorial, component/props/state framed exactly as L5.2 needs.
- [Next.js — App Router documentation](https://nextjs.org/docs/app)
  Official docs; specifically the "Server and Client Components" page is the primary source for L5.3, the single most-repeated rule in this repo.
- [TypeScript — Handbook (official)](https://www.typescriptlang.org/docs/handbook/intro.html)
  Use once JS/React basics are comfortable, before reading `types/dashboard.ts` etc. closely.
- [React — Using TypeScript](https://react.dev/learn/typescript)
  Official React docs' own page on typing component props and children with `ReactNode`. Primary
  source for Lesson 35 (optional Track 5 reinforcement). Confirmed live and on-topic 2026-07-18.
- [TypeScript Handbook — Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
  and [Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
  More precise than the Handbook's intro page for two specific mechanics: optional properties
  (`Object Types`) and literal/union types (`Everyday Types`). Use for: Lesson 35's optional-prop
  and `Tone`-style literal-union sections. Both confirmed live and on-topic 2026-07-18.
- [React — State as a Snapshot](https://react.dev/learn/state-as-a-snapshot)
  Primary source for Lesson 36 (optional Track 5 reinforcement) — state read within one render is a
  fixed value, not a live reference. Confirmed live and on-topic 2026-07-19.
- [React — You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
  Secondary source for Lesson 36's derived-value section only (compute during render vs. copy into
  state). Confirmed live and on-topic 2026-07-19.
- [React — Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
  Primary source for Lesson 37 (optional Track 5 reinforcement) — what an Effect is for, and its
  "Add cleanup if needed" section specifically, the cleanup pattern `DashboardLiveSections.tsx`
  uses. Confirmed live and on-topic 2026-07-19.
- [React — useEffect API reference](https://react.dev/reference/react/useEffect)
  Secondary source for Lesson 37's Strict Mode claim specifically — its Caveats section is the
  precise source for "one extra development-only setup → cleanup → setup cycle before the first
  real setup." Added after a review pass caught the original draft's Strict Mode wording as
  imprecise. Confirmed live and on-topic 2026-07-19.
- [React — Rendering Lists](https://react.dev/learn/rendering-lists)
  Primary source for Lesson 38 (optional Track 5 reinforcement) — why list items need a stable key
  and why array index breaks under reordering. Confirmed live and on-topic 2026-07-20.
- [TypeScript Handbook — Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
  Secondary source for Lesson 38 — what a type parameter is for (carrying a relationship between
  input and output types), used to explain `DataTable<T>`. Confirmed live and on-topic 2026-07-20.
- [React — useMemo API reference](https://react.dev/reference/react/useMemo)
  Secondary source for Lesson 38 — `useMemo` as a performance optimization only, whose calculation
  must stay correct even if the memoization were removed entirely. Confirmed live and on-topic
  2026-07-20.
- [Tailwind CSS v3 documentation](https://v3.tailwindcss.com/docs)
  Pinned to v3 docs specifically — this repo deliberately stays on Tailwind 3.4, not v4 (see `context/library-docs.md`). Use for: L5.4 (design tokens).
- [MDN — Introduction to CSS layout](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Introduction)
  Primary source for Lesson 39 (optional Track 5 reinforcement) — normal flow and the box model.
  Confirmed live and on-topic 2026-07-21.
- [MDN — Flexbox](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Flexbox)
  Source for Lesson 39's main-axis/cross-axis section. Confirmed live and on-topic 2026-07-21.
- [MDN — Grids](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Grids)
  Source for Lesson 39's grid-tracks/`fr`-unit section. Confirmed live and on-topic 2026-07-21.
- [MDN — min-width reference](https://developer.mozilla.org/en-US/docs/Web/CSS/min-width)
  Source for Lesson 39's intrinsic-minimum-size claim specifically — its `auto` value description
  documents that a flex/grid item's automatic minimum size becomes content-based unless the item is
  a scroll container, in which case it's zero. This is the exact mechanism behind
  `UploadPanel.tsx`'s `truncate` span truncating correctly without an explicit `min-w-0`. Narrowed
  during a review pass from an earlier, overbroad "anything other than `visible`" phrasing —
  `overflow: clip` is a documented exception that doesn't establish a scroll container. Confirmed
  live and on-topic 2026-07-21.
- [MDN — overflow reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow)
  Added during the same review pass, for Lesson 39's "Overflow ownership" section — the precise
  distinction between `overflow: hidden` (still a scroll container: programmatic scroll and
  focus-triggered scroll-into-view both still work, just no visible scrollbar or manual drag/wheel
  scroll) and `overflow: clip` (not a scroll container at all; nothing can scroll it, including
  programmatically). Confirmed live and on-topic 2026-07-21.
- [Tailwind — Responsive Design](https://v3.tailwindcss.com/docs/responsive-design)
  Source for Lesson 39's mobile-first breakpoint section — unprefixed utilities are the baseline,
  prefixed variants override starting at that breakpoint and up. Confirmed live and on-topic
  2026-07-21.
- [MDN — ARIA](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA)
  Primary source for Lesson 40 (optional Track 5 reinforcement) — states the first rule of ARIA
  use (prefer native HTML semantics over adding ARIA to a generic element) directly. Confirmed
  live and on-topic 2026-07-21.
- [W3C WAI ARIA APG — Names and Descriptions](https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/)
  Source for Lesson 40's accessible-name section — what an accessible name is, the three ways to
  supply one (visible label text, `aria-label`, `aria-labelledby`), and which roles are prohibited
  from having one at all. Confirmed live and on-topic 2026-07-21.
- [W3C WAI ARIA APG — Alert pattern](https://www.w3.org/WAI/ARIA/apg/patterns/alert/)
  Source for Lesson 40's `role="alert"` section — an implicit live region, announced automatically
  on appearance without requiring focus. Confirmed live and on-topic 2026-07-21.
- [W3C WAI ARIA APG — Sortable table example](https://www.w3.org/WAI/ARIA/apg/patterns/table/examples/sortable-table/)
  Added during a review pass, for Lesson 40's `aria-sort` finding on `DataTable`'s sortable
  headers — `aria-sort` belongs on the currently-sorted column header, with `ascending`/`descending`
  values. Confirmed live and on-topic 2026-07-22.
- [WCAG 2.2 — Understanding Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
  Added during the same review pass, to ground Lesson 40's "Visible focus" section in an objective,
  three-part test (identifiable, persistent, distinguishable) rather than an unstated judgment
  call. Confirmed live and on-topic 2026-07-22.
- [WCAG 2.2 — Understanding Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
  Added during the same review pass, as the direct citation for Lesson 40's "color is never the
  only signal" claim. Confirmed live and on-topic 2026-07-22.
- [Next.js — Project structure and organization](https://nextjs.org/docs/app/getting-started/project-structure#route-groups)
  Primary source for Lesson 41 (optional Track 5 reinforcement) — the "Route groups" section states
  directly that a parenthesized folder is organizational only and is omitted from the URL. Confirmed
  live and on-topic 2026-07-22.
- [Next.js — Layouts and Pages](https://nextjs.org/docs/app/getting-started/layouts-and-pages)
  Source for Lesson 41's root-layout and nested-layout sections — the root layout's required
  `html`/`body` tags, and layouts nesting automatically via the `children` prop. Confirmed live and
  on-topic 2026-07-22.
- [Next.js — Metadata and OG images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images#static-metadata)
  Source for Lesson 41's metadata section — states directly that the `metadata` object and
  `generateMetadata` exports are only supported in Server Components. Confirmed live and on-topic
  2026-07-22.
- [Next.js — generateMetadata API reference](https://nextjs.org/docs/app/api-reference/functions/generate-metadata#merging)
  Secondary source for Lesson 41 — the Ordering/Merging/Inheriting sections, whose own worked
  example is the direct precedent for this repo's `/dashboard` inheriting the root layout's title
  unchanged. Also the source for *why* metadata exports are Server-Component-only (must resolve
  before the initial HTML is sent). Confirmed live and on-topic 2026-07-22.
- [Next.js — Testing overview](https://nextjs.org/docs/app/guides/testing)
  Primary source for Lesson 42 (optional Track 5 reinforcement) — the Unit/Component/Integration/E2E/
  Snapshot vocabulary, quoted directly rather than paraphrased. Confirmed live and on-topic
  2026-07-22.
- [Next.js — Playwright setup guide](https://nextjs.org/docs/app/guides/testing/playwright)
  Source for Lesson 42's E2E section — Playwright's own description as a tool for automating real
  browsers to write End-to-End tests, used to frame this repo's own ad-hoc Playwright usage from
  Tutorial 11. Confirmed live and on-topic 2026-07-22.
- [Next.js — TypeScript config reference](https://nextjs.org/docs/app/api-reference/config/next-config-js/typescript)
  Source for Lesson 42's precise, version-specific claim that `next build` fails on TypeScript
  errors by default in this repo (`ignoreBuildErrors` is unset in `next.config.ts`). Confirmed live
  and on-topic 2026-07-22.
- [Next.js — ESLint plugin reference](https://nextjs.org/docs/app/api-reference/config/eslint)
  Source for Lesson 42's other half of that same claim — `next lint` (and the build-time ESLint
  integration it powered) was removed starting in Next.js 16, this repo's installed major version,
  so `next build` and `npm run lint` are fully independent checks here despite both existing in the
  same `package.json`. Confirmed live and on-topic 2026-07-22.
- [ESLint — Command Line Interface reference](https://eslint.org/docs/latest/use/command-line-interface)
  Added during Lesson 42's post-draft review pass — its documented exit-code rule (`0` unless there's
  an error, or warnings exceed a set `--max-warnings`) is the source for the corrected claim that
  this repo's bare `eslint` script exits successfully even with warnings present. Confirmed live and
  on-topic 2026-07-22.
- [React — hydrateRoot reference](https://react.dev/reference/react-dom/client/hydrateRoot)
  Added during the same review pass, replacing an inaccurate "byte-level comparison" framing of the
  donut chart's hydration bug — the precise documented expectation is that "the rendered content
  [be] identical with the server-rendered content." Confirmed live and on-topic 2026-07-22.
- [Playwright — Locator.hover() reference](https://playwright.dev/docs/api/class-locator#locator-hover)
  Added during the same review pass — the source for correcting Lesson 42's pointer-events story:
  `hover()` performs an actionability check (which is what actually surfaced the overlay defect) and
  separately targets an element's bounding-box center by default (a wholly separate, test-script-only
  concern for an annulus shape). Confirmed live and on-topic 2026-07-22.
- [Next.js — Server and Client Components: Interleaving](https://nextjs.org/docs/app/getting-started/server-and-client-components#interleaving-server-and-client-components)
  Reused as Lesson 43's one primary source, added during its post-draft review pass — the exact
  documented pattern behind `AppShell` (Client) rendering `DashboardPage` (Server) via `children`: a
  Server Component passed as a prop or child "[is] not imported into the Client Component's module
  graph. [It is] rendered on the server and passed to the Client Component as rendered output."
  Corrected an original draft that had missed `AppShell`'s own real Client boundary entirely.
  Confirmed live and on-topic 2026-07-23.

## Track 6 — Databases & Session Identity

- [PostgreSQL Tutorial (official docs)](https://www.postgresql.org/docs/current/tutorial.html)
  Official but somewhat dense — good once L6.1's "table = spreadsheet the server owns" framing is already in place.
- [psycopg 3 documentation](https://www.psycopg.org/psycopg3/docs/)
  Official docs for the driver this repo uses directly (no ORM). Use for: pairing with Tutorial 12.
- [Neon — Documentation](https://neon.tech/docs/introduction)
  Official docs for the specific hosted Postgres provider this repo uses (branching model — `main`/`dev`/`test` — is a Neon-specific feature worth understanding).
- [MDN — Window.localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
  Use for: L6.2, the concrete browser API `lib/session-id.ts` is built on.

## Track 7 — Deployment & Operations

- [MDN — Cross-Origin Resource Sharing (CORS)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
  The best plain-language explanation of what CORS actually is and why a backend must explicitly allow a frontend's origin. Use for: L7.1, directly explains the `CORS_ALLOWED_ORIGINS` env var and the trailing-slash bug this repo actually hit.
- [Render — Documentation](https://render.com/docs)
  Official docs for the backend host this repo deploys to.
- [Vercel — Documentation](https://vercel.com/docs)
  Official docs for the frontend host this repo deploys to.

## Track 8 — Capstone / Meta-Pattern

- [Michael Nygard — Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
  The original post that defined the ADR pattern this repo's own `docs/adr/` follows. Read this *after* the capstone re-read of the repo's own ADRs, to see how closely (or not) this project's practice matches the source pattern.

## Gaps

- No standalone beginner resource identified yet for "greedy/priority-ordered algorithms in plain language" (shipped as `0012`) — currently relying on the repo's own spec file as the primary source. Confirmed still the right call when Track 2 was actually built (2026-07-15) — the lesson's worked example (a 10-unit-stock, two-competing-orders scenario) taught the idea faster than a generic algorithms resource would have. Revisit only if a future learner finds the lesson's own example insufficient.
- No resource yet for "what is a database migration" at true first-principles level (L6.3) — most available material assumes SQL familiarity already. Flag for a future search pass once Track 6 is imminent.

## Wisdom (Communities)

Not yet populated — the mission as stated (interview readiness, reusable patterns, safe extension) is currently a solo-learning goal without a stated community-practice need. Revisit if the learner wants real-world feedback on interview answers or code review from other engineers (e.g. r/ExperiencedDevs, r/cscareerquestions for interview-specific practice, or a local/company code-review partner for the "safely extend it" goal).
