# Track 5 Tutorial Ideas — UI Components & Next.js

Use `$tutorial` to generate one code-grounded tutorial for each Track 5 case-study plan folder.
The skill consumes a folder's `plan.md`, `explanation.md`, and `ai-discussion-topics.md` together;
do not create three separate tutorials for those three files.

## Sequence and numbering

Tutorials 01–07 already exist. Preserve the Track 5 mapping stated in the Track 5 section of
`docs/teach/ROADMAP.md`:

1. `phase-7-ui-contract-wireframe-planning` → Tutorial 08
2. `phase-8-nextjs-frontend-foundation` → Tutorial 09
3. `phase-9-reusable-ui-components-static-pages` → Tutorial 10
4. `phase-10.2-portfolio-ui-polish` → Tutorial 11

The roadmap's later "Which `/tutorial` Outputs to Generate First" section still contains an older,
conflicting statement that Phase 12 should become Tutorial 08. For this Track 5 batch, follow the
explicit Track 5 checkpoint mapping above. Do not generate Phase 12 first and consume Tutorial 08.

Treat these two Track 5 folders as lower-priority retrospective tutorials:

- `phase-9.1-visual-alignment-fixes`
- `mobile-nav-shell-responsiveness`

To preserve the roadmap's reserved Tutorial 12 (Phase 12 persistence) and Tutorial 13 (Phase 11
deployment), generate the retrospective tutorials only after Tutorials 12 and 13 exist. They should
then take the next available numbers, expected to be Tutorials 14 and 15. If generated immediately
after Tutorial 11, the tutorial skill will assign 12 and 13 and create a numbering collision with
the roadmap.

## Prerequisite lesson gate

Before generating or deeply consuming Tutorial 08, attend all four Track 5 prerequisite lessons
from `docs/teach/ROADMAP.md`. They have not yet been shipped in `docs/teach/lessons/` at the time
this brief was written; the current lesson chain ends at `0030`.

Use `$teach` first to create, at the next available lesson numbers:

1. **L5.1 — Browser output and components:** HTML as structure, CSS as presentation, JavaScript as
   behavior, and a component as a reusable UI unit independent of React.
2. **L5.2 — React's minimum mental model:** component functions, JSX, props, state, events, and
   render-after-state-change. Use tiny examples before introducing this repo.
3. **L5.3 — Server and Client Components:** where each executes, what can cross the boundary,
   why functions cannot be serialized, and why browser-only APIs such as `localStorage` require a
   Client Component. This must be attended before Tutorial 09 and revisited in Tutorials 10 and 15.
4. **L5.4 — Design tokens and semantic styling:** CSS custom properties, Tailwind utility
   generation, semantic token names, and why this repo forbids hardcoded hex values and raw
   Tailwind palette classes. This must be attended before Tutorial 10.

An optional fifth guided lesson may trace one value through
`src/contracts.py` → `types/index.ts` → a component prop → rendered text. Keep it a retrieval
exercise, not a substitute for the four prerequisite lessons.

## Shared instructions for every Track 5 tutorial

- Run `$tutorial` once per plan folder, in the order above. Do not merge Track 5 into one oversized
  tutorial; each phase answers a different design question.
- Read each plan folder's three files in the skill-required order: `plan.md`, `explanation.md`, then
  `ai-discussion-topics.md`.
- Read every created or modified file named by `plan.md`. When a file is over 300 lines, read it in
  sections before selecting excerpts.
- Read Tutorials 06 and 07 for current series style, then the most relevant earlier Track 5
  tutorial for continuity. Preserve the established `CS & language concepts in this tutorial`
  section in addition to the `$tutorial` skill's required sections.
- Read the installed Next.js documentation before explaining framework behavior. At minimum use:
  `node_modules/next/dist/docs/01-app/01-getting-started/02-project-structure.md`,
  `03-layouts-and-pages.md`, `05-server-and-client-components.md`, `11-css.md`, and
  `node_modules/next/dist/docs/01-app/02-guides/tailwind-v3-css.md` where relevant.
- Embed only verbatim code from files that currently exist in the repository. Use current, verified
  line numbers. Never recreate a deleted Phase 8 stub or an earlier version of a component and
  present it as current code.
- The repository is post-Phase-12. Current frontend files include later API, mobile-navigation,
  and persistence work. State the historical phase boundary near the start of each tutorial and
  label later lines as forward references instead of silently removing or rewriting them.
- Explain why each design was chosen and name the rejected alternative's failure mode. Track 5
  should teach boundaries and trade-offs, not become a tour of Tailwind class names.
