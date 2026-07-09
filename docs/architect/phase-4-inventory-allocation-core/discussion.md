# Phase 4: Inventory Allocation Core — Discussion Record

A full teaching account of the reasoning behind the `/architect` session for Phase 4, including
the parts that got revised after the plan was first rejected. Written for someone who wasn't in
the room and has forgotten all of this.

---

## Why the research phase used two agents in parallel, not one

The session opened by fanning out two `Explore` agents at once rather than reading files
sequentially. One agent's job was purely textual: read `CONTEXT.md`'s glossary, the full
`02_demo_inventory_allocation.md` spec (every rule ID, every version label, the test-case
table), the five relevant `contracts.py` TypedDicts, and their hand-authored example values in
`tests/contract_fixtures.py`. The other agent's job was purely architectural precedent: read
`order_validation.py` end to end for its module structure and helper-function patterns, read
`excel_io.py` for the loader convention, and read `sample_data.py` for the *exact* column names
the sample inventory workbook actually uses.

The reason for splitting this way rather than, say, splitting by file count: the two agents
were answering genuinely different questions — "what does the business logic need to do?" and
"what does the existing codebase's shape look like?" — and neither needed the other's findings
to do its job. Running them in parallel wasn't just faster; it kept each agent's report focused,
since neither had to hold the other's context in its head while summarizing. The tradeoff is
that the main conversation had to wait for both to finish before it could reason about anything
requiring information from both reports (e.g. "does the sample inventory data's column names
match what the spec claims" — a cross-check that could only happen once both reports were in).

## The language-alignment gap: where the glossary and the spec disagree

`CONTEXT.md` is the project's domain glossary, and it's normally the first stop for "what does
this term mean." But this session found a gap in it: **Warehouse**, **Reorder Point**, and
**Reorder Alert** have no standalone glossary entries — they only appear folded into the
"Inventory Record" and "Supplier Follow-up" definitions. That's a minor structural gap. The
more consequential one: the glossary's own definition of **Supplier Follow-up** is *broader*
than what any numbered rule in the spec actually implements — it says "created when stock is
low, backordered, or below reorder point," a three-way disjunction, while IA-008 (the only rule
that defines a trigger at all) only covers the third case.

This matters because a glossary is descriptive prose, written to give a general sense of a
concept — it isn't a numbered, version-labeled rule the way IA-001 through IA-008 are. The
project's Scope Gate discipline ("implement only V1/unlabeled numbered rules") only has teeth
if glossary prose is treated as color commentary, not as an independent source of additional
scope. If glossary descriptions were treated as equally authoritative, you'd have no way to
tell "this needs implementing" from "this is helpful context the author was gesturing at" —
every generously-worded glossary entry would quietly expand what the module has to do.

## Deep dive: why "highest available quantity" isn't as literal as it reads

IA-007 V1 says: allocate from "the warehouse with the highest available quantity for that SKU."
Read with no other context, that's unambiguous — go find `available_qty`, pick the max. The
catch is that IA-002, one rule earlier in the same spec, has already defined a *derived*
quantity — `allocatable_qty = available_qty - reserved_qty` — as the thing that actually
determines how much of an order can be filled. The spec never says "IA-007 means the raw
column" or "IA-007 means the derived value." It just reuses ordinary English ("available
quantity") for a concept the spec itself had already given a more precise technical name to one
rule earlier.

Think of it like a recipe that defines "ripe tomatoes" as a technical term in step 2 ("tomatoes
that yield to gentle pressure and have no green near the stem"), then in step 5 just says "use
the tomatoes" — does step 5 mean *any* tomatoes on the counter, or the ripe ones step 2 was
building toward? Nothing in the text of step 5 forces either reading; you resolve it by asking
which reading makes the recipe internally consistent.

The concrete failure mode if you pick the literal/raw reading: imagine SKU `X` sits in two
warehouses. Warehouse A shows `available_qty=50, reserved_qty=48` (2 units actually free).
Warehouse B shows `available_qty=20, reserved_qty=0` (20 units actually free). Raw-`available_qty`
selection sends every order for SKU `X` to Warehouse A — the warehouse that can least fulfill
it — while Warehouse B, sitting on ten times the usable stock, never gets picked at all. No
exception fires. No test would catch this unless it specifically constructed a scenario where
raw and allocatable quantities disagree in rank order — which is exactly why
`test_reserved_stock_reduces_allocatable_qty` and `test_warehouse_choice_switches_as_stock_depletes`
were written to exercise scenarios where `reserved_qty` actually changes which warehouse looks
best.

## Deep dive: why allocation has to be sequential and stateful

A tempting shortcut for "allocate orders against inventory" is to treat it as a batch
computation: group all orders by SKU, group all inventory by SKU, and compute some kind of
distribution — proportional, first-come, whatever — in one vectorized pass over the whole
dataset. Pandas rewards this instinct; a lot of the codebase's other logic (validation, for
instance) really is a pure per-row computation with no cross-row dependency beyond duplicate
detection.

