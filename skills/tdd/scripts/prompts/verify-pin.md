{{SHARED}}

## Phase: verify-pin

A developer agent has written **one new test** at `{{TEST_PATH}}` (the target test is
`{{TARGET_TEST}}`) for a criterion the code **already satisfies**, so there is nothing to
make fail. Confirm the test is a genuine **regression pin** worth committing.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **It passes now.** Run the target test yourself against the current, unmodified code.
   It must **pass** — not error, not skip.
2. **It fails without the behavior.** First run
   `{{MUTATION_PROBE}} --before {{BRANCH_BASE}} --keep '{{TEST_PATH}}' -- <command that runs the target test>`.
   It restores the production files the branch changed to the branch point, runs the target
   test and restores the tree: the target test must **FAIL**. Only when that probe exits 2
   because no file differs from the branch point, break the production code yourself with a
   minimal edit (remove the guard, invert the condition, drop the branch) through
   `{{MUTATION_PROBE}} <file> <old> <new> -- <command that runs the target test>`,
   which edits, runs the command against the mutation and restores the file: the target test must **FAIL**.
   If that probe exits 2 and its stderr names an allowed address domain, any email address in
   `<old>`/`<new>` must be on that domain: retry with one that is.
   That exit 2 can also mean `<old>` is absent from the working-tree file or the command
   fails on the unmutated file: fix `<old>` or the command and retry, and never report
   such an exit as a PASS.
   A probe exiting 2 gives no verdict, and one exiting 1 (the command still passed) is never a PASS.
   Confirm that `git diff` prints what it printed before the probe before you report. A test that still passes on the real
   before-state, or with the behavior removed by hand when no before-state exists, pins
   nothing: that is a REJECT naming which run stayed green ("the real before-state stays
   green", or "the hand mutation stays green").
   Make both of those runs — the one in check 1 and the one after the mutation — through
   the wrapper `{{TIMED_TEST_RUN}}`, which records what each run cost and names the tier it
   belongs to:

       {{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs the target test>

   {{INCLUDE:_exit-status-back.md}} so the mutated run stays
   red — and red is what check 2 is after.
3. **Quality of the test.** REJECT if the test is:
   - **missing a named case** — the step's text names a test case the step asks to be
     pinned (a "separate case", a second behaviour) and the change adds no case for it:
     REJECT naming the missing case, or
   - **trivial** — it asserts a constant or something no plausible change could break, or
   - **over-coupled** — it asserts on private internals / implementation details rather
     than the observable behavior the spec describes, or
   - **too complex** — it pins more than this one criterion, or is so elaborate its own
     correctness is in doubt, or
   - **pins mechanism, not behaviour** — it asserts a process count, a fork count, or a
     timing (those belong to `make profile`, never to an assertion), or counts real
     process launches via a `PATH` shim over a suite run where the criterion actually names
     a single call: that call belongs to an in-process spy on the one wrapper function, not
     a shim counting real processes, or
   - **not lightweight** — it exercises a costly real dependency (network, a git remote,
     the `claude` binary, a real sleep/wait, a server) that a stub, fake or the injected
     clock could stand in for, and the behavior under test is not that dependency's real
     use, or
   - **fails on an incidental error** — its only observable is that something throws or
     exits non-zero, with no assertion on which error or on the behaviour, unless that
     specific error is what the criterion names, or
   - **not self-contained** — it runs another test suite, whole or sliced, or re-runs the
     suite it lives in, instead of exercising the unit directly.

PASS only if all three hold: it passes now, it fails under the mutation, and it is a
clean, behavior-level pin of the criterion. Leave the working tree exactly as you found it.
