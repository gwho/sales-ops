# Findings: Deep Explanation of Each Significant Issue

## 1. The Critical bug: an error contract that only covered half the pipeline

**What the problem was.** `backend/routers/inventory.py`'s `/api/inventory/allocate` endpoint runs two business functions in sequence: `validate_orders()` first, then `allocate_inventory()` on the resulting valid orders. `backend/uploads.py`'s `read_xlsx_upload()` was the designated boundary that converts `src/`'s business exceptions into `HTTPException(400, ...)` — but it only wraps the *loading* step (`load_orders`, `load_product_master`, `load_inventory`), not the *computation* step. `allocate_inventory()` itself can raise `MissingColumnsError` (if its input DataFrame lacks required columns — which happens when `validate_orders()` legitimately produces zero valid orders, since `pd.DataFrame([])` on an empty list has no columns at all) or `InvalidOrderDataError`/`InvalidInventoryDataError` (for malformed row values). None of these were caught anywhere between `allocate_inventory()` and FastAPI's outermost catch-all handler, so they fell through to `backend/errors.py`'s generic `Exception` handler and became a `500` with a message that told the user nothing about what actually went wrong.

**Why this violates the project's standards.** `context/architecture.md` states explicitly: "Convert technical exceptions into business-readable `{"detail": "string"}` responses at the `backend/` boundary." `docs/adr/0006`'s whole design premise is that known business/input failures return `400` with a specific message, and only *genuinely unexpected* failures return the generic `500`. A user uploading an orders file where every row happens to be invalid is not an unexpected failure — it's a completely ordinary, foreseeable input the business logic already has a name for (`MissingColumnsError`, precisely because the codebase anticipated this exact shape of problem for the *loading* step). The bug wasn't "no error handling exists" — it's that error handling existed for one call site and was silently assumed to cover a second, structurally different call site that happens to raise the same exception types.

**What the correct pattern is.** Any code path that can raise one of `src/`'s named business exceptions needs its own catch, scoped to exactly where that path lives — not just at the file-loading boundary, and not by trying to catch everything in one giant `try` around the whole request. The fix wraps only the `allocate_inventory()` call specifically:

```python
try:
    return allocate_inventory(valid_orders_df, inventory_df)
except (MissingColumnsError, InvalidOrderDataError, InvalidInventoryDataError) as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from exc
```

This is deliberately *not* a wider `try` around the whole `_run_allocation` function body, because `validate_orders()` itself never raises these exceptions (it returns error rows in its result envelope instead — a different, already-correct error-reporting mechanism for a different kind of failure). Wrapping too broadly would have masked that distinction.

**How to recognize this class of bug in future code.** Whenever a route handler chains two or more business-module function calls, ask specifically: "does *every* function in this chain have its exceptions caught somewhere, or did I only verify the first one?" The review that caught this did so by literally reproducing the empty-DataFrame case and reading the traceback — not by reasoning about the code abstractly. That's the generalizable lesson: for a multi-step pipeline, test the exception path of *every* step, not just the first one that happens to be visible in the happy-path test.

## 2. The race condition: two independent loading flags that both gate the same action

**What the problem was.** The "Run sample data" feature (added mid-session, after the original plan) introduced a second async operation — `handleRunSampleData` — that fetches files and then calls the exact same `runValidation`/`runAllocation`/`runAging` function the primary "Run" button calls. It has its own `sampleDataLoading` state, separate from `status`. The primary "Run" button's `disabled` expression only checked `status === "submitting"`, which is set *inside* `runValidation` — not during the file-fetching phase that precedes it in `handleRunSampleData`. So there was a real window, however brief, where a user could have "Run sample data" fetching files in the background while the primary "Run" button sat fully clickable.

**Why this matters even though the backend is stateless.** It's tempting to dismiss this as harmless because the backend never retains anything between requests — but the danger isn't server-side corruption, it's client-side confusion. Two concurrent `postJSON` calls against `/api/orders/validate` will both eventually resolve, and whichever resolves *last* wins the final `setCurrentResult`/`setStatus` call — with no guarantee that's the one matching what the UI visually shows as "currently selected." A user could end up looking at Order Validation results computed from sample data while the upload panel actually shows their own manually-picked file, with no error, no warning, nothing to indicate the mismatch.

**What the correct pattern is.** Every button that triggers a request affecting shared page state needs to be disabled by *every* loading flag that could be concurrently mutating that same state — not just its own dedicated flag:

```tsx
<Button onClick={handleRunValidation} disabled={!canSubmit || status === "submitting" || sampleDataLoading}>
```

The general principle: when two different user actions can both write to the same piece of state, treat "is *any* write currently in flight" as one combined gate, not two independent ones each guarding only its own trigger.

**How to recognize this in future code.** Any time a page introduces a second way to trigger an existing async action (a shortcut, a bulk-action, a retry button), check whether the *original* trigger's disabled condition was written before the second one existed. If so, it almost certainly doesn't know about the new flag — this bug pattern is specifically what happens when a feature is added incrementally without revisiting every pre-existing gate that touches the same state.

## 3. UploadPanel's silent display gap: a controlled/uncontrolled mismatch

