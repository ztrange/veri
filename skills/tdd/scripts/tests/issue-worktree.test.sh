#!/usr/bin/env bash
# Unit tests for scripts/issue-worktree.sh — the linked git worktree an issue branch lives
# in, so a conductor never drags the checkout it was invoked from off the default branch.
#
# Contract under test:
#   issue-worktree.sh <n> <slug>   creates/reuses <repo-root>/.tdd/wt/<n> on branch
#                                  tdd/<n>-<slug>, prints its absolute path, exit 0
#
# Run: scripts/tests/issue-worktree.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$HERE/../issue-worktree.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

make_repo() {
  mkdir -p "$1"
  new_repo -b main "$1" >/dev/null 2>&1
  git_q "$1" commit -q --allow-empty -m "initial" >/dev/null 2>&1
}

wt_path() { printf '%s\n' "$(cd "$1" && pwd -P)/.tdd/wt/$2"; }

registry() {
  git -C "$1" worktree list --porcelain 2>/dev/null
  git -C "$1" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null
}

linked_worktree() {
  local path="$(cd "$work" && pwd -P)/$2"
  git_q "$1" worktree add -q -b "$3" "$path" main >/dev/null 2>&1
  printf '%s\n' "$path"
}

ahead_pair() {
  upstream="$work/$1-upstream"
  clone="$work/$1-clone"
  make_repo "$upstream"
  git clone -q "$upstream" "$clone" >/dev/null 2>&1
  git_q "$upstream" commit -q --allow-empty -m "landed while the clone was busy" >/dev/null 2>&1
  remote_tip="$(git_q "$upstream" rev-parse main)"
  stale_tip="$(git_q "$clone" rev-parse main)"
}

repo="$work/fresh"
make_repo "$repo"
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
want="$(wt_path "$repo" 7)"

out="$(cd "$repo" && "$WT" 7 add-worktree 2>/dev/null)" && code=0 || code=$?

top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"
branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] \
  && [[ "$branch" == "tdd/7-add-worktree" ]] && [[ "$tip" == "$main_tip" ]]; } \
  && ok || no "fresh call: creates a worktree at .tdd/wt/7 on new branch tdd/7-add-worktree off the default branch and prints its path (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', branch='$branch' want 'tdd/7-add-worktree', tip='$tip' want main's $main_tip not side's $side_tip)"

repo="$work/again"
make_repo "$repo"
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

repo="$work/taken"
make_repo "$repo"
other="$(linked_worktree "$repo" taken-elsewhere tdd/11-collide)"
mine="$(wt_path "$repo" 11)"
before="$(registry "$repo")"

err="$(cd "$repo" && "$WT" 11 collide 2>&1 >/dev/null)" && code=0 || code=$?
after="$(registry "$repo")"

{ [[ "$code" == 2 ]] && [[ "$err" == *"$other"* ]] && [[ ! -e "$mine" ]] \
  && [[ "$after" == "$before" ]]; } \
  && ok || no "branch checked out elsewhere: exits 2 naming that worktree and touches nothing (exit=$code want 2, stderr='$err' want it to name '$other', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

repo="$work/remove-clean"
make_repo "$repo"
want="$(wt_path "$repo" 13)"
(cd "$repo" && "$WT" 13 done-with-this >/dev/null 2>&1)

(cd "$repo" && "$WT" --remove 13 >/dev/null 2>&1) && clean_code=0 || clean_code=$?
clean_after="$(registry "$repo")"

repo="$work/remove-dirty"
make_repo "$repo"
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

repo="$work/existing-branch"
make_repo "$repo"
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

upstream="$work/upstream-trunk"
make_repo "$upstream"
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

repo="$work/local-master"
make_repo "$repo"
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

repo="$work/no-default"
make_repo "$repo"
git_q "$repo" branch -m main trunk >/dev/null 2>&1
before="$(registry "$repo")"

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

repo="$work/from-linked"
make_repo "$repo"
linked="$(linked_worktree "$repo" from-linked-session session)"
want="$(wt_path "$repo" 27)"
nested="$(wt_path "$linked" 27)"

out="$(cd "$linked" && "$WT" 27 from-linked 2>/dev/null)" && code=0 || code=$?

top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] \
  && [[ ! -e "$nested" ]]; } \
  && ok || no "called from a linked worktree: creates and prints the main working tree's .tdd/wt/27, not one nested inside the caller (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', '$nested' $( [[ -e "$nested" ]] && echo "was created inside the linked worktree" || echo "absent, good" ))"

