# AI Discussion Topics — Feature landing-page-evidence-and-technical-credibility: Landing Page Evidence and Technical Credibility

## Group 1 — Build-time verification and data flow

1. Walk through exactly what happens, file by file, from `content/portfolio/sales-admin-automation-toolkit.json`'s `validationEvidence.orderId` field to the rendered sentence on `/`. Where does each word and each number in the final sentence originate?
2. Why does `lib/content/landing-evidence.ts` run its invariant checks as top-level module code instead of inside an exported function that `ValidationEvidence.tsx` calls? What would change if `/` were a dynamically rendered route instead of statically prerendered?
3. `landingValidationEvidence` is imported as a plain value, not called as a function. What would have to change about this code if the evidence needed to come from a runtime source (e.g. a live database query) instead of build-time JSON?
4. The loader's `fail()` helper throws with a message naming which file to fix. Who is the actual audience for that error message, and where would they most likely encounter it?

## Group 2 — Invariant design

5. Why does the loader check `matches.length !== 2` instead of `matches.length < 2`? Construct a concrete future edit to `sample_data/sample_orders.xlsx` that the looser check would miss but the exact check catches.
6. The loader also checks that the two matched rows have distinct `row_number`s. What real-world data bug would produce two matches with the *same* `row_number`, and why would that be worth failing the build over?
7. `summary.duplicate_orders` is checked against `matches.length` even though both numbers come from the same underlying `validate_orders()` run. Is this redundant, or does it protect against something the row-count check alone wouldn't catch?

## Group 3 — Content and ownership boundaries

8. `content/portfolio/sales-admin-automation-toolkit.json` owns 100% of the prose, but `lib/mock-data.ts` supplies the verified facts. Where exactly is the line between "prose" and "fact" drawn in `PortfolioValidationEvidence`'s field list, and could that line be drawn differently?
9. Why does the loader read `orderId`/`errorCode` from `portfolioContent.validationEvidence` instead of hardcoding them as constants in `lib/content/landing-evidence.ts` itself? What would go wrong if both places hardcoded the same values independently?
10. If a second evidence example were added later (say, a payment-aging case), should it reuse `PortfolioValidationEvidence`'s exact shape, or would a different shape be more honest about what's being verified?

## Group 4 — Accessibility and component boundaries

11. Why must `lib/content/landing-evidence.ts` never be imported into a Client Component? What Next.js concept explains what would actually happen if it were?
12. `ValidationEvidence.tsx` quotes a real error message but deliberately avoids `role="alert"`. What's the general rule for deciding when quoted error-shaped text needs live-region semantics and when it doesn't?
13. `WorkflowsSection`'s cards are now full-card `next/link`s with no nested interactive children. Why does "no nested interactive children" matter for a screen reader user specifically, beyond just "it's now clickable"?

## Group 5 — Responsive header fix

14. Why does `PublicHeader`'s brand label use two separate fixed strings toggled by breakpoint classes instead of a single string with CSS truncation? What failure mode does the two-string approach avoid?
15. What does `min-w-0` do on the brand wrapper `<span>`, and why is it necessary given the header's `flex items-center justify-between` layout? What would break without it?
