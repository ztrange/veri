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
# Exit:    0 one or more numbers printed; 3 nothing to do — no issue is takeable
set -euo pipefail

exec python3 -c '
import json, re, sys, pathlib

src = pathlib.Path(sys.argv[1])
issues = json.loads((src / "issues.json").read_text())
prs = json.loads((src / "prs.json").read_text())

# Openness is the whole of what a state is read for, and it is read the same way on both
# kinds of record: `gh` writes an issue state as OPEN/CLOSED and a PR state as
# OPEN/CLOSED/MERGED, and only the first of either is open.
def is_open(record):
    return record.get("state", "").upper() == "OPEN"

# An issue must be open to be taken and a blocker must not be, so the open issues are
# normalised once, here, into a set of numbers.
open_issues = {i["number"] for i in issues if is_open(i)}

# The issues an open PR has already claimed, by the `Closes #<n>` GitHub reads to link the
# two. Only open PRs claim anything: once one is merged or closed the issue is either done
# or free again.
claimed = {
    int(n)
    for pr in prs
    if is_open(pr)
    for n in re.findall(r"\bCloses #(\d+)", pr.get("body") or "")
}

def blockers(body):
    """The issue numbers named under the `## Blocked by` heading, up to the next heading.
    A section reading `None.` names none, and so does a body with no such section."""
    section = re.search(r"^## Blocked by$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return [int(n) for n in re.findall(r"#(\d+)", section.group(1))] if section else []

def solvable(issue):
    """The four conditions the spec names, all of which must hold at once. They are named
    here rather than run as early returns so the function reads as the definition it is."""
    number = issue["number"]
    still_open = number in open_issues
    opted_in = any(l.get("name") == "ready-for-agent" for l in issue.get("labels", []))
    unclaimed = number not in claimed
    unblocked = all(n not in open_issues for n in blockers(issue.get("body", "")))
    return still_open and opted_in and unclaimed and unblocked

numbers = sorted(i["number"] for i in issues if solvable(i))
for number in numbers:
    print(number)

# Nothing takeable is not an error: it is veri exit code 3, "nothing to do". The caller
# learns it from the code rather than from having to notice that stdout was empty.
if not numbers:
    sys.exit(3)
' "$VERI_GH_JSON"
