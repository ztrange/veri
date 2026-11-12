#!/bin/sh
# park-issue.sh — park an issue: label it `parked` and post one `### ⏸ Parked` comment. A shim over veri/park_issue.py.
#
# The `bailed` label comes off with the label write: `parked` replaces it.
# --blocked-by <m> also lists #m under the issue's `## Blocked by` (once), so selection waits on
# #m and #m inherits the parked issue's band; pass it when the unblock is another issue landing.
#
# Usage: park-issue.sh <issue-number> <cause> <unblock> [<pr-number|PR-URL>] [--blocked-by <n>[,<n>…]]
# Exit:  0 parked | 2 bad arguments, or no answer from gh
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/park_issue.py" "$@"
