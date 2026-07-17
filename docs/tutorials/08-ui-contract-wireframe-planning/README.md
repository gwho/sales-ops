# Tutorial 08 — UI Contract and Wireframe Planning: Designing a Frontend Before Writing Any JSX

**After completing this tutorial you will understand:** why Phase 7 plans field names and result
envelopes before imagining a single screen, and what concretely goes wrong when planning starts
from a mockup instead; how a TypeScript `type` can mirror a Python `TypedDict` field-for-field
without translating naming conventions or optionality, and why that specific discipline matters;
why every status badge in this project must be classified as direct, derived, or a direct/derived
hybrid, and what silently invented label each classification prevents; why a report's "generation
status" lives entirely in browser state with no Python contract field behind it; and how a
documented drift bug (`requested_quantity` vs. the real `requested_qty`) gets caught mechanically
instead of by eye, and why a second manual read-through can't be trusted to catch what the first
one already missed.

> [!NOTE]
> **Prerequisites:** Tutorial 07 (`07-fastapi-integration/README.md`) — not a content dependency
> (Phase 7 chronologically predates Phase 10), but the tutorial you just finished, so this one
> assumes you're comfortable with the result-envelope shapes it exercised. Tutorial 01
> (`01-python-foundation/README.md`) — `TypedDict`, `NotRequired`, and structural typing all
> reappear here applied to a second language (TypeScript) instead of just Python. Tutorial 05
> (`05-payment-aging-core/README.md`) — `PaymentAgingRow` and `follow_up_priority` are this
> tutorial's running full-trace example; you need to already trust where that field's value comes
> from. Before this tutorial, read Track 5's three concept lessons —
> `docs/teach/lessons/0031-browser-output-and-components.html`,
> `0032-react-minimum-mental-model.html`, and `0033-server-and-client-components.html` — for the
> browser/React/Server-Component vocabulary this tutorial assumes but Phase 7 itself never needed
> (it's a docs-only phase). Open
> [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md),
> [`context/ui-rules.md`](../../../context/ui-rules.md),
> [`src/contracts.py`](../../../src/contracts.py),
> [`src/payment_aging.py`](../../../src/payment_aging.py),
> [`src/inventory_allocation.py`](../../../src/inventory_allocation.py),
> [`src/report_export.py`](../../../src/report_export.py),
> [`tests/contract_fixtures.py`](../../../tests/contract_fixtures.py), and
> [`tests/test_contracts.py`](../../../tests/test_contracts.py) alongside this tutorial.

> [!NOTE]
> **A caveat about ordering, worth stating once, up front:** this tutorial series is numbered by
> *Concept Track* order, not calendar/phase order. Phase 7 (this tutorial's subject) chronologically
> happened **before** Phase 10 (Tutorial 07's subject) — the real commit history has Phase 7's own
> commit landing before FastAPI ever existed. Tutorial 07 comes first in this series anyway, because
> Track 4 (HTTP/statelessness) was scheduled ahead of Track 5 (frontend) in `docs/teach/ROADMAP.md`.
> Don't read anything in this tutorial as happening "after" FastAPI in real time — it didn't.
> Separately: this repository is post-Phase-12, and `context/ui-contract-plan.md` itself is not
> frozen at its Phase 7 state — its Figma Reference Reconciliation section was added during Phase 8,
> and one bug this tutorial discusses as "found but deliberately left unfixed" (Part 7) was
> genuinely fixed by a later, separate commit. Both are called out explicitly, in place, rather than
> silently smoothed over.

## CS & language concepts in this tutorial

| Concept | Where it appears | Category |
|---------|-----------------|----------|
| Structural mirroring across a language boundary | Every TS `type` in `ui-contract-plan.md` copies a Python `TypedDict`'s field names and optionality verbatim, no camelCase translation | Type theory |
| String-literal union as a controlled vocabulary | `status: "Fully Allocated" \| "Partially Allocated" \| "Backordered"` — TypeScript's version of Python's implicit string-enum fields | Type theory |
| Finite state machine | The Report Card lifecycle — `Needs Input → Not Generated → Processing → Ready`, one direction, one failure edge | Design patterns |
| Set-difference verification | The Phase 7 field-name diff: two regex-extracted sets (TS fields, Python fields) compared for a zero-mismatch result | Algorithms |
| Derived/materialized view | Every entry in "Derived Display-Only Aggregates" — a client-computed group-by/sum over already-fetched rows, backed by no new query or field | System design |

## How to use an LLM before this tutorial

### Concept 1 — Planning a system's data shape before its interface

> "Explain the difference between designing a user interface by sketching screens first (and
> figuring out what data each screen needs afterward) versus designing it by starting from the
> data a system can actually produce (and only then deciding how to lay it out). Give a concrete
> example of a UI element that a screens-first process might invent that a data-first process never
> would. Quiz me on which approach is more likely to produce a UI element with no real data behind
> it."

*What to listen for:* a screens-first process treats "what would look good/complete here" as the
starting question, and only checks against real data afterward — which means a plausible-looking
element (a trend arrow, a risk score, a "last updated by" field) can get designed and even half-built
before anyone notices no system actually produces that value. A data-first process makes that
mistake structurally harder: if a KPI or badge doesn't trace to a real field, there's nothing to
plan around, and the gap surfaces immediately instead of after implementation has already started.

*Practice question:* if a wireframe includes a "Customer Health Score" badge and no backend system
anywhere computes a health score, which process — screens-first or data-first — would catch that
before any code exists?

### Concept 2 — Mirroring a type across a language boundary

> "A backend written in one language (say, Python) produces JSON data that a frontend written in
> another language (say, TypeScript) consumes. Explain what it means to 'mirror' the backend's data
> shape into the frontend's type system field-for-field, versus 'translating' it (renaming fields to
> match the frontend language's naming conventions, e.g. snake_case to camelCase). What's a concrete
> cost of translating that mirroring avoids? Quiz me on what has to stay true for a mirrored type to
> keep working over time without maintenance."

*What to listen for:* translating introduces a mapping layer — something has to convert
`requested_qty` to `requestedQty` (or back), and that conversion code is one more thing that can
drift out of sync with the real backend field, or silently swallow a renamed/added field. Mirroring
verbatim means the frontend type and the backend field are, character-for-character, the same
string — there's no translation step to get wrong, at the cost of writing frontend code that reads
slightly less idiomatic to a TypeScript-only reader.

*Practice question:* if a Python field is renamed from `qty` to `quantity` and the frontend type
mirrors verbatim, what has to happen for the frontend to still compile correctly?

### Concept 3 — Controlled vocabularies as union types

> "Explain what a 'controlled vocabulary' field is — a field whose value is always one of a small,
> fixed, known set of strings (like a status or a priority), as opposed to free text. Explain how a
> statically-typed language's union-of-literals feature (e.g. TypeScript's `\"a\" | \"b\" | \"c\"`)
> can encode that fixed set at the type level, catching a typo'd or invented value at compile time
> instead of only at runtime. Quiz me on what a union-of-literals type *cannot* catch that a runtime
> check still could."

*What to listen for:* a union-of-literals type only protects code written against that type — it
catches a developer typing `"Fully Alocated"` in TypeScript code, but it does nothing to prevent the
actual JSON payload arriving over the network from containing an unexpected string the backend
produced by mistake; that's a runtime problem a compile-time type can never fully solve on its own.

*Practice question:* if a Python function has a bug and returns the string `"Fully Allcoated"`
(typo) instead of `"Fully Allocated"`, would a TypeScript type declaring
`status: "Fully Allocated" | "Partially Allocated" | "Backordered"` catch that at compile time, at
runtime, or not at all?

### Concept 4 — A finite state machine with one persisted state and several ephemeral ones

> "Explain what a finite state machine is: a fixed set of named states, and a fixed set of allowed
> transitions between them, with exactly one state true at a time. Give an example of a state
> machine that's *entirely* client-side/ephemeral (forgotten on page reload) versus one that's
> persisted server-side. What determines which kind is appropriate for a given piece of state? Quiz
> me on which kind fits 'has this specific report been generated in the current browser session.'"

*What to listen for:* the deciding factor is whether the *fact* the state represents needs to
survive beyond the current session/interaction, and whether any other part of the system needs to
query it independently of the UI that's currently displaying it. A report's "have I clicked
generate yet, this session" is disposable UI convenience state — nothing breaks if it's forgotten on
reload, since the underlying data (the result envelope) is still there to regenerate a report from.
A persisted state machine earns its cost when losing it would lose real information no other system
of record retains.

*Practice question:* if a report's `Ready`/`Processing`/`Not Generated` status were stored as a new
Python contract field instead of browser state, what would have to change about how
`export_payment_aging_report()` is called for that field to stay accurate?

### Concept 5 — Verifying a claim mechanically instead of by re-reading

> "Explain why re-reading your own written work a second time is a weak way to catch your own
> errors, compared to writing a small, independent, mechanical check (a script, a diff, an
> assertion) that verifies the same claim. What cognitive bias or blind spot does the mechanical
> check avoid that a second read-through doesn't? Quiz me on a scenario where 'I re-read it twice
> and it looked right' turned out to still be wrong."

*What to listen for:* a second manual read shares the same blind spots as the first — if you
misread or mistyped a name once while writing something, your mental model of "what it says" is
already wrong, and rereading your own text tends to confirm what you expect to see rather than what
is actually there. A mechanical check (extract both sets independently, diff them) has no such
expectation to confirm — it can only report what's actually present in each source, which is exactly
the property a self-review can't guarantee.

*Practice question:* if someone wrote 67 TypeScript field names by hand from four Python source
files, and then re-read all 67 by eye a second time to check for typos, would you trust that check
as much as an automated diff of two independently-extracted field-name sets? Why or why not?

## Architecture overview

Phases 1–6 (Tutorials 01–06) built and tested the Python core; Tutorial 07 wrapped it in a
stateless HTTP API. None of that produced a single line of frontend planning. Phase 7 is the first
phase whose entire deliverable is a plan for a Next.js frontend that doesn't exist yet — no JSX, no
`app/` routes, nothing runnable. It's pure documentation, and the documentation's job is to make
every future frontend decision traceable back to a real Python shape:

```text
     src/contracts.py                    src/order_validation.py
     (13 TypedDicts)                     src/inventory_allocation.py
           │                             src/payment_aging.py
           │                            (3 locally-defined result envelopes)
           └────────────────┬─────────────────────┘
                             ▼
              research pass: diff EXISTING planning prose
              (ui-rules.md, sales_admin_automation_toolkit_ui_specs/)
              against the REAL field names above — any drift found
              is treated as a bug to fix, not a spec to build from
                             │
                             ▼
         context/ui-contract-plan.md   (NEW — Phase 7's main artifact)
         ├─ Glossary (Status Badge, Derived Display Value)
         ├─ TypeScript `type` mirror of all 13 + 3 shapes, snake_case intact
         ├─ Route/Page Plan — 5 fixed routes, each with a "Consumes" contract list
         ├─ Table Column Plan — 9 table sets, every column named to a real field
         ├─ KPI Card Mapping — per page, 1 flagged derived KPI ("90+ Days Amount")
         ├─ Status Badges cross-reference — direct vs. derived, all 4 workflows
         ├─ Report Cards — a 4-state client-only lifecycle
         ├─ Empty/Loading/Error copy — verbatim from each spec's own UI section
         └─ Derived Display-Only Aggregates — 5 entries, each source/field/rule
                             │
                             ▼ (in the SAME session, found a second drift bug)
         context/ui-rules.md   (EDITED — Status Badges section rewritten,
                                 all 4 workflow groups, not just the 2 first
                                 thought to be broken)
                             │
                             ▼
         verification: a throwaway Python script extracts every TS field name
         by regex and every Python field name by regex, diffs the two sets —
         67 TS fields, 0 mismatches (script itself was never committed)
                             │
                             ▼
              Tutorials 09–11 (Phases 8–10.2): the real Next.js code
              this plan licenses — none of it exists yet at this point
```

Key invariants for this phase:

1. **Every field name in `ui-contract-plan.md`'s TypeScript interfaces must exist verbatim in
   `src/contracts.py` or one of the three envelope definitions.** Verified mechanically this
   session, not by re-reading (Part 7).
2. **A status badge label is either a verbatim contract-field value or an explicitly-documented
   derivation rule — never an unlabeled invented label.** Any future badge addition must state
   which category it is (Part 4).
3. **The Reports badge/report-card lifecycle is purely client-side session state.** No Python field
   tracks report-generation status, and no future implementation should add one to represent it
   (Part 6).

## Part 1 — Planning from output contracts, not from imagined screens

Open [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md) lines 1–12:

```markdown
# UI Contract Plan

Phase 7 deliverable (planning only — no production frontend code). Maps every future Next.js
surface (route, table, KPI, badge, report card, empty/loading/error state) to a real Python
output contract or an explicitly-labeled display-only derivation. Living reference, same tier
as `ui-tokens.md`/`ui-rules.md` — update it whenever `src/contracts.py` or the business-module
envelopes change.
...
## Glossary

- **Status Badge** — a UI label that either comes directly from a controlled-vocabulary contract
  field (e.g. `PaymentAgingRow.aging_bucket`), or is derived client-side from row/list membership
  (e.g. "Valid" = row is in `valid_orders`). Either way it must trace to real contract data...
- **Derived Display Value** — a value computed client-side from existing contract fields (a
  group-by/sum for a chart, a label transform of an existing field) that introduces no new
  business logic and requires no contract change.
```

The opening line states the whole phase's method in one sentence: map every future surface to a
real contract or an explicitly-labeled derivation. `docs/plan/phase-7-ui-contract-wireframe-planning/explanation.md`
§1 names what this method was reacting *against* — three planning surfaces already existed before
Phase 7 started (`ui-rules.md`'s Status Badges section and the three guidance folders under
`sales_admin_automation_toolkit_ui_specs/`, `ui_reference_to_figma_workflow/`,
`ui_prompts_for_agents_mcp/`), and every one of them was written before Phases 3–6 existed — before
the real field names, real status values, and real envelope shapes existed at all.

The concrete cost of that ordering surfaced immediately: `sales_admin_automation_toolkit_ui_specs/`'s
table plans used `requested_quantity`; the real field, locked in by Phase 4 (Tutorial 04), is
`requested_qty`. That's not a typo introduced by Phase 7 — it's a field name someone imagined before
`inventory_allocation.py` existed to say otherwise, and it survived, unexamined, until this phase's
research pass compared it against the real source.

**Checkpoint:** Walk through exactly how this phase's research caught the `requested_quantity` vs.
`requested_qty` drift — what was compared against what — and why would spot-checking a few fields by
eye likely have missed it?

<details>
<summary>Reveal answer</summary>

The catch came from treating the pre-existing guidance folder as a *claim to verify*, not a source
of truth to build from — every field name it used was checked against the actual `TypedDict`
definitions in `src/contracts.py` and the actual dict keys built in `src/inventory_allocation.py`,
one field at a time, rather than trusted because it "looked complete." Spot-checking a few fields by
eye would likely have missed this specific drift because `requested_quantity` *reads* as a
completely reasonable field name — nothing about it looks wrong in isolation; the only way to catch
it is to check it against the one place that actually defines the real name
(`AllocationResultRow.requested_qty` in `src/contracts.py:53`), which requires deliberately auditing
every field, not sampling a few that happen to look suspicious.
</details>

**Checkpoint:** `CONTEXT.md` was deliberately not edited this phase, with `Status Badge` and
`Derived Display Value` defined in `ui-contract-plan.md` instead. Design a test you could apply to
any future term to decide which glossary it belongs in.

<details>
<summary>Reveal answer</summary>

A workable test: does the term name a real-world business fact a domain expert (a sales admin, an
ops manager) would recognize and use in conversation about the business itself — independent of how
this particular codebase happens to be built? `CONTEXT.md`'s existing terms (Order, SKU, Allocatable
Quantity, Aging Bucket) all pass this test; someone could define "Aging Bucket" to a new hire without
ever mentioning React or TypeScript. `Status Badge` and `Derived Display Value` fail this test — they
only mean something in the context of *this specific frontend's implementation vocabulary*, and a
domain expert would never use either phrase to describe the business itself. The general rule this
implies: business-domain glossaries hold terms that would survive a full rewrite of the tech stack;
process/UI-planning glossaries hold terms that wouldn't.
</details>

