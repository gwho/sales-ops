# Workspace Migration and Build Recovery

Status: approved via `/architect` — see
`docs/architect/workspace-migration-and-build-recovery/` for the session
record once written. This is the authoritative execution runbook.

## Purpose

Permanently separate the public Sales Admin Automation Toolkit repository from
the private Career OS workspace, and move both projects outside the
iCloud-managed Desktop directory.

This addresses two independent build problems:

1. The private Career OS contained a second installed Next.js application.
   Its generated `node_modules/` and `.next/` trees caused the public Next.js
   build to spend an excessive amount of time scanning files before printing
   its startup banner.
2. Sustained `fileproviderd`, `bird`, and `cloudd` activity caused heavy and
   bursty disk contention during page-data collection. Ten bounded checks over
   approximately ten minutes never produced two quiet readings.

## Locked Decisions

- The private workspace will live at `~/Developer/career-os`.
- The public repository will live at `~/Developer/sales-ops`.
- Career OS remains local-only: no Git repository, tracking, commit, push,
  deployment, or public import.
- The workspaces must be siblings. Do not create a symlink from `sales-ops`
  back to Career OS.
- Keep `career_os/` and `Resume/` in the public repository's `.gitignore` as
  permanent guardrails after migration (both already present).
- Do not treat `outputFileTracingExcludes` as the root fix. It controls traced
  output on a per-route basis and has not been shown to prevent the earlier
  pre-banner filesystem scan.
- Do not retry timed production builds from the iCloud-managed Desktop path.
- Prefer atomic same-volume `mv` over copy-then-delete wherever the source and
  destination are confirmed to be on the same volume — a destructive
  copy-then-delete duplicates private data in flight for no benefit when an
  atomic, easily-reversible rename is available.
- Never use a recursive, whole-tree filesystem scan (`lsof +D <dir>`, a bare
  `find` over the repo root, etc.) as a process-safety check. That repeats the
  same class of large-tree filesystem walk this migration exists to eliminate.
  Process checks must be targeted: enumerate specific process names, then
  inspect each individual PID's cwd/open-handles.

## Session-Boundary Split

The agent session performing this migration runs with its working directory
*inside* the public repository being moved. The public-repository move must
never be triggered from inside that same session. Execution splits into:

- **The agent session** performs the pre-migration gate, the complete private
  Career OS migration, the public-safe `/remember save`, and the pre-move git
  snapshot ("baseline B"), then stops and hands off the exact move command.
- **The user**, outside the agent entirely, in a plain Terminal: closes the
  editor workspace for the old path, confirms no relevant process still
  touches it, and runs the single move command.
- **A fresh agent session** at the new public-repository path runs
  `/remember restore` first, then verifies git/worktree state against
  baseline B, confirms the new path is outside iCloud File Provider, and runs
  the clean build and route verification.

## Pre-Migration Gate

Before moving anything:

- Update this document itself with any corrections found during planning
  (already done as of this revision) — the fresh session treats this file as
  authoritative, so it must be current before handoff.
- Targeted, per-PID process check: enumerate processes by name (node, next,
  npm, vitest, playwright, tsserver, eslint, tailwind, editor helpers), then
  inspect each individual PID's working directory and open handles. Do not
  filter only on command lines that mention the old path by name — editor
  helper processes often don't. Do not run a recursive scan over the repo
  tree.
- Record the public repository's current HEAD, branch, remotes, staged diff
  summary, unstaged diff summary, untracked files, and ignored local
  configuration ("baseline A").
- Treat the existing worktree as dirty. A fast `git status` does not mean the
  worktree is clean.
- Do not commit, stash, reset, clean, push, or rewrite the current worktree as
  part of migration.
- Record private-workspace (`career_os/` and the sibling `Resume/` directory)
  file counts and checksums before moving anything.
- Confirm the destination paths do not already contain unrelated files, and
  confirm neither destination directory is itself inside an unrelated git
  worktree.

## Private Workspace Migration

1. Atomically move (`mv`, not copy) the complete ignored `career_os/`
   directory into `~/Developer/career-os`, preserving its `content/`, `ui/`,
   `outputs/`, `drafts/`, design references, teaching material, and planning
   documents. Re-checksum immediately and compare against the pre-move
   baseline; if it fails, move it back and stop.
