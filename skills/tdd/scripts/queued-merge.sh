#!/bin/sh
# queued-merge.sh — a merge that waits its turn on the merge lock: a shim over veri/queued_merge.py.
#
# Usage:   queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->
# Exit:    0 merged and cleaned up; 1 red CI or PR not reported merged (lock released); a rebase
#          conflict or refused push exits with git's code (lock kept); 2 no answer — bad arguments,
#          an unresolvable ref, a worktree lacking a commit origin/<branch> has (nothing pushed),
#          or a failed cleanup step after the merge (named on stderr)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/queued_merge.py" "$@"
