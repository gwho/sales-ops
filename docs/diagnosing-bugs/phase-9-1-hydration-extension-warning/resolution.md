# Hydration Extension Warning Resolution

## Change made

`app/layout.tsx` now adds `suppressHydrationWarning` to the root `<body>` element:

```tsx
<body
  className="min-h-screen bg-background font-sans text-text-primary"
  suppressHydrationWarning
>
  <AppShell>{children}</AppShell>
</body>
```

## Why this fix is appropriate

The warning was caused by attributes added outside the app before hydration. The app cannot prevent the browser extension from mutating `<body>`, and the extension attributes do not represent application state that React should patch.

`suppressHydrationWarning` is intentionally narrow here:

- It is applied only to `<body>`.
- It does not disable SSR for app content.
- It does not hide mismatches in workflow components, tables, charts, or pages.
- It handles the exact layer where the extension attributes appeared.

## Alternatives rejected

Disabling SSR for large parts of the app would be excessive. The app's UI is primarily static/server-rendered at this stage and should keep SSR.

Changing route pages or components would miss the actual mismatch location. The warning's diff showed the extra attributes on `<body>`, which is owned by the root layout.

Asking users to disable Grammarly or similar extensions can be useful for diagnosis, but it is not a code fix and would leave portfolio reviewers exposed to a noisy warning.

## Verification

The checks after the fix:

```text
npm run lint       passed
npm run typecheck  passed
npm run build      passed
uv run pytest      152 passed
```

`npm run build` initially failed in the sandbox because Next could not fetch the configured Google Font. It passed after rerunning with network permission. `uv run pytest` initially failed because the sandbox could not read the uv cache; it passed after rerunning with permission.

## Residual risk

This does not and should not silence arbitrary hydration mismatches deeper in the app. If a future warning points to app-owned content, date formatting, random values, invalid HTML nesting, or client/server branching, diagnose that separately instead of expanding this escape hatch.
