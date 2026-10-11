#!/bin/sh
# replaces-case-survivors.sh — name the cases a ⟦replaces-case⟧ step replaces that its suite still holds: a shim over veri/replaces_case_survivors.py.
#
# usage: replaces-case-survivors.sh <step text>
#
# Exit: 0 every named case is gone; 1 one or more remain, each printed; 2 bad arguments or an unreadable suite.
exec python3 "$(dirname "$0")/veri/replaces_case_survivors.py" "$@"
