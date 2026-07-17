# Teaching Notes

- **Zero assumed prior knowledge** is a hard constraint, not a soft preference: Python, pandas, pytest, uv, FastAPI, HTTP/REST, React, Next.js/App Router, TypeScript, SQL, Postgres, deployment/CORS/env vars, and architecture vocabulary (ADR, statelessness, contracts) are all treated as unknown until explicitly taught. Every lesson must teach the prerequisite concept before (or alongside) tying it to a real file — never assume, never skip.
- **Concept-first, phases as case studies** — the 12 build phases are *examples*, not the syllabus. `ROADMAP.md`'s Concept Track order intentionally diverges from phase-number order (e.g. Track 3 "Presentation" / Phase 6 is taught before Track 4 "APIs" / Phase 10, and Track 5 "Frontend" spans phases 7–10.2 as one track even though those phase numbers interleave with backend phases).
- Three co-equal mission drivers, none should be dropped from lesson design: interview readiness, reusable engineering patterns (portable beyond this repo), and safe independent extension of this specific codebase. Every lesson should ideally gesture at all three, not just "explain what the code does."
- **`socratic-teacher`/`practice-generator`/`rebuild-scaffolder` are real** — they're the user's `learn-to-code` repo's G→C→R agent system, defined globally at `~/.claude/agents/{teacher,examiner,scaffolder,practitioner,...}.md`. `practitioner` (= practice-generator) already loaded fine. `teacher`+`examiner` (= socratic-teacher, used in sequence) and `scaffolder` (= rebuild-scaffolder) were being silently excluded by this environment's agent loader — root cause traced to extra `model:`/`color:` frontmatter keys absent from the 5 agents that *do* load. Fixed by normalizing their frontmatter to the minimal working pattern (2026-07-14). **Confirmed via live re-test that this session's agent registry is cached at startup and did not pick up the fix immediately** — needs a fresh Claude Code session. First thing next session: re-verify one of `teacher`/`examiner`/`scaffolder` actually routes now, then update this note.
  - These three agents reference `learn-to-code`-specific conventions (its `CLAUDE.md` phase tracking, `docs/build-log.md`, `docs/scaffold-*.md`) that don't exist in `sales-ops` — expect minor friction, redirect them to this workspace's `ROADMAP.md`/`MISSION.md`/`NOTES.md` instead if they seem to be looking for the wrong files.
  - **Update (same day, later turn): confirmed the fix actually works.** `teacher`/`examiner`/`scaffolder` showed up as available in the very next turn's system reminder — proof the "needs a fresh session" theory was correct, not just a guess.
  - **Full G→C→R pipeline now fixed, at the user's request** ("yes give me the full pipeline"): applied the identical frontmatter normalization to the remaining 5 files — `builder`, `decomposer`, `guardian`, `reviewer`, `tester`. All 13 agents in `~/.claude/agents/` now share the minimal working frontmatter shape. These 5 will need the same "next fresh session" wait as the first 3 did before they'll actually appear as invocable agent types.
  - **The complete pipeline, once all 13 are live**: `curator` (topic entry, turns docs into a lesson plan) → `decomposer` (Socratic problem decomposition before any code) → `builder` (Generate phase — generates code from a spec, enforces a 5-criterion contract-first gate, annotates CORE INVARIANT/DRY RUN/COMPLEXITY/DECISION/SIDE EFFECT comments, ends with a mandatory step-away break) → `guardian` (audits Builder output against 7 NASA/Holzmann rules, Socratically, before Comprehend) → `tester` (PRE-GENERATE/DESIGN/REVIEW modes — test-design discipline, anchored to CORE INVARIANT) → `teacher` (CONCEPT MODE and COMPREHEND MODE/active-prediction) → `examiner` (three-tier Socratic testing + Trace Mode) → `scaffolder` (rebuild spec) → learner rebuilds cold → `reviewer` (Step-0 self-assessment first, then a conceptual diff with BLIND SPOT and CLUSTERING analysis) → `saboteur`/`challenger`/`architect` (Extend phase) → back to `decomposer` for the next feature. `practitioner` slots in after `teacher`+`examiner` confirm understanding, before touching reference code, per its own description.
  - This is the `learn-to-code` repo's actual pipeline, not something invented for `sales-ops` — these agents all read `CLAUDE.md`/`docs/build-log.md`/write to `docs/scaffold-*.md` by default (that repo's conventions). Using them here will hit the same friction noted above; redirect them to this workspace's own files when that happens.
