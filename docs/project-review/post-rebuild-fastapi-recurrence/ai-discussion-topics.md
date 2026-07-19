# AI Discussion Topics — Post-Rebuild FastAPI Recurrence Fix

## Group 1 — Silent failure paths

1. `WorkflowResultsRepository.save()` has three failure paths, and only one is silent. Why might a codebase end up with inconsistent logging across near-identical branches of the same function, even when the team clearly cares about logging (two of three branches already call `logger.exception`)?
2. What's the smallest possible change to `save()`'s `if self._pool is None: return False` branch that would make this failure mode discoverable from logs alone, without adding new tooling?
3. "Best-effort, never fails the request" and "silently broken with no way to notice" are both true of the current persistence write path at once. Is that a contradiction, or are they actually compatible design goals? What would make them incompatible?

## Group 2 — Verification honesty

4. This review explicitly separated "checked via curl" from "not checked, no browser tool available" rather than writing one combined "verified" claim. What's the actual risk if those two categories get collapsed into one?
5. Compare this session's pending-browser-verification flag to the Landing Page Evidence feature's identical flag from an earlier session. Is this a coincidence, or does it suggest something about how this project's tooling environment should be described in its own documentation?
6. If a browser-control tool *had* been available, which specific checks from this session's curl-based verification would have become redundant, and which would still have been necessary regardless (i.e., things curl genuinely cannot check)?

## Group 3 — Documentation gaps as root causes

7. The missing README local-dev section is described as "very likely why the symptom occurred in the first place." Is that a fair causal claim, or does it overstate what a README section can actually prevent (a developer/agent could still just... not read it)?
8. Of the three prevention options offered (documentation-only, preflight-only, combined orchestration), documentation-only was chosen. What evidence would justify upgrading to preflight-only later? What evidence would justify combined orchestration?
9. This project has an established two-service local architecture since Phase 10, but the README didn't reflect it until this session. What process (not tooling) would catch this kind of drift between "what the architecture actually requires" and "what's written down for a newcomer" before it causes a real symptom?

## Group 4 — Review scope discipline

10. This `/project-review` reviewed a diagnosis session's adherence to its own note, rather than reviewing new code against a build plan. How does that change what "Layer 2 — System integrity" even means when zero source files changed?
11. The persistence gap (Finding 1) was surfaced but explicitly not fixed in this session. What's the argument that surfacing-without-fixing is itself the correct review outcome here, rather than either fixing it immediately or omitting it from the report entirely?
