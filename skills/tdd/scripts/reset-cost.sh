#!/bin/sh
# reset-cost.sh — what each recorded reset of a role cost, and the growth knob it calls for: a shim over veri/reset_cost.py.
#
# Usage:   reset-cost.sh dev [--lane <lane>] | conductor <n>
# Exit:    0 printed; 2 an unreadable transcript or log, or bad arguments; 3 no reset recorded
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reset_cost.py" "$@"
