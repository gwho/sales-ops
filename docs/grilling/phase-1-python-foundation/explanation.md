# Why These Decisions: Deep Explanation

This file goes past *what* changed and into *why* each call was made, what the rejected alternative would have cost, and how the six decisions reinforce each other. Written for someone picking this project up months later with no memory of the session.

## 1. Sequencing: risk-of-time vs. risk-of-shape

The original ADR 0003 argument was a **shape-risk** argument: "if we build UI first, we'll build it around invented data shapes that turn out wrong once the real Python logic exists." That's a real failure mode in general software projects — it's the classic justification for backend-before-frontend. But it doesn't actually apply here, because the specs (`sales_admin_automation_toolkit_specs/01-03`) already pin down every input column, business rule, and output column to the field-name level, including suggested Python function signatures. The shapes aren't unknown. Rebuilding the ADR's argument on a premise that doesn't hold would leave the *decision* right but the *reasoning* wrong — and wrong reasoning is what causes someone to make the wrong call on the next ambiguous decision, because they're generalizing from a justification that doesn't generalize.

The corrected argument is a **time-risk** argument: this is a portfolio project with a specific audience (`context/project-overview.md`'s "Target Audience" — sales/ops hiring managers plus technical reviewers). The audience wants proof that the candidate understands sales-ops workflows and can build tested automation for them. A polished dashboard over placeholder logic doesn't prove that; a Python core with real pytest coverage against the specs' rule tables does. If the project runs out of time, "three fully tested Python modules, no UI" is a much stronger interview artifact than "a beautiful dashboard, no working logic underneath." That's why sequencing — not shape stability — is the load-bearing reason, and it's why Phase 6 was later named as a fallback demo milestone (see §5 below): the argument that got Python-first accepted also implies the Python core alone must be demo-ready.

**Rejected alternative:** leaving ADR 0003 as originally written. Cost: future agents reading the ADR would internalize "avoid shape ambiguity" as the operating principle, and might over-invest in defining contracts speculatively (see §2) for the wrong reason, or under-invest in getting the Python core actually finished because the ADR doesn't name that as the point.

## 2. Phase 1 scope: infrastructure vs. scaffolding

The question here was narrow but consequential: does "Phase 1 - Python Project Foundation" mean *empty folders and config*, or does it mean *empty folders plus the two modules every other module needs*?

The case for keeping it minimal (folders only) is simplicity — Phase 1 stays a pure checkbox phase, and each business module (Phase 3, 4, 5) defines its own I/O and output shape as it's built, closest to where it's used.

The case that won: `excel_io.py` and `contracts.py` aren't owned by any single business module — `context/architecture.md`'s system-boundaries table already listed `excel_io.py` as its own row with its own "must not own" column (workflow-specific rules). If three separate business modules each write their own "load Excel, validate required columns" logic and their own ad hoc output dict shapes, you get three subtly different missing-column error messages and three subtly different field-naming conventions (e.g., one module might call it `sku`, another `SKU`, another `product_sku`) — and nothing catches the mismatch until a UI or API tries to consume all three. Defining the shared pieces once, before any business logic exists to diverge, is cheaper than reconciling three implementations later.

This is the same principle as "define the interface before the implementations that will disagree about it" — a deep-module boundary drawn early, while there's only one clear place to draw it.

**Consequence for later decisions:** this is what makes the Phase 7 planning gate possible (see §5). If contracts didn't exist until Phase 3-5 were done, UI planning would have nothing concrete to plan against until the business logic was finished — collapsing the two-gate split back into one gate.

## 3. Sample files vs. pytest fixtues: two audiences, two artifacts

This is a case where the same underlying data (order rows, invoice rows) serves two audiences with incompatible needs, and trying to make one artifact serve both produces something worse at both jobs.

- **pytest's audience** is future-you-debugging-a-regression. That audience wants a fixture with exactly one thing wrong, so a failing test points unambiguously at one rule. A tiny 1-2 row DataFrame does this.
- **`sample_data/`'s audience** is an interviewer opening the file in Excel. That audience wants to believe this is a plausible day's worth of sales-admin data. A workbook engineered to trigger all 7 validation rules, all 5 aging buckets, and every allocation status in 30 rows reads as artificial the moment someone actually looks at it — real messy data doesn't distribute its errors evenly, and it definitely doesn't confine each row to exactly one problem (which is what you'd need for the workbook to double as a test fixture without becoming ambiguous).

There's a subtler cost to the merged approach that came up implicitly: **maintenance coupling**. If `sample_orders.xlsx` is also the exhaustive test fixture, then adding a new validation rule later means editing a shared, hand-crafted Excel file and re-verifying every existing row didn't accidentally start triggering the new rule too. Small DataFrame fixtures defined in Python don't have this problem — each test owns its own minimal input, so adding rule OV-008 later means adding one new test with its own 1-row fixture, touching nothing else.

**Rejected alternative:** one dirty workbook per input file, exhaustively covering every spec test case. Cost: brittle tests (edits to sample data can silently break unrelated test assertions), and a demo artifact that reads as fake to the audience it's meant to impress.

## 4. Field scope boundary: contracts follow specs, not each other

The interesting tension in this decision wasn't validation-vs-allocation, it was **consistency-vs-fidelity**. Adding `suggested_action` to `AllocationResultRow` for symmetry with `PaymentAgingRow` would make the contracts *look* more uniform, which is often a good instinct in API design. But uniformity for its own sake, applied here, means inventing a business output the allocation spec never asked for — effectively the Python layer deciding on behalf of the (not-yet-written) UI what "suggested action" means for an allocation result, without a spec backing that decision.

The rule that resolved this — a contract may only contain fields its spec explicitly defines — is really a restatement of the Scope Gate (§6) at the field level rather than the rule level. Both rules share the same shape: *"the specs are the boundary of what's approved; symmetry, cleanliness, or 'it'd be nice to have' are not sufficient justification to cross it."* Recognizing that these are the same principle applied at two different granularities (whole rules vs. individual fields) is why this session used `domain-modeling` right after this decision — the vocabulary needed names (Output Contract, Contract Fixture, Field Scope Boundary) precisely because the same underlying concept kept getting invoked informally in three different ways across `context/architecture.md`, `context/build-plan.md`, and `context/project-overview.md`, and without a shared name it's easy for a future agent to apply the rule inconsistently.

**Rejected alternative:** symmetric contracts (add `suggested_action` everywhere for consistency). Cost: contract drift from the specs, and — worse — it would have set a precedent that "consistency" is a valid reason to add fields, which is exactly the reasoning pattern the Scope Gate (§6) had to explicitly rule out one focus area later.

## 5. Two gates instead of one: separating cheap decisions from expensive ones

The original plan had UI work as a single downstream phase (7-9) blocked on Phases 3-6. The problem with a single gate is that it conflates two very different kinds of work with very different costs of being wrong:

- **Planning** (route structure, table columns, KPI mapping, wireframes) is cheap to redo. If a business rule changes after planning, the wireframe gets updated — a docs change.
- **Implementation** (actual Next.js components reading actual contract shapes) is expensive to redo. If a business rule changes after components are built against it, that's a code change plus a test-suite change plus possibly a re-render of dependent components.

Once Phase 1 produces `contracts.py` (a resolved dependency from §2), planning has everything it needs — field names and shapes — without needing the *logic* behind those fields to be correct yet. Splitting the gate lets the cheap work start early (parallel with Phases 3-6) while the expensive work still waits for the specs' full test-case tables to pass. This is a general pattern: gate the expensive, hard-to-reverse step on strong evidence; let the cheap, reversible step start on weaker evidence.

The Phase 6 fallback-milestone naming that came out of this discussion is a direct consequence of the sequencing argument in §1: if the payload is the tested Python core, then the Python core plus its Excel report output needs to be a *complete, presentable artifact on its own* — not contingent on Phase 8 ever happening. Naming this explicitly turns an implicit hope ("well, if we run out of time at least we'll have something") into an explicit phase-level requirement that Phase 6 isn't "done" until the reports are professional enough to open in front of an interviewer.

## 6. Scope Gate: a mechanical check because judgment calls don't scale across sessions

The original "Non-Goals for V1" list in `context/architecture.md` is a list of entire *categories* (auth, DB persistence, AI forecasting, email sending). It's easy to check against because those categories don't appear anywhere in the in-scope specs at all — there's no ambiguity to resolve.

The gap this session found is different in kind: **in-spec-but-out-of-scope** content. Rule IA-007 is a V1 rule (warehouse chosen by highest available quantity) with an *optional V2 variant* (prefer warehouse matching customer region) described in the same numbered list, in the same file, with no visual distinction beyond the word "Optional." An agent reading the spec top-to-bottom while implementing IA-007 could reasonably decide the V2 variant is "basically free to add since I'm already in this function" — and that instinct, applied repeatedly across a dozen small decisions, is exactly how scope creep happens: not through one big wrong decision, but through many small locally-reasonable ones that each individually look free.

This is why the resolution is a **mechanical** rule rather than a principle to apply with judgment: "grep the spec for a version label before implementing a rule that isn't in the build-plan's required list." A mechanical check doesn't require the implementing agent to re-derive the cost/benefit tradeoff each time — it just requires reading a label. The user's explicit rejection of a "trivial V2 rules are fine" carve-out matters here: any carve-out reopens the judgment call the mechanical rule exists to remove, and "is this trivial enough" is exactly the kind of locally-reasonable-sounding judgment that produces creep in aggregate.

**Rejected alternative:** allow trivial V2 rules to be implemented alongside their V1 counterpart when convenient. Cost: no clean stopping point — "trivial" is not a fixed bar, and the same reasoning extends to CRM Cleaner being "basically already specified, so why not," which is precisely the module the project already explicitly postponed.

## How the six decisions interlock

- §1 (sequencing risk, not shape risk) is the premise that makes §5's fallback-milestone naming necessary — if the Python core is the real payload, it has to be demo-complete on its own.
- §2 (contracts defined in Phase 1) is the prerequisite that makes §5's planning-gate split possible — planning needs shapes, and shapes now exist before Phase 3.
- §4 (field scope boundary) and §6 (Scope Gate) are the same principle — "specs are the boundary, not aesthetics or convenience" — applied at two different levels of granularity, which is why they were named as related concepts in `CONTEXT.md` rather than as two unrelated rules.
- §3 (sample data vs. test fixtures) is a narrower instance of the same "define an artifact by is actual audience, not by what's convenient to build once" reasoning that shows up in §5 (planning vs. implementation gates being genuinely different jobs).
