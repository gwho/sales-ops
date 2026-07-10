# AI Discussion Topics — Phase 8: Next.js Frontend Foundation (`/architect` session)

## Pausing on missing tooling vs. working around it

1. The session paused entirely rather than proceeding without Figma. What would have changed about the decision if the user's instruction had said "use Figma if convenient" instead of "stop and report the exact MCP error"? Where's the line between an instruction worth pausing for and one worth working around?
2. `claude mcp list` revealed Figma wasn't just unauthenticated but never configured. Why does that distinction matter for what gets communicated back to the user? What would have gone wrong if the report had simply said "Figma needs authorization" without checking which case it actually was?
3. The `claude-plugins-official` marketplace was already configured in this environment (from `posthog@claude-plugins-official`). What does that imply about how this environment was set up, and why did it make the plugin-install path lower-risk than starting from zero?
4. What is the actual difference between Figma's local Dev Mode MCP server and its remote `mcp.figma.com` server, and why might "broadest feature set, including Make resources" (the user's stated reason for choosing remote) be a meaningful distinction for a Figma **Make** prototype specifically, as opposed to a normal Figma design file?

## Treating an `AskUserQuestion` answer as a re-issued instruction

5. The user's answer to a yes/no-shaped question contained a full 10-item instruction block and four real URLs. What signals in that response indicated it should be treated as authoritative rather than just "additional context on top of the original ask"?
6. If the embedded instructions had *contradicted* the original kickoff message instead of just elaborating on it, how should that conflict have been resolved? Is "most recent wins" always correct?
7. What's the risk of over-applying this pattern — i.e., treating every verbose `AskUserQuestion` answer as a full instruction rewrite, even when the user just meant to explain their reasoning for picking an option?

## Gate verification: line-by-line vs. spot-check

8. Why is "8 spec cases, 23 test functions, therefore probably covered" a weaker claim than an explicit scenario → test-function table? What could a spot-check miss that a full mapping wouldn't?
9. The three research agents ran in parallel and independently. What would have been lost — or gained — by running them sequentially in the main conversation instead?
10. The `tail -20` pytest truncation bug produced output that "looked odd" and prompted a re-check. What's a general heuristic for recognizing when a verification command's output is suspiciously incomplete, versus when a short/quiet output is actually the expected success signal?
11. Agent 2 didn't just re-check that Phase 6's report tests passed — it independently re-verified that the `report_id` fixture fix (made earlier in the *same* session, by the same conversation) was numerically correct. Why re-verify your own recent work rather than trusting it because you just did it?

## Reading Figma Make source vs. screenshots

12. `get_design_context`'s tool description has a special-cased rule: for Figma Make URLs, always use `nodeId="0:1"`. Why would a Make prototype not have a normal navigable node tree the way a Figma design file does?
13. The Figma inspection returned full TSX source rather than a screenshot. What specific class of error (the $40,000 vs $50,000 threshold) was only catchable because the actual source — not a rendered image — was available? Would a human designer reviewing a screenshot have caught it?
14. Four independently-generated Figma prototypes agreed with each other on the `Critical | High | Medium | Low` priority vocabulary, even though the real code only has three tiers. Why is inter-prototype agreement not evidence of correctness here? What does it actually tell you about how the prototypes were likely generated?
15. The `SupplierFollowUpRow` case distinguished a derivable field (`shortageQty`, arguably `reorder_point - remaining_qty`) from a non-derivable one (`suggestedReorderQty`, genuinely new business logic). What test would you apply to decide which category a given Figma-invented field falls into?

## Deferring to existing decisions vs. asking

16. The chrome-pattern conflict (sidebar vs. top-nav) wasn't escalated to the user, but it also wasn't treated as mechanically resolved like the priority-vocab or threshold corrections. What made this one qualitatively different?
17. What would have had to be true about the Figma prototypes for the sidebar decision to have been worth reopening as a real question, rather than defaulting to the pre-existing `ui-rules.md` direction?
18. "A pre-existing approved decision beats a newly-inspected reference by default" is a strong default. What's a scenario where that default should be overridden — where new reference material *should* trigger reopening an old decision?

## The shadcn token collision as a mid-plan deviation

19. The token collision wasn't found during planning — it was found while writing the actual `tailwind.config.ts`. What does that suggest about the limits of `/architect`-style upfront planning, and when should new information discovered mid-implementation trigger going back to the user versus just proceeding?
20. Walk through exactly what would have broken if shadcn's default tokens had been added to `tailwind.config.ts` alongside the project's own tokens, given both define `colors.accent`. Would the failure have been immediately visible, or silent and delayed?
21. The `tokens-no-modification.md` skill rule is tagged CRITICAL and names a specific different project's file paths (`packages/playground-ui/...`). Why does a rule written for a different codebase still meaningfully apply here, and what did applying it actually require checking?
22. The main `skills/tailwind/SKILL.md` was read and explicitly set aside as inapplicable (HyperFrames v4 browser-runtime, not this project's v3 setup). What would have gone wrong if its guidance had been followed instead of being recognized as a mismatch?
23. "Choosing the primitives-plus-bridge option would itself count as the explicit approval the CRITICAL rule requires" — is offering that as one of two options in an `AskUserQuestion` a legitimate way to obtain "explicit approval," or does the CRITICAL rule imply a higher bar (e.g., a dedicated design-review step) than a single multiple-choice answer?

## What didn't need re-litigating

24. The scratchpad-then-transplant scaffolding pattern was decided once during plan review and then just executed. What made it possible to trust that decision without re-verifying the *reasoning* each time, while still verifying the *outcome* (`git status` on the three doc files) every time?
25. Reading the installed Next.js docs before writing config code caught the v3-vs-v4 issue before any code was written, avoiding a downgrade-after-the-fact. What's the general principle here about when "read the installed docs first" pays for itself versus when it's unnecessary overhead?
