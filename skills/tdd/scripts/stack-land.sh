#!/bin/sh
# stack-land.sh — land the stack's tested cut on the default branch: a shim over veri/stack_land.py.
#
# usage:   stack-land.sh [--now]   (run in the target repository's clone)
# Exit:    0 landed; 1 a clean refusal; 2 no answer, or any argument other than --now; 3 nothing to land
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_land.py" "$@"