repo="$work/cross-caller"
make_repo "$repo"
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

repo="$work/remove-from-linked"
make_repo "$repo"
want="$(wt_path "$repo" 31)"
(cd "$repo" && "$WT" 31 remove-from-linked >/dev/null 2>&1)
linked="$(linked_worktree "$repo" remove-from-linked-session remove-session)"

(cd "$linked" && "$WT" --remove 31 >/dev/null 2>&1) && code=0 || code=$?
after="$(registry "$repo")"

{ [[ "$code" == 0 ]] && [[ "$after" != *"worktree $want"* ]] && [[ ! -e "$want" ]]; } \
  && ok || no "--remove from a linked worktree: removes the main working tree's .tdd/wt/31 (exit=$code want 0, '$want' $( [[ -e "$want" ]] && echo "still on disk" || echo "gone, good" ), still in git's registry: $( [[ "$after" == *"worktree $want"* ]] && echo yes || echo no ))"

repo="$work/symlinked"
make_repo "$repo"
via="$work/reached-by-symlink"
ln -s "$(cd "$repo" && pwd -P)" "$via"
want="$(wt_path "$repo" 33)"

out="$(cd "$via" && "$WT" 33 through-symlink 2>/dev/null)" && code=0 || code=$?
listing="$(registry "$repo")"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && grep -qxF "worktree $out" <<<"$listing"; } \
  && ok || no "reached through a symlinked path: prints the resolved path git itself lists for the worktree (called from '$via', exit=$code want 0, stdout='$out' want '$want', git's registry $( grep -qxF "worktree $out" <<<"$listing" && echo "carries the line 'worktree $out'" || echo "carries no 'worktree $out' line; its worktree lines are:
$(grep '^worktree ' <<<"$listing")" ))"

ahead_pair ahead
want="$(wt_path "$clone" 35)"

out="$(cd "$clone" && "$WT" 35 from-remote-tip 2>/dev/null)" && code=0 || code=$?

tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$tip" == "$remote_tip" ]]; } \
  && ok || no "origin's default branch is ahead of the local one: cuts tdd/35-from-remote-tip from origin's tip (exit=$code want 0, stdout='$out' want '$want', tip='$tip' want origin's $remote_tip not the stale local main's $stale_tip)"

upstream="$work/untouched-upstream"
make_repo "$upstream"
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
dirty_after="$(git_q "$clone" status --porcelain --untracked-files=no)"

{ [[ "$code" == 0 ]] && [[ "$main_after" == "$main_before" ]] && [[ "$head_after" == "$head_before" ]] \
  && [[ "$branch_after" == "$branch_before" ]] && [[ -z "$dirty_after" ]] \
  && [[ ! -e "$clone/landed.txt" ]]; } \
  && ok || no "creating the issue branch leaves the local default branch ref and the caller's working tree untouched (exit=$code want 0, stdout='$out' want '$want', refs/heads/main='$main_after' want the clone's own $main_before not origin's $remote_tip, HEAD='$head_after' want '$head_before', current branch='$branch_after' want '$branch_before', tracked files $( [[ -z "$dirty_after" ]] && echo "clean, good" || echo "modified:
$dirty_after" ), landed.txt $( [[ -e "$clone/landed.txt" ]] && echo "was written into the caller's checkout" || echo "absent, good" ))"

upstream="$work/no-tracking-upstream"
make_repo "$upstream"
clone="$work/no-tracking-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
want="$(wt_path "$clone" 39)"

out="$(cd "$clone" && "$WT" 39 no-upstream 2>/dev/null)" && code=0 || code=$?

