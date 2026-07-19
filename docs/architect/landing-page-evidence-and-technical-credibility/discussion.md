# Discussion — Landing Page Evidence and Technical Credibility

This is the deep record of the reasoning behind the decisions in `decisions.md` — not a summary of
what was decided, but why, including the alternatives that were considered and specifically why each
one failed.

## Where this session started: two review passes, not a blank page

This `/architect` session didn't start from nothing. It was preceded by two separate reviews in the
same conversation:

1. A **code-grounded classification** of `context/designs/landing-page-ideas.md` — six externally
   sourced suggestions (isometric hero mockup, "impact" badges with invented percentages, a Bento
   grid, an animated flow diagram via React Flow, a before/after comparison slider, an "Operations
   Philosophy" bio section, plus subtle SaaS-style polish) — each checked against the actual
   codebase and classified ADOPT/ADAPT/REJECT/DEFER.
2. An **independent ideation pass** that deliberately set that document aside and asked "starting
   only from the project's own goals and architecture, what would *you* propose?" — which surfaced
   the persistence-feature gap, the dual-audience-reader gap, and the "no real evidence anywhere on
   the page" gap.

Both passes agreed on one thing even though they started from different premises: almost every
externally sourced idea failed for the same underlying reason — it either invented a business claim
with no backing (the ROI percentages), introduced a dependency for a cosmetic effect (React Flow,
a slider library), or fought the page's own established visual identity (gradients, shadows, an
isometric mockup on a page whose own ADR calls for flat/no-shadow/editorial). The `/architect`
session's job was to take the ideas that survived both passes — mainly "show real evidence" and
"surface the persistence feature" — and turn them into something specific enough to build.

## Why two research agents ran before any decision was finalized

The six decisions arrived at this session already had the user's own recommendation attached to each
one. That could have been treated as "already decided, just confirm and move on." It wasn't, because
a recommendation is only as good as the facts it's checked against, and several of those facts were
still unverified:

