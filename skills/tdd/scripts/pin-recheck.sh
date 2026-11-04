#!/bin/sh
# pin-recheck.sh — re-run each recorded pin mutation whose file a range touches: a shim over veri/pin_recheck.py.
#
# Usage: pin-recheck.sh <base-sha>   (run from the worktree)
# Exit:  0 every touched pin still goes red; 1 a pin stayed green under its mutation; 2 no answer, or a before-state pin whose replay range (its before sha to the issue ledger's tick commit, else the record's green) names no file; 3 no record touches the range
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_recheck.py" "$@"
