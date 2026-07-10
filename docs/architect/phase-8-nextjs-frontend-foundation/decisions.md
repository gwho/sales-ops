# Decisions — Phase 8: Next.js Frontend Foundation (`/architect` session)

One section per architectural decision made in this session's `/architect` planning (run twice — once paused on a missing Figma MCP connection, once completed after it was connected). Each covers what was decided, how it works, why this over the alternative, and what the alternative would have cost.

## 1. Hard-stop on Figma inspection rather than silently falling back

**Decision:** When the user's first Phase 8 kickoff instructed "use Figma MCP... if MCP cannot inspect them, stop and report the exact MCP error, do not silently fall back to screenshots," and no Figma MCP server was configured at all (confirmed via `claude mcp list` — only Gmail/Calendar/Drive/Zapier/PostHog listed, no `.mcp.json` in the repo), the session paused the entire `/architect` planning process rather than proceeding with a documentation-only Figma placeholder.

**How it works:** `claude mcp list` was run first to get the exact state (not "no Figma" but "Figma isn't even a configured server"), then WebSearch confirmed the two legitimate setup paths (`claude plugin install figma@claude-plugins-official`, the recommended one — already had its marketplace configured in this environment — or manual `claude mcp add --transport http figma https://mcp.figma.com/mcp`). The session reported the exact diagnosis and the exact remediation, then literally stopped and waited rather than continuing to plan Phase 8 without Figma input.

**Why this over an alternative:** The instruction was explicit and specific ("do not silently fall back"), which is a strong signal the user wanted this checked, not rationalized around. The cheaper alternative — proceed with the plan, note "Figma unavailable" as an assumption, let the user object at `ExitPlanMode` — would have produced a plan the user had already told me not to produce. Stopping cost one extra round trip; silently working around it would have cost a rejected plan and a re-explanation of the same instruction.

**Cost of the alternative:** A `/architect` blueprint delivered without Figma input, when the user had explicitly required it, forces either an awkward mid-review correction or a second full planning pass — strictly worse than pausing up front.

## 2. Treat an embedded `AskUserQuestion` answer as the authoritative revised instruction set

**Decision:** The user's answer to "how do you want to handle the missing Figma link" wasn't a simple option pick — it contained a full re-issued 10-item instruction block plus four real Figma URLs, submitted as free-text inside the question response. This was treated as superseding the original kickoff message, not as a clarification layered on top of it.

**How it works:** The revised instructions were more specific than the original (e.g., explicit V1/V1.5/V2/out-of-scope classification requirement, an explicit fallback for MCP failure, explicit reports-lifecycle client-state model) and included real URLs where the original had `<paste link>`. Rather than trying to reconcile two instruction sets, the second `/architect` invocation used the embedded text as the complete brief.

**Why this over an alternative:** Users sometimes paste a fuller version of what they meant to say the first time, especially after being asked a clarifying question — the `AskUserQuestion` free-text field became the practical channel for "let me actually finish typing what I meant." Treating it as authoritative avoided asking the user to re-paste the same information a third time.

**Cost of the alternative:** Ignoring the embedded detail and only acting on the literal option selected ("no link, proceed without Figma") would have discarded real URLs and a materially more detailed spec the user had already typed once.

## 3. Line-by-line gate re-verification, not a re-assertion of the prior spot-check

**Decision:** Phase 7's memory/progress-tracker had explicitly flagged the Phase 8 gate check as "a spot check... not a literal line-by-line traceability audit." This session re-did it properly: three parallel background research agents independently mapped every row of the three specs' §11/§12 test-case tables to a named test function, confirmed zero gaps (26/26), and separately confirmed Phase 6's report-structure tests (24/24) and the fixture correctness.

**How it works:** Agent 1 read all three spec test-case tables in full and all three test files in full, producing an explicit scenario → test-function mapping (not just a count comparison). Agent 2 independently verified Phase 6 report-structure coverage against the specs and confirmed the fixture format fix was real and correct. Agent 3 surveyed the Phase 8 planning docs. A fourth check — `uv run pytest` run directly, not just trusted from agent output — confirmed 152 passed with an explicit summary line, after an initial `tail`-truncated run misleadingly showed no summary at all (caught and re-run properly).

