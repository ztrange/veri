#!/bin/sh
# park-decision.sh — print the owner's answer to a park: the bodies of the trusted comments posted on an issue after
# its newest trusted `### ⏸ Parked` comment, oldest first. A shim over veri/park_decision.py.
#
# Usage: park-decision.sh <issue-number>
# Exit:  0 printed | 2 bad arguments, or no answer from gh | 3 no such comment
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/park_decision.py" "$@"
