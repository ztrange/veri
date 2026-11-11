#!/bin/sh
# release-issue.sh — put a parked, bailed or preflight-refused issue back on the queue. A shim over veri/release_issue.py.
#
# Adds the opt-in label (VERI_LABEL), removes this lane's `taken:<lane>` claim, then removes
# `parked` and `bailed` last, so a write gh does not answer leaves the issue findable and a
# re-run finishes the job. Removing `parked` by hand left the issue claimed and unlabelled:
# solvable-issues.sh skips every `taken:*` issue, so nothing ever took it back.
#
# Usage: release-issue.sh <issue-number>
# Exit:  0 released | 2 bad arguments, another lane's claim, or no answer from gh | 3 neither parked, bailed nor preflight-refused
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/release_issue.py" "$@"
