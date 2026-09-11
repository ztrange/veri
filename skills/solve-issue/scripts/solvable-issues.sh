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
# VERI_GH_JSON overrides both calls at once: it names a directory holding `issues.json` and
# `prs.json` fixtures with those exact shapes, which is what makes this testable with no
# network. Selection itself never learns which of the two it got — the documents are read
# here and handed on as text.
#
# jq is NOT a dependency of any script in this suite — `grep -n jq scripts/*.sh` returns
# this note and nothing else — so the JSON is read with python3's json module, the same
# interpreter extract-result.sh and the docs generator already require.
#
# Usage:   solvable-issues.sh [--repo owner/name]
#          VERI_GH_JSON=<dir> solvable-issues.sh
# Exit:    0 one or more numbers printed; 3 nothing to do — no issue is takeable
set -euo pipefail

# `--repo owner/name` is forwarded to gh verbatim and nothing is invented in its absence:
# a wrong repository is silently wrong, so gh's own default (the repo of the working
# directory) is the only sane fallback. The `[@]+` expansion is what keeps an empty array
# from becoming an empty argument under `set -u`.
repo_args=()
if [[ "${1:-}" == "--repo" ]]; then
  repo_args=(--repo "${2:?usage: solvable-issues.sh [--repo owner/name]}")
fi

# Both documents are asked of gh the same way — the same optional `--repo` scoping, the same
# JSON on stdout — so the scoping is applied in one place rather than spelled out at each
# call site, which is also the only place that awkward expansion has to be understood.
gh_json() {  # gh_json issue list --json number,… -> that document on stdout
  gh "$@" "${repo_args[@]+"${repo_args[@]}"}"
}

if [[ -n "${VERI_GH_JSON:-}" ]]; then
  issues_json="$(cat "$VERI_GH_JSON/issues.json")"
  prs_json="$(cat "$VERI_GH_JSON/prs.json")"
else
  issues_json="$(gh_json issue list --json number,title,labels,body,state)"
  prs_json="$(gh_json pr list --json body,state)"
fi

exec python3 -c '
import json, re, sys

issues = json.loads(sys.argv[1])
prs = json.loads(sys.argv[2])

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
' "$issues_json" "$prs_json"
