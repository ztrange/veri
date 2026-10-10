{{SHARED}}

## Phase: verify-migrate

A developer agent has finished the **migrate** phase of an interface change (the code
around `{{TEST_PATH}}`). In the migrate phase the product callers of the old interface move
to the new interface, and the old interface stays in place. Behaviour does not change, and
test files stay frozen. The phase started at `{{BASE_SHA}}`. Review what it changed with
`git diff {{BASE_SHA}}..HEAD`, and do not read the range's commit messages: `git log` and
`git show` on the range carry the author's rationale. Render one verdict on the settled
result.

{{STEP}}### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **Still green.** Run the fast command, `{{FAST_CMD}}` (`detect-test-command.sh --tier fast`
   prints it), then run the suites `affected-suites.sh` prints for the files the range
   touched yourself; both must be **green**. Make each of those two runs through the wrapper
   {{INCLUDE:_timed-test-run-tier.md}}:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   {{INCLUDE:_exit-status-back.md}} so a red run stays red.
2. **The callers moved.** Every product caller of the old interface now calls the new
   interface.
3. **The old interface stays.** Removing it is the contract phase's work.
4. **Test files stay frozen.** A range that touches a test file is a REJECT.

PASS if the suites are green, every product caller moved to the new interface and no test
file changed. REJECT, naming the specific problem, otherwise.
