#!/usr/bin/env bash
# invisible-work.sh — report work that is not visible, naming the invariant each finding
# breaks (issue #197). Reads, never writes: it deletes nothing, pushes nothing, opens nothing.
#
# Invariant 2 (#195): a branch is never created without a PR. A branch on `origin` for which
# no PR was ever opened — not open, not closed, not merged — is reported with its tip, its
# commit count ahead of the default branch, and, when its name has the `tdd/<n>-<slug>`
# shape, the number and state of issue <n>: that is what tells a live run from an abandoned
# one. An issue the repository does not have — a typo'd number, a transferred or deleted
# issue — has its state named `unknown` rather than guessed.
#
# Invariant 1 (#191): work in progress never lives only in a local branch. A local branch
# `origin` does not carry is reported with its tip, how many of its commits no `origin` ref
# holds, and the worktree it is checked out in, when there is one.
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
prs_json="$(gh_json prs.json pr list --state all --limit 10000 --json headRefName,state)"

# The default branch as `origin` names it: `refs/remotes/origin/HEAD` -> `origin/main`.
default="$(git symbolic-ref --short refs/remotes/origin/HEAD)"
default="${default#origin/}"

# One line per branch on origin: `<name> <tip> <commits ahead of the default branch>`.
# The default branch is not a finding, under its own name or its `HEAD` alias.
branches=""
while read -r ref tip; do
  name="${ref#refs/remotes/origin/}"
  [[ "$name" == "$default" || "$name" == HEAD ]] && continue
  ahead="$(git rev-list --count "origin/$default..$ref")"
  branches+="$name $tip $ahead"$'\n'
done < <(git for-each-ref --format='%(refname) %(objectname)' refs/remotes/origin/)

# The worktree each local branch is checked out in: `refs/heads/<name>` -> its path.
declare -A worktree_of=()
while read -r key value; do
  case "$key" in
    worktree) path="$value" ;;
    branch) worktree_of["$value"]="$path" ;;
  esac
done < <(git worktree list --porcelain)

# Invariant 1 (#191): one line per local branch `origin` does not carry:
# `<name> <tip> <commits no origin ref holds> [<worktree>]`.
locals=""
while read -r ref tip; do
  name="${ref#refs/heads/}"
  git show-ref -q --verify "refs/remotes/origin/$name" && continue
  lacks="$(git rev-list --count "$ref" --not --remotes=origin)"
  locals+="$name $tip $lacks ${worktree_of[$ref]:-}"$'\n'
done < <(git for-each-ref --format='%(refname) %(objectname)' refs/heads/)

exec python3 -c '
import json, re, sys

issues = {i["number"]: i["state"] for i in json.loads(sys.argv[1])}
with_pr = {p["headRefName"] for p in json.loads(sys.argv[3])}

for row in sys.argv[2].splitlines():
    name, tip, ahead = row.split()
    if name in with_pr:
        continue
    finding = f"invariant 2 (no PR): {name} tip {tip} {ahead} commits ahead"
    m = re.match(r"tdd/(\d+)-", name)
    if m:
        n = int(m.group(1))
        state = issues.get(n, "unknown")
        finding += f", issue #{n} {state}"
    print(finding)

for row in sys.argv[4].splitlines():
    name, tip, lacks, worktree = row.split(" ", 3)
    finding = f"invariant 1 (not on origin): {name} tip {tip} {lacks} commits origin lacks"
    if worktree:
        finding += f", worktree {worktree}"
    print(finding)
' "$issues_json" "$branches" "$prs_json" "$locals"
