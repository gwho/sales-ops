# Explanation — Feature landing-page-evidence-and-technical-credibility: Landing Page Evidence and Technical Credibility

## 1. The end-to-end data flow, traced concretely

The feature's centerpiece is the `ValidationEvidence` section, and its data flow is worth walking
through exactly, because the whole point of this feature was making that flow auditable rather than
trusting it.

It starts in `content/portfolio/sales-admin-automation-toolkit.json`, where a new
`validationEvidence` object holds `orderId: "SO-2026-010"` and `errorCode: "OV-002"` — this pair is
the *selector*, not the evidence itself. `lib/content/landing-evidence.ts` imports
`portfolioContent` (from `lib/content/portfolio.ts`, the existing typed JSON loader) and destructures
that selector at module scope: `const { orderId, errorCode } = portfolioContent.validationEvidence;`.
It also imports `orderValidationResult` from `lib/mock-data.ts` — the existing, already-established
typed access point for the build-time-regenerated mock JSON (`lib/mock-data/order-validation.json`,
itself produced by `scripts/generate_mock_data.py` running the real `validate_orders()` pipeline
against `sample_data/sample_orders.xlsx`). The loader filters `orderValidationResult.errors` for rows
matching both `orderId` and `errorCode`, and — this is the part that makes it more than a lookup —
immediately checks five separate facts against that filtered result: exactly two matches, distinct
`row_number`s, identical `error_message` text between the two, `summary.duplicate_orders` equal to
the match count, and both `summary.invalid_orders`/`summary.total_orders` present as numbers. Any
failure calls a local `fail()` helper that throws, with a message naming exactly which invariant
broke and pointing at the two files that need to be reconciled (the content JSON's selector, or the
sample data).

