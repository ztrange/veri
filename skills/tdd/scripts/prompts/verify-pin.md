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
2. **It fails under mutation.** Identify the behavior the spec criterion describes, copy
   the file first — `cp <file> <file>.orig` — then **break it yourself** with a minimal
   edit to the production code (remove the guard, invert the condition, drop the branch)
   and run the target test again: it must **FAIL**. Then restore the code exactly —
   `mv <file>.orig <file>`, and confirm that `git diff` prints what it printed before the probe — before you report. A test that still passes with the behavior removed
   pins nothing: that is a REJECT.
   Make both of those runs — the one in check 1 and the one after the mutation — through
   the wrapper `{{TIMED_TEST_RUN}}`, which records what each run cost and names the tier it
   belongs to:

       {{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs the target test>

   {{INCLUDE:_exit-status-back.md}} so the mutated run stays
   red — and red is what check 2 is after.
3. **Quality of the test.** REJECT if the test is:
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
   - **not self-contained** — it runs another test suite, whole or sliced, or re-runs the
     suite it lives in, instead of exercising the unit directly.

PASS only if all three hold: it passes now, it fails under the mutation, and it is a
clean, behavior-level pin of the criterion. Leave the working tree exactly as you found it.
