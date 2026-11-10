#!/bin/sh
# queued-merge.sh — a merge that waits its turn on the merge lock: a shim over veri/queued_merge.py.
#
# Usage:   queued-merge.sh <pr-url> <worktree> <branch> <tag-message|->
# Exit:    0 merged and cleaned up; 1 red CI or a merge call that exited 0 with the PR not reported
#          merged (lock released); a merge call that exits non-zero exits with its code (lock released)
#          unless the PR reads merged within VERI_MERGE_SETTLE_READS re-reads (default 10),
#          VERI_MERGE_SETTLE_SLEEP s apart (default 3); a rebase conflict or refused push exits with
#          git's code (lock kept); 2 no answer — bad arguments, a PR already merged, closed unmerged,
#          unreadable or with its head already on origin/main (refused before any rebase or push),
#          an unresolvable ref, a worktree lacking a commit origin/<branch> has (nothing pushed),
#          or a failed cleanup step after the merge (named on stderr)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/queued_merge.py" "$@"
