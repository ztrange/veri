#!/bin/sh
# step-close.sh — a step's close-out after a passing or skipped verify-refactor (SKILL.md *Refactor loop*, sub-step 6's
# PASS branch), in one call: a shim over veri/step_close.py.
#
# Usage:   step-close.sh <n>
# Exit:    0 every call clean; 2 bad arguments, no refactor-pending step, a missing or mismatched input,
#          or a branch-base record (.tdd/issue-<n>-branch-base in the main tree) missing or not hex;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/step_close.py" "$@"
