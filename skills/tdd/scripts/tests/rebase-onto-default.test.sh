#!/usr/bin/env bash
# Tests for scripts/rebase-onto-default.sh — the rebase a run owes before its PR is marked
# ready, when the default branch moved while the run worked.
#
# Contract under test:
#   rebase-onto-default.sh, run in a worktree whose branch already contains origin/<default>
#                       → exit 3, "nothing to do": there is no rebase to make.
#                       → nothing on stdout.
#                       → HEAD and the working tree exactly what they were before the call.
#   rebase-onto-default.sh, run on a branch behind origin/<default> with no conflict
#                       → rebases onto it, exit 0.
#                       → stdout is two lines: the pre-rebase sha, then the onto sha.
#                       → HEAD contains origin/<default>, with the branch's own commits on top.
#   rebase-onto-default.sh, run on a branch whose rebase onto origin/<default> conflicts
#                       → aborts the rebase, exit 1.
#                       → stdout is the conflicting files, one per line.
#                       → HEAD at the pre-rebase sha, a clean tree, and no rebase in progress.
#
# Run: scripts/tests/rebase-onto-default.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
REBASE="$HERE/../rebase-onto-default.sh"
work="$(scratch_dir)"

report_stderr() {
  local before="$fail"
  report "$1"
  if [[ "$fail" -gt "$before" && -s "${stderr_file:-/dev/null}" ]]; then
    sed 's/^/    stderr: /' "$stderr_file"
  fi
  return 0
}

stderr_file=/dev/null

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

identify() { git -C "$1" config user.name veri && git -C "$1" config user.email veri@example.test; }

origin_fixture() {
  local dir="$1"
  mkdir -p "$dir"
  new_repo --bare -b main "$dir/origin.git" >/dev/null 2>&1
  new_repo -b main "$dir/seed" >/dev/null 2>&1
  echo "base" > "$dir/seed/file.txt"
  git_q "$dir/seed" add -A >/dev/null 2>&1
  git_q "$dir/seed" commit -q -m "initial" >/dev/null 2>&1
  git_q "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
  git clone -q "$dir/origin.git" "$dir/clone" >/dev/null 2>&1
  identify "$dir/seed"
  identify "$dir/clone"
}

run_branch() {
  local repo="$1"
  git_q "$repo" checkout -q -b tdd/1-a-run >/dev/null 2>&1
  echo "the run's work" > "$repo/work.txt"
  git_q "$repo" add -A >/dev/null 2>&1
  git_q "$repo" commit -q -m "feat: a step's green commit (#1)" >/dev/null 2>&1
}

advance_origin() {
  local dir="$1"
  git_q "$dir/seed" add -A >/dev/null 2>&1
  git_q "$dir/seed" commit -q -m "feat: another run merged (#2)" >/dev/null 2>&1
  git_q "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
  git -C "$dir/clone" fetch -q origin >/dev/null 2>&1
}

behind_branch() {
  local dir="$1"
  origin_fixture "$dir"
  run_branch "$dir/clone"
  echo "another run's work" > "$dir/seed/other.txt"
  advance_origin "$dir"
}

conflicting_branch() {
  local dir="$1" repo="$1/clone"
  run_branch "$repo"
  echo "the run's edit" > "$repo/file.txt"
  git_q "$repo" commit -q -a --amend --no-edit >/dev/null 2>&1
  echo "another run's edit" > "$dir/seed/file.txt"
  echo "another run's work" > "$dir/seed/work.txt"
  advance_origin "$dir"
}

expect_conflict_aborted() {
  local repo="$1" pre="$2" rc="$3" out="$4" got_files want_files head_after d
  [[ "$rc" -eq 1 ]] || problems+=("exit: want 1, got $rc")
  got_files="$(printf '%s\n' "$out" | LC_ALL=C sort)"
  want_files="$(printf 'file.txt\nwork.txt')"
  [[ "$got_files" == "$want_files" ]] ||
    problems+=("stdout: want the conflicting files $(printf '%q' "$want_files"), got $(printf '%q' "$out")")
  head_after="$(git -C "$repo" rev-parse HEAD)"
  [[ "$head_after" == "$pre" ]] || problems+=("HEAD: want the pre-rebase sha $pre, got $head_after")
  for d in rebase-merge rebase-apply; do
    [[ ! -e "$(git -C "$repo" rev-parse --path-format=absolute --git-path "$d")" ]] ||
      problems+=("rebase: want none in progress, found $d")
  done
}

expect_refused() {
  local repo="$1" stdout="$2" why="$3" head_before rc head_after
  head_before="$(git -C "$repo" rev-parse HEAD)"
  (cd "$repo" && bash "$REBASE" > "$stdout" 2>"$stderr_file")
  rc=$?
  [[ "$rc" -eq 2 ]] || problems+=("exit: want 2, got $rc")
  [[ ! -s "$stdout" ]] || problems+=("stdout: want empty, got $(printf '%q' "$(cat "$stdout"; echo .)")")
  head_after="$(git -C "$repo" rev-parse HEAD)"
  [[ "$head_after" == "$head_before" ]] || problems+=("HEAD: want it unchanged at $head_before${why}, got $head_after")
}