2. Atomically move the existing ignored source-resume directory (a sibling
   directory inside the public repository root, gitignored separately, not
   inside `career_os/`) into a private `sources/` subdirectory of the new
   Career OS root. Re-checksum and compare the same way.
3. Update private source-document metadata (specifically any file with a
   hardcoded absolute path into the old repository location) to use paths
   relative to the Career OS root instead.
4. Update private agent briefs and workflow documents so paths are relative to
   the new Career OS root. The runtime relationship remains
   `ui/nextjs` -> `content` and `outputs`. A literal-path grep alone is not
   exhaustive — also manually skim prose documents for path references a grep
   pattern wouldn't catch.
5. Bootstrap the private workspace root as four separate files, each written
   with an editing tool (never a shell redirect):
   - `AGENTS.md` — canonical and complete: privacy rules, path conventions,
     content-safety rules, the "generators run locally only, never deployed"
     rule, and this workspace's own `/remember` convention.
   - `CLAUDE.md` — short pointer: read `AGENTS.md` first, never git-init or
     deploy this workspace, run `/remember restore` before doing anything
     else in a new session here.
   - `memory.md` — this workspace's own memory structure, populated per the
     "Private Memory Cleanup" section below.
   - `.gitignore` — a single `*`, as defense-in-depth against accidental
     tracking.
6. Verify the move (checksums *and* full functional verification — see
   Verification below) before removing anything further from the old public
   repository location. Deletion is not needed for `career_os/`/`Resume/`
   themselves, since step 1/2 already relocated them via `mv` rather than
   copying — but do not proceed past this point until both checks pass.

### Private Memory Cleanup

The tracked public `memory.md` has an uncommitted, purely-appended private
Career OS section (verify the exact line range live — do not assume a
specific range without checking `git diff --stat` and a byte-level `diff`
against `HEAD` first).

- Extract that section to a temporary file.
- Write it into the new private `memory.md` beneath a fixed
  `## Migrated Private Memory — Verbatim` heading.
- Extract only the content beneath that heading back out to a second
  temporary file and `diff` it byte-for-byte against the original extraction —
  expect zero difference. Do not normalize, summarize, or rewrite the
  appendix during this integrity step. Additional structured Career OS memory
  may be added in separate sections only after this verbatim comparison
  passes.
- Only after that passes, edit the public `memory.md` (with an editing tool,
  not a shell truncation) to remove exactly the private section, leaving the
  rest byte-identical to `HEAD`.
- Confirm the public file now matches `HEAD` exactly and contains no personal
  Career OS facts. This is the required state *before* running `/remember
  save` (next).
- Run `/remember save` with an explicit instruction that it must append a
  public-safe "Workspace Migration Handoff" section only — never overwrite
  prior Sales Admin Automation Toolkit memory, and never include candidate
  facts, resume content, target employers, personal filenames, private Career
  OS content, or source-document details. Record only: the new workspace
  paths, migration state, the manifest location, the active landing-page
  worktree state, and pending verification.
- Capture "baseline B" (a fresh git-state snapshot) *after* `/remember save*`
  completes — this, not "empty diff," is the correct post-move comparison
  target, since the public-safe handoff section is expected to be present.

### Generated Career OS Artifacts

The Career OS Next.js `node_modules/` and `.next/` directories are generated
artifacts, not source-of-truth data. If they are currently parked outside the
public project root in a temporary directory from an earlier diagnostic
session:

- Do not restore them beneath the old `sales-ops` path or the new
  `career-os` path.
- Keep the parked copy until the new private workspace has been verified.
- Run `npm ci` in `~/Developer/career-os/ui/nextjs` to create dependencies at
  the correct location.
- Generate a fresh `.next/` build rather than restoring the old build cache.
- Remove the parked artifacts only after successful verification and explicit
  approval. Temporary storage may be purged by the operating system, so these
  artifacts must never be treated as a backup.

## Public Repository Migration

Perform this at a session boundary because moving the repository invalidates
the current editor, terminal, and agent workspace paths — see
Session-Boundary Split above. The agent session prepares everything and stops
before the move; the user performs the move itself.

1. Stop all terminal-launched dev servers, builds, and test processes.
2. Save unsaved editor buffers, close the editor workspace/window for the old
   path, and if any language-server helper process for it lingers, quit the
   editor application entirely.
