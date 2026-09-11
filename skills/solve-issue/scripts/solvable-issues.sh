#!/usr/bin/env bash
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line, lowest first.
#
# An issue is solvable when it is open, carries the `ready-for-agent` label (the human's
# explicit opt-in — nothing is taken because it merely exists), every issue it names
# under its `## Blocked by` heading is closed, and no open pull request already says
# `Closes #<n>` for it — such a PR means a run is in flight on that issue, or one bailed
# and left the branch behind, and either way the issue is not veri's to take. A body whose
# `## Blocked by` section reads `None.` names no issue at all, so the test for "unblocked"
# is the absence of a `#<n>` reference under that heading rather than the literal word.
#
# The repository's issues and pull requests are read as the JSON `gh` emits:
#   gh issue list --json number,title,labels,body,state
#   gh pr list    --json body,state
# but the shell-out itself is not done here yet — VERI_GH_JSON names a directory holding
# `issues.json` and `prs.json` fixtures with those exact shapes, which is what makes this
# testable with no network.
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
prs = json.loads((src / "prs.json").read_text())

# Openness is the whole of what a state is read for — an issue must be open to be taken,
# and a blocker must not be — so it is normalised once, here, into a set of numbers.
open_issues = {i["number"] for i in issues if i.get("state", "").upper() == "OPEN"}

# The issues an open PR has already claimed, by the `Closes #<n>` GitHub reads to link the
# two. Only open PRs claim anything: once one is merged or closed the issue is either done
# or free again.
claimed = {
    int(n)
    for pr in prs
    if pr.get("state", "").upper() == "OPEN"
    for n in re.findall(r"\bCloses #(\d+)", pr.get("body") or "")
}

def blockers(body):
    """The issue numbers named under the `## Blocked by` heading, up to the next heading.
    A section reading `None.` names none, and so does a body with no such section."""
    section = re.search(r"^## Blocked by$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return [int(n) for n in re.findall(r"#(\d+)", section.group(1))] if section else []

def solvable(issue):
    if issue["number"] not in open_issues:
        return False
    if not any(l.get("name") == "ready-for-agent" for l in issue.get("labels", [])):
        return False
    if issue["number"] in claimed:
        return False
    return all(n not in open_issues for n in blockers(issue.get("body", "")))

for number in sorted(i["number"] for i in issues if solvable(i)):
    print(number)
' "$VERI_GH_JSON"
