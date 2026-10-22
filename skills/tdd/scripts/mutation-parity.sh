#!/bin/sh
# mutation-parity.sh — apply each pairs-table row's mutation and report whether the row's
# kept case catches it: a shim over veri/mutation_parity.py.
#
# A row is tab-separated: <suite> <old case> redundant <kept case> <mutation patch>.
#
# usage: mutation-parity.sh <pairs-table>
#
# stdout:  one row per pairs-table row: <old case> <kept case> <mutation> <result>
# exit:    0 every row proven · 1 a row unproven · 2 no <pairs-table>
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/mutation_parity.py" "$@"
