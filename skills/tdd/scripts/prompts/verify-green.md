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
2. **The fast command and the test files covering the change are green.** Run the fast command,
   `{{FAST_CMD}}` (`detect-test-command.sh --tier fast` prints it), then run the test files covering the files
   the change touched, as `affected-suites.sh` prints them, yourself, not just the target test. There must be **no
   regressions** — every test that passed before must still pass. A new pass bought with a
   broken sibling test is a REJECT. This is not the project's full test suite: the
   conductor runs that once, before it readies the PR. Make each of those two runs through
   the same wrapper, each under its own tier:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   {{INCLUDE:_verify-coverage-probe.md}}

   Run only the commands this prompt names, and never set `VERI_TEST_LOCK`. When a command
   gives no answer (it times out, is killed or cannot run), end without a verdict rather
   than rerunning it another way.

3. **The pass is genuine.** The behavior the spec asks for is actually present — the test
   was not made to pass by weakening the assertion, deleting cases, skipping/xfailing the
   test, or hard-coding the exact expected value in a way that doesn't implement the
   behavior. Any of these is a REJECT.{{REPLACES_CASE}}{{SUITE_REPAIR}}{{CI_REPAIR}}{{FIXTURE_REPAIR}}
4. **Only code a test requires.** REJECT production code that no test requires — a
   branch, option, flag, parameter or guard whose removal leaves every test green — and name
   that code in REASON:, since a verdict that only says something is unneeded costs the
   revise leaf the search you have already done. Probe every branch, option, flag,
   parameter and guard the step's diff added before you answer, and do not stop at the
   first one whose removal leaves every test green: name each such item in REASON:, one
   per line, since the revise leaf fixes only what you name. Production code outside the
   step's criterion is rejected by asking for its removal, never by offering a test for it,
   and is not named on a `MISSING_TEST:` line. REJECT, too, when your own reason for a PASS
   would name a guard, argument or clause whose removal turns no case of the fast tier plus
   the `changed` run red. Establish each by a mutation of your own: remove the code through
   `{{MUTATION_PROBE}} <file> <old> <new> -- <one command running {{FAST_CMD}} and the test files affected-suites.sh prints, together>`,
   never those test files or one test file alone, so a branch only a fast-tier case
   requires is not judged required by no test. It edits, runs the
   command and restores the file; if it exits 1 (the suites stay green) nothing
   required the code, and an exit of 2 gives no verdict. If that probe exits 2 and its
   stderr names an allowed address domain, any email address in `<old>`/`<new>` must be on
   that domain: retry with one that is. Confirm that
   `git diff` prints what it printed before the probe — before you report, since a verifier
   that reports first leaves the developer's tree mutated for the next leaf.
5. {{INCLUDE:_verify-comments-lead.md}} change {{INCLUDE:_verify-comments-allowed.md}} change {{INCLUDE:_verify-comments-never-reject.md}}
6. **No exit code is discarded.** Run `{{DISCARDED_EXIT}}` in the worktree. REJECT each
   `<file>:<line>` it prints, naming that line, unless the spec says that call's failure is
   ignored. Its exit 0 or 3 passes this check; on its exit 2, write no `VERDICT:` line.

When a REJECT's cause is a behaviour no test pins — a line the step needs that every test
leaves unchecked — put one `MISSING_TEST: <behaviour>` line, naming that behaviour, before
the `VERDICT:` line. A rejection for a product defect carries no such line. Nor does a rejection for production
code outside the step's criterion: that code is not named on a `MISSING_TEST:` line, since
it is rejected by asking for its removal, not by a test.

When the step above is followed by a list of the ledger's later unchecked steps and the
`MISSING_TEST:` behaviour is one of them, also put one `LATER_STEP: <step text>` line, copying
that step's text from the list, before the `VERDICT:` line.

On a REJECT, put one `CHECK: <n>` line before the `VERDICT:` line, `<n>` the number of the
lowest-numbered of the checks above that failed.

PASS only if the target test, the fast command and those test files are green and the pass genuinely reflects
the behavior the spec requires.
