#!/bin/sh
# pin-recheck.sh — re-run each recorded pin mutation whose file a range touches: a shim over veri/pin_recheck.py.
#
# Usage: pin-recheck.sh <base-sha> [--ledger <file>]   (run from the worktree)
# Exit:  0 every touched pin still goes red; 1 a pin stayed green under its mutation (and not on the base too), or a before-state pin this range disarmed (red on the base, green at HEAD); 2 no answer (a bare `--ledger` with no file, any other argument after the base sha, a base (`git merge-base origin/main HEAD`) that cannot be resolved or replayed, a pin's recorded command cannot run: command not found, or no makefile), or a before-state pin with a green commit whose replay range (its before sha to the issue ledger's tick commit, else the record's green) names no file, or a named test file missing at HEAD that the range did not delete; 3 no record touches the range, or every selected pin is retired
#        Retired: a pin of either record type whose named test file the range deletes is reported `retired:` (record, mutated file, deleted path), is neither replayed nor mutated, and counts toward exit 3 when no other pin is selected
#        Stale: a before-state pin green on its before-state both at HEAD and on the range's base is printed `stale: <record file> <test path>`, and a mutation pin green under its mutation both at HEAD and on the base is printed `stale: <record file> <mutated file>`; neither changes the exit code
#        Receipt: removed at start; on exit 0 or 3 .tdd/pin-recheck-ok holds HEAD's sha, which tick-ledger.sh and clear-refactor-pending.sh require
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pin_recheck.py" "$@"
