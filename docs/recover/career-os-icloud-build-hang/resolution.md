# Resolution — `npm run build` Hang (career_os + iCloud Contention)

## Root causes (two, independent)

1. **`career_os/`, a private gitignored directory nested inside the public repo,
   contained a second, fully-installed Next.js application** (its own `node_modules` +
   `.next`, ~774MB / 24,584 files). Something in `next build`'s own pre-banner startup
   scanning walked into this untracked subtree, doing a slow, synchronous, one-file-at-a-
   time read of thousands of files before the build ever printed its own startup banner.

2. **`~/Desktop` (and everything under it, including this whole repo) is under active
   iCloud Drive "Desktop & Documents" sync.** Separately from cause 1, macOS's
   `fileproviderd`/`bird`/`cloudd` daemons were contending for the same disk I/O the
   build's own "Collecting page data" phase needed, at times spiking to 90%+ combined
   CPU — a second, environment-level source of slowness with no code-level fix.

Neither cause was a bug in the newly-written portfolio-landing-page code — both were
confirmed independent of it (the landing page's own components do no build-time file I/O
beyond a static JSON import).

## What was changed to fix it

The actual fix was **not** a code or configuration change to the application — it was a
filesystem reorganization, planned and executed as a separate, explicitly-approved
migration (see `docs/architect/workspace-migration-and-build-recovery/`):

- `career_os/` (and a sibling private `Resume/` directory) were moved out of the public
  repo entirely, to a new sibling workspace at `~/Developer/career-os` — permanently
  removing the nested-Next.js-app scan target.
- The public repo itself was planned to move from `~/Desktop/sales-ops` (iCloud-managed)
  to `~/Developer/sales-ops` (outside iCloud's Desktop-sync scope) — removing the second
  cause. As of this writing that move is still pending a user-run handoff step (see the
  workspace-migration session docs for why the move can't be triggered from inside the
  same agent session that's working inside the folder being moved).

**Explicitly rejected as "the fix":** `next.config.ts`'s `outputFileTracingExcludes`. It
governs per-route *output* tracing (used for serverless bundling), not the pre-banner
project-analysis scan that was actually observed hanging — applying it would have been
treating a plausible-sounding Next.js config knob as a fix without evidence it touches the
actual code path involved.

## What was discarded

- The idea of leaving `career_os/` in place and trying to configure Next.js around it
  (via tracing excludes or similar) — discarded once the stack-sample evidence showed the
  hang was in an early, pre-configuration-load phase of the build, not something a
  build-time config option was likely to reach.
- Treating the `career_os` fix as sufficient on its own — discarded once the second stall
  (iCloud contention) was found under quiet-but-not-verified-quiet conditions after the
  first cause was removed.

## What the session learned that wasn't known before

- **`tail`-piped command output is not reliable evidence of a hang.** `npm run build 2>&1 |
  tail -100` can sit silently for the same reason whether the underlying process is dead
  slow or working normally but not yet finished — `tail` withholds everything until the
  producer exits. Every diagnostic build in this session onward was run unbuffered
  (`npm run build` directly, no pipe) specifically so a live banner/progress line would be
  visible as it happened.
- **macOS's `sample` tool (built-in, no extra install) can distinguish "blocked on I/O,"
  "spinning on CPU," and "genuinely idle waiting for an event"** from a single 3-second
  stack capture — this is a much stronger diagnostic than process CPU% alone, which can
  look similar (near-0%) for both "hung" and "waiting on a fast operation" states.
- **A project directory living inside iCloud's Desktop-sync scope is a real, and
  under-appreciated, source of dev-tooling slowness** — not just for this build, but
  potentially for any tool doing heavy file I/O in that tree, independent of anything in
  the project's own code or dependencies.
- **Diagnosing under contended conditions produces noisy, hard-to-trust timing data.** A
  later bounded re-test (a diagnostic checkpoint before the planned repo move) explicitly
  required iCloud CPU to drop below a threshold for two consecutive checks before running
  a timed build at all — and when that condition wasn't met within the bounded window, the
  correct response was to report the test as environmentally blocked rather than run the
  build anyway and risk treating contaminated timing data as a real measurement.
