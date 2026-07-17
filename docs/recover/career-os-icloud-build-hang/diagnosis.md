# Diagnosis — `npm run build` Hang (career_os + iCloud Contention)

## What broke

`npm run build` (piped through `tail -100`) produced no output and never completed within
its 120-second timeout, moved to a background task, and stayed silent for 14+ minutes with
zero visible progress — no Next.js startup banner, no `.next/` directory created.

## Failure mode: isolated, diagnosable — not a polluted session or a wrong foundation

This was **Failure Mode 1** in `/recover` terms: a specific, isolated symptom (one command
hanging), with the rest of the project (typecheck, lint, the actual landing-page feature
code) working correctly, and no prior failed correction attempts yet. The recovery
procedure that applies here is "diagnose before touching code" — explicitly *not*
"try a fix and see if it works," which is what makes the rest of this session's approach
(stack sampling before any file was touched) the correct one rather than a shortcut.

## Why a plain retry or `.next` clear wasn't trusted as evidence

The first corrective attempt already tried was: delete `.next`, rerun `npm run build`. That
alone did not resolve anything and, per `/recover`'s own reminder, a silent
`npm run build 2>&1 | tail -100` is not evidence of a hang — `tail` can withhold all output
until the producer process exits, so an apparently-frozen terminal could just be `tail`
buffering, not a real stall. This is why the next step was **not** another blind retry, but
direct process inspection.

## How the diagnosis was actually reached

1. **Retrieved live process state**, not just command output: `ps` for the exact PID tree
   (`npm run build` → `node .../next build`), confirming the process was alive, using
   ~0% CPU on average over 13+ minutes, and — critically — that `.next/` had never been
   created at all. A healthy `next build` creates `.next/` within seconds; its total
   absence after 13 minutes was the first strong signal this wasn't "slow," it was stuck.

2. **Took a macOS `sample` stack trace** of the actual `next build` process (`sample <pid> 3`)
   rather than guessing. The call graph showed ~100% of samples inside a repeating,
   bounded-depth recursive cycle bottoming out in `node::fs::ReadFileUtf8` →
   `uv_fs_read` → a blocking `read()` syscall — the signature of a **synchronous
   directory walk performing one blocking file read per file**, not a hung network call,
   not an interactive prompt (stdin was already redirected from `/dev/null`), and not true
   infinite recursion (the stack depth was bounded, and the sample-to-sample counts varied,
   which a true infinite loop on one fixed operation wouldn't do).

3. **Investigated what that recursive scan could be walking.** `career_os/` — a private,
   gitignored directory nested inside the project — was found to be 774MB across 24,584
   files, including a second, fully-installed Next.js application at
   `career_os/ui/nextjs/node_modules`. This became the leading hypothesis: something in
   Next's own pre-banner project analysis was walking into this untracked, oversized
   subtree.

4. **Ran a single-variable falsification test**, with explicit user approval before
   executing it: temporarily `mv career_os /tmp/career_os-parked` (fully reversible, not a
   delete), then reran the build unbuffered. The startup banner and `.next/` creation
   appeared within seconds — a night-and-day change from 14+ minutes of nothing. This
   directly confirmed the hypothesis rather than merely being consistent with it.

## A second, independent stall found by the same discipline

After removing `career_os`, the build proceeded further (compiled successfully, banner
printed) but then stalled again during "Collecting page data," this time inside a
*different* worker process (`.next/build/*.js`), again showing the same
`uv_fs_read`-heavy pattern via a fresh `sample`. Rather than assume this was the same bug
recurring, the process tree and `.next/` file count were re-checked (frozen at 23 files for
5+ minutes — no progress, not just slow), and `ps`/`top` were checked for overall system
load. This surfaced a second, unrelated cause: `fileproviderd`/`bird`/`cloudd` (macOS
iCloud Drive's file-provider daemons) were consuming 60-90%+ CPU, and `brctl status`
confirmed `~/Desktop` was under active "Desktop & Documents" iCloud sync with a real,
growing pending-sync queue — triggered in part by the earlier `mv` operations themselves.

## Signs that pointed to each failure mode specifically

- **career_os cause:** zero child processes spawned, zero `.next/` output, ~100% of a
  stack sample in synchronous file reads, resolved instantly and completely by removing
  one specific directory — a clean, single-variable, reproducible result.
- **iCloud cause:** the *build's own* worker process was doing legitimate compute
  (`Array.map()` over routes) interspersed with the same file-read pattern, system-wide
  CPU was dominated by non-build processes, and `brctl status` gave direct, independent
  confirmation of an active sync backlog — not just an inference from build behavior
  alone.

Distinguishing these two required not stopping at the first plausible explanation:
removing `career_os` did fix the *first* symptom completely, but a second symptom
persisted under different, environmentally-driven conditions — treating that as "the same
bug, must not be fully fixed yet" would have been the wrong conclusion.