tracks="$(git_q "$clone" for-each-ref --format='%(upstream:short)' refs/heads/tdd/39-no-upstream)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ -z "$tracks" ]]; } \
  && ok || no "the new issue branch has no upstream (exit=$code want 0, stdout='$out' want '$want', tdd/39-no-upstream's upstream=$( [[ -z "$tracks" ]] && echo "none, good" || echo "'$tracks' want none" ))"

upstream="$work/unreachable-upstream"
make_repo "$upstream"
clone="$work/unreachable-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
rm -rf "$upstream"
want="$(wt_path "$clone" 41)"
before="$(registry "$clone")"

errfile="$work/unreachable.err"
out="$(cd "$clone" && "$WT" 41 fetch-fails 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"
after="$(registry "$clone")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ "$err" == *"fetch"* ]] && [[ ! -e "$want" ]] \
  && [[ "$after" == "$before" ]]; } \
  && ok || no "the fetch fails: exits 2 with a diagnostic on stderr, nothing on stdout, and no worktree or branch created (exit=$code want 2, stdout='$out' want empty, stderr='$err' want it to name the 'fetch', '$want' $( [[ -e "$want" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

repo="$work/no-remote"
make_repo "$repo"
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
want="$(wt_path "$repo" 43)"

errfile="$work/no-remote.err"
out="$(cd "$repo" && "$WT" 43 no-remote 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/43-no-remote" ]] \
  && [[ "$tip" == "$main_tip" ]] && [[ -z "$err" ]]; } \
  && ok || no "no remote at all: cuts tdd/43-no-remote from the local main without going to a remote (exit=$code want 0, stdout='$out' want '$want', branch='$branch' want 'tdd/43-no-remote', tip='$tip' want the local main's $main_tip not side's $side_tip, stderr $( [[ -z "$err" ]] && echo "silent, good" || echo "carried:
$err" ))"

upstream="$work/resume-no-fetch-upstream"
make_repo "$upstream"
clone="$work/resume-no-fetch-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$clone" switch -q -c tdd/45-resume-no-fetch >/dev/null 2>&1
git_q "$clone" commit -q --allow-empty -m "work from the previous run" >/dev/null 2>&1
branch_tip="$(git_q "$clone" rev-parse tdd/45-resume-no-fetch)"
git_q "$clone" switch -q main >/dev/null 2>&1
main_tip="$(git_q "$clone" rev-parse main)"
rm -rf "$upstream"
want="$(wt_path "$clone" 45)"

errfile="$work/resume-no-fetch.err"
out="$(cd "$clone" && "$WT" 45 resume-no-fetch 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/45-resume-no-fetch" ]] \
  && [[ "$tip" == "$branch_tip" ]] && [[ -z "$err" ]]; } \
  && ok || no "resume onto an existing issue branch with the remote unreachable: checks it out as it is without going to the remote (exit=$code want 0, stdout='$out' want '$want', branch='$branch' want 'tdd/45-resume-no-fetch', tip='$tip' want the existing branch's $branch_tip not main's $main_tip, stderr $( [[ -z "$err" ]] && echo "silent, good" || echo "carried:
$err" ))"

SKILL="$HERE/../../SKILL.md"

entry="$(awk '
  !in_e && index($0, "- `$S/issue-worktree.sh <n> <slug>`") == 1 { in_e = 1; print; next }
  in_e && /^([-#]|[0-9]+\.)/ { exit }
  in_e { print }' "$SKILL" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' ')"

says() {
  local complaint="$1" re="$2"
  [[ "$entry" =~ $re ]] || problems="$problems; $complaint"
}

problems=""
if [[ -z "${entry// /}" ]]; then
  problems="; no bullet for '\$S/issue-worktree.sh <n> <slug>' found in $SKILL — what the conductor is told about the base could not be established"
else
  says "nothing names a fetch — a conductor reading it cannot tell the base is refreshed at all" \
    'fetch'
  says "the base is still described as the default branch, which reads as the local one" \
    'origin/<[a-z-]+>|origin/(main|master|the default)|remote.s (tip|default)|remote default branch|tip of (the )?(remote|origin)'
  says "nothing says the local default branch is stale, so the fetch reads as belt and braces" \
    'stale|behind|lags?|out of date'
fi
[[ -z "$problems" ]] \
  && ok || no "SKILL.md's issue-worktree.sh entry says the branch is cut from the freshly fetched remote default branch and why the local one is not used (${problems#; }; text read: '$entry')"

problems=""
if [[ -z "${entry// /}" ]]; then
  problems="; no bullet for '\$S/issue-worktree.sh <n> <slug>' found in $SKILL — how the default branch is named could not be established"
else
  says "nothing says the default branch's name is resolved from the remote when refs/remotes/origin/HEAD is absent" \
    'refs/remotes/origin/head[^.]*(absent|missing)[^.]*(ls-remote|from the remote|remote itself)|(ls-remote|from the remote|remote itself)[^.]*refs/remotes/origin/head[^.]*(absent|missing)'
  says "nothing says the refusal when the remote's default cannot be resolved names refs/remotes/origin/HEAD" \
    'nam(e|es|ing)[^.]{0,40}refs/remotes/origin/head'
  says "nothing says the local main/master fallback holds only when there is no origin remote" \
    'main/master[^.]*no origin remote|no origin remote[^.]*main/master'
  [[ "$entry" =~ records[[:space:]]+no[[:space:]]+origin/head ]] &&
    problems="$problems; it still says a local main/master supplies the name when the clone records no origin/HEAD — the guess #865 removes"
fi
[[ -z "$problems" ]] \
  && ok || no "#865: SKILL.md's issue-worktree.sh entry says the default branch's name is resolved from the remote when refs/remotes/origin/HEAD is absent, the refusal names that ref when it cannot be, and the local main/master fallback holds only with no origin remote (${problems#; }; text read: '$entry')"

ahead_pair no-origin-head
git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD >/dev/null 2>&1
want="$(wt_path "$clone" 47)"

origin_head="$(git_q "$clone" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)"

out="$(cd "$clone" && "$WT" 47 no-origin-head 2>/dev/null)" && code=0 || code=$?

tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ -z "$origin_head" ]] && [[ "$tip" == "$remote_tip" ]]; } \
  && ok || no "an origin remote but no refs/remotes/origin/HEAD: cuts tdd/47-no-origin-head from origin's freshly fetched tip (exit=$code want 0, stdout='$out' want '$want', the clone's refs/remotes/origin/HEAD $( [[ -z "$origin_head" ]] && echo "absent as seeded, good" || echo "was '$origin_head' — the seed did not remove it, so this case cannot tell the arms apart" ), tip='$tip' want origin's $remote_tip not the stale local main's $stale_tip)"

