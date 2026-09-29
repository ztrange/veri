#!/usr/bin/env bash
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line: the `priority`-labelled ones first, then the `bug`-labelled ones, then the rest,
# each band ascending by number.
#
# An issue is solvable when it is open, carries the opt-in label (`ready-for-agent`, or the
# name `VERI_LABEL` gives instead — the human's explicit opt-in, since nothing is taken
# because it merely exists), every issue it names under its `## Blocked by` heading is
# closed, and no open pull request already says `Closes #<n>` for it — such a PR means a run
# is in flight on that issue, or one bailed and left the branch behind, and either way the
# issue is not veri's to take. A body whose `## Blocked by` section reads `None.` names no
# issue at all, so the test for "unblocked" is the absence of any issue reference under that
# heading rather than the literal word. A reference is spelled either way GitHub writes one:
# `#<n>`, or the full `https://github.com/<owner>/<repo>/issues/<n>` URL its autocomplete
# inserts — and that URL blocks only when its `<owner>/<repo>` is this repository's, since
# another project's `#<n>` is not this one's.
#
# The open PR is the claim, and it is the only mark of a run every machine can see. The
# conductor pushes the branch and opens its draft PR as the first act after the plan commit, so
# an issue whose run is in flight — or whose run bailed and left the branch behind — carries an
# open PR saying `Closes #<n>` from then on, and is left out here for as long as it does. veri
# is developed from more than one computer and `origin` is all they share, so a claim recorded
# anywhere else is one the other machine cannot read (ADR-0024). A `veri:in-flight` label would
# be visible too, but it outlives the run that set it with nothing to clear it, and it
# duplicates what the PR already records.
#
# The lock `.tdd/wt/<n>/.tdd/conductor.pid`, written under the repository's main working tree,
# is NOT a second claim: it is the worktree guard, and it guards one machine's worktree only.
# While the pid in there still answers `kill -0`, no second conductor on that same machine may
# enter the live run's tree and follow *Resume*, whose `git reset --hard HEAD` throws the live
# leaf's uncommitted work away. A pid is a machine-local name — it means nothing on
# another computer — so a lock nobody answers for frees the worktree and never the issue: a
# bailed run's issue stays out of the pool on the strength of its still-open draft PR, whatever
# its pid says (ADR-0024).
#
# The repository's issues and pull requests are read as the JSON `gh` emits:
#   gh issue list --limit 10000 --json number,title,labels,body,state
#   gh pr list    --limit 10000 --json body,state
# gh returns a page, not the repository — 30 items unless told `--limit` — and has no
# "all", so the limit is a number no repository here comes near.
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
#          VERI_LABEL=<name>  solvable-issues.sh
# Exit:    0 one or more numbers printed; 2 no answer could be obtained — VERI_LABEL or
#          VERI_PRIORITY_LABEL is set but empty; 3 nothing to do — no issue is takeable
set -euo pipefail

repo_args=()
repo=""
if [[ "${1:-}" == "--repo" ]]; then
  [[ -n "${2:-}" ]] || { echo "usage: solvable-issues.sh [--repo owner/name]" >&2; exit 2; }
  repo="$2"
  repo_args=(--repo "$repo")
fi

# hazard: `${VAR-x}` is empty only when VAR is set but empty; `${VAR:-x}` cannot tell that from unset.
refuse_if_empty() {  # refuse_if_empty <var-name> — exit 2 if that variable is set but empty
  local var="$1"
  if [[ -z "${!var-x}" ]]; then
    echo "solvable-issues: $var is set but empty: name a label or leave it unset" >&2
    exit 2
  fi
}

refuse_if_empty VERI_LABEL
label="${VERI_LABEL:-ready-for-agent}"

refuse_if_empty VERI_PRIORITY_LABEL
priority_label="${VERI_PRIORITY_LABEL:-priority}"

source "$(dirname "$0")/lib/github.sh"

# hazard: the `[@]+` expansion keeps an empty array from becoming an empty argument.
gh_json() {  # gh_json <fixture-file> <rest-path> <gh args…> -> that document on stdout
  local fixture="$1" rest="$2"; shift 2
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/$fixture"
  else
    gh_list "repos/${repo:-"{owner}/{repo}"}/$rest" "$@" "${repo_args[@]+"${repo_args[@]}"}"
  fi
}

issues_json="$(gh_json issues.json issues issue list --limit 10000 --json number,title,labels,body,state)"
prs_json="$(gh_json prs.json pulls pr list --limit 10000 --json body,state)"

source "$(dirname "$0")/lib/main-working-tree.sh"
main_tree="$(main_working_tree)"

# hazard: the python block is one single-quoted string, so an apostrophe inside it ends it.
PYTHONPATH="$(cd "$(dirname "$0")" && pwd)/lib" exec python3 -c '
import json, os, re, sys

import blocked_by

def documents(text):
    items, at, decoder = [], 0, json.JSONDecoder()
    while at < len(text):
        page, at = decoder.raw_decode(text, at)
        items.extend(page)
    return items

issues = documents(sys.argv[1])
prs = documents(sys.argv[2])
label = sys.argv[3]
priority_label = sys.argv[4]
this_repo = sys.argv[5]
main_tree = sys.argv[6]

def is_open(record):
    return record.get("state", "").upper() == "OPEN"

open_issues = {i["number"] for i in issues if is_open(i)}

claimed = {
    int(n)
    for pr in prs
    if is_open(pr)
    for n in re.findall(r"\bCloses #(\d+)", pr.get("body") or "")
}

def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        pass
    return True

def in_flight(number):
    if not main_tree:
        return False
    lock = os.path.join(
        main_tree, ".tdd", "wt", str(number), ".tdd", "conductor.pid")
    try:
        with open(lock) as f:
            pid = int(f.read().strip())
    except (OSError, ValueError):
        return False
    return alive(pid)

def has_label(issue, name):
    return any(l.get("name") == name for l in issue.get("labels", []))

def solvable(issue):
    """The four conditions the spec names, all of which must hold at once. They are named
    here rather than run as early returns so the function reads as the definition it is.
    `unclaimed` is one condition observed two ways — an open PR saying `Closes #<n>`, and a
    live conductor pid — because both say the same thing about the issue: somebody already
    has it. Which of the two was seen changes nothing a caller does."""
    number = issue["number"]
    still_open = number in open_issues
    opted_in = has_label(issue, label)
    unclaimed = number not in claimed and not in_flight(number)
    unblocked = all(n not in open_issues for n in blocked_by.blockers(issue.get("body") or "", this_repo))
    return still_open and opted_in and unclaimed and unblocked

def order(issue):
    if has_label(issue, priority_label):
        band = 0
    elif has_label(issue, "bug"):
        band = 1
    else:
        band = 2
    return (band, issue["number"])

numbers = [i["number"] for i in sorted((i for i in issues if solvable(i)), key=order)]
for number in numbers:
    print(number)

if not numbers:
    sys.exit(3)
' "$issues_json" "$prs_json" "$label" "$priority_label" "$repo" "$main_tree"