- Weave every numbered question from the folder's `ai-discussion-topics.md` into the relevant Part
  as a checkpoint with a collapsible answer. Do not add a separate quiz section.
- Include three challenges: trace, extend, and break-and-fix/design. Keep changes fictional or
  reversible and require the learner to predict first.
- Each end-to-end trace must cross at least three layers, such as Python contract → TypeScript type
  → page/component → rendered UI.
- Do not update `context/progress-tracker.md` or `context/ui-registry.md` when generating tutorials.
  Those files describe shipped features, not teaching artifacts.

---

## Tutorial 08 — UI Contract and Wireframe Planning

```text
/tutorial docs/plan/phase-7-ui-contract-wireframe-planning
```

Write to `docs/tutorials/08-ui-contract-wireframe-planning/README.md`.

### Teaching goal

Show that UI planning can be concrete engineering work before JSX exists. The central invariant is:
every route, table column, KPI, badge, and report state must trace to an existing Python output
contract or to an explicitly documented display-only derivation.

This is a docs-only phase. Treat `context/ui-contract-plan.md` as the phase's main artifact and
`src/contracts.py` plus the three business-module result envelopes as implementation ground truth.
Do not force the tutorial to look code-heavy by inventing frontend code that Phase 7 deliberately
did not build.

### Read before writing

- Track 5 prerequisite lessons L5.1–L5.3
- `docs/tutorials/01-python-foundation/README.md`
- `docs/tutorials/05-payment-aging-core/README.md`
- `docs/plan/phase-7-ui-contract-wireframe-planning/{plan,explanation,ai-discussion-topics}.md`
- `context/ui-contract-plan.md`
- `context/ui-rules.md`
- `context/ui-tokens.md`
- `src/contracts.py`
- `src/order_validation.py`
- `src/inventory_allocation.py`
- `src/payment_aging.py`
- `src/report_export.py`
- `tests/contract_fixtures.py`
- `tests/test_report_export.py`
- `sales_admin_automation_toolkit_ui_specs/` and the Figma reconciliation section only as
  non-authoritative design inputs

### Recommended Parts

1. **Planning from output contracts, not from imagined screens** — why Phase 7 starts with field
   names and result envelopes.
2. **Mirroring Python shapes into TypeScript without semantic translation** — snake_case stays
   intact and optionality must match.
3. **A fixed route set backed by real workflows** — why the plan has five routes and no ERP-style
   Orders/Customers/Analytics expansion.
4. **Direct, derived, and direct/derived status labels** — contrast `Fully Allocated`,
   `Supplier Follow-up`, and `Below Reorder Point`.
5. **Tables and KPIs as declared projections** — every visible field or aggregate names its source
   rows, source fields, and grouping rule.
6. **Report lifecycle as browser state, not a Python contract field** — `Needs Input` →
   `Not Generated` → `Processing` → `Ready`, with failures rendered separately.
7. **Documentation drift as a testable defect** — `requested_quantity` vs. `requested_qty`, the
   67-field mechanical comparison, and the stale `ReportManifest` example.

Map questions 1–3 to Parts 1/2/7, 4–6 to Part 4, 7–9 to Part 6, 10–12 to Part 7, and 13–15 to
Parts 5/1. Preserve all 15 questions.

### Full trace and challenges

Trace `PaymentAgingRow.follow_up_priority` from `src/contracts.py` through the TypeScript planning
block, table-column plan, badge vocabulary, and planned Payment Aging page. Contrast it with the
derived `Supplier Follow-up` label, which comes from list membership rather than a field value.

- **Trace:** audit one KPI and one badge back to their exact Python fields.
- **Extend:** design one allowed display-only aggregate using the source-rows/source-fields/rule
  template; do not invent a business recommendation.
- **Break and fix:** deliberately change one TypeScript field name in a scratch copy and design a
  mechanical drift check that catches it.

---

## Tutorial 09 — Next.js Frontend Foundation

```text
/tutorial docs/plan/phase-8-nextjs-frontend-foundation
```

Write to `docs/tutorials/09-nextjs-frontend-foundation/README.md`.

### Teaching goal

Explain how the Python-first repository gained a Next.js App Router shell without replacing or
coupling itself to the Python project. The tutorial should prove the whole foundation pipeline:
contracts → TypeScript → generated JSON → App Router pages → semantic-token CSS.

### Current-code caveat

Phase 8's route files were stubs and were replaced in later phases. Do not reconstruct those deleted
stubs. Use the current stable foundation files (`app/layout.tsx`, `app/page.tsx`, config, token,
type, and mock-generation files) as verbatim code. Describe the old stub-page role from the plan
documents in prose only, and label current full pages as later evolution.

