#!/bin/sh
# preflight-refused.sh — record a preflight refusal in the run's event log: a shim over veri/preflight_refused.py.
#
# Usage:   preflight-refused.sh <issue-number> <check>
# Exit:    0 the event was written; 2 a missing or empty argument, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/preflight_refused.py" "$@"
