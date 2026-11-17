#!/bin/sh
# red-half.sh — a step's Red half on the FAILS path (SKILL.md *Red*), in one call: a shim over veri/red_half.py.
#
# Usage:   red-half.sh <n>
# Exit:    0 every call clean; 3 a wait ran out, call it again; 2 bad arguments, a refused step or a missing input;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/red_half.py" "$@"
