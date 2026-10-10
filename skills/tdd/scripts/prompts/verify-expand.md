{{SHARED}}

## Phase: verify-expand

A developer agent has finished the **expand** phase of an interface change (the code
around `{{TEST_PATH}}`). The expand phase adds the new interface to production, and the
old interface becomes a proxy that delegates to it. Behaviour does not change, and test
files stay frozen. The phase started at `{{BASE_SHA}}`. Review what it changed with
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
2. **The new interface exists.** Production gains the new interface the step names.
3. **The old interface is a proxy.** The old interface delegates to the new one; no caller
   has moved yet.
4. **Test files stay frozen.** A range that touches a test file is a REJECT.

PASS if the suites are green, the new interface exists, the old one is a proxy over it and
no test file changed. REJECT, naming the specific problem, otherwise.
