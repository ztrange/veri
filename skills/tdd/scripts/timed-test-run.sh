#!/bin/sh
# timed-test-run.sh — run a test command and record what it cost in one test-run event: a shim over veri/timed_test_run.py.
#
# usage: timed-test-run.sh <tier> <suites> <cmd> [args …]
# Exit:    the command's own status, unmapped; 2 a missing or empty <tier> or <cmd>
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/timed_test_run.py" "$@"