name="rebase-onto-default.test.sh: a branch already containing origin/<default> exits 3 with empty stdout and HEAD and tree unchanged"
problems=()
dir="$work/up-to-date"
stderr_file="$work/up-to-date.err"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
head_before="$(git -C "$repo" rev-parse HEAD)"
status_before="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
[[ "$rc" -eq 3 ]] || problems+=("exit: want 3, got $rc")
[[ -z "$out" ]] || problems+=("stdout: want empty, got $(printf '%q' "$out")")
head_after="$(git -C "$repo" rev-parse HEAD)"
[[ "$head_after" == "$head_before" ]] || problems+=("HEAD: want it unchanged at $head_before, got $head_after")
status_after="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
[[ "$status_after" == "$status_before" ]] ||
  problems+=("working tree: want it unchanged at $(printf '%q' "$status_before"), got $(printf '%q' "$status_after")")
report_stderr "$name"

name="rebase-onto-default.test.sh: a branch behind origin/<default> with no conflict rebases onto it, exits 0, prints the pre-rebase and onto shas, and keeps its own commit on top"
problems=()
dir="$work/behind"
stderr_file="$work/behind.err"
behind_branch "$dir"
repo="$dir/clone"
pre="$(git -C "$repo" rev-parse HEAD)"
onto="$(git -C "$repo" rev-parse origin/main)"
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
[[ "$rc" -eq 0 ]] || problems+=("exit: want 0, got $rc")
want_out="$(printf '%s\n%s' "$pre" "$onto")"
[[ "$out" == "$want_out" ]] ||
  problems+=("stdout: want $(printf '%q' "$want_out"), got $(printf '%q' "$out")")
git -C "$repo" merge-base --is-ancestor "$onto" HEAD ||
  problems+=("HEAD: want it to contain origin/main $onto, it does not")
parent="$(git -C "$repo" rev-parse HEAD~1 2>/dev/null)"
[[ "$parent" == "$onto" ]] || problems+=("HEAD~1: want the onto sha $onto, got $parent")
subject="$(git -C "$repo" log -1 --format=%s HEAD)"
[[ "$subject" == "feat: a step's green commit (#1)" ]] ||
  problems+=("HEAD subject: want the branch's own commit, got $(printf '%q' "$subject")")
report_stderr "$name"

name="rebase-onto-default.test.sh: a rebase that conflicts is aborted, exits 1, leaves HEAD at the pre-rebase sha with a clean tree and no rebase in progress, and prints the conflicting files one per line"
problems=()
dir="$work/conflict"
stderr_file="$work/conflict.err"
origin_fixture "$dir"
repo="$dir/clone"
conflicting_branch "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
expect_conflict_aborted "$repo" "$pre" "$rc" "$out"
status_after="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
[[ -z "$status_after" ]] || problems+=("working tree: want clean, got $(printf '%q' "$status_after")")
report_stderr "$name"

name="rebase-onto-default.test.sh: in a repo configured with rebase.backend=apply, a rebase that conflicts is still aborted, exits 1, prints the conflicting files, and leaves no rebase in progress"
problems=()
dir="$work/conflict-apply"
stderr_file="$work/conflict-apply.err"
origin_fixture "$dir"
repo="$dir/clone"
git -C "$repo" config rebase.backend apply
conflicting_branch "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
expect_conflict_aborted "$repo" "$pre" "$rc" "$out"
report_stderr "$name"

name="rebase-onto-default.test.sh: when a fetch succeeds without refreshing origin/<default>, exits 2 with nothing on stdout and never rebases onto the stale local copy"
problems=()
dir="$work/fetch-skips-default"
stderr_file="$work/fetch-skips-default.err"
behind_branch "$dir"
repo="$dir/clone"
git -C "$repo" config remote.origin.fetch '+refs/heads/tdd/*:refs/remotes/origin/tdd/*'
echo "a third run's work" > "$dir/seed/third.txt"
advance_origin "$dir"
expect_refused "$repo" "$dir/stdout" ", not rebased onto the stale origin/main"
report_stderr "$name"

name="rebase-onto-default.test.sh: with no refs/remotes/origin/HEAD and a remote whose default branch cannot be resolved, exits 2 naming refs/remotes/origin/HEAD, HEAD unchanged and no rebase started (#865)"
problems=()
dir="$work/no-origin-head"
stderr_file="$work/no-origin-head.err"
behind_branch "$dir"
repo="$dir/clone"
git -C "$repo" config remote.origin.followRemoteHEAD never
git -C "$repo" remote set-head origin -d >/dev/null 2>&1
git -C "$dir/origin.git" symbolic-ref HEAD refs/heads/no-such-branch
expect_refused "$repo" "$dir/stdout" ", with no default branch to rebase onto"
grep -F 'refs/remotes/origin/HEAD' "$stderr_file" > /dev/null ||
  problems+=("stderr: want a line naming refs/remotes/origin/HEAD, got $(printf '%q' "$(cat "$stderr_file")")")
