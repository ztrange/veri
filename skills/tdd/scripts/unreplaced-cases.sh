#!/bin/sh
# unreplaced-cases.sh — name the bash cases a ⟦replaces-case⟧ step lists that have no pytest replacement: a shim over veri/unreplaced_cases.py.
#
# usage: unreplaced-cases.sh
# exit:  2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/unreplaced_cases.py" "$@"