**Why this over an alternative:** The gate is documented in `CLAUDE.md` as a hard implementation gate for Phase 8 — "cannot start until every test case... passes." A hard gate deserves the audit method its own documentation asks for, not the cheaper method that was already flagged as insufficient in the prior session's memory. Re-doing it properly also meant the gate confirmation in this PR is a genuine claim, not a repeated caveat.

**Cost of the alternative:** Continuing to spot-check and re-assert "probably fine" across multiple phases erodes the gate's meaning — eventually a real gap would go unnoticed because "spot-checked, not audited" had become the accepted status quo.

## 4. Figma inspected as reference input, corrections resolved unilaterally in favor of contracts

**Decision:** Once Figma MCP was connected and all four Make prototypes were inspected via `get_design_context`, every contradiction found between the prototypes and the real Python contracts was resolved in favor of the contracts, documented as a correction, and **not** raised as a question to the user — because the user's own instructions already established the resolution rule ("Figma is visual reference only... source of truth remains the contracts").

**How it works:** Each prototype's full React/TSX source was read (not just a screenshot), extracting literal field names, enum values, and hardcoded numbers, then diffed against `src/contracts.py`, `inventory_allocation.py`, `payment_aging.py`, and `context/ui-contract-plan.md`. Seven distinct corrections were found and written into a new "Figma Reference Reconciliation" section: an invented 4-tier priority vocab where only 3 tiers are real; two invented allocation-status values; three invented `SupplierFollowUpRow` fields; a wrong dollar threshold ($40k vs the real $50k); client-side email templating that duplicates a server-generated field; and an 8-item mega-nav where only 5 routes are real.

**Why this over an alternative:** Asking the user to adjudicate each of these would have been asking them to re-derive a rule they had already given ("Figma never wins over contracts"). The mechanical application of an already-stated rule is not a judgment call requiring a question — it's exactly the kind of "ask only what matters" discipline `/architect` is supposed to apply.

**Cost of the alternative:** Turning seven mechanical corrections into seven questions would have been noise — the answer to all of them was already determined by the instruction the user gave before Figma was even inspected.

## 5. One real judgment call surfaced: the chrome-pattern conflict, resolved by precedence, not by asking

**Decision:** Of the four Figma prototypes, only the Dashboard used the sidebar-nav chrome that `context/ui-rules.md`/`CLAUDE.md` already mandate; the two Inventory Allocation prototypes used a horizontal top-nav+stepper, and the Payment Aging prototype used a bare top bar. This was the one finding with real design weight — but it was still resolved without a blocking question, because a pre-existing, already-approved decision (sidebar nav, documented before any Figma reference existed) directly covers it.

**How it works:** The reconciliation section states plainly: the sidebar decision wins uniformly across all five routes; the non-sidebar prototypes remain useful reference for their *content* (stepper, filter bar, upload panel) but not their *chrome*. This is presented as a resolved decision in the written plan, available for the user to push back on at `ExitPlanMode`, rather than as an open question blocking the plan.

**Why this over an alternative:** A documented, already-approved design direction takes precedence over a newly-inspected AI-generated prototype by default — the burden is on new information to justify overriding an existing decision, not on the existing decision to re-justify itself every time new reference material shows up. Since three of four Figma screens didn't even agree with each other on chrome, there was no coherent "Figma consensus" to weigh against the existing rule anyway.

**Cost of the alternative:** Blocking the plan on "which chrome pattern do you want" would have re-opened a decision that was never actually put in question by anything in this session — the Figma prototypes disagreeing with each other and with the existing rule is not new evidence that the existing rule is wrong.

## 6. Phase 8 scope kept narrow: scaffold only, Figma reconciliation as documentation-only output