- 2026-07-14: this session (via `/teach`, then a refined follow-up request) produced `MISSION.md`, `ROADMAP.md`, and `RESOURCES.md`. Explicitly no lessons yet — "do not teach yet" was the governing instruction both times. First real lesson session should start at Lesson 1 in `ROADMAP.md`'s "First 8–12 Lessons" list (L0.1), unless the user redirects.
- 2026-07-14 (later, same day): first real lesson batch produced — all of Track 1, as 7 lessons (`docs/teach/lessons/0001`–`0007`) instead of the coarser L0.1/L1.1/L1.2/L1.3 sketch in `ROADMAP.md`. This is a deliberate refinement, not a contradiction: the user asked explicitly for a finer split (repo/tutorial navigation as its own lesson; Python basics, uv/pytest, and contracts/TypedDict each split out; Excel/DataFrame and demo-vs-test-data each split out; plus a new 7th "guided trace" capstone lesson not previously in the roadmap). `ROADMAP.md`'s Track 1 section has been annotated to point at the real lesson files without rewriting its own prose — treat the roadmap as the original syllabus sketch and the lesson files as what was actually shipped.
  - Built the workspace's first shared components: `docs/teach/assets/style.css` (Tufte-ish serif/mono, light+dark via `prefers-color-scheme`, print-friendly) and `docs/teach/assets/quiz.js` (self-contained multiple-choice widget, immediate click-to-reveal feedback, no dependencies). Every future lesson should reuse these, not reinvent styling or quiz mechanics.
  - Also produced the workspace's first 4 reference docs, in `docs/teach/reference/`: a Python reading cheat sheet, a pytest reading cheat sheet, a DataFrame/table mental model, and a contracts/TypedDict glossary. The glossary explicitly notes it's a *pre-study* glossary, not yet the evidence-gated canonical `GLOSSARY.md` the teach skill's format describes — terms should only graduate to that stricter canonical glossary once the user actually demonstrates understanding of them in conversation, per `LEARNING-RECORD-FORMAT.md`'s rules. Don't conflate the two.
  - No learning records written yet — correctly so. No interaction/evidence of actual understanding has happened; these lessons were authored, not yet completed by the user. The first learning record should come from the user's real answers/exercises, not from lesson authorship itself.
  - All 7 lessons deep-link into the real Tutorials 01/02 (`docs/tutorials/01-python-foundation/`, `docs/tutorials/02-sample-data/`) and real repo files (`src/contracts.py`, `src/excel_io.py`, `src/sample_data.py`, `tests/test_excel_io.py`, `tests/test_sample_data.py`, `tests/contract_fixtures.py`) rather than re-explaining their content — per the explicit instruction to build a *companion course*, not a rewrite. Lesson 7's guided trace uses two real sample-data rows (`SO-2026-030` unknown-SKU, `SO-2026-031` inactive-SKU) as its worked example and its self-directed exercise, respectively.
