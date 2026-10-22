#!/bin/sh
# rebase-onto-default.sh — rebase the run's branch onto origin/<default>, from the worktree it runs in: a shim over veri/rebase_onto_default.py.
#
# usage: rebase-onto-default.sh
# Exit:    3 the branch already contains origin/<default>, HEAD and tree untouched; 0 rebased, stdout the
#          pre-rebase sha then the onto sha; 1 a conflict, aborted, stdout the conflicting files one per line;
#          2 git refused the rebase, no default branch resolved, origin not fetched, or origin/<default> stale
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/rebase_onto_default.py" "$@"