## Part 2 — Mirroring Python shapes into TypeScript without semantic translation

Open [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md) lines 14–16, then the
`PaymentAgingRow` block at lines 132–144:

```markdown
Literal `type` definitions (`code-standards.md`: prefer `type` over `interface` for data
shapes/unions), copy-pasteable into `types/index.ts` in Phase 8. Snake_case fields preserved
verbatim to match the JSON the Python core returns — no camelCase adapter layer decided yet.
```

```ts
export type PaymentAgingRow = {
  invoice_id: string;
  customer_name: string;
  invoice_date: string; // ISO date
  due_date: string; // ISO date
  invoice_amount: number;
  paid_amount: number;
  outstanding_amount: number;
  days_overdue: number; // signed — negative means not yet due
  aging_bucket: "Current" | "1-30 Days" | "31-60 Days" | "61-90 Days" | "90+ Days";
  follow_up_priority: "High" | "Medium" | "Low" | "Watch" | "None";
  suggested_action: string; // one of 5 fixed strings keyed by follow_up_priority
};
```

Compare this to `src/contracts.py:93–104`'s real `PaymentAgingRow`:

```python
class PaymentAgingRow(TypedDict):
    invoice_id: str
    customer_name: str
    invoice_date: str
    due_date: str
    invoice_amount: float
    paid_amount: float
    outstanding_amount: float
    days_overdue: int
    aging_bucket: str
    follow_up_priority: str
    suggested_action: str
```

