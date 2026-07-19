/teach to build optional Track 5 — UI Components & Next.js reinforcement lessons as a companion
course to Tutorials 08–11, not a rewrite of the four prerequisite lessons or the generated
tutorials.

Track 5's required roadmap arc is already complete:

- `0031-browser-output-and-components.html`
- `0032-react-minimum-mental-model.html`
- `0033-server-and-client-components.html`
- `0034-design-tokens-and-semantic-styling.html`
- `docs/tutorials/08-ui-contract-wireframe-planning/README.md`
- `docs/tutorials/09-nextjs-frontend-foundation/README.md`
- `docs/tutorials/10-reusable-ui-components-static-pages/README.md`
- `docs/tutorials/11-portfolio-ui-polish/README.md`

Do not overwrite or expand those files merely to fit the ideas below. If the goal is only to
satisfy `ROADMAP.md`, Track 5 is finished. Use this prompt only when the learner wants deeper
retention and enough frontend fluency to extend the current application independently.

The roadmap also already reserves two later retrospective tutorials:

- Phase 9.1 Visual Alignment Fixes
- Mobile Nav/Shell Responsiveness

Do not pre-empt those retrospectives. In particular, leave their fixed-height shell, page-owned
filtering, literal Tailwind class-map, drawer-state, focus-entry, and route-change-close traces to
their existing briefs in
`docs/tutorials/tutoiral-ideas/track-5-ui-components-nextjs-ideas.md`.

## Read first

Teaching workspace and existing course:

- `docs/teach/MISSION.md`
- `docs/teach/ROADMAP.md`
- `docs/teach/NOTES.md`
- `docs/teach/RESOURCES.md`
- `docs/teach/assets/style.css`
- `docs/teach/assets/quiz.js`
- `docs/teach/lessons/0031-browser-output-and-components.html`
- `docs/teach/lessons/0032-react-minimum-mental-model.html`
- `docs/teach/lessons/0033-server-and-client-components.html`
- `docs/teach/lessons/0034-design-tokens-and-semantic-styling.html`
- `docs/teach/reference/*.html`
- Tutorials 08–11 listed above
- `docs/tutorials/tutoiral-ideas/track-5-ui-components-nextjs-ideas.md`

Current repository evidence:

- `app/layout.tsx`
- `app/(public)/layout.tsx`
- `app/(public)/page.tsx`
- `app/(workspace)/layout.tsx`
- `app/(workspace)/dashboard/page.tsx`
- `components/dashboard/DashboardLiveSections.tsx`
- `components/layout/AppShell.tsx`
- `components/layout/SidebarNav.tsx`
- `components/layout/TopHeader.tsx`
- `components/tables/DataTable.tsx`
- `components/workflow/UploadPanel.tsx`
- `components/feedback/{LoadingState,EmptyState,BusinessErrorMessage}.tsx`
- `components/ui/{Button,Table,Badge,Card}.tsx`
- `components/landing/*.tsx`
- `lib/api-client.ts`
- `lib/session-id.ts`
- `types/index.ts`
- `types/dashboard.ts`
- `docs/plan/portfolio-landing-page/{plan.md,explanation.md,ai-discussion-topics.md}`
- `docs/architect/portfolio-landing-page/{decisions.md,discussion.md,ai-discussion-topics.md}`
- `context/ui-rules.md`
- `context/ui-tokens.md`
- `context/ui-registry.md`

Installed framework documentation — this repo's Next.js version is authoritative:

- `node_modules/next/dist/docs/01-app/01-getting-started/02-project-structure.md`
- `node_modules/next/dist/docs/01-app/01-getting-started/03-layouts-and-pages.md`
- `node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`
- `node_modules/next/dist/docs/01-app/01-getting-started/10-error-handling.md`
- `node_modules/next/dist/docs/01-app/01-getting-started/14-metadata-and-og-images.md`
- `node_modules/next/dist/docs/01-app/02-guides/testing/index.md`
- the specific Jest, Vitest, Playwright, or Cypress guide only if a lesson actually discusses that
  tool

Use official React, TypeScript, MDN, W3C/WAI, Tailwind v3, and installed Next.js documentation as
primary sources. Verify every external URL before adding it to a lesson or `RESOURCES.md`; do not
rely on remembered framework behavior. Useful starting points already verified when this prompt
was written:

