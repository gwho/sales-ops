# Discussion — Mobile Nav/Shell Responsiveness Pass

A full teaching record of the `/architect` planning session for the mobile nav/shell
responsiveness pass — what was explored, what was proposed, what the user corrected, and
the reasoning behind each turn. This is the deepest of the three session-docs files; where
`decisions.md` states the outcome and the winning argument, this file walks through the
alternatives, the wrong turns, and the "why" in more expansive form.

## 1. Why the initial exploration skipped the Explore subagent

The `/architect` skill's own Phase 1 guidance says to launch Explore subagents for
"broad codebase exploration ... uncertain scope." This session deliberately used direct
`Read`/`Bash grep` calls instead, on the grounds that the scope was already narrow and
concretely named: the user's own request specified "the fixed sidebar," "a mobile header
menu button," and "the existing SidebarNav route list" — which map onto exactly three
known files (`components/layout/AppShell.tsx`, `SidebarNav.tsx`, `TopHeader.tsx`), a known
token file (`context/ui-tokens.md`), and a known config file (`tailwind.config.ts`). This
matches the skill's own stated exception: "Use 1 agent when the task is isolated to known
files... you're making a small targeted change." Spawning a fresh agent to re-derive
context already available (memory of the Phase 10.2 session, which had already named this
exact limitation) would have been strictly slower with no compensating benefit — this is
the same reasoning documented generally in this environment's guidance against spawning
subagents when a task doesn't need parallelized or context-isolated work.

What the direct reads turned up, efficiently, was the exact shape of the problem:
`AppShell.tsx` was a Server Component composing a fixed-width `SidebarNav` with no
responsive behavior at all; `context/ui-registry.md` already had this named as a known,
explicitly-deferred limitation from Phase 10.2 ("the sidebar has no responsive
collapse/drawer behavior... would need its own planning decision") — meaning this session
existed specifically to resolve a debt the project had already, deliberately, chosen not
to pay down earlier. Reading `components/ui/Button.tsx` and `tailwind.config.ts` also
surfaced that `lucide-react` was already a dependency (used for `SidebarNav`'s per-item
icons since Phase 10.2), meaning a `Menu`/`X` toggle icon needed no new package — a small
but real point in favor of the "no new dependency" drawer-build decision made later.

## 2. Language alignment: making the ambiguous terms explicit before proposing anything

Before any implementation questions, the session presented four term definitions back to
the user for confirmation: "desktop breakpoint," "hide the fixed sidebar" (specifically:
*removed from layout flow*, not just dimmed or visually hidden), "drawer/overlay" (the
*same* `SidebarNav` component reused inside an off-canvas panel, not a rebuilt nav list),
and "mobile header menu button" (a new icon toggle in `TopHeader`, visible only below the
desktop breakpoint). None of these were corrected by the user in this round — but stating
them explicitly mattered anyway, because "hide the sidebar" is genuinely ambiguous between
"visually hidden but still taking up layout space" (which would leave main content
squeezed even with the sidebar invisible) and "removed from flow entirely" (which is what
actually fixes the reported bug). Naming this distinction up front meant the later
implementation could be checked against an explicit, agreed definition rather than an
assumed one.

## 3. The three AskUserQuestion decisions and the reasoning behind each

**Breakpoint (`lg` vs `md`).** The case for `lg` wasn't just "pick the existing value" —
it was specifically that the app's own workflow pages already treat sub-`lg` widths as
needing a different, more compact layout (their KPI summary grids collapse below
`lg:grid-cols-*`). Using a different, narrower breakpoint for the *navigation* shell than
for the *content* layout would create an inconsistent-feeling middle band of viewport
widths (roughly 768–1023px) where content already looks "mobile" but navigation still
looks "desktop" — the fixed sidebar squeezing a content area that's already rendering as
if it expects to be narrow. The user's own reasoning, given when confirming this choice,
converged on the same point independently: "if you use `md / 768px`, an iPad-sized
portrait viewport can still get the fixed `w-60` sidebar plus compressed content, which is
the issue we're trying to remove."

**The `--overlay` token.** This is a case where the `/architect` session did real,
substantive design-system work, not just implementation sequencing. `ui-tokens.md`'s
"no new token without an explicit decision" rule exists so that every color in the app has
a documented, single reason to exist and a documented scope — the alternative (an inline
opacity modifier on an existing token, or worse, a raw Tailwind color class) would have
been faster to write but would have silently violated that rule and left a future reader
unable to answer "where did this color come from and what else depends on it?" without
grepping the whole codebase. The user's own framing, when making this decision, named the
principle plainly: "a drawer backdrop is a real surface state, and using a token is
cleaner than hardcoding opacity behavior in one component."

**Drawer build (hand-rolled vs. a headless library).** This decision connects to a
pattern already established twice in this project's history: Phase 8 kept shadcn to
"plumbing only" (`cn()`, `components.json`, dependencies) specifically because shadcn's
generated components carry their own default token names that collide with this project's
`ui-tokens.md` names, and Phase 9 then hand-wrote every primitive component rather than
generating them. A headless dialog library like Radix doesn't have that specific
token-collision problem (it's usually unstyled), but it does add a new dependency and a
`context/library-docs.md` obligation for what is, in the end, a five-link navigation
drawer — not a complex, deeply nested modal system where a library's battle-tested
focus-trap and scroll-lock machinery would clearly pay for its own weight.

## 4. The mid-session clarification: "make the sidebar toggle on/off... you can suggest the best modern approach"

After the plan file was first drafted (still using the single-wrapper,
`-translate-x-full`-based design at that point) and before `ExitPlanMode` was called, the
user sent a message mid-turn confirming the general direction — a toggleable sidebar via a
modern approach — without yet raising the specific accessibility objections that came in
the full review round afterward. This message functioned as confirmation of the overall
shape (hamburger-toggles-drawer, the same pattern used by GitHub mobile, Vercel's own
dashboard, Linear, and effectively every responsive admin shell built in the last several
years) rather than a request to reconsider the approach entirely. It's a useful example of
how a mid-turn message during an agent's tool-call sequence can serve as an early,
partial confirmation that gets refined further once the user actually reads the full
drafted plan — the deeper corrections (tab-order, ARIA claims, wrapper structure) arrived
only once the complete plan file existed for the user to review end to end.

## 5. The plan-review round: five corrections, and why each one mattered more than it might look

When `ExitPlanMode` was called, the user did not approve the first draft outright — they
rejected it with five required modifications, all incorporated before re-submitting. This
is worth walking through in the order the user gave them, since each one reveals something
about what a "narrow pass" plan can silently get wrong if nobody stress-tests it:

**"Create the docs/plan folder... even if not a numbered phase."** The first draft's plan
file didn't mention writing `/feature-docs` output at all, because the work wasn't being
tracked as a numbered "Phase." The user's correction generalizes a rule that had only been
followed by convention before (Sample Data Enrichment and the mock-data pipeline
reconnection got full docs without phase numbers) into an explicit, stated requirement:
"this is still a feature." The user additionally specified *which* topics `explanation.md`
had to teach — not just "write docs," but named the five specific things (why `AppShell`
becomes client, why `TopHeader` also does, how the breakpoint mechanism works, why
`--overlay` exists, how close behavior works) that a future reader would most need
explained rather than left to infer from the diff alone.

**"Closed drawer must not be keyboard-tabbable... do not rely on `-translate-x-full`
alone."** This is the single most substantive technical correction in the round. The
first draft's design — one wrapper, permanently mounted, sliding via CSS transform — is a
genuinely common pattern that looks completely correct to a sighted reviewer testing with
a mouse. The user's objection named the exact, specific failure mode (offscreen content
remaining in the tab order) and offered two concrete acceptable fixes rather than leaving
the direction open-ended: conditional rendering, or `inert`/`aria-hidden`. This is a useful
example of catching an accessibility bug *before* any code existed, purely by someone with
the right knowledge reviewing a written plan — the same class of bug that later, during
implementation, still needed a second, related fix (the focus-management issue documented
in the feature-docs `explanation.md`) once the conditionally-mounted version was actually
built and tested with Playwright. Catching the *first* half of this problem at plan-review
time didn't guarantee the *second* half (focus entry point) would be caught without
runtime testing — which is exactly what happened.

**"Clarify TopHeader becomes a Client Component."** Technically, as discussed in
`decisions.md` §5, this wasn't strictly required for the code to compile — a component
without its own directive, rendered inside an already-client module, still ends up in the
client bundle. The user's correction wasn't about correctness; it was about the plan
document's clarity for a future reader, who shouldn't have to trace the React Server
Components' module-boundary rules by hand to understand why a "just a header" component
has an `onClick` handler in it.

**"Use separate desktop/mobile wrappers if simpler."** This correction and the tab-order
correction reinforce each other: the user's suggested restructuring (two separate wrapper
elements, each independently reusing `SidebarNav`) turned out to be the natural, clean way
to implement "conditionally render the mobile drawer only when open" — trying to keep one
wrapper that both toggles fixed/relative positioning at `lg` *and* toggles mounted/unmounted
below `lg` would have made the conditional-rendering logic considerably harder to reason
about than two independent, simpler elements each handling exactly one job.

