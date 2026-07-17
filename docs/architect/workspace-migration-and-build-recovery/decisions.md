# Decisions — Workspace Migration and Build Recovery

Architectural and procedural decisions from planning and executing the permanent
separation of the private Career OS workspace from the public repo, and the (still
pending) relocation of the public repo outside iCloud's Desktop-sync scope.

## 1. Two permanent sibling workspaces, never nested or symlinked

**What it is:** `~/Developer/career-os` (private, git-free, forever) and
`~/Developer/sales-ops` (public repo) as siblings under `~/Developer/`, replacing the
prior arrangement where `career_os/` and `Resume/` lived *inside* the public repo,
gitignored.

**Why not a symlink instead of a real move:** A symlink from the public repo back to the
private workspace would keep exactly the coupling this migration exists to remove — a
build-time filesystem walk starting at the public repo's root could still legally follow
the symlink into the private tree. Physical separation, not merely logical/gitignore-level
separation, was the actual goal.

## 2. Atomic same-volume `mv`, not copy-then-delete

**What it is:** Every relocation (`career_os/` → `~/Developer/career-os`, the sibling
`Resume/` directory → `~/Developer/career-os/sources/`) used `mv`, confirmed in advance to
be a same-volume operation (`stat -f "%d %N"` showed identical device IDs for `~/Desktop`,
`~`, and `~/Developer`) and therefore an atomic rename, not a slow byte-copy.

**Why not `ditto`/copy + verify + `rm -rf`:** The original plan draft used exactly that
copy-then-delete pattern (matching the source document's literal wording, "copy... then
verify... then remove"). This was corrected during review: a destructive copy-then-delete
duplicates private data in flight for the entire verification window, for no benefit when
an atomic rename is available, reversible by simply moving the same directory back, and
does not risk a stale duplicate anywhere. The correction also caught that the pattern
needed `rm -rf` as a *separate* step after copying — removing that step entirely is safer
than trying to gate it carefully.

## 3. Every relocation is immediately checksum-verified before anything else touches it

**What it is:** Each `mv` was followed immediately by a full recursive `shasum -a 256`
checksum comparison against a pre-move baseline (captured in Phase A, before any move),
excluding `.DS_Store` (Finder regenerates these differently at the destination — a
mismatch there is not a data-integrity problem, so excluding it from the manifest avoids a
false-alarm block).

**Why immediately, not batched at the end:** A rollback ("move it back") is only cheap and
safe while nothing else has happened yet. Verifying each move before proceeding to the
next step means a failure at step N doesn't require untangling what steps N+1...M might
have already assumed about the moved data.

## 4. Targeted per-PID process checks, never a recursive filesystem-rooted scan

**What it is:** Confirming "no process is using this directory" was done by enumerating
specific process names (`node`, `next`, `tsserver`, `eslint`, editor helpers), then
inspecting each individual PID's cwd/open-handles (`lsof -p <pid>`) — never
`lsof +D <directory>` or a bare recursive `find` over the repo tree.

**Why:** This exact class of operation — a recursive walk over a large directory tree —
was the root cause under active diagnosis in the paired `/recover` session (see
`docs/recover/career-os-icloud-build-hang/`). Using it as a "is anything using this
folder" check would repeat the same expensive pattern the whole migration exists to
eliminate, potentially producing the same kind of slow/hanging diagnostic command this
project had just spent significant effort avoiding.

## 5. Private workspace bootstrap: four explicit files, not one combined note

**What it is:** `~/Developer/career-os` was bootstrapped with four separate files:
`AGENTS.md` (canonical, complete privacy/path/content-safety/`/remember` rules),
`CLAUDE.md` (short pointer: read `AGENTS.md` first, never git-init/deploy, run
`/remember restore` first), `memory.md` (this workspace's own memory, in its own
structure), and `.gitignore` containing a single `*` as defense-in-depth.

**Why a deny-all `.gitignore` in a workspace that's never supposed to be a git repo at
all:** Belt-and-suspenders — if this workspace were ever accidentally `git init`'d (a
mistake, not an intended path), the `.gitignore` would still stop everything from being
staged by default, rather than relying solely on "nobody will ever run `git init` here"
holding true forever.

## 6. `memory.md` excision: verify twice, in a specific order, never trust a single diff

**What it is:** The private section (verified to be exactly lines 559-633 via a
byte-level `diff` against `git show HEAD:memory.md` — not assumed from an approximate line
range) was extracted to a temp file, written into the new private `memory.md` beneath a
fixed `## Migrated Private Memory — Verbatim` heading, then re-extracted from *that* file
and diffed byte-for-byte against the original extraction before the public file was
touched at all. Only after that verbatim round-trip passed was the public `memory.md`
edited to remove the section, and *that* result was diffed against `HEAD` to confirm an
exact match.

**Why the order matters:** Editing the public file first and trusting the private copy
was captured "close enough" would risk silently losing or altering personal data with no
way to detect it after the public file no longer has it. Verifying the private copy's
integrity *before* removing the source is the only way a mistake stays recoverable.

**A real mistake this caught:** The first attempt at the public-file edit introduced a
byte-level difference from `HEAD` — not in the section that was supposed to be removed,
but a single line where straight quotes (`"`) had been swapped for curly quotes (`"…"`)
in the *kept* portion, purely from how the edit's old/new strings were typed. The
byte-for-byte `diff` against `HEAD` caught this immediately; a visual read-through of the
file would very likely not have, since both quote styles render almost identically in most
fonts.

## 7. Public `/remember save` happens *after* private cleanup, not before

**What it is:** The order is: extract and verify the private section → remove it from the
public `memory.md` → confirm the public file matches `HEAD` and contains no personal
facts → *then* run `/remember save`, with an explicit instruction that it must append a
public-safe "Workspace Migration Handoff" section only, never overwrite prior project
memory, and never include personal facts.

**Why this order, not the reverse:** Running `/remember save` before the private section
was removed risks the save operation itself re-summarizing or re-including private content
into what's supposed to become a fully public-safe file. Doing the sanitization first, and
only then adding new content, means there's no window where a memory-save step could
reintroduce what was just removed.

## 8. Session-boundary split: the agent session cannot trigger the public repo's own move

**What it is:** The migration plan is split into what the *agent session* does (private
migration, memory sanitization, pre-move git-state snapshot, then a handoff) versus what
the *user* does outside the agent, in a plain terminal (close the editor workspace, verify
no process still touches the old path, run the single `mv` command) versus what a *fresh*
agent session at the new path does (verify, then continue).

**Why:** The agent session's own working directory is *inside* `~/Desktop/sales-ops` — the
very folder being moved. The instant that `mv` executes, any subsequent command in the
same session referencing the old absolute path fails (the inode moved; the old path no
longer resolves to anything). Rather than assume the harness would gracefully handle a
mid-session cwd invalidation, the move was deliberately handed off to a context that isn't
running from inside the folder being moved.

## 9. Two baselines, not one — captured at different points for different comparisons

**What it is:** "Baseline A" was captured at the very start (before any move), "baseline
B" after the private migration and the public-safe `/remember save` completed. Later, if
the move still hadn't happened by the time of a diagnostic checkpoint, that checkpoint
compared current state against baseline B specifically, not baseline A.

**Why two, not one:** Baseline A predates the intentional `memory.md` edit — comparing
post-migration state against baseline A would show `memory.md` as "changed" in a way that
looks like an anomaly but is actually expected and correct. Baseline B is captured *after*
that intentional edit, so it's the correct "did anything unexpected change" comparison
target for everything that happens afterward.
