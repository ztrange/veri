#!/bin/sh
# timed-test-run.sh — run a test command and record what it cost in one test-run event: a shim over veri/timed_test_run.py.
#
# usage: timed-test-run.sh <tier> <suites> <cmd> [args …]
# Output:  the command's whole output, stdout and stderr merged, goes to .tdd/test-runs/<started>-<tier>-<pid>.log under
#          the worktree's top level, never to the caller; in its place stdout gets a bounded report: one line with the
#          tier, exit status, seconds and the passed/failed/error counts of pytest's summary line ("counts not found"
#          when none), at most 10 of pytest's FAILED/ERROR short-summary lines (each its case and first failure line,
#          cut to 300 characters), "… <k> more failing cases cut" past 10, and the saved file's path. Never the traceback.
# Exit:    the command's own status, unmapped; 2 a missing or empty <tier> or <cmd>, or a log directory it cannot create
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/timed_test_run.py" "$@"
