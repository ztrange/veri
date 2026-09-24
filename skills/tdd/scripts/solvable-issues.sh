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
# another project's #120 is not this one's.
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
# leaf's uncommitted work away (#170). A pid is a machine-local name — it means nothing on
# another computer — so a lock nobody answers for frees the worktree and never the issue: a
# bailed run's issue stays out of the pool on the strength of its still-open draft PR, whatever
# its pid says (ADR-0024).
#
# The repository's issues and pull requests are read as the JSON `gh` emits:
#   gh issue list --limit 10000 --json number,title,labels,body,state
#   gh pr list    --limit 10000 --json body,state
# gh returns a page, not the repository — 30 items unless told `--limit` (#244) — and has no
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

# `--repo owner/name` is forwarded to gh verbatim and nothing is invented in its absence:
# a wrong repository is silently wrong, so gh's own default (the repo of the working
# directory) is the only sane fallback. The `[@]+` expansion is what keeps an empty array
# from becoming an empty argument under `set -u`.
#
# The slug is also kept on its own, because it is the only thing that says which repository
# a URL-form blocker has to name to be one: `/<owner>/<other>/issues/120` is another
# project's issue, not this one's #120.
repo_args=()
repo=""
if [[ "${1:-}" == "--repo" ]]; then
  # Checked rather than read through `${2:?…}`, which aborts with status 1 — the code this
  # script reserves for a real answer. A --repo with no repository named is exit 2 (#270).
  [[ -n "${2:-}" ]] || { echo "usage: solvable-issues.sh [--repo owner/name]" >&2; exit 2; }
  repo="$2"
  repo_args=(--repo "$repo")
fi

# A label tunable set but EMPTY is a misconfigured run, not a choice — a launcher writing
# `VERI_LABEL="$some_unset_var"` is how it gets there — so refuse before anything is fetched
# rather than guess which name was meant. The two expansions each tunable is read through
# differ by one character and that difference is the whole of it: `${VAR-x}` yields the value
# when the variable is set and the literal `x` when it is not, so it is empty in exactly the
# set-but-empty case, whereas the `${VAR:-…}` that supplies the default cannot tell empty from
# unset and would quietly take one for the other. Fail closed like refactor-budget.sh does on a
# malformed budget: a diagnostic on stderr, exit 2 — no answer could be obtained — and nothing
# on stdout for a caller to mistake for a pool.
#
# Both labels refuse in that one shape, so it is written once and asked by name: `${!var-x}` is
# the same expansion read indirectly. The function is called as a statement rather than in a
# command substitution, so its `exit` is this script's exit and not a subshell's.
refuse_if_empty() {  # refuse_if_empty <var-name> — exit 2 if that variable is set but empty
  local var="$1"
  if [[ -z "${!var-x}" ]]; then
    echo "solvable-issues: $var is set but empty: name a label or leave it unset" >&2
    exit 2
  fi
}

# The opt-in label, read the way every other tunable in this suite is read. Setting it moves
# the gate rather than widening it: the pool becomes exactly the issues carrying that name,
# and `ready-for-agent` stops being special. That is what lets two loops on one repository
# drain two disjoint pools instead of racing for the same issues. Empty, it would match every
# issue — the opt-in gate gone, which is the failure the refusal above prevents.
refuse_if_empty VERI_LABEL
label="${VERI_LABEL:-ready-for-agent}"

# The label that says "take this one sooner", read like every other tunable. It names a band
# in the print order and nothing else: an issue carrying it still has to pass all four
# conditions above, so priority reorders the solvable set and never enlarges it. The default
# is the `priority` label the repository already has. Empty, it would put the whole solvable
# set in the priority band — the ordering equivalent of an empty opt-in label — so it refuses
# the same way.
refuse_if_empty VERI_PRIORITY_LABEL
priority_label="${VERI_PRIORITY_LABEL:-priority}"

