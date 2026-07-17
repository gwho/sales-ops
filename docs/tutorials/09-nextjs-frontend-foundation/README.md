# Tutorial 09 — Next.js Frontend Foundation: Contracts → TypeScript → Generated JSON → Pages → Tokens

**After completing this tutorial you will understand:** why the Next.js scaffold was built in an
isolated scratchpad and transplanted rather than run directly at the repo root; how the App
Router's file-based routing convention turns a directory structure into a route table with no
separate routes file; why Tailwind was pinned to 3.4 and installed the "v3 way" instead of
accepting a v4 scaffold; how a color token travels from a CSS variable through
`tailwind.config.ts` to a compiled utility class actually rendered in a browser; why shadcn/ui
landed as plumbing only, with zero primitive components, because of one specific token-name
collision; and why the frontend's mock data is generated once, at build time, from the real
Python pipeline, and never imported at runtime.

> [!NOTE]
> **Prerequisites:** Tutorial 08 (`08-ui-contract-wireframe-planning/README.md`) — the direct
> predecessor. Every TypeScript type this tutorial cites was already fully explained there; this
> tutorial only covers what changed when that plan became real files. Track 5's three lessons —
> `docs/teach/lessons/0031-browser-output-and-components.html`,
> `0032-react-minimum-mental-model.html`, and `0033-server-and-client-components.html` — this
> tutorial is the first one that actually exercises L5.3's Server/Client Component rule against
> real files, not an invented example. Open
> [`app/layout.tsx`](../../../app/layout.tsx), [`app/globals.css`](../../../app/globals.css),
> [`tailwind.config.ts`](../../../tailwind.config.ts),
> [`types/index.ts`](../../../types/index.ts),
> [`scripts/generate_mock_data.py`](../../../scripts/generate_mock_data.py),
> [`lib/mock-data.ts`](../../../lib/mock-data.ts),
> [`lib/utils.ts`](../../../lib/utils.ts), and
> [`components.json`](../../../components.json) alongside this tutorial.

> [!NOTE]
> **A caveat about the current codebase, worth stating once, up front:** this repository is now
> post-Phase-12, and Phase 8's own route files no longer exist in their original form — they were
> stub Server Components (a title, a "Phase 9 builds this" note, a link back to `/dashboard`), and
> every one of them was replaced with real, live, data-wired pages in later phases. This tutorial
> never reconstructs those deleted stubs; it describes their historical role from
> `docs/plan/phase-8-nextjs-frontend-foundation/plan.md` in prose only, and cites verbatim code
> only from files that are still genuinely stable: `app/layout.tsx`, `app/globals.css`,
> `tailwind.config.ts`, `types/index.ts`, and the mock-data pipeline. One further wrinkle, also
> worth naming directly: at the time of writing, this repository's working tree also holds
> **uncommitted, in-progress work** restructuring `app/` into `(public)`/`(workspace)` route
> groups with a new marketing landing page. That work is real but unfinished — this tutorial
> deliberately cites the last **committed** state of every file (`git show HEAD:<path>`, not the
> working tree), because an in-progress refactor is not yet the "current stable foundation" this
> tutorial's brief asks for. If you open these files yourself and see a different `app/` layout
> than what's shown here, that uncommitted work is why.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Isolate-then-transplant (staging area) | Scaffolding into `<scratchpad>/next-scaffold`, then copying only vetted files into the real repo root | System design |
| Convention-over-configuration routing | The App Router's directory structure — `app/dashboard/page.tsx` *is* the `/dashboard` route, with no separate route table to maintain | System design |
| Indirection via named variables | `--accent` (CSS custom property) → `hsl(var(--accent))` (Tailwind config) → `bg-accent` (utility class) — one value, renamed once, used everywhere | Design patterns |
| Build-time code generation vs. runtime coupling | `scripts/generate_mock_data.py` runs once, writes static JSON; nothing under `app/`/`components/`/`lib/*.ts` ever imports Python at runtime | System design |
| Module search path (`sys.path`) for a standalone script | `sys.path.insert(0, str(ROOT))` in `generate_mock_data.py` — resolving `src.*` imports for a script run directly, outside pytest's own path setup | OS fundamentals |

## How to use an LLM before this tutorial

### Concept 1 — Scaffolding a new tool inside an existing, non-empty project

> "A code-generation tool (a framework scaffolder, a project template CLI) is designed to run in
> an empty directory and will overwrite or create files with common names (`README.md`,
> `.gitignore`, config files) without checking what's already there. Explain a safe way to use such
> a tool inside a project that already has real content at those same paths. Quiz me on what
> specifically could go wrong if you skipped the safety step and ran the tool directly at the
> project root."

*What to listen for:* the safe pattern is to run the generator somewhere isolated (a scratch
directory, a temp folder), inspect exactly what it produced, and then deliberately copy over only
the files that are genuinely new additions — never blindly overlay the generator's output onto a
directory that already has its own versions of the same filenames.

*Practice question:* if a scaffolding tool and an existing project both want to own a file called
`.gitignore`, what does "isolate, inspect, then selectively merge" actually mean for that one file
specifically — copy, don't copy, or something else?

### Concept 2 — File-based routing as convention over configuration

> "Explain 'convention over configuration' as a design philosophy, contrasted with an explicit
> configuration file (like a `routes.json` or a `urls.py` list) that maps URL paths to handlers by
> hand. Using a file-based router as the example (a framework where a file's location in a folder
> tree determines its URL), explain the concrete productivity trade-off: what do you gain, and
> what do you lose the ability to do easily? Quiz me on how you'd add a genuinely non-standard
> route (say, one with a dynamic, deeply nested segment) under a pure convention-based system."

*What to listen for:* convention over configuration removes an entire category of file (the
explicit route table) and an entire category of bug (a route registered but the handler file
missing, or vice versa) — the trade-off is that anything the convention *can't* express cleanly
(highly dynamic or computed routing logic) has to be bent into the folder-naming convention itself
rather than written as arbitrary code in one central place.

*Practice question:* under a pure file-based router, if you delete a page file, does the
corresponding route still exist?

### Concept 3 — CSS custom properties as a single point of truth for a design value

> "Explain why a CSS custom property (`--accent: #1a56db;` referenced everywhere as
> `var(--accent)`) is preferable to hardcoding the same color value directly in every rule that
> needs it. Walk through exactly what has to change, and where, to update the color under each
> approach. Quiz me on what happens if two developers, unaware of each other, hardcode the 'same'
> brand color slightly differently (say, one off-by-one RGB value) across a codebase with no
> shared variable."

*What to listen for:* a custom property collapses "every place this color is used" down to one
place that actually defines the value — changing it once changes every consumer automatically.
Hardcoding the same value repeatedly means every occurrence is an independent, unenforced promise
that they all currently agree, a promise that silently breaks the moment any one of them is edited
without the others.

*Practice question:* if a brand color needs to change from blue to green, how many files change
under a custom-property system versus a system where the color was pasted as a literal hex value
in fifteen different component files?

### Concept 4 — Generating data at build time instead of coupling two runtimes together

> "Two systems, written in different languages, need to share the same data. Compare two designs:
> (A) the consuming system calls the producing system live, at runtime, every time it needs the
> data; (B) the producing system's output is captured once, ahead of time, as a static file the
> consuming system reads with no live dependency on the producer at all. Give a concrete reason
> design (B) is often preferred when the producing system's runtime isn't available in the
> consuming system's deployment environment. Quiz me on what design (B) can't do that design (A)
> can."

