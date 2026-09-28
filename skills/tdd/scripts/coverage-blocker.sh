#!/usr/bin/env bash
# coverage-blocker.sh — what a refactor-kind run does when Cover answers `COVERED: no` (#499).
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

[[ -n "${1:-}" ]] || { echo "usage: coverage-blocker.sh <refactor-issue-number>" >&2; exit 2; }
n="$1"

url="$(gh issue create \
  --title "Cover the behaviour #$n refactors" \
  --body "Refactor #$n refused: its Cover probe found the code it would move uncovered (\`COVERED: no\`). Find a seam and surround the behaviour with tests, then #$n can be retaken.")"
new="${url##*/}"

body="$(gh issue view "$n" --json body -q .body)"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
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
gh issue edit "$n" --body-file "$tmp" >/dev/null
echo "$url"
