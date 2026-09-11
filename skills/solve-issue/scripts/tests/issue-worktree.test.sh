#!/usr/bin/env bash
# Unit tests for scripts/issue-worktree.sh — the linked git worktree an issue branch lives
# in, so a conductor never drags the checkout it was invoked from off the default branch
# (issue #43).
#
# Contract under test:
#   issue-worktree.sh <n> <slug>   creates/reuses <repo-root>/.tdd/wt/<n> on branch
#                                  tdd/<n>-<slug>, prints its absolute path, exit 0
#
# Everything is asserted against a throwaway `git init` repo with one commit — worktrees
# need a commit to check out — and through git's own answers (`worktree list`, `rev-parse`)
# rather than by looking at the directory, because a plain `mkdir` would pass the latter.
#
# Run: scripts/tests/issue-worktree.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$HERE/../issue-worktree.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# git_q <repo> <args...> — git with an identity of its own, so the suite does not depend on
# whatever user.name/user.email the machine running it happens to carry (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# new_repo <path> — a throwaway repo at <path>, on `main`, carrying one commit. Both halves
# matter: `git worktree add` refuses a repo with no commit to check out, and -b main names the
# default branch explicitly rather than inheriting whatever init.defaultBranch the machine
# running the suite is configured with.
new_repo() {
  mkdir -p "$1"
  git init -q -b main "$1" >/dev/null 2>&1
  git_q "$1" commit -q --allow-empty -m "initial" >/dev/null 2>&1
}

# wt_path <repo> <n> — the path the script under test is expected to print for issue <n>.
# macOS puts mktemp dirs behind the /var -> /private/var symlink and git reports the resolved
# path, so resolve ours too (`pwd -P`, P for physical) or the comparison fails on a correct
# script.
wt_path() { printf '%s\n' "$(cd "$1" && pwd -P)/.tdd/wt/$2"; }

# 1. a fresh call creates the worktree on a new branch cut from the DEFAULT branch, and
# prints its path.
#
# The seed leaves the caller's checkout on `side`, one commit ahead of `main`: without it,
# "off the default branch" and "off whatever HEAD happened to be" are the same assertion,
# and the bug this script exists to prevent is exactly a conductor acting on the checkout's
# current branch. So the new branch's tip must equal main's tip, not side's.
repo="$work/fresh"
new_repo "$repo"
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
want="$(wt_path "$repo" 7)"

out="$(cd "$repo" && "$WT" 7 add-worktree 2>/dev/null)" && code=0 || code=$?

# git's verdict on what is at that path: its own toplevel, its checked-out branch, its tip.
top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"
branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] \
  && [[ "$branch" == "tdd/7-add-worktree" ]] && [[ "$tip" == "$main_tip" ]]; } \
  && ok || no "fresh call: creates a worktree at .tdd/wt/7 on new branch tdd/7-add-worktree off the default branch and prints its path (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', branch='$branch' want 'tdd/7-add-worktree', tip='$tip' want main's $main_tip not side's $side_tip)"

# 2. a second call for the same issue is a no-op that still answers: same path, exit 0, and
# nothing new created.
#
# "Creates nothing new" is asserted from git's own registry rather than from the filesystem:
# `worktree list --porcelain` plus every branch ref is the full set of things this script can
# add, so snapshotting both around the second call catches a stray worktree or a `tdd/9-...`
# duplicate that a directory check would miss.
repo="$work/again"
new_repo "$repo"
want="$(wt_path "$repo" 9)"

first="$(cd "$repo" && "$WT" 9 resume-me 2>/dev/null)" && first_code=0 || first_code=$?
before="$(git -C "$repo" worktree list --porcelain 2>/dev/null; git -C "$repo" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null)"

second="$(cd "$repo" && "$WT" 9 resume-me 2>/dev/null)" && second_code=0 || second_code=$?
after="$(git -C "$repo" worktree list --porcelain 2>/dev/null; git -C "$repo" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null)"

{ [[ "$first_code" == 0 ]] && [[ "$second_code" == 0 ]] && [[ "$second" == "$want" ]] \
  && [[ "$second" == "$first" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "second call: prints the same path, exits 0 and creates nothing new (first exit=$first_code want 0 stdout='$first', second exit=$second_code want 0 stdout='$second' want '$want', git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
