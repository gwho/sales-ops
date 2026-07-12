# AI Discussion Topics — Feature mobile-nav-shell-responsiveness: Mobile Nav/Shell Responsiveness Pass

## Client Component boundaries

1. Walk through exactly why `AppShell` had to become a Client Component but the pages it wraps (like `/dashboard`) did not. What's the precise rule about passing `children` versus passing a function prop across that boundary?
2. `TopHeader` didn't strictly *need* its own `"use client"` directive to compile correctly (it's nested inside a client subtree either way) — so why was it added anyway? What would a future reader lose if it were omitted?
3. If a third component needed to read `isDrawerOpen` (say, a future breadcrumb bar), where would that logic go — prop drilling further, or lifting differently? What are the tradeoffs at this app's current size?

## The tab-order bug and its fix

4. Explain precisely why `transform: translateX(-100%)` hides an element visually but doesn't remove it from the tab order. What CSS property *would* remove it from the tab order without an actual DOM removal?
5. Conditional mounting was chosen over `inert` or a manually-managed `tabIndex={-1}`/`aria-hidden` toggle on a permanently-mounted drawer. Argue for the alternative — what would `inert` have bought here, and what would it have cost?
6. What would happen to this fix if `SidebarNav` ever became expensive to mount (e.g., it started fetching data on mount)? Would conditional mounting still be the right call, or would that change the calculus?

## The focus-management bug

7. Walk through, step by step, why pressing Tab once after opening the drawer via keyboard landed on "View all" inside `<main>` rather than a drawer link — name the exact DOM order involved.
8. The fix focuses the drawer's first `<a>` directly rather than the wrapper `<div>` with a `tabIndex={-1}`. What's the concrete, observable difference a user would notice between these two approaches?
9. This fix is explicitly not a focus trap. Describe exactly what a keyboard user can still do that a full focus trap would prevent — is that a real problem for this app's actual nav (5 items), or mostly theoretical?
10. If a future page adds a genuinely modal dialog (e.g., a delete-confirmation popup), should it reuse any part of this drawer's pattern, or does a true modal need a fundamentally different implementation? What would have to change?

## The `react-hooks/set-state-in-effect` lint rule

11. Walk through exactly why calling `setIsDrawerOpen(false)` inside a `useEffect` keyed on `pathname` causes an extra render pass, using the render/commit/effect timeline.
12. The render-time fix (`if (pathname !== drawerClosedForPathname) { ...; setIsDrawerOpen(false); }`) calls `setState` directly in the component body. Why doesn't this cause an infinite loop, and what would have to be true about the code for it to actually cause one?
13. Is `drawerClosedForPathname` an accurate name for what that state variable represents? What would you call it instead, and does the current name make the invariant (`pathname !== drawerClosedForPathname` implies "just navigated") easy or hard to see at a glance?

## Token discipline and scope boundaries

14. `--overlay` was given the exact same HSL triple as `--surface-inverse` rather than a new hue. What's the argument for keeping them numerically identical versus letting them diverge over time as separate, independently-tunable tokens?
15. `SidebarNav` was deliberately kept free of any mobile/desktop awareness. Construct the case for the opposite design (a `variant` prop) — under what future circumstance would that become the better tradeoff?
