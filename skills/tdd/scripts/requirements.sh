#!/bin/sh
# requirements.sh — read a REQUIREMENTS.md: a shim over veri/requirements.py.
#
# Usage:   requirements.sh units <file>          each prose unit the file declares, one per line, in file order
#          requirements.sh claims <file> <unit>  the unit's rows as ID<TAB>Requirement, Why omitted
# Exit:    0 printed; 2 bad arguments, or a table that does not parse (stderr names the line)
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/requirements.py" "$@"
