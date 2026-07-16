Use /teach to build Track 2 — Business Rules & Testing Discipline as a companion course to the already-generated tutorials, not a rewrite of them.

Read first:

- docs/teach/MISSION.md
- docs/teach/ROADMAP.md
- docs/teach/NOTES.md
- docs/teach/RESOURCES.md
- docs/teach/assets/style.css
- docs/teach/assets/quiz.js
- docs/teach/lessons/0000-files-folders-and-the-terminal.html through 0007-track-1-guided-trace.html
- docs/teach/reference/\*.html
- docs/tutorials/03-order-validation-core/README.md
- docs/tutorials/04-inventory-allocation-core/README.md
- docs/tutorials/05-payment-aging-core/README.md
- tests/test_order_validation.py
- tests/test_inventory_allocation.py
- tests/test_payment_aging.py
- src/order_validation.py
- src/inventory_allocation.py
- src/payment_aging.py
- docs/plan/phase-3-order-validation-core/{plan.md,explanation.md,ai-discussion-topics.md}
- docs/plan/phase-4-inventory-allocation-core/{plan.md,explanation.md,ai-discussion-topics.md}
- docs/plan/phase-5-payment-aging-core/{plan.md,explanation.md,ai-discussion-topics.md}

Create Track 2 lessons starting at the next available lesson number after `0007`. Do not overwrite existing Track 1 lessons.

Goal:
Teach the minimum conceptual foundation needed before, during, and after Tutorials 03–05. Each lesson should be short, beautiful, self-contained HTML using the existing shared stylesheet and quiz widget. Each lesson should give one tangible win and then point into the real tutorial or test file where that concept appears.

Recommended lesson sequence:

1. `0008-business-rules-vs-code-rules.html`
   Teach what a business rule is, how it differs from a programming error, and how a test proves a rule on a known example. Use `tests/test_order_validation.py` as the destination, but keep the lesson concept-first.

2. `0009-structured-errors-and-result-envelopes.html`
   Teach why business logic returns structured dict/list outputs instead of printing, crashing, or returning loose tuples. Connect to `OrderValidationResult`, `InventoryAllocationResult`, and `PaymentAgingResult`.

3. `0010-reading-tests-as-specifications.html`
   Teach how to read test names, arrange/act/assert shape, helper fixtures, `pytest.raises`, and exact assertions. Use examples from all three Track 2 test files. This should be the practical “how to read the proof” lesson before Tutorial 03.

4. `0011-independent-rule-evaluation-and-data-issues.html`
   Teach the difference between collecting every issue on one row vs first-match-wins classification. Use Phase 3 multiple validation errors and Phase 5 PA-006/PA-007 data issues as contrast.

5. `0012-priority-ordered-processing-and-mutable-state.html`
   Teach the plain-language greedy/priority allocation idea before Tutorial 04: sort first, allocate one line, mutate remaining stock, never recompute the past.

6. `0013-date-arithmetic-boundaries-and-signed-values.html`
   Teach date subtraction, boundary cases, negative `days_overdue`, Watch windows, and why boundary tests exist. Prepare directly for Tutorial 05.

7. `0014-track-2-guided-test-trace.html`
   Capstone rehearsal lesson. Pick one real test from each module:
   - one validation test from Phase 3
   - one allocation depletion/sort test from Phase 4
   - one payment aging boundary test from Phase 5

   For each, make the learner predict:
   - what input row(s) are being constructed
   - what business rule is under test
   - what output contract should change
   - what assertion proves the behavior

Each lesson must:

- Link to the relevant generated tutorial README.
- Link to the real source/test file.
- Include 2–3 retrieval checks using the existing `quiz.js` format.
- Include one tiny exercise that sends the learner into a real file.
- Include a reminder to ask the agent if the reasoning step felt like guessing.
- Avoid duplicating the full tutorial explanations. The lesson prepares; the tutorial deepens.
- Add or update reference docs only when the idea will recur across later tracks.

Suggested new reference docs:

- `docs/teach/reference/business-rule-testing-glossary.html`
- `docs/teach/reference/test-reading-patterns.html`
- `docs/teach/reference/boundary-case-checklist.html`
- `docs/teach/reference/result-envelope-pattern.html`

Do not create learning records unless the learner has actually completed exercises or answered questions. Lesson authorship alone is not evidence of learning.
