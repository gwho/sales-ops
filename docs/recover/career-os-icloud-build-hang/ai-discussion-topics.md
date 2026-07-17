# AI Discussion Topics — career_os + iCloud Build Hang

## Recognizing failure modes

1. What specifically made this a `/recover` "Failure Mode 1" (isolated, diagnosable bug)
   rather than "Failure Mode 3" (wrong foundation)? What evidence would have pointed
   toward Failure Mode 3 instead?
2. Why does "diagnose before touching code" matter more when a symptom is a *hang* than
   when it's a clear error message? What's different about the evidence available in each
   case?

## Reading process state directly

3. Why is "the process is using 0% CPU" ambiguous on its own — what are at least two very
   different real states that would both show near-0% CPU?
4. What does it mean that `.next/` had not been created at all after 13+ minutes, and why
   is that a stronger signal than "the build seems slow"? What would a *merely slow but
   healthy* build's `.next/` directory look like at the 1-minute mark versus this case?
5. Why did checking file-descriptor/socket state (via `lsof`) matter in ruling out a
   network-related hang, separate from the stack sample?

## Stack sampling as a diagnostic tool

6. What does a repeating, bounded-depth call cycle in a stack sample tell you that a truly
   unbounded/infinite recursive stack would not?
7. Why does `node::fs::ReadFileUtf8` → `uv_fs_read` → a blocking `read()` syscall, repeated
   across nearly 100% of samples, specifically indicate a synchronous directory walk
   rather than, say, a slow single large file read?
8. What's the tradeoff between taking one 3-second stack sample versus several samples
   over a longer window? When would a single sample be misleading?

## Falsification and single-variable testing

9. Why was moving `career_os` out (not deleting it) chosen as the test, and why did that
   choice matter for being able to trust the result either way?
10. What would it have meant if removing `career_os` had *not* changed the build's
    behavior at all? Would that have ruled out the hypothesis, or just made it
    insufficient on its own?
11. After the first cause was fixed, a second stall appeared. What's the risk of assuming
    "it's the same bug, must not be fully fixed" without checking, versus what was actually
    done (re-inspect the process tree, re-sample the stack, check system load
    independently)?

## Environmental factors in local development

12. Why can a directory being under iCloud's "Desktop & Documents" sync feature slow down
    unrelated developer tooling, in principle — what is the file provider daemon actually
    doing that would compete with a build process for resources?
13. What's the argument for treating "the build is slow because of iCloud sync" as
    something requiring a structural fix (moving the project) rather than something to
    just wait out or work around per-session?
14. Why would a build-timing measurement taken while `fileproviderd`/`bird`/`cloudd` are
    still actively spiking be considered unreliable, even if the build eventually
    completes? What's the right response when a bounded quiet-check window expires without
    ever reaching "quiet"?