- `/tutorial` generation order is **settled** (2026-07-14, user agreed with the flagged disagreement): 1 phase-1, 2 phase-2, 3 phase-3, 4 phase-4, 5 phase-5, 6 phase-6, 7 phase-10, 8 phase-12 — Phases 3–5 kept as one unbroken arc (produce → generalize → confirm), Phase 6 deliberately after all three (easier once every output-contract family is already familiar). One asymmetry to remember: Tutorial 8 (Phase 12) is *generated* in this batch for series continuity, but shouldn't be *fully taught* until after Track 5's RSC/Client Component lesson (L5.3) lands — its central insight depends on that concept.
- The repo already has an unusually rich internal doc trail (ADRs, `docs/grilling/`, `docs/plan/*/{plan,explanation,ai-discussion-topics}.md`, `docs/architect/`, `CONTEXT.md`) — treat these as primary knowledge sources for lesson-writing, cite them directly, don't re-derive explanations from the code alone when a doc already explains the "why."
- Known repo hygiene issue (not this workspace's concern, but noted so it isn't mistaken for intentional structure): the working tree has a batch of stray `" 2"`-suffixed duplicate files (e.g. `backend/db 2.py`, `docs/adr/0007-... 2.md`) — editor/Finder-style duplicates, untracked. Flagged to the user separately in this same session, outside the teaching workspace.
- 2026-07-15: a fresh session (no memory of the 2026-07-14 work above — this workspace wasn't in `MEMORY.md` and the conversation had no prior context on it) received `/teach me the minimum Python/project basics needed before Tutorial 1: what a repository is, what a Python module is, what pytest does, what uv is doing, and how to read a test file` — verbatim the L1.1 scope already shipped as `0002`/`0003`, with L0.1 (`0001`) also already covering "what a repository is." Before building anything, checked `docs/teach/` on disk (it wasn't empty), read `0001`–`0003` in full, confirmed near-total overlap, and surfaced this to the user instead of silently duplicating.
  - User's call: build a genuinely lower prequel instead — **`0000-files-folders-and-the-terminal.html`**, covering what a file/folder/directory/path/file-extension/terminal-command *is*, which `0001` uses constantly but never defines. Cited Software Carpentry's "The Unix Shell" (`01-intro.html`, `02-filedir.html`) as primary source — verified via live web search, not parametric recall, per this skill's "never trust your parametric knowledge" rule.
  - Wired two-way navigation: `0001`'s bottom nav now links back to `0000` (was `<span>← You are here</span>`, a dead end, since `0001` used to be first). No other existing lesson file touched — `0002`–`0007`'s internal "Lesson N of 7" counters were deliberately left alone rather than renumbered, since `0000` sits *before* Track 1's own count, not inside it.
  - Updated `ROADMAP.md` (Track 0 section + "First 8–12 Lessons" list) and `RESOURCES.md` (new "Prequel" section) to reflect the addition. Also worth remembering for next session: **this workspace itself isn't yet referenced anywhere in the cross-session `MEMORY.md` system** — a session starting fresh has no way to know `docs/teach/` exists short of noticing it in `git status`/`ls`, which is exactly what happened here. Worth a `[[teach-workspace-location]]`-style memory pointer at some point, so future sessions don't risk rebuilding this from scratch.
  - **Update (same day, later turn): the memory pointer was actually added** — `teach_workspace_location.md`, referenced from the cross-session `MEMORY.md` index. A session starting fresh from this point forward should find `docs/teach/` immediately instead of rediscovering it by accident.
- 2026-07-15 (later, new session): built all of Track 2 — 7 lessons (`0008`–`0014`) plus 4 new reference docs — from a fully-specified task file the user had written themselves at `docs/teach/lessons-ideas/track2-ideas.md` (exact lesson sequence, required test-file citations, and failure modes to name were all user-authored, not agent-derived). Followed it closely rather than re-deriving structure from scratch; the memory pointer above meant this session found the workspace immediately instead of re-discovering it.
  - One deliberate correction from the task file's literal wording, made because the code doesn't support the literal reading: the task file described lesson `0011` as contrasting "collecting every issue on one row" against "first-match-wins classification," citing *both* Phase 3's OV-001 *and* Phase 5's PA-006/PA-007 as the contrast pair. But PA-006/PA-007 are actually evaluated independently (a row can carry both at once, per `test_row_with_missing_due_date_and_invalid_amount_produces_two_data_issues`) — they're a second example of the *same* "collect every issue" shape as OV-001, not a first-match-wins example. Built `0011` with the factually correct contrast instead: OV-001 + PA-006/PA-007 both illustrating "collect every issue," contrasted against Phase 5's real first-match-wins case, `_follow_up_priority()`'s priority chain — which is also the exact contrast Tutorial 05 Part 6 already documents in its own CS-concept callout, so this reading is grounded in code the tutorials already treat as canonical, not a new interpretation invented for this lesson.
  - Navigation design decision: `0007` (end of Track 1) still points forward to Tutorial 01, unchanged — it does **not** chain into `0008`. The real intended sequence, per `ROADMAP.md`'s own Track dependency table, is Track 1 → Tutorial 1 → Tutorial 2 → **Track 2** → Tutorial 3 → Tutorial 4 → Tutorial 5, so Track 2 isn't Track 1's next click, it's the thing a learner reaches after finishing Tutorial 2. `0008` therefore starts its own chain with `← You are here` (the same pattern `0001` used before `0000` existed), not a back-link into Track 1.
  - `0014` (capstone) deliberately does **not** interleave one lesson before each of Tutorials 3/4/5 — all of `0008`–`0014` chains linearly, and `0014`'s own "Next" points straight at Tutorial 03, mirroring `0007`'s exact role for Track 1. `ROADMAP.md`'s "First 8–12 Lessons" list was updated to reflect this (Track 2 is one block before Tutorial 3, not three separate insertions before Tutorials 3/4/5 individually) — the original L2.3/L2.4 syllabus sketch's "before Phase 4 specifically" / "before Phase 5 specifically" phrasing described which *concept* each lesson warms up, not a literal stop-and-read-the-tutorial-now instruction.
  - Test-quality note worth remembering: while writing `0013` and `boundary-case-checklist.html`, confirmed Watch's `-7` boundary (`-7 <= days_overdue <= 0`) has **no dedicated test** in `tests/test_payment_aging.py` today — only `-5` (interior) and `0` (near edge) are directly tested. Left this as a visible, honestly-flagged gap in both the lesson's exercise and the reference doc's table, rather than glossing over it — it's a real, current gap in the test suite, not a teaching simplification.
  - Confirmed via live search (not memory) that `https://docs.python.org/3/library/datetime.html` and `https://docs.pytest.org/en/stable/how-to/fixtures.html` are the correct current URLs before citing them in `0013`/`0010` and `RESOURCES.md`.
  - No learning records written — correctly so, per this file's own standing rule: lesson authorship isn't evidence of learning, only the user's own completed exercises/answers are.
