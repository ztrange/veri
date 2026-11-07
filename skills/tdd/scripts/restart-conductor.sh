#!/bin/sh
# restart-conductor.sh — restart run <n>'s conductor once its growth passes the knob: a shim over veri/restart_conductor.py.
#
# Usage:   restart-conductor.sh <n>
# Exit:    0 the run ended; 2 bad arguments; 3 no live conductor
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/restart_conductor.py" "$@"