*What to listen for:* design (B) means the consuming system has zero runtime dependency on the
producing system's language, interpreter, or libraries even existing in its own deployment
environment — genuinely useful when, say, a JavaScript frontend's hosting environment has no
Python runtime at all. The cost: design (B)'s data is only ever as fresh as the last time it was
regenerated — it can't reflect something that changed in the producer *after* the static file was
last written, the way a live call always would.

*Practice question:* if the underlying Python business rules change tomorrow, does design (B)'s
already-generated JSON file automatically reflect that change the next time someone loads the
frontend?

### Concept 5 — A module search path, and why a standalone script needs one set up explicitly

> "Explain what a language's 'module search path' is (Python's `sys.path`, Node's
> `node_modules` resolution, etc.) — the ordered list of places an interpreter looks when you
> write `import something`. Explain why a test runner (like pytest) often configures this path
> automatically for you, but a script you run directly with `python some_script.py` might not have
> the same path set up, especially if the script needs to import code from a parent directory.
> Quiz me on what error you'd see if a script imported a package that wasn't anywhere on its
> search path."

*What to listen for:* a test runner like pytest typically discovers the project root itself (via a
config file or its own root-finding heuristics) and adds it to the search path before running any
test — a plain script invoked directly gets none of that automatic setup, so if it needs to import
something from a location that isn't already on the default search path, the script itself has to
add that location before the import statement runs.

*Practice question:* if a script at `scripts/generate_mock_data.py` tries to
`from src.inventory_allocation import allocate_inventory` without first adding the repository root
to its search path, what specific error would Python raise?

## Architecture overview

Tutorial 08 (Phase 7) produced a plan with no runnable code behind it. Phase 8 is where that plan
becomes a real, buildable Next.js application — still with almost no real UI logic (that's
Tutorials 10–11), but every piece of *plumbing* the real pages will eventually stand on:

```text
   context/ui-contract-plan.md          sample_data/*.xlsx (real, committed fictional data)
   (Phase 7's TypeScript block,               │
    route plan, token references)             ▼
              │                    src/order_validation.py, inventory_allocation.py,
              │ copied verbatim              payment_aging.py, report_export.py
              ▼                               │  (the SAME tested pipeline every
        types/index.ts                        │   real upload would run)
    (13 contract types + 3 envelopes,          ▼
     snake_case, no adapter)         scripts/generate_mock_data.py
              │                      (manual, build-time only —
              │ imported by type-only            │  `uv run python scripts/generate_mock_data.py`
              ▼                      or `npm run mock-data`)
        lib/mock-data.ts                        │
    (asserts raw JSON against                   ▼
     types/index.ts, ONE place)      lib/mock-data/*.json  (committed output —
              │                       order-validation, inventory-allocation,
              │  imported by pages/components   payment-aging, reports)
              ▼                                 │
     (Tutorials 10-11's real pages) ◄────────────┘

   ── in parallel, the visual/token half ──

   context/ui-tokens.md  (authoritative token source)
              │  copied verbatim (HSL channel triples)
              ▼
   app/globals.css  :root { --accent: 221 83% 53%; ... }
              │  read by
              ▼
   tailwind.config.ts   colors.accent.DEFAULT = "hsl(var(--accent))"
              │  generates
              ▼
   compiled utility classes (bg-accent, text-text-primary, ...)
              │  used by
              ▼
   app/layout.tsx, app/page.tsx, and every stub page — Server Components,
   no "use client" anywhere in Phase 8 (nothing needs state or a browser API yet)
```

Key invariants for this phase:

1. **The Next.js app must never import from `tests/` at runtime.** The build-time generator is the
   only sanctioned bridge between Python and the frontend, and only at build/dev time (Part 7).
2. **`context/ui-tokens.md` is the single authoritative token set.** Nothing in
   `tailwind.config.ts` or `app/globals.css` may add, rename, or invent a color token without a
   dedicated token-change decision (Part 4).
3. **Tailwind stays on 3.4.x, installed the v3 way.** No `@import "tailwindcss"`, no `@theme`
   block, no v4 CSS-first config (Part 3).

## Part 1 — Scaffold beside Python without clobbering the repo

The repo root, before Phase 8, was not empty — it held the entire Python project (`src/`,
`tests/`, `pyproject.toml`, `uv.lock`), the whole `context/` design system, and — critically — the
real `AGENTS.md`, `CLAUDE.md`, `README.md`, and `.gitignore` files every workflow in this project
depends on. `docs/plan/phase-8-nextjs-frontend-foundation/explanation.md` §1 names exactly what
`create-next-app` would have done if run directly at that root: Next 16's scaffold ships its own
agent-guidance files, and running the generator there would have produced its own `AGENTS.md` and
`CLAUDE.md` — silently overwriting the project's authoritative guidance with generic Next.js
boilerplate.

The actual sequence: scaffold into `<scratchpad>/next-scaffold`, inspect what it produced, then
copy only the genuinely Next.js-specific files to the real root — `app/`, `public/`,
`next.config.ts`, `next-env.d.ts`, `tsconfig.json`, `eslint.config.mjs`, `package.json` —
deliberately leaving behind the generated `AGENTS.md`, `CLAUDE.md`, `README.md`, `.git`,
`node_modules`, `.next`, and `package-lock.json`. `.gitignore` (open the current file,
[`.gitignore`](../../../.gitignore) lines 1–25) was merged by hand rather than copied wholesale —
line 8's own comment marks exactly where the Next.js/Node section was appended:

```gitignore
# --- Next.js / Node (Phase 8) ---
/node_modules
/.pnp
.pnp.*
/.next/
/out/
/build
/coverage
...
.env*
!.env.example
.vercel
*.tsbuildinfo
next-env.d.ts
```

The Python ignore rules that already existed above this section (not shown here — open the file
directly) survived completely untouched; the two rule sets now coexist in one file because the
merge was done by a human reading both sides, not by letting one generator's output replace the
other's.

> **System design — Isolate-then-transplant (staging area):** Scaffolding into an isolated
> location, inspecting the output, then selectively copying only the vetted parts into a live
> system is the same general shape as any staging environment, a git worktree used to test a risky
> change, or a build artifact promoted from a clean-room build server into production only after
> review. The core idea: never let an automated tool write directly into a system whose existing
> state you can't afford to silently lose.

**Checkpoint:** `create-next-app` generated its own `AGENTS.md` and `CLAUDE.md`. If those had
overwritten the real ones at the root, what specifically would have broken in later sessions — and
would `git` have made it obvious, or silently staged the clobbered versions?

<details>
<summary>Reveal answer</summary>

Every later session's very first instruction is to read `CLAUDE.md`/`AGENTS.md` for project
guidance (this project's own `CLAUDE.md` states this explicitly) — a session that instead read
Next.js's generic scaffold guidance would have no idea about the Python-first sequencing decision,
the Field Scope Boundary, the Scope Gate, or any of this project's actual rules, and would likely
start inventing scope the project explicitly forbids. `git` would **not** make this obvious by
itself — `git status`/`git diff` would show a real, valid-looking modification to both files, with
no automatic flag that the new content came from an unrelated tool rather than a deliberate edit;
a reviewer would have to actually read the diff and recognize the content was wrong, which is
exactly the kind of mistake easy to wave through in a large, busy diff.
</details>

**Checkpoint:** The `.gitignore` was merged by hand rather than copied. Walk through what would
have gone wrong if Next's `.gitignore` had simply replaced the Python one. Which ignore rules from
each side had to coexist?

<details>
<summary>Reveal answer</summary>

A straight replacement would have dropped every Python-specific ignore rule (things like
`__pycache__/`, `.venv/`, `*.pyc` — not shown in the excerpt above, but present earlier in the real
file) the moment the Next.js section was copied in, meaning the next `git add` would start
accidentally staging Python build artifacts and virtual environment files that were previously,
correctly, invisible to git. The two rule sets that had to coexist: Python's own ignores (already
present) and the new Next.js/Node section (`/node_modules`, `/.next/`, `.env*`, `next-env.d.ts`,
etc.) — genuinely unrelated rule sets serving two different toolchains in the same repository, with
no overlap and no conflict, but only if both are kept rather than one replacing the other.
</details>