**What the problem was.** `UploadPanel` displayed its filename from a `useState` set only inside its own `<input type="file">`'s `onChange` handler. "Run sample data" never touches that input — it calls `fetchSampleFile()` and sets the *parent page's* `ordersFile`/`productMasterFile` state directly. The component had no way to know a file had been selected through any path other than its own internal input, so after clicking "Run sample data," the actual results would render correctly (the parent's state was genuinely updated and submitted) while the upload card visually still read "Choose a file…" — a real, confusing disconnect between what happened and what the UI showed happened.

**Why this is a design-system-relevant bug, not just a display quirk.** `context/ui-rules.md` and this project's general UI philosophy treat "the UI must reflect real state, never imply something that isn't true" as load-bearing (see the Business Error rules: "never a raw exception," "always business-readable" — the same spirit of not letting displayed information diverge from reality). A component silently showing stale information after a real state change is the same category of problem as showing a wrong error message, just milder.

**What the correct pattern is.** `UploadPanel` gained a `selectedFileName?: string | null` prop, and the parent page now passes it derived directly from the same state it hands to the backend:

```tsx
<UploadPanel onFileChange={setOrdersFile} selectedFileName={ordersFile?.name ?? null} />
```

```tsx
const displayedFileName = selectedFileName !== undefined ? selectedFileName : fileName;
```

Because `selectedFileName` is always derived from the exact `File` object that will actually be submitted — regardless of whether it arrived via the native picker or `fetchSampleFile()` — the display can never drift from reality again. This is a general fix, not a special case for "Run sample data": any *future* third way of setting the file (a drag-and-drop zone, a paste handler, whatever) would automatically display correctly too, because the fix addresses the actual root cause (component owning its own copy of information the parent already has) rather than patching the specific "Run sample data" code path.

**How to recognize this in future code.** Any component with internal `useState` that mirrors information a parent component also has access to is a latent version of this bug — it works fine as long as there's only one way to change that information, and breaks the moment a second path is added. The tell is a component whose visible state can only change through its own event handlers, in a codebase where the *actual* source of truth (the File object, in this case) lives one level up.

## 4. The accessibility inconsistency: two error states, one accessible and one not

**What the problem was.** `BusinessErrorMessage` (used for the main workflow-run error) has `role="alert"`, so a screen reader announces it the moment it appears. The separate report-download error used a bare `<p className="...text-danger">{reportErrorDetail}</p>` with no such role — visually similar (red text), but functionally invisible to assistive technology unless the user happens to be already focused near it.

**Why this matters beyond a checklist item.** This wasn't "forgot to add an attribute" in isolation — it's that the codebase already had the *correct*, accessible pattern (`BusinessErrorMessage`) sitting right next to the *incorrect* one on the same page, for the same conceptual category of information (a failed request, described in business-readable language). That's a more insidious kind of drift than a wholesale missing feature: a future contributor copying the "nearby" pattern for a third error state has a coin-flip chance of copying the wrong one, because both visually look plausible.

**What the correct pattern is.** Reuse the existing accessible component rather than hand-rolling a visually-similar but functionally-lesser one:

```tsx
{reportStatus === "failed" && reportErrorDetail ? (
  <div className="max-w-xs">
    <BusinessErrorMessage message={reportErrorDetail} />
  </div>
) : null}
```

**How to recognize this in future code.** Whenever a new error/status display is added, actively search the codebase for an existing component serving the same *conceptual* role first — not just for a similar-looking snippet to copy. The giveaway that this happened here: the fix required zero new logic, only swapping which existing component got called. That's usually a sign the original code reinvented something that already existed one file away.

## 5. Process lesson: TDD found the one bug automated tests could catch; the review found the rest

Only the Critical backend bug had a real test seam — `TestClient` posting to a real FastAPI route, asserting a status code and a `detail` string, is exactly the kind of integration-style test this project's `tests/test_backend_*.py` suite already uses. The RED step (writing the test, watching it fail with the exact predicted `MissingColumnsError` traceback) confirmed the diagnosis was correct *before* any fix was written — not just "the fix works" after the fact, but "the bug is exactly what we think it is" before touching production code.

The four Important frontend findings had no equivalent seam — this project has no component-test harness. Applying TDD's discipline there would have meant either building test infrastructure that doesn't exist (out of scope for a bug-fix pass) or writing a shallow test that doesn't actually exercise the real bug (the anti-pattern TDD itself warns against — a test that passes when behavior is fine and passes when behavior breaks is worse than no test). Instead, those fixes were verified the way the rest of this project already verifies frontend behavior: `typecheck`/`lint`/`build`, then a live-browser Playwright pass targeting the specific claimed behavior. This is a real project-specific pattern worth remembering: TDD's rigor applies fully where a seam exists (the Python backend, tested via `TestClient`), and the project falls back to live-browser verification where it doesn't (the React frontend, with no Jest/RTL setup) — neither approach is used where the other would be more correct.

## 6. What the re-review found that the fix pass didn't self-report: stale documentation

The second `/project-review` pass surfaced something the fixing session itself never flagged: the approved plan's Decision 12 says `backend/uploads.py` is "the only place" certain exceptions get caught — a claim that became false the moment the Critical fix added a second catch site in `inventory.py`, for a structurally different reason (a different call path raising the same exception types). This is worth recording as its own lesson: a bug fix that changes an architectural invariant a planning document asserted needs to either update that document or explicitly note the deviation — otherwise the next person who reads the approved plan to understand "how does error handling work here" will believe something that's no longer true. Nobody in the fixing session thought to check whether the fix contradicted a documented claim, because the fixing session was focused on the bug, not on auditing prose. That's exactly the kind of gap a second, differently-scoped pass (re-review focused on drift-from-plan, not on "does the fix work") is positioned to catch that the original fixing work structurally could not have caught on its own.
