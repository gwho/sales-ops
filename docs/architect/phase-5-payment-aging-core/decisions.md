# Phase 5: Payment Aging Core — Architect Session Decisions

Eight decisions were resolved via two rounds of `AskUserQuestion` before any code was
written, followed by a third round of corrections after the first plan draft was
rejected and rewritten in place. Each section below is one decision: what it is, why
it mattered, what the alternative would have cost, and — where relevant — what it
looked like once implemented.

## 1. Single envelope function, not the spec's three-function split

**The decision:** `calculate_payment_aging(invoices_df, as_of_date=None) -> PaymentAgingResult`
does everything in one call — aging, data issues, and draft messages together — instead
of the spec's suggested `calculate_payment_aging() -> tuple[df, df]` plus a separate
`create_follow_up_messages(aging_df)`.

**Why this over the alternative:** The spec's section 11 signatures are implementation
*suggestions*, not a contract — nothing in `03_demo_payment_aging.md` requires callers
to invoke two functions in sequence. Phase 3 and Phase 4 both already settled this
question for the codebase: `validate_orders()` and `allocate_inventory()` are each a
single function returning a single dict envelope. Splitting Phase 5 into three
functions would mean the module has no single object that *is* "the payment aging
result" — a future FastAPI route would need to know the call order and manually merge
three separate return values, which is exactly the kind of orchestration logic
`context/code-standards.md`'s Python Module Boundaries table reserves for route
handlers, not business modules.

**What the alternative would have cost:** A caller-side merge step duplicated at every
call site (tests, future API routes, future report export), and a second place where
"is this the current payment aging result" could drift out of sync — e.g., a message
generated from a stale `aging_df` after a caller re-ran `calculate_payment_aging` but
forgot to re-run `create_follow_up_messages`.

## 2. Paid invoices stay in the aging table

**The decision:** An invoice with `outstanding_amount <= 0` still gets a full
`PaymentAgingRow` — with `follow_up_priority="None"` and
`suggested_action="No action required"` — rather than being dropped from the output
entirely.

**Why this over the alternative:** PA-002's text is narrow: "exclude it from *overdue
follow-up*." Three independent signals in the spec point the same direction: the
downloadable sheet is literally named "All Invoices with Aging" (section 6), section
7's suggested-actions table has a dedicated `Paid → "No action required"` row (which
needs a row to attach to), and the "Aging output columns" table (which becomes
`PaymentAgingRow`) has no carve-out excluding Paid rows. Reading "excluded from overdue
follow-up" as "never gets a High/Medium/Low/Watch priority or a draft reminder" — not
"never appears in the table" — satisfies all three signals at once.

**What the alternative would have cost:** A report that silently loses paid invoices
from view. For a sales-ops tool whose whole purpose is giving someone a full picture
of receivables, an "All Invoices" sheet that quietly isn't all invoices is a
correctness bug users would only discover by noticing a missing row, not by an error.

## 3. `total_invoices` counts every row; the other summary fields don't

**The decision:** `PaymentAgingSummary.total_invoices` counts every row loaded from the
file, including PA-006/PA-007 data-issue rows. `aging_bucket_counts`,
`total_outstanding_amount`, `overdue_amount`, and `high_priority_count` are computed
only from `aging_rows` — the valid subset.

**Why this over the alternative:** This mirrors a precedent already set in Phase 3:
`ValidationSummary.total_orders` counts every loaded order row, valid or not, while
`invalid_orders`/`duplicate_orders`/etc. are sub-counts of that total. Keeping
"total_X" fields meaning "everything in the file" consistent across modules means a
developer who already understands one module's summary semantics doesn't have to
re-learn the convention for the next one.

**What the alternative would have cost:** If `total_invoices` only counted
aging-eligible rows, the KPI card labeled "total invoices" on the eventual UI would
under-report the actual file size whenever any row has a data issue — a subtle
mismatch between "how many rows did I upload" and "how many invoices does this say I
have," discoverable only by manually counting rows in the source Excel file.

## 4. `as_of_date: date | None = None`, resolved inside the function body

**The decision:** The "today" reference date is optional, named `as_of_date` (not
`reference_date`), and resolves via `effective_date = as_of_date or date.today()`
inside `calculate_payment_aging()` — never as a literal default argument value.