- Was `lib/mock-data.ts` real, tested output, or hand-typed fixture data dressed up to look real? If
  it were hand-typed, "source proof from mock-data" (Decision 2's premise) would be building
  Decision 2 on the exact same kind of unverified claim it was trying to avoid.
- What does the ADR actually say about session persistence, word for word? Paraphrasing from memory
  risked repeating the "saved to this browser only" mistake this project had already made and fixed
  once.
- Are the landing page's workflow cards keyboard-reachable today? This wasn't asked in the six
  decisions at all — it only surfaced because a research agent was asked to check current
  accessibility semantics as part of general due diligence, not because anyone suspected it.

Two agents ran in parallel rather than one sequential pass because the two research areas were
genuinely independent — one traced a data pipeline (`lib/mock-data.ts` → `scripts/generate_mock_data.py`
→ `src/contracts.py` → `sample_data/README_sample_data.md`), the other traced documentation and
markup (`docs/adr/0007-...md`, `CONTEXT.md`, component JSX) — so there was nothing for them to block
each other on.

**What the research actually changed, concretely:** without it, Decision 2 would likely have been
implemented as "hardcode the numbers we see when we run the script once" — because that's the fast
path, and nothing in the six decisions as originally phrased forced anyone to check whether a
*programmatic* import was even possible (it required confirming `lib/mock-data.ts` exports something
importable and typed, not just that a JSON file exists somewhere).

## Why "exactly two," not "at least one"

This is the single most important technical decision in the whole plan, and it went through three
distinct versions before landing:

- **v1 (implicit):** "pluck the `SO-2026-010` / `OV-002` row" — singular, no count check at all. The
  failure mode: this is silently wrong *today*, because there are two matching rows and picking
  "the" row means arbitrarily picking one (whichever `.find()` returns first) while the copy still
  says "duplicate," which only makes sense if there are two.
- **v2:** "throw if fewer than two matches." Better — it would catch the case where the sample data
  changes and the duplicate disappears entirely, or shrinks to a single row. But it has a subtler
  gap: it would *not* catch the case where a future edit to `sample_data/sample_orders.xlsx`
  accidentally introduces a *third* occurrence of `SO-2026-010`. The landing copy explicitly says
  "appears twice" — three occurrences would make that sentence false while the "at least two" check
  stayed green.
- **v3 (locked):** exactly two, with distinct `row_number`s, and `summary.duplicate_orders === 2`
  as a second, independent check against the same fact from a different part of the output. This is
  the version that actually enforces what the sentence claims, not an approximation of it.

The general lesson here — and the reason this is worth a whole discussion section rather than a
one-line note — is that "add a check" is not automatically the same as "add the *right* check." A
check that's looser than the claim it's protecting gives false confidence: the build stays green,
but the claim can still quietly become false. This mirrors a principle already established elsewhere
in this codebase: `context/code-standards.md` draws a firm line between sample workbooks (plausible,
mostly-clean demo fixtures) and pytest DataFrame fixtures (where exhaustive, exact edge-case coverage
belongs) — the project already had a precedent for "don't trust eyeballing a sample file, verify it
programmatically and precisely." This decision just applied that same discipline to a new surface
(landing-page copy) that hadn't needed it before, because no landing content had cited real data
until now.

## Why the loader reads its selector from the JSON instead of owning a constant

The second review round caught something easy to miss: even after Decision 2 added invariant checks,
an early version of the loader still had `"SO-2026-010"` written into it directly, as a constant.
That looks harmless — it's still a "real" ID, still checked against the actual data — but it creates
a second place where the identity of the flagship example is decided. If someone later changed
`content/portfolio/...json`'s `validationEvidence.orderId` to reference a different case (say, if the
sample data's flagship duplicate case changed in a future phase), the loader's hardcoded constant
wouldn't know to follow. The two would silently disagree, and whichever one the component happened
to read from would "win" without anyone deciding that on purpose.

The fix — the loader reads `orderId`/`errorCode` *from* the JSON at runtime, rather than hardcoding
them — means there is exactly one place in the entire codebase where "which case are we citing" is
decided. This is the same "single source of truth" instinct behind `src/contracts.py`'s
`CONTRACT_SCHEMA_VERSIONS` guarding against stale-shape rows, or `DataTable`'s column config being
the one place render logic lives instead of being duplicated per page — a recurring pattern in this
codebase of preferring one authoritative location over two synchronized ones, because synchronized
copies drift and single sources can't.

## Why this creates a deliberate, narrow exception to an existing rule — and why that's acceptable here

`docs/architect/portfolio-landing-page/decisions.md` #3 established, during the *original* landing
page build, that `content/portfolio/sales-admin-automation-toolkit.json` is the single source for
all landing content. This session's Decision 2 breaks that rule: the evidence *numbers* (the message
text, the row/summary counts) come from `lib/mock-data.ts`, not the JSON.

This wasn't done lightly, and it wasn't hidden — Decision 3 (the content ownership split) exists
specifically to contain the exception. The rule that survives is: **the JSON still owns 100% of the
prose.** Only the verified *facts* being quoted come from elsewhere, and even then, only through a
single loader whose entire job is checking those facts before anything downstream sees them. A
future reader who sees `ValidationEvidence.tsx` importing from `lib/content/landing-evidence.ts`
instead of only from `portfolioContent` should understand this as "this one component quotes
external, verified facts" — a marked exception, not a precedent that any component can now import
data from anywhere it likes.

## Why the rejected ideas failed the way they did (not just "no")

It's worth being specific about *why* each rejected idea from the earlier review passes failed,
because the failure modes are different, and recognizing which failure mode a *future* idea falls
into is the actual transferable skill:

- **ROI percentages / "impact" badges** ("Reduces manual entry by 40%") — **fabricated claim.**
  There is no field in `src/contracts.py`, no test, no measurement anywhere in the project that could
  produce this number. It isn't wrong because it's flashy; it's wrong because nothing makes it true.
