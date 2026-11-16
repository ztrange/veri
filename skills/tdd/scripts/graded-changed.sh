#!/bin/sh
# graded-changed.sh — name each unit listed in a GRADED file that differs between <base-sha> and HEAD: a whole-file
# unit when its file changed, a file#heading unit when that section's text changed. A shim over veri/graded_changed.py.
#
# usage: graded-changed.sh <base-sha>
# Exit:  0 none changed; 1 some changed; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/graded_changed.py" "$@"
