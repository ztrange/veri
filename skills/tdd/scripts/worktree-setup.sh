#!/bin/sh
# worktree-setup.sh — run the target repo's `veri: setup: <cmd>` line once in the run worktree: a shim over veri/worktree_setup.py.
#
# Usage:   worktree-setup.sh <n>   (run from inside the worktree)
# Exit:    0 setup ran, or no such line; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/worktree_setup.py" "$@"
