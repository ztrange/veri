#!/bin/sh
# stop-settle.sh — STOPPING.md steps 1-6 in one call: a shim over veri/stop_settle.py.
#
# Usage:   stop-settle.sh <n> <mode> [--drop]
# Exit:    0 the stop settled; 1 a stop on its `stopped at` line (a dirty tree without --drop); 3 a leaf wait's slice
#          ran out, call it again; 2 bad arguments or a missing .tdd/issue-<n>-preflight, before any call
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stop_settle.py" "$@"
