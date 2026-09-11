{{SHARED}}

## Phase: verify-pin

A developer agent has written **one new test** at `{{TEST_PATH}}` (the target test is
`{{TARGET_TEST}}`) for a criterion the code **already satisfies**, so there is nothing to
make fail. Confirm the test is a genuine **regression pin** worth committing.

### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **It passes now.** Run the target test yourself against the current, unmodified code.
   It must **pass** — not error, not skip.
2. **It fails under mutation.** Identify the behavior the spec criterion describes, then
   **break it yourself** with a minimal edit to the production code (remove the guard,
   invert the condition, drop the branch) and run the target test again: it must **FAIL**.
   Then restore the code exactly — `git checkout -- <file>`, and confirm with `git diff
   --exit-code` — before you report. A test that still passes with the behavior removed
   pins nothing: that is a REJECT.
3. **Quality of the test.** REJECT if the test is:
   - **trivial** — it asserts a constant or something no plausible change could break, or
   - **over-coupled** — it asserts on private internals / implementation details rather
     than the observable behavior the spec describes, or
   - **too complex** — it pins more than this one criterion, or is so elaborate its own
     correctness is in doubt.

PASS only if all three hold: it passes now, it fails under the mutation, and it is a
clean, behavior-level pin of the criterion. Leave the working tree exactly as you found it.
