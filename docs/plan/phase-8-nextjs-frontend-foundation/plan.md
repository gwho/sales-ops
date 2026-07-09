# Plan — Feature phase-8-nextjs-frontend-foundation: Next.js Frontend Foundation

## What was built

Next.js App Router scaffold at the repo root (Next 16.2.10, React 19.2.4, TypeScript strict), sitting alongside the existing Python `src/`. Scaffold-only: config, routing, tokens, mock data. No reusable components, no data wiring (Phase 9).

**Created:**

- `app/layout.tsx` — root layout; Inter via `next/font/google` bound to `--font-inter`; body uses semantic token classes (`bg-background`, `text-text-primary`, `font-sans`).
- `app/globals.css` — `@tailwind` v3 directives + the `:root` design-token variables copied verbatim from `context/ui-tokens.md` (HSL channel triples); `@layer base` body defaults.
- `app/page.tsx` — root route; `redirect("/dashboard")`.
- `app/dashboard/page.tsx` — stub landing; links to the 4 workflow routes via `next/link`.
- `app/order-validation/page.tsx`, `app/inventory-allocation/page.tsx`, `app/payment-aging/page.tsx`, `app/reports/page.tsx` — stub Server Components; title + "Phase 9 builds this" note + back-to-dashboard link. Each carries a header comment naming the contract/components Phase 9 will build there.
- `tailwind.config.ts` — Tailwind 3.4 config; `content` globs for `app/`, `components/`, `lib/`; `theme.extend.colors` maps every `ui-tokens.md` token to `hsl(var(--token))`; `fontFamily.sans` → `var(--font-inter)`.
- `postcss.config.mjs` — `tailwindcss` + `autoprefixer` (v3 PostCSS path).
- `lib/utils.ts` — `cn()` (clsx + tailwind-merge), shadcn convention.
- `components.json` — shadcn config (new-york, rsc, cssVariables, `@/*` aliases, lucide) for future `shadcn add` in Phase 9.
- `types/index.ts` — all output-contract TS types + the 3 result envelopes, copied verbatim from `context/ui-contract-plan.md` (snake_case).
- `scripts/generate_mock_data.py` — build-time-only generator; imports `tests/contract_fixtures.py`, assembles the 3 envelopes + manifest list, writes `lib/mock-data/*.json`.
- `lib/mock-data/{order-validation,inventory-allocation,payment-aging,reports}.json` — committed mock JSON output.
- `next.config.ts`, `tsconfig.json`, `eslint.config.mjs`, `next-env.d.ts` (gitignored), `public/*.svg`, `package.json`, `package-lock.json` — from the scaffold; `package.json` renamed to `sales-admin-automation-toolkit`, deps pinned (Tailwind 3.4.19, no v4), `typecheck` script added.

**Modified:**

- `.gitignore` — appended Next.js/Node ignore entries under a labeled section; Python entries kept.
- `context/ui-contract-plan.md` — added the Figma Reference Reconciliation section (V1 / corrections / out-of-scope for the 4 Figma Make prototypes); updated the top note from "no Figma available" to "inspected in Phase 8 via MCP".
- `context/progress-tracker.md` — Current Status advanced to Phase 8 complete; Phase 8 checklist checked off; Phase 7 Figma line corrected; two Phase 8 Decisions Made entries added.

## Schema changes

None. No database exists in this project; the Python core is stateless and file-driven.

## Key invariants

- **The Next.js app must never import from `tests/` at runtime.** `scripts/generate_mock_data.py` is the only sanctioned bridge, and only at build time. Runtime UI reads the committed `lib/mock-data/*.json`. Violating this couples the shipped app to test-only code.
- **`context/ui-tokens.md` is the authoritative token set. Do not add, rename, or invent color tokens** in `tailwind.config.ts` or `app/globals.css` without a token-change decision. In particular, do not introduce shadcn's default tokens (`--primary`, `--card`, `--destructive`, shadcn's `--accent`) — shadcn's `--accent` (gray hover) collides with this project's `--accent` (brand blue).
- **Tailwind stays on 3.4.x. Never upgrade to v4** (`context/library-docs.md`). The setup is the v3 path (`tailwind.config.ts` + `@tailwind` directives + autoprefixer), not v4's CSS-first `@import "tailwindcss"` / `@tailwindcss/postcss`.
- **`types/index.ts` is a verbatim mirror of `context/ui-contract-plan.md`** (which mirrors `src/contracts.py`). snake_case field names are intentional — no camelCase adapter. If contracts change, update `ui-contract-plan.md` first, then regenerate this file, then re-run the mock-data generator.
- **shadcn primitive components are deferred to Phase 9.** Only plumbing (`cn()`, `components.json`, deps) exists now. Each primitive gets added when a real component needs it, reconciled to `ui-tokens.md`, and `/imprint`ed.
- **The route set is fixed at 5** (`/dashboard`, `/order-validation`, `/inventory-allocation`, `/payment-aging`, `/reports`) plus the root redirect. Do not add ERP-style nav destinations (Orders, Customers, Analytics) that no output contract backs.
- **Regenerate mock JSON after any contract-fixture change:** `uv run python scripts/generate_mock_data.py`. The mock JSON is committed output, not hand-edited.
