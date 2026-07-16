Use /teach to build Track 3 — Presentation Without Leakage as a companion course to Tutorial 06, not a rewrite of it.

Read first:

- docs/teach/MISSION.md
- docs/teach/ROADMAP.md
- docs/teach/NOTES.md
- docs/teach/RESOURCES.md
- docs/teach/assets/style.css
- docs/teach/assets/quiz.js
- docs/teach/lessons/0008-business-rules-vs-code-rules.html through 0014-track-2-guided-test-trace.html
- docs/teach/reference/\*.html
- docs/tutorials/06-excel-report-export/README.md
- src/report_export.py
- tests/test_report_export.py
- tests/contract_fixtures.py
- src/contracts.py
- docs/plan/phase-6-excel-report-export/{plan.md,explanation.md,ai-discussion-topics.md}

Create Track 3 lessons starting at the next available lesson number after `0014`. Do not overwrite Track 1 or Track 2 lessons.

Goal:
Teach the conceptual bridge from “business modules produce trusted result envelopes” to “presentation modules consume those envelopes without changing their meaning.” The learner should finish Track 3 able to explain why `report_export.py` is forbidden from recalculating, why workbook tests save/reload, and why report metadata should be derived from the real workbook state.

Recommended lesson sequence:

1. `0015-presentation-layer-vs-business-logic.html`
   Teach separation of concerns: business logic decides; presentation formats. Use the concrete failure mode “report recomputes and disagrees with dashboard/module output.”

2. `0016-consuming-contracts-without-changing-them.html`
   Teach the other side of contracts: Phases 3–5 produced envelopes, Phase 6 consumes them. Explain pass-through sheets, precomputed lists, and why `Backorders` uses `result["backorders"]` as-is.

3. `0017-excel-workbooks-sheets-and-manifests.html`
   Teach the Excel mental model: workbook, sheet, row, cell, header row, sheet order, manifest. Connect `wb.sheetnames` to “derive metadata from the artifact you actually built.”

4. `0018-serialization-boundaries-and-safe-cell-values.html`
   Teach serialization boundaries: Python values are not Excel values. Cover `None`, `NaN`, `NaT`, `pd.NA`, empty strings, and why tests must save/reload with `openpyxl.load_workbook()`.

5. `0019-explicit-columns-and-empty-reports.html`
   Teach why headers come from constants, not `rows[0].keys()`: empty sheets, `NotRequired` fields, stable column order, and human-facing reports.

6. `0020-allow-lists-hidden-state-and-safe-defaults.html`
   Teach two safety defaults from Tutorial 06: explicit allow-lists for `Follow-up List`, and timestamp-based report IDs instead of counters/global state.

7. `0021-track-3-guided-report-trace.html`
   Capstone rehearsal. Trace one real `PaymentAgingResult` into the exported workbook:
   `aging_rows` → `Follow-up List` filter → workbook sheets → `wb.sheetnames` → manifest → saved/reloaded workbook assertions.

Each lesson must:

- Be a short, self-contained HTML file using `../assets/style.css` and `../assets/quiz.js`.
- Link to Tutorial 06 and the exact source/test files it prepares the learner to read.
- Include 2–3 retrieval checks using the existing quiz component.
- Include one tiny exercise in a real file.
- Use real code snippets from `src/report_export.py` or `tests/test_report_export.py`, but keep the lesson concept-first.
- Avoid re-explaining all of Tutorial 06. The lesson prepares; Tutorial 06 deepens.
- Name failure modes explicitly.
- Add/update reference docs only for concepts that recur later.

Suggested reference docs:

- `docs/teach/reference/presentation-layer-glossary.html`
- `docs/teach/reference/report-export-mental-model.html`
- `docs/teach/reference/serialization-boundary-checklist.html`
- `docs/teach/reference/contract-consumer-pattern.html`

Also update `docs/teach/ROADMAP.md` to mark Track 3 lessons as shipped, matching the Track 1/2 pattern. Update `RESOURCES.md` only after verifying official source URLs live, especially openpyxl and Python `io.BytesIO`.

Do not create learning records unless the learner has actually completed exercises or answered questions.

Additional topics worth covering beyond the current roadmap:
Serialization boundary thinking: every export/API/database layer needs a “what values are legal here?” adapter.
Round-trip testing: test the artifact after save/load, not just the in-memory object.
Single source of truth: derive metadata from built state instead of maintaining parallel lists.
Human-facing stability: empty reports still need headers because humans read structure, not just data rows.
Presentation defense-in-depth: allow-lists can be presentation-safe without becoming business-rule revalidation.
