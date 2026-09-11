#!/usr/bin/env bash
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line, lowest first.
#
# An issue is takeable when it is open and carries the `ready-for-agent` label: the
# human's explicit opt-in. Nothing is taken because it merely exists.
#
# The repository's issues are read as the JSON `gh issue list` emits:
#   gh issue list --json number,title,labels,body,state
# but the shell-out itself is not done here yet — VERI_GH_JSON names a directory holding
# an `issues.json` fixture with that exact shape, which is what makes this testable with
# no network.
#
# jq is NOT a dependency of any script in this suite (`grep -n jq scripts/*.sh` finds
# nothing), so the JSON is read with python3's json module — the same interpreter
# extract-result.sh and the docs generator already require.
#
# Usage:   VERI_GH_JSON=<dir> solvable-issues.sh
set -euo pipefail

exec python3 -c '
import json, sys, pathlib

src = pathlib.Path(sys.argv[1])
issues = json.loads((src / "issues.json").read_text())

def takeable(issue):
    if issue.get("state", "").upper() != "OPEN":
        return False
    return any(l.get("name") == "ready-for-agent" for l in issue.get("labels", []))

for number in sorted(i["number"] for i in issues if takeable(i)):
    print(number)
' "$VERI_GH_JSON"
