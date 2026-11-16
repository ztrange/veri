#!/bin/sh
# stack-branch.sh — the stack branch a repository's CLAUDE.md names: a shim over veri/stack_branch.py.
#
# usage:   stack-branch.sh [repo-root]   (repo-root defaults to the current directory)
# Exit:    0 the branch the one CLAUDE.md line starting `veri: stack branch: <name>` (outside a code fence) names,
#          printed on stdout; 2 the line names no branch, a placeholder, a refs/ or origin/ name, the default branch
#          in any case (as origin states it or
#          origin/HEAD records it), or a name git refuses as a branch name, the default branch cannot be told, or two
#          lines name one (stderr naming the line), or bad arguments; 3 no such line, or no CLAUDE.md: nothing printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_branch.py" "$@"