- 2026-07-15 (later session): built all of Track 3 — 7 lessons (`0015`–`0021`) plus 4 new reference
  docs — from a fully-specified task file the user had written themselves at
  `docs/teach/lessons-ideas/track-3-ideas.md` (exact lesson sequence, required source files, and
  the suggested reference-doc list were all user-authored, not agent-derived), the same working
  pattern as Track 2's `track2-ideas.md` session.
  - **Mechanism note, worth remembering for future sessions**: `~/.claude/skills/teach/SKILL.md`
    carries `disable-model-invocation: true` in its frontmatter, so `/teach` never appears in this
    agent's available-skills list and cannot be invoked as a tool call — it only activates when the
    *user* types `/teach` themselves. The task file's own first line said "Use /teach to build
    Track 3..." but the user's actual request didn't type the slash command. Resolved by reading
    `SKILL.md` directly (already on disk) and following its workspace conventions by hand — same
    lessons/reference-doc/asset structure, same philosophy — rather than attempting to call a
    disabled skill. Worth surfacing to the user if a future task file assumes `/teach` is
    self-invoking; it isn't, by design.
  - Content mapping, since the original syllabus only had one L3.1 entry for this whole track: `0015`
    is the direct L3.1 shipment (presentation vs. business logic, the recalculation-leak failure
    mode); `0016`–`0021` are genuinely new material the original one-lesson sketch never separately
    named — producer/consumer contract reading, Excel vocabulary, serialization boundaries,
    explicit-column headers, allow-lists/hidden-state, and the capstone trace. Same "finer split
    than the sketch" pattern Tracks 1 and 2 both used, annotated into `ROADMAP.md` without rewriting
    its own original prose, per that file's own established convention.
  - `0021`'s capstone traces a single real fixture (`PAYMENT_AGING_ROW_FIXTURE` +
    `DRAFT_MESSAGE_ROW_FIXTURE` from `tests/contract_fixtures.py`) through the whole
    `export_payment_aging_report` pipeline as five predict-then-reveal steps, closer in shape to
    Tutorial 06's own "Full data flow" trace than to `0014`'s three-separate-tests format — a
    deliberate choice, since Track 3's source material (one module, one pipeline) is genuinely
    different in shape from Track 2's (three independent business modules).
  - Navigation: `0015` starts its own chain with `← You are here`, same pattern `0008` used before
    it — Track 3 is not `0014`'s next click. Per `ROADMAP.md`'s own Track dependency table, the real
    sequence is Track 2 → Tutorial 3 → Tutorial 4 → Tutorial 5 → **Track 3** → Tutorial 6, so `0014`
    was deliberately left untouched rather than retrofitted to point at `0015` — matching the same
    "don't rewire earlier chapters" precedent already set when `0007` was left pointing at Tutorial
    01 after Track 2 shipped. `0021`'s own "Next" points straight at Tutorial 06, mirroring `0007`'s
    and `0014`'s exact capstone role.
  - URL verification: `https://docs.python.org/3/library/io.html#io.BytesIO` returned a live 200 and
    was fetched and read directly. `https://openpyxl.readthedocs.io/en/stable/` (already cited in
    `RESOURCES.md` from an earlier session) returned HTTP 429 (rate-limited) on every fetch attempt
    in this session, including with a browser User-Agent — treated as "server is up, just
    rate-limiting automated requests," not evidence of a dead link, and left as-is rather than
    replaced with an unverified deep-linked sub-page. Noted explicitly in `RESOURCES.md` so a future
    session doesn't mistake the 429 for a broken citation.
  - No learning records written — correctly so, per this file's own standing rule.
