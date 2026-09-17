{{SHARED}}

## Phase: verify-green

A developer agent has written the implementation intended to make the target test
`{{TARGET_TEST}}` at `{{TEST_PATH}}` pass. Confirm the Green step is a genuine pass.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **The target test passes.** Run `{{TARGET_TEST}}` yourself; it must pass.
2. **The full suite is green.** Run the project's **full test suite**, not just the
   target test. There must be **no regressions** — every test that passed before must
   still pass. A new pass bought with a broken sibling test is a REJECT.
3. **The pass is genuine.** The behavior the spec asks for is actually present — the test
   was not made to pass by weakening the assertion, deleting cases, skipping/xfailing the
   test, or hard-coding the exact expected value in a way that doesn't implement the
   behavior. Any of these is a REJECT.

PASS only if the target test and the full suite are green and the pass genuinely reflects
the behavior the spec requires.
