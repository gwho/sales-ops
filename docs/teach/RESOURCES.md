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

- [MDN — An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
  Vendor-neutral, widely regarded as the best plain-language HTTP primer. Use for: L4.1.
- [FastAPI — Tutorial (official)](https://fastapi.tiangolo.com/tutorial/)
  Written by the framework's own author; the project's `context/library-docs.md` already tracks project-specific deviations from it. Use for: pairing with Tutorial 7.
- [MDN — HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
  Reference for L4.1's "200/400/404/500" vocabulary.

## Track 5 — UI Components & Next.js

- [React — Learn React (official)](https://react.dev/learn)
  The canonical modern React tutorial, component/props/state framed exactly as L5.2 needs.
- [Next.js — App Router documentation](https://nextjs.org/docs/app)
  Official docs; specifically the "Server and Client Components" page is the primary source for L5.3, the single most-repeated rule in this repo.
- [TypeScript — Handbook (official)](https://www.typescriptlang.org/docs/handbook/intro.html)
  Use once JS/React basics are comfortable, before reading `types/dashboard.ts` etc. closely.
- [Tailwind CSS v3 documentation](https://v3.tailwindcss.com/docs)
  Pinned to v3 docs specifically — this repo deliberately stays on Tailwind 3.4, not v4 (see `context/library-docs.md`). Use for: L5.4 (design tokens).

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
