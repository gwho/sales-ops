# Sales Admin Automation Toolkit — Concept-First Learning Roadmap

Built from: all 7 ADRs (`docs/adr/`), all 3 grilling sessions (`docs/grilling/`), 18 `docs/plan/*` phase folders, `docs/architect/*`, `CONTEXT.md`, `context/architecture.md`, `context/code-standards.md`, `context/project-overview.md`, `context/build-plan.md`, and the real `src/`/`backend/`/`app/` code. No teaching happens in this document — it's the syllabus. See `MISSION.md` for why this exists and `RESOURCES.md` for the external sources it points to.

**Reading this roadmap**: each Concept Track pairs a **prerequisite lesson** (a bare concept, assuming nothing) with a **case-study checkpoint** (a real phase of this repo that demonstrates it, usually generated via `/tutorial`). Tracks are ordered by dependency, not by phase number — Track 4 (Frontend) intentionally sits after Track 2/3 (Python core), because this repo's frontend is *derived from* its backend contracts, and understanding that derivation is itself one of the mission's target skills.

---

## Concept Track Overview

| Track | Concept theme | Case-study phase(s) | Depends on |
|---|---|---|---|
| 0 | Reading this repo | — (meta, no dedicated tutorial) | none |
| 1 | Python, data-as-tables, contracts | Phase 1, Phase 2 | Track 0 |
| 2 | Business rules & testing | Phase 3, Phase 4, Phase 5 | Track 1 |
| 3 | Presentation without leakage | Phase 6 | Track 2 |
| 4 | HTTP APIs & statelessness | Phase 10 | Track 2 |
| 5 | UI components & Next.js | Phase 7, Phase 8, Phase 9/9.1, Phase 10.2 | Track 1 (contracts), can start after Track 2 or 3 |
| 6 | Databases & breaking statelessness deliberately | Phase 12 | Track 4, Track 5 |
| 7 | Deployment & operations | Phase 11 | Track 4, Track 5 |
| 8 | Capstone: the meta-pattern (ADRs, Scope Gate, grilling) | all ADRs + grilling sessions, revisited as a set | everything above |

---

## Track 0 — Reading This Repo (meta, no /tutorial)

No prior knowledge assumed beyond "a repo is a folder of files under version control."

**Prequel added (2026-07-15):** even that floor turned out to be one assumption too high. The
learner asked, verbatim, for L1.1's exact scope ("what a repository is, what a Python module is,
what pytest does, what uv is doing, how to read a test file") — but by the time that prompt
arrived, L1.1 already existed as `0002`/`0003` and L0.1 already existed as `0001`. Rather than
regenerate duplicate content, the gap turned out to be one level lower: `0001` itself assumes the
reader already knows what a file, folder, path, file extension, and terminal command *are* — it
never teaches those, it just uses the vocabulary. Shipped
`0000-files-folders-and-the-terminal.html` to cover exactly that, wired as `0001`'s new
back-link. Nothing in `0001`–`0007` was rewritten; this is a pure prequel insertion.

- **Lesson 0.1**: What a Python module/package is, what `src/`, `backend/`, `app/` each mean as top-level folders, and how this repo's own doc trail works (`docs/adr` = a decision and why; `docs/plan` = what was built and why; `docs/grilling` = the argument that happened *before* the decision). This is the map before the territory.

---

## Track 1 — Python, Data-as-Tables, and Contracts

**Status: lessons shipped (2026-07-14)**, as a finer 7-lesson split of the original L0.1/L1.1–L1.3
sketch below — see `docs/teach/lessons/0001`–`0007` and `docs/teach/reference/*.html`. The
prerequisite-lesson bullets below are kept as the original syllabus sketch; the mapping to what was
actually shipped is:

| Sketch | Shipped as |
|---|---|
| L0.1 (Track 0 — repo/doc-trail navigation) | `0001-how-to-read-this-repo-and-tutorials.html` |
| L1.1 (module/function basics, pytest/uv, test reading) | split across `0002-python-files-functions-and-data.html` and `0003-uv-pytest-and-test-reading.html` |
| L1.2 (DataFrame minimum model) | `0005-excel-boundaries-and-table-shaped-data.html` |
| L1.3 (dict vs. TypedDict, contracts) | `0004-contracts-typeddict-and-json-shapes.html` |
| *(not previously sketched)* | `0006-demo-data-vs-test-data.html` — prerequisite for Tutorial 2's fixture-design discussion, previously left folded into Tutorial 2's own intro (see the old note at "First 8–12 Lessons" item 5); now a standalone lesson instead |
| *(not previously sketched)* | `0007-track-1-guided-trace.html` — new capstone: rehearses table-shape → contract-shape → test-assertion prediction on a real sample-data row, before starting Tutorial 1 |

**Prerequisite lessons (teach before touching real code):**
- **L1.1**: What a repository/module/function is; what `pytest` and `uv` do; how to read a test file top-to-bottom. *(This is exactly the lesson you should ask for before Tutorial 1 — see your own example prompt below.)*
- **L1.2**: Data as tables — what a spreadsheet row/column becomes once loaded into code (a pandas `DataFrame`: rows, columns, `.iloc`, filtering). Minimum viable mental model only.
- **L1.3**: Structured data shapes — plain `dict` vs. Python's `TypedDict`, and why a codebase would bother declaring the *shape* of its data up front (a "contract"). This is the single idea every later layer (business modules, report export, UI types, API responses, Postgres rows) turns out to be a projection of — it has to land before Track 2's case studies make sense.