upstream="$work/develop-default-upstream"
make_repo "$upstream"
main_only_tip="$(git_q "$upstream" rev-parse main)"
git_q "$upstream" switch -q -c develop >/dev/null 2>&1
git_q "$upstream" commit -q --allow-empty -m "work on the default branch" >/dev/null 2>&1
develop_tip="$(git_q "$upstream" rev-parse develop)"
clone="$work/develop-default-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$clone" branch main refs/remotes/origin/main >/dev/null 2>&1
git_q "$clone" config remote.origin.followRemoteHEAD never >/dev/null 2>&1
git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD >/dev/null 2>&1
want="$(wt_path "$clone" 865)"

origin_head="$(git_q "$clone" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)"
local_main="$(git_q "$clone" rev-parse --verify --quiet refs/heads/main 2>/dev/null)"

errfile="$work/develop-default.err"
out="$(cd "$clone" && "$WT" 865 develop-default 2>"$errfile")" && code=0 || code=$?

tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ -z "$origin_head" ]] && [[ "$local_main" == "$main_only_tip" ]] && [[ "$tip" == "$develop_tip" ]]; } \
  && ok || no "#865: an origin remote whose default is develop, a local main, and no refs/remotes/origin/HEAD: cuts tdd/865-develop-default from the remote's own default, not the guessed main (exit=$code want 0, the clone's refs/remotes/origin/HEAD='$origin_head' want absent, local main='$local_main' want $main_only_tip, tip='$tip' want origin/develop's $develop_tip not main's $main_only_tip, stderr='$(cat "$errfile")')"

upstream="$work/unresolvable-default-upstream"
make_repo "$upstream"
clone="$work/unresolvable-default-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$clone" config remote.origin.followRemoteHEAD never >/dev/null 2>&1
git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD >/dev/null 2>&1
git_q "$clone" remote set-url origin "$work/unresolvable-default-gone" >/dev/null 2>&1
want="$(wt_path "$clone" 866)"

origin_head="$(git_q "$clone" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)"
before="$(registry "$clone")"

errfile="$work/unresolvable-default.err"
out="$(cd "$clone" && "$WT" 866 unresolvable-default 2>"$errfile")" && code=0 || code=$?
after="$(registry "$clone")"

