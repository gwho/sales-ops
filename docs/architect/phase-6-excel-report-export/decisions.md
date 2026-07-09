# Phase 6: Excel Report Export — Architect Session Decisions

Two `Explore` agents researched the specs, contracts, and Phase 3–5 source in parallel
before any decision was asked. One round of four `AskUserQuestion` decisions was
resolved normally; a second round was rejected by the user (a tool-use rejection, not a
substantive "no") and replaced with the user's own written corrections against the
plan draft. Below is every decision, in the order it was locked, with why it mattered
and what the alternative would have cost.

## 1. Export functions accept envelopes, not raw DataFrames

**The decision:** `export_order_validation_report(result: OrderValidationResult, ...)`,
and the two allocation/aging equivalents, take the already-built result envelope each
business module returns — not the separate `valid_orders_df`, `validation_errors_df`,
etc. that `01_demo_order_validation.md` §10–11's suggested signatures literally show.

**Why this over the alternative:** The research pass found that `validate_orders()`,
`allocate_inventory()`, and `calculate_payment_aging()` all already return a single
JSON-serializable `TypedDict` envelope (`OrderValidationResult`,
`InventoryAllocationResult`, `PaymentAgingResult`) — this was locked by Phases 3–5, not
a Phase 6 decision. If `report_export.py` took separate DataFrames instead, every real
caller would have to destructure an envelope it already has back into pieces, just so
`report_export.py` could reassemble them — a pointless round-trip that also duplicates
field typing already pinned in `contracts.py`. The specs' suggested signatures predate
the envelope pattern Phase 3 established; they're implementation suggestions, not a
contract, exactly as Phase 5's decision #1 already established for the same kind of
spec-vs-established-pattern conflict.

**What the alternative would have cost:** Every caller — tests, and eventually a
FastAPI route — would need boilerplate to re-split an envelope it already holds, and
`report_export.py` would need to re-derive field names DataFrame-column-by-column
instead of trusting the TypedDict shape it's handed.

## 2. Each export function returns `tuple[bytes, ReportManifest]`