Every field name matches exactly: `invoice_id`, not `invoiceId`; `days_overdue`, not `daysOverdue`.
This is a deliberate decision, not an oversight — a snake_case-to-camelCase adapter layer was never
decided, so the plan doesn't invent one. The TypeScript version does add real information the
Python `TypedDict` can't express on its own: `aging_bucket` and `follow_up_priority` are typed as
`str` in Python (Tutorial 01 Part 1 covered why — no runtime enforcement, checked structurally at
type-check time only), but the TypeScript plan narrows both to the exact literal union of values
`_aging_bucket()` (`src/payment_aging.py:115–125`) and `_follow_up_priority()`
(`src/payment_aging.py:128–140`) can actually produce. That narrowing had to be done by reading the
Python *logic*, not just the Python *type* — the contract's own type annotation doesn't reveal the
five follow_up_priority values or their exact spelling; only the function body does.

> **Type theory — String-literal union as a controlled vocabulary:** TypeScript's
> `"High" | "Medium" | "Low" | "Watch" | "None"` is a union of string literal types — a value typed
> this way can only ever be one of those five exact strings, checked at compile time. Python has no
> exact equivalent without a separate `Literal[...]` type or an `Enum` class, neither of which this
> project uses for these contracts (Tutorial 01 covered why: `TypedDict` fields are typed as plain
> `str`, relying on the business-rule function's own logic — not the type system — to guarantee only
> five values ever get produced). The TypeScript plan is stricter than the Python source it mirrors,
> in this one specific respect.

**Checkpoint:** The automated field-name diff script found 0 mismatches across 67 TypeScript
fields. What kinds of errors would this script *not* catch (e.g. a field with the right name but
wrong type, or a field that exists but is documented with the wrong optionality)?

<details>
<summary>Reveal answer</summary>