**Checkpoint:** `next-env.d.ts` is gitignored (per Next's convention) yet required for types. How
is it regenerated, and why is it safe to not commit it? What generates it if a fresh clone runs
`tsc` before `next dev`?

<details>
<summary>Reveal answer</summary>

Next.js itself regenerates `next-env.d.ts` automatically, the moment either `next dev` or
`next build` runs — it's a small, fully-deterministic file (a couple of triple-slash type
references) that Next writes fresh every time, never hand-edited by a developer. It's safe to not
commit precisely because of that determinism: any machine with the same Next.js version installed
will regenerate byte-for-byte the same file, so committing it would only add a file that changes
on every install without ever representing a real, reviewable decision. If a fresh clone somehow
ran `tsc` (a raw TypeScript check) *before* ever running `next dev`/`next build` at least once, the
file would be genuinely missing and the type check would likely fail on the missing triple-slash
reference — in practice this doesn't happen because `npm install`/`next dev` are always the first
commands run against a freshly cloned Next.js project.
</details>

**Checkpoint:** What is the exact list of files that were deliberately *not* transplanted from the
scaffold, and why was each one excluded?

<details>
<summary>Reveal answer</summary>

`AGENTS.md`, `CLAUDE.md`, and `README.md` — excluded because the real root already has
authoritative versions of all three, and Next's generated versions would have silently replaced
project-specific guidance with generic scaffold text (the exact failure this Part opens with).
`.git` — excluded because the scratchpad scaffold has its own throwaway git history that has
nothing to do with this project's real commit history; transplanting it would have meant two
unrelated repositories fighting over one `.git` directory. `node_modules` and `.next` — excluded
because both are large, fully regeneratable build/dependency artifacts (`npm install` and
`next build` recreate them from `package.json`/source respectively); committing or transplanting
either would bloat the transplant for zero benefit. `package-lock.json` — excluded specifically
because the scaffold's own lockfile reflects whatever dependency versions `create-next-app`
happened to resolve at scaffold time (including Tailwind v4, before the deliberate v3 downgrade in
Part 3) — the real lockfile needed to be generated fresh, after the real `package.json` was
finalized with the correct pinned versions.
</details>

**Try it yourself:** Run `git log --oneline -- .gitignore | tail -5` from the repo root and find
the commit that first added the "Next.js / Node (Phase 8)" section. Read that commit's diff
(`git show <hash> -- .gitignore`) and confirm the Python-specific ignore rules above that section
are untouched lines, not re-added ones — direct proof the merge preserved rather than replaced them.

## Part 2 — App Router structure and the root redirect

Open [`app/layout.tsx`](../../../app/layout.tsx) (the current, committed file — note this already
includes a Phase 9 addition, `AppShell`, called out below):

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

import { AppShell } from "@/components/layout/AppShell";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sales Admin Automation Toolkit",
  description:
    "Order validation, inventory allocation, payment aging, and report export dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body
        className="min-h-screen bg-background font-sans text-text-primary"
        suppressHydrationWarning
      >
        <AppShell>{children}</AppShell>
      </body>
    </html>
  )
}
```

`AppShell` (the `import` on line 5) is a **Tutorial 10 (Phase 9) addition** — Phase 8's original
root layout rendered `{children}` directly inside `<body>`, with no shell component at all, since
nothing to shell around existed yet (every route was still a stub). It's left in place here,
labeled, rather than reconstructed as it looked in Phase 8, per this tutorial's own caveat about
not recreating deleted stub-era code. What Phase 8 *did* originate, and what's still true today: no
`"use client"` directive anywhere in this file. Per L5.3
(`docs/teach/lessons/0033-server-and-client-components.html`), that makes `RootLayout` a Server
Component by default — it runs on the server, needs no state, no event handlers, and no browser-only
API, so there was never a reason to opt it into the client bundle.

Now open [`app/page.tsx`](../../../app/page.tsx) (again, the current committed root — a separate,
uncommitted restructuring exists in the working tree, per this tutorial's opening caveat):

```tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
}
```

The root route (`/`) exists purely to forward to `/dashboard` — `explanation.md` §5 states the
reasoning plainly: `/dashboard` is the intended landing surface, so the bare root just redirects
rather than duplicating dashboard content at two URLs. Per the App Router's file convention (the
Next.js docs installed at
`node_modules/next/dist/docs/01-app/01-getting-started/03-layouts-and-pages.md`), a `page.tsx` file
inside a folder makes that folder's path publicly routable — `app/dashboard/page.tsx` is
`/dashboard`, `app/reports/page.tsx` is `/reports`, with no separate routes file anywhere declaring
this mapping. It's the same file-based routing convention L5.1's browser-fundamentals lesson
gestures at generally, now a concrete, working mechanism.

> **System design — Convention over configuration:** A file's *location* in the `app/` tree is the
> entire specification of its URL — there is no `routes.ts` or `urls.py`-style manifest anywhere in
> this project mapping paths to handlers by hand. This buys the property Part 1's "how is
> `next-env.d.ts` regenerated" checkpoint touched on from a different angle: nothing can drift out
> of sync between "the routes that exist" and "the routes a separate config file claims exist,"
> because there is only one source of truth, the folder structure itself. The cost, not exercised
> in this project's fixed 5-route set: a URL scheme too dynamic or computed to express as folder
> names has to be bent into the convention's own escape hatches (dynamic segments, route groups)
> rather than written as arbitrary routing logic in one place.

Phase 8's five workflow routes (`app/dashboard/page.tsx` through `app/reports/page.tsx`, per
`plan.md`'s "What was built" list) were, at the time, genuinely minimal: `plan.md` describes each
as "stub Server Components: title + 'Phase 9 builds this' note + back-to-dashboard link," each
carrying "a header comment naming the contract/components Phase 9 will build there." None of that
stub content survives today — every one of those five routes is now a live, data-wired page
(Tutorial 10 and later cover what replaced them) — but the *convention* those stubs first
established (a Server Component, real semantic-token classes instead of placeholder markup, one
file per route) is exactly what Part 4 and later tutorials build on.

**Checkpoint:** The stub pages used real semantic token classes instead of placeholder markup. Why
was that a deliberate verification choice rather than over-engineering a stub?

<details>
<summary>Reveal answer</summary>

A stub page using literal placeholder text and inline styles would compile and render, but would
prove nothing about whether the token pipeline (`ui-tokens.md` → `globals.css` →
`tailwind.config.ts` → compiled classes) actually works end to end — it would only prove Next.js
itself is running. Using real classes like `bg-surface`, `text-text-primary`, and
`hover:border-accent` on stub content that will be thrown away anyway costs nothing extra to write,
and turns every stub page into a genuine, if minimal, test of the exact pipeline Part 4 covers —
`explanation.md` §6 confirms this is exactly how it was used: the stub pages' rendered HTML and
compiled CSS were grepped for these specific classes as part of verification, not decoration.
</details>

**Checkpoint:** Root `app/page.tsx` uses `redirect("/dashboard")`. What are the trade-offs versus
making `/` itself the dashboard, and does the redirect opt the route out of static prerendering?

<details>
<summary>Reveal answer</summary>

Making `/` itself the dashboard would mean the dashboard's content lives at two conceptual
identities (the literal root, and a named `/dashboard` path) with no canonical URL — anything
linking to "the dashboard" specifically would have to choose one path or the other, and any future
route that isn't the dashboard but also wants "the root" (a marketing page, for instance — exactly
what the uncommitted working-tree restructuring mentioned in this tutorial's caveat is building)
would have nowhere to go without moving the dashboard's real content off the root first. A
server-side `redirect()` call does make the route dynamic rather than a static, prerenderable
page — Next.js can't prerender a page whose entire body is "immediately redirect elsewhere" the
same way it prerenders genuinely static content, since the redirect itself is a runtime response
action, not static markup to cache.
</details>

**Try it yourself:** Run
`uv run python -c "print('n/a — this is a Next.js check, run the command below instead')"` — then
actually run `npm run build` from the repo root (or `npx next build` if that script isn't defined)
and read the route table Next.js prints at the end. Confirm `/` is marked with a redirect-related
indicator (Next's build output distinguishes static, dynamic, and redirect-driving routes) rather
than appearing as a fully static prerendered route.

## Part 3 — Tailwind 3.4 as a deliberate compatibility boundary

Open [`context/library-docs.md`](../../../context/library-docs.md) lines 108–117:

```markdown
## Tailwind CSS 3.4

