# Review: Phase 10 Bug-Fix Cycle

## Scope

A three-part cycle run immediately after the Phase 10 (FastAPI Integration) feature was implemented, verified, committed, and pushed as PR #9: an initial `/project-review`, a `/tdd` fix pass addressing every finding, and a follow-up `/project-review` re-verifying the fixes. All three steps used independent review agents that read the actual current code fresh rather than trusting prior claims — including the fix-verification pass, which re-derived everything from source rather than accepting the fixing session's own summary.

## Round 1 — Initial `/project-review`

Dispatched an `Explore` agent with instructions to actively hunt for problems across the plan (`docs/architect/phase-10-fastapi-integration/approved-plan.md`), every `backend/*.py` file, `lib/api-client.ts`, all three live-wired pages, `ReportCard`, `UploadPanel`, `Button`, the backend test suite, and `context/code-standards.md`/`context/architecture.md`.

**What passed:** Plan alignment (all 13 approved-plan decisions verified as landed correctly), sync `def` handlers, consistent `Annotated[..., File()]`/`Form()]` usage, the uniform error contract on every *traced* path, `lib/api-client.ts`'s promise handling, zero hardcoded colors, proper file-input labeling, `ReportCard`'s backward compatibility with `/dashboard`.

**What failed — 1 Critical:**
- `backend/routers/inventory.py`'s `_run_allocation` didn't catch `MissingColumnsError`/`InvalidOrderDataError`/`InvalidInventoryDataError` raised from *inside* `allocate_inventory()` itself (only `read_xlsx_upload`'s load-time errors were caught). Reproduced live: an orders file where every row is invalid → zero valid orders → `pd.DataFrame([])` → `allocate_inventory`'s internal column check raises → uncaught → generic `500` instead of the intended `400`.

**What failed — 4 Important:**
- Primary "Run" and "Download Report" buttons on all 3 workflow pages weren't disabled while `sampleDataLoading` was true, allowing overlapping requests.
- `UploadPanel` never reflected files loaded via "Run sample data" (it only tracked its own native `<input>`'s `onChange`).
- Report-download errors rendered as a bare `<p>` instead of `BusinessErrorMessage`, missing `role="alert"`.
- (A fifth item, the overly broad `except Exception` in `backend/uploads.py`, was flagged Minor rather than Important — no live misfire found, just latent risk.)

**What failed — Minor:** `backend/routers/orders.py`'s duplicated load/validate logic (vs. `inventory.py`'s already-factored `_run_allocation`); missing regression test for the zero-valid-orders path; no default `type="button"` on `Button`.

## Round 2 — `/tdd` fix pass

Followed the vertical-slice TDD discipline for the one item with a real test seam:

1. **RED**: wrote `test_allocate_inventory_zero_valid_orders_returns_400_not_500` and its `/report`-endpoint counterpart in `tests/test_backend_inventory.py`, using a crafted one-row orders file with a blank `customer_name` (guaranteed to fail OV-001, producing zero valid orders). Ran the suite and watched both tests fail with the exact predicted `MissingColumnsError` traceback propagating uncaught.
2. **GREEN**: wrapped `allocate_inventory(valid_orders_df, inventory_df)` in `_run_allocation` with `except (MissingColumnsError, InvalidOrderDataError, InvalidInventoryDataError) as exc: raise HTTPException(400, detail=str(exc))`. Both new tests passed; the fix covers both `/api/inventory/allocate` and `/api/inventory/allocate/report` in one place since they share `_run_allocation`.

Then applied the remaining findings directly (no test seam exists for frontend UI state or component props in this project — no Jest/RTL harness):
- Added `sampleDataLoading` to all 6 button-disable expressions across the 3 pages.
- Added a `selectedFileName?: string | null` prop to `UploadPanel`, wired from every one of the 6 call sites across the 3 pages, so the panel display is driven by the same file state that's actually submitted regardless of whether it arrived via native pick or "Run sample data."
- Replaced all 3 pages' bare `<p>{reportErrorDetail}</p>` with `<BusinessErrorMessage message={reportErrorDetail} />`.
- `Button` now defaults `type="button"`.
- Factored `backend/routers/orders.py`'s duplicated logic into a `_load_and_validate` helper, matching `inventory.py`'s pattern.
- Assessed `backend/uploads.py`'s broad exception catch and left it as-is with an explanatory comment — no clean, version-stable parse-error exception hierarchy exists across pandas/openpyxl to narrow to safely.

Verified: `uv run pytest` (196 passing, up from 194), `npm run typecheck`/`lint`/`build` all clean, and a fresh live-browser Playwright pass specifically targeting the fixed behaviors — including catching and correcting one flaky assertion in the verification script itself (an `innerText()` race against React's commit timing, resolved by waiting for the button to return to its resting label before reading the DOM).

## Round 3 — Re-review `/project-review`

Dispatched a second independent agent with an explicit per-finding checklist (not a free-form re-scan) to verify each of the 6 fixes landed correctly, re-run the full test suite and build pipeline, and check for architecture drift against the approved plan's 13 decisions.

**Result:** all 6 fixes confirmed correctly and completely applied — every button-disable expression, every `UploadPanel` call site, every `BusinessErrorMessage` replacement checked individually by direct file read, not sampling. Full suite 196/196, typecheck/lint/build clean. No architecture-principle violations: `src/` still has zero FastAPI imports, the error contract stays a single string, no state was lifted out of page-local scope.

**Remaining Minor items, deferred (not blocking):**
- `docs/architect/phase-10-fastapi-integration/approved-plan.md`'s Decision 12 literally claims `backend/uploads.py` is "the only place" that catches those three exception types — now inaccurate, since the Critical fix necessarily added a second, different-call-path catch site in `inventory.py`. The plan document itself wasn't updated to reflect this.
- A stray untracked Excel lock file (`sample_data/~$sample_invoices.xlsx`) sitting in the working tree, unrelated to any fix, not yet cleaned up.
- `context/progress-tracker.md` and `docs/plan/phase-10-fastapi-integration/{plan,explanation}.md` weren't updated to reflect this fix round specifically.
