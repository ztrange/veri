#!/bin/sh
# run-finished.sh — whether a run is safe to merge: a shim over veri/run_finished.py.
#
# Usage:   run-finished.sh <issue>
# Exit:    0 finished; 1 not finished; 2 no run for the issue, or no answer
exec python3 "$(dirname "$0")/veri/run_finished.py" "$@"
