#!/bin/sh
# time-budget.sh — the two tunables that decide whether a recorded test-command run is worth a word
# in the narration: a shim over veri/time_budget.py.
#
# VERI_UNIT_BUDGET (default 10) is seconds, the unit tier's ceiling; VERI_TIME_WARN_RATIO (default
# 1.5) is a multiplier on a tier's usual, for every tier. Both are validated before either is printed.
#
# usage: time-budget.sh          # prints the resolved seconds, then the resolved ratio
# Exit:    0 the seconds then the ratio on stdout; 2 a value that is not a number, nothing on stdout,
#          a diagnostic naming the variable at fault on stderr
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/time_budget.py" "$@"
