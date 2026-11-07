#!/bin/sh
# report.sh — render the /vreport figures per open PRD: a shim over veri/prd_report.py.
#
# Usage:   report.sh --report
# Exit:    0 printed; 2 bad arguments, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/prd_report.py" "$@"
