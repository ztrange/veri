{{SHARED}}

## Phase: verify-red

A developer agent has written **one new failing test** at `{{TEST_PATH}}` (the target
test is `{{TARGET_TEST}}`). Confirm the Red step is sound.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **It runs and fails.** Run the test yourself. It must **fail**, not error before it
   reaches its assertions.
2. **It fails for the right reason.** The failure must be the *missing behavior from the
   spec* (e.g. an absent function/route/field, or a wrong returned value) — NOT an
   import typo, a syntax error, a missing fixture, or an unrelated environment problem.
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
