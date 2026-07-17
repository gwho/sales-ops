# Discussion — Workspace Migration and Build Recovery

The full reasoning trail behind planning and partially executing the private/public
workspace separation — including three rounds of plan rejection and correction, the
execution itself, and a diagnostic checkpoint that stopped short when it found something
unexplained.

## Where this came from

This migration wasn't planned in isolation — it was the direct, user-authored response to
the two root causes found in the paired `/recover` build-hang session
(`docs/recover/career-os-icloud-build-hang/`): a private, nested Next.js app inside
`career_os/`, and the whole project living inside iCloud's Desktop-sync scope. The user
had already written a runbook document,
`context/workspace-migration-and-build-recovery.md`, laying out locked decisions (new
paths, git-free requirement, sibling-not-nested structure) before asking for it to be
turned into an executable plan — so this was explicitly *not* a case of designing the
approach from scratch; the job was translating already-decided intent into a correct,
safe, concrete sequence, and catching anything the source document got approximately
right but not exactly right.

## Research before planning: verifying claims instead of trusting the source document

Rather than translate the runbook directly into commands, three research passes ran in
parallel first: one auditing the actual git state (HEAD, branch, remotes, exact staged/
unstaged/untracked diffs, `.gitignore` contents), one auditing `career_os/`'s real
structure (directory tree, any hardcoded absolute paths, the actual location of the
"source resume" directory the runbook referenced only vaguely), and one auditing
`memory.md`'s actual line-level structure (exactly where the private section starts and
ends, verified byte-for-byte, not estimated from reading the file once).

This surfaced a real correction to the runbook's own text before a single command was run:
the source-resume directory the runbook called "the existing ignored source-resume
directory" was described in one planning pass as `/Users/jessejames/Desktop/Resume/` — a
sibling of the project on the Desktop. **This was independently verified with `test -d`
and found to be wrong**: no such directory exists there. The real directory is
`/Users/jessejames/Desktop/sales-ops/Resume/` — inside the repo, gitignored via a
repo-root-relative `.gitignore` pattern. This is exactly the kind of claim that "sounds
plausible and matches a prior guess" but turns out false on a two-second direct check —
the lesson generalizes: a path claim from a subagent's writeup is a claim, not a fact,
until confirmed against the live filesystem, especially right before it's used in a batch
of `mv` commands touching private data.

## Round 1 review: the plan mostly aligned, but four things needed fixing

The first draft plan was rejected with four corrections, each catching a different kind of
gap:

1. **The wrong source-resume path** (described above) — propagated through several
   command examples in the first draft; needed fixing everywhere it appeared, not just in
   one summary line.

2. **`/remember save` ordering.** The original draft ran `/remember save` as part of the
   handoff, without being explicit that it must happen strictly *after* private-memory
   cleanup. The correction spelled out the exact sequence: extract → verify privately →
   remove from public file → confirm public file matches `HEAD` → *then* save, with an
   explicit "append, not overwrite" instruction and a list of what the save must and must
   not include. It also corrected what "post-move verification" should expect:
   `memory.md`'s diff should match baseline B (captured *after* the save), not be
   literally empty — a plan that says "confirm memory.md has an empty diff" after a step
   that intentionally adds new content to that same file is internally inconsistent.

3. **Copy-then-delete flagged as unnecessarily destructive**, once same-volume `mv` was
   confirmed available — see Decision 2 in `decisions.md` for the full reasoning. The
   correction also caught a subtlety: the *second* move (the sibling `Resume/` directory
   into a new `sources/` subdirectory) only behaves as a rename, not a merge, if the
   destination doesn't already exist — so an explicit existence check was added before
   that specific `mv`.

4. **Recursive `lsof +D <repo>` flagged as repeating the exact failure mode under
   diagnosis.** This is a genuinely subtle point: a check *for* a problem can itself
   reproduce the problem if it's shaped the same way. The fix generalizes to "verify a
   resource is unused by inspecting the specific things that might be using it, not by
   scanning the resource itself."

## Round 2 review: three more corrections after the plan was revised

