#!/bin/sh
# park-issue.sh — park an issue: label it `parked` and post one `### ⏸ Parked` comment. A shim over veri/park_issue.py.
#
# Usage: park-issue.sh <issue-number> <cause> <unblock> [<pr>]
# Exit:  0 parked | 2 bad arguments, or no answer from gh
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/park_issue.py" "$@"