Inventory allocation doesn't have that property, and the reason is IA-001. Priority ordering
isn't a tiebreaker applied *after* computing some fair-share distribution — it's the primary
axis the whole batch has to respect. If a High-priority order and a Normal-priority order both
want the last 10 units of a SKU, the correct outcome is "High gets all 10, Normal gets 0 and is
backordered," not "each gets 5" and not "whichever appears first in the file gets 10." The only
way to guarantee that outcome is to process orders one at a time, in IA-001's exact sort order,
letting each line's allocation immediately and permanently reduce the balance the *next* line
will see.

This is implemented by literally mutating a shared dict in place:

```python
chosen["allocatable_qty"] -= allocated_qty
chosen["allocated_qty"] += allocated_qty
```

`chosen` here is the *same dictionary object* stored inside `inventory_by_sku[sku]` — not a
copy. So when the next order line for the same SKU looks up its candidate warehouses, it's
looking at post-allocation state automatically, with no need to re-fetch or explicitly pass a
running balance around. This is a deliberate, narrow use of mutable shared state inside a
single function call — code-standards.md's "no hidden global state" rule is about state that
leaks *across* calls or modules; a private, function-scoped mutation that's fully consumed and
discarded when `allocate_inventory()` returns doesn't violate that principle, but it's worth
being explicit about why it's here rather than a pure/functional alternative: threading an
immutable balance dict through the loop and returning a new one each iteration would work
identically and might be easier to reason about in isolation, at the cost of more allocation
churn and slightly more code. This tradeoff is flagged directly in
`ai-discussion-topics.md` #6.

One consequence worth naming explicitly: because warehouse choice is *re-evaluated per line*,
not decided once per SKU, the same SKU can be fulfilled from different warehouses across
different lines in the same batch, as stock depletes. `test_warehouse_choice_switches_as_stock_depletes`
exercises this directly — an order for 15 units picks HK Warehouse (20 available) over SG
Warehouse (10 available); once HK drops to 5, the *next* order for the same SKU picks SG
instead, because SG's now-untouched 10 beats HK's depleted 5. Nothing about this is stated
directly in the spec's rule text — it falls out mechanically from applying IA-007 fresh, per
line, against continuously-updated state.

## Deep dive: inferring behavior from a fixture instead of from spec text

The spec's own test-case table (§11) never describes what should happen to the `warehouse`
field when an order line is fully backordered, or when a SKU has no inventory rows at all.
Normally the fallback for "the spec is silent" is first-principles reasoning from the rest of
the document. Here, a different kind of evidence was available: `tests/contract_fixtures.py`
was written during Phase 2 — *before Phase 4's business logic existed* — specifically to prove
the contract shapes could hold believable example data. Its `BACKORDER_ROW_FIXTURE` already
had `"warehouse": "HK Warehouse"` on a row with `"allocated_qty": 0`.

This raises a real epistemic question, discussed explicitly in `ai-discussion-topics.md` #5:
is a hand-authored fixture from an earlier phase *evidence* of intended behavior, or just one
person's guess at the time, carrying no more authority than any other inference you might make?
The position taken in this session: it's evidence worth weighting, but not overriding — the
decision to still populate `warehouse` on a backorder was ultimately justified by an independent
operational argument ("useful routing hint for when stock arrives") that happened to *agree*
with the fixture, not by treating the fixture as authoritative on its own. Had the fixture
suggested something operationally nonsensical, the right move would have been to flag the
conflict rather than defer to it blindly. The fact that the fixture and first-principles
reasoning converged here made this an easy call; it wouldn't always be.

## Deep dive: Scope Gate discipline applied to a glossary-vs-rule conflict

This project's Scope Gate rule (documented in `CLAUDE.md` and `CONTEXT.md`) exists to stop
"reasonable-sounding" scope creep — the risk isn't usually a rule you'd obviously reject, it's
a rule that sounds so natural you implement it without noticing it was never actually specified.
The Supplier Follow-up trigger-scope decision is a clean example: nobody was proposing anything
exotic by suggesting "also flag backordered lines for follow-up" — it's a completely reasonable
feature, and the glossary practically invites it ("...or backordered..."). The discipline here
isn't "reject reasonable ideas" — it's "implement only what a numbered V1/unlabeled rule
actually specifies, and treat anything else, however reasonable, as a candidate for a *new ADR*,
not a default."

