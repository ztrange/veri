#!/bin/sh
# green-half.sh — a step's Green half on the PASS path (SKILL.md *Green*), in one call: a shim over veri/green_half.py.
#
# Usage:   green-half.sh <n>
# Exit:    0 every call clean; 3 a wait ran out, call it again; 2 bad arguments, a refused step or a missing input;
#          otherwise the stopping call's own code when neither 0 nor 3, else 1
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/green_half.py" "$@"
