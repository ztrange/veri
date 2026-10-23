#!/bin/sh
# next-unchecked.sh — print the first open step a leaf is handed, for the cycle loop: a shim over veri/next_unchecked.py.
#
# usage: next-unchecked.sh   (the ledger on stdin)
# Exit:    0 the first open ordinary or diff-checked step's text printed; 3 none — every step done, or no step
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/next_unchecked.py" "$@"
