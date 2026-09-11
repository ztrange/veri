#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — rung 2's selection layer. Given a repo's
# issues and open PRs, print the numbers of the issues veri may take RIGHT NOW, one per
# line, lowest first, and exit 0; print nothing and exit 3 when there are none.
#
# Contract under test (issue #41):
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh. That override is the whole reason this suite needs no
#                        network: the fixtures carry the exact shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# 1. The base case, and the one the VERI_GH_JSON override exists to make testable: a single
# open issue, carrying the ready-for-agent opt-in label, naming no blocker, with no open PR
# claiming it. Nothing stands between veri and a run on it, so it is listed on its own line.
#
# The body writes `None.` with a trailing period on purpose — that is how veri's own issues
# write the section (#41's own `## Blocked by` reads `None.`), so what makes an issue
# unblocked is the ABSENCE of a `#<n>` reference under the heading, not the literal string
# `None`. Asserting against the real format keeps the parser honest about veri's own repo.
fx="$work/unblocked"
mkdir -p "$fx"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 41,
    "title": "solvable-issues.sh: list the issues veri may take, in order",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA script that prints the numbers veri may take.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON
printf '[]\n' > "$fx/prs.json"

out="$(VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == "41" ]]; } \
  && ok || no "open ready-for-agent issue with no blockers is listed (exit=$code want 0, stdout='$out' want '41')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