The future Next.js UI must use Tailwind CSS 3.4. Do not upgrade to Tailwind v4.

Rules:

- Define project colors as CSS variables and expose them through `tailwind.config.ts`.
- Components must use semantic project tokens, not raw Tailwind palette classes.
- No hardcoded hex values in JSX.
- Use consistent spacing, radius, and status tokens from `ui-tokens.md`.
```

This rule predates Phase 8 by several planning sessions, but Phase 8 is the first phase that had
to actually satisfy it against a real scaffolding tool's defaults. `explanation.md` §2 names the
concrete friction: `create-next-app@latest` (which produced Next 16.2.10 here) defaults its
`--tailwind` flag to **v4** — and Tailwind v4 isn't a newer version of the same configuration
system, it's a different one. v4 is CSS-first (`@import "tailwindcss"`, `@theme` blocks,
`@tailwindcss/postcss`), has no `tailwind.config.ts` by default, and doesn't read a v3-style JS
config unless explicitly told to.

**Checkpoint:** Why is downgrading a v4 scaffold to v3 harder than scaffolding with
`--no-tailwind` and adding v3 manually? Name the concrete v4-vs-v3 differences that make it messy.

<details>
<summary>Reveal answer</summary>

Downgrading an already-scaffolded v4 project means *undoing* a whole parallel wiring scheme before
building the v3 one: removing the `@tailwindcss/postcss` PostCSS plugin, removing `@import
"tailwindcss"` and any `@theme` blocks from the generated CSS, and only then adding v3's
`tailwindcss`/`postcss`/`autoprefixer` packages, a `postcss.config.mjs`, `@tailwind` directives,
and a `tailwind.config.ts` from scratch — two full configuration systems briefly coexisting and
needing careful untangling. Scaffolding with `--no-tailwind` skips the whole v4 setup from the
start, so there's nothing to undo — the v3 path documented in the installed Next.js docs
(`node_modules/next/dist/docs/01-app/02-guides/tailwind-v3-css.md`) is added once, cleanly, onto a
project that never had any Tailwind wiring to begin with.
</details>

The actual verification, per `explanation.md` §2, checked two separate places, not one:

**Checkpoint:** The verification checked "package.json AND lockfile are 3.4.x" and that
`@tailwindcss/postcss` is absent. Why check the lockfile separately from `package.json` — what
could `package.json` alone hide?

<details>
<summary>Reveal answer</summary>

`package.json`'s dependency line for Tailwind (confirmed in the real file: `"tailwindcss":
"^3.4.17"`) declares an *acceptable range*, not the exact version actually installed — the caret
(`^`) permits any 3.x release compatible with 3.4.17. `package-lock.json` records the *exact
resolved version* that `npm install` actually put in `node_modules` (this is the same lockfile
concept Tutorial 01's Part 7 covered for `uv.lock` — a manifest states a range, a lockfile freezes
one specific resolution). Checking only `package.json` could miss a scenario where the lockfile
somehow resolved to an unexpected version still nominally inside the stated range, or — more to the
point here — checking only the manifest wouldn't prove Tailwind v4's marker package
(`@tailwindcss/postcss`) is genuinely absent from what's actually installed, since a stray v4
dependency could in principle be pulled in transitively without `package.json` itself naming it
directly.
</details>

> **System design — Reproducible builds via lockfiles, revisited:** Tutorial 01 covered this exact
> idea for `uv.lock`; `package-lock.json` plays the identical role for the Node/npm side of this
> project. A project committing both lockfiles is stating the same thing twice, once per
> toolchain: "every reviewer who runs the install command gets the exact bytes this was built and
> tested against," not just something inside a declared version range.

**Try it yourself:** Run `npm ls tailwindcss` from the repo root and confirm the resolved version
starts with `3.4`. Then run `grep -r "tailwindcss/postcss" package-lock.json` and confirm zero
matches — direct, current proof that no v4 marker package has crept into the dependency tree since
Phase 8.

## Part 4 — The semantic-token pipeline

Open [`app/globals.css`](../../../app/globals.css) lines 1–20 and
[`tailwind.config.ts`](../../../tailwind.config.ts) lines 19–40:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/*
 * Design tokens — the authoritative project token set (context/ui-tokens.md).
 * HSL channel triples, consumed as hsl(var(--token)) via tailwind.config.ts.
 * Light theme only. Do not add or rename tokens without a token-change decision.
 */
:root {
  --background: 210 40% 98%;
  --surface: 0 0% 100%;
  ...
  --accent: 221 83% 53%;
  --accent-hover: 224 76% 48%;
  --accent-subtle: 214 100% 97%;
  ...
}
```

```ts
theme: {
  extend: {
    colors: {
      background: "hsl(var(--background))",
      surface: {
        DEFAULT: "hsl(var(--surface))",
        muted: "hsl(var(--surface-muted))",
        subtle: "hsl(var(--surface-subtle))",
      },
      ...
      accent: {
        DEFAULT: "hsl(var(--accent))",
        hover: "hsl(var(--accent-hover))",
        subtle: "hsl(var(--accent-subtle))",
      },
      ...
    },
  },
},
```

Three files, one value, chained: `--accent: 221 83% 53%;` is declared exactly once, in
`globals.css`'s `:root` block, copied verbatim from `context/ui-tokens.md`. `tailwind.config.ts`
never hardcodes a color — every entry in `theme.extend.colors` is `hsl(var(--some-token))`,
referencing the CSS variable by name rather than restating its value. A component then writes
`className="bg-accent"`, and Tailwind's build step generates the compiled CSS rule connecting that
class name to the `hsl(var(--accent))` expression, which the browser resolves against whatever
`--accent` currently equals.

**Checkpoint:** The tokens are stored as HSL channel triples (`221 83% 53%`) and consumed as
`hsl(var(--accent))`. Why store them channel-only instead of as full `hsl(...)` strings? What
would break in the Tailwind config if they were stored as full color strings?

<details>
<summary>Reveal answer</summary>

Storing only the channel numbers (hue, saturation, lightness — no function wrapper) lets Tailwind
apply an *opacity modifier* at the point of use, e.g. `bg-accent/50` for 50% opacity — Tailwind
generates that by wrapping the stored channels in `hsl(var(--accent) / 50%)` at build time. If
`--accent` instead held a complete string like `hsl(221 83% 53%)`, wrapping it again inside another
`hsl(...)` call (`hsl(hsl(221 83% 53%) / 50%)`) would be invalid CSS — the opacity-modifier feature
depends specifically on the variable holding *only* the raw channel values, ready to be wrapped by
whatever function and modifier the utility class needs at generation time.
</details>

