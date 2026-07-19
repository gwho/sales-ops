# Plan — Feature landing-page-evidence-and-technical-credibility: Landing Page Evidence and Technical Credibility

## What was built

- `types/portfolio-content.ts` (modified) — added `PortfolioWorkflowHref` closed union (`/order-validation` | `/inventory-allocation` | `/payment-aging` | `/reports`); added `href: PortfolioWorkflowHref` to `PortfolioWorkflow`; added `PortfolioProofStrip` (`string[]`); added `PortfolioValidationEvidence` (prose-fragment type: `heading`, `orderId`, `errorCode`, `duplicateStatement`, `messageLead`, `summaryLead`, `summaryOutcome`); added `PortfolioTechnicalHighlight` (`heading`/`body`); added `proofStrip`, `validationEvidence`, `technicalHighlight` fields to `PortfolioContent`.
- `content/portfolio/sales-admin-automation-toolkit.json` (modified) — added `href` to each of the 4 workflow entries; added `proofStrip` (2 durable capability statements); added `validationEvidence` (heading + prose fragments citing `SO-2026-010`/`OV-002`); added `technicalHighlight` (Phase 12 session-persistence blurb).
- `lib/content/landing-evidence.ts` (new) — reads `portfolioContent.validationEvidence.orderId`/`.errorCode` as its selector, looks up matches in `lib/mock-data.ts`'s `orderValidationResult`, throws a descriptive error at module-eval time if any invariant fails, exports `landingValidationEvidence` (verified message + row numbers + counts).
- `components/landing/ProofStrip.tsx` (new) — renders `portfolioContent.proofStrip` as a thin bordered strip under `Hero`.
- `components/landing/ValidationEvidence.tsx` (new) — Server Component; composes `portfolioContent.validationEvidence`'s prose with `landingValidationEvidence`'s verified facts.
- `components/landing/TechnicalHighlight.tsx` (new) — Server Component; renders `portfolioContent.technicalHighlight`.
- `components/landing/WorkflowsSection.tsx` (modified) — each card wrapped in `next/link` to `workflow.href`, full `focus-visible` ring treatment added.
- `components/landing/PublicHeader.tsx` (modified) — anchor links wrapped in `hidden sm:flex`; brand label split into two fixed strings (`sm:hidden` / `hidden sm:inline`); brand wrapper gets `min-w-0 whitespace-nowrap`; CTA gets `shrink-0 whitespace-nowrap`.
- `app/(public)/page.tsx` (modified) — wired `ProofStrip`, `ValidationEvidence`, `TechnicalHighlight` into the section order: `Hero` → `ProofStrip` → `WorkflowsSection` → `ValidationEvidence` → `WorkflowSequence` → `ValueSection` → `BoundaryNote` → `TechnicalHighlight` → `TechSection` → `ClosingCta`.
- `context/ui-registry.md` (modified) — new entries for `ProofStrip`, `ValidationEvidence`, `TechnicalHighlight`; updated entries for the `WorkflowsSection` group (focus-visible on cards) and `PublicHeader`/`PublicFooter` (mobile fix).
- `docs/architect/landing-page-evidence-and-technical-credibility/` (new) — `decisions.md`, `discussion.md`, `ai-discussion-topics.md` from the preceding `/architect` session.

## Schema changes

None. No database, migration, or API contract changes — this is a frontend content/presentation feature only.

## Key invariants

- `lib/content/landing-evidence.ts` must throw at module-eval time unless: exactly 2 rows match the selected `orderId`/`errorCode`; those 2 rows have distinct `row_number` values; their `error_message` values are identical; `summary.duplicate_orders === 2`; `summary.invalid_orders` and `summary.total_orders` are present and numeric. Never loosen any of these to an "at least" check — the public copy asserts an exact fact ("appears twice"), and the invariant must assert exactly that fact, not an approximation of it.
- `lib/content/landing-evidence.ts` must read its lookup selector (`orderId`, `errorCode`) from `portfolioContent.validationEvidence` — never hardcode a duplicate constant for either value inside the loader. There must be exactly one place in the codebase that decides which case is being cited.
- `lib/content/landing-evidence.ts` must never be imported into a Client Component (no file containing `"use client"` may import it, directly or transitively).
- `components/landing/ValidationEvidence.tsx` must remain a Server Component.
- The quoted validation message in `ValidationEvidence.tsx` must never use `role="alert"` or any ARIA live region — it is static, build-time evidence, not a live event.
- `content/portfolio/sales-admin-automation-toolkit.json` remains the single source for all landing-page prose. `lib/content/landing-evidence.ts` may only source verified *facts* (message text, row numbers, counts) from `lib/mock-data.ts` — never prose.
- `PortfolioWorkflow.href` must stay typed as `PortfolioWorkflowHref` (the closed union) — do not widen it to a bare `string`.
- Each `WorkflowsSection` card must remain a single focusable element (the full-card `next/link`) with no nested interactive children.
- `PublicHeader`'s brand treatment is two fixed strings ("Sales Ops Toolkit" below `sm`, "Sales Admin Automation Toolkit" at `sm`+) with no CSS-truncation fallback — do not silently collapse this to one responsive string.