**Case-study checkpoints:**
- `/tutorial docs/plan/phase-1-python-foundation` → **Tutorial 1**. Read alongside `src/contracts.py` and `src/excel_io.py`. Confirms: TypedDict-as-contract, why `excel_io.py` never contains business rules.
- `/tutorial docs/plan/phase-2-sample-data` → **Tutorial 2**. Read alongside `src/sample_data.py`. Concept: demo fixtures (believable, mostly-clean) vs. test fixtures (exhaustive one-rule-per-case) are different tools for different jobs; deterministic-data design (why dates are parameterized, not hardcoded to "today").

---

## Track 2 — Business Rules & Testing Discipline

**Status: lessons shipped (2026-07-15)**, as a 7-lesson split of the original L2.1–L2.4 sketch
below, following the exact same "finer split than the syllabus sketch" pattern Track 1 used — see
`docs/teach/lessons/0008`–`0014` and `docs/teach/reference/*.html`. The prerequisite-lesson bullets
below are kept as the original syllabus sketch; the mapping to what was actually shipped is:

| Sketch | Shipped as |
|---|---|
| L2.1 (business rule vs. code rule, a test as proof) | `0008-business-rules-vs-code-rules.html` |
| L2.2 (structured errors instead of printing/crashing, result envelopes) | `0009-structured-errors-and-result-envelopes.html` |
| *(the "Testing-as-a-skill lesson" bullet below, previously left vague)* | `0010-reading-tests-as-specifications.html` — builder helpers (`**overrides`), `@pytest.mark.parametrize`, section comments as a table of contents |
| *(not previously sketched)* | `0011-independent-rule-evaluation-and-data-issues.html` — the "collect every finding" shape (OV-001, PA-006/PA-007) contrasted against the "first-match-wins" shape (`_follow_up_priority`), a distinction the original sketch didn't separate out |
| L2.3 (priority-ordered/greedy processing, before Phase 4) | `0012-priority-ordered-processing-and-mutable-state.html` |
| L2.4 (date arithmetic, signed quantities, before Phase 5) | `0013-date-arithmetic-boundaries-and-signed-values.html` |
| *(not previously sketched)* | `0014-track-2-guided-test-trace.html` — capstone, mirrors `0007`'s role: one real test from each of Phases 3/4/5, predict-then-reveal, before starting Tutorial 03 |

New reference docs shipped alongside: `business-rule-testing-glossary.html`,
`test-reading-patterns.html` (extends Track 1's pytest cheat sheet with builder helpers and
parametrize — doesn't repeat `assert`/`pytest.raises`), `boundary-case-checklist.html` (every
boundary actually tested across the three Track 2 modules, plus one honestly-flagged gap — Watch's
`-7` edge has no dedicated test today), and `result-envelope-pattern.html` (all three envelopes'
field names side by side).

**Prerequisite lessons (original syllabus sketch):**
- **L2.1**: What a "business rule" is (a real-world policy, e.g. "an order missing a delivery date is invalid") vs. what a unit test actually verifies (that the code enforces the policy correctly on a specific, known input).
- **L2.2**: Deterministic, side-effect-free functions — why this repo's rule is "business logic never prints, always returns structured errors," and what "no hidden global state" buys you when testing.
- **L2.3** *(before Phase 4 specifically)*: Sequential/priority-ordered processing — a plain-language walk through "process the highest-priority item first, and once it's filled, move to the next" (a greedy allocation algorithm, taught without the word "algorithm" scaring anyone).
- **L2.4** *(before Phase 5 specifically)*: Date arithmetic and signed vs. unsigned quantities — why "days overdue" being allowed to go *negative* (not floored at zero) is a deliberate design choice, not a bug.