3. Open a plain Terminal outside the editor, `cd` to the parent of the
   destination.
4. Confirm via targeted per-PID checks (not a recursive scan) that no
   relevant process still touches the old path.
5. Move the complete repository, including `.git`, environment files, staged
   changes, unstaged changes, untracked files, and ignored files, to
   `~/Developer/sales-ops` — a single `mv` command, since both paths are
   confirmed to be on the same volume.
6. Do not let the editor auto-restore the old workspace.
7. Open a fresh agent session at the new path.
8. In that new session: run `/remember restore` first, then compare the new
   HEAD, branch, remotes, `git status`, staged diff, unstaged diff, and
   `memory.md` diff against baseline B (an exact match, including the
   public-safe handoff section — not a literal-empty-diff check).
9. Confirm no Career OS, source-resume, or other private personal files
   remain inside the public repository.
10. Confirm neither new workspace is managed by iCloud File Provider.

Do not leave a second editable copy of `sales-ops` on Desktop. If a temporary
rollback copy is required, label it clearly, do not work from it, and remove
it only after explicit approval and successful verification.

## Verification

### Career OS

- File counts and checksums match the pre-migration inventory.
- No `.git` directory exists in the private workspace or any parent that would
  accidentally track it.
- The content loader finds every resume-version JSON file.
- `npm ci`, type checking, linting, tests, and a production build succeed from
  `~/Developer/career-os/ui/nextjs`.
- PDF generation writes only to the private `outputs/` directory.
- No private content is imported into or copied beneath the public repository.

### Sales Admin Automation Toolkit

- HEAD, branch, remotes, staged changes, unstaged changes, untracked files,
  ignored configuration, and environment files match the pre-migration state.
- `memory.md`'s diff matches baseline B exactly and passes a privacy scan (no
  personal Career OS facts) — not a literal-empty-diff check.
- Type checking and linting pass.
- Run `npm run build` directly with live output; do not pipe it through
  `tail`. For a clean-cache comparison specifically, move (not delete) the
  existing `.next/` and `tsconfig.tsbuildinfo` to a temporary rollback
  location outside the repo first, but keep the migrated `node_modules` as-is
  — a clean Turbopack compile needs a fresh `.next`, not reinstalled
  dependencies, and `npm ci` would add network/install I/O as an unwanted
  second variable. Run `npm ci` only as a separate, later test if
  dependency-install reproducibility specifically needs checking.
- Record time to the Next.js banner, compilation time, page-data collection
  time, and total build time.
- Run one `npx next build --webpack` comparison only if the default build
  still stalls under the non-iCloud path.
- Route verification requires the backend too: `.env` has no
  `NEXT_PUBLIC_API_BASE_URL`, so the frontend defaults to
  `http://127.0.0.1:8000` — without FastAPI running, the dashboard will
  report API failures. Start FastAPI on `127.0.0.1:8000`, confirm `GET
  /health`, then start the Next.js production server on `localhost:3000`
  specifically (matches the backend's default local CORS origin). Verify `/`,
  `/dashboard`, all three workflow routes, and `/reports` at desktop and
  mobile widths, confirm no browser console errors, then stop both processes.
  If port 3000 or 8000 is already occupied, stop the exact stale process
  rather than letting the frontend silently bind to a different port.

## Build-Diagnosis Reminders

- A silent `npm run build 2>&1 | tail -100` is not evidence of a hang because
  `tail` may withhold output until the producer exits.
- Do not run concurrent production builds while diagnosing performance.
- Do not repeatedly clear `.next/` without a falsifiable reason.
- Distinguish pre-banner scanning, compilation, page-data collection, and
  output tracing when reporting build timing.
- Change one variable per diagnostic run.
- If both Turbopack and Webpack stall after migration, investigate filesystem,
  process, dependency, or machine-level contention before changing application
  code.

## Completion Criteria

The migration is complete only when:

- private Career OS files and source documents exist only in the private local
  workspace;
- the tracked public repository contains no personal Career OS content;
- the active public repository runs outside iCloud-managed Desktop;
- both workspaces pass their relevant verification commands, including route
  verification with both frontend and backend running;
- the public production build completes with observable live output; and
- no temporary or duplicate workspace is mistaken for the active source of
  truth.