**Why this over the alternative:** Two constraints pulled in different directions.
The spec's section 9 UI description calls it `as_of_date` (a date-selector control),
so keeping that name preserves wire-compatibility with whatever future
API/UI layer calls into this function. But `sample_data.py`'s existing
`reference_date: date | None = None` parameter — already used for
`generate_invoices()` — establishes the codebase's actual convention for "resolve at
call time, not at function-definition time." A literal default like
`as_of_date: date = date.today()` would bake in the date Python evaluated the module
at import time, silently going stale for every subsequent call in a long-running
process (a classic Python mutable/eager-default-argument trap, here applied to dates
instead of lists/dicts). The chosen shape keeps the spec's naming and the codebase's
resolution-timing convention simultaneously.

**What the alternative would have cost:** Either a naming mismatch with the future
UI/API layer (if `reference_date` had been kept), or a genuinely stale "today" in any
long-running process — e.g., a FastAPI server that imports `payment_aging.py` once at
startup and serves requests for days, every one of them silently using the server's
boot-time date instead of the actual current date.

## 5. `days_overdue` keeps its sign — never floored at 0

**The decision:** `days_overdue` is the raw `effective_date - due_date` day count:
positive when overdue, `0` when due today, **negative** when due in the future.

**Why this over the alternative:** PA-005's Watch rule — "not overdue but due within 7
days" — needs a way to express "how close is this invoice to its due date" for
invoices that haven't hit their due date yet. A floored value (every non-overdue row
reporting `0`) destroys that information: "due in 2 days" and "due in 200 days" would
be indistinguishable, forcing a second, un-contracted internal calculation just to
answer a question the field name already promises to answer. Keeping the sign lets
Watch be one condition — `-7 <= days_overdue <= 0` — using the same field every other
branch already computed.

**What the alternative would have cost:** Either Watch becomes unimplementable without
a hidden second calculation that never appears in the output contract, or the contract
itself would need a new field (`days_until_due`) that section 6 of the spec never
defines — a Field Scope Boundary violation to work around a self-inflicted flooring
decision.

## 6. Draft reminders only for rows that are actually, currently overdue

**The decision:** A `DraftMessageRow` is generated only when
`outstanding_amount > 0 and days_overdue > 0 and follow_up_priority in {"High", "Medium", "Low"}`.
Watch, Current, Paid, and data-issue rows never get a message.

**Why this over the alternative:** Section 8's text is specific: "a simple draft
message for each *overdue* customer." A Watch-priority invoice, by definition, hasn't
missed its due date yet — sending it a message worded around "which is currently N
days overdue" (the spec's own template text) would be factually wrong for a negative
`days_overdue`. This decision also had to be reconciled against Decision 5's
consequence that a not-yet-due invoice can still carry `follow_up_priority = "High"`
(see the aging-bucket-vs-priority-override discussion in `discussion.md`) — the
`days_overdue > 0` guard is what stops that combination from producing a
factually-wrong "70 days overdue" message on an invoice that's actually due in the
future.

**What the alternative would have cost:** Sending a demo/sample reminder message to a
"customer" whose invoice isn't overdue, worded as though it were — undermining the
whole point of the feature as a portfolio-quality demonstration of correct business
logic.

## 7. Invalid `paid_amount` degrades silently; invalid `invoice_amount` doesn't

**The decision:** Blank, non-numeric, or negative `paid_amount` all fall back to
`0.0` with no `PaymentDataIssueRow` raised. Only `invoice_amount` failing the same
checks produces a PA-007 data issue and excludes the row from `aging_rows`.

**Why this over the alternative:** PA-007's text names one field: "If invoice amount
is missing or less than 0, flag as error." PA-001 documents exactly one failure mode
for `paid_amount` — "If paid_amount is missing, treat it as 0" — with no equivalent
"and if invalid, flag as error" clause. Extending PA-007's error path to `paid_amount`
by analogy would be inventing a rule the spec doesn't state, which the Scope Gate
explicitly rules out even when the change "looks trivial." Since `paid_amount` is
already treated as optional (blank → 0), and nothing distinguishes "blank" from "any
other unusable value" for an optional field, non-numeric and negative values got the
same fallback as blank.

**What the alternative would have cost:** A data issue thrown for a plausible, minor
data-entry mistake (e.g. a stray space or currency symbol accidentally typed into a
paid-amount cell) that PA-007 never asked to be flagged — expanding what counts as an
"error" row beyond what the spec defines, and quietly narrowing which invoices make it
into the aging table for a field the spec itself calls optional.

