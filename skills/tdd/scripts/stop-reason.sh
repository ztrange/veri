#!/bin/sh
# stop-reason.sh — why a run ended: a shim over veri/stop_reason.py.
#
# usage: stop-reason.sh <issue>
# Exit:  0 a reason printed | 2 bad arguments, an issue with no run under .tdd/wt, a missing events log, or a run whose conductor-<n>.log has no result record
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stop_reason.py" "$@"
