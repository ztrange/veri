#!/bin/sh
# rebase-onto-default.sh — rebase the run's branch onto origin/<default>, from the worktree it runs in: a shim over veri/rebase_onto_default.py.
#
# usage: rebase-onto-default.sh [--graded-only]
#   --graded-only  a conflict confined to GRADED files is resolved by union (each side's re-signed units kept) and the
#                  rebase continues; any other conflict still exits 1 as below
# Exit:    3 the branch already contains origin/<default>, HEAD and tree untouched; 0 rebased, stdout the
#          pre-rebase sha then the onto sha; 1 a conflict, aborted, stdout the conflicting files one per line;
#          2 git refused the rebase, no default branch resolved, origin not fetched, or origin/<default> stale
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/rebase_onto_default.py" "$@"
