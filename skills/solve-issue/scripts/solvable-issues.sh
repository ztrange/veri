#!/usr/bin/env bash
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line, lowest first.
#
# An issue is solvable when it is open, carries the `ready-for-agent` label (the human's
# explicit opt-in — nothing is taken because it merely exists), and every issue it names
# under its `## Blocked by` heading is closed. A body whose section reads `None.` names no
# issue at all, so the test for "unblocked" is the absence of a `#<n>` reference under that
# heading rather than the literal word.
#
# The repository's issues are read as the JSON `gh issue list` emits:
#   gh issue list --json number,title,labels,body,state
# but the shell-out itself is not done here yet — VERI_GH_JSON names a directory holding
# an `issues.json` fixture with that exact shape, which is what makes this testable with
# no network.
#
# jq is NOT a dependency of any script in this suite — `grep -n jq scripts/*.sh` returns
# this note and nothing else — so the JSON is read with python3's json module, the same
# interpreter extract-result.sh and the docs generator already require.
#
# Usage:   VERI_GH_JSON=<dir> solvable-issues.sh
set -euo pipefail

exec python3 -c '
import json, re, sys, pathlib

src = pathlib.Path(sys.argv[1])
issues = json.loads((src / "issues.json").read_text())

state = {i["number"]: i.get("state", "").upper() for i in issues}

def blockers(body):
    """The issue numbers named under the `## Blocked by` heading, up to the next heading.
    A section reading `None.` names none, and so does a body with no such section."""
    section = re.search(r"^## Blocked by$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return [int(n) for n in re.findall(r"#(\d+)", section.group(1))] if section else []

def solvable(issue):
    if issue.get("state", "").upper() != "OPEN":
        return False
    if not any(l.get("name") == "ready-for-agent" for l in issue.get("labels", [])):
        return False
    return all(state.get(n) != "OPEN" for n in blockers(issue.get("body", "")))

for number in sorted(i["number"] for i in issues if solvable(i)):
    print(number)
' "$VERI_GH_JSON"
