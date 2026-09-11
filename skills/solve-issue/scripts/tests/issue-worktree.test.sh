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

# 1. a fresh call creates the worktree on a new branch cut from the DEFAULT branch, and
# prints its path.
#
# The seed leaves the caller's checkout on `side`, one commit ahead of `main`: without it,
# "off the default branch" and "off whatever HEAD happened to be" are the same assertion,
# and the bug this script exists to prevent is exactly a conductor acting on the checkout's
# current branch. So the new branch's tip must equal main's tip, not side's.
repo="$work/fresh"
mkdir -p "$repo"
git init -q -b main "$repo" >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "initial" >/dev/null 2>&1
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
# macOS puts mktemp dirs behind the /var -> /private/var symlink, and git reports the
# resolved path — so resolve ours too, or the printed-path comparison fails on a correct script.
repo_real="$(cd "$repo" && pwd -P)"
want="$repo_real/.tdd/wt/7"

out="$(cd "$repo" && "$WT" 7 add-worktree 2>/dev/null)" && code=0 || code=$?

# git's verdict on what is at that path: its own toplevel, its checked-out branch, its tip.
top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"
branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] \
  && [[ "$branch" == "tdd/7-add-worktree" ]] && [[ "$tip" == "$main_tip" ]]; } \
  && ok || no "fresh call: creates a worktree at .tdd/wt/7 on new branch tdd/7-add-worktree off the default branch and prints its path (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', branch='$branch' want 'tdd/7-add-worktree', tip='$tip' want main's $main_tip not side's $side_tip)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
