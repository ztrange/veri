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

# registry <repo> — everything the script under test is able to add to a repo: git's own list
# of registered worktrees, plus every branch ref. Snapshotting this either side of a call is
# how the "creates nothing new" and "touches nothing" assertions are made; a filesystem check
# would miss a stray `tdd/<n>-...` branch, and would be fooled by a plain `mkdir`.
registry() {
  git -C "$1" worktree list --porcelain 2>/dev/null
  git -C "$1" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null
}

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
# "Creates nothing new" is asserted from git's own registry() rather than from the filesystem,
# so a stray worktree or a duplicate `tdd/9-...` branch would show up as a changed snapshot.
repo="$work/again"
new_repo "$repo"
want="$(wt_path "$repo" 9)"

first="$(cd "$repo" && "$WT" 9 resume-me 2>/dev/null)" && first_code=0 || first_code=$?
before="$(registry "$repo")"

second="$(cd "$repo" && "$WT" 9 resume-me 2>/dev/null)" && second_code=0 || second_code=$?
after="$(registry "$repo")"

{ [[ "$first_code" == 0 ]] && [[ "$second_code" == 0 ]] && [[ "$second" == "$want" ]] \
  && [[ "$second" == "$first" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "second call: prints the same path, exits 0 and creates nothing new (first exit=$first_code want 0 stdout='$first', second exit=$second_code want 0 stdout='$second' want '$want', git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

# 3. the branch is already checked out somewhere else — another conductor owns it. Refuse:
# exit 2, say where it is, and leave the repo exactly as it was.
#
# The seed is a worktree at a path of our own choosing holding tdd/11-taken, which is what a
# second conductor's checkout looks like from here. The diagnostic has to carry that path
# because it is the only thing that tells a human which run to go and look at, so the
# assertion is on the path appearing in stderr, not merely on some message being printed.
# "Touches nothing" is the same registry() snapshot as case 2, plus the absence of the
# directory the script would otherwise have created.
repo="$work/taken"
new_repo "$repo"
other="$(cd "$work" && pwd -P)/taken-elsewhere"
git_q "$repo" worktree add -q -b tdd/11-collide "$other" main >/dev/null 2>&1
mine="$(wt_path "$repo" 11)"
before="$(registry "$repo")"

# 2>&1 >/dev/null, in that order: stderr is pointed at where stdout currently goes (the
# capture), then stdout is sent to /dev/null. So $err holds the diagnostic alone.
err="$(cd "$repo" && "$WT" 11 collide 2>&1 >/dev/null)" && code=0 || code=$?
after="$(registry "$repo")"

{ [[ "$code" == 2 ]] && [[ "$err" == *"$other"* ]] && [[ ! -e "$mine" ]] \
  && [[ "$after" == "$before" ]]; } \
  && ok || no "branch checked out elsewhere: exits 2 naming that worktree and touches nothing (exit=$code want 2, stderr='$err' want it to name '$other', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

# 4. --remove <n> takes the worktree back out again — but only when there is nothing in it to
# lose. Both halves are the same criterion (a removal that cannot tell the two apart is either
# useless or destructive), so they are asserted together.
#
# Clean half: git's registry must no longer list the path, and the directory must be gone.
# Only the `worktree <path>` line is asserted absent, not the whole snapshot — whether the
# branch is also deleted is not something this step decides.
#
# Dirty half: the worktree carries a staged, uncommitted file, which is a change a human would
# lose. Refusing means exit 2 and leaving everything — registry and directory — exactly as it
# was. The file is staged rather than merely written so it is an uncommitted change under any
# reading of the word.
repo="$work/remove-clean"
new_repo "$repo"
want="$(wt_path "$repo" 13)"
(cd "$repo" && "$WT" 13 done-with-this >/dev/null 2>&1)

(cd "$repo" && "$WT" --remove 13 >/dev/null 2>&1) && clean_code=0 || clean_code=$?
clean_after="$(registry "$repo")"

repo="$work/remove-dirty"
new_repo "$repo"
dirty="$(wt_path "$repo" 14)"
(cd "$repo" && "$WT" 14 still-working >/dev/null 2>&1)
printf 'work in progress\n' > "$dirty/notes.txt"
git_q "$dirty" add notes.txt >/dev/null 2>&1
dirty_before="$(registry "$repo")"

(cd "$repo" && "$WT" --remove 14 >/dev/null 2>&1) && dirty_code=0 || dirty_code=$?
dirty_after="$(registry "$repo")"

{ [[ "$clean_code" == 0 ]] && [[ "$clean_after" != *"worktree $want"* ]] && [[ ! -e "$want" ]] \
  && [[ "$dirty_code" == 2 ]] && [[ -e "$dirty/notes.txt" ]] && [[ "$dirty_after" == "$dirty_before" ]]; } \
  && ok || no "--remove: removes a clean worktree and refuses one with uncommitted changes with exit 2 (clean: exit=$clean_code want 0, '$want' $( [[ -e "$want" ]] && echo "still on disk" || echo "gone, good" ), still in git's registry: $( [[ "$clean_after" == *"worktree $want"* ]] && echo yes || echo no ); dirty: exit=$dirty_code want 2, notes.txt $( [[ -e "$dirty/notes.txt" ]] && echo "survived, good" || echo "was destroyed" ), git's worktree+branch registry $( [[ "$dirty_after" == "$dirty_before" ]] && echo unchanged || echo "changed:
--- before
$dirty_before
--- after
$dirty_after" ))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
