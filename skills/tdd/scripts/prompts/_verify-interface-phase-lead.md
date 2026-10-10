The phase started at `{{BASE_SHA}}`. Review what it changed with
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