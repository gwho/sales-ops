# AI Discussion Topics — Workspace Migration and Build Recovery

## Trusting claims versus verifying them

1. A research pass claimed a specific directory path existed and was the "source resume
   directory." It was wrong. What's a general rule for deciding which claims in a
   plan-supporting research document need independent verification before being used in
   destructive/irreversible commands, versus which can be trusted as reported?
2. Why does verifying a private `memory.md` migration byte-for-byte (not just "looks
   right on read-through") matter specifically for personal/private data, more than it
   might for, say, a public code comment?

## Reversibility and blast radius

3. Why is a same-volume `mv` meaningfully safer than a copy-then-delete, given that both
   are intended to end with the data in the same final place? What specifically can go
   wrong with copy-then-delete that can't happen with an atomic rename?
4. What made the second `mv` (the sibling `Resume/` directory into a new `sources/`
   folder) require an extra precondition check that the first `mv` didn't need in the same
   way?
5. Why does "verify each move immediately, before the next step" reduce risk compared to
   "do all the moves, then verify everything at the end"?

## Self-referential diagnostics

6. Why would using a recursive `lsof +D <directory>` scan to check "is this directory in
   use" be a bad idky specifically in *this* project's context, even though it's a
   completely normal, safe command in general? What made it special here?
7. What's the general principle for recognizing when a verification step might reproduce
   the exact problem it's trying to verify the absence of?

## Session boundaries and process isolation

8. Why can't an agent session safely execute a command that moves the very directory it's
   currently running from? What specifically breaks, mechanically?
9. What would you expect to happen, concretely, to a running shell session's subsequent
   commands if its working directory's underlying folder were renamed out from under it
   mid-session?
10. Why does handing off the actual move to a fresh, uninvolved context (a plain terminal,
    then a brand-new session at the new path) resolve this more safely than trying to
    detect and recover from the cwd invalidation within the same session?

## Baselines and comparison targets

11. Why are two baselines ("A" and "B") needed here instead of one? What specifically
    would go wrong if only baseline A (captured before any work started) were used to
    verify state after the private-memory cleanup and `/remember save` had both run?
12. If you were designing a similar migration, how would you decide how many baseline
    snapshots you need, and at which points in the process to take them?

## Handling ambiguity and unexpected findings honestly

13. During a bounded "iCloud quiet check," an early implementation accepted a single
    passing reading instead of the two-consecutive-readings the instructions specified.
    Why was it correct to flag this as a shortfall in the *check's own implementation*
    rather than silently treating the result as good enough?
14. A later checkpoint found an unrelated file modified since the last baseline. What are
    the possible explanations for a change like that appearing mid-session, and why is
    "stop and ask" the right response instead of either reverting it or assuming it's fine
    and continuing?
15. What's the risk of a migration or long-running process "helpfully" absorbing
    unexplained changes into its own baseline as it goes, rather than treating each
    comparison point as a hard checkpoint?

## Ordering private-data operations correctly

16. Why does removing private content from a public file need to happen, and be verified,
    *before* running a save/memory operation that touches that same file — rather than
    after, or concurrently?
17. What's the risk of writing a "public-safe" summary of a session's private-data work
    (like a migration handoff note) if that summary is generated before the private
    content has actually been confirmed removed from the file it's being appended to?

## Documentation as a durable artifact, separate from the immediate plan

18. Why did the tracked runbook document (`context/workspace-migration-and-build-
    recovery.md`) need its own explicit update step, separate from just having the
    in-session plan be correct? What's the risk of only fixing the plan and not the
    document a future session will read?
19. In general, when a plan is corrected through review, what's a good rule for deciding
    which other artifacts (docs, comments, runbooks) need the same correction propagated
    into them?
