#!/bin/sh
# refactor-overflow.sh — file the structural candidates a closing pass could not reach: a shim over veri/refactor_overflow.py.
#
# usage: refactor-overflow.sh <n> <owed-file> <reached> [<skipped-file>]
#
# Prints the new issue's URL.
#
# Exit: 0 filed; 2 a missing or non-numeric argument, a missing <skipped-file>, or gh failing to file; 3 nothing left unreached, nothing filed.
exec python3 "$(dirname "$0")/veri/refactor_overflow.py" "$@"
