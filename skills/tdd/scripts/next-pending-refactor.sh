#!/bin/sh
# next-pending-refactor.sh — print the first step that is green but not yet tidied: a shim over veri/next_pending_refactor.py.
#
# usage: next-pending-refactor.sh   (the ledger on stdin)
# Exit:    0 the first refactor-pending step's text printed, its mark stripped; 3 no step carries the mark
exec python3 "$(dirname "$0")/veri/next_pending_refactor.py" "$@"