### Read before writing

- Track 5 lessons L5.1–L5.3
- Tutorial 08
- `docs/plan/phase-8-nextjs-frontend-foundation/{plan,explanation,ai-discussion-topics}.md`
- the installed Next.js docs listed in the shared instructions
- `app/layout.tsx`, `app/page.tsx`, `app/globals.css`
- `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `postcss.config.mjs`
- `tailwind.config.ts`, `package.json`, `package-lock.json`
- `types/index.ts`
- `scripts/generate_mock_data.py`
- `lib/mock-data/*.json`
- `lib/utils.ts`, `components.json`
- `.gitignore`
- `context/ui-contract-plan.md`, `context/ui-tokens.md`, `context/library-docs.md`
- `src/contracts.py`, `tests/contract_fixtures.py`

### Recommended Parts

1. **Scaffold beside Python without clobbering the repo** — scratchpad transplant and protected
   root files.
2. **App Router structure and the root redirect** — layout, page convention, fixed routes, and
   Server Components by default.
3. **Tailwind 3.4 as a deliberate compatibility boundary** — why the v3 pipeline was installed
   manually instead of accepting a v4 scaffold.
4. **The semantic-token pipeline** — CSS variables → Tailwind config → utility classes → rendered
   output.
5. **Why shadcn remained plumbing-only** — the conflicting `--accent` meanings and the failure
   mode of generated parallel tokens.
6. **One contract shape across Python and TypeScript** — verbatim snake_case and no adapter churn.
7. **Build-time fixture bridge, never a runtime test import** — Python generator → committed JSON
   → later UI consumers.
8. **Verification beyond compilation** — package/lockfile checks, built CSS inspection, route
   output, and Python regression tests.

Map questions 1–4 to Part 1, 5–8 to Parts 3/4, 9–13 to Part 5, 14–18 to Parts 6/7, and 19–24 to
Parts 2/8 and a short design-input subsection. Preserve all 24 questions.

### Full trace and challenges

Trace one contract field from `src/contracts.py` → `context/ui-contract-plan.md` →
`types/index.ts` → `scripts/generate_mock_data.py` → one committed JSON file → a current typed
import in `lib/mock-data.ts`. Explicitly separate what Phase 8 built from what later phases consume.

- **Trace:** prove the token pipeline for `bg-surface` from CSS variable to compiled utility use.
- **Extend:** add a type-only example field on paper and list the exact coordinated files and
  regeneration step required; do not edit the real contract.
- **Break and fix:** explain what `create-next-app` at the occupied repo root could overwrite and
  design a preflight that catches it.

---

## Tutorial 10 — Reusable Components and Static Pages

```text
/tutorial docs/plan/phase-9-reusable-ui-components-static-pages
```

Write to `docs/tutorials/10-reusable-ui-components-static-pages/README.md`.

### Teaching goal

Turn L5.1–L5.4 into a real component system. Focus on component responsibility, serializable
Server/Client boundaries, semantic status mapping, and the decision to render an honest static
showcase instead of fake async behavior before FastAPI was connected.

### Current-code caveat

Most Phase 9 components were refined in Phases 9.1, 10, 10.2, Mobile Nav, and 12. Use current code
verbatim and call out later additions in place. Do not describe current workflow pages as static;
they are now live Client Components. Use the Phase 9 plan/explanation for the historical static
showcase decision and stable component regions for code excerpts.

### Read before writing

- Track 5 lessons L5.1–L5.4
- Tutorials 08 and 09
- `docs/plan/phase-9-reusable-ui-components-static-pages/{plan,explanation,ai-discussion-topics}.md`
- `context/ui-registry.md`, `context/ui-rules.md`, `context/ui-tokens.md`
- `components/ui/{Button,Card,Badge,Table}.tsx`
- `components/layout/{AppShell,SidebarNav,TopHeader}.tsx`
- `components/feedback/{EmptyState,LoadingState,BusinessErrorMessage}.tsx`
- `components/workflow/{StatusBadge,MetricCard,ReportCard,UploadPanel,WorkflowStepper}.tsx`
- `components/tables/DataTable.tsx`
- `lib/mock-data.ts`, `lib/formatters.ts`, `types/index.ts`
- all five `app/*/page.tsx` route files, with later-phase code labeled
- installed Next.js Server/Client Component documentation

### Recommended Parts

1. **Primitives rewritten against project tokens** — why generated shadcn defaults were rejected.
2. **Component ownership by responsibility** — layout, feedback, workflow, table, and primitive
   layers.
3. **The Server-to-Client serialization failure** — why `DataTable` render functions forced the
   three workflow pages across the Client boundary.
4. **Status meaning before status color** — explicit domain tone helpers and why the same word
   `High` has two visual meanings.
5. **Static showcase instead of simulated workflow state** — real file selection, immediate mock
   results, no fake timers, and honest unavailable actions at the Phase 9 boundary.
6. **Typed mock data as the only frontend data source** — one assertion boundary in
   `lib/mock-data.ts`.
7. **Generic tables with deliberately small behavior** — local single-column sort and explicit
   empty states, while filtering/pagination stayed out of scope.
8. **Display formatting without changing business meaning** — timezone-safe date parsing and the
   documented `90+ Days Amount` aggregate.
9. **The component registry as a maintenance contract** — implementation and documentation must
   evolve together.

Map questions 1–4 to Part 3, 5–8 to Part 4, 9–11 to Part 1, 12–14 to Part 5, and 15–17 to
Parts 7/9. Preserve all 17 questions.

### Full trace and challenges

Trace one validation error row from typed mock data through a page column definition,
`DataTable`, `StatusBadge`, `severityTone`, `Badge`, and the final semantic token classes. Explain
where a function prop crosses or does not cross the Server/Client boundary.

- **Trace:** follow the two meanings of `High` to their separate tone helpers and call sites.
- **Extend:** design a small Client child that owns one table's column functions while a Server
  parent passes only serializable rows.
- **Break and fix:** pass a render-function-bearing columns array from a Server Component to
  `DataTable`, predict the build failure, then describe the two valid repairs.

---

## Tutorial 11 — Portfolio UI Polish

```text
/tutorial docs/plan/phase-10.2-portfolio-ui-polish
```

Write to `docs/tutorials/11-portfolio-ui-polish/README.md`.

### Teaching goal

Teach visual polish as constrained systems work: tokens, stable component contracts, information
hierarchy, interaction accessibility, and rendered verification. The lesson is not "make it look
nicer"; it is how to improve presentation without changing API contracts or business outcomes.

### Current-code caveat

The fixed-width mobile sidebar limitation recorded in Phase 10.2 was later resolved by
`mobile-nav-shell-responsiveness`; state that it was a valid phase boundary, not a current defect.
Phase 12 also moved live dashboard sections into `DashboardLiveSections.tsx`. Read both the current
dashboard shell and that Client Component when tracing dashboard visuals.

### Read before writing

- Tutorial 10, plus Tutorial 07 for the live-page state that existed before this polish pass
- `docs/plan/phase-10.2-portfolio-ui-polish/{plan,explanation,ai-discussion-topics}.md`
- `docs/architect/phase-10.2-portfolio-ui-polish/`
- `context/ui-tokens.md`, `context/ui-registry.md`
- `app/globals.css`, `tailwind.config.ts`
- `components/ui/Button.tsx`
- `components/layout/SidebarNav.tsx`
- `components/workflow/MetricCard.tsx`, `components/workflow/UploadPanel.tsx`
- `components/tables/TableSectionHeading.tsx`
- `components/charts/DonutBreakdownChart.tsx`
- `components/charts/VerticalBucketBarChart.tsx`
- `app/dashboard/page.tsx`, `components/dashboard/DashboardLiveSections.tsx`
- the three workflow pages

### Recommended Parts

1. **A bounded polish phase with non-goals** — no backend, contracts, or new business metrics.
2. **Inverse-surface tokens as a shared visual role** — one family for sidebar and selected dark
   actions, with tightly scoped consumers.
3. **Restyle internals while preserving prop contracts** — `MetricCard` changes without call-site
   API churn.
4. **Executive hierarchy through deliberate omission** — dashboard KPI consolidation and why
   workflow pages retain full detail.
5. **Two interaction strategies for two chart shapes** — shared React state for the donut versus
   CSS group state for independent bars.
6. **Hydration and pointer-event failures found by real interaction checks** — exact causes and
   repaired invariants.
7. **Grid/flex mechanics behind UploadPanel and chart-card alignment** — fix the layout mechanism,
   not the screenshot's surface symptom.
8. **Verification and scope handoff** — desktop/mobile screenshots, keyboard focus, token scans,
   and explicitly deferring the responsive-nav feature.

Map questions 1–3 to Part 2, 4–8 to Parts 6/7, 9–11 to Part 4, 12–13 to Part 5, and 14–15 to
Part 8. Preserve all 15 questions.

### Full trace and challenges

Trace an Allocation Status segment from saved result/mock fallback → `allocationStatusTone()` →
`DonutBreakdownChart` props → literal stroke class map → keyboard focus → shared tooltip state.
Identify which lines are Phase 10.2 and which are later Phase 12 data-source changes.

- **Trace:** follow `surface-inverse` from CSS variable to sidebar and dark-button consumers.
- **Extend:** design one additional hover/focus affordance while preserving Server Component status
  where no shared JavaScript state is required.
- **Break and fix:** remove `pointer-events-none` from the donut overlay, predict the failed
  interaction, and explain why a screenshot alone may not reveal it.

---

## Retrospective Tutorial — Phase 9.1 Visual Alignment Fixes

```text
/tutorial docs/plan/phase-9.1-visual-alignment-fixes
```

Generate only after Tutorials 12 and 13; use the next available tutorial number, expected 14.
Suggested slug: `visual-alignment-fixes`.

### Teaching goal and current-code caveat

Teach rendered-output review as engineering, not decoration: layout-height invariants, filtering
through composition, literal Tailwind class maps, defensive chart rendering, and display-only
aggregates. Current dashboard data sections now live in `DashboardLiveSections.tsx`; use current
code and describe the Phase 9.1 location in prose rather than quoting obsolete page code.

Read the plan folder, Tutorial 10, Tutorial 11, `context/ui-registry.md`, current dashboard shell
and live sections, all Phase 9.1-created table/chart components, `DataTable.tsx`, `AppShell.tsx`,
`SidebarNav.tsx`, `lib/mock-data.ts`, and the three workflow pages.

Recommended Parts:

1. source review versus rendered verification;
2. the fixed-height shell and internal scroll ownership;
3. filtering by page composition instead of growing `DataTable`;
4. dense table hierarchy, truncation, and numeric alignment;
5. literal `Record<Tone, string>` maps for Tailwind scanning;
6. charts that receive meaning instead of deciding their own tones;
7. zero-total guards and amount-versus-count aggregates;
8. currency-neutral display and documented derived values.

Map questions 1–4 to Parts 1/2, 5–7 to Part 3, 8–10 to Parts 5/6, 11–12 to Part 7, and 13–15
to Parts 7/8. Preserve all 15 questions.

Trace Payment Aging rows through `amountByAgingBucket()` into `VerticalBucketBarChart`, contrasting
that amount aggregate with `aging_bucket_counts`. Challenges should trace a filter, extend a
display-only aggregate, and break/fix a dynamically interpolated Tailwind class.

---

## Retrospective Tutorial — Mobile Nav/Shell Responsiveness

```text
/tutorial docs/plan/mobile-nav-shell-responsiveness
```

Generate after the Phase 9.1 retrospective; use the next available tutorial number, expected 15.
Suggested slug: `mobile-nav-shell-responsiveness`.

### Teaching goal

Use one compact feature to consolidate L5.2 and L5.3: lift shared state to the nearest common
ancestor, keep Server Component children beneath a Client shell, conditionally mount hidden
navigation, manage focus honestly, and avoid claiming modal semantics without a focus trap.

Read the plan folder, Tutorials 09–11, the installed Server/Client Component docs,
`components/layout/{AppShell,TopHeader,SidebarNav}.tsx`, `app/layout.tsx`, `app/globals.css`,
`tailwind.config.ts`, `context/ui-tokens.md`, and the relevant `context/ui-registry.md` entries.

Recommended Parts:

1. why shared drawer state belongs in `AppShell`;
2. Client shell with Server Component `children` versus forbidden function props;
3. separate desktop/mobile wrappers and conditional mounting;
4. visual position versus DOM/tab order;
5. focus entry without pretending there is a focus trap;
6. route-change state adjustment and the render/effect timeline;
7. truthful ARIA (`aria-expanded`, `aria-controls`) and rejected modal claims;
8. overlay token scope and keeping `SidebarNav` viewport-agnostic.

Map questions 1–3 to Parts 1/2, 4–6 to Part 3, 7–10 to Parts 4/5/7, 11–13 to Part 6, and 14–15
to Part 8. Preserve all 15 questions.

Trace a keyboard user opening the drawer: toggle event → `isDrawerOpen` → conditional DOM mount →
`drawerRef` focus effect → first nav link → Escape or route-change closure. Challenges should audit
tab order, compare conditional mount with `inert`, and design what must change before the drawer
could truthfully become an ARIA modal.

## Completion report for the batch

After each tutorial, report the output path, number of Parts, number of implementation files read,
question count woven into checkpoints, and prerequisite chain. After the four core tutorials,
confirm that Track 5's required case-study checkpoints are complete. Report the two retrospective
tutorials separately so they are not mistaken for prerequisites to Tutorials 08–11.
