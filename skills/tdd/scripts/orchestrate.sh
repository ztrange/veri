#!/bin/sh
# orchestrate.sh — the loop above the conductor: a shim over veri/orchestrate.py.
#
# Asks solvable-issues.sh which issues veri may take, launches one conductor for the first of them
# through run-conductor.sh, and asks again, until nothing is left to take. Every assistant event a
# conductor streams prints `context <issue> <tokens>`; a conductor over VERI_CONDUCTOR_CTX_BUDGET
# (tokens, default 120000) is SIGTERMed at its next step boundary; a parked issue prints `parked <n>`.
# VERI_CONDUCTOR_STOP_TIMEOUT (seconds, default 10, a finite number above 0 and at most 100000000)
# is how long a stopped conductor gets before it is killed.
#
# Usage:   orchestrate.sh
# Exit:    0 solvable-issues.sh answered 3, or every issue it names is parked; 2 solvable-issues.sh
#          exited anything but 0 or 3, VERI_CONDUCTOR_CTX_BUDGET is not a whole number,
#          VERI_CONDUCTOR_STOP_TIMEOUT is outside its bounds, run-conductor.sh cannot be started, or its stdout is closed or its reader has exited
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/orchestrate.py" "$@"
