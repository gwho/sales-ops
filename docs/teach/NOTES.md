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
- 2026-07-18: started Track 5's optional reinforcement sequence, from a fully-specified task file
  at `docs/teach/lessons-ideas/track-5-reinforcement-ideas.md` (same pattern as the Track 2/3/4
  `*-ideas.md` sessions). **Scope/pacing confirmed with the user first, via `AskUserQuestion`**,
  given the task file specs nine lessons (`0035`–`0043`) plus seven reference docs: user chose to
  generate only the first lesson this round rather than the full batch or a 4-lesson sub-batch, to
  check tone/depth/format fit before continuing. Shipped `0035-tsx-and-typed-component-props.html`
  plus its companion reference doc, `typed-react-component-contract.html`.
  - Confirmed `0035` was genuinely the next free number (`ls docs/teach/lessons/` stops at `0034`)
    before naming any files, same check every prior track session has done first.
  - Content follows the task file's brief closely: TSX as JSX-plus-typechecking, named vs. inline
    prop types (`MetricCardProps`/`UploadPanelProps` vs. both route-group layouts' inline
    `{ children: ReactNode }`), optional props and destructured defaults, `ReactNode`, literal
    unions (`Tone`), and callback prop signatures — deliberately tied back to Lesson 33's
    Server/Client serialization-boundary rule (a function prop is fine between two Client
    Components; `UploadPanel` and every workflow page that renders it both already start with
    `"use client"`). Generics were kept to a one-paragraph forward reference to the not-yet-written
    Lesson 38, per the task file's explicit instruction not to teach them yet.
  - Every code excerpt was pulled from the real current files with line numbers verified by direct
    `Read` immediately before writing (`MetricCard.tsx`, `UploadPanel.tsx`, `StatusBadge.tsx`, both
    route-group `layout.tsx` files, `order-validation/page.tsx`, `DashboardLiveSections.tsx`).
    All excerpts are fully verbatim, with no `...`-trimmed lines inside any `<pre><code>` block —
    an initial draft trimmed a couple of blocks for brevity, caught in review (see below) and
    corrected to either the complete real excerpt or a shorter real call site that needed no
    trimming at all.
  - All three external URLs (`react.dev/learn/typescript`, and the TypeScript Handbook's "Object
    Types" and "Everyday Types" pages) were fetched and confirmed live/on-topic before citing,
    per this workspace's standing verify-before-cite rule.
  - Navigation: since `0036`–`0043` don't exist yet, `0035`'s forward nav (top and bottom) is a
    plain, non-linking note rather than a link that would 404 — the first deviation from every
    prior track's practice of shipping a full chain with real forward links in one session, because
    this is deliberately a single-lesson first pass. `ROADMAP.md` flags that `0035`'s forward nav
    needs rewiring to a real link once `0036` ships. `0034` itself was left untouched, matching the
    Track 4 precedent of a reinforcement chain starting its own "You are here" entry point.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught and fixed seven issues** before treating `0035` as
    done: (1) the sample-data paragraph conflated the workflow page's own "Run sample data" feature
    with the dashboard's unrelated Phase-12 automatic sample *fallback* — reworded to distinguish
    them; (2) the exercise told the learner to revert with `git checkout --`, which would silently
    discard any other unstaged changes in that file — replaced with editor Undo as the default,
    plus a `git diff` check-first warning if git is used instead; (3) three code blocks used `...`
    to trim real content, violating this workspace's verbatim-excerpt rule — fixed by quoting the
    complete function/comment in two cases and swapping to a shorter, already-complete real call
    site (`UploadPanel`'s Product Master File usage, lines 314–320) in the third; (4) the generics
    forward-reference misnamed `DataTable`'s second prop as `rows` — it's `data`, confirmed against
    `DataTable.tsx` line 33; (5) all three retrieval-quiz option sets had a visibly longer, more
    precise correct answer — rebalanced to near-equal length per option so length itself isn't a
    tell; (6) added an explicit "Why this matters" box naming all three mission drivers, which the
    lesson previously only gestured at implicitly; (7) the companion reference doc's inline-vs-named
    table implied a mechanical field-count threshold ("one or two fields" vs. "several") that
    contradicted the lesson's own "judgment call" framing — reworded to match.
- 2026-07-19: shipped `0036-render-snapshots-events-and-derived-state.html`, the second lesson in
  the same Track 5 optional reinforcement sequence, continuing the "one lesson at a time" pacing
  the user chose for `0035`.
  - Content follows the task file's brief: state as a render-time snapshot (not a live variable),
    immutable whole-object replacement, event handlers as user-caused work contrasted with the
    external-synchronization case an Effect exists for, and derived `const`s computed fresh every
    render instead of copied into state. Deliberately kept to the density the reviewing pass on
    `0035` recommended for this lesson: one render-timeline walkthrough (`runValidation`), one
    derived-state contrast (`canSubmit`/`currentStep`/`errorFiltersActive`/`orderFiltersActive`),
    three length-balanced retrieval checks, one predict-then-verify exercise — no separate section
    for "component purity" or "immutable updates," folded into the render-timeline section instead
    of given their own subsections, to avoid exceeding `0035`'s scope.
  - Used the same source page as `0035` (`order-validation/page.tsx`) rather than switching files,
    for continuity — every excerpt (`runValidation`, the Run Validation button, `canSubmit`/
    `currentStep`, the two `FiltersActive` consts) is fully verbatim with line numbers verified by
    direct `Read` immediately before writing. No `...`-trimmed excerpts.
  - Deliberately did *not* teach `useMemo` even though `filteredErrors`/`filteredValidOrders` in
    the same file use it — that's reserved for Lesson 38 per the task file's explicit sequencing
    (memoization is a "bigger idea," not this lesson's derived-value point). The derived-value
    examples chosen (`canSubmit`, `currentStep`, the two `FiltersActive` consts) are plain `const`s
    with no memoization involved, so the lesson never has to gesture at `useMemo` to explain them.
  - The exercise avoids React 18's automatic-batching-across-`await`-boundaries behavior entirely —
    an earlier draft considered asking the learner to predict every render triggered by clicking
    "Run sample data" end-to-end, which turned out to depend on subtle batching mechanics not
    actually in this lesson's scope (or the task file's). Replaced with a single, fully
    deterministic prediction inside one synchronous block (a `console.log` placed between two
    setter calls that both run before any `await`), matching react.dev's own canonical "State as a
    Snapshot" example instead of inventing a harder one.
  - Both external URLs (`react.dev/learn/state-as-a-snapshot`, `react.dev/learn/you-might-not-need-an-effect`)
    were fetched and confirmed live/on-topic before citing. The second citation is explicitly scoped
    to "read only its early sections on computing values during rendering" — its Effect-specific
    content is Lesson 37's citation to make, not this lesson's.
  - Navigation: `0035`'s forward nav (both top and bottom) was rewired from its placeholder note to
    a real link now that `0036` exists, per `ROADMAP.md`'s own note that this rewiring was pending.
    `0036`'s forward nav is now the placeholder note, following the same convention.
  - No reference doc shipped this round — the task file's `react-render-effect-decision-guide.html`
    reads as a synthesis of this lesson's render/event material and Lesson 37's Effect material, so
    it's deferred until `0037` ships rather than authored half-scoped now. Flagged in `ROADMAP.md`.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught and fixed six issues** before treating `0036` as
    done, the same pattern as `0035`'s review: (1) the `canSubmit` code block had raw `&&`, which
    is invalid inside an HTML entity-parsing context — escaped to `&amp;&amp;` (still displays as
    `&&` in the browser); (2) the lesson called `runValidation` itself "the event handler," but the
    real handlers wired to `onClick` are `handleRunValidation`/`handleRunSampleData` — reworded in
    both places `runValidation` was introduced to call it the shared helper those handlers call,
    not the handler itself; (3) one in-body link pointed at `0037-effects-cleanup-and-async-ui.html`,
    which doesn't exist yet — the top/bottom nav already used a non-linking placeholder for this,
    the in-body reference didn't match; fixed to the same placeholder convention; (4) the "fixed
    binding" framing of the snapshot section risked implying state objects are deeply frozen —
    added a sentence clarifying the binding is fixed per-render but an object's fields aren't
    automatically protected from direct mutation, which is *why* this repo always replaces objects
    wholesale, tying forward into the immutable-update paragraph that follows; (5) all three
    quizzes still had the correct answer as the longest option by 2–3 words — rebalanced to within
    one word per set; (6) "run this component again soon" implied a timing guarantee setState
    doesn't make — reworded to "schedules another render with the new value," which also avoids
    pre-committing to language that would need walking back once batching comes up later.
- 2026-07-19 (later, same day): shipped `0037-effects-cleanup-and-async-ui.html`, the third lesson
  in the Track 5 optional reinforcement sequence, same one-at-a-time pacing.
  - Content follows the task file's brief closely: `useEffect` as synchronization with something
    genuinely outside React (a network fetch), not a general "run code later" hook; the empty
    dependency array read two ways (runs once after mount, and can't loop on a value — `status` —
    the Effect itself writes); the `cancelled` cleanup guard against updating an unmounted
    component; and the early `status === "loading"` return that exists specifically to stop sample
    data from flashing before live data resolves. All three of the task file's named failure modes
    (unmounted-component updates, sample-data flashing, effect loops from depending on
    self-written state) are addressed directly, one per major section, and each also has its own
    retrieval-check question.
  - Used `DashboardLiveSections.tsx` as the traced file, per the task file's explicit instruction —
    the one component in this repo that genuinely needs an Effect. Every excerpt (the full
    `useEffect` block, the loading/failed early-return branches with their ADR 0007 comment, the
    three `IsSample` derived consts) is fully verbatim, line numbers verified by direct `Read`
    immediately before writing. No `...`-trimmed excerpts.
  - Added a short bridging section back to `order-validation/page.tsx`'s `useMemo`-wrapped
    `filteredErrors` (Lesson 35 previewed `useMemo` without teaching it; this lesson still doesn't
    teach its mechanics, only quotes its dependency array, `[errors, errorSeverity, errorSearch]`,
    as one line of real, complete code to contrast against the Effect's `[]`) — this is the
    concrete seed for the still-deferred `react-render-effect-decision-guide.html`, now that both
    of its prerequisite lessons (`0036` render/event material, `0037` Effect material) exist.
  - Applied `0036`'s review lessons proactively rather than waiting to be told: caught and fixed,
    before calling the draft done, an in-body link to Lesson 42 written as a live `<a href>` even
    though `0042` doesn't exist yet — converted to the same plain non-linking placeholder text
    every other not-yet-generated forward reference in this sequence uses. Also verified via a
    small script that no code block contains an unescaped raw `<` (the loading/failed branch's JSX
    needed `&lt;`/`&gt;` escaping; the two plain-logic blocks didn't need any).
  - The exercise (delete both `if (cancelled) return;` guards, predict whether `npm run typecheck`
    still passes, verify, undo) was chosen specifically to be safe and deterministic — an earlier
    idea (temporarily change the dependency array to `[status]` and actually reload the page to
    watch it loop) was rejected the same way `0036`'s batching-heavy exercise idea was: it would
    have worked, but only by live-triggering a runaway fetch loop against the local dev backend,
    which isn't a safe or necessary way to prove the point. The shipped exercise instead makes a
    forward connection to Lesson 42 (not yet generated): removing the guard doesn't change any
    value's type, so the build stays green even though a real runtime bug now exists — a concrete,
    safe instance of "a clean build doesn't prove runtime correctness."
  - The one external URL (`react.dev/learn/synchronizing-with-effects`) was fetched and confirmed
    live/on-topic before citing, per this workspace's standing verify-before-cite rule.
  - Navigation: `0036`'s forward nav (top and bottom) was rewired from its placeholder to a real
    link to `0037`, the same rewiring `0035` got when `0036` shipped. `0037`'s own forward nav is
    now the placeholder, per the established convention.
  - No reference doc shipped this round either — `react-render-effect-decision-guide.html` is now
    genuinely ready to write (both `0036` and `0037` exist), but wasn't requested this session;
    flagged as pending, not deferred-for-a-reason, in `ROADMAP.md`.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught and fixed a conceptual error, not just wording** —
    more substantive than either prior review. The lesson's central rule had been quietly wrong:
    "reaching outside React needs an Effect" is **necessary but not sufficient** — Lesson 36's
    `runValidation` already reaches outside React (a real HTTP request) and is correctly an event
    handler, not an Effect, because that request is caused by a click, not by rendering. The actual
    rule is *caused by rendering itself* vs. *caused by a user action*; "reaches outside React" was
    never the discriminator. Fixed everywhere this appeared: the mission box, the section
    introducing the Effect, the derived-value bridge section, the say/avoid box, and the closing
    ask-teacher box — all now explicitly contrast the dashboard fetch against `runValidation`'s
    click-triggered fetch rather than treating "outside React" alone as the trigger.
  - **Also fixed a factual error in the dependency-array reasoning**, caught the same way: the
    original draft claimed adding `status` to the Effect's dependency array would cause "an Effect
    loop that never settles." Traced through by hand, that's wrong — `setStatus("loaded")` firing a
    second, redundant Effect run would itself call `setStatus("loaded")` again with the *same*
    value, which React bails out of re-rendering for (`Object.is` same-value check), so the cycle
    stops after one wasted request, not infinitely. Rewrote the explanation around the actually
    correct reason `status` doesn't belong in the array — it's this Effect's own *output*, not an
    input to the synchronization — and added a one-sentence, clearly-hypothetical aside about what
    a *genuine* infinite Effect loop looks like (no dependency array at all) without claiming this
    file's code would produce one. Updated the matching quiz option and `ROADMAP.md`'s description
    to match.
  - **Broadened the cleanup-guard explanation and the Strict Mode claim**, which the original draft
    got directionally right but incompletely: `[]` doesn't just mean "runs once" full stop — it
    means once per mount in production, and twice (an extra setup → cleanup → setup cycle) under
    development Strict Mode, specifically to stress-test cleanup logic. The `cancelled` guard's
    real job is ignoring a stale result from *any* cleaned-up Effect instance, not only the
    component-unmounted case — the Strict Mode double-invoke is the other concrete case it guards
    against, and it doesn't cancel the underlying `fetch`, only the result. Verified this
    specifically against the `useEffect` API reference's Caveats section (not just the
    "Synchronizing with Effects" guide already cited) and added it as a second citation.
  - **Fixed one factual slip**: the derived-value section had said `useMemo` was "previewed in
    Lesson 35" — Lesson 35 previewed generics (`DataTable<T>`), not `useMemo`. Corrected to "reserved
    for Lesson 38."
  - **Sharpened the exercise's own explanation**: the original claimed removing the `cancelled`
    guard changed "nothing about its type or usage" — untrue, `cancelled` genuinely becomes a
    write-only variable, which is a real usage change. The actual reason `npm run typecheck` still
    passes is that this repo's `tsconfig.json` doesn't enable `noUnusedLocals` (verified directly
    against the file), so nothing in the toolchain is configured to catch a write-only local, let
    alone the runtime bug itself. This makes the Lesson 42 forward-connection sharper and avoids
    presenting a configuration-dependent result as if it were a universal TypeScript rule.
  - Rebalanced the second quiz's option lengths to within one word (previously 11/13/10), same pass
    that broadened its correct answer to "a stale response from a cleaned-up Effect instance," not
    only "a component that's already gone."
- 2026-07-20: shipped `0038-list-keys-identity-generics-and-memoized-derivations.html`, the fourth
  lesson in the Track 5 optional reinforcement sequence, same one-at-a-time pacing. This is the
  lesson `0035` (generics) and `0037` (`useMemo`) both explicitly forward-referenced without
  teaching — both payoffs land here.
  - Content follows the task file's brief: generics, list keys, immutable sorting, and memoized
    derivations, unified around one running example — `DataTable<T>` plus its two
    `order-validation/page.tsx` call sites — rather than four separate examples, to keep a
    four-concept lesson from sprawling. Both of the task file's named tangible wins are addressed
    directly: tracing `T` from `DataTableColumn<ValidationErrorRow>[]` through `render(row)` to a
    call site's inferred type parameter, and choosing a row key
    (`` getRowKey={(r) => `${r.row_number}-${r.error_code}`} ``) grounded in the fact that this
    exact table is sortable, not a hypothetical — **later corrected by review, see below, to also
    show this exact key is not actually unique**, not just presented as safe. All three named
    failure modes (index keys on reorderable data, mutating the prop array via `.sort()`, treating
    `useMemo` as semantics-changing rather than caching) get their own section and their own
    retrieval-check question.
  - Every excerpt (`ERROR_COLUMNS`' `order_id` column, the `<DataTable>` call site, `DataTable.tsx`'s
    `TableRow key={getRowKey(row)}` line, its `[...data].sort(...)` block, and its
    `[data, sort, columns]` dependency array) is fully verbatim, line numbers verified by direct
    `Read` immediately before writing — including `DataTable.tsx` in full this time, not just the
    portion read incidentally while authoring `0035`/`0036`. One excerpt (`ERROR_COLUMNS`' opening
    plus its `order_id` column) deliberately skips a line (the `row_number` column) — the box label
    states the discontinuous range explicitly (`lines 46, 48–54`) rather than implying false
    contiguity, the same convention `0035`'s reviewed layouts excerpt established.
  - Added `DonutBreakdownChart.tsx`'s `key={segment.label}` as a one-sentence second instance of
    the same key-identity rule outside any table, confirmed by reading that file — kept brief
    rather than expanded into its own section, since the task file's "chart segments" mention reads
    as reinforcement, not a fourth full example to unpack.
  - Caught and fixed one self-introduced authoring bug before treating the draft as done: the first
    write of the "Keys" section's inline `getRowKey` code sample had literal backslash characters
    before its backticks (`` \`...\` ``) — an artifact of drafting the snippet as if it needed
    JS-string escaping, which plain HTML text never does. Verified via a grep for the literal
    `` \` `` sequence, found one instance, fixed it, then re-verified none remained.
  - The two-part exercise mirrors `0037`'s successful pattern (predict, edit, observe via a real
    feedback loop, undo) but deliberately varies the feedback mechanism across its two parts rather
    than reusing `npm run typecheck` twice: Part 1 is a `typecheck`-verified prediction (a
    nonexistent field access on `ValidationErrorRow` inside a column's `render`), Part 2 is a
    browser-observed prediction (temporarily drop `sort` from `DataTable.tsx`'s memo dependency
    array and watch the header's ▲/▼ indicator visibly disagree with the actual row order after a
    click) — chosen because it's safe, fully reversible, and directly demonstrates the "stale
    cache, not a crash" failure mode without needing to touch application data or trigger any
    network activity.
  - All three external URLs (`react.dev/learn/rendering-lists`, the TypeScript Handbook's
    "Generics" page, `react.dev/reference/react/useMemo`) were fetched and confirmed live/on-topic
    before citing.
  - Navigation: `0037`'s forward nav (top and bottom) was rewired from its placeholder to a real
    link to `0038`. `0038`'s own forward nav is now the placeholder, per the established
    convention.
  - No reference doc shipped this round — `list-identity-and-memoization-checklist.html` is
    `0038`'s named companion per the task file, and is now genuinely ready to write, but wasn't
    requested this session; flagged as pending in `ROADMAP.md` alongside the still-pending
    `react-render-effect-decision-guide.html`.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught one critical and three substantive conceptual
    issues**, the most significant of the four review passes across this sequence so far.
    - **Critical, and the actual blocking issue**: the lesson had called
      `` getRowKey={(r) => `${r.row_number}-${r.error_code}`} `` a "safe" key. It isn't —
      `test_ov001_emits_one_error_per_missing_field_in_fixed_order` in
      `tests/test_order_validation.py` (traced against `src/order_validation.py`'s OV-001 loop,
      which passes the same `row_number` parameter to every missing-field error it emits for one
      row) proves a single row can emit two same-`error_code` OV-001 errors, producing a genuine
      duplicate key whenever a row is missing two or more required fields. Verified by reading the
      test and the business-rule source directly, not by taking the finding on faith. Rewrote the
      "Keys" section to teach two separate requirements (stable **and** unique among siblings, not
      one bundled idea), reveal this repo's real key satisfies only the first, and propose an
      interim fix (fold `error_message` into the key) while naming the actually-correct fix (a
      dedicated Python-emitted identity field) as a contract change and therefore out of a
      frontend lesson's scope per this repo's own Field Scope Boundary rule — a real repo defect
      is now named honestly in the lesson, not silently presented as fine, and critically not
      "fixed" by editing application code either, since lesson-authoring is never supposed to
      change app code.
    - Reframed the index-key danger from an overstated claim (implying this exact table would
      display wrong data after a sort) to the accurate one: this table's stateless, pure-value
      cells would still show correct text per row, because every cell renders straight from its
      row prop; the actual risk is component/DOM-level state (uncontrolled inputs, focus,
      selection, animation, local row state) reattaching to the wrong business row. Framed
      explicitly as a latent defect in a reusable sortable table pattern, not a claim about this
      table's current visible behavior.
    - Rewrote the `useMemo` section around `Object.is` reference equality specifically, replacing
      vague "when one of these three actually changes" language: `ERROR_COLUMNS` has a stable
      module-scope reference, `filteredErrors` is itself already memoized by the page, and
      `toggleSort`'s `setSort` call constructs a fresh object literal on every click — so `sort`'s
      *reference* changes every time regardless of whether its fields differ, which is
      meaningfully different from Lesson 37's primitive-string same-value bailout case and is now
      stated correctly instead of glossed over. Also softened "only when"/"simply wouldn't move" to
      "normally," with an explicit note (grounded in the `useMemo` reference itself) that React may
      still discard a cached value on its own and that Strict Mode can run the calculation twice.
    - Added a real `npm run lint` step to the exercise's Part 2 — verified directly by temporarily
      removing `sort` from `DataTable.tsx`'s dependency array, running `npm run lint`, capturing
      the actual warning (`react-hooks/exhaustive-deps`, "React Hook useMemo has a missing
      dependency: 'sort'"), and reverting the file via `git checkout` before writing anything into
      the lesson — not transcribed from the review's summary of the expected warning. This
      completes a three-layer verification triad in one exercise (typecheck misses it, the browser
      shows it, ESLint names it), bridging cleanly into Lesson 42.
    - Minor fixes also applied: the closing `ask-teacher` box now explicitly invites follow-up
      questions instead of only recommending rereading; and a new closing synthesis box
      distinguishes the lesson's three different senses of "identity" (compile-time generics,
      runtime keys, reference-equality memo deps) so a learner doesn't conflate them as one
      mechanism, per the review's suggestion.
    - `ROADMAP.md`'s `0038` row and this entry's own earlier bullet were both corrected to match —
      the review explicitly asked that the incorrect "safe row key" claim not be left standing in
      either tracking file.
- 2026-07-21: shipped `0039-css-layout-flow-flex-grid-and-overflow.html`, the fifth lesson in the
  Track 5 optional reinforcement sequence, same one-at-a-time pacing. This is the first lesson in
  the sequence that isn't React/TypeScript mechanics — pure CSS layout, assumed as zero prior
  knowledge like every other Track 5 lesson.
  - Content follows the task file's brief closely, organized around the throughline the task
    file's own "tangible win" names: which ancestor owns height, and (per a same-day review pass,
    see below) which region owns scrolling for which axis — not a single global scroll owner. All
    five named target files were used with real, verified examples rather than invented ones:
    `Card.tsx` (box model/border-box), `AppShell.tsx` (flex main/cross axis, traced through its
    real nested `flex`/`flex-col` structure), `ValueSection.tsx` (grid tracks, the `fr` unit, and a
    second mobile-first example), `UploadPanel.tsx` (intrinsic minimum size, two genuinely
    different real fixes to the same problem), and `AppShell.tsx`, `SidebarNav.tsx`,
    `app/(public)/layout.tsx`, and `Table.tsx` together for overflow ownership (several real,
    independently-scoped strategies layered on the same page, not one blanket rule).
  - The intrinsic-minimum-size claim — that `UploadPanel`'s `truncate` span correctly truncates
    without an explicit `min-w-0`, because `overflow: hidden` alone already zeroes a flex item's
    automatic minimum size per the CSS spec — was verified against MDN's `min-width` reference
    before writing a word of the lesson, not assumed from general flexbox familiarity. This is the
    most technically subtle claim in the lesson and the one most likely to be wrong if guessed at;
    it wasn't guessed at.
  - Caught and fixed two self-introduced verbatim-excerpt violations before treating the draft as
    done, both in the same pattern the `0035` review originally flagged: an early draft of the
    `AppShell.tsx` excerpt was hand-abridged with a `{/* SidebarNav */}`-style comment standing in
    for real JSX, and an early draft of the `Table.tsx` excerpt replaced
    `className={cn("w-full border-collapse text-xs", className)} {...props}` with a literal
    `"..."` placeholder. Both were rewritten as genuinely verbatim excerpts (the `AppShell` one
    using an honestly-labeled two-range citation, `lines 55–58, 73–77`, skipping the unrelated
    mobile-drawer JSX) and verified with a script that specifically distinguishes real `{...props}`
    JSX spread syntax from a truncation ellipsis, catching the exact class of mistake `0038`'s
    review caught in prose rather than code.
  - Caught and softened one unverified factual claim on a self-review before calling the draft
    done, without being told to: an early draft of the "avoid" framing asserted that this exact
    shell "routinely breaks another [viewport], or creates a second, nested scrollbar... a real
    cost this repo has already paid once, in work the deferred Phase 9.1 retrospective covers in
    full" — a specific claim about Phase 9.1's actual content that was never verified, and that
    reading `docs/plan/phase-9.1-visual-alignment-fixes` to verify would itself have violated the
    task file's explicit instruction not to pre-empt that reserved retrospective. Rewrote to note
    only that the retrospective exists and is reserved for that shell's specific history, without
    claiming to know or narrate what it contains — satisfies both the accuracy bar and the
    non-pre-emption instruction at once, rather than trading one for the other.
  - All five external URLs (MDN's "Introduction to CSS layout," "Flexbox," "Grids," and
    `min-width` reference; Tailwind's "Responsive Design" page) were fetched and confirmed
    live/on-topic before citing — more citations than any prior lesson in this sequence, justified
    by the task file's own eight-concept list spanning both general CSS (MDN) and Tailwind-specific
    convention (mobile-first prefixes).
  - The exercise avoids the two known problem patterns from earlier reviews (an unsafe live edit,
    or an inaccurate prediction stated as fact): removing `overflow-y-auto` from `AppShell.tsx`'s
    `<main>` is safe and fully reversible, and the predicted outcome (content clipped with no
    scrollbar able to reach it, not "the page scrolls instead" — later narrowed by review from an
    overbroad "no scrollbar anywhere" claim, since `SidebarNav`'s own unrelated scrollbar is
    unaffected) was reasoned through by hand against the real ancestor chain's actual
    `overflow-hidden`/`h-screen` values before being written down.
  - Navigation: `0038`'s forward nav (top and bottom) was rewired from its placeholder to a real
    link to `0039`. `0039`'s own forward nav is now the placeholder, per the established
    convention.
  - No reference doc shipped this round — `css-layout-debugging-checklist.html` is `0039`'s named
    companion per the task file, now genuinely ready to write, but wasn't requested this session;
    flagged as pending in `ROADMAP.md` alongside the two other still-pending reference docs.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught three substantive conceptual issues**, all in the
    direction of "the lesson's model was too absolute for the real system it was describing."
    - **The central "exactly one owner" framing was wrong**, not just imprecise:
      `SidebarNav.tsx` line 24 (`<nav className="flex h-full w-60 shrink-0 flex-col gap-1
      overflow-y-auto ...">`) has its own real `overflow-y-auto`, verified by directly reading the
      file — a second, independent scroll region the lesson's "the only element in that whole tree
      with `overflow-y-auto` is `<main>`" claim flatly missed. Rewrote around a per-region,
      per-axis model instead ("identify every size constraint and overflow boundary, then name
      which region and axis each one owns"), applied consistently: the lede, the mission box, the
      workspace-shell section (now explicitly "two independent internal scroll regions, not one,"
      with a real `SidebarNav.tsx` excerpt added), the exercise (narrowed from "no scrollbar
      anywhere" to "no scrollbar capable of reaching the clipped main content," with an explicit
      note that the sidebar is an unrelated sibling branch, unaffected by the exercise's edit
      either way), `ROADMAP.md`, and this entry's own earlier bullet (below).
    - **The Grid section overstated `fr` as content-independent**: `grid-cols-[1fr_2fr]` was
      described as splitting exactly 1:2 "not by either block's own content — the parent grid
      decided the split before either child rendered." Verified against MDN's own explicit note
      that `fr` distributes *available* space, not all space, so a track with large intrinsic
      content can still claim space before the remainder gets divided by weight. Rewrote as "a
      target ratio, not a content-independent guarantee," and changed "fixed tracks" to "explicit
      tracks" throughout, since "fixed" implied exactly the content-independence that isn't true.
    - **`overflow-hidden` was described as leaving content "with no way to reach it," which is
      false**: verified against MDN's `overflow` reference that `overflow: hidden` still
      establishes a scroll container — tabbing to a clipped focusable element scrolls it into
      view, and `scrollTo()`/`scrollTop` still work programmatically. `overflow: clip` is the
      value that's genuinely unreachable (not a scroll container at all). Rewrote the "Overflow
      ownership" section's opening to state this distinction precisely, added a new citation
      (MDN's `overflow` reference) to the lesson's cite box and `RESOURCES.md`, and narrowed the
      intrinsic-minimum-size section's parallel claim from "anything other than `visible`" to the
      more precise "becomes a scroll container," explicitly flagging `overflow: clip` as the
      documented exception rather than letting the two sections quietly contradict each other.
    - Minor fixes applied in the same pass: quiz 1's correct answer no longer claims `<main>` has
      "nothing capping it" (its parent does constrain it) — reworded to "Header has fixed height
      and cannot shrink; main grows into remaining space," per the review's exact suggested
      wording; quiz 2's options rebalanced from 11/10/10 words to 11/11/11.
    - `ROADMAP.md`'s `0039` row and this entry's own earlier bullets were rewritten to match —
      same standing practice `0038`'s review established, of not leaving a corrected claim
      standing anywhere in the tracking files.
- 2026-07-21 (later, same day): shipped `0040-accessible-components-as-contracts.html`, the sixth
  lesson in the Track 5 optional reinforcement sequence, same one-at-a-time pacing. Densest concept
  list of any lesson in this sequence so far — eleven named sub-concepts across six components —
  handled by grouping into six sections around shared mechanisms rather than one section per
  concept (e.g. `aria-current`, `aria-expanded`, and `role="alert"` share one section as "ARIA
  computed from the same state driving the visuals," since that's the actual unifying idea, not
  three unrelated attributes).
  - All six named components (`UploadPanel`, `TopHeader`, `SidebarNav`, `BusinessErrorMessage`,
    `DataTable`, both chart components) contributed real, verified excerpts — `Badge.tsx` was
    added as a seventh, since `StatusBadge` itself is a thin wrapper and the actual
    color-plus-text rendering lives one layer down.
  - Caught and fixed two of my own verbatim/citation errors before treating the draft as done,
    both by re-reading the real files against my own draft rather than trusting memory: (1) the
    `UploadPanel.tsx` excerpt was mislabeled `lines 64–72` when the quoted content actually ran
    through line 74 — fixed after re-reading the file directly; (2) the `SidebarNav.tsx` excerpt
    used a literal `...` inside a `<pre><code>` block to bridge two non-adjacent lines (29 and 35)
    — the exact class of mistake `0039`'s own self-review had just caught and fixed in a different
    spot. Split into two separate single-line boxed excerpts instead, consistent with how `0038`'s
    review-driven fix and `0039`'s `AppShell` fix both handled non-contiguous real citations.
  - Named one real, current, unfixed gap in the repo rather than presenting every example as
    flawless, continuing the precedent `0038`'s row-key finding set: `DataTable`'s sortable column
    headers are real `<button>`s (keyboard/click semantics free) but convey the current sort
    direction only via a visible `▲`/`▼` character, never `aria-sort` on the header cell — checked
    directly with `grep -rn "aria-sort"` across `components/` and `app/` before asserting this,
    not assumed from not having noticed one.
  - The "Visible focus" section deliberately declines to render a verdict on whether
    `VerticalBucketBarChart`'s `focus:outline-none` (paired with a real `group-focus:` dim + reveal
    -tooltip replacement) is an adequate substitute for a focus ring — stated the mechanism
    precisely and pushed the judgment call into the exercise instead, which asks the learner to tab
    through the real running dashboard and decide for themselves. Chosen deliberately after `0039`'s
    review made clear the cost of a confident-but-wrong technical verdict; here the honest answer
    is "reasonable people could disagree," so the lesson says that instead of picking a side it
    can't fully back.
  - Three citations (MDN's "ARIA" overview, the W3C WAI ARIA APG's "Names and Descriptions" and
    "Alert" pages) were fetched and confirmed live/on-topic before citing — fewer than `0039`'s six,
    since most of this lesson's eleven sub-concepts are concrete instances of the same two or three
    underlying ARIA principles rather than needing their own separate source.
  - The exercise is a pure observation exercise (tab through the real running dashboard, watch what
    happens) with no code edit and nothing to undo — a deliberate departure from every prior
    lesson's edit-based exercise, chosen because the "Visible focus" section's open question is
    itself something to observe, not something a typecheck or lint run could settle.
  - Navigation: `0039`'s forward nav (top and bottom) was rewired from its placeholder to a real
    link to `0040`. `0040`'s own forward nav is now the placeholder, per the established
    convention.
  - Scope boundary respected explicitly: the lesson never analyzes `AppShell`'s drawer
    focus-trap/focus-move behavior (real code that exists in the file, per `0039`'s own citation of
    `AppShell.tsx`), even though it's directly adjacent to material this lesson does cover — named
    once in the closing `ask-teacher` box as reserved for the deferred mobile-nav retrospective,
    per the task file's explicit instruction, rather than silently ignored or partially leaked.
  - No reference doc shipped this round — `accessible-component-contract.html` is `0040`'s named
    companion per the task file, now genuinely ready to write, but wasn't requested this session;
    flagged as pending in `ROADMAP.md` alongside the other three still-pending reference docs.
  - No learning records written — correctly so, per this file's standing rule.
  - **Post-draft review pass (same day) caught two critical and four substantive issues** — the
    deepest and most technically demanding review of any lesson in this sequence, because it
    required verifying claims about the ARIA specification itself, not just this repo's code.
    - **Critical: `aria-label` on the bar-chart div is not a valid pattern, and the original draft
      called it one.** Verified directly against the ARIA 1.2 spec's definition of the `generic`
      role: "the element does not support name from author. Authors MUST NOT use the `aria-label`
      or `aria-labelledby` attributes to name the element." A plain `<div>` with no ARIA role has
      the implicit role `generic`, `tabIndex` doesn't change that, and the original draft's framing
      — that `aria-label` here was legitimate "manual work standing in for what a button gets for
      free" — was simply wrong; the label may be silently ignored by assistive tech. Rewrote the
      section to state this as a real, current gap, and added an entirely new section covering
      `DonutBreakdownChart.tsx` (which the lede had always promised but an earlier draft never
      actually delivered) as the genuine working contrast: its circles use `role="img"` +
      `aria-label`, and `img` is an explicitly nameable role, which is *why* that one actually
      works. Did not edit `VerticalBucketBarChart.tsx` itself — named the gap and described what a
      real fix would look like (`role="img"`, an accessible `<figure>`, or an accompanying data
      table), consistent with this workspace's standing rule against changing application code
      while authoring lessons.
    - **Critical: `UploadPanel`'s visible `label` prop was never actually connected to the file
      input's accessible name, and the original draft implied it was.** Re-read the component
      closely enough to notice the `label` prop ("Orders File," "Product Master File") renders as
      a bare `<span>` (line 54), entirely separate from the real `<label htmlFor={inputId}>`
      further down whose own text — "Choose a file… Browse" — is what actually becomes the input's
      accessible name. Consequence, verified against the real page: `order-validation/page.tsx`
      renders two `UploadPanel`s whose accessible names are effectively identical, since neither
      incorporates the distinguishing prop text. Also added a second, previously entirely
      unmentioned gap in the same component: no `focus-within:` styling anywhere on the visible
      label, so tabbing to the `sr-only` input produces no visible focus indicator at all —
      confirmed by checking the full className list, not assumed.
    - **Quiz 1 contradicted the lesson's own TopHeader excerpt** — it claimed the toggle button
      "needs neither tabIndex nor aria-label explicitly," while the very first code excerpt in the
      lesson shows it has an explicit `aria-label` (correctly, since it's icon-only). Rewrote the
      question entirely, per the review's suggested redesign, to contrast `DataTable`'s
      content-named button against the bar chart's now-corrected invalid `aria-label`.
    - **`role="alert"` was over-narrowed to "only works because of conditional rendering."**
      Verified against MDN's live-region guidance that the general mechanism is broader: a live
      region announces *dynamic* changes — new content or an in-place text mutation, both after
      the page has already loaded — not specifically React unmount/remount. Reworded the
      explanation and Quiz 2 around the general rule, with conditional rendering named as this one
      component's specific instance of it, not the definition.
    - Fixed two overclaims caught in the same pass: "every ARIA attribute is bound to state"
      narrowed to "every *stateful* ARIA attribute" (`aria-hidden="true"` and the literal
      `aria-controls="mobile-sidebar-drawer"` string are intentionally not state-derived); "this
      repo hides every purely decorative icon" narrowed to name the real counter-example,
      `MetricCard.tsx`'s icon wrapper, which has no `aria-hidden` and isn't given one automatically
      — verified by reading `node_modules/lucide-react`'s actual `defaultAttributes.js` and
      `Icon.js` directly rather than assuming the installed library's default behavior.
    - Added WCAG's Focus Visible three-part test (identifiable, persistent, distinguishable)
      *before* the focus-outline judgment call, applied it explicitly to `UploadPanel`'s
      objectively-failing case and to all three real `focus:outline-none` replacements across both
      charts (including a self-caught correction mid-edit: an early rewrite claimed
      `DonutBreakdownChart`'s legend rows replace the outline with "nothing at all," which is
      wrong — `onFocus` triggers the same `hoveredLabel` state `onMouseEnter` does, producing a
      real background-highlight-plus-percentage-reveal change; caught by re-reading the file
      instead of trusting the first draft of that sentence). Extended the exercise to cover the
      objective `UploadPanel` case alongside the judgment calls, and to the donut chart's doubled
      per-datum focus stops.
    - Minor fixes: "six components" corrected to "seven" in the lede (five named plus two charts);
      added the WCAG Use of Color citation directly to the color section; added the WAI
      sortable-table pattern citation to the existing `aria-sort` finding.
    - `ROADMAP.md`'s `0040` row and `RESOURCES.md` were both updated to match, per the same
      standing practice every prior review in this sequence has followed.
- 2026-07-22: shipped `0041-route-groups-layout-composition-and-metadata.html`, the seventh lesson
  in the Track 5 optional reinforcement sequence, same one-at-a-time pacing. First lesson in this
  sequence to teach genuinely new repo structure rather than reinforcing existing Tutorial 09-11
  material — the `(public)`/`(workspace)` route groups didn't exist until the portfolio-landing-page
  session (per this project's own `memory.md`).
  - Read the five real files the task brief named (`app/layout.tsx`, `app/(public)/layout.tsx`,
    `app/(workspace)/layout.tsx`, `app/(public)/page.tsx`, `app/(workspace)/dashboard/page.tsx`) plus
    all six current route files under `app/` before writing a line, to get the folder→URL table
    and every excerpt's line numbers right the first time — verbatim/citation accuracy held with no
    correction round needed, but a post-draft review pass (below) still caught real conceptual
    overclaims that source-reading alone hadn't surfaced.
  - Fetched all four Next.js doc pages used (`project-structure#route-groups`,
    `layouts-and-pages`, `metadata-and-og-images#static-metadata`,
    `generate-metadata#merging`) live via WebFetch before citing any of them, rather than relying on
    the locally installed docs snapshot alone — confirmed each still matches the installed
    `node_modules/next/dist/docs` copy and is live at version 16.2.11.
  - Real, verified finding used as the lesson's central worked example: three of the five
    `(workspace)` pages (`order-validation`, `inventory-allocation`, `payment-aging`) currently
    can't export `metadata` because their `page.tsx` module is `"use client"`, while `dashboard` and
    `reports` stay Server Components that simply choose not to. Confirmed via `grep` across `app/`
    that only `app/layout.tsx` and `app/(public)/page.tsx` export a `metadata` object anywhere in
    the app.
  - Went one step further than reading source to verify a claim: rather than asserting metadata
    inheritance from the docs' abstract example alone, ran `npm run build` and `grep`-compared the
    real prerendered `<title>` tags in `.next/server/app/index.html` (overridden: "... | Portfolio
    Case Study") against `dashboard.html` and `reports.html` (both inherit the root layout's plain
    title, byte-for-byte). This became both a cited excerpt and the lesson's own exercise — predict
    `reports.html`'s title from the rule, then run the same `grep` to check it, entirely reversible
    since `.next/` is a gitignored build artifact.
  - Cited `docs/architect/portfolio-landing-page/decisions.md` directly for the real, sessioned
    reason the route-group split exists (no operational sidebar chrome on a portfolio visitor's
    first view) and its named consequence (`<Link>`/router navigation between `/` and `/dashboard`
    stays one client-side transition because this app defines only one root layout) — real project
    history, not an invented rationale.
  - **Post-draft review pass (same day) caught two conceptual overclaims and five smaller precision
    issues** — the first lesson in this sequence where verbatim/citation accuracy held clean but
    the underlying claims still needed correction:
    - **The lesson had presented the workspace pages' shared title as an intentional SEO/indexing
      decision** ("none of its workspace pages are meant to be indexed publicly"). No architecture
      doc records that decision and this app has no `robots`/`noindex` mechanism enforcing it either
      way. Reworded to state this as the app's current, undocumented behavior and a real, low-risk
      improvement to flag — not a considered trade-off — and added WCAG's Page Titled criterion
      ("titles identify the current location without requiring users to read or interpret page
      content") to ground why unique titles matter for navigation/accessibility, not only SEO.
    - **The metadata-timing explanation overclaimed a universal "very first HTML response" rule.**
      This app's own metadata is entirely the static object form (confirmed via `grep`, no
      `generateMetadata` function exists anywhere in `app/`), resolved at build time because every
      route is prerendered — but the docs separately describe a dynamic `generateMetadata` function
      streaming its result in after the initial UI on a dynamically-rendered route. Reworded to
      state both as two delivery timings for the same Server-Component-only rule, not one universal
      behavior, without touching any application code.
    - "Three of them structurally can't [export metadata]" conflated the current `page.tsx` module
      with the route itself — a Server Component page wrapping a Client child could still export
      real metadata for that same route. Reworded to scope the limitation to the module.
    - "A route group is a filing decision, nothing more" undersold the mechanism — the route-groups
      reference itself documents opting a route subset into a shared layout and defining multiple
      root layouts as real use cases. Reworded to "an organizational and layout-selection boundary,"
      naming those use cases, while keeping the correct point that it's never a URL or authorization
      boundary.
    - "Navigating between them stays a client-side transition" was too general — narrowed to
      `<Link>`/router navigation specifically, and tied to the real reason (one shared root layout),
      since the docs' own full-reload caveat applies specifically to multiple-root-layout setups this
      repo doesn't use.
    - "Each contains multiple real routes" was factually wrong for `(public)`, which holds exactly
      one route (`/`) against `(workspace)`'s five. Reworded to state the real, uneven split.
    - Quiz answer choices were uneven (roughly 7-10 words per option across the three questions) —
      rebalanced every option to within one word of its siblings per question.
    - Added an explicit caveat to the exercise that `.next/server/app/` is this installed Next.js
      version's own internal build-output layout, real and inspectable today but not a documented,
      version-stable public API — good for a one-off local check, not for permanent tooling.
    - `ROADMAP.md`'s `0041` row was rewritten to match every correction above, per the same standing
      practice every prior review in this sequence has followed.
  - Explicitly named a non-boundary the task brief flagged as a failure mode: route groups carry no
    authorization meaning, and this app has no login step at all, workspace routes included.
  - Navigation: `0040`'s forward nav (top and bottom) was rewired from its placeholder to a real
    link to `0041`. `0041`'s own forward nav is now the placeholder, per the established
    convention.
  - No reference doc shipped this round — `app-router-layout-map.html` is `0041`'s named companion
    per the task file, not requested this session; flagged as pending in `ROADMAP.md` alongside the
    other three still-pending reference docs.
  - No learning records written — correctly so, per this file's standing rule.
  - `ROADMAP.md` (status line, lesson-count table row, navigation paragraph) and `RESOURCES.md`
    (four new citations) were both updated to match, per the same standing practice every prior
    lesson in this sequence has followed.
