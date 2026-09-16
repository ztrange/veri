#!/usr/bin/env bash
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line: the `bug`-labelled ones first, then the rest, each band ascending by number.
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
# An open PR is not the only claim, because it is the LAST thing a run makes: the conductor
# opens its draft PR after every step is green, so for the whole run before that — hours; #137
# took about eleven — the issue would otherwise still read as takeable, and a second conductor
# taking it lands in the live run's worktree and follows *Resume*, whose `git reset --hard
# HEAD` throws the live leaf's uncommitted work away (#170). So a run also claims its issue
# from its FIRST step, by writing its own pid into `.tdd/wt/<n>/.tdd/conductor.pid` under the
# repository's main working tree, and an issue whose lock names a process that still answers
# `kill -0` is left out here.
#
# A pid rather than a `veri:in-flight` label on the issue: a label is visible across machines,
# but it outlives the process that set it, so a crashed or killed run leaves its issue claimed
# until a human goes and un-claims it by hand. A pid that no longer answers reads as free on
# the very next selection — which is what a bailed run needs, since its issue must stay
# resumable. The cost is that the claim is local to one machine, and #102's parallel conductors
# are local to one machine too.
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
#          VERI_LABEL=<name>  solvable-issues.sh
# Exit:    0 one or more numbers printed; 2 no answer could be obtained — VERI_LABEL is set
#          but empty; 3 nothing to do — no issue is takeable
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
  repo="${2:?usage: solvable-issues.sh [--repo owner/name]}"
  repo_args=(--repo "$repo")
fi

# The opt-in label, read the way every other tunable in this suite is read. Setting it moves
# the gate rather than widening it: the pool becomes exactly the issues carrying that name,
# and `ready-for-agent` stops being special. That is what lets two loops on one repository
# drain two disjoint pools instead of racing for the same issues.
#
# Set but EMPTY is a misconfigured run, not a choice — a launcher writing
# `VERI_LABEL="$some_unset_var"` is how it gets there — so refuse before anything is fetched
# rather than guess which label was meant. The two expansions below differ by one character
# and that difference is the whole of it: `${VERI_LABEL-x}` yields the value when the variable
# is set and the literal `x` when it is not, so it is empty in exactly the set-but-empty case,
# whereas the `${VERI_LABEL:-…}` that supplies the default cannot tell empty from unset and
# would quietly take one for the other. Fail closed like refactor-budget.sh does on a
# malformed budget: a diagnostic on stderr, exit 2 — no answer could be obtained — and
# nothing on stdout for a caller to mistake for a pool.
if [[ -z "${VERI_LABEL-x}" ]]; then
  echo "solvable-issues: VERI_LABEL is set but empty: name a label or leave it unset" >&2
  exit 2
fi
label="${VERI_LABEL:-ready-for-agent}"

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

issues_json="$(gh_json issues.json issue list --json number,title,labels,body,state)"
prs_json="$(gh_json prs.json pr list --json body,state)"

# The directory the in-flight locks hang off: the repository's MAIN working tree, because that
# is where issue-worktree.sh puts every run's worktree (`wt_path`, off `main_working_tree`) —
# never the checkout this script happens to have been called from, which for a conductor
# started inside a session worktree is a different directory entirely (#166). git's registry
# prints the main working tree as the first block's `worktree <path>` line, so that first line
# with its label taken off is the answer.
#
# `|| true` because a caller outside any repository is not an error here: git says nothing, the
# root comes out empty, and the liveness check below then finds no lock and claims nothing —
# which is the right reading, since with no repository there is no worktree to hold a run.
#
# Taking the label off is inside the function, not a second assignment to a name in the script's
# own scope, for the reason issue-worktree.sh:37-40 argues about the same two steps; a second copy
# of that argument here is one that drifts.
main_working_tree() {
  local first_line
  first_line="$(git worktree list --porcelain 2>/dev/null | head -n 1 || true)"
  printf '%s\n' "${first_line#worktree }"
}
main_tree="$(main_working_tree)"

exec python3 -c '
import json, os, re, sys

issues = json.loads(sys.argv[1])
prs = json.loads(sys.argv[2])
label = sys.argv[3]
this_repo = sys.argv[4]
main_tree = sys.argv[5]

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

# A blocker is spelled `#<n>` or as the full URL GitHub itself renders and autocompletes, and
# the owner and name in that URL are part of the reference rather than decoration around the
# digits: an issue #120 exists in a fork, in a dependency and in the demo repo veri is pointed
# at, so reading the number alone invents a blocker out of some other project. Which repository
# "this one" is comes from `--repo`; with nothing said there is nothing to compare against, so
# any github.com issue URL is read as local — the same assumption gh makes when it falls back
# to the repo of the working directory.
slug_pattern = re.escape(this_repo) if this_repo else r"[^/\s]+/[^/\s]+"
blocker_ref = r"(?:#|https://github\.com/%s/issues/)(\d+)" % slug_pattern

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

def blockers(body):
    """The issue numbers named under the `## Blocked by` heading, up to the next heading.
    A section reading `None.` names none, and so does a body with no such section."""
    section = re.search(r"^## Blocked by$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return [int(n) for n in re.findall(blocker_ref, section.group(1))] if section else []

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
    unblocked = all(n not in open_issues for n in blockers(issue.get("body", "")))
    return still_open and opted_in and unclaimed and unblocked

# The order the surviving set is printed in — the only thing the caller reads as "what to do
# next", since the /tdd loop takes the first line. A `bug` label moves an issue ahead of every
# plain one however much older that plain one is: what is BROKEN goes before what is merely
# wanted (#113). Inside a band the old rule stands, ascending by number, so the queue is still
# first-come-first-served among equals. One key, not two passes: `False` sorts before `True`,
# so `not is_bug` puts the labelled band in front and `number` breaks every tie within it.
#
# The sort runs on what `solvable()` already let through, so order never enlarges the set: a
# bug that is blocked, claimed or not opted in is still not printed.
def order(issue):
    is_bug = has_label(issue, "bug")
    return (not is_bug, issue["number"])

numbers = [i["number"] for i in sorted((i for i in issues if solvable(i)), key=order)]
for number in numbers:
    print(number)

# Nothing takeable is not an error: it is veri exit code 3, "nothing to do". The caller
# learns it from the code rather than from having to notice that stdout was empty.
if not numbers:
    sys.exit(3)
' "$issues_json" "$prs_json" "$label" "$repo" "$main_tree"
