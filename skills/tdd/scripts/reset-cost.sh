#!/bin/sh
# reset-cost.sh — what each recorded restart of a run's conductor cost, and the growth knob it calls for: a shim over veri/reset_cost.py.
#
# Usage:   reset-cost.sh conductor <n>
# Exit:    0 printed; 2 an unreadable conductor log, or bad arguments; 3 no restart recorded
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reset_cost.py" "$@"
