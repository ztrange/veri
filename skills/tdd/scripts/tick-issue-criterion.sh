#!/bin/sh
# tick-issue-criterion.sh — tick one acceptance-criterion checkbox on a GitHub issue: a shim over veri/tick_issue_criterion.py.
#
# Thin I/O wrapper around tick-criterion.sh: reads the issue body via `gh`, flips the
# first unchecked box matching <matcher> (see tick-criterion.sh), and writes the body
# back. The deterministic edit lives in tick-criterion.sh, which is unit-tested.
#
# usage: tick-issue-criterion.sh <issue-number> <matcher>
#   GH_REPO=owner/name tick-issue-criterion.sh <issue-number> <matcher>
#
# Exit: 0 if a box was ticked and the issue updated, 3 if no unchecked box matched
# (the issue is left untouched). Requires an authenticated `gh`.
exec python3 "$(dirname "$0")/veri/tick_issue_criterion.py" "$@"