for d in rebase-merge rebase-apply; do
  [[ ! -e "$(git -C "$repo" rev-parse --path-format=absolute --git-path "$d")" ]] ||
    problems+=("rebase: want none started, found $d")
done
report_stderr "$name"

name="rebase-onto-default.test.sh: with no refs/remotes/origin/HEAD and a remote that names its default branch, a branch already containing it exits 3 and a conflicting rebase exits 1 naming the conflicting files, as when the ref is set (#865)"
problems=()
dir="$work/no-origin-head-up-to-date"
stderr_file="$work/no-origin-head-up-to-date.err"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
git -C "$repo" config remote.origin.followRemoteHEAD never
git -C "$repo" remote set-head origin -d >/dev/null 2>&1
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
[[ "$rc" -eq 3 ]] || problems+=("up to date, exit: want 3, got $rc")
[[ -z "$out" ]] || problems+=("up to date, stdout: want empty, got $(printf '%q' "$out")")
dir="$work/no-origin-head-conflict"
origin_fixture "$dir"
repo="$dir/clone"
git -C "$repo" config remote.origin.followRemoteHEAD never
git -C "$repo" remote set-head origin -d >/dev/null 2>&1
conflicting_branch "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && bash "$REBASE" 2>>"$stderr_file")"
rc=$?
expect_conflict_aborted "$repo" "$pre" "$rc" "$out"
report_stderr "$name"

name="rebase-onto-default.test.sh: run while the caller's own rebase is in progress, exits 2 and leaves that rebase in progress, with HEAD and the rebase state directory unchanged (#819)"
problems=()
dir="$work/caller-rebase"
stderr_file="$work/caller-rebase.err"
origin_fixture "$dir"
repo="$dir/clone"
conflicting_branch "$dir"
git_q "$repo" rebase -q origin/main >/dev/null 2>&1
echo "a third run's work" > "$dir/seed/third.txt"
advance_origin "$dir"
state_dir="$(git -C "$repo" rev-parse --path-format=absolute --git-path rebase-merge)"
state_of() { [[ -d "$state_dir" ]] && (cd "$state_dir" && find . -type f -exec cksum {} + | LC_ALL=C sort); }
head_before="$(git -C "$repo" rev-parse HEAD)"
state_before="$(state_of)"
[[ -n "$state_before" ]] || problems+=("fixture: want the caller's rebase in progress at $state_dir, found none")
out="$(cd "$repo" && bash "$REBASE" 2>"$stderr_file")"
rc=$?
[[ "$rc" -eq 2 ]] || problems+=("exit: want 2, got $rc")
head_after="$(git -C "$repo" rev-parse HEAD)"
[[ "$head_after" == "$head_before" ]] || problems+=("HEAD: want it unchanged at $head_before, got $head_after")
[[ -d "$state_dir" ]] || problems+=("rebase: want the caller's rebase still in progress at $state_dir, found none")
state_after="$(state_of)"
[[ "$state_after" == "$state_before" ]] ||
  problems+=("rebase state: want it unchanged at $(printf '%q' "$state_before"), got $(printf '%q' "$state_after")")
report_stderr "$name"

name="rebase-onto-default.test.sh: run through a symlink to the skill directory and from another working directory, a branch behind origin/<default> rebases as when run in place, exits 0, prints the pre-rebase and onto shas, and the caller's clone is the one rebased, never the skill's repository"
problems=()
stderr_file="$work/symlink.err"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
skill_head_before="$(git -C "$HERE" rev-parse HEAD)"
for where in in-place linked; do
  dir="$work/symlink-$where"
  behind_branch "$dir"
  repo="$dir/clone"
  pre="$(git -C "$repo" rev-parse HEAD)"
  onto="$(git -C "$repo" rev-parse origin/main)"
  script="$REBASE"
  [[ "$where" == linked ]] && script="$work/linked-skill/scripts/rebase-onto-default.sh"
  out="$(cd "$repo" && bash "$script" 2>>"$stderr_file")"
  rc=$?
  [[ "$rc" -eq 0 ]] || problems+=("$where, exit: want 0, got $rc")
  want_out="$(printf '%s\n%s' "$pre" "$onto")"
  [[ "$out" == "$want_out" ]] ||
    problems+=("$where, stdout: want $(printf '%q' "$want_out"), got $(printf '%q' "$out")")
  parent="$(git -C "$repo" rev-parse HEAD~1 2>/dev/null)"
  [[ "$parent" == "$onto" ]] || problems+=("$where, HEAD~1: want the onto sha $onto, got $parent")
done
skill_head_after="$(git -C "$HERE" rev-parse HEAD)"
[[ "$skill_head_after" == "$skill_head_before" ]] ||
  problems+=("skill repository HEAD: want it unchanged at $skill_head_before, got $skill_head_after")
report_stderr "$name"

finish
