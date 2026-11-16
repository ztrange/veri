#!/bin/sh
# stack-pr.sh — the one open pull request from the stack branch to the default branch, which makes CI run on each push
# to the stack: a shim over veri/stack_pr.py.
#
# usage:   stack-pr.sh   (run in the target repository's clone; no arguments)
# Exit:    0 its url printed, opened (ready, not a draft; its body says it is never merged itself and that slices are cut
#          from it, and closes nothing) when the stack is ahead and none is open; 3 the stack is not ahead of the default
#          branch, origin holds no stack, or stack-branch.sh exits 3: nothing opened; 2 GitHub gave no answer, two open
#          pull requests track the stack, stack-branch.sh exits 2, a fetch got no answer, or bad arguments: nothing opened
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_pr.py" "$@"