A field-name diff only checks that a *name* exists on both sides — it says nothing about whether
the *type* attached to that name is correct. It would not catch `invoice_amount` being typed as
`string` on the TypeScript side when the real Python field is a `float`; it would not catch a field
marked required in TypeScript when the real Python field is `NotRequired[...]` (or the reverse); and
it would not catch a `Record<...>` shape (like `aging_bucket_counts`) whose *key set* is wrong even
though the top-level field name matches. This is exactly why the checkpoint's practice question in
this tutorial's pre-study matters: a mechanical check only verifies the specific claim it was built
to verify, and "the field name exists" is a narrower claim than "the field is fully, correctly
documented."
</details>

**Try it yourself:** Open [`src/contracts.py`](../../../src/contracts.py) and pick any `TypedDict`
you haven't looked at yet (e.g. `RemainingInventoryRow`, lines 66–73). Find its mirror in
`context/ui-contract-plan.md`'s TypeScript Interfaces section. Confirm every field name matches
exactly, and that every `NotRequired[...]` Python field became an optional (`?`) TypeScript field —
`reorder_point?: number;` mirroring `reorder_point: NotRequired[int]`.

## Part 3 — A fixed route set backed by real workflows

Open [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md) lines 184–194:

```markdown
## Route / Page Plan

Fixed 5-route set (`build-plan.md` Phase 8, `architecture.md`):

| Route | Consumes | Composes |
|---|---|---|
| `/dashboard` | All 3 summaries (when run this session) + all 3 `ReportManifest`s (when generated) | KPI strip (3 sections, independent empty states) + 3 workflow entry cards + 3 report cards + demo-mode note |
| `/order-validation` | `OrderValidationResult` | `UploadPanel` ×2, KPI strip (`ValidationSummary`), Validation Errors table, Valid Orders preview table, download action |
| `/inventory-allocation` | `InventoryAllocationResult` | `UploadPanel` ×2, KPI strip (`AllocationSummary`), Allocation Results table, Backorders table, Remaining Inventory table, Supplier Follow-up table, download action |
| `/payment-aging` | `PaymentAgingResult` | `UploadPanel` + date selector, KPI strip (`PaymentAgingSummary`), aging bucket chart, Follow-up List table, Draft Messages preview, Data Issues section, download action |
| `/reports` | All 3 `ReportManifest`s (session-derived) | 3 `ReportCard`s, one per `report_type` |
```

Every route's "Consumes" column names an exact result envelope from Tutorials 03–06 — there is no
sixth route for something like "Analytics" or "Customers," because nothing in the Python core
produces a `CustomerRecord` or a cross-workflow analytics shape. This is `context/ui-rules.md`'s
own rule stated plainly: "Every page must map to Python output contracts. Do not invent KPI cards
or table columns that the Python core cannot produce" — applied here at the *route* level, before a
single table column is even planned.

The `/dashboard` route gets its own explicit scope note immediately below the table (lines 196–202):
a "read-only aggregate landing page composed strictly from existing outputs — no persisted
cross-workflow state, no new backend contract," with an explicit list of what's deliberately
excluded: "a global health score, a cross-workflow risk score, a unified operations queue,
historical trends — none of these have a Python source and would require persistence or new
business logic."

**Checkpoint:** If a future Phase (say, a Phase 11 that adds a new contract field) forgets to
update `context/ui-contract-plan.md`, how would that drift most likely be discovered — and is there
a way to make that discovery automatic rather than dependent on someone noticing?

<details>
<summary>Reveal answer</summary>

Today, discovery is manual and reactive — most likely, a developer building the actual Phase 9/10
component notices the plan doesn't have a field they need, or a code reviewer comparing a new PR's
`types/index.ts` against `ui-contract-plan.md` spots the gap. Nothing currently runs the Phase 7
verification script (or an equivalent) as part of CI, so a forgotten update wouldn't fail any
automated check — it would only surface the next time a human happened to compare the two documents
side by side, exactly the way the Reports lifecycle inconsistency in Part 6 was caught. Making this
automatic would mean committing a permanent version of the one-off diff script from Part 7 as a real
CI check, run whenever `src/contracts.py` or the three business modules change — turning "someone
might notice" into "the build fails until it's updated," the same shift Tutorial 03's deterministic
error-ordering discussion made for output order.
</details>

**Try it yourself:** Run `uv run pytest tests/test_contracts.py -v` and count the passing tests.
None of them assert anything about `context/ui-contract-plan.md` — confirm this by searching the
test file for the string `"ui-contract-plan"` and finding zero matches. This is direct proof of the
previous checkpoint's answer: the plan document and the Python test suite are not currently wired
together at all.

## Part 4 — Direct, derived, and direct/derived status labels

Open [`context/ui-rules.md`](../../../context/ui-rules.md) lines 117–139:

```markdown
## Status Badges

Every badge label is either **direct** (comes verbatim from a controlled-vocabulary Python
contract field) or **derived** (computed client-side from row/list membership or a display
transform of a direct field — never a new business rule). Full field-level detail and TypeScript
types: `context/ui-contract-plan.md`.

Order validation:

- direct (`ValidationErrorRow.severity`): `Error`, `Warning`
- derived (list membership in `valid_orders`/`errors`): `Valid`, `Has Errors`, `Has Warnings`

(The previous list — `Missing Field`, `Invalid SKU`, `Duplicate Order`, `Invalid Quantity`,
`Needs Review` — mistook error *categories* for row statuses...)

Inventory allocation:

- direct (`AllocationResultRow.status`): `Fully Allocated`, `Partially Allocated`, `Backordered`
- direct/derived (`RemainingInventoryRow.reorder_alert`, `Yes`/`No`): render as
  `Below Reorder Point` only when `reorder_alert = "Yes"` — this is a display label for the
  field, not a separate vocabulary
- derived (list membership in `supplier_follow_ups`): `Supplier Follow-up`
```

Three categories, not two — `explanation.md` §2 walks through why the first draft's binary
direct-vs-derived split wasn't enough. A first pass corrected only Order Validation and Reports
(the two groups with badges that had *no* real-field backing at all), leaving Inventory Allocation
and Payment Aging as "already correct" because a few labels spot-checked against real fields
(`Fully Allocated`, `Current`, `High`) turned out to be genuine values. The user's correction caught
something the spot-check missed: those labels *were* real, but sitting in the same list were labels
that weren't — `Below Reorder Point` (a display transform of `RemainingInventoryRow.reorder_alert`,
never a value that field literally holds — the field holds `"Yes"`/`"No"`) and `Supplier Follow-up`
(not a field value at all, just a signal that a row exists in a separate list).

**Checkpoint:** Explain, in your own words, why "the labels are factually correct" was not
sufficient justification for calling the Inventory Allocation and Payment Aging badge lists
"already correct."

<details>
<summary>Reveal answer</summary>

