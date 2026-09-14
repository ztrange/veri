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

# wt_path <root> <n> — issue <n>'s worktree path under <root>. The `.tdd/wt/<n>` layout is
# written once, here, and asked of two different roots: the fixture repo's main working tree,
# where every case expects the worktree to land, and — in case 9 — the linked worktree it must
# never be nested inside. Spelling that second one out by hand would put the layout in two
# places, and a case asserting the absence of a path it had mistyped would pass for the wrong
# reason.
#
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

# linked_worktree <repo> <name> <branch> — a second working directory of <repo>, at $work/<name>
# on a new <branch> cut from main, with its path printed. That is what a Claude session checkout
# looks like from here, and two cases below need one: as the checkout that already holds the
# issue branch (case 3), and as the checkout the script under test is called from (case 9).
#
# `pwd -P` for the same reason wt_path does it: git reports every worktree path with its symlinks
# resolved, so a path we hand git unresolved comes back different and a correct script compares
# unequal. Resolving it here means neither caller has to remember that.
linked_worktree() {
  local path="$(cd "$work" && pwd -P)/$2"
  git_q "$1" worktree add -q -b "$3" "$path" main >/dev/null 2>&1
  printf '%s\n' "$path"
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
other="$(linked_worktree "$repo" taken-elsewhere tdd/11-collide)"
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

# 5. the branch exists already but no worktree holds it — a resume after the last run's worktree
# was removed, or a branch pushed earlier and fetched back. Check it out instead of failing on
# `-b`, which git refuses once the ref is there.
#
# The seed puts a commit on tdd/17-resume and then leaves it behind on `main`, so the branch
# exists, is ahead of main, and nobody has it checked out. That gap is the whole assertion: a
# worktree whose tip is the branch's own commit proves the existing branch was checked out,
# while one sitting at main's tip would mean the branch was cut afresh and the resumed work
# silently dropped.
repo="$work/existing-branch"
new_repo "$repo"
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c tdd/17-resume >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work from the previous run" >/dev/null 2>&1
branch_tip="$(git_q "$repo" rev-parse tdd/17-resume)"
git_q "$repo" switch -q main >/dev/null 2>&1
want="$(wt_path "$repo" 17)"

out="$(cd "$repo" && "$WT" 17 resume 2>/dev/null)" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/17-resume" ]] \
  && [[ "$tip" == "$branch_tip" ]]; } \
  && ok || no "existing branch, no worktree: checks the branch out into .tdd/wt/17 instead of failing on -b (exit=$code want 0, stdout='$out' want '$want', branch='$branch' want 'tdd/17-resume', tip='$tip' want the existing branch's $branch_tip not main's $main_tip)"

# 6. the default branch comes from origin/HEAD when there is a remote — including when it is
# named neither `main` nor `master`.
#
# Every other case here runs against a `git init` repo with no remote, so only the local
# main/master fallback is ever exercised and "reads origin/HEAD" and "guessed `main`" are the
# same answer. The seed closes that gap: an upstream whose only branch is `trunk`, cloned, so
# the clone carries no local `main` or `master` at all — the fallback has nothing to answer
# with, and a script that ignored origin/HEAD could only fail. origin/HEAD is pointed at
# origin/trunk explicitly rather than trusted to whatever `git clone` inferred, so the case
# pins the ref the script reads and not a clone-time side effect.
upstream="$work/upstream-trunk"
new_repo "$upstream"
git_q "$upstream" branch -m main trunk >/dev/null 2>&1
clone="$work/clone-trunk"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$clone" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/trunk >/dev/null 2>&1
trunk_tip="$(git_q "$clone" rev-parse refs/remotes/origin/trunk)"
want="$(wt_path "$clone" 21)"

out="$(cd "$clone" && "$WT" 21 remote-default 2>/dev/null)" && code=0 || code=$?

tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$tip" == "$trunk_tip" ]]; } \
  && ok || no "origin/HEAD names a default branch that is neither main nor master: cuts the new worktree from it (exit=$code want 0, tip='$tip' want origin/trunk's $trunk_tip)"

# 7. no remote at all and the only branch is `master` — the local fallback's second name, which
# every other case here leaves unexercised because new_repo seeds `main`.
#
# The seed renames `main` to `master` (so the first name the fallback tries is genuinely absent,
# and a script that only knew `main` could only fail with exit 2) and then leaves the checkout on
# a `side` branch one commit ahead. That last part is the same guard as case 1: with the checkout
# sitting on `master` itself, "cut from master" and "cut from whatever HEAD was" would be the
# same tip and the assertion would prove nothing.
repo="$work/local-master"
new_repo "$repo"
git_q "$repo" branch -m main master >/dev/null 2>&1
master_tip="$(git_q "$repo" rev-parse master)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
want="$(wt_path "$repo" 23)"

out="$(cd "$repo" && "$WT" 23 local-master 2>/dev/null)" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/23-local-master" ]] \
  && [[ "$tip" == "$master_tip" ]]; } \
  && ok || no "no remote and only a local master: cuts tdd/23-local-master from master (exit=$code want 0, stdout='$out' want '$want', branch='$branch' want 'tdd/23-local-master', tip='$tip' want master's $master_tip not side's $side_tip)"

# 8. no remote and no branch by either fallback name — the script cannot name a base to cut from,
# so it must refuse rather than guess. Exit 2, "no answer could be obtained": a repo whose default
# branch is unnameable is plumbing broken before any TDD cycle starts, not a step that failed.
#
# The seed renames `main` to `trunk`, so neither `main` nor `master` exists and there is no remote
# to supply an origin/HEAD either — every arm of the lookup comes back empty. Cases 6 and 7 pin the
# two arms that can answer; this one pins what happens when none can.
#
# Four things are asserted together because they are one criterion — a refusal that still printed a
# path, or still cut a branch, would be worse than a crash. stdout must be empty (the caller parses
# that line as a worktree path and would `cd` into whatever it said), stderr must carry a diagnostic
# naming the default branch as the thing that could not be determined (distinguishing this refusal
# from case 3's "already checked out elsewhere"), and git's own registry() snapshot must be
# byte-identical either side of the call.
repo="$work/no-default"
new_repo "$repo"
git_q "$repo" branch -m main trunk >/dev/null 2>&1
before="$(registry "$repo")"

# stdout is captured and stderr diverted to a file, so both streams can be asserted on from the one
# run — case 3's `2>&1 >/dev/null` trick keeps only stderr, and here stdout's emptiness is half the
# criterion.
errfile="$work/no-default.err"
out="$(cd "$repo" && "$WT" 25 no-default 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"
after="$(registry "$repo")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ "$err" == *"default branch"* ]] \
  && [[ "$after" == "$before" ]]; } \
  && ok || no "no remote and no main or master: exits 2 with a diagnostic on stderr, nothing on stdout, and nothing created (exit=$code want 2, stdout='$out' want empty, stderr='$err' want it to name the 'default branch', git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

# 9. called from inside a *linked* worktree — a Claude session checkout, or any other second
# working directory of the same repo — the issue worktree still lands under the **main** working
# tree (issue #166). Every case above runs from the main working tree, where "the checkout we
# were called from" and "the main working tree" are the same directory and the distinction
# cannot show up.
#
# It has to be the main tree and not the caller's: a worktree nested inside a session checkout
# dies with that checkout (taking the run's leaf logs with it), and a resume from the main clone
# computes the un-nested path, fails to find it registered, and then refuses because the branch
# is checked out "somewhere else".
#
# The seed is a linked worktree of the fixture repo on its own branch, which is what a session
# checkout looks like from here. Both halves are asserted: the path printed is the main tree's
# and git agrees a worktree is really there, and nothing was created under the linked worktree.
repo="$work/from-linked"
new_repo "$repo"
linked="$(linked_worktree "$repo" from-linked-session session)"
want="$(wt_path "$repo" 27)"
nested="$(wt_path "$linked" 27)"

out="$(cd "$linked" && "$WT" 27 from-linked 2>/dev/null)" && code=0 || code=$?

top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] \
  && [[ ! -e "$nested" ]]; } \
  && ok || no "called from a linked worktree: creates and prints the main working tree's .tdd/wt/27, not one nested inside the caller (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', '$nested' $( [[ -e "$nested" ]] && echo "was created inside the linked worktree" || echo "absent, good" ))"

# 10. the two callers agree: a run created from a linked worktree is found again by a later call
# from the **main** working tree — same path, exit 0, nothing new created (issue #166).
#
# Case 2 already pins idempotence, but both of its calls come from the same checkout, so it holds
# just as well for a script that roots the worktree wherever it happens to be standing. This case
# is the one that separates them: the create runs from the session checkout and the resume runs
# from the main clone, which is exactly the pair that used to disagree — the second caller computed
# a path nobody had registered, found the branch checked out in the nested worktree, and refused
# with "another conductor owns it" about a run nobody was driving.
#
# "Creates nothing" is git's own registry() snapshot either side of the second call, the same way
# case 2 asks it: a resume that quietly cut a second branch or registered a second worktree would
# show up there and nowhere on the filesystem.
repo="$work/cross-caller"
new_repo "$repo"
linked="$(linked_worktree "$repo" cross-caller-session cross-session)"
want="$(wt_path "$repo" 29)"

first="$(cd "$linked" && "$WT" 29 cross-caller 2>/dev/null)" && first_code=0 || first_code=$?
before="$(registry "$repo")"

second="$(cd "$repo" && "$WT" 29 cross-caller 2>/dev/null)" && second_code=0 || second_code=$?
after="$(registry "$repo")"

{ [[ "$first_code" == 0 ]] && [[ "$second_code" == 0 ]] && [[ "$second" == "$want" ]] \
  && [[ "$second" == "$first" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "created from a linked worktree, called again from the main working tree: prints the same path, exits 0 and creates nothing (create from '$linked' exit=$first_code want 0 stdout='$first', call from the main working tree exit=$second_code want 0 stdout='$second' want '$want', git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

# 11. --remove run from a linked worktree removes the worktree under the **main** working tree
# (issue #166). Case 4 pins --remove from the main working tree, where the caller's checkout and
# the main tree are the same directory, so it holds just as well for a remove that deletes
# whatever is under wherever it is standing.
#
# This is the `merge` skill's cleanup: it calls `issue-worktree.sh --remove <n>` from whatever
# checkout the merge is being driven in, which is not the checkout the run was created from. A
# remove that resolved the caller's root would compute a path nobody registered and leave the real
# worktree behind.
#
# The seed creates issue 31's worktree from the main working tree and then calls --remove from a
# linked worktree of the same repo. Both halves of "removed" are asserted the way case 4 asks
# them: git's registry no longer lists the path, and the directory is gone from disk.
repo="$work/remove-from-linked"
new_repo "$repo"
want="$(wt_path "$repo" 31)"
(cd "$repo" && "$WT" 31 remove-from-linked >/dev/null 2>&1)
linked="$(linked_worktree "$repo" remove-from-linked-session remove-session)"

(cd "$linked" && "$WT" --remove 31 >/dev/null 2>&1) && code=0 || code=$?
after="$(registry "$repo")"

{ [[ "$code" == 0 ]] && [[ "$after" != *"worktree $want"* ]] && [[ ! -e "$want" ]]; } \
  && ok || no "--remove from a linked worktree: removes the main working tree's .tdd/wt/31 (exit=$code want 0, '$want' $( [[ -e "$want" ]] && echo "still on disk" || echo "gone, good" ), still in git's registry: $( [[ "$after" == *"worktree $want"* ]] && echo yes || echo no ))"

# 12. the repository is reached through a symlinked path — the path printed is still the
# symlink-resolved one, so it is byte-identical to the `worktree` line
# `git worktree list --porcelain` prints for that worktree (issue #166).
#
# This is the property the script's own comment set out to keep when it picked a git-reported
# root: git resolves every worktree path it stores and every one it prints, so a script that
# built the path out of the caller's *logical* cwd would hand back a spelling git never uses.
# Nothing downstream would notice at creation time and everything would afterwards — the
# idempotence check greps the registry for that exact line, and `git worktree remove` is given
# the same string.
#
# The seed is a symlink pointing at the fixture repo, and the script is called through it. The
# assertion is on git's own line and not merely on a resolved-looking string: `grep -qxF`
# (-x whole line, -F literal, so a `.` in the path is a dot) is the same question the script
# asks of the registry, so a printed path that fails it is one the script could not find again.
#
# Every other case reaches the fixture directly. On macOS mktemp hands out /var/... paths that
# are themselves behind a symlink to /private/var, which makes the distinction show up there by
# accident; on Linux, where mktemp answers with a real /tmp path, it would not show up at all.
# The explicit symlink is what makes the case ask the question on both.
repo="$work/symlinked"
new_repo "$repo"
via="$work/reached-by-symlink"
ln -s "$(cd "$repo" && pwd -P)" "$via"
want="$(wt_path "$repo" 33)"

out="$(cd "$via" && "$WT" 33 through-symlink 2>/dev/null)" && code=0 || code=$?
listing="$(registry "$repo")"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && grep -qxF "worktree $out" <<<"$listing"; } \
  && ok || no "reached through a symlinked path: prints the resolved path git itself lists for the worktree (called from '$via', exit=$code want 0, stdout='$out' want '$want', git's registry $( grep -qxF "worktree $out" <<<"$listing" && echo "carries the line 'worktree $out'" || echo "carries no 'worktree $out' line; its worktree lines are:
$(grep '^worktree ' <<<"$listing")" ))"

# 13. the remote's default branch is ahead of the local one — the new branch is cut from the
# remote's tip, not from the stale local branch that happens to carry the default branch's name
# (issue #174).
#
# The local `main` lags `origin/main` by design here: pulling the primary clone while a conductor
# is live would change the scripts running under it, so the pull waits (#165). A run started in
# that window used to be built on a base already behind, and its PR then owed a rebase over
# everything that landed meanwhile — replayed one `refactor:` commit at a time, through whatever
# conflicts concurrent issues had left in the same files.
#
# The seed is case 6's upstream+clone pair with the two tips pulled apart afterwards: the clone is
# taken first, and only then does the upstream gain a commit. So at the moment of the call the
# clone's local `main` AND its `refs/remotes/origin/main` both sit at the old tip, and the only way
# to reach the new one is to go and fetch it. A script that read the remote-tracking ref without
# refreshing it would answer the same as one that read the local branch, and the case would not
# tell them apart.
#
# The assertion is the new worktree's HEAD, asked of git: it must be the upstream's current tip,
# not the tip the clone was taken at.
upstream="$work/ahead-upstream"
new_repo "$upstream"
clone="$work/ahead-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$upstream" commit -q --allow-empty -m "landed while the clone was busy" >/dev/null 2>&1
remote_tip="$(git_q "$upstream" rev-parse main)"
stale_tip="$(git_q "$clone" rev-parse main)"
want="$(wt_path "$clone" 35)"

out="$(cd "$clone" && "$WT" 35 from-remote-tip 2>/dev/null)" && code=0 || code=$?

tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$tip" == "$remote_tip" ]]; } \
  && ok || no "origin's default branch is ahead of the local one: cuts tdd/35-from-remote-tip from origin's tip (exit=$code want 0, stdout='$out' want '$want', tip='$tip' want origin's $remote_tip not the stale local main's $stale_tip)"

# 14. cutting from origin's tip costs the caller's own checkout nothing: the local default branch
# ref does not move and the main working tree is not touched (issue #174).
#
# Case 13 pins where the new branch is cut from; this one pins the price of getting there. The
# obvious way to reach the remote's tip is to pull the primary clone first, and that is exactly what
# must not happen: pulling it while a conductor is live changes the scripts running under it, which
# is why the pull waits in the first place (#165). `git fetch origin <default>` refreshes
# refs/remotes/origin/<default> and nothing else — no local branch ref moves, no file in the
# caller's checkout does — so the two requirements stop being in tension.
#
# The seed is case 13's, with the upstream's extra commit adding a *file* rather than being empty:
# the clone is taken first, so its local `main` is genuinely behind and a pull would have both a
# commit to move the ref to and a file to write into the tree. Without that gap a script that pulled
# and one that fetched would leave the same repository behind, and the case would prove nothing.
#
# Five things asserted together, because "unchanged" is not a property any one of them carries
# alone: refs/heads/main still at the tip the clone was taken at, the checkout still on `main` and
# still at that same commit, no tracked file modified, and the file only the remote carries still
# absent from the caller's checkout — the last being the half asked of the tree's contents rather
# than of refs, since a `checkout` and a `pull` leave different evidence.
upstream="$work/untouched-upstream"
new_repo "$upstream"
clone="$work/untouched-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
printf 'landed while the clone was busy\n' > "$upstream/landed.txt"
git_q "$upstream" add landed.txt >/dev/null 2>&1
git_q "$upstream" commit -q -m "landed while the clone was busy" >/dev/null 2>&1
remote_tip="$(git_q "$upstream" rev-parse main)"

main_before="$(git_q "$clone" rev-parse refs/heads/main)"
head_before="$(git_q "$clone" rev-parse HEAD)"
branch_before="$(git_q "$clone" branch --show-current)"
want="$(wt_path "$clone" 37)"

out="$(cd "$clone" && "$WT" 37 leave-the-clone-alone 2>/dev/null)" && code=0 || code=$?

main_after="$(git_q "$clone" rev-parse refs/heads/main)"
head_after="$(git_q "$clone" rev-parse HEAD)"
branch_after="$(git_q "$clone" branch --show-current)"
# --untracked-files=no: the worktree the script was asked to create lands at .tdd/wt/37 *inside*
# the fixture, which carries no .gitignore, so it shows up as untracked. That is the script's own
# output, not a change to the caller's checkout. A pull or a checkout shows up in tracked files.
dirty_after="$(git_q "$clone" status --porcelain --untracked-files=no)"

{ [[ "$code" == 0 ]] && [[ "$main_after" == "$main_before" ]] && [[ "$head_after" == "$head_before" ]] \
  && [[ "$branch_after" == "$branch_before" ]] && [[ -z "$dirty_after" ]] \
  && [[ ! -e "$clone/landed.txt" ]]; } \
  && ok || no "creating the issue branch leaves the local default branch ref and the caller's working tree untouched (exit=$code want 0, stdout='$out' want '$want', refs/heads/main='$main_after' want the clone's own $main_before not origin's $remote_tip, HEAD='$head_after' want '$head_before', current branch='$branch_after' want '$branch_before', tracked files $( [[ -z "$dirty_after" ]] && echo "clean, good" || echo "modified:
$dirty_after" ), landed.txt $( [[ -e "$clone/landed.txt" ]] && echo "was written into the caller's checkout" || echo "absent, good" ))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
