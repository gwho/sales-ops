# Hydration Extension Warning Diagnosis

## What broke

The browser showed a React/Next hydration warning on `/inventory-allocation`:

```text
A tree hydrated but some attributes of the server rendered HTML didn't match the client properties.
```

The reported diff pointed at `app/layout.tsx` and showed extra attributes on `<body>` on the client side:

```text
data-new-gr-c-s-check-loaded="14.1309.0"
data-gr-ext-installed=""
```

Those attributes were not rendered by the app. They are injected by a browser extension before React hydrates.

## Feedback loop

This was not fully reproducible from the terminal because the symptom depends on a browser extension mutating the DOM before hydration. The useful captured artifact was the exact Next/React overlay diff from the user, which identified the mismatched element and attributes.

The verification loop after the fix was:

```bash
npm run lint
npm run typecheck
npm run build
uv run pytest
```

This loop verifies the root-layout change is valid and does not break the app, but final confirmation of the original warning requires the same browser extension environment.

## Root cause

The app's server-rendered `<body>` matched the code in `app/layout.tsx`, but the browser extension added Grammarly-related attributes before React hydration. React then compared the server-rendered body attributes with the client DOM and reported a hydration mismatch.

This matches the official Next.js hydration-error guidance, which lists browser extensions modifying HTML as a common cause and `suppressHydrationWarning` as an escape hatch for unavoidable mismatches.

## Why the fix belongs in the root layout

The mismatch occurred on the `<body>` element defined by the root layout, not in a route page or reusable component. Fixing child components would not address an attribute mismatch on `<body>`.

The narrow fix is to suppress hydration warnings on the root `<body>` element only.