Factual correctness of the *individual* labels being checked said nothing about whether *every*
label in the list had the same property. A list can be a mix of genuinely-real values and
plausible-sounding invented ones, and spot-checking a handful of the real ones proves nothing about
the ones left unchecked. The actual standard this phase settled on is stricter than "the labels
happen to be correct" — it's "the *reason* each label exists is stated explicitly," which is what
would have caught `Below Reorder Point` and `Supplier Follow-up` immediately, since neither one has
a one-sentence "this is exactly the field value" answer the way `Fully Allocated` does.
</details>

**Checkpoint:** `Below Reorder Point` is described as "direct/derived" rather than purely one or the
other. What distinguishes a direct/derived hybrid from a purely derived label like
`Supplier Follow-up`?

<details>
<summary>Reveal answer</summary>

`Below Reorder Point` is *sourced* directly from one field's value (`reorder_alert`) — there's no
list membership or cross-row computation involved, just this one row's own field — but the label
text itself is a display transform, not the field's literal value (`reorder_alert` never contains
the string `"Below Reorder Point"`; it contains `"Yes"` or `"No"`). `Supplier Follow-up` is purely
derived: it has no field on the row it's describing at all — its entire existence depends on
checking whether a *matching* row exists in a separate list (`supplier_follow_ups`), which is a
membership computation, not a value transform of anything already on the row.
</details>

**Checkpoint:** If someone wanted to reintroduce a `Paid` badge for Payment Aging (removed in this
rewrite for having no defined derivation), what exact rule would you write, and where would it need
to be documented for it to meet this project's new standard?

<details>
<summary>Reveal answer</summary>

The rule: `Paid` when `outstanding_amount <= 0` — a direct/derived hybrid, the same shape as
`Below Reorder Point`, sourced from one field's value (`PaymentAgingRow.outstanding_amount`) but
displayed as a transformed label rather than the raw number. It would need to be added to *both*
places this phase keeps in sync: `context/ui-rules.md`'s Status Badges section (as a new
direct/derived bullet under Payment Aging, with the exact rule stated) and
`context/ui-contract-plan.md`'s Status Badges table (the equivalent cross-reference row). Adding it
to only one of the two would recreate exactly the kind of two-documents-disagree drift Part 6
covers for the Reports lifecycle.
</details>

**Try it yourself:** Run `grep -n "Overdue\|Due Soon\|Paid\b" context/ui-rules.md` from the repo
root. Confirm none of those three old, undefined Payment Aging labels survive anywhere in the
current file — the rewrite didn't just add correct labels alongside the old ones, it removed the
ones with no stated derivation.

## Part 5 — Tables and KPIs as declared projections

Open [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md) lines 232–239:

```markdown
**Payment Aging** (`PaymentAgingSummary`, mixed):
- Total Outstanding (`total_outstanding_amount`) — direct
- Overdue Amount (`overdue_amount`) — direct
- High Priority Count (`high_priority_count`) — direct
- Aging bucket chart (`aging_bucket_counts`) — direct, 5-way breakdown
- **"90+ Days Amount"** — the spec (`03_demo_payment_aging.md` §9) lists this as a 4th KPI
  card, but no summary field produces it: `aging_bucket_counts` is a *count* dict, not an
  *amount* dict. This is a **derived display-only aggregate**: sum
  `aging_rows[].outstanding_amount` where `aging_bucket === "90+ Days"`.
```

