#!/bin/sh
# orchestrate.sh — the loop above the conductor: a shim over veri/orchestrate.py.
#
# Asks solvable-issues.sh which issues veri may take, launches one conductor for the first of them
# through run-conductor.sh, and asks again, until nothing is left to take. Every assistant event a
# conductor streams prints `context <issue> <tokens>`; a conductor over VERI_CONDUCTOR_CTX_BUDGET
# (tokens, default 120000) is SIGTERMed at its next step boundary; a parked issue prints `parked <n>`.
#
# Usage:   orchestrate.sh
# Exit:    0 solvable-issues.sh answered 3, or every issue it names is parked; 2 solvable-issues.sh
#          exited anything but 0 or 3, VERI_CONDUCTOR_CTX_BUDGET is not a whole number, or
#          run-conductor.sh cannot be started
exec python3 "$(dirname "$0")/veri/orchestrate.py" "$@"
