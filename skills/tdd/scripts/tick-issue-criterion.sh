#!/usr/bin/env bash
# tick-issue-criterion.sh — tick one acceptance-criterion checkbox on a GitHub issue.
#
# Thin I/O wrapper around tick-criterion.sh: reads the issue body via `gh`, flips the
# first unchecked box matching <matcher> (see tick-criterion.sh), and writes the body
# back. The deterministic edit lives in tick-criterion.sh, which is unit-tested.
#
# Usage:
#   tick-issue-criterion.sh <issue-number> <matcher>
#   GH_REPO=owner/name tick-issue-criterion.sh <issue-number> <matcher>
#
# Exit: 0 if a box was ticked and the issue updated, 3 if no unchecked box matched
# (the issue is left untouched). Requires an authenticated `gh`.
set -euo pipefail

USAGE="usage: tick-issue-criterion.sh <issue-number> <matcher>"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

require_args 1 "$@"
n="$1"
matcher="${2:-}"

source "$HERE/lib/github.sh"

body="$(gh_issue_view "$n" body)"

new="$(printf '%s' "$body" | "$HERE/tick-criterion.sh" "$matcher")" || {
  status=$?
  if [[ "$status" -eq 3 ]]; then
    echo "tick-issue-criterion: no unchecked criterion matched '$matcher' on #$n" >&2
  fi
  exit "$status"
}

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
printf '%s' "$new" > "$tmp"
gh_issue_edit "$n" "$tmp" || exit 2