- `https://react.dev/learn/passing-props-to-a-component`
- `https://react.dev/learn/state-as-a-snapshot`
- `https://react.dev/learn/synchronizing-with-effects`
- `https://react.dev/learn/you-might-not-need-an-effect`
- `https://react.dev/learn/rendering-lists`
- `https://www.typescriptlang.org/docs/handbook/2/objects.html`
- `https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Introduction`
- `https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/`

## Goal

Move the learner from "I can follow this repo's frontend tutorials" to "I can predict React's
rendering behavior, design a typed and accessible component contract, diagnose layout/state bugs,
and choose an appropriate verification layer before changing the UI."

Keep all three mission drivers visible:

1. explain frontend trade-offs clearly in an interview;
2. reuse the concepts in another React/Next.js application;
3. extend this repository without breaking its contracts, design system, or Server/Client boundary.

## What is already covered — do not duplicate it

- Browser output and the framework-independent component idea: Lesson 31.
- Components, props, state, event handlers, and re-rendering at minimum depth: Lesson 32.
- Server/Client Components, serializable props, and `localStorage`: Lesson 33 and Tutorials 09–10.
- Semantic tokens and the CSS-variable → Tailwind-class pipeline: Lesson 34 and Tutorials 09–11.
- Contract-driven UI planning, finite report states, and documentation drift: Tutorial 08.
- App Router foundation, Tailwind 3.4 setup, mock-data generation, and root layout/page conventions:
  Tutorial 09.
- Component ownership, variants, discriminated unions, generic tables, sorting, status-tone helpers,
  and the function-prop serialization failure: Tutorial 10.
- Hydration mismatch, chart hover/focus behavior, pointer-event bugs, Grid stretch, and bounded visual
  polish: Tutorial 11.
- Multipart `FormData`, API request state, report request state, and browser-owned versus server-owned
  results: Track 4 reinforcement and Tutorial 07.

The lessons below should close gaps between those topics, not summarize them again.

## Recommended optional reinforcement sequence

Start at the next available lesson number after `0034`. The filenames below assume `0035` is still
free; renumber the entire sequence if another track has claimed those numbers. Keep this as a
separate optional chain rather than rewiring Lesson 34's existing link to Tutorial 08.

1. `0035-tsx-and-typed-component-props.html`

   Teach the missing bridge from plain JavaScript/React vocabulary to the TypeScript actually used
   in this repo: JSX expressions, destructured props, optional props, literal unions,
   `ReactNode`/`children`, callback prop signatures, and why a component's prop type is an API
   contract. Compare `MetricCard`, `UploadPanel`, and the public/workspace layouts. Keep generics as
   a preview for Lesson 38 rather than teaching them all at once.

   Tangible win: the learner can read a component signature and predict which call sites typecheck.
   Failure mode: treating TypeScript annotations as decorative comments, then passing an impossible
   combination of props or misunderstanding `children` as a global variable.

2. `0036-render-snapshots-events-and-derived-state.html`

   Deepen Lesson 32 without repeating it. Teach component purity, state as a render-time snapshot,
   event handlers as the place for user-caused work, immutable updates, and values that should be
   computed during render instead of copied into state. Use one workflow page's `currentResult`,
   filtered rows, and request-status branches. Contrast a genuine event with an effect.

   Tangible win: given a state update, the learner predicts the current render and the next render
   before running code. Failure mode: setting state during render or storing a filtered/derived list
   as a second source of truth that drifts from its inputs.

3. `0037-effects-cleanup-and-async-ui.html`

   Teach `useEffect` as synchronization with an external system, not a general "run code later"
   hook. Trace `DashboardLiveSections.tsx`: first render → effect → async dashboard request → loaded
   or failed render → cleanup guard. Explain dependency arrays, stale async completion, unmount
   cleanup, and why the sample fallback is resolved only after the request completes. Contrast this
   with values that Tutorial 10 correctly derives during render/`useMemo`.

   Tangible win: the learner can explain why the `cancelled` guard exists and identify one piece of
   code that does not belong in an effect. Failure mode: updating an unmounted component, flashing
   sample data before live data resolves, or creating an effect loop by depending on the state it
   writes.

