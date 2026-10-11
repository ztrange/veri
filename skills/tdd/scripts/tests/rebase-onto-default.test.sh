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

finish
