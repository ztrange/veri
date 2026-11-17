#!/bin/sh
# stack-red.sh — whether CI's latest answer on the stack branch is red, which freezes joins: a shim over
# veri/stack_red.py.
#
# usage:   stack-red.sh   (run in the target repository's clone; no arguments)
# Reads every workflow's runs; while the newest is a re-run not completed, its previous attempt answers (unreadable:
# exit 2); while it is a first attempt not completed, its own head's newest completed run answers.
# Exit:    0 the stack is red: one line printed, `<head-sha> <run-url> <conclusion>`, of the newest by creation time of
#          the newest 100 workflow runs GitHub lists for the stack branch that completed with a conclusion other than
#          cancelled, when that conclusion is not success, neutral or skipped; 3 it concluded success, neutral or
#          skipped, or none of the 100 completed with a conclusion other than cancelled (nothing printed, one stderr
#          line saying which); 2 GitHub gave no answer or one not of the workflow-runs shape, a fetch of origin got no
#          answer, stack-branch.sh did not exit 0 (3 included), or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_red.py" "$@"
