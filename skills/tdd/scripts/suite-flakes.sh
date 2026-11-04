#!/bin/sh
# suite-flakes.sh — list test files cleared by the alone-rerun in two or more runs: a shim over veri/suite_flakes.py.
#
# Usage:   suite-flakes.sh <run-dir> [<run-dir>...]
# Exit:    0 one or more files listed; 2 no argument, or no answer; 3 nothing to do — no file in two runs
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/suite_flakes.py" "$@"
