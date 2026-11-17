#!/bin/sh
# run-start.sh — SKILL.md step 1's fixed calls after preflight, in one call: a shim over veri/run_start.py.
#
# Usage:   run-start.sh <n>
# Exit:    0 every call clean; 2 bad arguments or a missing .tdd/issue-<n>-preflight; otherwise the stopping
#          call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/run_start.py" "$@"
