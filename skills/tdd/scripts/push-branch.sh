#!/bin/sh
# push-branch.sh — copy the run's branch to the remote, from the worktree it runs in: a shim over veri/push_branch.py.
#
# usage: push-branch.sh [--force-with-lease=<branch>:<sha>]
#          --force-with-lease replaces the remote copy only if it is still at <sha>. Never a bare force.
# Exit:    0 pushed, or origin unreachable after the retries (recorded push-failed); 1 a non-fast-forward
#          or stale-lease rejection (recorded push-rejected); 2 a bad argument, a bad tunable or a failed
#          event write
#
# After a push that lands on a tdd/<n>-<slug> branch it also replaces origin's refs/veri/runs/<n> with the run's
# records (the issue's journal lines, skill pin and timeout pin) and updates the issue's pointer comment
# (pointer-comment.sh); a failure of either is one stderr line and never changes the exit code.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/push_branch.py" "$@"
