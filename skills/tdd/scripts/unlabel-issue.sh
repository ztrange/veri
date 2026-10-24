#!/bin/sh
# unlabel-issue.sh — remove the opt-in label from an issue: a shim over veri/unlabel_issue.py.
#
# usage: unlabel-issue.sh <issue-number>
#          Removes VERI_LABEL (default ready-for-agent), so solvable-issues.sh stops listing the issue,
#          and adds taken:<lane>, <lane> the text after VERI_LABEL's last ":", or main.
# Exit:    0 removed, or the label was already absent; 2 a bad argument, or gh gave no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/unlabel_issue.py" "$@"
