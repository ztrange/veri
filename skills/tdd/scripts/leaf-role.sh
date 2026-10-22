#!/bin/sh
# leaf-role.sh — turn a leaf's NAME into the role its events are logged under: a shim over veri/leaf_role.py.
#
# usage: leaf-role.sh <leaf-name>
#
# Prints `VERI_ACTOR=<actor> VERI_PHASE=<phase> VERI_ATTEMPT=<n>` on one line.
# Exit:    0 the role line printed; 2 no name, an unknown leading word, or no phase — a diagnostic on stderr, nothing on stdout
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/leaf_role.py" "$@"
