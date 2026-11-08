#!/bin/sh
# diff-leaf-deviation.sh — record a diff-checked leaf that strays from its one commit: a shim over veri/diff_leaf_deviation.py.
#
# usage: diff-leaf-deviation.sh <leaf> <step-base-sha> <ledger>
# Exit:    0 deviation recorded; 2 a missing argument; 3 no deviation
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/diff_leaf_deviation.py" "$@"
