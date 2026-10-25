#!/bin/sh
# queued-merge.sh — a merge that waits its turn on the merge lock: a shim over veri/queued_merge.py.
#
# Usage:   queued-merge.sh <pr> <worktree> <branch> <tag-message|->
# Exit:    0 merged; 1 stopped by red CI (lock released); 2 no answer — bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/queued_merge.py" "$@"
