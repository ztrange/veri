#!/bin/sh
# stack-carry.sh — carry the stack onto the new default branch after a slice landed: a shim over veri/stack_carry.py.
#
# usage:   stack-carry.sh <old-cut>   (run in the target repository's clone; <old-cut> is the stack commit the landed
#          slice ended at, as it was on origin/<stack> before the landing)
# Exit:    0 carried; 1 a clean refusal (a rebase conflict, a tree the merge-tree check disagrees with, origin moved);
#          2 no answer, or any argument list but one commit; 3 nothing to carry (<old-cut> is the stack's tip)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_carry.py" "$@"
