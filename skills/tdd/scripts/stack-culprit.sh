#!/bin/sh
# stack-culprit.sh — the issue whose end turned the stack red, and the cases it broke: a shim over
# veri/stack_culprit.py.
#
# usage:   stack-culprit.sh <red-sha>   (run in the target repository's clone)
# Reads the cases CI named red on <red-sha> (the failed log of the newest red answer among its workflows, at the attempt that answered, as stack-red.sh decides it), at most the
# first 5, and runs each alone through the repository's `veri: one test file:` command at each issue end from the
# newest tested commit at or below <red-sha> (origin/<default> when none is) to <red-sha>, oldest first, in a detached
# worktree of its own under .tdd/, removed on every exit; at most 20 issue ends. A case is red when its run exits
# non-zero with a failure line naming it, absent when not found there; the exit code alone never decides.
# Exit:    0 a case is red at an issue end: printed, one per line, `red: <red-sha>`, `issue: <n>…`, `commit: <sha>`,
#          `before: <sha>`, then `case: <case><TAB><first FAIL line>` per red case; 3 no issue end turns a case red
#          (nothing printed, stderr naming the cases run); 2 an unreadable log or one naming no case, a <red-sha> not on
#          origin/<default>..origin/<stack>, an alone run with no answer, a case absent at <red-sha> itself, more than 20 untested ends, no answer from GitHub or a fetch,
#          stack-branch.sh not exiting 0, a worktree it cannot add, or bad arguments. On 0 or 3 it comments the answer
#          and the red run's url once on the stack's tracking pull request.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_culprit.py" "$@"
