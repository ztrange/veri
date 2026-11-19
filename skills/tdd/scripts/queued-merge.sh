#!/bin/sh
# queued-merge.sh — a merge that waits its turn on the merge lock: a shim over veri/queued_merge.py.
#
# Usage:   queued-merge.sh [--skip-suite <model-id> <reason>] <pr-url> <worktree> <branch> <tag-message|->
#          queued-merge.sh --local-green
# Exit:    0 merged and cleaned up. After the merge call, whatever its code, the PR's state is re-read
#          up to VERI_MERGE_SETTLE_READS times (default 10), VERI_MERGE_SETTLE_SLEEP s apart (default 3),
#          the lock held through the window and released once after its last read when no read says
#          merged. 1 red CI, or a merge call that exited 0 whose window's reads answered and never said
#          merged (lock released); a merge call that exited non-zero whose window's reads answered and
#          never said merged exits with its code (a merge call killed after VERI_GH_TIMEOUT s is one
#          that exited 2); a rebase conflict or refused push exits with git's code (lock kept);
#          2 no answer — bad arguments, settle tunables, VERI_GIT_NETWORK_TIMEOUT or VERI_GH_TIMEOUT
#          (empty included; before the lock), a window in which no read answered, a wait-ci.sh exit 2
#          (a PR head that never matched the pushed sha; lock released), a git network call killed
#          after VERI_GIT_NETWORK_TIMEOUT s (default 600; the first fetch: lock released; the leased
#          push: lock kept; the fetch after the merge, not retried, or the tag push: a failed tag
#          step; the branch delete: a failed cleanup step), an error raised before the merge call (lock
#          released, kept while a rebase is stopped), a PR already merged, closed unmerged,
#          unreadable or with its head already on origin/main (refused before any rebase or push), an
#          unresolvable ref, a worktree lacking a commit origin/<branch> has (nothing pushed), or a
#          failed cleanup step after the merge, the tag step included (named on stderr)
#
# During an outage (.tdd/github-outage in the main working tree) a stacked run joins the local stack offline, gated by
# the all-tier command; its amend writes Veri-Suite: passed, not gated or skipped <model-id> <reason>. --skip-suite skips
# that gate, refused (exit 2, nothing done) unless the join is offline and <model-id> names opus or fable. A red gate
# over a Veri-Suite: skipped commit above origin's stack writes .tdd/stack-local-red; joins exit 1 while stack-red.sh
# reads it. --local-green, run in the clone, runs the all-tier command on the local stack's tip: 0 green, the file
# removed; 1 red; 2 outside an outage or no answer; 3 no .tdd/stack-local-red.
#
# On a tdd/<n>-<slug> branch, the cleanup after a confirmed merge also deletes origin's refs/veri/runs/<n> (the run's
# records), bounded by VERI_GIT_NETWORK_TIMEOUT; a ref origin lacks counts as deleted, any other failure (a kill at the
# bound included) is the failed cleanup step "run records delete".
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/queued_merge.py" "$@"
