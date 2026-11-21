#!/bin/sh
# reject-breakdown.sh — the verifier REJECT verdicts of metrics reports, per week: a shim over veri/reject_breakdown.py.
#
# Usage:   reject-breakdown.sh < <dated reports>
#          stdin: one `<YYYY-MM-DD> <report path>` line per report
# Exit:    0 printed; 2 a line not `<YYYY-MM-DD> <path>`, or a report unreadable or with no `#### By phase` table, named by its line; 3 no report named
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reject_breakdown.py" "$@"
