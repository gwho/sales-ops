# Plan — Feature mobile-nav-shell-responsiveness: Mobile Nav/Shell Responsiveness Pass

## What was built

- `app/globals.css` — added `--overlay: 222 47% 11%;` to the `:root` token block, next to the existing Inverse Surface tokens.
- `tailwind.config.ts` — added `overlay: "hsl(var(--overlay))"` as a flat sibling color, exposing `bg-overlay` / `bg-overlay/50`.
- `components/layout/AppShell.tsx` — promoted from Server to Client Component. Added `isDrawerOpen` state; a render-time (not effect-based) reset of the drawer on route change; an `Escape`-key effect; a `drawerRef` + effect that focuses the drawer's first link on open; two separate sidebar wrappers (always-mounted desktop wrapper, conditionally-mounted mobile drawer + backdrop).
- `components/layout/TopHeader.tsx` — promoted from Server to Client Component. Added `{ isDrawerOpen, onToggle }` props and a new `lg:hidden` icon toggle button (`Menu`/`X` from `lucide-react`).
- `components/layout/SidebarNav.tsx` — **unchanged**. Reused as-is inside both wrappers.
- `context/ui-tokens.md` — documented the new `--overlay` token under a new "Overlay (Mobile Nav/Shell Responsiveness)" section.
- `context/ui-registry.md` — updated `AppShell`, `SidebarNav`, `TopHeader` entries; added a new "Page composition notes (Mobile Nav/Shell Responsiveness)" section; resolved the Phase 10.2 "known limitation, out of scope" note.
- `context/progress-tracker.md` — added a new named "Mobile Nav/Shell Responsiveness" checklist section and two Decisions Made entries; updated "Current Status" to reference it.

## Schema changes

None. No backend, API, or database changes — this is a frontend shell/layout change only.

## Key invariants

- **The mobile drawer wrapper and its backdrop must only ever be mounted in the DOM while `isDrawerOpen` is `true`.** Do not change this to a permanently-mounted element hidden via `-translate-x-full`, `hidden`, `opacity-0`, or any other visibility-only technique — a permanently-mounted drawer leaves its nav links in the keyboard tab order even while visually off-canvas, which was found and fixed as a real bug during this pass (see `explanation.md` §3).
- **`SidebarNav` itself must stay a single, unmodified component with no knowledge of mobile vs. desktop.** The responsive behavior lives entirely in `AppShell`'s two wrapper elements (`hidden lg:block` for desktop, conditional mount for mobile). Do not add a `variant` prop or breakpoint-aware logic to `SidebarNav` — that would duplicate what `AppShell` already handles and risk the two call sites drifting apart.
- **The drawer's route-change reset must stay a render-time state adjustment (`if (pathname !== drawerClosedForPathname) { ... }`), not a `useEffect`.** Putting `setIsDrawerOpen(false)` directly in an effect body triggers ESLint's `react-hooks/set-state-in-effect` rule (a real lint error encountered and fixed during this pass, not a style preference) and causes an avoidable extra render pass.
- **`--overlay` is scoped to drawer/modal backdrops only.** Do not reuse `bg-overlay` for any other surface without a new token-change decision, per `ui-tokens.md`'s existing token-discipline rule.
- **On open, focus must move into the drawer's first link (`drawerRef.current?.querySelector("a")?.focus()`), not just onto the drawer container.** Because the drawer is rendered before `TopHeader` in the DOM, a keyboard user tabbing forward from the header's toggle button would otherwise skip over the drawer entirely into `<main>` — a real bug found via the Playwright verification pass (see `explanation.md` §4). Removing this focus-management effect reintroduces that bug.
- **No `role="dialog"` / `aria-modal="true"` on the drawer wrapper**, since there is no real focus trap backing that claim — `SidebarNav`'s own `<nav>` landmark provides the real semantics. Do not add modal ARIA roles without also implementing an actual focus trap.
