#!/bin/sh
# run-affordable.sh — can this run still afford to finish?: a shim over veri/run_affordable.py.
#
# Projects the run's spend so far plus <steps-remaining> steps at the median full step's cost
# against VERI_RUN_BUDGET.
#
# usage: run-affordable.sh <steps-remaining> (a whole number)    (run from the run's worktree)
# Exit:    0 the projection is within the ceiling, nothing printed; 1 it exceeds the ceiling, printing
#          spent, steps remaining, the median and the projection; 2 a bad argument, or no answer;
#          3 nothing to do — no completed full step to take a median from
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/run_affordable.py" "$@"
