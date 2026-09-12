{{SHARED}}

## Phase: verify-red

A developer agent has written **one new failing test** at `{{TEST_PATH}}` (the target
test is `{{TARGET_TEST}}`). Confirm the Red step is sound.

### The issue's behavior spec

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
     correctness is in doubt.

PASS only if the test fails for the right reason AND is a clean, behavior-level pin of
the criterion.
