# Decisions — Mobile Nav/Shell Responsiveness Pass

Architecture decisions from the `/architect` planning session for a narrow mobile nav/shell
responsiveness pass, fixing the Phase 10.2-flagged limitation where the fixed `w-60`
`SidebarNav` squeezed main content on mobile viewports. No workflow-page, table, dashboard,
or backend/API changes are in scope. Source: the planning conversation (initial code
exploration, AskUserQuestion rounds, a mid-session user clarification, and the user's five
plan-review corrections) — not the implementation, which happened after this session.

## 1. Breakpoint: `lg` (1024px), not `md` (768px)

**Decision:** The sidebar stays a fixed column at `lg` and above; below `lg` it becomes a
toggleable mobile drawer.

**How it works:** `lg` is Tailwind's default 1024px breakpoint. No custom breakpoints exist
in this project's `tailwind.config.ts`.

**Why this over the alternative:** The rest of the app already switches layout at `lg`
(workflow-page KPI summary grids use `lg:grid-cols-6/5/4`). Using the same breakpoint here
means a portrait tablet — which already gets "mobile-style" single-column KPI grids
elsewhere in the app — also gets the mobile nav treatment, rather than getting a fixed
sidebar squeezing content at exactly the width where other pages already conclude the
viewport is too narrow for the desktop layout. `md` (768px) was the alternative: it would
have confined the fix to phone-width viewports only, leaving portrait tablets with the
original squeezed-content bug this pass exists to fix.

## 2. New `--overlay` token, not a reuse of `--surface-inverse` inline

**Decision:** Add a new CSS custom property, `--overlay: 222 47% 11%`, exposed via
Tailwind as `overlay: "hsl(var(--overlay))"`, used at the drawer backdrop as `bg-overlay/50`.

**Why this over the alternative:** `ui-tokens.md` has a standing rule that no color token
gets added or reused in a new context without an explicit decision — this session **is**
that decision, made deliberately rather than skipped. The rejected alternative was a solid,
full-opacity backdrop reusing `bg-surface-inverse` directly with no new token: zero token
additions, but no dimming effect, fully blocking the page behind it rather than a
translucent scrim — a less common, less polished mobile-nav treatment. The chosen value is
numerically identical to `--surface-inverse`'s HSL triple (same palette, not a new hue)
but kept as a *separate* token so a future change to the sidebar's dark tone doesn't
silently also change the drawer backdrop's tone (or vice versa) through an undocumented
shared dependency.

**Cost of the alternative:** The solid-backdrop option would have avoided a token
addition entirely, at the cost of a distinctly less refined mobile UX (no visual sense
that the backdrop is a translucent overlay rather than an opaque wall).

## 3. Hand-rolled drawer, no headless dialog library

**Decision:** Build the drawer as a plain fixed-position `<div>`, no new dependency.

**Why this over the alternative:** This project has an established, explicit precedent of
hand-writing every UI primitive against its own token system rather than adopting a
component library — the same reasoning that kept shadcn's actual primitive components out
of the app back in Phase 8/9 (only `cn()`/`components.json`/deps were taken from shadcn's
setup, never its generated components), specifically because shadcn's default token names
collide with this project's own `ui-tokens.md` names. A headless dialog library like Radix
would have brought real value (built-in focus-trap, scroll-lock, Escape handling) but at
the cost of a new dependency and a required `context/library-docs.md` entry — more
footprint than a "narrow pass" fixing one specific, well-scoped layout bug calls for.

**Cost of the alternative:** Radix (or similar) would have made the accessibility
decisions in §5 below unnecessary to reason about by hand — but at the cost of introducing
this project's first UI dependency outside its own hand-written primitives, a bigger
architectural shift than the task warranted.

## 4. Two separate wrapper elements, conditionally mounted — not one dual-purpose `-translate-x-full` panel

**Decision:** `AppShell` renders two distinct elements around `SidebarNav`: an
always-mounted desktop wrapper (`hidden lg:block`), and a mobile drawer wrapper +
backdrop that are **only mounted in the DOM while `isDrawerOpen` is true** — not a single
wrapper that stays permanently mounted and toggles between `-translate-x-full` and
`translate-x-0`.