4. `0038-list-keys-identity-generics-and-memoized-derivations.html`

   Use `DataTable<T>`, chart segments, dashboard tables, and filtered workflow rows to connect four
   ideas that all depend on identity: generic row types, stable `key` values, immutable sorting, and
   memoized derived arrays. Explain that a key identifies an item among siblings; it is not merely a
   warning suppressor. Teach `useMemo` as a performance/cache tool whose result must remain correct
   without it—not as a place to hide side effects.

   Tangible win: the learner can choose a safe row key and trace `T` from a page's row type through
   `DataTableColumn<T>` to `render(row)`. Failure mode: index keys on reorderable data, mutating the
   prop array with `.sort()`, or believing `useMemo` changes application semantics.

5. `0039-css-layout-flow-flex-grid-and-overflow.html`

   Supply the CSS prerequisite Tutorial 11 currently has to teach while already debugging a real
   layout. Cover normal flow, block sizing, the box model, flex main/cross axes, grid tracks,
   intrinsic minimum sizes, overflow ownership, and mobile-first breakpoints. Use `AppShell`,
   `PublicLayout`, `UploadPanel`, `Table`, and one landing-page section. Keep the fixed-height shell's
   historical repair for the deferred Phase 9.1 retrospective; this lesson should teach the general
   mechanics needed to understand that repair later.

   Tangible win: the learner can point to which ancestor owns height and which descendant owns
   scrolling before changing classes. Failure mode: adding arbitrary widths/heights until one
   screenshot looks right while breaking another viewport or creating nested page scrollbars.

6. `0040-accessible-components-as-contracts.html`

   Teach accessibility as part of a component's public behavior, not a final styling audit. Cover
   semantic HTML before ARIA, accessible names, `<label>`/`htmlFor`/`useId`, buttons versus clickable
   `<div>` elements, keyboard reachability, visible focus, `aria-current`, `aria-expanded`,
   `role="alert"`, decorative `aria-hidden`, and why color cannot be the only status signal. Use
   `UploadPanel`, `TopHeader`, `SidebarNav`, `BusinessErrorMessage`, `DataTable`, and both chart
   components. Leave the drawer's modal/focus-trap decision for the deferred mobile-nav tutorial.

   Tangible win: the learner can state the accessible name and keyboard behavior of a real control.
   Failure mode: adding ARIA that contradicts the DOM, removing focus outlines, or using color alone
   to communicate a business status.

7. `0041-route-groups-layout-composition-and-metadata.html`

   Teach the post-Tutorial-11 application structure introduced by the portfolio landing page:
   `(public)` and `(workspace)` route groups change organization/layout ownership without appearing
   in the URL; the root layout owns global document concerns; nested layouts own their respective
   chrome; and static metadata belongs to Server Components. Trace `/` and `/dashboard` through
   their different layout trees. Explain why route groups are organization, not authorization or
   deployment boundaries.

   Tangible win: the learner predicts the URL and layout stack for any current page from its folder
   path. Failure mode: expecting `(workspace)` to appear in the URL, duplicating global providers in
   both nested layouts, or marking a metadata-exporting page as a Client Component.

8. `0042-frontend-verification-layers.html`

   Teach what each existing check proves and what it cannot prove: TypeScript catches impossible
   shapes; ESLint catches selected code patterns; `next build` proves compilation/renderability;
   HTTP smoke checks prove a route responds; keyboard/manual checks prove interaction behavior; and
   browser automation can prove a full user path. Introduce unit, component, integration, and E2E
   tests from the installed Next.js testing guide without installing a new library or pretending the
   repo already has a frontend test suite. Use Tutorial 11's hydration and pointer-event failures as
   examples of bugs a green build could not catch.

   Tangible win: given a proposed UI change, the learner chooses the smallest verification layer
   that can actually observe its failure mode. Failure mode: treating a successful build as proof of
   accessibility/interactivity, or reaching for brittle screenshot tests when a type/unit assertion
   would be sharper.

