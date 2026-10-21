#!/bin/sh
# tick-issue-criterion.sh — tick one acceptance-criterion checkbox on a GitHub issue: a shim over veri/tick_issue_criterion.py.
#
# Reads the issue body via `gh`, calls ledger.ledger_tick directly to flip the first
# unchecked box matching <matcher> under `## Acceptance criteria` only, and writes the
# body back.
#
# usage: tick-issue-criterion.sh <issue-number> <matcher>
#   GH_REPO=owner/name tick-issue-criterion.sh <issue-number> <matcher>
#
# Exit: 0 if a box was ticked and the issue updated, 3 if no unchecked box under
# `## Acceptance criteria` matched (the issue is left untouched). Requires an authenticated `gh`.
exec python3 "$(dirname "$0")/veri/tick_issue_criterion.py" "$@"