`PaymentAgingSummary.aging_bucket_counts` (`src/contracts.py:90`, computed at
`src/payment_aging.py:170–190`'s `_build_summary`) is a `dict[str, int]` — every bucket's *row
count*, nothing about dollar amounts. The demo spec's own UI section names a KPI ("90+ Days Amount")
that needs a *sum*, not a *count*, and no Python summary field currently produces that sum. Rather
than silently treat the spec's KPI as unsupported and drop it, or silently add a new Python field
to cover it, the plan does a third thing: names it explicitly as a **derived display-only
aggregate** — computed in the browser, from data the frontend already has, with the exact rule
spelled out.

Every one of the five entries in the Derived Display-Only Aggregates table (lines 289–303) follows
the same three-part template — source rows, source fields, grouping rule — spelled out, not implied:

```markdown
| Chart / value | Source | Rule |
|---|---|---|
| "90+ Days Amount" KPI | `PaymentAgingResult.aging_rows` | sum `outstanding_amount` where `aging_bucket === "90+ Days"` |
| "Gap to Reorder Point" (Dashboard Inventory Shortage Alerts) | `InventoryAllocationResult.supplier_follow_ups` | `reorder_point - remaining_qty`, per row. Display label only — never call this "suggested reorder quantity"... |
```

The "Gap to Reorder Point" entry's warning is the sharpest illustration of this Part's boundary:
`reorder_point - remaining_qty` is arithmetic over two fields the row already has — genuinely
display-only. "Suggested reorder quantity" sounds almost identical but is a different kind of claim
entirely: it would imply the system is *recommending a business action* (how much to reorder), which
no rule in `inventory_allocation.py` computes or validates. `SupplierFollowUpRow`
(`src/contracts.py:76–82`) has no such field, and inventing the label would silently promise a
business capability the Python core was never built to back.

> **System design — Derived/materialized view:** Every row in this table is the same general shape
> as a database materialized view or a spreadsheet's `SUMIF`: a value computed from already-stored
> rows via a fixed, named rule, kept separate from the rows it's computed *from*. The reason this
> phase insists on writing the rule down explicitly (source rows, source fields, grouping rule)
> rather than just implementing it later is the same reason a materialized view's defining query is
> versioned and reviewed — an aggregate with an implicit, undocumented rule is much easier to get
> subtly wrong (the wrong filter, the wrong grouping key) than one whose definition is written down
> once and can be checked against the real fields before any chart code exists.

**Checkpoint:** Walk through the "90+ Days Amount" KPI: why is
`sum(outstanding_amount) where aging_bucket === "90+ Days"` allowed as a derived aggregate, while a
hypothetical "customers at risk of churn" metric computed from the same rows would not be?

<details>
<summary>Reveal answer</summary>

The "90+ Days Amount" aggregate performs pure arithmetic — filtering and summing two fields
(`aging_bucket`, `outstanding_amount`) that `payment_aging.py` already computed and already put a
real business meaning behind. Nothing about the *meaning* of "customers whose invoices are 90+ days
overdue, summed" is invented by the aggregation step; the aggregation only reshapes already-decided
facts for display. "Customers at risk of churn" is a fundamentally different kind of claim — no rule
anywhere in `payment_aging.py` (or any other business module) defines what "at risk of churn" means,
what threshold triggers it, or what inputs it should weigh. Computing it client-side wouldn't be
reshaping an existing business decision for display — it would be *inventing* a new business
decision inside a presentation layer, exactly the failure mode Track 3's presentation-layer lessons
warned against, just one layer earlier (before any frontend code exists to make the mistake in).
</details>

**Checkpoint:** The plan documents each derived aggregate with an explicit source-rows/source-fields/
grouping-rule triple. What would be lost if a future contributor added a new chart to
`ui-contract-plan.md` without following that same documentation pattern?

<details>
<summary>Reveal answer</summary>

Without the triple, a reviewer (or a future self) reading the new chart entry would have no
mechanical way to verify the chart is genuinely display-only rather than a smuggled-in business
rule — the whole point of writing "source rows: X, source fields: Y, rule: Z" is that each part can
be independently checked against `src/contracts.py`: does field Y really exist on row type X, and
does rule Z only perform arithmetic/grouping rather than introduce a threshold or classification
Python never computed? An entry that just said "shows customers at risk" with no triple would hide
exactly the "Gap to Reorder Point" vs. "suggested reorder quantity" distinction this Part covers —
there'd be no structured way to catch the same mistake a second time.
</details>

**Try it yourself:** Open `context/ui-contract-plan.md`'s Derived Display-Only Aggregates table and
pick the "Outstanding amount by aging bucket" entry. Confirm its source field
(`PaymentAgingResult.aging_rows[].outstanding_amount`) and grouping key (`aging_bucket`, in the
fixed five-bucket order) both trace to real fields in `src/contracts.py`'s `PaymentAgingRow`. Then
compare it against `aging_bucket_counts` in the same summary — confirm the table's own note that
these are genuinely different aggregates (a *sum* vs. a *count*) over the same grouping key, not two
names for the same thing.

## Part 6 — Report lifecycle as browser state, not a Python contract field

Open [`context/ui-contract-plan.md`](../../../context/ui-contract-plan.md) lines 252–267:

```markdown
## Report Cards

One `ReportCard` per `report_type` (`order_validation`, `inventory_allocation`, `payment_aging`)
on `/reports`, mirrored on `/dashboard`.

Derived client-state model (UI-only, not Python-sourced), matching `context/ui-rules.md`'s
Reports badge lifecycle:

\`\`\`
Needs Input     -- underlying workflow hasn't run this session, no result envelope to export
Not Generated   -- envelope exists, export function not yet called
Processing      -- export function in flight
Ready           -- ReportManifest received; card shows file_name, sheet_names, generated_at,
                   download action
\`\`\`

An export failure reverts the card to `Not Generated` with a `BusinessErrorMessage` shown — no
separate persisted error state.
```

`explanation.md` §3 documents a mistake this exact section went through before landing on this
final shape — worth reading as a case study in verifying your own work, not just a historical
footnote. While writing `ui-contract-plan.md`'s Report Cards section, a four-state lifecycle was
designed independently: `not_generated → generating → ready → error`. This was written *before* the
corresponding `ui-rules.md` edit, and used different label text (`generating` instead of the
existing `Processing`, a new `error` state instead of the existing `Needs Input`) than what the
approved plan had actually specified.

The mismatch was caught by a specific, deliberate step: reading `ui-contract-plan.md`'s Report
Cards section side-by-side with the freshly-rewritten `ui-rules.md` Status Badges section, after
both were already written, and noticing the label sets didn't agree. `explanation.md` names why a
per-file review — checking each document against the source contracts in isolation — wouldn't have
caught this: both files, read individually against `src/contracts.py`, were internally
self-consistent and defensible; the *disagreement* only existed in the gap *between* them, which no
single-file check can see.

> **Design patterns — Finite state machine:** The final, reconciled Report Card lifecycle is a
> textbook finite state machine: four named states, one direction of normal travel
> (`Needs Input → Not Generated → Processing → Ready`), and exactly one failure edge
> (`Processing → Not Generated`, on export failure) — no fifth state, no cycle back from `Ready`
> except by starting a fresh export. Writing it out explicitly, in order, with its one failure
> transition named, is what makes "what happens if export fails" answerable by reading four lines
> instead of by tracing hypothetical component code that doesn't exist yet.

**Checkpoint:** Two documents (`ui-contract-plan.md` and `ui-rules.md`) were both edited in the same
session and ended up with different Reports lifecycle models before the inconsistency was caught.
What review step actually caught this, and why wouldn't a per-file review have found it?

<details>
<summary>Reveal answer</summary>

The catching step was a direct side-by-side comparison of the two documents' Reports-lifecycle
sections against *each other*, done after both had already been written — not a review of either
document in isolation against `src/contracts.py`. A per-file review wouldn't have found it because
neither file was individually wrong in a way that check would catch: `ui-contract-plan.md`'s
`not_generated → generating → ready → error` was a coherent, defensible four-state design taken on
its own, and so was `ui-rules.md`'s `Needs Input → Not Generated → Processing → Ready`. The defect
only exists as a *relationship* between the two documents (they don't use the same vocabulary for
the same concept), which is invisible to any check that only ever looks at one file at a time.
</details>

**Checkpoint:** Why was `error` deliberately not added as a fifth persisted lifecycle state, even
though report generation can genuinely fail? What's the tradeoff of reverting to `Not Generated`
instead?

<details>
<summary>Reveal answer</summary>

Adding a persisted `error` state would mean the frontend needs to remember *that* a specific export
attempt failed, independent of the card's current generate-ability — which is exactly the kind of
new client-side state the plan is trying to keep minimal, since nothing about a failed attempt is a
fact any other part of the system needs to know once the user has been shown the message. Reverting
to `Not Generated` (with a `BusinessErrorMessage` shown once, in the moment) keeps the state machine
at four states instead of five, and correctly reflects the only fact that actually matters
afterward: no successful export has happened yet, so the card's real capability (offer to try again)
is identical whether this is the first attempt or the second. The tradeoff: a user who navigates away
and back loses the specific error message, since it's ephemeral rather than persisted — an accepted
cost, since the underlying data needed to retry is untouched.
</details>

**Checkpoint:** If Phase 8 needs to show a user "your last 3 report generation attempts," would that
require a new Python contract field, or can it stay client-side? Justify your answer using the
Field Scope Boundary reasoning from this phase.

<details>
<summary>Reveal answer</summary>

It could stay entirely client-side, using the exact same reasoning that kept the four-state
lifecycle out of `ReportManifest`: "the last 3 attempts" is a fact about *this browser session's
interaction history*, not a fact any Python business rule computes or needs to know about — nothing
in `export_payment_aging_report()`'s signature or return value would need to change, since each
call is already stateless and returns everything a client-side history log would need to record
(a `ReportManifest` on success, an error message on failure). The Field Scope Boundary reasoning
applies directly: a contract may only contain fields its originating spec explicitly defines, and
nothing in `03_demo_payment_aging.md` (or any other spec) defines a persisted "attempt history"
concept — inventing one to support this UI feature would be adding business-facing scope through the
UI layer, exactly what Part 5's "suggested reorder quantity" near-miss also warns against.
</details>

**Try it yourself:** Run `grep -n "generating\|not_generated" context/ui-contract-plan.md` from the
repo root. Confirm zero matches — the lowercase, four-word first-draft vocabulary this checkpoint
discusses doesn't survive anywhere in the current file; only the reconciled, capitalized
`Needs Input`/`Not Generated`/`Processing`/`Ready` vocabulary remains.

## Part 7 — Documentation drift as a testable defect

Open [`tests/contract_fixtures.py`](../../../tests/contract_fixtures.py) lines 164–170 and
[`src/report_export.py`](../../../src/report_export.py) lines 185–195:

```python
REPORT_MANIFEST_FIXTURES: list[ReportManifest] = [
    {
        "report_id": "rpt-order_validation-20260709091500",
        "report_type": "order_validation",
        "file_name": "order_validation_report.xlsx",
        "generated_at": "2026-07-09T09:15:00",
        "sheet_names": ["Summary", "Valid Orders", "Validation Errors", "Original Orders"],
    },
    ...
```

```python
def _build_manifest(
    report_type: str, file_name: str, sheet_names: list[str], generated_at: datetime
) -> ReportManifest:
    report_id = f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"
```

`docs/plan/phase-7-ui-contract-wireframe-planning/explanation.md` §4 documents a real bug this
phase found while grounding `ReportManifest` examples in `tests/contract_fixtures.py`, as the
approved plan required: at the time, `REPORT_MANIFEST_FIXTURES`'s `report_id` values (like
`"rpt-order-validation-20260709-001"`) didn't match what `_build_manifest()` actually produces
(`f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"`, e.g.
`"rpt-order_validation-20260709091500"`) — a hyphenated `report_type` with a fake sequence suffix,
versus the real underscored `report_type` with a full `HHMMSS` timestamp and no sequence at all.

