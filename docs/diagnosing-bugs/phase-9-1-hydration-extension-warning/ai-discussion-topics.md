# AI Discussion Topics

## Hydration Mechanics

1. Why does React compare server-rendered HTML with the first client render during hydration?
2. What kinds of mismatches can React patch, and which mismatches does it deliberately leave alone?
3. Why can browser extensions create hydration warnings even when application code is deterministic?

## Scope Of The Fix

4. Why is suppressing the warning on `<body>` safer than disabling SSR for affected pages?
5. What would be risky about adding `suppressHydrationWarning` broadly across the app?
6. How can a developer tell whether a hydration warning is caused by app code or by an external DOM mutation?

## Next.js Root Layout

7. Why is `app/layout.tsx` the correct ownership boundary for `<html>` and `<body>` changes in the App Router?
8. What kinds of bugs should be fixed in route components instead of the root layout?
9. How does `next/font` affect production builds, and why can sandboxed builds fail when font fetching is blocked?

## Debugging Practice

10. What makes a browser-extension hydration bug hard to reproduce from a terminal-only feedback loop?
11. When is a captured browser overlay or screenshot strong enough evidence to guide a fix?
12. What additional check would you run in the affected browser to confirm the original warning is gone?
