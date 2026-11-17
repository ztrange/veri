#!/bin/sh
# issue-decisions.sh — print, oldest first, each comment on an issue that counts as a decision: `owner:` for a trusted
# comment that is not one of veri's own and does not start with `Decided:`, `judge:` for a trusted one that does.
# A shim over veri/issue_decisions.py.
#
# Usage: issue-decisions.sh <issue-number>
# Exit:  0 printed | 2 bad arguments, or no answer from gh | 3 no decision comment
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/issue_decisions.py" "$@"