{ [[ "$code" == 2 ]] && [[ -z "$origin_head" ]] && grep -F 'refs/remotes/origin/HEAD' "$errfile" >/dev/null \
  && [[ ! -e "$want" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "#865: an origin remote whose default cannot be resolved and no refs/remotes/origin/HEAD: exits 2 naming refs/remotes/origin/HEAD and creates no worktree (exit=$code want 2, the clone's refs/remotes/origin/HEAD='$origin_head' want absent, stderr='$(cat "$errfile")' want it to name refs/remotes/origin/HEAD, $want $( [[ -e "$want" ]] && echo "exists" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ), stdout='$out')"

repo="$work/no-origin-local-main"
make_repo "$repo"
main_tip="$(git_q "$repo" rev-parse main)"
git_q "$repo" switch -q -c side >/dev/null 2>&1
git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
side_tip="$(git_q "$repo" rev-parse side)"
want="$(wt_path "$repo" 867)"

remotes="$(git_q "$repo" remote 2>/dev/null)"

errfile="$work/no-origin-local-main.err"
out="$(cd "$repo" && "$WT" 867 no-origin-local-main 2>"$errfile")" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ -z "$remotes" ]] && [[ "$out" == "$want" ]] \
  && [[ "$branch" == "tdd/867-no-origin-local-main" ]] && [[ "$tip" == "$main_tip" ]]; } \
  && ok || no "#865: no origin remote at all and a local main: still falls back to the local main as the base (exit=$code want 0, remotes='$remotes' want none, stdout='$out' want '$want', branch='$branch' want 'tdd/867-no-origin-local-main', tip='$tip' want main's $main_tip not side's $side_tip, stderr='$(cat "$errfile")')"

upstream="$work/remote-only-upstream"
make_repo "$upstream"
git_q "$upstream" switch -q -c tdd/49-remote-only >/dev/null 2>&1
mkdir -p "$upstream/.tdd"
printf -- '- [x] 1. the step the previous run finished\n' > "$upstream/.tdd/issue-49.md"
git_q "$upstream" add .tdd/issue-49.md >/dev/null 2>&1
git_q "$upstream" commit -q -m "plan: the previous run's ledger" >/dev/null 2>&1
ledger_want="$(cat "$upstream/.tdd/issue-49.md")"
remote_branch_tip="$(git_q "$upstream" rev-parse tdd/49-remote-only)"
git_q "$upstream" switch -q main >/dev/null 2>&1
clone="$work/remote-only-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
main_tip="$(git_q "$clone" rev-parse main)"
want="$(wt_path "$clone" 49)"

local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/49-remote-only && echo present || echo absent)"
remote_ref="$(git_q "$clone" rev-parse --verify --quiet refs/remotes/origin/tdd/49-remote-only 2>/dev/null)"

out="$(cd "$clone" && "$WT" 49 remote-only 2>/dev/null)" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"
ledger_got="$(cat "$want/.tdd/issue-49.md" 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$local_ref" == absent ]] && [[ "$remote_ref" == "$remote_branch_tip" ]] \
  && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/49-remote-only" ]] \
  && [[ "$tip" == "$remote_branch_tip" ]] && [[ "$ledger_got" == "$ledger_want" ]]; } \
  && ok || no "a branch that exists only on the remote: checked out at its own tip with its ledger present, not re-cut from the default branch (exit=$code want 0, the clone's refs/heads/tdd/49-remote-only=$local_ref want absent, its refs/remotes/origin/tdd/49-remote-only='$remote_ref' want $remote_branch_tip, stdout='$out' want '$want', branch='$branch' want 'tdd/49-remote-only', tip='$tip' want the remote branch's $remote_branch_tip not main's $main_tip, .tdd/issue-49.md $( [[ "$ledger_got" == "$ledger_want" ]] && echo "present, good" || echo "read back as '$ledger_got' want '$ledger_want'" ))"

upstream="$work/tracks-upstream"
make_repo "$upstream"
git_q "$upstream" switch -q -c tdd/51-tracks >/dev/null 2>&1
git_q "$upstream" commit -q --allow-empty -m "the previous run's work" >/dev/null 2>&1
git_q "$upstream" switch -q main >/dev/null 2>&1
clone="$work/tracks-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
want="$(wt_path "$clone" 51)"

local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/51-tracks && echo present || echo absent)"

out="$(cd "$clone" && "$WT" 51 tracks 2>/dev/null)" && code=0 || code=$?

tracks="$(git_q "$clone" for-each-ref --format='%(upstream:short)' refs/heads/tdd/51-tracks)"

{ [[ "$code" == 0 ]] && [[ "$local_ref" == absent ]] && [[ "$out" == "$want" ]] \
  && [[ "$tracks" == "origin/tdd/51-tracks" ]]; } \
  && ok || no "a worktree made for a remote-only branch tracks that remote branch (exit=$code want 0, the clone's refs/heads/tdd/51-tracks=$local_ref want absent before the call, stdout='$out' want '$want', tdd/51-tracks's upstream=$( [[ -n "$tracks" ]] && echo "'$tracks'" || echo "none" ) want 'origin/tdd/51-tracks')"

