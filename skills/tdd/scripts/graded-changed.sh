#!/bin/sh
# graded-changed.sh — name each unit listed in a GRADED file whose signed text differs between <base-sha> and HEAD:
# a file#heading unit when its own text changed, a split whole-file unit when its view changed, an unsplit one when
# its file changed. A shim over veri/graded_changed.py.
#
# usage: graded-changed.sh <base-sha>
# Exit:  0 none changed; 1 some changed; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/graded_changed.py" "$@"