**"Add minimal accessibility roles... avoid claiming full modal behavior unless you
implement a real focus trap."** This correction operates at a different level from the
others — it's not about what to build, but about not *overclaiming* what was built. The
instinct to reach for `role="dialog"`/`aria-modal="true"` on anything that looks like an
off-canvas panel is common, and it would have made the plan look more "complete" on paper.
The user's objection is really a principle about honesty in accessibility semantics: an
ARIA attribute is a promise to assistive technology, and a promise the implementation
doesn't keep (no focus trap) is actively worse than making no promise at all, since it sets
an incorrect expectation rather than an absent one.

## 6. What this session illustrates about `/architect`'s value beyond "write a todo list"

Two of these five corrections (the tab-order fix and the ARIA-claims fix) are genuine
accessibility bugs that would have shipped invisibly to anyone testing with a mouse and a
sighted eye — exactly the population most likely to review a pull request for this kind of
change. Both were caught from a written plan, before any code existed, by a reviewer
applying real domain knowledge about how off-screen CSS positioning interacts with the
accessibility tree, and about what ARIA attributes actually promise. This is the core
value proposition of a planning session that produces a reviewable artifact (the plan
file) rather than jumping straight to code: a plan can be stress-tested for problems that
are much cheaper to name in prose than to discover later via a failing Playwright
assertion — which is exactly what happened next, when the *other* half of the same
underlying problem (focus entering the drawer correctly on open) only surfaced once the
implementation was actually run through a keyboard-only verification pass.
