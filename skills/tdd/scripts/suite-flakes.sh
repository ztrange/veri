#!/bin/sh
# suite-flakes.sh — list test targets (a file or a pytest node id) cleared by the alone-rerun in two or more runs: a shim over veri/suite_flakes.py.
#
# Usage:   suite-flakes.sh <run-dir> [<run-dir>...]
# Exit:    0 one or more targets listed; 2 no argument, or no answer; 3 nothing to do — no target in two runs
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/suite_flakes.py" "$@"
