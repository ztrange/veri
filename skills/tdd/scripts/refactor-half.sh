#!/bin/sh
# refactor-half.sh — a step's first refactor pass (SKILL.md *Refactor loop*), in one call: a shim over veri/refactor_half.py.
#
# Usage:   refactor-half.sh <n>
# Exit:    0 every call clean; 3 a wait ran out, call it again; 2 bad arguments, no refactor-pending step or a missing input;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refactor_half.py" "$@"
