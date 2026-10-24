#!/bin/sh
# parked-issues.sh — print the parked set from GitHub alone: a shim over veri/parked_issues.py.
#
# Usage: parked-issues.sh
# Exit:  0 printed | 2 any argument, or no answer from gh
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/parked_issues.py" "$@"