**The Phase 7 decision, as it actually happened:** fixing this would mean editing
`tests/contract_fixtures.py` — a Python test-data file — during a phase whose explicit mandate is
docs-only. The resolution was to source `ReportManifest` examples from the real exporter and its
test file instead, document the mismatch explicitly with both formats shown side by side, and flag
it as a follow-up for whoever next touches Phase 2 or Phase 6 test data, rather than silently fixing
it without dedicated review or silently working around it.

**Where the bug stands today:** the fixture excerpt above already shows the *corrected* format —
`"rpt-order_validation-20260709091500"`, not the old hyphenated version `explanation.md` describes
finding. A later, separate commit (`aca6762`, "fix: align ReportManifest fixture report_id with real
exporter format") fixed exactly this bug after Phase 7 ended, and added a permanent regression test.
Open [`tests/test_contracts.py`](../../../tests/test_contracts.py) lines 230–238:

```python
def test_report_manifest_fixture_ids_match_exporter_format():
    for manifest in REPORT_MANIFEST_FIXTURES:
        timestamp = (
            manifest["generated_at"]
            .replace("-", "")
            .replace(":", "")
            .replace("T", "")
        )
        assert manifest["report_id"] == f"rpt-{manifest['report_type']}-{timestamp}"
```

This test reconstructs the exact format `_build_manifest()` produces from each fixture's own
`generated_at` field and asserts the fixture's `report_id` matches — the fixture can never drift from
the real exporter format again without this test failing. `context/ui-contract-plan.md`'s own
**Data-accuracy note** (just below the `ReportManifest` TypeScript block) was updated to match:
"`tests/contract_fixtures.py`'s `REPORT_MANIFEST_FIXTURES` now matches the real exporter format...
`tests/test_contracts.py` includes a regression assertion." This is the concrete answer to
`ai-discussion-topics.md`'s Question 3 (Part 3, above) playing out for real, on this exact bug — the
"someone might notice" gap became "the build fails until it's fixed," just not within Phase 7's own
scope.

**Checkpoint:** The fixture/exporter `report_id` mismatch was found, documented, but not fixed in
Phase 7 itself. What's the argument for fixing it immediately instead of flagging it as a follow-up?
What's the argument against?

<details>
<summary>Reveal answer</summary>

Fixing it immediately would mean the plan's own examples are correct from the moment they're
written, and nothing downstream (a future Phase 9 developer copying a fixture value into a mock)
risks propagating the wrong format even briefly. The argument against — the one Phase 7 actually
followed — is scope discipline: `tests/contract_fixtures.py` is Python test data, entirely outside a
docs-only phase's stated mandate, and a fix made under time pressure to "just get the docs phase
unblocked" is exactly the kind of unreviewed, out-of-scope change `CLAUDE.md`'s module-boundary
rules exist to prevent. The eventual real fix (`aca6762`) landed as its own dedicated commit, later,
with its own regression test — a cleaner outcome than a fix squeezed into a phase that wasn't
scoped to touch that file.
</details>

**Checkpoint:** If you were the next person to fix `tests/contract_fixtures.py`'s
`REPORT_MANIFEST_FIXTURES`, what would you need to check beyond just updating the `report_id`
string format?

<details>
<summary>Reveal answer</summary>

Every other field the fixture claims, cross-checked against what the real exporter and its test
suite actually produce — not just `report_id`. Concretely: does `sheet_names` for each report type
still match the real, current sheet-writing order in each `export_*_report` function (Tutorial 06
covered why sheet order is itself a tested contract, not an accident); does `generated_at`'s ISO
format match `generated_at.isoformat(timespec="seconds")`'s real output; does `file_name` match the
literal string each export function passes to `_build_manifest`. The `report_id` bug is a useful
signal that the fixture was drafted by hand rather than derived from the real code — the same
suspicion should extend to every other field in the same fixture, not just the one already caught.
</details>

**Checkpoint:** This bug was only found because the plan required grounding examples in real
fixture data rather than inventing plausible-looking examples. What's a general argument for why
"ground every example in real data" is worth the extra friction it creates?

<details>
<summary>Reveal answer</summary>

An invented, plausible-looking example can be wrong in a way nothing will ever catch, because
nothing checks it against anything real — it only has to look right to a human reader, forever. An
example required to trace back to a real fixture or a real function's actual output creates a
structural opportunity to catch drift, even when (as happened here) the *fixture itself* turns out
to be wrong: grounding in real data doesn't guarantee correctness on the first pass, but it means
every example is checkable against something, rather than being a dead end no future audit could
ever verify. The extra friction (finding and reading the real fixture, discovering it disagrees with
the real exporter) is exactly the cost of that checkability — a cost this bug shows was worth
paying.
</details>

**Try it yourself:** Run `uv run pytest tests/test_contracts.py -k manifest -v` and read both
passing test names. Then run
`git log --oneline -S"test_report_manifest_fixture_ids_match_exporter_format" -- tests/test_contracts.py`
and confirm the one commit that introduced this regression test is a separate, later commit from
Phase 7's own `docs: add Phase 7 UI contract and wireframe plan` commit — direct proof the fix
happened after this tutorial's phase ended, not during it.

## Full data flow: tracing `follow_up_priority` from a Python field to a planned badge

1. **The value is computed.** `src/payment_aging.py:128–140`'s `_follow_up_priority()` evaluates
   an ordered chain (Paid → High → Medium → Low → Watch → None, Tutorial 05 Part 6) and returns one
   of exactly five strings.
2. **The value is stored in the contract.** `src/contracts.py:103`:
   `follow_up_priority: str` inside `PaymentAgingRow` — a plain string at the Python type level,
   with the *real* constraint (only five possible values) living entirely in step 1's function body,
   not in this type declaration (Part 2).
3. **The value is mirrored, and narrowed, into TypeScript.**
   `context/ui-contract-plan.md:142`:
   `follow_up_priority: "High" | "Medium" | "Low" | "Watch" | "None";` — the plan reads the Python
   *logic*, not just the Python *type*, to write a stricter TypeScript type than the source it
   mirrors (Part 2).
4. **The value is named in the Table Column Plan.**
   `context/ui-contract-plan.md:220`: `Follow-up Priority (StatusBadge)` — one of the eleven planned
   columns for the Payment Aging rows table, explicitly flagged to render as a `StatusBadge`
   component (Part 5).
5. **The value is classified in the Status Badges cross-reference.**
   `context/ui-rules.md:136–137` and `context/ui-contract-plan.md:249`: listed as **direct** — no
   derivation rule needed, because the field itself is already a controlled vocabulary (Part 4).
6. **The value reaches the planned page.**
   `context/ui-contract-plan.md:193`: the `/payment-aging` route's "Composes" column names a
   "Follow-up List table" — Tutorial 05's guided trace already showed `FOLLOW_UP_PRIORITIES`
   (`src/report_export.py:84`) filtering `aging_rows` by this exact field for the Excel report's
   "Follow-up List" sheet; the planned frontend table reuses the identical filter concept for a
   browser view of the same data.

**Contrast — the derived `Supplier Follow-up` label takes a structurally different path.** It has no
step 1 or step 2 at all: no function computes a "Supplier Follow-up" value, and no `TypedDict` field
holds it. Its origin is `InventoryAllocationResult.supplier_follow_ups` (`src/inventory_allocation.py:395,`
401–403) — a *separate list*, populated only when `_build_remaining_inventory_row()`
(`src/inventory_allocation.py:336–366`) decides a `RemainingInventoryRow` needs a matching
`SupplierFollowUpRow`. The badge doesn't read a field's *value*; it checks *list membership* — "does
a row for this SKU/warehouse exist in `supplier_follow_ups`" — which is exactly the direct-vs-derived
distinction Part 4 draws, made concrete across two genuinely different data-flow shapes.

## Extend it (challenges)

**Challenge 1 — Trace** (15–20 min): Pick one KPI and one badge you haven't already traced in this
tutorial — for example, the "Low Stock SKUs" KPI tile (`AllocationSummary.low_stock_sku_count`) and
the `Valid` badge (Order Validation). For each, write out the exact chain from Python field (or
list) → `ui-contract-plan.md`'s TypeScript type → its entry in the Table Column Plan or KPI Card
Mapping → its entry in the Status Badges cross-reference. Confirm both are classified correctly
(direct, derived, or direct/derived) per Part 4's definitions.

<details>
<summary>Hint</summary>

`low_stock_sku_count` is computed in `src/inventory_allocation.py`'s `allocate_inventory()` from a
`set` of SKUs (Tutorial 04 Part 7 covered this — it's a *distinct-SKU* count, not the same number as
`len(supplier_follow_ups)`). `Valid` has no backing field at all — it's derived purely from whether a
row appears in `valid_orders` rather than `errors`, the same list-membership shape as
`Supplier Follow-up`.
</details>

**Challenge 2 — Extend** (20–30 min): Design one new, allowed display-only aggregate for this
project, using the exact source-rows/source-fields/rule template from Part 5 (`| Chart / value |
Source | Rule |`). It must be pure arithmetic or grouping over fields that already exist in
`src/contracts.py` — no new business interpretation, no invented threshold, no recommendation. A
reasonable starting idea: "average `days_overdue` across every row with `follow_up_priority = High`."
Write the exact table row, then justify in one sentence why it doesn't cross into the same territory
as the rejected "suggested reorder quantity."

<details>
<summary>Hint</summary>

An average is still pure arithmetic over an existing field (`days_overdue`) filtered by an existing
field's exact value (`follow_up_priority`) — no new classification, no new threshold invented. Watch
for the trap this Part explicitly names: don't phrase your aggregate's *label* in a way that implies
a recommendation or judgment ("customers we should worry about") rather than a plain description of
what was computed ("average days overdue, High priority").
</details>

**Challenge 3 — Break and fix / Design** (30–45 min): In a scratch copy of
`context/ui-contract-plan.md` (don't edit the real file), rename one TypeScript field —
change `PaymentAgingRow.follow_up_priority` to `followUpPriority` — leaving everything else
untouched. Design a mechanical check (a script, following the same shape as Phase 7's own one-off
diff script from Part 2/3, which was never committed to this repo) that would catch this specific
rename as a drift. Specify: what does your check extract from each side (the TypeScript file, the
Python source), and what exact comparison would fail? You don't need to write runnable code — a
precise, step-by-step design is the deliverable, mirroring Tutorial 01 Challenge 3's "design, don't
necessarily implement" framing.

<details>
<summary>Hint</summary>

The real Phase 7 script (per `explanation.md` §5) extracted field names via regex from two different
syntaxes — TypeScript `type` blocks and Python's dual `name: type` (`TypedDict`) / `"name":`
(dict-literal) syntax — then diffed the two resulting sets. Your design needs to specify exactly
which regex pattern would match `follow_up_priority:` inside a `type` block, and confirm that
`followUpPriority:` would extract a *different* string that has no match in the Python-side set —
that mismatch, surfacing as "in TypeScript but not in Python," is what a diff-based check would
report as the rename's symptom.
</details>

For deeper exploration,
`docs/plan/phase-7-ui-contract-wireframe-planning/ai-discussion-topics.md` has all 15 prompts this
tutorial's checkpoints were woven from, organized under their original four headings (documentation
drift, the Status Badges rewrite, the Reports lifecycle inconsistency, and derived aggregates/scope
discipline). Feed them to an LLM *after* forming your own answer first — the gap between what you
thought and what you learn is where understanding lands.