**Why this over the alternative:** This was a direct, required correction from the user's
plan review, not the original draft. The first draft of this plan proposed one wrapper,
always mounted, switching between off-canvas and on-canvas via a CSS transform — a common
pattern, but one with a known, real accessibility defect: `transform: translateX(-100%)`
moves an element off-screen visually but does **not** remove it from the keyboard tab
order. A keyboard-only user tabbing through the page would walk straight through every nav
link inside the "closed" drawer, since those links remain fully focusable even while
invisible off-screen. The user's review flagged this precisely and offered two acceptable
fixes: conditional rendering, or the `inert` HTML attribute (plus `aria-hidden`) applied
while closed. Conditional rendering was chosen as the simpler of the two — it needs no
extra attribute-toggling logic and, combined with the plan's separate "two wrappers, not
one" correction (below), maps naturally onto "the desktop wrapper is a completely different
element from the mobile wrapper" rather than one element trying to serve both roles.

**Cost of the alternative:** No animated slide-in/slide-out transition. Conditional
mounting means the drawer simply appears/disappears; a smooth bidirectional transition
would require additional mount-before-animate / delay-unmount-until-animation-ends timing
logic that this narrow pass deliberately left out of scope. The dimmed backdrop still
gives clear, immediate visual feedback without motion.

## 5. `TopHeader` and `AppShell` become Client Components — stated explicitly, not left implicit

**Decision:** Both `AppShell.tsx` and `TopHeader.tsx` get `"use client"` directives.

**Why this over the alternative:** `AppShell` needs `"use client"` because it now owns
`isDrawerOpen` state and calls hooks (`useState`, `useEffect`, `useRef`, `usePathname`) —
this was already an unavoidable, undisputed consequence of the design once state ownership
was decided. `TopHeader` is more subtle: technically, a component with no directive of its
own, imported and rendered directly inside an already-client module, is automatically part
of the client bundle without needing to redeclare `"use client"` itself. The user's review
still required the plan to say so explicitly — `TopHeader.tsx` now accepts an `onToggle`
callback prop and renders a real `onClick` handler, which is a genuine interactive
component regardless of the technical bundling mechanics, and the plan needed to name that
plainly rather than leave a future reader to work out why a "simple header" has an event
handler wired through it.

## 6. No `role="dialog"` / `aria-modal="true"` on the drawer, since there's no real focus trap

**Decision:** The mobile drawer wrapper gets no ARIA role beyond what `SidebarNav`'s own
internal `<nav>` element already provides. The toggle button gets `aria-expanded`,
`aria-controls="mobile-sidebar-drawer"`, and a state-dependent `aria-label`.

**Why this over the alternative:** This was the user's fifth and final review correction.
`role="dialog"` combined with `aria-modal="true"` is a specific promise to assistive
technology: that focus is contained inside the element while it's open, and the rest of
the page is effectively hidden from AT navigation until it closes. This implementation
does not enforce that — there is no focus trap, by explicit decision (see §3's rejected
Radix alternative) — so claiming modal semantics without backing them up would actively
mislead screen reader users about what the widget does. `SidebarNav`'s own `<nav>` landmark
already gives the drawer's contents a real, accurate semantic role; layering an inaccurate
`aria-modal` claim on top would be worse than adding no extra role at all.

**Cost of the alternative:** A keyboard or screen-reader user can, in principle, continue
navigating past the end of the drawer's links back into the page behind the backdrop while
the drawer is open. Accepted as a known, named scope boundary for this narrow pass rather
than solved with a full focus-trap implementation.

## 7. Learning docs required even though this isn't a numbered phase

**Decision:** `docs/plan/mobile-nav-shell-responsiveness/{plan,explanation,ai-discussion-topics}.md`
were written via `/feature-docs` immediately after implementation, and this
`docs/architect/mobile-nav-shell-responsiveness/` folder captures the planning session
itself — matching the repo's stated rule that every feature gets these docs, "even if not
a numbered phase."

**Why this over the alternative:** Earlier named, non-phase-numbered work in this project
(Sample Data Enrichment, the mock-data pipeline reconnection) set the precedent that a
piece of work doesn't need a "Phase N" slot in `context/build-plan.md` to warrant full
documentation — it only needs to be a real, discrete feature. This pass is tracked in
`context/progress-tracker.md` as a named entry rather than claiming the reserved Phase 12
slot (Postgres-backed dashboard), consistent with that precedent.
