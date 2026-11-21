#!/bin/sh
# reject-breakdown.sh — the verifier REJECT verdicts of metrics reports, per week: a shim over veri/reject_breakdown.py.
#
# Usage:   reject-breakdown.sh < <dated reports>   one `<YYYY-MM-DD> <report path>` line per report
# Exit:    0 printed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reject_breakdown.py" "$@"