upstream="$work/local-ahead-upstream"
make_repo "$upstream"
git_q "$upstream" switch -q -c tdd/53-local-ahead >/dev/null 2>&1
git_q "$upstream" commit -q --allow-empty -m "the tip the previous run pushed" >/dev/null 2>&1
remote_branch_tip="$(git_q "$upstream" rev-parse tdd/53-local-ahead)"
git_q "$upstream" switch -q main >/dev/null 2>&1
clone="$work/local-ahead-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
git_q "$clone" switch -q -c tdd/53-local-ahead origin/tdd/53-local-ahead >/dev/null 2>&1
git_q "$clone" commit -q --allow-empty -m "committed by the last run and never pushed" >/dev/null 2>&1
local_branch_tip="$(git_q "$clone" rev-parse tdd/53-local-ahead)"
git_q "$clone" switch -q main >/dev/null 2>&1
want="$(wt_path "$clone" 53)"

local_ref="$(git_q "$clone" rev-parse --verify --quiet refs/heads/tdd/53-local-ahead 2>/dev/null)"
remote_ref="$(git_q "$clone" rev-parse --verify --quiet refs/remotes/origin/tdd/53-local-ahead 2>/dev/null)"

out="$(cd "$clone" && "$WT" 53 local-ahead 2>/dev/null)" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$local_ref" == "$local_branch_tip" ]] && [[ "$remote_ref" == "$remote_branch_tip" ]] \
  && [[ "$local_branch_tip" != "$remote_branch_tip" ]] && [[ "$out" == "$want" ]] \
  && [[ "$branch" == "tdd/53-local-ahead" ]] && [[ "$tip" == "$local_branch_tip" ]]; } \
  && ok || no "a local branch ahead of its remote: checked out at its own tip, not rewound to the remote's (exit=$code want 0, the clone's refs/heads/tdd/53-local-ahead='$local_ref' want the local tip $local_branch_tip, its refs/remotes/origin/tdd/53-local-ahead='$remote_ref' want the remote tip $remote_branch_tip $( [[ "$local_branch_tip" != "$remote_branch_tip" ]] && echo "— they differ, good" || echo "— the seed left them equal, so this case cannot tell the arms apart" ), stdout='$out' want '$want', branch='$branch' want 'tdd/53-local-ahead', tip='$tip' want the local branch's $local_branch_tip not the remote's $remote_branch_tip)"

upstream="$work/neither-upstream"
make_repo "$upstream"
git_q "$upstream" switch -q -c tdd/99-some-other-run >/dev/null 2>&1
git_q "$upstream" commit -q --allow-empty -m "another issue's run, pushed" >/dev/null 2>&1
other_tip="$(git_q "$upstream" rev-parse tdd/99-some-other-run)"
git_q "$upstream" switch -q main >/dev/null 2>&1
clone="$work/neither-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
main_tip="$(git_q "$clone" rev-parse main)"
want="$(wt_path "$clone" 55)"

local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/55-neither && echo present || echo absent)"
remote_ref="$(git_q "$clone" show-ref --verify --quiet refs/remotes/origin/tdd/55-neither && echo present || echo absent)"

out="$(cd "$clone" && "$WT" 55 neither 2>/dev/null)" && code=0 || code=$?

branch="$(git -C "$want" branch --show-current 2>/dev/null)"
tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

{ [[ "$code" == 0 ]] && [[ "$local_ref" == absent ]] && [[ "$remote_ref" == absent ]] \
  && [[ "$out" == "$want" ]] && [[ "$branch" == "tdd/55-neither" ]] \
  && [[ "$tip" == "$main_tip" ]]; } \
  && ok || no "a name in neither namespace, in a repo that has a remote: still cut from the default branch (exit=$code want 0, the clone's refs/heads/tdd/55-neither=$local_ref and refs/remotes/origin/tdd/55-neither=$remote_ref want both absent, stdout='$out' want '$want', branch='$branch' want 'tdd/55-neither', tip='$tip' want the default branch's $main_tip — not the other remote branch tdd/99-some-other-run's $other_tip)"

repo="$work/live-holder"
make_repo "$repo"
live="$(wt_path "$repo" 61)"

