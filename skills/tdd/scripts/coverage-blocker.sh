#!/usr/bin/env bash
# coverage-blocker.sh — what a refactor-kind run does when Cover answers `COVERED: no`.
#
# Files an unlabelled coverage issue for the refactor issue — no opt-in label, so the queue
# never takes it itself — and names that new issue under the refactor issue's `## Blocked by`
# heading, in place of a `None` line or after the blockers already listed, so
# solvable-issues.sh stops listing the refactor issue until the coverage exists and it cannot
# be retaken only to refuse again.
#
# Usage:
#   coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Prints the new issue's URL. Exit: 0 on success, 2 on bad arguments. Requires an
# authenticated `gh`, which reads GH_REPO from the environment itself.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

USAGE="usage: coverage-blocker.sh <refactor-issue-number>"
require_args 1 "$@"
n="$1"

source "$HERE/lib/github.sh"

title="Cover the behaviour #$n refactors"
text="Refactor #$n refused: its Cover probe found the code it would move uncovered (\`COVERED: no\`). Find a seam and surround the behaviour with tests, then #$n can be retaken."
url="$(gh api "repos/{owner}/{repo}/issues" -f "title=$title" -f "body=$text" -q .html_url)" || exit 2
new="${url##*/}"

body="$(gh_issue_view "$n" body)"

tmp="$(mktemp)"
at_exit 'rm -f "$tmp"'
printf '%s\n' "$body" | awk -v blocker="- #$new" '
  /^## / { in_blocked = ($0 ~ /^## Blocked by/) }
  in_blocked && /^None/ { line[++n] = blocker; next }
  in_blocked && /^- #/ { last = n + 1 }
  { line[++n] = $0 }
  END {
    for (i = 1; i <= n; i++) {
      print line[i]
      if (i == last) print blocker
    }
  }
' > "$tmp"
gh_issue_edit "$n" "$tmp" || exit 2
echo "$url"
