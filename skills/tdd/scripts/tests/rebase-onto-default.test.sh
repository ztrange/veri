#!/usr/bin/env bash
# Tests for scripts/rebase-onto-default.sh — the rebase a run owes before its PR is marked
# ready, when the default branch moved while the run worked (issue #238).
# Zero-dependency plain-shell asserts, same idiom as push-branch.test.sh.
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
# The origin is a bare repository on the local disk, cloned so the clone carries
# origin/HEAD the way a real one does: the default branch is whatever the remote says, and
# the suite needs no network to say it.
#
# Run: scripts/tests/rebase-onto-default.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REBASE="$HERE/../rebase-onto-default.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# git_q <repo> <args...> — git with an identity of its own, so the suite does not depend on
# whatever user.name/user.email the machine running it happens to carry (CI carries none).
git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

# origin_fixture <dir> — a bare origin at <dir>/origin.git whose default branch `main`
# holds one commit, and a clone of it at <dir>/clone. Creates <dir> itself.
origin_fixture() {
  local dir="$1"
  mkdir -p "$dir"
  git init -q --bare -b main "$dir/origin.git" >/dev/null 2>&1
  git init -q -b main "$dir/seed" >/dev/null 2>&1
  echo "base" > "$dir/seed/file.txt"
  git_q "$dir/seed" add -A >/dev/null 2>&1
  git_q "$dir/seed" commit -q -m "initial" >/dev/null 2>&1
  git_q "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
  git clone -q "$dir/origin.git" "$dir/clone" >/dev/null 2>&1
}

# run_branch <repo> — cut the run's branch from origin/main in <repo> and give it one commit
# of its own, the step's green commit a rebase must keep on top.
run_branch() {
  local repo="$1"
  git_q "$repo" checkout -q -b tdd/1-a-run >/dev/null 2>&1
  echo "the run's work" > "$repo/work.txt"
  git_q "$repo" add -A >/dev/null 2>&1
  git_q "$repo" commit -q -m "feat: a step's green commit (#1)" >/dev/null 2>&1
}

# advance_origin <dir> — another run merged: commit whatever the caller wrote into
# <dir>/seed, push it to origin's main, and fetch it into the clone, which is now behind.
advance_origin() {
  local dir="$1"
  git_q "$dir/seed" add -A >/dev/null 2>&1
  git_q "$dir/seed" commit -q -m "feat: another run merged (#2)" >/dev/null 2>&1
  git_q "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
  git -C "$dir/clone" fetch -q origin >/dev/null 2>&1
}

# conflicting_branch <dir> — the run's branch in <dir>/clone and another run's merge to
# origin's main both edit file.txt and work.txt, differently, so rebasing the one onto the
# other conflicts on both files.
conflicting_branch() {
  local dir="$1" repo="$1/clone"
  run_branch "$repo"
  echo "the run's edit" > "$repo/file.txt"
  git_q "$repo" commit -q -a --amend --no-edit >/dev/null 2>&1
  echo "another run's edit" > "$dir/seed/file.txt"
  echo "another run's work" > "$dir/seed/work.txt"
  advance_origin "$dir"
}

# expect_conflict_aborted <repo> <pre> <rc> <out> — probe the answer to conflicting_branch's
# rebase, adding to `problems`: exit 1, stdout naming file.txt and work.txt, HEAD back at
# <pre>, and no rebase in progress under either backend's directory.
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

# expect_refused <repo> <stdout-file> <why> — run the script in <repo> and probe an answer
# that is no answer, adding to `problems`: exit 2, nothing at all in <stdout-file>, and HEAD
# still where it was before the call. <why> finishes the HEAD problem's line with what a
# moved HEAD would mean.
expect_refused() {
  local repo="$1" stdout="$2" why="$3" head_before rc head_after
  head_before="$(git -C "$repo" rev-parse HEAD)"
  (cd "$repo" && bash "$REBASE" > "$stdout" 2>/dev/null)
  rc=$?
  [[ "$rc" -eq 2 ]] || problems+=("exit: want 2, got $rc")
  [[ ! -s "$stdout" ]] || problems+=("stdout: want empty, got $(printf '%q' "$(cat "$stdout"; echo .)")")
  head_after="$(git -C "$repo" rev-parse HEAD)"
  [[ "$head_after" == "$head_before" ]] || problems+=("HEAD: want it unchanged at $head_before${why}, got $head_after")
}

# 1. A branch cut from origin/main, one commit ahead of it and not behind: nothing to rebase.
name="rebase-onto-default.test.sh: a branch already containing origin/<default> exits 3 with empty stdout and HEAD and tree unchanged"
problems=()
dir="$work/up-to-date"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
head_before="$(git -C "$repo" rev-parse HEAD)"
status_before="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
out="$(cd "$repo" && bash "$REBASE" 2>/dev/null)"
rc=$?
[[ "$rc" -eq 3 ]] || problems+=("exit: want 3, got $rc")
[[ -z "$out" ]] || problems+=("stdout: want empty, got $(printf '%q' "$out")")
head_after="$(git -C "$repo" rev-parse HEAD)"
[[ "$head_after" == "$head_before" ]] || problems+=("HEAD: want it unchanged at $head_before, got $head_after")
status_after="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
[[ "$status_after" == "$status_before" ]] ||
  problems+=("working tree: want it unchanged at $(printf '%q' "$status_before"), got $(printf '%q' "$status_after")")