- 2026-07-16 (later session): shipped Track 4's two prerequisite lessons (`0022`-`0023`, HTTP
  request/response/multipart uploads and statelessness/trust boundaries) as a required first step
  of a `/tutorial` task file for Tutorial 07
  (`docs/tutorials/tutoiral-ideas/lesson-7-fastapi-integration-ideas.md`), which explicitly said
  "if those lessons have not been generated yet, create them before Tutorial 07." Checked
  `ROADMAP.md` first and confirmed Track 4 was still just the two-item syllabus sketch, not yet
  shipped.
  - **Numbering note**: the next available public lesson number was `0022`, immediately after Track
    3's `0021` capstone. Confirmed by listing `docs/teach/lessons/` before naming the new files,
    not by assuming `0021` was still the latest.
  - **Scope note, a deliberate departure from the Track 1-3 pattern**: every earlier track expanded
    its syllabus sketch into a much finer lesson split (Track 1's 4-item sketch became 7 lessons,
    Track 2's 4-item sketch became 7, Track 3's single L3.1 became 7). Track 4 shipped as close to
    literally two lessons for two syllabus items, per the task file's own explicit instruction to
    keep them "concept first and code-light" — the code depth is deliberately reserved for
    Tutorial 07 itself, not front-loaded into the prerequisite lessons. No new reference docs were
    added for the same reason: nothing in these two lessons is dense enough yet to need a
    compressed lookup page, and neither term set recurs elsewhere in the workspace yet.
  - `0023`'s primary source is this repo's own `docs/grilling/phase-10-fastapi-integration/explanation.md`
    and `docs/adr/0006`, not an external primer — the same "no clean beginner external resource
    exists, use the repo's own worked example" pattern `0012`/`0015`/`0019`/`0020` already
    established, applied here because generic "what does stateless mean" explainers online tend to
    either assume REST/backend familiarity already or oversimplify past the point of being useful
    before Tutorial 07's real ADR 0006 case study.
  - URL verification: `RESOURCES.md`'s existing Track 4 entries (from an earlier, unlogged session)
    were checked with `curl -L` before reuse — the two MDN URLs cited (`/Web/HTTP/Overview`,
    `/Web/HTTP/Status`) turned out to 301-redirect to MDN's reorganized `/Guides/` and `/Reference/`
    paths respectively; updated to the canonical redirect targets rather than left pointing at the
    old paths. `fastapi.tiangolo.com/tutorial/` returned a direct 200.
  - No learning records written — correctly so, per this file's standing rule.