1. **Private workspace bootstrap was underspecified** — "add an AGENTS.md/CLAUDE.md-style
   note" isn't the same as four separate files with distinct, specific responsibilities.
   The correction split this into exactly what each file must contain (see Decision 5),
   and added a check that neither the new private workspace nor `~/Developer` itself is
   already inside some unrelated git worktree — a check that's easy to skip because it
   sounds redundant with "this workspace has no `.git`," but actually catches a different
   failure (being *nested inside* someone else's repo, not having its own).

2. **The tracked runbook document itself needed updating *before* handoff**, not just the
   ephemeral plan file. The reasoning: a fresh session at the new path is instructed to
   treat `context/workspace-migration-and-build-recovery.md` as authoritative — if that
   document still describes the old (rejected) copy-then-delete approach, wrong source
   path, and empty-diff expectation, the fresh session inherits exactly the mistakes this
   review round just corrected. This is a case where "the plan is right" and "the durable
   documentation is right" are two different deliverables, and only fixing the former
   would silently reintroduce the latter's errors the next time someone reads the doc.

3. **Process verification needed to check every relevant PID's cwd/handles individually**,
   not filter first by whether a process's command line happened to mention the old path
   by name — because editor language-server helper processes (tsserver, eslint, tailwind
   servers) don't put a workspace path in their command line at all; they're only
   associated with a workspace via a `--clientProcessId` that has to be cross-referenced
   against which editor *window* that ID belongs to. (Concretely, during execution, this
   distinction correctly separated a `job-pilot` editor window's helper processes,
   irrelevant here, from the actual `sales-ops`-tied ones.)

## Round 3 review: two more corrections, both about precision

1. **"No meaningful difference" was too loose a bar for verifying the migrated private
   memory.** The correction demanded an exact mechanism: write the migrated content
   beneath a fixed heading, then extract *only* what's beneath that heading back out and
   diff it byte-for-byte against the original extraction, with an explicit instruction not
   to normalize or rewrite during that specific check. This closes a gap where "looks the
   same" could hide a real difference a human skim wouldn't catch — exactly what happened
   moments later during actual execution (the quote-character mismatch described in
   Decision 6).

2. **Route verification needed the backend running, not just the frontend** — because
   the frontend's dashboard has no local override for its API base URL and defaults to
   `127.0.0.1:8000`; verifying `/dashboard` renders without the FastAPI backend running
   would only prove the page loads, not that it actually works, and would risk mistaking
   API-failure error states for a passing check.

## Execution: the plan held up, with one supporting decision made during the audit

Executing the approved plan produced, in order: the tracked runbook rewritten with every
correction folded in; two `mv` operations, each immediately checksum-verified (exact
match both times); the two absolute-path fixes; a grep-plus-manual-skim pass over prose
docs that found no other broken path references (only coincidental prose mentions of
"sales-ops" as a project name — e.g. a deployed portfolio URL — and generic words like
"folder"/"reporting" that a naive grep flagged but a read-through confirmed were harmless);
the four-file private-workspace bootstrap; the verbatim memory excision (which caught the
quote-character mistake exactly as the tightened verification round anticipated); a full
fresh install-and-verify pass in the relocated private workspace (`npm ci`, typecheck,
lint, 13/13 tests, a fast ~2-second build, and a real PDF-generation run, confirming the
content loader's relative-path design — `path.resolve(process.cwd(), '..', '..', ...)` —
worked correctly at the new location without any code change); and the public-safe
`/remember save`.

One useful confirmation came from the fast, clean build inside the newly-relocated private
workspace: it compiled in under 2 seconds with no stall, which is exactly what a healthy
Next.js build looks like once it isn't fighting either of the two root causes — a small
piece of corroborating evidence for the original diagnosis, even though it wasn't the
public repo's own (larger, more contended) build being tested.

## A bounded diagnostic checkpoint, requested mid-handoff, that stopped short — twice

Before running the public repo's `mv`, the user asked for one more bounded check: confirm
nothing had drifted since the plan's baseline, then verify iCloud activity had actually
quieted down before trusting any build timing, all without touching code or the approved
plan. Two things are worth noting about how this played out:

1. **The first "quiet" reading was based on a single data point**, not the "two
   consecutive checks" the instructions asked for — a mistake in the *implementation* of
   the check, not the plan. Rather than accept a technically-matching-but-weaker signal as
   sufficient, this was flagged honestly and a stricter re-check was run, which then
   correctly failed to reach quiet conditions within its own bounded window — reporting
   "environmentally blocked," not attempting the build anyway. This mirrors the same
   discipline from the `/recover` session: don't let a partial pass substitute for the
   actual, specified condition.

2. **A later, separate checkpoint (requested again after the migration had progressed
   further) found a real, unexplained difference against the recorded baseline** — an
   unrelated documentation file (`sample_excel_data_requirements/01_business_scenario.md`)
   had been modified, and a new file had appeared, neither of which were part of the
   migration work. Per the explicit instruction ("stop if there is an unexplained
   difference"), the correct response was to stop and report it rather than guess whether
   it was safe to proceed past, silently absorb it into the baseline, or revert it
   unilaterally. This is the same principle as never assuming a memory-restore's context
   is complete: surface the gap, let the person decide, don't guess.