9. `0043-track-5-guided-ui-trace.html`

   Capstone rehearsal. Require prediction before every reveal and interleave concepts from the
   optional lessons:

   - Trace a workflow result row from `types/index.ts` → page state → filtered/memoized rows →
     `DataTable<T>` → stable row key → semantic table markup.
   - Trace the dashboard lifecycle from Server Component shell → Client boundary → initial loading
     render → effect and session-aware request → live-or-sample resolution → accessible chart/table
     output.
   - Trace `/` and `/dashboard` from route-group folder → nested layout → root layout → metadata and
     rendered chrome.

   Finish with a 90-second interview drill: "How do you decide whether state, an effect, a Client
   Component boundary, and an E2E test are necessary for a new UI behavior?" A complete answer must
   discuss source of truth, external synchronization, browser-only capabilities, serialization, and
   observable risk.

## Requirements for every generated lesson

- Short, self-contained HTML using `../assets/style.css` and `../assets/quiz.js`; reuse assets by
  default and add a new shared asset only when at least two lessons need it.
- Assume zero prior frontend knowledge. Define JSX, render, effect, DOM, semantic HTML, layout,
  accessible name, and test level before relying on those terms.
- Tie the lesson explicitly to `MISSION.md`: interview explanation, portable engineering skill,
  and safe extension of this repo.
- Cite one high-trust primary source and link the exact current source files the lesson prepares the
  learner to read.
- Include 2–3 retrieval checks using the existing quiz component. Keep answer choices equal in
  length where practical so formatting does not reveal the answer.
- Include one tiny, reversible exercise in a real file or a scratch copy. Require a written or
  spoken prediction before the learner inspects/runs the result.
- Include an immediate feedback loop: a typecheck, a DOM/keyboard observation, a focused search,
  or a comparison against a known source line. Do not leave correctness to self-assessment alone.
- Name the specific failure mode the concept prevents.
- Link backward/forward inside this optional sequence and link to the relevant generated tutorial;
  do not rewrite the original Track 5 navigation chain.
- Use only verbatim snippets from files that currently exist. Verify line numbers immediately
  before authoring; the repo is post-Phase-12 and includes a later portfolio landing page.
- Do not add third-party dependencies or change application code while authoring lessons.
- Do not create learning records until the learner actually answers questions or completes an
  exercise. Lesson authorship is not evidence of learning.

## Suggested reference documents

Create only when their corresponding lessons are generated, and keep them compressed enough to
use during real work:

- `docs/teach/reference/typed-react-component-contract.html`
- `docs/teach/reference/react-render-effect-decision-guide.html`
- `docs/teach/reference/list-identity-and-memoization-checklist.html`
- `docs/teach/reference/css-layout-debugging-checklist.html`
- `docs/teach/reference/accessible-component-contract.html`
- `docs/teach/reference/app-router-layout-map.html`
- `docs/teach/reference/frontend-verification-ladder.html`

## Further topics beyond the current roadmap and generated docs

These are deliberately optional. Add them only if the learner's exercises show the prerequisite
sequence above is comfortable:

- **Route-level failure UI:** design-only practice with `loading.tsx`, `error.tsx`, and
  `not-found.tsx`, explicitly noting that this repo does not currently use all three conventions.
- **Controlled, uncontrolled, and hybrid inputs:** use `UploadPanel`'s local filename plus
  parent-owned `selectedFileName` as a concrete hybrid contract, then compare with the controlled
  Payment Aging date field.
- **Client-boundary budget:** audit how far each `"use client"` boundary pulls imports into the
  client module graph and identify where a smaller interactive leaf could reduce shipped
  JavaScript without breaking composition.
- **Content modeling for UI:** trace `lib/content/portfolio.ts` into small landing components and
  compare content data, component structure, and domain output contracts—three different kinds of
  "data" that should not be conflated.
- **Frontend observability:** distinguish a user-facing error state, a console diagnostic, and a
  production telemetry event before proposing any monitoring library.
- **Visual regression judgment:** decide which layout invariants deserve screenshots and which
  should be asserted structurally; avoid snapshotting every pixel by default.

Do not update `MISSION.md` unless the learner explicitly changes the learning mission. Do not
update `ROADMAP.md`, `NOTES.md`, or `RESOURCES.md` merely because this ideas file exists. If the
optional lessons are actually generated, update `ROADMAP.md` and `NOTES.md` to mark them as
optional Track 5 reinforcement, and update `RESOURCES.md` only with verified sources that were
actually used. Never update `context/progress-tracker.md` or `context/ui-registry.md` for teaching
artifacts.