**The decision:** Not just workbook bytes (as the specs' suggested signatures show),
but bytes *and* a freshly-built `ReportManifest` in one call.

**Why this over the alternative:** `report_export.py` is the only code that knows, at
the moment of writing, what sheets it actually created, what the file name is, and
when it ran — a caller building the manifest separately would have to duplicate that
knowledge (and could drift out of sync with the real sheet list if the export logic
ever changed). `context/library-docs.md`'s note that the future
`GET /api/reports/{report_id}` route needs to "return downloadable Excel files for
reports" also implies the route needs both the bytes to serve and the manifest to
register the report — returning both from one call avoids a second orchestration step.

**What the alternative would have cost:** A second function (or inline caller logic)
re-deriving `sheet_names` from the same list of sheet-writing calls `report_export.py`
already made — one more place for the two lists to silently disagree.

## 3. Workbooks are built in memory, never written to disk inside the module

**The decision:** `io.BytesIO()` buffer, `wb.save(buffer)`, return `buffer.getvalue()`.

**Why this over the alternative:** `report_export.py`'s job per `code-standards.md`'s
module-boundary table is "Excel workbook generation from already-computed outputs" —
nothing in that boundary includes file-system responsibility, and giving it one would
mean the module also owns decisions like output directory, filename collision
handling, and cleanup, none of which are Phase 6's problem. Keeping it in-memory
matches the specs' own suggested return type (`-> bytes`) and slots directly into a
future HTTP response body without any intermediate file.

**What the alternative would have cost:** A module boundary violation the moment a
future FastAPI route needed to persist reports somewhere — that's a routing/storage
concern, not a report-generation concern, and mixing them would make `report_export.py`
harder to unit test (tests would need a scratch directory instead of just reading
bytes back with `openpyxl.load_workbook`).

## 4. `operations_follow_up_pack.xlsx` is excluded from Phase 6

**The decision:** The combined 9-sheet workbook `build-plan.md` calls "optional" is
not built this phase.

**Why this over the alternative:** Tracing the feature to its actual source —
`05_integration_and_app_flow.md` §7 — found it explicitly labeled **V1.5**, not V1.
`build-plan.md`'s casual "optional" phrasing doesn't override the Scope Gate, which
this project treats as a mechanical check (grep the spec for a version label), not a
judgment call — the same rule that already excluded IA-007's region-matching
preference in Phase 4. Building it without a new ADR would be implementing V1.5 work
under cover of a Phase 6 checklist item that only mentions it as "optional," exactly
the kind of scope creep the Scope Gate exists to catch.

**What the alternative would have cost:** A feature shipped without the ADR process
the project's own non-negotiable rules require for anything above V1 — and a 9-sheet
workbook whose 9th sheet (`CRM Data Issues`) depends on the entirely-out-of-scope CRM
Cleaner module, compounding one scope violation with a second.

## 5. `original_orders_df` is optional, but `Original Orders` is never optional

**The decision:** `export_order_validation_report(result, original_orders_df:
pd.DataFrame | None = None, ...)`. The `Original Orders` sheet is **always** created —
populated when a DataFrame is passed, empty (header-only) when it isn't. There is no
branch that omits the sheet.

**Why this over the alternative:** This decision changed shape mid-session. The
`AskUserQuestion` round initially framed it as "required in practice," but the user's
written correction on the plan draft caught an internal inconsistency: a `None`-typed
optional parameter combined with prose describing "required" behavior is a
contradiction — either the type says it can be absent, or the described behavior does,
not both. The fix makes both consistent: the parameter really can be `None` (so
isolated unit tests of the other three sheets don't need to fabricate an orders
DataFrame just to satisfy the signature), but the *sheet* is never conditionally
dropped from the workbook, because `Original Orders` is locked into
`REPORT_MANIFEST_FIXTURES`'s `sheet_names` list for `order_validation` — a workbook
missing it would fail every manifest-shape test the moment someone passed `None`.

**What the alternative would have cost:** A `None` input silently changing the
workbook's sheet count depending on an implementation detail unrelated to the sheet
names contract — the exact "shape asymmetry that isn't spec-driven" the project's
Field Scope Boundary principle warns against, here applied to sheet presence instead
of contract fields.

## 6. `Follow-up List` uses an explicit priority allow-list, not a `!= "None"` exclusion

**The decision:** `row["follow_up_priority"] in {"High", "Medium", "Low", "Watch"}`,
not `row["follow_up_priority"] != "None"`.

**Why this over the alternative:** Both filters produce identical output for
well-formed data — `PaymentAgingSummary.aging_bucket_counts` and every test in Phase 5
only ever produce one of exactly five priority strings. The difference only shows up
on malformed input: a `!=` check *includes by default* — any unexpected string that
isn't literally `"None"` ends up in the follow-up list. An allow-list *excludes by
default* — an unexpected string is silently kept out of the list rather than shown to
a sales rep as something requiring follow-up. Given `Follow-up List` is presentation
over already-validated `payment_aging.py` output (which only ever emits the five known
strings), this is a defense-in-depth choice for a module boundary, not a response to
any known bug.

**What the alternative would have cost:** Nothing today, since `payment_aging.py`'s
output is already constrained — but a future change to that module (e.g., adding a
sixth priority tier) would silently start appearing in `Follow-up List` under the `!=`
version without anyone deciding it should, whereas the allow-list version would
silently *exclude* it instead, which is the safer failure direction for a report a
human reads and acts on.

## 7. `report_id` is timestamp-based, not sequential

**The decision:** `f"rpt-{report_type}-{generated_at:%Y%m%d%H%M%S}"`.

**Why this over the alternative:** `REPORT_MANIFEST_FIXTURES`'s hand-authored fixture
IDs end in `-001`, which looks like a sequential counter, but Phase 6 has no database
or persistent report registry to count against — inventing one would mean adding
hidden global state (`code-standards.md`'s explicit prohibition) just to produce a
cosmetic suffix. A timestamp is unique per real call, and — because `generated_at` is
itself an injectable parameter (decision 8) — fully deterministic in tests without
needing to mock a counter or a clock.

**What the alternative would have cost:** Either genuinely hidden module-level state
(a counter surviving between calls, breaking "no hidden global state" and creating
test-order-dependence), or a fake-looking always-`-001` suffix that misleads a reader
into thinking report generation is tracked somewhere it isn't.

## 8. `generated_at` is an injectable optional parameter, formatted with `timespec="seconds"`

**The decision:** `generated_at: datetime | None = None` on every export function,
resolved via `effective = generated_at or datetime.now()` inside the function body,
and stamped into the manifest via `effective.isoformat(timespec="seconds")`.

**Why this over the alternative:** This directly mirrors Phase 5's `as_of_date`
decision — resolve "now" at call time, never as a literal default-argument value (the
classic eager-default-evaluation trap). The `timespec="seconds"` addition came from the
user's correction: without it, `isoformat()` includes microseconds, and a test that
freezes `generated_at` to a specific `datetime` but compares against a manifest built a
few microseconds later would flake for no reason connected to the actual behavior
being tested.

**What the alternative would have cost:** Without injectability, every
workbook-structure test involving `report_id` or `generated_at` would need a
time-mocking library just to get a stable value to assert against. Without
`timespec="seconds"`, tests would need fuzzy/tolerant timestamp comparisons instead of
exact-match assertions.

## 9. Header fill color is one named constant, documented as Excel styling — not a UI-token exemption

**The decision:** A single `HEADER_FILL_COLOR = "D9E1F2"`-style constant in
`report_export.py`, with a comment noting it's workbook formatting distinct from the
Next.js/Tailwind design system — not hex literals scattered inline, and not framed as
"CLAUDE.md's no-hardcoded-hex rule doesn't apply here."

**Why this over the alternative:** The first plan draft asserted the UI-token rule
"doesn't apply" to backend Excel generation and left it at that — technically true
(the rule governs `ui-tokens.md`'s semantic Tailwind classes, which don't exist in a
Python/openpyxl context), but the user's correction flagged it as *overclaiming*: a
blanket "this rule doesn't apply" is exactly the kind of reasoning that, read months
later out of context, looks like an excuse rather than a boundary. Naming the constant
and commenting *why* it's a different category of thing makes the distinction
self-evident in the code itself, not just in this document.

**What the alternative would have cost:** A future reader (or reviewer) skimming
`report_export.py`, seeing a raw hex string, and either flagging it as a violation of a
rule that was never meant to cover it, or — worse — copying the "rules don't apply
here" reasoning into a context where it actually would apply.

## 10. `_safe_cell_value` normalizes `None`/`NaN`/`NaT`/`pd.NA` before every cell write

**The decision:** A dedicated helper converts all four "empty" representations to
`""` before writing to any openpyxl cell, used in both the typed detail-sheet writer
(for `NotRequired` contract fields) and the raw-DataFrame writer (for `Original
Orders`).

**Why this over the alternative:** This wasn't in the original plan draft — the user
added it as a correction, specifically because two different sources of "missing"
values needed the same treatment for different reasons. `NotRequired` TypedDict fields
(e.g. `ValidationErrorRow.order_id`) can be Python `None` when a row's dict simply
omits the key, handled today via `row.get(col, "")` — but that only catches *absent*
keys, not a key present with value `None` or `NaN`. `Original Orders`, meanwhile, is
raw pandas data — a blank Excel cell in the uploaded source file becomes `NaN` (or
`NaT` for a blank date column) once loaded via `pd.read_excel`, and openpyxl writing a
raw `float('nan')` into a cell produces a workbook Excel itself may flag as containing
an invalid value, rather than a clean blank cell.

**What the alternative would have cost:** Without the helper, either an
inconsistent-looking report (`None` rendering as the literal string `"None"` in some
paths and a blank in others, depending on which code path wrote the cell), or — worse
for the "professional, interview-ready" Phase 6 goal — a workbook that opens with an
Excel warning about invalid numeric content in the `Original Orders` sheet whenever a
sample source file has any blank cell, which realistically it does.

## 11. Column headers are explicit per-sheet constants, never derived from `dict.keys()`

**The decision:** Every detail sheet's header row comes from a module-level constant
list (e.g. `VALIDATION_ERROR_COLUMNS`), matching each `TypedDict`'s field-declaration
order in `contracts.py` — not from inspecting the keys of whatever rows happen to be
in the list being rendered.

**Why this over the alternative:** Two failure modes rule out dynamic key-derivation.
First, an empty `list[TypedDict]` (a genuinely common case — e.g. a report with zero
validation errors) has no rows to derive keys *from*, so a sheet with zero errors would
either need special-casing or would render with no header at all. Second, `NotRequired`
fields mean two real rows of the same `TypedDict` can have different key sets (e.g. one
`ValidationErrorRow` with a `sku` and one without) — deriving headers from "whichever
row happens to be first" makes the header row's contents depend on data ordering,
which is exactly the kind of instability a report a human reads shouldn't have.

**What the alternative would have cost:** A workbook-structure test suite that has to
special-case the empty-list scenario for every sheet type, plus a live bug risk where
reordering test fixture data (with no logic change at all) changes which columns
appear in a generated report.

## 12. Manual "open it and look" verification requires asking first — not a default step

**The decision:** `openpyxl.load_workbook(BytesIO(...))` structural checks are the
primary and sufficient automated verification. Actually opening a generated `.xlsx` in
Excel or Preview to eyeball formatting is a separate GUI action that needs explicit
approval before happening, not something folded automatically into "the feature is
done."

**Why this over the alternative:** The first plan draft's verification section
described writing a workbook to a temp file "and opening it" as though that were a
normal automated step. The user's correction pointed out this crosses into a real
action with real side effects outside the automated test loop (launching a GUI
application) — the same category of thing the project's broader "check with the user
before hard-to-reverse or externally-visible actions" convention already covers for
git operations, just applied here to a local desktop-app launch instead.

**What the alternative would have cost:** An agent silently opening Excel or Preview
mid-session without the user expecting an application window to pop up — a minor but
real surprise, and a precedent that "verification" can include launching arbitrary
local GUI applications without asking.

## 13. `/session-docs` runs after `ExitPlanMode`, not during Plan Mode

**The decision:** Documenting this architect session was deferred until after the plan
was approved and Plan Mode's file-write restriction lifted, rather than attempted
while still inside Plan Mode.

**Why this over the alternative:** Plan Mode's operating rule for this session
restricted file edits to the single plan file at
`/Users/jessejames/.claude/plans/for-phase-6-excel-spicy-matsumoto.md` — every other
action had to be read-only. `/session-docs` writes three new files under
`docs/architect/`, which is categorically a write action, so it could not run before
`ExitPlanMode` regardless of when it was requested. The plan itself was updated to
explicitly list `/session-docs` as build step 0, so the ordering is now a locked part
of the Phase 6 sequence rather than an ad hoc afterthought.

**What the alternative would have cost:** Either a failed tool call attempting to
write session docs mid-Plan-Mode, or (if it had somehow been permitted) documentation
written before the plan was in its final, corrected form — missing the very
corrections (decisions 5, 6, 8, 9, 10, 12) that came from the user's review of the
draft.