first="$(cd "$repo" && "$WT" 61 live-run 2>/dev/null)" && first_code=0 || first_code=$?
mkdir -p "$live/.tdd"
printf '%s\n' "$$" > "$live/.tdd/conductor.pid"
before="$(registry "$repo")"

errfile="$work/live-holder.err"
out="$(cd "$repo" && "$WT" 61 live-run 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"
after="$(registry "$repo")"

{ [[ "$first_code" == 0 ]] && [[ "$first" == "$live" ]] && [[ "$code" == 2 ]] && [[ -z "$out" ]] \
  && [[ "$err" == *"$$"* ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "a second call while the conductor that made the worktree is still alive: exits 2 naming the holder and prints no path (seed: first call exit=$first_code want 0, stdout='$first' want '$live'; second call exit=$code want 2, stdout='$out' want empty, stderr='$err' want it to name the live pid $$, git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo "changed:
--- before
$before
--- after
$after" ))"

repo="$work/non-utf8-pid"
make_repo "$repo"
want="$(wt_path "$repo" 965)"

first="$(cd "$repo" && "$WT" 965 non-utf8 2>/dev/null)" && first_code=0 || first_code=$?
mkdir -p "$want/.tdd"
printf '\xff\xfe\n' > "$want/.tdd/conductor.pid"

errfile="$work/non-utf8-pid.err"
out="$(cd "$repo" && "$WT" 965 non-utf8 2>"$errfile")" && code=0 || code=$?
err="$(cat "$errfile")"

{ [[ "$first_code" == 0 ]] && [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ -z "$err" ]]; } \
  && ok || no "#965: a second call for a registered worktree whose .tdd/conductor.pid holds the bytes \\xff\\xfe\\n: prints the path, exits 0 and prints nothing on stderr (seed: first call exit=$first_code want 0, stdout='$first'; second call exit=$code want 0, stdout='$out' want '$want', stderr='$err' want empty)"

repo="$work/seeded-log"
make_repo "$repo"
seeded="$(wt_path "$repo" 62)"
mkdir -p "$seeded/.tdd"
line='{"event": "skill-repin", "commit": "0123456"}'
printf '%s\n' "$line" > "$seeded/.tdd/events.jsonl"

errfile="$work/seeded-log.err"
out="$(cd "$repo" && "$WT" 62 seeded 2>"$errfile")" && code=0 || code=$?
top="$(cd "$seeded" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null || true)"
log="$(cat "$seeded/.tdd/events.jsonl" 2>/dev/null || true)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$seeded" ]] && [[ "$top" == "$seeded" ]] && [[ "$log" == *"$line"* ]]; } \
  && ok || no "a path holding only a seeded .tdd/events.jsonl: the worktree is made there and the log survives (exit=$code want 0, stdout='$out' want '$seeded', git toplevel there='$top' want '$seeded', log='$log' want it to hold '$line', stderr='$(cat "$errfile")')"

usage_line="usage: issue-worktree.sh <n> <slug> | --remove <n>"
problems=""
for args in "" "270" "--remove" "'' x"; do
  eval "set -- $args"
  errfile="$work/usage.err"
  out="$(cd "$work" && "$WT" "$@" 2>"$errfile")" && code=0 || code=$?
  err="$(cat "$errfile")"
  [[ "$code" == 2 ]] || problems+="; ($args) exit=$code want 2"
  [[ -z "$out" ]] || problems+="; ($args) stdout='$out' want empty"
  [[ "$err" == "$usage_line" ]] || problems+="; ($args) stderr='$err' want exactly '$usage_line'"
done
set --
{ [[ -z "$problems" ]]; } \
  && ok || no "a bad argument list — none, 270 alone, --remove alone, an empty first argument — exits 2 with nothing on stdout and stderr exactly the usage line (${problems#; })"

repo="$work/not-a-number"
make_repo "$repo"
before="$(registry "$repo")"
problems=""
for n in abc 0 -3 7a ../escape; do
  errfile="$work/not-a-number.err"
  out="$(cd "$repo" && "$WT" "$n" slug 2>"$errfile")" && code=0 || code=$?
  err="$(cat "$errfile")"
  [[ "$code" == 2 ]] || problems+="; ($n) exit=$code want 2"
  [[ -z "$out" ]] || problems+="; ($n) stdout='$out' want empty"
  [[ "$err" == "$usage_line" ]] || problems+="; ($n) stderr='$err' want exactly '$usage_line'"
