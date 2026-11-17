#!/bin/sh
# stack-red.sh — whether CI's latest answer on the stack branch is red, which freezes joins: a shim over
# veri/stack_red.py.
#
# usage:   stack-red.sh   (run in the target repository's clone; no arguments)
# Reads every workflow's runs and decides each workflow alone (red if any is; else exit 2 if any gave no answer); a
# run re-run or cancelled at a later attempt answers from its first earlier attempt that completed uncancelled.
# Exit:    0 the stack is red: one line printed, `<head-sha> <run-url> <conclusion>`, of the newest red answer among
#          the workflows of the newest 100 workflow runs GitHub lists for the stack branch (red: a conclusion other
#          than success, neutral or skipped); 3 every workflow that has answered concluded success, neutral or
#          skipped, or none has answered (nothing printed, one stderr line saying which); 2 no workflow is red and
#          one gave no answer (an earlier attempt that cannot be read or reads not completed), GitHub gave no answer
#          or one not of the workflow-runs shape, a fetch of origin got no answer, stack-branch.sh did not exit 0
#          (3 included), or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_red.py" "$@"
