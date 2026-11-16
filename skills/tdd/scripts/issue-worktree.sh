#!/bin/sh
# issue-worktree.sh — the linked git worktree an issue branch lives in: a shim over veri/issue_worktree.py.
#
# usage: issue-worktree.sh [--take-over] <n> <slug>
#        issue-worktree.sh --remove <n>
# --take-over fetches origin's branch for the issue and cuts the worktree on a local branch from it, where without it the run is refused as another run's.
# --remove also deletes the run's pinned-scripts snapshot directory, but only one named veri-snapshot-* whose .veri-snapshot marker names this worktree; any other is left in place with a stderr line.
# Exit:    0 the worktree's absolute path printed on stdout, or the worktree removed; 2 a bad argument list, a refusal, a call from the skill's own scripts directory, or a failing git
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/issue_worktree.py" "$@"
