#!/bin/sh
# rebase-onto-default.sh — rebase the run's branch onto origin/<default>, from the worktree it runs in: a shim over veri/rebase_onto_default.py.
#
# usage: rebase-onto-default.sh [--graded-only] | --resolved <onto-sha>
#   --graded-only  a conflict confined to GRADED files is resolved by union (each side's re-signed units kept) and the
#                  rebase continues; any other conflict still exits 1 as below
#   --resolved     after a develop-rebase leaf resolved a conflicted rebase onto <onto-sha>: fetch and rebase nothing,
#                  re-record the run's branch base as <onto-sha>, exit 0, stdout the base it replaced (none if none);
#                  exit 2, the record untouched, when the sha is not hex, HEAD lacks it, or the record cannot be written
# Exit:    3 the branch already contains origin/<default>, HEAD and tree untouched; 0 rebased, stdout the
#          pre-rebase sha then the onto sha; 1 a conflict, aborted, stdout the conflicting files one per line;
#          2 git refused the rebase, no default branch resolved, origin not fetched, or origin/<default> stale
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/rebase_onto_default.py" "$@"
