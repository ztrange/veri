#!/bin/sh
# stop-reason.sh — why a run ended: a shim over veri/stop_reason.py.
#
# usage: stop-reason.sh <issue>
# Exit:  0 a reason printed | 2 bad arguments, or an issue with no run under .tdd/wt
exec python3 "$(dirname "$0")/veri/stop_reason.py" "$@"