- 2026-07-16 (later session): built Track 4's optional reinforcement sequence — seven lessons
  (`0024`–`0030`) plus five new reference docs — from a fully-specified task file the user had
  written at `docs/teach/lessons-ideas/track-4-ideas.md`, the same "follow the user's own spec
  closely" working pattern as every earlier task-file session (Track 2, Track 3, and the
  `0022`/`0023` prerequisite lessons themselves). Confirmed via `ls docs/teach/lessons/` and
  `ls docs/teach/reference/`
  before naming files that `0024`–`0030` and all five suggested reference-doc filenames were free —
  not assumed from the task file's own suggested names.
  - **Scope was confirmed with the user first, via `AskUserQuestion`,** rather than assumed —
    the task file itself frames the whole sequence as conditional ("if the goal is only to satisfy
    the roadmap, Track 4 is already ready for Tutorial 07"), and `0022`/`0023` alone already fully
    satisfy the roadmap's Track 4 requirement. The user chose to build the full seven-lesson +
    five-reference-doc sequence anyway, for retention *after* completing Tutorial 07 — this is
    genuinely optional reinforcement, not a gap that was blocking anything.
  - **Navigation precedent, also confirmed rather than assumed:** `0024` starts its own chain with
    `← You are here`, *not* rewiring `0023`'s existing "Next: Tutorial 07 →" bottom-nav link —
    matching the exact "don't rewire earlier chapters" precedent `0008` and `0015` already set.
    `0023` was left completely untouched. `0030` (capstone) ends with "Track complete," no forward
    link — there's no Tutorial N waiting on the other side of this particular block, unlike Tracks
    1-3's capstones.
  - Content mapping to the task file's suggested topics-beyond-the-roadmap list: the multipart
    `Content-Type` boundary trap folded into `0025` (it's the same FormData/UploadFile chain, one
    layer below the field-name question); HTTP-contract-testing-vs-business-result-testing folded
    into `0026` (the exact distinction `tests/test_backend_errors.py` demonstrates); headers-as-API-contract
    became `0027`'s central framing rather than a side note; the browser-vs-server-state bridge
    became `0029`'s entire subject; the 90-second "why not generate-once-fetch-by-ID" interview drill
    and the design-only fourth-workflow rehearsal were placed as `0030`'s and `0028`'s exercises
    respectively, rather than as separate lessons — each fit naturally as the capping exercise for
    the lesson whose concept it directly exercises.
  - Every lesson's "Primary source"/"What you're rehearsing" box points at specific Tutorial 07
    Part numbers and real file/line citations gathered by reading Tutorial 07 in full (all 9 Parts
    plus both data-flow traces) before writing anything — per this workspace's standing rule to
    cite the repo's own doc trail directly rather than re-derive explanations from the code alone.
  - No learning records written — correctly so, per this file's standing rule: this is lesson
    authorship, not evidence of the user having completed the exercises or answered the retrieval
    checks yet.
- 2026-07-17 (later session): shipped Track 5's four prerequisite lessons (`0031`–`0034`) from a
  fully-specified task file at
  `docs/tutorials/tutoiral-ideas/track-5-ui-components-nextjs-ideas.md`, which also specifies the
  four core Track 5 `/tutorial` outputs (Tutorials 08–11) to generate afterward via the separate
  `tutorial` skill. Confirmed via `ls docs/teach/lessons/` that `0031` was genuinely the next free
  number (the task file's own claim that "the current lesson chain ends at `0030`" checked out
  against the real directory) before naming any files.
  - **Scope/pacing confirmed with the user first, via `AskUserQuestion`**, given the batch's total
    size (4 lessons + 4 full code-grounded tutorials, each historically 1,000–1,600+ lines): user
    chose one continuous run rather than pausing between lessons and tutorials, or between each
    individual tutorial.
  - Content shipped close to literally one lesson per syllabus item (L5.1→`0031`, L5.2→`0032`,
    L5.3→`0033`, L5.4→`0034`), the same close-to-literal pattern Track 4's `0022`/`0023` used —
    not the finer 7-lesson expansion Tracks 1–3 used — because the task file's own brief scoped
    each lesson tightly (a "tiny exercise," not a deep dive) and explicitly reserves code depth
    for the Tutorials themselves.
  - `0033` (Server/Client Components) is the load-bearing lesson of this set — flagged in
    `ROADMAP.md` as required before Tutorial 09 and revisited in Tutorials 10 and 15 (Track 5's
    Phase 12/Postgres forward-reference already exists in `ROADMAP.md`'s Track 6 entry). Grounded
    directly in this repo's installed copy of the Next.js docs
    (`node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`),
    read in full before writing, per this workspace's standing "read the real doc, don't rely on
    parametric recall" rule — same posture the task file's own shared instructions require for
    the Tutorials.
  - All external URLs (two MDN pages, two react.dev pages, one react.dev RSC reference, the public
    Next.js Server/Client Components page, two Tailwind v3 docs pages) were verified live with
    `curl -L` before citing — all returned clean `200`s, no redirects to chase this time (contrast
    the Track 4 session's MDN redirects, noted above).
  - Navigation: `0031` starts its own chain with `← You are here`, matching every earlier track's
    first-lesson precedent. `0034`'s forward link points at the *future* path
    `docs/tutorials/08-ui-contract-wireframe-planning/README.md` (corrected once, mid-session,
    away from an initial accidental link to the task-file itself) — the file didn't exist yet at
    the moment `0034` was written, but does by the time this same session finishes the batch.
  - No learning records written — correctly so, per this file's standing rule.
- 2026-07-17 (same session, continued): generated Track 5's four required `/tutorial` outputs —
  `docs/tutorials/08-ui-contract-wireframe-planning/` through `11-portfolio-ui-polish/` — via the
  separate `tutorial` skill, invoked once per phase in the order the task file specified
  (phase-7 → phase-8 → phase-9 → phase-10.2), each call passed the task file's full per-tutorial
  brief (teaching goal, exact read list, recommended Parts, question-to-Part mapping, trace/
  challenge specs) as args, not just the plan-folder path. User chose "all in one continuous run"
  when asked about pacing beforehand, given the batch's size (4 lessons + 4 tutorials, each
  historically 1,000+ lines).
  - **A critical discovery made early and handled throughout**: this session's own working tree
    has real, uncommitted, in-progress work — a landing-page/route-group restructuring
    (`app/(public)/`, `app/(workspace)/`, `components/landing/`, `lib/content/`) that isn't part of
    any committed phase. Caught by comparing `git status --short` against what `app/page.tsx`
    should contain per `plan.md`, and finding `app/page.tsx` literally deleted in the working tree.
    Every tutorial in this batch was written citing `git show HEAD:<path>` (the last *committed*
    state) for every file touched by that restructuring, never the uncommitted working-tree
    version — each tutorial's own opening caveat names this explicitly so a reader who opens the
    real files and sees a different `app/` layout isn't confused. This is the correct extension of
    the shared brief's own "cite current, stable, committed code, not deleted stubs" rule to a case
    the brief didn't explicitly anticipate: uncommitted, *unstable* current-tree state is not
    "current stable" either.
  - Beyond that one restructuring, several individual files had genuinely evolved past their
    origin-phase description in `explanation.md`/`plan.md`, independent of the uncommitted work
    above — each handled the same way (cite current code, name the later commit/phase explicitly,
    correct the stale prose rather than silently reproducing it): `scripts/generate_mock_data.py`
    now reads real `sample_data/*.xlsx` through the full business-rule pipeline instead of
    `tests/contract_fixtures.py` (changed in commit `745ac10`, after Phase 8); the
    `REPORT_MANIFEST_FIXTURES` `report_id` bug Tutorial 08 Part 7 covers as "found but deliberately
    left unfixed" in Phase 7 was genuinely fixed in a later, separate commit (`aca6762`), verified
    via `git log -S` before writing that Part; `AppShell.tsx`/`TopHeader.tsx` are now full Client
    Components with a mobile drawer (the `mobile-nav-shell-responsiveness` work), not Phase 9's
    original plain-Server-Component shell; `DataTable` now explicitly defers filtering to callers
    (a Phase 9.1 revision of Phase 9's original "sort only" scope); `UploadPanel` now hands its
    selected `File` up via `onFileChange` (a Phase 10 addition, per the component's own docstring);
    and Phase 12 moved the dashboard's live KPI/chart/table sections out of `app/dashboard/page.tsx`
    into a new Client Component, `components/dashboard/DashboardLiveSections.tsx` — Tutorial 11's
    full data-flow trace and every dashboard-visual code excerpt cite that current file, not
    Phase 10.2's original (now-relocated) code.
  - Every one of these forward-references and corrections was verified against real evidence before
    being stated as fact — `git log --oneline`/`git log -S`/`git show HEAD:<path>`/direct file
    reads — never inferred from the plan/explanation docs' prose alone, consistent with this
    workspace's standing "verify, don't trust stale docs" rule (already established for the
    Track 4 session's MDN redirects and the Track 2 session's PA-006/PA-007 correction).
  - Question-to-Part mapping preserved all questions from every phase's `ai-discussion-topics.md`
    per the task file's explicit instructions: Tutorial 8 (15/15), Tutorial 9 (24/24), Tutorial 10
    (17/17), Tutorial 11 (15/15) — 71 questions total, zero dropped, none answered in a separate
    quiz section (every one is a `**Checkpoint:**` inside the Part it maps to, per the `tutorial`
    skill's own quality rules).
  - No learning records written — correctly so, per this file's standing rule: this is lesson/
    tutorial authorship, not evidence of the user having worked through any of it yet.
