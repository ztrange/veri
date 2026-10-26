#!/bin/sh
# worktree-setup.sh — run the target repo's `veri: setup: <cmd>` line once in the run worktree: a shim over veri/worktree_setup.py.
#
# Usage:   worktree-setup.sh <n>   (run from inside the worktree)
# Exit:    0 setup ran; 1 the command failed; 2 bad arguments or an unreadable file; 3 no such line or already set up
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/worktree_setup.py" "$@"
