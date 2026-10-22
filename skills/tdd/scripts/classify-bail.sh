#!/bin/sh
# classify-bail.sh — classify a bail's <cause> into a category: a shim over veri/classify_bail.py.
#
# Given a cause as $1, print its category on the first stdout line and exit 0.
# An unrecognised cause prints an error to stderr and exits non-zero (2).
#
# usage: classify-bail.sh <cause>
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/classify_bail.py" "$@"