report "$name"

# 2. origin/main moved on by a commit touching another file than the branch's: the branch is
#    behind, the rebase is clean, and the run's own commit lands on top of the new tip.
name="rebase-onto-default.test.sh: a branch behind origin/<default> with no conflict rebases onto it, exits 0, prints the pre-rebase and onto shas, and keeps its own commit on top"
problems=()
dir="$work/behind"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
echo "another run's work" > "$dir/seed/other.txt"
advance_origin "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
onto="$(git -C "$repo" rev-parse origin/main)"
out="$(cd "$repo" && bash "$REBASE" 2>/dev/null)"
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
report "$name"

# 3. origin/main moved on by a commit touching the same files as the branch's own commit,
#    differently: the rebase conflicts on both, and the script owes an abort.
name="rebase-onto-default.test.sh: a rebase that conflicts is aborted, exits 1, leaves HEAD at the pre-rebase sha with a clean tree and no rebase in progress, and prints the conflicting files one per line"
problems=()
dir="$work/conflict"
origin_fixture "$dir"
repo="$dir/clone"
conflicting_branch "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && bash "$REBASE" 2>/dev/null)"
rc=$?
expect_conflict_aborted "$repo" "$pre" "$rc" "$out"
status_after="$(git -C "$repo" status --porcelain=v1 --untracked-files=all)"
[[ -z "$status_after" ]] || problems+=("working tree: want clean, got $(printf '%q' "$status_after")")
report "$name"

# 4. The branch is behind, but a tracked file carries an uncommitted edit: git refuses to
#    start the rebase at all. That is no conflict — the plumbing failed, not the merge — so
#    the answer is exit 2, not 1. stdout goes to a file rather than through $(…), which
#    would strip a stray newline and let one pass for "nothing on stdout".
name="rebase-onto-default.test.sh: a rebase git refuses for a reason other than a conflict, such as a dirty working tree, exits 2 with nothing on stdout and HEAD unchanged"
problems=()
dir="$work/dirty"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
git -C "$repo" config rebase.autoStash false
echo "another run's work" > "$dir/seed/other.txt"
advance_origin "$dir"
echo "an uncommitted edit" > "$repo/file.txt"
expect_refused "$repo" "$dir/stdout" ""
report "$name"

# 5. The same conflict as case 3, in a repo configured to rebase with the apply backend:
#    git then keeps its in-progress state under rebase-apply rather than rebase-merge, and
#    the conflict is still a conflict — aborted, exit 1, the conflicting files named.
name="rebase-onto-default.test.sh: in a repo configured with rebase.backend=apply, a rebase that conflicts is still aborted, exits 1, prints the conflicting files, and leaves no rebase in progress"
problems=()
dir="$work/conflict-apply"
origin_fixture "$dir"
repo="$dir/clone"
git -C "$repo" config rebase.backend apply
conflicting_branch "$dir"
pre="$(git -C "$repo" rev-parse HEAD)"
out="$(cd "$repo" && bash "$REBASE" 2>/dev/null)"
rc=$?
expect_conflict_aborted "$repo" "$pre" "$rc" "$out"
report "$name"

# 6. The clone fetched origin/main once, after another run merged, so the branch is behind
#    it — but the origin has since gone out of reach, so what the clone holds may be stale. Rebasing onto it would be rebasing onto a guess: the answer is exit 2, no
#    stdout, and HEAD where it was. stdout goes to a file for the reason case 4 gives.
name="rebase-onto-default.test.sh: when origin/<default> cannot be fetched, exits 2 with nothing on stdout and never rebases onto the stale local copy"
problems=()
dir="$work/unreachable"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
echo "another run's work" > "$dir/seed/other.txt"
advance_origin "$dir"
mv "$dir/origin.git" "$dir/origin-gone.git"
expect_refused "$repo" "$dir/stdout" ", not rebased onto the stale origin/main"
report "$name"

# 7. The clone fetched origin/main once, after another run merged, so the branch is behind
#    it. Its fetch refspec then narrows to the run's own branches, and another run merges
#    again: the origin is in reach and `git fetch` succeeds, yet it refreshes nothing under
#    origin/main, so what the clone holds is stale all the same. A fetch that exited 0 is
#    not a default branch that was fetched: exit 2, no stdout, and HEAD where it was.
#    stdout goes to a file for the reason case 4 gives.
name="rebase-onto-default.test.sh: when a fetch succeeds without refreshing origin/<default>, exits 2 with nothing on stdout and never rebases onto the stale local copy"
problems=()
dir="$work/fetch-skips-default"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
echo "another run's work" > "$dir/seed/other.txt"
advance_origin "$dir"
git -C "$repo" config remote.origin.fetch '+refs/heads/tdd/*:refs/remotes/origin/tdd/*'
echo "a third run's work" > "$dir/seed/third.txt"
advance_origin "$dir"
expect_refused "$repo" "$dir/stdout" ", not rebased onto the stale origin/main"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
