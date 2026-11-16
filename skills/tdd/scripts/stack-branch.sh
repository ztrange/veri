#!/bin/sh
# stack-branch.sh — the stack branch a repository's CLAUDE.md names: a shim over veri/stack_branch.py.
#
# usage:   stack-branch.sh [repo-root]   (repo-root defaults to the current directory)
# Exit:    0 the branch a `veri: stack branch: <name>` line of CLAUDE.md names, printed on stdout; 2 the line names no
#          branch, the default branch, or a name `git check-ref-format --branch` refuses (stderr naming the line), or bad
#          arguments; 3 no such line, or no CLAUDE.md: nothing printed, the repository stacks nothing
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_branch.py" "$@"
