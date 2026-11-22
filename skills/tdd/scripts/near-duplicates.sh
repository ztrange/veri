#!/bin/sh
# near-duplicates.sh — the blocks a step's commit added that repeat code elsewhere in the files it touched:
# a shim over veri/near_duplicates.py.
#
# usage: near-duplicates.sh <commit>
#
# Prints one `<file>:<first>-<last> <file>:<first>-<last>` line per pair, the added block first.
# Exit:    0 pairs printed; 2 a missing or unresolvable <commit>; 3 no pair
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/near_duplicates.py" "$@"
