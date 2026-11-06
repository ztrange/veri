#!/bin/sh
# pin-recheck.sh — re-run each recorded pin mutation whose file a range touches: a shim over veri/pin_recheck.py.
#
# Usage: pin-recheck.sh <base-sha>   (run from the worktree)
# Exit:  0 every touched pin still goes red; 1 a pin stayed green under its mutation; 2 no answer (a pin's recorded command cannot run: command not found, or no makefile), or a before-state pin with a green commit whose replay range (its before sha to the issue ledger's tick commit, else the record's green) names no file, or a named test file missing at HEAD that the range did not delete; 3 no record touches the range, or every selected pin is retired
#        Retired: a pin whose named test file the range deletes is reported `retired:` (record, mutated file, deleted path), is neither replayed nor mutated, and counts toward exit 3 when no other pin is selected
#        Receipt: removed at start; on exit 0 or 3 .tdd/pin-recheck-ok holds HEAD's sha, which tick-ledger.sh and clear-refactor-pending.sh require
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_recheck.py" "$@"