If every check passes, the module exports `landingValidationEvidence`, a plain object with the
verified `errorMessage`, `rowNumbers`, `invalidOrders`, and `totalOrders`. `ValidationEvidence.tsx`
imports that object directly (not a function call — see §3 for why this matters) and interleaves it
with the JSON's prose fragments: `{verified.orderId} {evidence.duplicateStatement} {evidence.messageLead}
"{verified.errorMessage}."` for the first sentence, and `{evidence.summaryLead} {verified.invalidOrders}
of {verified.totalOrders} {evidence.summaryOutcome}` for the second. The result, rendered, reads
exactly as: *"SO-2026-010 appears twice in the fictional sample file. The validator flags both rows
with 'Duplicate order ID found.' Overall, 8 of 36 order rows contain one or more issues, giving
operations a clear exception list before fulfilment."* — every number and every quoted word in that
sentence traces back to a real, checked value; every surrounding word traces back to the JSON's
hand-authored, code-reviewed prose. Nothing in that sentence was typed by hand into a component.

## 2. Why the invariant check happens at module scope, not inside a function

`lib/content/landing-evidence.ts`'s invariant checks run as top-level module code — not wrapped in a
function that `ValidationEvidence.tsx` calls at render time. This was a deliberate choice, and it
matters because of how Next.js's App Router handles this specific route. The production build's own
output confirms `/` is prerendered as static content (`○ (Static) prerendered as static content` in
the `next build` output, alongside `/dashboard` and the workflow pages) — meaning the entire page,
including `ValidationEvidence`, is rendered exactly once, at build time, not per visitor request.
A module-scope check runs exactly once too, at the moment the module is first imported during that
build — so if the invariant ever fails, it fails during `next build`, which is precisely the point
where a broken claim should be caught (before deploy, loudly, in CI or a local build), not silently
at runtime for whichever visitor happens to trigger a re-render. Wrapping the check in a function
that's called from inside the component would work today, but it would make the *timing* of the
check ambiguous — it could theoretically run on every render instead of once, and more importantly
it would obscure the intent that this is a build-time contract, not a request-time computation. The
module-scope placement makes that intent unmissable to a future reader of the file.

## 3. Why `ValidationEvidence.tsx` imports `landingValidationEvidence` as a value, not a function

Following from §2: `ValidationEvidence.tsx` does `import { landingValidationEvidence } from
"@/lib/content/landing-evidence"` and uses it directly as `verified.orderId`, `verified.errorMessage`,
etc. — no `getEvidence()` call, no `await`. This looks slightly unusual next to typical data-fetching
patterns (which usually look like a function call), but it's correct here specifically because the
"fetch" already happened — synchronously, at module-eval time, described in §1 — and what's exported
is the already-verified result, not a promise or a lazy getter. Introducing a function wrapper here
would add an appearance of runtime computation to something that is actually fixed at build time,
which would be a "looks more dynamic than it is" trap for a future reader trying to understand
whether this data can change between requests (it cannot, on this statically-generated route).

## 4. Why exactly two matches, not "at least one" — and how that was actually confirmed against real data

The single most load-bearing check in the loader is `matches.length !== 2`. This wasn't an arbitrary
choice of strictness; it's a direct consequence of what the sample data actually contains. Before
writing the loader, the real `lib/mock-data/order-validation.json` was inspected directly (via a
small Python script reading the committed JSON) to confirm the exact shape of the flagship duplicate
case: `SO-2026-010` appears in the `errors` array exactly twice, at `row_number: 11` (paired with
`sku: "PART-BULB-013"`) and `row_number: 37` (paired with `sku: "DIAG-TONO-007"`), both with
`error_code: "OV-002"` and the identical `error_message: "Duplicate order ID found."`. The
`summary.duplicate_orders` field independently reads `2`. Writing the check as "at least one match"
or even "at least two matches" would have technically passed against this real data too — but it
would have permitted the check to keep passing even if a future regeneration of `sample_data/sample_orders.xlsx`
introduced a *third* occurrence of `SO-2026-010`, which would make the landing copy's claim ("appears
twice") false while every existing check stayed green. The exact-equality check is what actually
enforces the sentence being displayed, not an approximation of it.

## 5. `next/link` full-card pattern: why no wrapper `<a>` was needed

`WorkflowsSection.tsx`'s cards were converted from plain `<div>`s to `<Link href={workflow.href}>`
wrapping the entire card's content (icon chip, tag, title, description) directly, with the existing
`hover:bg-surface-muted` classes plus the new `focus:outline-none focus-visible:ring-2
focus-visible:ring-accent focus-visible:ring-offset-2` moved onto the `<Link>` itself. This was
confirmed safe against the installed Next.js docs (`node_modules/next/dist/docs/01-app/03-api-reference/02-components/link.md`)
before writing it: as of Next.js 13, `<Link>` no longer requires a child `<a>` tag — it renders its
own anchor and forwards standard `<a>` attributes like `className` directly. That meant the
conversion was a straightforward swap of the outer element type (`div` → `Link`, plus an `href` prop)
with zero changes to the JSX structure inside it, and no risk of the old pre-v13 nested-`<a>` pattern
producing invalid HTML.

## 6. `PublicHeader`'s mobile fix: why two fixed strings instead of CSS truncation

The brand label swap (`Sales Ops Toolkit` below `sm`, `Sales Admin Automation Toolkit` at `sm` and
above) uses two separate `<span>`s toggled by Tailwind's `sm:hidden` / `hidden sm:inline`, rather than
a single string with `truncate`/`text-overflow: ellipsis`. This looks like it does more work (two
strings to maintain instead of one plus a CSS rule), but it was chosen because CSS truncation doesn't
guarantee a *readable* result — an ellipsis could land anywhere in "Sales Admin Automation Toolkit"
depending on exact pixel width, producing something like "Sales Admin A…" that reads as a rendering
artifact rather than a designed abbreviation. Two fixed, chosen-in-advance strings guarantee the
narrow-viewport brand always reads as a real, complete phrase. The wrapping `<span>` also carries
`min-w-0` — a detail that's easy to get wrong: without it, a flex child (this wrapper sits inside the
header's `flex items-center justify-between` row) defaults to a `min-width` based on its content's
intrinsic size, which can prevent it from shrinking at all and push the CTA button off-screen instead
of letting the brand truncate/swap gracefully. `whitespace-nowrap` on the same wrapper, plus
`shrink-0 whitespace-nowrap` on the CTA `<Link>`, ensures neither element wraps its text onto a second
line at narrow widths, which would break the header's fixed `h-14` height.

## 7. Two pre-existing gaps found and fixed as a side effect, not the original ask

Two of the changes in this pass weren't part of the original six architecture decisions handed into
the `/architect` session — they surfaced as side-findings during research and were folded in after
confirmation:

- `WorkflowsSection`'s cards had a `hover:bg-surface-muted` affordance but no `href`/`tabIndex` at
  all — a real accessibility gap (a keyboard user tabbing through the page had nothing to land on
  where a mouse user saw a hover response), not something anyone had reported as broken. It was found
  by explicitly checking the component's JSX for interactive semantics, not by symptom.
- `PublicHeader.tsx` had zero responsive classes anywhere in the file — confirmed by grepping the
  component for any breakpoint prefix and finding none. This one was almost certainly a real bug
  waiting to be noticed at a narrow viewport, not a deliberate simplification; it just hadn't been
  exercised at a narrow width before this pass looked for it.

Both are documented in `docs/architect/landing-page-evidence-and-technical-credibility/decisions.md`
#8-9 as confirmed additions to the original scope, with the user's explicit sign-off before
implementation — they weren't silently bundled in.

## 8. Why the implementation had no build or type errors to document

Unlike a typical feature build, this implementation produced zero TypeScript errors, zero lint
errors, and a clean `next build` on the first attempt after all files were written. That's worth
noting explicitly rather than treated as unremarkable, because it's a direct consequence of how much
of the "figuring it out" happened before any code was written: three separate rounds of plan review
(data-integrity, scope-locking, precision — see the architect session's `discussion.md` §"Why this
session ends before any code") had already resolved every type shape, every file name, every exact
string of copy, and every edge case in the invariant logic before implementation began. The one
thing that *was* confirmed only during implementation — the exact export name and shape of
`lib/mock-data.ts` (`orderValidationResult`, typed via `OrderValidationResult` from `types/index.ts`)
— was verified by reading the file directly rather than assumed, exactly as the plan's own
"Assumptions" section required.

## 9. No context-file corrections were needed

Unlike some feature passes, this one didn't require any correction to `context/ui-tokens.md`,
`context/ui-rules.md`, or `context/architecture.md` — every visual pattern used (bordered strips,
`text-danger` for flagged text, the existing focus-visible ring convention, `Section`/`SectionLabel`/
`SectionHeading` composition) already existed and was reused verbatim. The only context file touched
was `context/ui-registry.md`, which is expected and required after any UI change — not a correction,
but the normal record-keeping this project's `/imprint` step performs after every component.