done
after="$(registry "$repo")"
leftover="$(cd "$repo" && ls -A .tdd 2>/dev/null || true)"
[[ "$after" == "$before" ]] || problems+="; git's worktree+branch registry changed:
--- before
$before
--- after
$after"
[[ -z "$leftover" ]] || problems+="; .tdd holds '$leftover' want nothing created"
{ [[ -z "$problems" ]]; } \
  && ok || no "#819: an <n> that is not a positive whole number — abc, 0, -3, 7a, ../escape — exits 2 with the usage line on stderr and creates no worktree and no branch (${problems#; })"

repo="$work/remove-not-a-number"
make_repo "$repo"
victim="$(cd "$repo" && pwd -P)/.claude/worktrees/victim"
git_q "$repo" worktree add -q -b victim "$victim" main >/dev/null 2>&1
(cd "$repo" && "$WT" 5 held >/dev/null 2>&1)
before="$(registry "$repo")"
problems=""
for n in abc 0 -3 ../../.claude/worktrees/victim; do
  errfile="$work/remove-not-a-number.err"
  out="$(cd "$repo" && "$WT" --remove "$n" 2>"$errfile")" && code=0 || code=$?
  err="$(cat "$errfile")"
  [[ "$code" == 2 ]] || problems+="; ($n) exit=$code want 2"
  [[ -z "$out" ]] || problems+="; ($n) stdout='$out' want empty"
  [[ "$err" == "$usage_line" ]] || problems+="; ($n) stderr='$err' want exactly '$usage_line'"
done
after="$(registry "$repo")"
[[ "$after" == "$before" ]] || problems+="; git's worktree+branch registry changed:
--- before
$before
--- after
$after"
[[ -d "$victim" ]] || problems+="; the clean worktree at $victim was removed"
{ [[ -z "$problems" ]]; } \
  && ok || no "#819: --remove given an <n> that is not a positive whole number — abc, 0, -3, ../../.claude/worktrees/victim — exits 2 with the usage line on stderr and removes no worktree (${problems#; })"

repo="$work/skill-link-caller"
make_repo "$repo"
skill_link="$work/skill-link"
ln -s "$(cd "$HERE/../.." && pwd -P)" "$skill_link"
want="$(wt_path "$repo" 34)"
errfile="$work/skill-link.err"

out="$(cd "$repo" && "$skill_link/scripts/issue-worktree.sh" 34 via-skill-link 2>"$errfile")" && code=0 || code=$?
top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null || true)"
branch="$(git -C "$want" branch --show-current 2>/dev/null || true)"

{ [[ "$code" == 0 ]] && [[ "$out" == "$want" ]] && [[ "$top" == "$want" ]] && [[ "$branch" == "tdd/34-via-skill-link" ]]; } \
  && ok || no "run through a symlink to the skill directory from another repository: prints that repository's .tdd/wt/34 and creates the worktree there, as when run in place (exit=$code want 0, stdout='$out' want '$want', toplevel='$top' want '$want', branch='$branch' want 'tdd/34-via-skill-link', stderr='$(cat "$errfile")')"

repo="$work/pinned-scratch"
make_repo "$repo"
decoy="$work/decoy"
make_repo "$decoy"
mutant="$decoy/skills/tdd/scripts"
mkdir -p "$mutant"
cp -R "$HERE/../veri" "$mutant/veri"
awk '/^exec python3/ { print "cd \"$(dirname \"$0\")\"" } { print }' "$WT" > "$mutant/issue-worktree.sh"
chmod +x "$mutant/issue-worktree.sh"
before="$(registry "$decoy")"
errfile="$work/pinned-scratch.err"

out="$(cd "$repo" && "$mutant/issue-worktree.sh" 41 escaped 2>"$errfile")" && code=0 || code=$?
after="$(registry "$decoy")"

problems=""
[[ "$after" == "$before" ]] || problems+="; the decoy repository's worktree+branch registry changed:
--- before
$before
--- after
$after"
[[ ! -e "$decoy/.tdd/wt/41" ]] || problems+="; $decoy/.tdd/wt/41 was created"
[[ "$code" != 0 || "$out" != *"$decoy"* ]] || problems+="; exit=0 naming '$out', want the case to fail on a subject that resolved the decoy repository"
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: an issue-worktree.sh that resolves its main tree from its own directory, not the suite's scratch repository, creates no worktree, branch or .tdd/wt entry outside that repository (${problems#; })"

finish
