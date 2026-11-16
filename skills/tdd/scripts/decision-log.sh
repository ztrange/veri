#!/bin/sh
# decision-log.sh — record a judge's decision about no issue: one JSON line in .tdd/decisions.jsonl of the main working
# tree. A shim over veri/decision_log.py.
#
# Usage: decision-log.sh record <question> <decision> <rule> <by>
# Exit:  0 recorded | 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/decision_log.py" "$@"
