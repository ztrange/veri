#!/usr/bin/env bash
# invisible-work.sh — report work that is not visible, naming the invariant each finding
# breaks (issue #197). Reads, never writes: it deletes nothing, pushes nothing, opens nothing.
#
# Invariant 2 (#195): a branch is never created without a PR. A branch on `origin` for which
# no PR was ever opened — not open, not closed, not merged — is reported with its tip, its
# commit count ahead of the default branch, and, when its name has the `tdd/<n>-<slug>`
# shape, the number and state of issue <n>: that is what tells a live run from an abandoned
# one.
#
# The repository's issues are read as the JSON `gh` emits:
#   gh issue list --state all --limit 10000 --json number,state
# VERI_GH_JSON overrides it, naming a directory holding `issues.json` in that shape — the same override solvable-issues.sh establishes, so this runs with no
# network in its tests. The JSON is read with python3, as there.
#
# Usage:   invisible-work.sh
#          VERI_GH_JSON=<dir> invisible-work.sh
set -euo pipefail

gh_json() {  # gh_json <fixture-file> <gh args…> -> that document on stdout
  local fixture="$1"; shift
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/$fixture"
  else
    gh "$@"
  fi
}

issues_json="$(gh_json issues.json issue list --state all --limit 10000 --json number,state)"

# The default branch as `origin` names it: `refs/remotes/origin/HEAD` -> `origin/main`.
default="$(git symbolic-ref --short refs/remotes/origin/HEAD)"
default="${default#origin/}"

# One line per branch on origin: `<name> <tip> <commits ahead of the default branch>`.
branches=""
while read -r ref tip; do
  name="${ref#refs/remotes/origin/}"
  ahead="$(git rev-list --count "origin/$default..$ref")"
  branches+="$name $tip $ahead"$'\n'
done < <(git for-each-ref --format='%(refname) %(objectname)' refs/remotes/origin/)

exec python3 -c '
import json, re, sys

issues = {i["number"]: i["state"] for i in json.loads(sys.argv[1])}

for row in sys.argv[2].splitlines():
    name, tip, ahead = row.split()
    finding = f"invariant 2 (no PR): {name} tip {tip} {ahead} commits ahead"
    m = re.match(r"tdd/(\d+)-", name)
    if m:
        n = int(m.group(1))
        state = issues[n]
        finding += f", issue #{n} {state}"
    print(finding)
' "$issues_json" "$branches"