## 8. Draft message amounts are currency-aware, not hardcoded to `$`

**The decision:** `_format_amount()` renders `f"{currency} {amount:,.2f}"` when the
invoice's own `currency` column is present (e.g. `"HKD 58,000.00"`), or a bare
`f"{amount:,.2f}"` when it's blank — not a fixed `$` symbol.

**Why this over the alternative:** The user rejected both options offered in the
original question — "always `$`" and "no symbol at all" — and proposed a third: use
the source invoice's own `currency` field when present. This was the correct call
because the pre-existing `DRAFT_MESSAGE_ROW_FIXTURE` (authored in Phase 2, before this
module existed) hardcoded `$58,000.00` for an invoice that `sample_data.py` generates
with `currency: "HKD"` — a literal factual error in a fixture nobody had caught yet,
because nothing had implemented the logic that would render it. `currency` isn't part
of any output contract field (`DraftMessageRow` has no `currency` key — adding one
would violate the Field Scope Boundary, since section 8 never defines a structured
currency output), but `message_text` is free-form prose, so nothing stops the *source*
`currency` value from being interpolated into that text without touching the contract
shape at all.

**What the alternative would have cost:** Continuing to render `$` on every message
would have meant every sample HKD/SGD/TWD invoice's draft reminder was quietly wrong —
a portfolio artifact that looks polished but is factually incorrect the moment anyone
who knows the sample data reads one of the generated messages.

## 9. `row_number` never leaves the function — added during the correction round

**The decision:** No `row_number` field was added to `PaymentDataIssueRow`, and no
`contracts.py` change was made. Any per-row loop position stays purely internal.

**Why this was added:** This wasn't one of the original eight questions — it surfaced
when the user reviewed the first plan draft and flagged that the draft's phrasing
("used to build a business-readable error_message... 'Row 5: due date is missing.'")
implied embedding a row number into output text, without the plan explicitly deciding
whether that also meant adding a `row_number` field to the contract. The correction
made explicit what had been implicit: the existing `PaymentDataIssueRow` contract
(`invoice_id`, `customer_name`, `error_code`, `error_message`, `severity`) doesn't
carry a row number, `contracts.py` wasn't going to be touched this phase, and the
implementation should match the shape that already exists rather than silently
drifting from it via message-text content.

**What the alternative would have cost:** A `contracts.py` change made incidentally,
inside a phase whose plan never called for touching output contracts — exactly the
kind of scope drift the Field Scope Boundary rule exists to prevent, except triggered
by an implementation detail (how to phrase an error message) rather than a deliberate
design choice.

## 10. `follow_up_priority == "None"` always means `"No action required"`

**The decision:** Both a Paid invoice and a not-paid-but-not-due-soon invoice
(`days_overdue < -7`) share the exact same `suggested_action` text.

**Why this was promoted from an assumption to an explicit decision:** The original
plan draft listed this only as a low-risk assumption, not a question put to the user.
The correction round's note — "the spec only lists Paid for that text, but it is the
cleanest fallback for None" — confirmed the assumption was correct, but also
established it as a locked decision rather than something a future agent might
"discover" needs re-deciding. Section 7's suggested-actions table genuinely has no row
for plain "None" (only for "Paid"), so *something* had to be chosen for the contract's
required `suggested_action: str` field on every row that isn't Paid, High, Medium,
Low, or Watch.

## 11. `paid_amount` is never a loader-required column

**The decision:** `INVOICES_REQUIRED_COLUMNS` contains only the five fields the spec
marks "Required: Yes" (`invoice_id`, `customer_name`, `invoice_date`, `due_date`,
`invoice_amount`). A file missing the `paid_amount` *column* entirely behaves
identically to a file that has the column but leaves individual cells blank — both
default every row's `paid_amount` to `0.0`.

**Why this was added:** Also a correction-round addition, not an original question —
the user wanted this stated explicitly rather than left implicit in the loader's
required-columns list, specifically so a future agent skimming the code wouldn't
"tighten" the loader to require `paid_amount` by analogy with the five genuinely
required fields. Column-level absence and cell-level blankness resolving to the same
`0.0` fallback (rather than the missing-column case raising `MissingColumnsError`)
was locked in as a named test (`test_missing_paid_amount_column_entirely_defaults_to_zero`
in `plan.md`'s verification list) precisely because it's the kind of distinction that
looks like an edge case but has a one-line-diff way to silently break.
