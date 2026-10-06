{{SHARED}}

## Phase: verify-red

A developer agent has written **one new failing test** at `{{TEST_PATH}}` (the target
test is `{{TARGET_TEST}}`). Confirm the Red step is sound.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

{{BUG_REPRODUCTION}}
### Your checks

1. **It runs and fails.** Run the suites `affected-suites.sh` prints for the change
   yourself, not one suite picked by hand. The target test must **fail** — check 2 is
   where the way it failed is judged. Make that run through the wrapper
   `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to:

       {{TIMED_TEST_RUN}} affected '<the suites affected-suites.sh printed>' <the command that runs them>

   The wrapper hands the command's own exit status straight back, so a red run stays red —
   and red is what this check is after.
2. **It fails for the right reason.** The failure must be the *missing behavior from the
   spec*: an absent function, script, file, route or field, or a wrong returned value. An
   error on exactly the name the step introduces is a valid red — in bash, Python or JS a
   name that does not exist yet errors before any assertion runs, so a test that cannot
   even reach its assertions for that reason is red, not broken. Any *other* error before
   an assertion is a REJECT: a typo'd name, a wrong path, a missing fixture, a syntax error
   in the test, or an unrelated environment problem.
   A test that fails for the wrong reason is a REJECT.
3. **Quality of the test.** REJECT if the test is:
   - **trivial** — it cannot meaningfully fail once the behavior exists (asserts a
     constant, `assert True`, tests nothing the spec asks for), or
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

PASS only if the test fails for the right reason AND is a clean, behavior-level pin of
the criterion.