**Case-study checkpoints (in this order — Phase 4 genuinely consumes Phase 3's output, so the sequence isn't arbitrary):**
- `/tutorial docs/plan/phase-3-order-validation-core` → **Tutorial 3**. First full business module. Establishes the "envelope" return pattern (`{summary, valid_orders, errors}`) reused everywhere after.
- `/tutorial docs/plan/phase-4-inventory-allocation-core` → **Tutorial 4**. Concept: a real pipeline dependency — this module's input is *the previous module's output*, not fresh data. Also: `allocatable_qty` vs. raw `available_qty` (why "looks full on paper" isn't the same as "available").
- `/tutorial docs/plan/phase-5-payment-aging-core` → **Tutorial 5**. Third repetition of the envelope pattern — by now it should feel familiar rather than novel, which is itself the point (spaced repetition of one structural idea across three different business domains).

**Settled (2026-07-14): Phase 3 → 4 → 5 stays intact as one unbroken arc, not deferred.** Confirmed with the learner — Phase 4 teaches dependency-between-workflows and Phase 5 tests whether the contract-driven envelope pattern actually generalizes; breaking the arc for Phase 6/10/12 would have undercut both. See the revised "Which `/tutorial` Outputs to Generate First" section below.

**Testing-as-a-skill lesson** (woven in after Tutorial 3, not a separate phase folder): read `tests/test_order_validation.py` and `tests/contract_fixtures.py` side by side — hand-authored fixtures vs. real sample Excel data, and why both exist.

---

## Track 3 — Presentation Without Leakage

**Status: lessons shipped (2026-07-15)**, as a 7-lesson expansion of the original single L3.1
sketch below, following the same "finer split than the syllabus sketch" pattern Tracks 1 and 2
used — see `docs/teach/lessons/0015`–`0021` and `docs/teach/reference/*.html`. The
prerequisite-lesson bullet below is kept as the original syllabus sketch; the mapping to what was
actually shipped is:

| Sketch | Shipped as |
|---|---|
| L3.1 (presentation layer vs. business logic layer, the recalculation-leak failure mode) | `0015-presentation-layer-vs-business-logic.html` |
| *(not previously sketched)* | `0016-consuming-contracts-without-changing-them.html` — the producer/consumer half of the contract pattern Track 2's Lesson 9 taught from the producer's side only; covers the real `ImportError` `explanation.md` records and the "separate parameter, not a new field" escape hatch |
| *(not previously sketched)* | `0017-excel-workbooks-sheets-and-manifests.html` — workbook/sheet/row/cell/header-row/manifest vocabulary, and `wb.sheetnames` as a single-source-of-truth example |
| *(not previously sketched)* | `0018-serialization-boundaries-and-safe-cell-values.html` — `None`/`NaN`/`NaT`/`pd.NA` as this repo's four "nothing" representations, `_safe_cell_value`, and why tests must save/reload with `openpyxl.load_workbook()` rather than inspect an in-memory `Workbook` |
| *(not previously sketched)* | `0019-explicit-columns-and-empty-reports.html` — why sheet headers come from explicit constants, not `rows[0].keys()`, tying back to Track 1's `NotRequired` lesson |
| *(not previously sketched)* | `0020-allow-lists-hidden-state-and-safe-defaults.html` — allow-list vs. deny-list as a general safety pattern, and why `report_id` carries no module-level counter |
| *(not previously sketched)* | `0021-track-3-guided-report-trace.html` — capstone, mirrors `0007`'s and `0014`'s role: one real `PaymentAgingRow` traced end to end into a saved, reloaded workbook, before starting Tutorial 06 |

New reference docs shipped alongside: `presentation-layer-glossary.html` (Lessons 15/16/20's
terms), `contract-consumer-pattern.html` (the producer/consumer pattern, generalized past this
one track), `report-export-mental-model.html` (Excel vocabulary plus the four-step
`export_*_report` shape), and `serialization-boundary-checklist.html` (this repo's four "nothing"
values plus a reusable checklist for any future serialization boundary — JSON, Postgres — not just
Excel).

**Prerequisite lesson (original syllabus sketch):**
- **L3.1**: Separation of concerns — a "presentation layer" (formats already-computed results for humans) vs. a "business logic layer" (decides what the results *are*). Why mixing them is a common real-world bug source (a report that quietly recomputes and disagrees with the screen).

**Case-study checkpoint:**
- `/tutorial docs/plan/phase-6-excel-report-export` → **Tutorial 6**. Read alongside `src/report_export.py`. Concept: `report_export.py` never recalculates anything — it only formats. Good first example of "what's on the *other side* of a contract" (consumption, not production). **Sequenced after Phases 3–5, not before** — report export is easiest to understand once every one of the 13 output-contract families is already familiar from having built/tested them; reading it earlier would mean formatting fields you haven't seen produced yet.

---

## Track 4 — HTTP APIs & Statelessness

**Status: prerequisite lessons shipped (2026-07-16)** — see `docs/teach/lessons/0022`–`0023`. Unlike
Tracks 1-3, this track's syllabus sketch (L4.1, L4.2 below) was shipped almost exactly as written —
two short, deliberately code-light lessons, not a finer split — since Tutorial 07 itself carries the
code depth. No new reference docs were added; nothing in these two lessons recurs elsewhere yet.

**Prerequisite lessons:**
- **L4.1**: What HTTP is — request/response, verbs (GET/POST), status codes (200/400/404/500), and what "an API" means in the most concrete possible terms (a URL that returns structured data instead of a web page). Shipped as `0022-http-request-response-and-multipart-uploads.html`.
- **L4.2**: What "stateless" means for a server, and what a "trust boundary" is — why a server should never treat client-submitted data as authoritative for something it could recompute itself. Shipped as `0023-statelessness-and-trust-boundaries.html`.

**Case-study checkpoint:**
- `/tutorial docs/plan/phase-10-fastapi-integration` → **Tutorial 7**. Pairs with `docs/grilling/phase-10-fastapi-integration/` (the actual argument about whether to persist a "Workflow Run," resolved: no). Concept: statelessness as a *testable property*, not a slogan; report endpoints always re-accept files and recompute rather than trusting a stored result.

**Status: optional reinforcement sequence shipped (2026-07-16, later session)** — seven lessons
(`docs/teach/lessons/0024`–`0030`) plus five new reference docs, built *after* Tutorial 07 was
already complete, from a fully-specified task file the user had written at
`docs/teach/lessons-ideas/track-4-ideas.md` (same "follow the user's own spec closely" pattern as
the Track 2/3 `track2-ideas.md`/`track-3-ideas.md` sessions). This is **optional Track 4
reinforcement, not a change to the settled L4.1/L4.2 prerequisite shape above** — the roadmap's
"Track 4 is already ready for Tutorial 07" status stands unchanged; these seven lessons exist only
for retention *after* Tutorial 07, rehearsing one concept each rather than teaching anything new.

| Lesson | Concept rehearsed |
|---|---|
| `0024-api-endpoint-map-and-route-boundaries.html` | The 7 real endpoints as 3 shapes (Workflow Result / Report Artifact / sample-file download), not interchangeable URLs |
| `0025-formdata-uploadfile-and-loader-callbacks.html` | The `FormData` key → `Annotated[UploadFile, File()]` → `read_xlsx_upload` → `load_*` chain; the multipart-boundary `Content-Type` trap |
| `0026-api-error-contracts-and-business-readable-failures.html` | The uniform `{"detail": "string"}` shape across all three error sources; the `raise_server_exceptions=False` testing gotcha |
| `0027-cors-exposed-headers-and-browser-downloads.html` | `allow_origins` vs. `expose_headers` as two separate permissions; `postReport()`/`downloadBlob()` vs. a plain `<a download>` |
| `0028-thin-api-adapters-and-framework-free-business-core.html` | The adapter/business-rule boundary; ends with a design-only "fourth workflow" rehearsal exercise |
| `0029-client-state-vs-server-state-current-result-vs-report-request.html` | Browser-owned `currentResult`/`RequestStatus`/`ReportRequestState` vs. server memory (none, in Phase 10) — Phase 12 kept as a forward reference only |
| `0030-track-4-guided-api-trace.html` | Capstone — two full request traces (Run Validation, Download Inventory Allocation Report) plus a 90-second interview drill on "why not generate-once-fetch-by-ID" |

New reference docs shipped alongside: `http-api-glossary.html` (companion to 0022/0024/0025),
`statelessness-trust-boundary-checklist.html` (companion to 0023/0024 — generalizes past this repo),
`api-error-contract-pattern.html` (companion to 0026), `cors-and-downloads-cheat-sheet.html`
(companion to 0027), and `thin-api-adapter-pattern.html` (companion to 0028).

Navigation follows the same precedent Tracks 2/3 established: `0024` starts its own chain with
`← You are here` rather than rewiring `0023`'s existing "Next: Tutorial 07 →" — `0023` is untouched.
`0030` (capstone) has no forward link — "Track complete" — since there's no further numbered Track
4 content waiting on the other side of it.

---

## Track 5 — UI Components & Next.js

**Status: prerequisite lessons shipped (2026-07-17)** as `docs/teach/lessons/0031`–`0034`, from a
fully-specified `/tutorial` task file at
`docs/tutorials/tutoiral-ideas/track-5-ui-components-nextjs-ideas.md`. Unlike Tracks 1–3, this
prerequisite set shipped close to literally four lessons for four syllabus items (the same
close-to-literal pattern Track 4's `0022`/`0023` used) rather than a finer split — the task file's
own brief scoped each lesson tightly and reserved code depth for the Tutorials themselves. The
mapping:

| Sketch | Shipped as |
|---|---|
| L5.1 (browser output, component as a framework-free concept) | `0031-browser-output-and-components.html` |
| L5.2 (React's minimum mental model) | `0032-react-minimum-mental-model.html` |
| L5.3 (Server/Client Components) | `0033-server-and-client-components.html` |
| L5.4 (design tokens and semantic styling) | `0034-design-tokens-and-semantic-styling.html` |

**Prerequisite lessons (original syllabus sketch):**
- **L5.1**: What a browser renders (HTML/CSS/JS, bare minimum) and what a UI "component" is as a concept, independent of any framework.
- **L5.2**: React basics — components, props, state — the smallest mental model that makes the next lesson legible.
- **L5.3**: Next.js App Router's Server Component vs. Client Component split, and *why* it exists (a server-rendered page can't access browser-only things like `localStorage`). This single rule recurs across four+ phases in this repo — it deserves its own dedicated lesson before the first case study, not a footnote.
- **L5.4** *(before Phase 9 specifically)*: What a design-token system is and why "no hardcoded hex colors, no raw Tailwind color classes" is a real engineering rule, not a style preference.

**Case-study checkpoints: shipped (2026-07-17)**, as `docs/tutorials/08-ui-contract-wireframe-planning/`
through `11-portfolio-ui-polish/`, from the same task-file-driven session that shipped the four
prerequisite lessons above (`docs/tutorials/tutoiral-ideas/track-5-ui-components-nextjs-ideas.md`).
Track 5's full required arc — L5.1–L5.4 through Tutorial 11 — is now complete:
- `/tutorial docs/plan/phase-7-ui-contract-wireframe-planning` → **Tutorial 8** (961 lines, 7 Parts, all 15 `ai-discussion-topics.md` questions woven in). Docs-only phase — read as a case study in "plan a UI's data shape without writing UI code yet," and the badge-label rule (every status label must trace to a real contract field, never an invented one).
- `/tutorial docs/plan/phase-8-nextjs-frontend-foundation` → **Tutorial 9** (1204 lines, 8 Parts, all 24 questions). First real frontend code. Confirms L5.3 against the actual `app/` folder structure.
- `/tutorial docs/plan/phase-9-reusable-ui-components-static-pages` → **Tutorial 10** (1058 lines, 9 Parts, all 17 questions). Component registry practice (`context/ui-registry.md`), the token discipline from L5.4 in action.
- `/tutorial docs/plan/phase-10.2-portfolio-ui-polish` → **Tutorial 11** (1015 lines, 8 Parts, all 15 questions).
- *(Second-wave, lower priority, deliberately deferred)*: `phase-9.1-visual-alignment-fixes`,
  `mobile-nav-shell-responsiveness` — the task file that shipped Tutorials 8–11 explicitly reserves
  these for *after* Tutorial 12 (Phase 12/Postgres) and Tutorial 13 (Phase 11/deployment) exist, so
  they land as Tutorials 14–15 rather than colliding with those reserved numbers. Neither Tutorial
  12 nor 13 exists yet as of this note — do not generate the retrospectives until they do.

**Status: optional reinforcement in progress (2026-07-20, four of nine lessons)** — from a
fully-specified task file at `docs/teach/lessons-ideas/track-5-reinforcement-ideas.md`, the same
"follow the user's own spec closely" pattern the Track 2/3/4 `*-ideas.md` sessions used. This is
**optional Track 5 reinforcement, not a change to the settled L5.1–L5.4 prerequisite shape
above** — Track 5's "ready for Tutorial 08" status stands unchanged; these lessons exist only for
retention *after* Tutorial 11, one concept each. The task file specs nine lessons
(`0035`–`0043`) plus seven reference docs; four lessons have shipped so far, generated one at a
time by request rather than as a single batch.

| Lesson | Concept rehearsed |
|---|---|
| `0035-tsx-and-typed-component-props.html` | TSX as JSX-plus-typechecking; named vs. inline prop types; optional props and defaults; `ReactNode`/children; literal unions (`Tone`); callback prop signatures; why a function prop is fine between two Client Components but not across the Server→Client boundary (Lesson 33) |
| `0036-render-snapshots-events-and-derived-state.html` | State as a fixed value captured for one render (not a live variable) using `runValidation`'s setter calls; immutable whole-object replacement (`setCurrentResult(result)`); a genuine click-caused event vs. the external-synchronization case an Effect exists for (forward reference to Lesson 37); derived `const`s (`canSubmit`, `currentStep`, `errorFiltersActive`, `orderFiltersActive`) computed fresh every render instead of copied into state |
| `0037-effects-cleanup-and-async-ui.html` | `useEffect` as synchronization caused by rendering itself, not by a user action (reaching outside React is necessary but not sufficient — Lesson 36's click-triggered `runValidation` reaches outside React too, correctly, without an Effect), traced through `DashboardLiveSections.tsx`'s one real Effect; the empty dependency array as "runs once per mount in production, twice in development Strict Mode" and as the correct declaration that `status` is this Effect's own output, not an input (with the corrected, non-catastrophic account of what listing `status` would actually cause: one redundant re-fetch, not an infinite loop); the `cancelled` cleanup guard against a stale response from any cleaned-up Effect instance — unmount or a Strict Mode remount — landing on top of a newer one; the early `status === "loading"` return that prevents flashing sample data before live data resolves; a brief bridge back to `0036`/Tutorial 10's `useMemo`-derived `filteredErrors` as the render-time (non-Effect) side of the same dividing line |
| `0038-list-keys-identity-generics-and-memoized-derivations.html` | The two forward references from `0035` (generics) and `0037` (`useMemo`) finally taught, alongside keys and immutable sorting, using `DataTable<T>` and its two `order-validation/page.tsx` call sites as one running example: tracing `T` from `DataTableColumn<ValidationErrorRow>[]` through `render(row)` to the call site's inferred type parameter; keys as two separate requirements — stable across reorders *and* unique among siblings — with index keys reframed as a latent correctness defect in a reusable sortable table (not a claim that this text-only table currently displays wrong data) and, critically, `getRowKey`'s own real composite key (`` `${r.row_number}-${r.error_code}` ``) shown to be stable but **not actually unique**, proven by a real test (`test_ov001_emits_one_error_per_missing_field_in_fixed_order`) where one row emits two same-code OV-001 errors — named as a genuine, unfixed defect in the current repo, not silently glossed over, with the real fix (a dedicated Python-emitted identity field) named as out of a frontend lesson's scope per Field Scope Boundary; `[...data].sort(...)` as immutable sort meeting a genuinely mutating array method; `useMemo`'s dependency array explained via `Object.is` reference equality specifically (`ERROR_COLUMNS`'s stable module-level reference, `filteredErrors`'s own memoization, `sort`'s fresh object literal on every click) rather than vague "when something changes" language; and a closing synthesis distinguishing three different senses of "identity" in the lesson (compile-time generics, runtime keys, reference-equality memo deps) so they aren't mistaken for one mechanism. The exercise's second part also runs `npm run lint` against the real, verified `react-hooks/exhaustive-deps` warning, alongside the typecheck and browser checks |

New reference doc shipped alongside `0035`: `typed-react-component-contract.html`. `0036`, `0037`,
and `0038` shipped without their own reference docs — the task file's
`react-render-effect-decision-guide.html` reads as a synthesis of `0036`'s render/event material
and `0037`'s Effect material specifically, and `list-identity-and-memoization-checklist.html` is
`0038`'s intended companion per the task file's own reference-doc list, but neither was requested
this session.

Navigation follows the same precedent Track 4's `0024`–`0030` established: `0035` starts its own
chain without rewiring `0034`'s existing "Next: Tutorial 08 →" — `0034` is untouched. Each shipped
lesson's forward nav (top and bottom) is rewired from a plain non-linking placeholder to a real
link as soon as the next lesson actually ships — `0035`→`0036`, `0036`→`0037`, and now
`0037`→`0038`. Since `0039`–`0043` don't exist yet, `0038`'s own forward nav is the placeholder
note, the same convention every prior lesson in this chain used while it was the newest one.

---

## Track 6 — Databases & Breaking Statelessness Deliberately

**Prerequisite lessons:**
- **L6.1**: What a relational database is, at the level of "a table is like a spreadsheet the server owns," plus specifically what a JSONB column is and why this repo chose "one JSONB row per session+workflow" over a fully normalized schema.
- **L6.2**: Identity without authentication — what a session is, what a UUID is, why `localStorage` + a request header was chosen over cookies here (a real cross-origin trade-off between Vercel and Render).
- **L6.3**: What a database migration and a transaction are, at the "why would code need to change a table's shape safely" level.

**Case-study checkpoint:**
- `/tutorial docs/plan/phase-12-postgres-backed-latest-session-dashboard` → **Tutorial 12**. Pairs with `docs/grilling/phase-12-postgres-backed-latest-session-dashboard/`. This is the single most conceptually dense phase in the repo — it directly requires Track 4 (statelessness) and Track 5's L5.3 (RSC/Client split) to appreciate its central insight: the choice of `localStorage` for session identity is what *structurally forces* the dashboard to be a Client Component. Save this for when both prerequisite tracks are genuinely solid, not just "covered."

---

## Track 7 — Deployment & Operations

**Prerequisite lesson:**
- **L7.1**: What "deployment" means (a build step vs. a running server), what an environment variable is, and what CORS actually is (a browser-enforced same-origin restriction, and why a backend has to explicitly allow a frontend's origin).

**Case-study checkpoint:**
- `/tutorial docs/plan/phase-11-deployment-baseline` → **Tutorial 13** *(lower code density than others — optional to fully tutorial-ize; may work fine as a direct read of `docs/plan/phase-11-deployment-baseline/explanation.md` plus the README's "Live Demo" section instead)*.

---

## Track 8 — Capstone: The Meta-Pattern

No new prerequisite lesson — this track is *only* legible after living through the case studies above. Teaching it first would be inert vocabulary.

- Revisit, as a set: all 7 ADRs, all 3 grilling sessions, `CONTEXT.md`'s process terms (Output Contract, Field Scope Boundary, Scope Gate, Anonymous Session ID, etc.).
- Extract explicitly, as portable skills independent of this repo: the ADR three-part worthiness test (seen concretely in the Phase 10 grilling session — not everything becomes an ADR, only decisions that pass a specific test), "grill before you architect" sequencing, the Scope Gate mechanical check (V1/unlabeled vs. Optional/V1.5/V2 — a rule designed to prevent scope creep *without relying on judgment calls*), Field Scope Boundary (contracts may be asymmetric across modules — resist the urge to add a field "for symmetry"), and the `docs/plan` + `docs/architect`/`docs/grilling` + `/feature-docs` + `/imprint` documentation habit itself as a reusable practice.
- `docs/plan/python-first-sequence/` and `docs/plan/context-reset/` are best read here, as background for *why* the phase sequence itself was reordered mid-project — not worth a dedicated `/tutorial` (they're docs-only, little code to trace), but genuinely instructive as capstone reading.

---

## First 8–12 Lessons, In Dependency Order

This is the literal `/teach` queue — start at the top, don't skip:

0. **Lesson 0** — Files, folders, paths, file extensions, and what a terminal/command is, from
   true zero. Shipped as `0000-files-folders-and-the-terminal.html` (2026-07-15) — genuinely
   below L0.1, not a rename of it.
1. **L0.1** — What a repo/module is, how this repo's own doc trail works.
2. **L1.1** — Python module/function basics, what pytest and uv do, how to read a test file. *(Your own example prompt — this is lesson 2, right before Tutorial 1.)*
3. **L1.2** — Data as tables (pandas DataFrame, minimum viable model).
4. **L1.3** — dict vs. TypedDict, contracts as a concept. → **Tutorial 1** (`phase-1-python-foundation`)
5. *(fixture-design concept, folded into Tutorial 2's intro rather than a standalone lesson)* → **Tutorial 2** (`phase-2-sample-data`)
6. **Track 2, `0008`–`0014`** — business rule vs. code error, structured result envelopes, reading
   tests as specifications, independent-rule-evaluation vs. first-match-wins, priority-ordered/
   greedy processing, date arithmetic &amp; signed quantities, and a guided-test-trace capstone —
   one linear block (mirroring how Track 1's `0000`–`0007` worked before Tutorial 1), consumed
   entirely before Tutorial 3 starts, not interleaved one-lesson-per-tutorial. → **Tutorial 3**
   (`phase-3-order-validation-core`)
7. → **Tutorial 4** (`phase-4-inventory-allocation-core`) — no separate `/teach` lesson in between;
   `0012`'s priority-ordered-processing content (item 6 above) already covers this tutorial's
   prerequisite concept.
8. → **Tutorial 5** (`phase-5-payment-aging-core`) — likewise, `0013`'s date-arithmetic content
   (item 6 above) already covers this tutorial's prerequisite concept.
9. **Track 3, `0015`–`0021`** — presentation vs. business logic, consuming contracts without
   changing them, Excel workbook/sheet/manifest vocabulary, serialization boundaries and safe cell
   values, explicit columns and empty reports, allow-lists and hidden-state-free safe defaults, and
   a guided report-trace capstone — one linear block (mirroring how Track 2's `0008`–`0014` worked
   before Tutorial 3), consumed entirely before Tutorial 6, not a single lesson. → **Tutorial 6**
   (`phase-6-excel-report-export`)
10. **L4.1** — HTTP/REST basics, request/response, status codes. Shipped as `0022`.
11. **L4.2** — Statelessness and trust boundaries. Shipped as `0023`. → **Tutorial 7**
    (`phase-10-fastapi-integration`)
12. **L5.1 + L5.2** — What a browser renders; React components/props/state (branch point into the frontend track).

**Important asymmetry, worth stating explicitly: generation order ≠ consumption order for Tutorial 8.** The settled `/tutorial` batch below generates `phase-12-postgres-backed-latest-session-dashboard` as Tutorial 8, right after Tutorial 7 — that's the right call for *having the file ready* and for `/tutorial`'s own continuity mechanic (each new tutorial references the prior ones in the series, so generating in one unbroken run is cleaner than generating out of order later). But Phase 12's central insight — the session-identity choice in `localStorage` *structurally forcing* the dashboard into a Client Component — only lands once L5.3 (the RSC/Client Component rule, Track 5) has actually been taught. So: **generate Tutorial 8 now, as part of this batch, but don't schedule the lesson that deeply teaches it until after Track 5 is solid** (i.e., after Tutorial 9 or 10 below). Reading Tutorial 8 early is fine for orientation; treat its Q1→Q8 coupling insight as a forward-reference to revisit, not something to fully absorb out of order.

Everything from Track 5 onward (Tutorials 9–13, generated after this batch) and Track 6/7/8 follow after item 12, once 1–12 feel solid — not before.

---

## Which `/tutorial` Outputs to Generate First, and Why

**Settled (2026-07-14).** Generate in **this exact order** — `/tutorial` explicitly references prior tutorials in the series for continuity, so the numbering has to build up incrementally:

1. `/tutorial docs/plan/phase-1-python-foundation` — foundation for tooling, tests, module boundaries, and the contract pattern everything else depends on. Nothing else in the repo makes sense without this.
2. `/tutorial docs/plan/phase-2-sample-data` — needed before Tutorial 3 can meaningfully show *real* sample data flowing through validation; also the natural place to teach "demo fixtures vs. test fixtures."
3. `/tutorial docs/plan/phase-3-order-validation-core` — first full business-logic case study; establishes the envelope pattern (`{summary, valid_orders, errors}`) reused in 4 and 5.
4. `/tutorial docs/plan/phase-4-inventory-allocation-core` — kept immediately after Phase 3, not deferred: this module's input is *literally Phase 3's output* (a real pipeline dependency), and teaches priority-ordered/stateful processing as a genuinely new mechanic, not just a restatement of Phase 3.
5. `/tutorial docs/plan/phase-5-payment-aging-core` — completes the business-core trilogy; the pattern-generalization test (does the envelope/contract discipline hold up a third time, in an independent business domain, without hand-holding).
6. `/tutorial docs/plan/phase-6-excel-report-export` — deliberately *after* 3–5, not before: report export is a consumer of every one of the 13 output-contract families, so it's easiest to understand once you've already built and tested all of them yourself. Reading it earlier would mean formatting fields you hadn't seen produced yet.
7. `/tutorial docs/plan/phase-10-fastapi-integration` — the statelessness/trust-boundary concept; the first real conceptual leap past the pure-Python core, pairs directly with `docs/grilling/phase-10-fastapi-integration/`.
8. `/tutorial docs/plan/phase-12-postgres-backed-latest-session-dashboard` — richest single phase (own grilling session, own architect session, own ADR). **Generation-order note**: generating this now keeps the tutorial series' continuity mechanic intact (each tutorial builds on the numbered ones before it, so generating in one unbroken run beats coming back later out of sequence). But *consuming* Tutorial 8 deeply should still wait until Track 5's RSC/Client Component rule (L5.3) is taught — Phase 12's central insight (session identity in `localStorage` structurally forcing a Client Component) depends on it. Generate now, fully teach later — see the "First 8–12 Lessons" section above for exactly where that revisit slots in.

This is the complete Python-business-core-through-persistence arc: 1→2→3→4→5→6→7→8, unbroken, matching the reasoning that Phases 3–5 form one pattern (produce → generalize → confirm) that shouldn't be interrupted, and Phase 6 is easier once all three are already familiar.

**Second wave** (after the above eight feel solid): `phase-7-ui-contract-wireframe-planning`, `phase-8-nextjs-frontend-foundation`, `phase-9-reusable-ui-components-static-pages`, `phase-10.2-portfolio-ui-polish`, `phase-11-deployment-baseline` — this is Track 5 (Frontend) and Track 7 (Deployment), and is also when Tutorial 8's Phase 12 insight should actually be revisited and fully taught (once L5.3 lands via Tutorial 9).

**Third wave / optional**: `phase-9.1-visual-alignment-fixes`, `mobile-nav-shell-responsiveness` (same concept family as Phase 9/10.2, lower marginal value). `python-first-sequence` and `context-reset` are better read directly (Track 8, capstone) than turned into dedicated tutorials — they're docs-only reorientations with little code to trace.

---

## Retrieval-Practice Plan

Spaced across the tracks, not bunched at the end. Each targets a different retrieval mode — recall, trace, rebuild, explain — deliberately rotating so no single mode gets stale.

| When | Mode | Prompt |
|---|---|---|
| After Tutorial 1 | **Recall** | List the 13 output-contract families from memory, no lookup. Then check against `src/contracts.py`. |
| After Tutorial 3 | **Trace** | Given a specific messy order row (pick one from `sample_data/sample_orders.xlsx`), predict which OV-rule(s) fire *before* reading `order_validation.py`, then verify. |
| After Tutorial 5 | **Rebuild** | Re-implement the aging-bucket assignment logic from the payment-aging spec alone (no peeking at `payment_aging.py`), then diff your version against the real one and explain every discrepancy. |
| After Tutorial 6 | **Explain** | In under 90 seconds, explain out loud (or write, timed) why `report_export.py` is forbidden from recomputing anything — as if to an interviewer who just asked "why not just have the report endpoint call the business function again itself, inline?" |
| After Tutorial 7 | **Explain** | Explain why `/api/orders/validate/report` re-accepts the source file instead of accepting a `run_id` — tie the answer explicitly to the trust-boundary concept from L4.2, not just "because the ADR says so." |
| After Tutorial 9 (L5.3) | **Recall** | State the RSC/Client Component rule in one sentence, then find three separate places in the repo where it was applied (or would have caused a bug if ignored). |
| After Tutorial 12 | **Trace** | Trace `X-Session-Id` end-to-end: browser `localStorage` → HTTP header → `backend/session.py` → `workflow_results` row → back out through `GET /api/dashboard` → rendered in `DashboardLiveSections.tsx`. Name every file it passes through, from memory, before checking. |
| Capstone (Track 8) | **Rebuild** | Draft a fictional ADR for a hypothetical "Phase 13" feature (pick a real, plausible one — e.g. "authenticated accounts") using the repo's own three-part ADR-worthiness test, without re-reading an existing ADR while drafting. Then compare structure (not content) against ADR 0006 or 0007. |

Learning records (`./learning-records/0001-*.md` onward) should be written whenever one of these produces a genuine surprise, a corrected misconception, or a clean pass — not for merely "covering" a lesson. See `LEARNING-RECORD-FORMAT.md`.

---

## Tool Usage: When to Use What

**Update (2026-07-14): found all three.** `socratic-teacher`, `practice-generator`, and `rebuild-scaffolder` aren't exact names, but real agents matching them exist at `~/.claude/agents/` — they belong to a separate G→C→R (Generate → Comprehend → Rebuild) teaching-agent system built for the `learn-to-code` repo, defined globally so they're available everywhere, but this environment's loader was silently excluding 8 of the 13 agent files in that folder. Diffing the ones that load against the ones that didn't showed a clean pattern: the working agents (`architect`, `challenger`, `curator`, `practitioner`, `saboteur`) all have minimal two-line frontmatter (`name` + `description` only); the excluded ones all carried extra `model:`/`color:` keys. Normalized the frontmatter of the three relevant files (`teacher.md`, `examiner.md`, `scaffolder.md`) to match. **A live re-test in this same session still failed** — the agent registry is evidently loaded once at session start and cached, so this fix needs a fresh Claude Code session to take effect. Re-verify with a trivial test call (or just try using one for real) once you start a new session.

The real mapping, once that fresh session picks up the fix:

- **`socratic-teacher` → `teacher` (initial instruction) + `examiner` (Socratic testing)**, used in sequence, not interchangeably. `teacher` has CONCEPT MODE (real-world analogy → ≤5-line example → checking question → gotcha → skill-gained statement) for a topic not yet seen, and COMPREHEND MODE (line-by-line active-prediction reading of a real file). `examiner` is the harder Socratic-questioning pass afterward — three tiers (What/Why/What-if), one question at a time, never reveals the answer on a first wrong attempt, plus a dedicated Trace Mode for following one data object through the whole codebase (a strong fit for the `X-Session-Id` trace in the Retrieval-Practice table above).
- **`practice-generator` → `practitioner`** — already confirmed working in this session (it's one of the 5 that load correctly). No fix needed.
- **`rebuild-scaffolder` → `scaffolder`** — produces a five-part rebuild spec (purpose statement, interface contract as type signatures only, behavioural expectations including an edge case, a thinking-sequence of questions, checkpoint stages) and writes it to `docs/scaffold-[name].md`, then refuses to give implementation code afterward, only Socratic redirection. This is a much better match for "rebuild from memory" than the `saboteur`-based workaround in the prior draft of this doc.
- **`/teach` (this skill)** — builds the course itself: prerequisite concept lessons, MISSION/ROADMAP maintenance, reference docs. Use it whenever the next thing needed is *a concept that isn't in the repo yet* (e.g. "what is HTTP") or a lesson tying a concept to real files.
- **`/tutorial <docs/plan/phase-folder>`** — turns an already-completed phase's plan/explanation/discussion docs into a code-grounded, numbered chapter, tracing every file the phase touched. Use it once a phase's prerequisite concepts are taught, per the settled order above.
- **`architect`** agent — Socratic with a devil's-advocate edge, but scoped specifically to code *you've* written during an "Extend" phase (once you're modifying this repo yourself, not just reading it). Use it once you reach the mission's "safely extend this project" goal, not during pure reading.
- **`challenger`** agent — ranked list of modifications to attempt, low-risk to high-impact, predict-then-observe. Good fit for a "what would you change" pass once a tutorial + its rebuild exercise are both done, before moving to the next track.

**Update (2026-07-14, later same day): the full 13-agent pipeline is now fixed**, not just the 3 originally requested — `builder`, `decomposer`, `guardian`, `reviewer`, and `tester` got the same frontmatter normalization. Full detail and the complete pipeline order (`curator` → `decomposer` → `builder` → `guardian` → `tester` → `teacher` → `examiner` → `scaffolder` → `reviewer` → `saboteur`/`challenger`/`architect`, with `practitioner` slotting in after `teacher`+`examiner`) is in `NOTES.md`. For *this* mission (mastering an already-built repo, not building a new one from a spec), the relevant subset stays `teacher`/`examiner`/`scaffolder`/`practitioner`/`architect`/`challenger` as described above — `builder`/`decomposer`/`guardian`/`tester`/`reviewer` are oriented around the Generate-phase workflow (writing new code from a spec, e.g. the mission's "safely extend this project" goal), not around comprehending existing code.

**One rough edge to expect**: `teacher`, `examiner`, and `scaffolder` were written against the `learn-to-code` repo's own conventions — they instruct themselves to read that repo's `CLAUDE.md` for a "current phase," `docs/build-log.md` for recent activity, and `scaffolder` writes to `docs/scaffold-[name].md`. None of those exist in this repo (`sales-ops`) in that form. They'll likely just not find those files and proceed anyway, but if one seems confused about "phase" or "recent work," that's why — redirect it explicitly to `ROADMAP.md`/`MISSION.md`/`NOTES.md` here instead.

Rough sequence per case-study phase: **`/teach` (prerequisite lesson) → `/tutorial` (code-grounded chapter) → `teacher` in COMPREHEND MODE (active prediction over the real file) → `examiner` (Socratic tiered testing, or Trace Mode for a data-flow prompt) → `practitioner` (calibrated practice problem) → `scaffolder` (rebuild spec, then rebuild cold) →** only once you're extending the repo yourself, **`architect`** or **`challenger`**.
