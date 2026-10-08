#!/bin/sh
# issue-worktree.sh — the linked git worktree an issue branch lives in: a shim over veri/issue_worktree.py.
#
# usage: issue-worktree.sh <n> <slug> | --remove <n>
# Exit:    0 the worktree's absolute path printed on stdout, or the worktree removed; 2 a bad argument list, a refusal, a call from the skill's own scripts directory, or a failing git
exec python3 "$(dirname "$0")/veri/issue_worktree.py" "$@"
