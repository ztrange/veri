Run the fast command, `{{FAST_CMD}}`, then the suites that `affected-suites.sh` prints
   for your change, each through the wrapper `{{TIMED_TEST_RUN}}`, which records what the run cost and names the tier it belongs to:

{{INCLUDE:_timed-test-run-fast-affected.md}}

   Finish only when both runs are green.
