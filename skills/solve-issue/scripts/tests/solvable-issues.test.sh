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

# A fixture directory for one case, printed so the caller can capture it. Both halves of
# the override's contract are seeded here: the directory itself, and the `prs.json` every
# case so far shares — no case yet involves an open PR — which leaves each case below
# writing only the one file it actually varies, its `issues.json`.
fixture() {  # fixture <name> -> path
  local dir="$work/$1"
  mkdir -p "$dir"
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

# 1. The base case, and the one the VERI_GH_JSON override exists to make testable: a single
# open issue, carrying the ready-for-agent opt-in label, naming no blocker, with no open PR
# claiming it. Nothing stands between veri and a run on it, so it is listed on its own line.
#
# The body writes `None.` with a trailing period on purpose — that is how veri's own issues
# write the section (#41's own `## Blocked by` reads `None.`), so what makes an issue
# unblocked is the ABSENCE of a `#<n>` reference under the heading, not the literal string
# `None`. Asserting against the real format keeps the parser honest about veri's own repo.
fx="$(fixture unblocked)"
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

# 2. A blocker gates the issue, and only while it is open. Both halves are the same
# criterion observed twice, so they are one case: the same two issues are fed in twice,
# changing nothing but #49's state. While #49 is OPEN, #50 names it under `## Blocked by`
# and must not be listed — #49 itself still is, since it carries the label and names no
# blocker of its own. Close #49 and #50 becomes takeable; #49 drops out because a closed
# issue is never solvable, so the same fixture pair yields "49" then "50".
fx="$(fixture blocked)"
issues() {  # issues <state-of-49>
  cat <<JSON
[
  {
    "number": 50,
    "title": "the /solve-issues loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA loop over solvable-issues.sh.\n\n## Blocked by\n\n#49\n"
  },
  {
    "number": 49,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "$1",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
}

issues OPEN > "$fx/issues.json"
while_open="$(VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && open_code=0 || open_code=$?

issues CLOSED > "$fx/issues.json"
once_closed="$(VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && closed_code=0 || closed_code=$?

{ [[ "$open_code" == 0 && "$while_open" == "49" ]] \
  && [[ "$closed_code" == 0 && "$once_closed" == "50" ]]; } \
  && ok || no "issue blocked by an open issue is withheld until that issue closes (blocker open: exit=$open_code want 0, stdout='$while_open' want '49'; blocker closed: exit=$closed_code want 0, stdout='$once_closed' want '50')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