- **Isometric hero mockup, gradient CTA, pulse animation** — **identity violation.** These aren't
  false claims, they're just visually incompatible with a decision this project already made on
  purpose (`decisions.md` #1: flat, bordered, no-shadow, editorial). The failure mode here isn't
  "untrue," it's "inconsistent with an explicit prior decision that would need to be reopened, not
  quietly overridden."
- **React Flow, a comparison-slider library** — **unjustified dependency.** The capability these
  would add (an animated diagram, a drag interaction) already has a working, dependency-free
  alternative in this codebase's own conventions (`WorkflowSequence`'s plain-div icon-chip pattern;
  the charts' "no charting library, pure CSS/SVG" precedent). Adding a library here means taking on
  real long-term maintenance weight for a decorative effect that could be achieved without it.
- **A hardcoded test count in a proof strip** — **staleness.** Not false *today*, but true only
  until the next phase changes it, with no mechanism forcing an update. This is the same category of
  problem Decision 2's build-time invariant exists to prevent, just applied to a number instead of a
  quoted message.
- **"Operations Philosophy" bio section with a headshot** — **boundary ambiguity, not a clear
  reject.** This is the one idea from the ideation pass that wasn't classified as wrong, but as
  needing the user's explicit call — because it sits next to a real precedent (`decisions.md` #5:
  the "Role Fit" section was deliberately excluded as private positioning logic belonging in a
  separate workspace) without being identical to it. It's flagged in `ai-discussion-topics.md` as
  worth exploring further, not resolved here.

## Accessibility reasoning: why `role="alert"` was rejected for a quoted error message

It would be easy to assume a component displaying a validation *error* message should reuse
`BusinessErrorMessage`'s pattern, which does use `role="alert"`. That pattern exists for a specific
reason: `BusinessErrorMessage` announces something that just happened in response to a user action
(a failed upload, a failed report request) — a live event, where an assistive-technology user needs
to be interrupted and told about it immediately. `ValidationEvidence.tsx` quotes a *fixed, historical*
message as evidence — nothing is happening when the page loads; it's closer to a blockquote than a
notification. Marking static, decorative-in-timing content as `role="alert"` would make a screen
reader announce it unprompted on every page load, which is both inaccurate (nothing alerted) and
annoying (an unexpected interruption on a page that's supposed to be a calm, one-time read).

This connects to a pattern already established elsewhere: `PersistenceNotice` deliberately avoids
`BusinessErrorMessage`'s `role="alert"` treatment for the same underlying reason — a failed
best-effort save is a caveat, not an alert, so it gets a quieter treatment. The lesson generalizes:
`role="alert"`/`aria-live` should be reserved for content that becomes true *while the user is
present*, not content that's simply about an error (as a topic) but was already true when the page
rendered.

## Why the mobile header fix needed a specific pixel width, not just "mobile"

The first version of the `PublicHeader` fix said "hide the three anchor links below `sm`." That's a
real fix for the most visible problem, but it was accepted without checking whether what remained —
the full brand string, plus the "Open Dashboard" CTA, plus the existing `px-6` padding — would
actually fit in the narrowest realistic viewport. "Mobile" isn't one width; a fix that's fine at
390px (a common phone width) can still break at 320px (the classic small-device baseline, still
common enough to be worth checking explicitly). This is why the locked plan names 320px specifically
as a required verification width rather than leaving "mobile" as a vague target — a responsive fix
that hasn't been checked at its worst case hasn't actually been checked.

## Why this session ends before any code, and why that mattered here specifically

Plan mode's iterative correction loop caught three genuinely different classes of problem across
three rounds, not the same kind of issue restated three times:

- **Round 1** caught a *data integrity* gap — the single-row-vs-pair mistake, invisible unless you
  actually looked at how many times `SO-2026-010` appears in the source file.
- **Round 2** caught a *scope-locking* gap — decisions that sounded resolved ("source from
  mock-data") but still left an implementation-time choice hidden inside them (which file owns the
  selector constant; whether `TechnicalHighlight` extends `TechSection` "or similar").
- **Round 3** caught a *precision* gap — an invariant that was technically present but not tight
  enough ("fewer than two" instead of "exactly two"), and a responsive fix that was directionally
  right but not verified against its actual worst case.

None of these would have been caught by "does this plan look reasonable" — they required someone
reading closely enough to ask "wait, is that literally true" at three different levels of detail.
That's the actual value this session is documenting: not just *what* was decided, but that getting
from "a reasonable-sounding plan" to "a plan where every claim is exactly as strong as its
backing evidence" took deliberate, repeated scrutiny — it wasn't free, and it wasn't a single pass.