**Decision:** Despite the extensive Figma inspection and reconciliation work, none of it changed any Phase 8 code. Phase 8's actual deliverable stayed exactly what `build-plan.md` defines: Next.js scaffold, config, routing, mock data — no real components, no page content wired to data. The Figma findings were written into `context/ui-contract-plan.md` purely as a Phase 9 input.

**How it works:** The blueprint's "How to build it" section never references Figma-derived visual details in any of its 13 build steps — it references only the contracts, `ui-tokens.md`, and `ui-contract-plan.md`. The reconciliation section is explicitly framed in the plan as "documentation-only this phase."

**Why this over an alternative:** Doing real Figma-informed component work in Phase 8 would have quietly expanded Phase 8's scope into Phase 9's territory, undermining the entire phase-boundary discipline this project has followed since Phase 1 (`build-plan.md`'s explicit phase gates, the Scope Gate for spec versioning, etc.). The user's own instructions for this session repeated "scaffold only" and "no real components" multiple times across both kickoff messages — extending scope here would have contradicted a directly stated constraint, not just a stylistic preference.

**Cost of the alternative:** Blurring the Phase 8/9 boundary here would set a precedent that "gather now, build a little now too" is acceptable, eroding the phase-gate discipline that has made this project's build sequence auditable phase-by-phase.

## 7. shadcn primitives deferred to Phase 9 — discovered mid-build, not in the original blueprint

**Decision:** This decision wasn't in the original `/architect` blueprint (which still listed "shadcn init + add button/card/table/badge/input/select primitives" as a Phase 8 step) — it was forced during implementation when `context/ui-tokens.md`'s literal token names were read against shadcn's known defaults, and a direct collision was found on `--accent` (brand blue here, gray hover in shadcn). The project's own `skills/tailwind-best-practices/references/rules/tokens-no-modification.md` (tagged CRITICAL) forbids modifying design tokens without explicit approval, which reframed "should we add shadcn primitives" from an execution detail into a real architectural fork.

**How it works:** Raised via `AskUserQuestion` mid-implementation (not silently resolved, since it deviated from the already-approved plan) with two real options: plumbing-only (defer primitives, no token risk) versus primitives-now-plus-a-token-bridge (which would itself count as the "explicit approval" the CRITICAL rule requires). The user chose plumbing-only. `components.json`, `lib/utils.ts` (`cn()`), and the four runtime deps (`clsx`, `tailwind-merge`, `class-variance-authority`, `lucide-react`) were installed; no primitive component files were created.

**Why this over an alternative:** Since Phase 8 renders zero real components anyway, deferring primitives cost nothing this phase and avoided baking in a token-collision resolution before any component existed to justify the trade-off. It also correctly separated a token-system decision (which needs explicit, deliberate approval per the project's own rules) from routine scaffolding (which doesn't).

**Cost of the alternative:** Adding shadcn's token set now, even as a "bridge," would have been the exact unauthorized token modification the CRITICAL rule warns about, and would have forced a reconciliation decision (how to rename shadcn's `--accent` to avoid the collision, whether to prefix shadcn tokens, etc.) speculatively, before any real usage pattern existed to inform it.

## 8. Standing infrastructure decisions carried into Phase 8 without re-litigation

Several decisions from the plan review (before implementation began) were locked in and then just executed, not re-discussed: scratchpad-then-transplant scaffolding (to avoid `create-next-app` clobbering `AGENTS.md`/`CLAUDE.md`/`README.md`), the Tailwind v3 setup path (`--no-tailwind` at scaffold time, manual v3 install, per the installed Next docs' explicit v3 guide) instead of accepting v4 and downgrading, mock JSON generated by a build-time-only script from `tests/contract_fixtures.py` rather than hand-transcribed (specifically to avoid repeating the exact `report_id` staleness bug fixed earlier in the same session), and the `docs/plan/` feature-docs folder as a required Phase 8 deliverable. None of these required a design decision during implementation — they were architectural decisions made once, during plan review, and then followed mechanically.
