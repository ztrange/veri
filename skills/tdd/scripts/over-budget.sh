#!/bin/sh
# over-budget.sh — turn one recorded test-command run into a yes or no: a shim over veri/over_budget.py.
#
# usage: over-budget.sh <tier> <seconds> <usual>
# Exit:  0 over budget, one ⏱ line on stdout; 1 not over budget, nothing on stdout;
#        2 a missing argument, or a tunable time-budget.sh refuses
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/over_budget.py" "$@"
