#!/usr/bin/env bash
# invisible-work.sh — report work that is not visible, naming the invariant each finding
# breaks. Reads, never writes: it deletes nothing, pushes nothing, opens nothing.
#
# Invariant 2: a branch is never created without a PR. A branch on `origin` for which
# no PR was ever opened — not open, not closed, not merged — is reported with its tip, its
# commit count ahead of the default branch, and, when its name has the `tdd/<n>-<slug>`
# shape, the number and state of issue <n>: that is what tells a live run from an abandoned
# one. An issue the repository does not have — a typo'd number, a transferred or deleted
# issue — has its state named `unknown` rather than guessed.
#
# Invariant 1: work in progress never lives only in a local branch. A local branch
# `origin` does not carry is reported with its tip, how many of its commits no `origin` ref
# holds, and the worktree it is checked out in, when there is one. A local branch whose PR was
# merged or closed is residue — its branch on `origin` deleted after the decision, as GitHub's
# "delete branch on merge" leaves every clone — a cleanup question, not a finding.
#
# The default branch is never reported: it needs no PR, being where PRs land.
#
# A branch any PR was opened for, whatever that PR's state, is not an invariant-2 finding:
# invariant 2 is a branch with no PR at all. One whose PR is still open sits in GitHub's
# review queue already.
#
# The repository's issues and PRs are read as the JSON `gh` emits:
#   gh issue list --state all --limit 10000 --json number,state
#   gh pr list --state all --limit 10000 --json headRefName,state
# VERI_GH_JSON overrides both, naming a directory holding `issues.json` and `prs.json` in those shapes — the same override solvable-issues.sh establishes, so this runs with no
# network in its tests. The JSON is read with python3, as there.
#
# Exit: 0 when at least one finding was printed, 3 with empty stdout when there is nothing
# to report, 2 with a diagnostic on stderr and empty stdout when `origin` cannot be reached
# or `gh` cannot be read — so a fetch failure never reads as a clean repository.
#
# Usage:   invisible-work.sh
#          VERI_GH_JSON=<dir> invisible-work.sh
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"
source "$(dirname "$0")/lib/github.sh"

gh_json() {  # gh_json <fixture-file> <rest-path> <gh args…> -> that document on stdout
  local fixture="$1" rest="$2"; shift 2
  if [[ -n "${VERI_GH_JSON:-}" ]]; then
    cat "$VERI_GH_JSON/$fixture"
  else
    gh_list "repos/{owner}/{repo}/$rest" "$@"
  fi
}

if ! git ls-remote --heads origin > /dev/null; then
  echo "invisible-work.sh: cannot reach origin" >&2
  exit 2
fi

if ! issues_json="$(gh_json issues.json "issues?state=all&per_page=100" issue list --state all --limit 10000 --json number,state)" ||
   ! prs_json="$(gh_json prs.json "pulls?state=all&per_page=100" pr list --state all --limit 10000 --json headRefName,state)"; then
  echo "invisible-work.sh: cannot read issues and PRs from gh (unauthenticated?)" >&2
  exit 2
fi

default="$(git symbolic-ref --short refs/remotes/origin/HEAD)"
default="${default#origin/}"

branches=""
while read -r ref tip; do
  name="${ref#refs/remotes/origin/}"
  [[ "$name" == "$default" || "$name" == HEAD ]] && continue
  ahead="$(git rev-list --count "origin/$default..$ref")"
  branches+="$name $tip $ahead"$'\n'
done < <(git for-each-ref --format='%(refname) %(objectname)' refs/remotes/origin/)

declare -A worktree_of=()
while read -r key value; do
  case "$key" in
    worktree) path="$value" ;;
    branch) worktree_of["$value"]="$path" ;;
  esac
done < <(git worktree list --porcelain)

locals=""
while read -r ref tip; do
  name="${ref#refs/heads/}"
  git show-ref -q --verify "refs/remotes/origin/$name" && continue
  lacks="$(git rev-list --count "$ref" --not --remotes=origin)"
  locals+="$name $tip $lacks ${worktree_of[$ref]:-}"$'\n'
done < <(git for-each-ref --format='%(refname) %(objectname)' refs/heads/)

exec python3 -c '
import json, re, sys

def documents(text):
    items, at, decoder = [], 0, json.JSONDecoder()
    while at < len(text):
        page, at = decoder.raw_decode(text, at)
        items.extend(page)
    return items

def head(pr):
    return pr["headRefName"] if "headRefName" in pr else pr["head"]["ref"]

issues_text, prs_text = sys.stdin.read().split("\0")
issues = {i["number"]: i["state"].upper() for i in documents(issues_text)}
prs = documents(prs_text)
with_pr = {head(p) for p in prs}
decided = {head(p) for p in prs if p["state"].upper() in ("MERGED", "CLOSED")}
findings = []

for row in sys.argv[1].splitlines():
    name, tip, ahead = row.split()
    if name in with_pr:
        continue
    finding = f"invariant 2 (no PR): {name} tip {tip} {ahead} commits ahead"
    m = re.match(r"tdd/(\d+)-", name)
    if m:
        n = int(m.group(1))
        state = issues.get(n, "unknown")
        finding += f", issue #{n} {state}"
    findings.append(finding)

for row in sys.argv[2].splitlines():
    name, tip, lacks, worktree = row.split(" ", 3)
    if name in decided:
        continue
    finding = f"invariant 1 (not on origin): {name} tip {tip} {lacks} commits origin lacks"
    if worktree:
        finding += f", worktree {worktree}"
    findings.append(finding)

for finding in findings:
    print(finding)

sys.exit(0 if findings else 3)
' "$branches" "$locals" < <(printf '%s\0%s' "$issues_json" "$prs_json")
