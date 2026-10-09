{{SHARED}}

## Phase: verify-green

A developer agent has written the implementation intended to make the target test
`{{TARGET_TEST}}` at `{{TEST_PATH}}` pass. Confirm the Green step is a genuine pass.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **The target test passes.** Run `{{TARGET_TEST}}` yourself; it must pass. Make that run
   through the wrapper {{INCLUDE:_timed-test-run.md}} and names the
   tier it belongs to:

       {{TIMED_TEST_RUN}} target '{{TEST_PATH}}' <the command that runs the target test>

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.
2. **The fast command and the affected suites are green.** Run the fast command,
   `{{FAST_CMD}}` (`detect-test-command.sh --tier fast` prints it), then run the suites `affected-suites.sh`
   prints for the change yourself, not just the target test. There must be **no
   regressions** — every test that passed before must still pass. A new pass bought with a
   broken sibling test is a REJECT. This is not the project's full test suite: the
   conductor runs that once, before it readies the PR. Make each of those two runs through
   the same wrapper, each under its own tier:

{{INCLUDE:_timed-test-run-fast-affected.md}}

3. **The pass is genuine.** The behavior the spec asks for is actually present — the test
   was not made to pass by weakening the assertion, deleting cases, skipping/xfailing the
   test, or hard-coding the exact expected value in a way that doesn't implement the
   behavior. Any of these is a REJECT.{{REPLACES_CASE}}{{SUITE_REPAIR}}
4. **Only code a test requires.** REJECT production code that no test requires — a
   branch, option, flag or parameter whose removal leaves every test green — and name
   that code in REASON:, since a verdict that only says something is unneeded costs the
   revise leaf the search you have already done. Establish it the way verify-pin
   establishes a mutation: copy the file first — `cp <file> <file>.orig` — then
   remove the code yourself and run the suites again, and if they stay green nothing
   required it. Then restore the tree exactly — `mv <file>.orig <file>`, and confirm that
   `git diff` prints what it printed before the probe — before you report, since a verifier
   that reports first leaves the developer's tree mutated for the next leaf.
5. {{INCLUDE:_verify-comments-lead.md}} change {{INCLUDE:_verify-comments-allowed.md}} change {{INCLUDE:_verify-comments-never-reject.md}}

PASS only if the target test, the fast command and the affected suites are green and the pass genuinely reflects
the behavior the spec requires.