**Checkpoint:** `tailwind.config.ts` uses `theme.extend.colors` rather than replacing the palette.
What does that choice mean for whether `bg-blue-600` still works, and does that undermine the "no
raw palette classes" rule? Where is that rule actually enforced?

<details>
<summary>Reveal answer</summary>

`extend` *adds* the project's semantic color names alongside Tailwind's full built-in palette
rather than replacing it — so `bg-blue-600` remains a perfectly valid, compilable Tailwind class
after this config, exactly as if the `extend` block didn't exist. This does mean the "no raw
palette classes" rule from `library-docs.md`/`CLAUDE.md` is **not** enforced by the Tailwind config
itself — nothing in `tailwind.config.ts` makes `bg-blue-600` fail to compile. The rule is enforced
entirely by process discipline (code review, and this project's own documented conventions) rather
than by a build-time mechanism — a real, named gap worth recognizing rather than assuming a linter
or config setting silently blocks it, since none currently does.
</details>

> **Design patterns — Indirection via named variables:** This three-file chain
> (`globals.css` → `tailwind.config.ts` → compiled class) is one concrete instance of a level of
> indirection: instead of every consumer of "the accent color" holding its own copy of the literal
> value, every consumer holds a *name*, and exactly one place resolves that name to a value. This
> is the same principle behind a compiler's symbol table, a spreadsheet's named ranges, or a DNS
> record — changing what a name *points to* is one edit, versus finding and editing every direct
> reference to the old value.

**Try it yourself:** Run `npm run build`, then find the compiled CSS output under `.next/static/`
(the exact path depends on the build hash — `find .next/static -name "*.css"` will locate it).
Grep it for `--accent:221` (minified output has no space after the colon) and separately for
`.bg-accent` — confirm both the raw variable definition and the compiled utility class are present
in the same file, closing the loop this Part describes.

## Part 5 — Why shadcn remained plumbing-only

Open [`components.json`](../../../components.json) and [`lib/utils.ts`](../../../lib/utils.ts) in
full — both are short enough to read completely:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge conditional + conflicting Tailwind class names (shadcn/ui convention). */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

The approved plan for this phase listed "shadcn init + add button/card/table/badge/input/select
primitives" — and that step could not be executed as written. `explanation.md` §3 names the exact
conflict, discovered only once `ui-tokens.md`'s real token names were checked against shadcn's own
conventions: this project's `--accent` is the brand **blue** (`221 83% 53%`); shadcn/ui's own
`--accent` token means something entirely different — a **subtle gray hover background**. Dropping
a shadcn `button.tsx` in as-is would either render unstyled (its expected tokens don't exist in
this config) or force adding shadcn's parallel token set into `tailwind.config.ts`, at which point
`colors.accent` would need two contradictory definitions in the same file.

**Checkpoint:** Explain the `--accent` collision precisely: what does `--accent` mean in
`ui-tokens.md` versus in shadcn, and what would render wrong if both definitions landed in
`colors.accent`?

<details>
<summary>Reveal answer</summary>

`ui-tokens.md`'s `--accent` is the project's primary brand color — a saturated blue meant for
primary buttons, active nav items, and other "this is the main call to action" surfaces. shadcn's
`--accent` is a low-emphasis neutral, typically a light gray, meant for subtle hover states on
otherwise plain elements (a menu item's hover background, for instance) — visually and semantically
the near-opposite of a brand color. If both definitions coexisted in `tailwind.config.ts`'s
`colors.accent`, only one could actually win at the `accent` key — the last one merged, or a build
error if the config tooling refuses ambiguous duplicate keys — meaning either every "primary brand
action" surface would render as a washed-out gray, or every shadcn-generated subtle hover surface
would render as a jarring, unintended blue, depending on which definition happened to survive.
</details>

**Checkpoint:** The `tokens-no-modification` skill rule is tagged CRITICAL. Why did that rule
convert "should we add shadcn primitives now?" from a judgment call into a near-mechanical "no"?
What would selecting the other option have counted as?

<details>
<summary>Reveal answer</summary>

A CRITICAL-tagged rule ("Never Modify Design Tokens... without explicit approval") removes the
question "is this specific token change acceptable, this one time" from ordinary engineering
judgment and turns it into a hard gate requiring a dedicated, separate approval step before
proceeding — exactly the same posture `CLAUDE.md`'s Scope Gate takes toward V1.5/V2 spec rules
(Tutorial 04's IA-007 discussion covered the identical mechanism, applied to business rules instead
of design tokens). Adding shadcn's primitives as originally planned, which would have required
adding shadcn's own `--accent`/`--primary`/`--destructive` tokens to make the components render
correctly, would have counted as exactly the forbidden action the rule names — an unreviewed
token-set modification — regardless of how reasonable it might have seemed as a one-off convenience
in the moment.
</details>

**Checkpoint:** Phase 9 will add shadcn primitives "reconciled to `ui-tokens.md`." Concretely, what
does reconciling a shadcn `button.tsx` involve — which classes get rewritten, and to what?

<details>
<summary>Reveal answer</summary>

Reconciling means taking a shadcn-generated component's source and replacing every one of its own
token-class references (`bg-primary`, `text-primary-foreground`, `hover:bg-accent`, `border-input`,
and similar) with this project's real semantic classes (`bg-accent`, `text-text-on-accent`,
`hover:bg-accent-hover`, `border-border`) — keeping the component's actual structure, variant
logic, and accessibility behavior intact, while swapping every color/token reference to point at
`ui-tokens.md`'s real token set instead of shadcn's own assumed one. Tutorial 10 covers this
happening for real, against `components/ui/Button.tsx`.
</details>

**Checkpoint:** `components.json` still declares `baseColor: slate` and `cssVariables: true`. When
Phase 9 runs `shadcn add button`, what will it generate, and why is that a Phase 9 problem rather
than a Phase 8 one?

<details>
<summary>Reveal answer</summary>

Running the shadcn CLI with this config will generate a `button.tsx` written against shadcn's own
`slate`-based token set — the exact same `--primary`/`--accent`/`--destructive` vocabulary this
Part's whole discussion is about, since `components.json` only configures *how* shadcn generates
code (style, aliases, whether it expects CSS variables), not *which* project-specific tokens it
should target instead, because shadcn has no concept of a project's own custom token names. It's a
Phase 9 problem rather than a Phase 8 one because Phase 8 never actually runs `shadcn add` for any
component — `components.json` exists purely as configuration, unused until the first real `add`
command runs, which this phase deliberately deferred.
</details>

**Checkpoint:** The main `skills/tailwind/SKILL.md` was read and then disregarded. Why was it the
wrong skill for this project, and what would have gone wrong if its v4 guidance had been followed?

<details>
<summary>Reveal answer</summary>

That skill's actual content turned out to be written for a different runtime context entirely —
HyperFrames/Tailwind-v4-browser-runtime guidance, not a Next.js project using a committed
`tailwind.config.js` and `@tailwind` directives. Following its v4-oriented guidance in this project
would have meant reintroducing exactly the CSS-first, `@theme`-block configuration style Part 3
deliberately avoided — the wrong tool for a project whose `library-docs.md` explicitly pins
Tailwind 3.4 and forbids v4. Recognizing a skill's guidance doesn't match the actual project
context, and disregarding it in favor of the skills that do apply
(`tailwind-configuration`/token rules), is itself a skill worth naming: reading a resource
critically rather than applying it just because it exists and has "tailwind" in its name.
</details>

**Try it yourself:** Run `grep -rn "shadcn" package.json` and confirm no shadcn *component*
package is a runtime dependency — only `clsx`, `tailwind-merge`, `class-variance-authority`, and
`lucide-react` (the plumbing) should appear, no actual `shadcn/ui` component package, since shadcn
components are copied into the repo as source, not installed from npm.

## Part 6 — One contract shape across Python and TypeScript

Open [`types/index.ts`](../../../types/index.ts) lines 1–9 and 108–118:

```ts
/**
 * Output-contract types for the Sales Admin Automation Toolkit UI.
 *
 * Copied verbatim from context/ui-contract-plan.md, which is the source of
 * truth (mirroring src/contracts.py + the three business-module result
 * envelopes). snake_case field names are intentional — they match the JSON the
 * Python core emits. No camelCase adapter (decided in Phase 7); if that changes,
 * update ui-contract-plan.md first, then regenerate this file.
 */
```

```ts
export type PaymentAgingSummary = {
  total_invoices: number;
  total_outstanding_amount: number;
  overdue_amount: number;
  high_priority_count: number;
  // Always has all 5 keys, even when a bucket has zero rows.
  aging_bucket_counts: Record<
    "Current" | "1-30 Days" | "31-60 Days" | "61-90 Days" | "90+ Days",
    number
  >;
};
```

Tutorial 08 covered why `context/ui-contract-plan.md`'s TypeScript block mirrors `src/contracts.py`
field-for-field, with no camelCase translation — this file is that decision's second application,
not a new one. `types/index.ts` isn't independently authored against the Python source; its own
docstring says plainly it's "copied verbatim from `context/ui-contract-plan.md`," which is itself
already the mirror. This is a deliberate single-direction chain (Python → planning doc → TypeScript
file), not three independent transcriptions of the same source that could each drift differently.

**Checkpoint:** If `src/contracts.py` gains a new field tomorrow, what is the exact ordered
sequence of edits/regenerations needed to keep `contracts.py`, `ui-contract-plan.md`,
`types/index.ts`, and `lib/mock-data/*.json` consistent?

<details>
<summary>Reveal answer</summary>

In order: (1) the Python change lands in `src/contracts.py` (and whatever business-module function
actually computes the new field's value); (2) `context/ui-contract-plan.md`'s TypeScript block is
updated to add the mirrored field, following Tutorial 08's field-name/optionality discipline; (3)
`types/index.ts` is updated to match — since it's a verbatim copy of step 2, this is a mechanical
sync, not independent design work; (4) `uv run python scripts/generate_mock_data.py` (or
`npm run mock-data`) is re-run, regenerating every `lib/mock-data/*.json` file from the real,
now-updated Python pipeline, so the committed mock data actually contains the new field's real
computed values. Skipping step 4 specifically would leave `types/index.ts` claiming a field exists
that the actual committed JSON doesn't contain — a real runtime mismatch, since nothing type-checks
JSON *content* against a TypeScript type at build time, only the `as Type` assertion in
`lib/mock-data.ts` (Part 7) which trusts the cast rather than verifying it.
</details>

**Try it yourself:** Open `context/ui-contract-plan.md` and `types/index.ts` side by side. Pick any
one contract (e.g. `SupplierFollowUpRow`) and confirm every field, including optionality markers
(`?`), matches exactly between the two files — direct, current proof the "copied verbatim" claim in
`types/index.ts`'s own docstring holds.

## Part 7 — Build-time fixture bridge, never a runtime test import

Open [`scripts/generate_mock_data.py`](../../../scripts/generate_mock_data.py) lines 1–19 and
44–56:

```python
"""Generate the Next.js UI's mock JSON from the committed sample Excel data.

BUILD-TIME ONLY, MANUAL. This is the single sanctioned place where the frontend's
mock data is produced. The Next.js app itself must never import from `sample_data/`
or `src/` at runtime — it reads the committed JSON emitted here into `lib/mock-data/`.

This script loads `sample_data/*.xlsx` through each business module's own `load_*`
helper and runs the real `validate_orders` -> `allocate_inventory` ->
`calculate_payment_aging` -> `report_export` pipeline, the same code path a real
upload would exercise. Because of that, a failure here is a genuine compatibility
signal, not just a data-generation bug...
"""
```

```python
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.inventory_allocation import allocate_inventory, load_inventory  # noqa: E402
from src.order_validation import load_orders, load_product_master, validate_orders  # noqa: E402
from src.payment_aging import calculate_payment_aging, load_invoices  # noqa: E402
```

**A necessary correction before going further:** `explanation.md` §4 (written during Phase 8
itself) describes this script as importing `tests.contract_fixtures` — a small, single-row,
hand-authored fixture set — and calls the resulting mock envelopes "intentionally small," single
rows "enough to prove the shape end to end, not a full demo dataset." That was accurate *at the
time Phase 8 shipped*. The real, current file (shown above) does something different: it reads the
real, richer `sample_data/*.xlsx` files and runs them through the actual business-rule pipeline —
`validate_orders` → `allocate_inventory` → `calculate_payment_aging` → the report exporters — the
exact code path a real upload would exercise. This changed in a later, separate commit
(`745ac10`, "feat: enrich sample Excel data and regenerate UI mock JSON"), after Phase 8 ended.
The committed `lib/mock-data/*.json` today reflects this: `order-validation.json` alone carries 28
valid orders and 12 errors, not one row of each.

What didn't change: the invariant this Part is actually about. `tests/contract_fixtures.py` is
still real, still exists, and is still used — but only by `tests/test_contracts.py` and
`tests/test_report_export.py`, entirely separate from this script and from anything the frontend
reads. The two data sources serve genuinely different jobs (Tutorial 02's demo-fixture-vs-test-
fixture distinction, applied here at the mock-data-generator level): `contract_fixtures.py` proves
contract *shape*; `sample_data/*.xlsx` run through the real pipeline proves the frontend has
*realistic, rule-computed* data to build against.

**Checkpoint:** Why is "the app must never import `tests/` at runtime" an invariant rather than a
style preference? What are the two distinct problems it prevents?

<details>
<summary>Reveal answer</summary>

First, coupling: a shipped, deployed Next.js application importing from a `tests/` directory would
mean production code depends on test-only infrastructure that has no reason to exist in a
deployment artifact — bloating the bundle with code (and potentially Python interop machinery) that
serves no runtime purpose. Second, and more fundamental: there is no live bridge between a running
Next.js server/browser and a Python process at all in this project's architecture — "importing
`tests/` at runtime" isn't just discouraged, it's not even mechanically possible without inventing
an entirely new cross-language runtime dependency this project has never needed. The invariant
names the second, deeper fact as a rule precisely so no future contributor tries to solve a data
problem by inventing that dependency instead of regenerating the static JSON.
</details>

**Checkpoint:** `scripts/generate_mock_data.py` inserts the repo root on `sys.path`. Why is that
necessary for a standalone script when the pytest suite imports `tests.contract_fixtures` without
it?

<details>
<summary>Reveal answer</summary>

pytest performs its own project-root discovery (via `pyproject.toml`/`pytest.ini`/its own
heuristics) and adds the discovered root to `sys.path` automatically before collecting and running
any test — this is built-in pytest behavior a test file never has to set up itself. A script
invoked directly with `uv run python scripts/generate_mock_data.py` gets none of that automatic
setup: Python's default module search path for a directly-run script includes the script's own
directory (`scripts/`) but not automatically the repository root one level up, so
`from src.inventory_allocation import ...` would fail with `ModuleNotFoundError: No module named
'src'` unless the script explicitly adds the root itself, which is exactly what
`sys.path.insert(0, str(ROOT))` does before any `src.*` import runs.
</details>

**Checkpoint:** The mock envelopes were originally described as "intentionally small." What was
the actual source of that smallness at the time, and what changed to produce today's richer
dataset?

<details>
<summary>Reveal answer</summary>

At the time Phase 8 shipped, the script imported `tests/contract_fixtures.py` — a fixture set
containing exactly one hand-authored example row per contract family, by design (Tutorial 08's Part
1 already covered why: these fixtures exist to prove a shape can hold believable data, not to be a
demo dataset). "Small" was a direct, mechanical consequence of the single-row source, not a
deliberate frontend-sizing decision. The later `745ac10` commit changed the *source* entirely —
swapping `tests/contract_fixtures.py` for the real `sample_data/*.xlsx` files run through the
actual business-rule pipeline — which is why today's `order-validation.json` has 28 valid orders
instead of 1: the smallness was always a property of which upstream data the script happened to
read, not of the script's own logic.
</details>

**Checkpoint:** Walk through how sourcing `reports.json` from a real pipeline run (rather than
hand-writing it) protects against reintroducing the stale `report_id` drift Tutorial 08 Part 7
covered.

<details>
<summary>Reveal answer</summary>

Tutorial 08 Part 7 covered a real bug: `tests/contract_fixtures.py`'s hand-authored
`REPORT_MANIFEST_FIXTURES` once had a `report_id` format that didn't match what
`_build_manifest()` actually produces. `generate_mock_data.py` never hand-writes a `report_id`
anywhere — it calls the real `export_order_validation_report()`/`export_inventory_allocation_report()`/
`export_payment_aging_report()` functions directly (lines 89–97) and writes whatever
`ReportManifest` those functions actually return. Since the `report_id` string is constructed
entirely inside `_build_manifest()` (`src/report_export.py`), and this script never re-derives or
re-types that string itself, there is no code path here that *could* reintroduce a stale, hand-typed
format — the mock data is correct by construction, inheriting whatever the real exporter does,
automatically, forever, rather than needing to be kept in sync by a human remembering to match it.
</details>

Open [`lib/mock-data.ts`](../../../lib/mock-data.ts) lines 1–20 as the final stop this data
actually reaches:

```ts
/**
 * Typed access point for the build-time mock JSON.
 *
 * Pages import from here, never from `lib/mock-data/*.json` directly, so the
 * JSON shape is asserted against `types/index.ts` in exactly one place...
 */

import orderValidationData from "@/lib/mock-data/order-validation.json";
...
import type {
  OrderValidationResult,
  InventoryAllocationResult,
  PaymentAgingResult,
  PaymentAgingRow,
  ReportManifest,
} from "@/types";

export const orderValidationResult = orderValidationData as OrderValidationResult;
```

This file is itself a **Tutorial 10 (Phase 9) addition** — Phase 8 wrote the JSON generator and
the committed JSON files, but nothing yet consumed them; there were no non-stub pages to import
into. It's shown here anyway, labeled, because it's the natural final link in this Part's chain: raw
JSON becomes a typed constant in exactly one file, and every future page imports the typed constant,
never the raw JSON path directly — the same "one assertion boundary" principle Tutorial 10 will
cover in full.

**Try it yourself:** Run `uv run python scripts/generate_mock_data.py` yourself (safe — it only
overwrites `lib/mock-data/*.json` with output computed the same way the committed version already
was) and read the four `wrote ...` lines it prints. Then run `git diff --stat lib/mock-data/` and
confirm either no changes (the pipeline is deterministic, per `MOCK_AS_OF_DATE`/`MOCK_GENERATED_AT`
being fixed constants) or a diff you can explain — direct proof the committed JSON really is this
script's exact, reproducible output.

## Part 8 — Verification beyond compilation

`explanation.md` §6 opens with the reasoning this whole Part is organized around: "'It compiled' is
weaker than 'the tokens actually render.'" `next build` succeeding proves the TypeScript and JSX
are syntactically valid and every import resolves — it says nothing about whether a browser
actually shows `bg-accent` as the intended blue, or whether the server can actually route to every
page. Verification went further, in a specific order: the production server was started on a spare
port, and every route was curled directly — the root returned 200 after following the redirect,
and all five workflow stub routes returned 200. The dashboard's returned HTML was then grepped and
confirmed to contain the real semantic-token classes (`bg-surface`, `text-text-primary`,
`border-border`, `hover:border-accent`), not raw palette classes.

**Checkpoint:** Verification grepped the built CSS on disk for both `:root` variables and compiled
utility classes. Why are both halves necessary — what failure would show up in one but not the
other?

<details>
<summary>Reveal answer</summary>

Grepping only for the `:root` variable definitions (`--accent:221 83% 53%`) would prove
`globals.css` itself compiled and its variable declarations survived the build — but it says
nothing about whether `tailwind.config.ts` correctly wired any utility class to actually *reference*
that variable; a misconfigured `theme.extend.colors` entry (a typo'd variable name, a missing
`hsl()` wrapper) could leave the variable defined but genuinely unused by any generated class.
Grepping only for the compiled utility classes (`.bg-accent`) would prove Tailwind generated
*some* rule for that class name, but not whether the rule's actual value resolves correctly — a
class could exist and compile to `background-color: hsl(var(--totally-wrong-variable))` and this
check alone wouldn't catch it. Checking both, and confirming they reference the same variable name,
is what actually closes the loop end to end, the same "don't trust one half of a chain to prove the
whole chain" reasoning Tutorial 06 Part 6 used for save/reload round-trip verification versus
inspecting an in-memory object.
</details>

> **OS fundamentals — Testing a live process versus inspecting a build artifact:** Curling a
> running production server and grepping the built CSS on disk are two different verification
> techniques with different blind spots — a running server proves the whole request/response cycle
> genuinely works (routing, middleware, actual HTTP responses), while grepping the static build
> output proves something is present in the compiled artifact independent of whether a server is
> even running at the time. `explanation.md` notes the built-CSS grep was actually the *more*
> reliable check once the server was stopped — a static artifact doesn't go away when a process
> exits, and doesn't require a spare port or cleanup the way a live server check does.

**Try it yourself:** Run `npm run typecheck` (the `tsc --noEmit` script `explanation.md` notes was
added to `package.json` specifically because the scaffold provided none) and confirm it passes
under strict mode. Then run `npm run lint` and confirm it's clean — `explanation.md` notes the one
warning this phase actually caught and fixed (`postcss.config.mjs`'s anonymous default export,
resolved by assigning the config object to a `const` first, visible in the current file).

## A short note on the Figma reference inspection

Not one of the eight numbered Parts above, because — per `explanation.md` §7 — this work changed
no Phase 8 code at all. Worth covering briefly anyway, since three of this tutorial's 24 discussion
questions concern it directly.

This session was the first with the Figma MCP server connected. Four Figma Make prototype links
were inspected, and — as expected of AI-generated prototypes — they drifted from the real
contracts in specific, catalogued ways: a `Critical | High | Medium | Low` priority vocabulary
where the real one is `High | Normal | Low`; `Invalid SKU` treated as an allocation *status* value,
when the real `AllocationResultRow.status` has exactly three values and an invalid SKU never
reaches allocation at all (it's caught upstream by rule OV-003, Tutorial 03); a stated $40,000
high-priority payment threshold where the real rule (`payment_aging.py`) is $50,000; an 8-item
ERP-style mega-nav where the real route set is the fixed five this tutorial's Part 2 covers.

**Checkpoint:** The Figma prototypes put `Invalid SKU` in the allocation status column. Explain why
that is contract-wrong and where an invalid SKU is actually handled in the pipeline.

<details>
<summary>Reveal answer</summary>

`AllocationResultRow.status` (`src/contracts.py`, Tutorial 08 Part 2) has exactly three real
values: `Fully Allocated`, `Partially Allocated`, `Backordered` — there is no fourth value for an
invalid SKU, because an order line with an invalid SKU never reaches `allocate_inventory()` at
all. Tutorial 03 covered rule OV-003: `validate_orders()` catches an unknown or inactive SKU during
*order validation*, before Phase 4's allocation step ever runs, and a row that fails any Error-level
rule is excluded from `valid_orders` — the only input `allocate_inventory()` ever receives. Placing
"Invalid SKU" in the *allocation* status column conflates two entirely separate pipeline stages, the
same kind of stage-conflation mistake Tutorial 04's Part 2 already named as a real risk.
</details>

**Checkpoint:** The Figma reconciliation "changed no Phase 8 code." Why capture it now at all, and
what concrete Phase 9 mistake does the documented reconciliation prevent?

<details>
<summary>Reveal answer</summary>

Capturing it now, while the inspection is fresh, means Phase 9 builds from an already-corrected
classification instead of a developer re-discovering (or worse, missing) each of these drifts
independently while under the pressure of actually writing component code. The concrete mistake
this prevents: without the documented reconciliation, a Phase 9 developer skimming the Figma
prototype for layout inspiration could easily copy a `Critical` priority tag, a $40,000 threshold
label, or an `Invalid SKU` status badge directly into real component code, each one silently wrong
against the actual Python contracts — exactly the invented-label failure mode Tutorial 08 Part 4's
whole Status Badges discussion exists to prevent, just arriving via a new source (an AI-generated
mockup) instead of an old hand-written guidance folder.
</details>

**Checkpoint:** Only the Dashboard prototype used the mandated sidebar; the others used top-nav
plus a stepper, or a bare top bar. Why did the sidebar decision win uniformly, and what parts of the
non-sidebar prototypes are still usable?

<details>
<summary>Reveal answer</summary>

`context/ui-rules.md`'s sidebar-navigation mandate predates all four prototypes and was never a
Figma-derived decision to begin with — it's an existing, settled project convention, so a Figma
prototype disagreeing with it is the prototype being wrong, not new evidence to weigh. The
resolution: `AppShell`/`SidebarNav` (Tutorial 10) applies uniformly across all five real routes,
regardless of what chrome any individual prototype happened to use. What's still usable from the
non-sidebar prototypes is their *content* patterns, independent of chrome — the stepper component's
visual treatment, the filter-bar layout, the upload-panel affordance — Figma's *layout vocabulary*
for these pieces informs Phase 9's components even though its *navigation chrome* is discarded
outright.
</details>

## Full data flow: one contract field, from `src/contracts.py` to a typed frontend import

1. **The field is defined.** `src/contracts.py`'s `PaymentAgingRow` declares
   `follow_up_priority: str` (Tutorial 08 Part 2 covered why this is a plain `str`, not a stricter
   Python type).
2. **The field is planned and narrowed into TypeScript.**
   `context/ui-contract-plan.md`'s `PaymentAgingRow` block types the same field as
   `"High" | "Medium" | "Low" | "Watch" | "None"` — a stricter union type than the Python source,
   derived by reading `_follow_up_priority()`'s actual logic (Tutorial 08 Part 2).
3. **The field is copied verbatim into a real, buildable TypeScript file.**
   `types/index.ts:130`: the identical union type, inside the identical `PaymentAgingRow` shape —
   this tutorial's Part 6, the first time this exact field exists as code Next.js will actually
   compile, not just planning-document prose.
4. **The field's real values are computed and written to disk.**
   `scripts/generate_mock_data.py` (Part 7) runs `calculate_payment_aging()` against
   `sample_data/sample_invoices.xlsx` and writes every resulting row — including its real,
   rule-computed `follow_up_priority` — into `lib/mock-data/payment-aging.json`.
5. **The field reaches a typed constant a real page can import.**
   `lib/mock-data.ts:26`: `export const paymentAgingResult = paymentAgingData as PaymentAgingResult;`
   — the JSON's `follow_up_priority` string values are now typed, at this one boundary, against the
   exact union type step 3 declared.

Every one of these five steps already exists as real, committed, current code — nothing in this
trace is hypothetical or planning-only, unlike Tutorial 08's equivalent trace, which stopped at
planning documents because Phase 7 built no code at all. Tutorial 10 picks up exactly here: what
actually reads `paymentAgingResult` and renders a `StatusBadge` from its `follow_up_priority`
field.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Prove the token pipeline for `bg-surface` from CSS variable to
compiled utility use, the same way Part 4 traced `bg-accent`. Write out, in order: the `:root`
declaration in `app/globals.css`, the `tailwind.config.ts` entry that maps `surface` to it, and one
real file under `app/` or `components/` that actually uses the `bg-surface` class (search for it).
Confirm the class exists in the compiled CSS output the same way Part 4's "Try it yourself" did for
`bg-accent`.

<details>
<summary>Hint</summary>

`surface` in `tailwind.config.ts` is a nested object (`DEFAULT`/`muted`/`subtle`), not a single
value — make sure your trace picks the right one (`bg-surface` maps to the `DEFAULT` key
specifically, `bg-surface-muted` to a different one) and doesn't conflate the three.
</details>

**Challenge 2 — Extend** (20–30 min): Add a type-only example field on paper — don't edit the real
contract — say, a hypothetical `currency: string` field added to `PaymentAgingRow`. List, in the
exact order Part 6's checkpoint established, every file that would need a coordinated edit, and
what specifically changes in each: `src/contracts.py`, `src/payment_aging.py` (to actually compute
and populate the value), `context/ui-contract-plan.md`, `types/index.ts`, and the regeneration
command that would need to run afterward. Do not actually make any of these edits.

<details>
<summary>Hint</summary>

Don't forget the business-module function itself — a new field on the `TypedDict` alone doesn't
make any Python code actually populate it; `calculate_payment_aging()`'s row-building dict literal
would need the new key added too, or every real row would silently be missing it despite the type
now claiming it's required.
</details>

**Challenge 3 — Break and fix / Design** (30–45 min): Explain, concretely, what `create-next-app`
run directly at the repo root (skipping Part 1's scratchpad-and-transplant step entirely) could
have overwritten. Then design a preflight check — a script, a pre-command checklist, anything
concrete — that would catch this risk *before* the scaffolding command runs, not after. Your design
should specifically address: what files does it check for, and what does it do if one of them
already exists at the target path.

<details>
<summary>Hint</summary>

The real risk isn't every file `create-next-app` writes — most of them (`app/`, `next.config.ts`)
are genuinely new additions with no pre-existing collision. The risk is narrowly the small set of
filenames Part 1's own "Try it yourself" and checkpoints already named: `AGENTS.md`, `CLAUDE.md`,
`README.md`, and `.gitignore`. A preflight design only needs to check for pre-existing files at
exactly those paths, not attempt to guard every file the scaffolder might ever write.
</details>

For deeper exploration,
`docs/plan/phase-8-nextjs-frontend-foundation/ai-discussion-topics.md` has all 24 prompts this
tutorial's checkpoints were woven from, organized under their original five headings (scaffold
safety, the Tailwind v3 pin, the shadcn token collision, mock data and the test-import boundary,
and routing/verification/Figma). Feed them to an LLM *after* forming your own answer first — the
gap between what you thought and what you learn is where understanding lands.