The concrete cost of skipping that discipline here wouldn't have been abstract. `SupplierFollowUpRow.reorder_point`
is typed as a required `int`, not `NotRequired[int]`, in `contracts.py`. A backordered line with
no known `reorder_point` literally has no valid value to put in that required field — expanding
the trigger would have forced an immediate, unplanned decision about whether to loosen that
contract (itself an ADR-worthy change) or fabricate a placeholder value (a worse outcome:
manufacturing data that looks meaningful but isn't). Catching the scope question *before* writing
code avoided backing into that fork mid-implementation.

## The correction round: what the first rejected plan got wrong, and why each catch matters

The first version of the plan was rejected by the user, not because the four headline decisions
were wrong, but because of gaps the user's own review caught — a useful reminder that an
approved architectural framework doesn't mean every operational detail inside it has been
thought through.

**Branching state was assumed, not verified.** The plan's original last step said "branch off
`main` (now that PR #1 is merged)." That was true about PR #1, but the plan silently assumed PR
#2 (Phase 3) had *also* merged by the time Phase 4 execution actually happened, and that local
`main` was up to date. Neither was safe to assume — PR #2 was still open, and local `main` was
stale by two commits. Branching from it as originally planned would have produced a Phase 4
branch **missing `src/order_validation.py` entirely**, along with the 63-test baseline Phase 4
depends on. This is the same "verify before recommending" discipline that applies to memory
recall (a fact that was true when written may not be true now) applied to git state instead —
the fix wasn't a different branching *strategy*, it was making the branching step check reality
at execution time rather than encode an assumption made at planning time.

**`low_stock_sku_count` had an ambiguity the original decisions didn't cover.** None of the
four `AskUserQuestion` decisions had addressed how to *count* low-stock SKUs for the summary
KPI — it was assumed to be "obviously" the number of follow-up rows. The user caught that this
undercounts nothing but *overcounts* multi-warehouse SKUs: `MED-LENS-001` alerts in both HK and
SG Warehouse in the real sample data, so a naive `len(supplier_follow_ups)` would report "2
low-stock SKUs" for what's actually one product needing attention. This is structurally the
*same bug class* Phase 3 already had to solve once, for `ValidationSummary.invalid_orders`
(computed as a distinct-row `set`, not summed from `duplicate_orders + invalid_skus +
missing_field_count`, to avoid double-counting a row that fails multiple rules). Seeing the same
shape of bug reappear in a different module is itself a signal — it's the kind of thing worth
generalizing into a checklist item rather than re-discovering ad hoc each phase (see
`ai-discussion-topics.md` #20).

**The reorder boundary (`<` vs `<=`) is a one-value blind spot.** Every test case in the spec's
own §11 table, and every one of the four original decisions, happens to produce identical output
whether the reorder-alert comparison uses `<` or `<=` — because none of them land exactly on the
threshold. The user specifically asked for a test covering `remaining_qty == reorder_point`
precisely because that's the one input where the two implementations diverge, and nothing in
the existing plan would have caught choosing the wrong one. This is a general lesson about
boundary conditions: a comparison operator's off-by-one behavior is invisible in aggregate test
coverage unless a test is deliberately constructed to sit exactly on the boundary.

**Malformed inventory data needed an explicit failure-mode decision, and it deliberately
*breaks* Phase 3's own precedent.** Phase 3 converts every malformed value into a business
-readable `ValidationErrorRow` rather than raising — but that's only possible because
`contracts.py` defines an output surface (`ValidationErrorRow`) for exactly that situation.
Phase 4 doesn't have an equivalent (`InventoryDataIssueRow` doesn't exist), so mechanically
copying Phase 3's "never raise" pattern here would mean silently defaulting a malformed
`available_qty` to something — and there's no safe default. Zero would make a warehouse look
phantom-empty; skipping the row would make it disappear from `remaining_inventory` and
`supplier_follow_ups` with no trace. The user's instruction to raise a business-readable
exception instead is the right resolution specifically *because* the two phases have genuinely
different available output surfaces — it's not an inconsistency, it's each module correctly
using the contract surface it actually has.

**The sanity-check verification needed an extra step the plan hadn't spelled out.** The original
plan's verification section said to sanity-check `allocate_inventory()` against
`sample_data/sample_orders.xlsx` directly. The user caught that this file, by design (per Phase
2's deliberate imperfections), is *not* fully valid on its own — it contains one duplicate
`order_id` and one unknown SKU specifically so Phase 3's validation rules have something to
catch. Feeding it straight into `allocate_inventory()` would allocate against invalid order
rows Phase 3 was supposed to filter out first. The corrected verification chain routes the
sample file through `load_orders` → `load_product_master` → `validate_orders()` first, and
only passes the resulting `valid_orders` list (converted to a DataFrame) into
`allocate_inventory()` — mirroring how Phase 4 would actually be invoked downstream of Phase 3
in a real pipeline.

## What the final sanity check actually proved (and didn't)

After the corrected plan was approved and implemented, running that exact verification chain
against the real sample data reproduced the values in `tests/contract_fixtures.py`
field-for-field: order `SO-2026-008` for `MED-LENS-001` came out as `requested_qty=25,
allocated_qty=20, backorder_qty=5, warehouse="HK Warehouse", status="Partially Allocated"` —
matching `ALLOCATION_RESULT_ROW_FIXTURE` exactly, including `supplier_name` and `lead_time_days`
on the resulting `SupplierFollowUpRow`.

It's worth being precise about what this confirms and what it doesn't. It's strong evidence
that the implementation's *shape* matches what the Phase 2 fixture author (working from the
same spec, months earlier, with no implementation to check against) independently expected the
correct output to look like — a genuine, non-trivial confirmation, since the fixture wasn't
written to match this code. What it does *not* prove is that every rule is correct in every
case — it's one scenario, driven by one sample dataset, and the actual proof of correctness is
the 22 tests in `tests/test_inventory_allocation.py`, each targeting one rule or one edge case
in isolation. The sanity check is a plausibility check on the whole system working together;
the test suite is the actual specification-conformance evidence.