# One document, from whichever of the two sources is in force. Both the override and the
# `--repo` scoping are decided here rather than around the pair of fetches, so each document
# is named exactly once — beside the gh call that produces it and the fixture that stands in
# for it — and this stays the only place that awkward `[@]+` expansion has to be understood.
gh_json() {  # gh_json <fixture-file> <gh args…> -> that document on stdout
  local fixture="$1"; shift
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/$fixture"
  else
    gh "$@" "${repo_args[@]+"${repo_args[@]}"}"
  fi
}

issues_json="$(gh_json issues.json issue list --limit 10000 --json number,title,labels,body,state)"
prs_json="$(gh_json prs.json pr list --limit 10000 --json body,state)"

# The directory the in-flight locks hang off: the repository's MAIN working tree, resolved by
# lib/main-working-tree.sh (#166). A caller outside any repository gets an empty root, and the
# liveness check below then finds no lock and claims nothing — which is the right reading, since
# with no repository there is no worktree to hold a run.
# shellcheck source=lib/main-working-tree.sh
source "$(dirname "$0")/lib/main-working-tree.sh"
main_tree="$(main_working_tree)"

# The `## Blocked by` reading comes from lib/blocked_by.py (#460), reached the way status.sh
# reaches event_log: PYTHONPATH naming the lib, so a second reader imports the same parsing
# rather than copying it.
PYTHONPATH="$(cd "$(dirname "$0")" && pwd)/lib" exec python3 -c '
import json, os, re, sys

import blocked_by

issues = json.loads(sys.argv[1])
prs = json.loads(sys.argv[2])
label = sys.argv[3]
priority_label = sys.argv[4]
this_repo = sys.argv[5]
main_tree = sys.argv[6]

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

# `os.kill(pid, 0)` is `kill -0`: it sends no signal and answers only whether the process is
# there to send one to. A process owned by another user answers PermissionError — it exists,
# which is the whole question, so the `except OSError` falls through to the same answer the
# call itself gives — while one that is gone answers ProcessLookupError.
def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        pass
    return True

# The lock a run in flight leaves behind, and whether the conductor that wrote it is still
# there. Everything about it is fail-open: no repository root, no worktree, no lock file, a
# lock holding something that is not a number — each means nobody has claimed this issue, so
# the issue stays takeable. A claim has to be POSITIVELY observed, because the cost of reading
# a stale file as a live run is an issue nobody can take until a human deletes it, while the
# cost of the opposite is the collision that was already there.
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

# Whether an issue carries a label, asked the same way whoever is asking: the opt-in label
# that decides whether an issue may be taken at all, and the `bug` label that decides where it
# sorts, are two questions about one field, and `gh` writes that field as a list of objects
# with a `name`. One reading of that shape, so a fixture missing `labels` entirely is handled
# in one place rather than in each caller.
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
    unblocked = all(n not in open_issues for n in blocked_by.blockers(issue.get("body", ""), this_repo))
    return still_open and opted_in and unclaimed and unblocked

# The order the surviving set is printed in — the only thing the caller reads as "what to do
# next", since the /tdd loop takes the first line. Three bands, one key read left to right:
# the priority label says take this one sooner and beats everything, a `bug` label moves an
# issue ahead of every plain one however much older that plain one is — what is BROKEN goes
# before what is merely wanted — and inside a band the old rule stands, ascending by number,
# so the queue is still first-come-first-served among equals (#113, folding in #215). One key
# rather than three passes, and the band is ONE number rather than one term per label: an
# issue carrying both labels belongs to the priority band and is then ordered by number among
# the other priority issues, which a `(not is_priority, not is_bug, number)` key would get
# wrong — it would sort the both-labelled issue ahead of a lower-numbered plain priority one.
#
# The sort runs on what `solvable()` already let through, so order never enlarges the set: a
# priority or bug issue that is blocked, claimed or not opted in is still not printed.
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

# Nothing takeable is not an error: it is veri exit code 3, "nothing to do". The caller
# learns it from the code rather than from having to notice that stdout was empty.
if not numbers:
    sys.exit(3)
' "$issues_json" "$prs_json" "$label" "$priority_label" "$repo" "$main_tree"
