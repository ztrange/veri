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
# holds one commit, and a clone of it at <dir>/clone.
origin_fixture() {
  local dir="$1"
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

# 1. A branch cut from origin/main, one commit ahead of it and not behind: nothing to rebase.
name="rebase-onto-default.test.sh: a branch already containing origin/<default> exits 3 with empty stdout and HEAD and tree unchanged"
problems=()
dir="$work/up-to-date"
mkdir -p "$dir"
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
mkdir -p "$dir"
origin_fixture "$dir"
repo="$dir/clone"
run_branch "$repo"
echo "another run's work" > "$dir/seed/other.txt"
git_q "$dir/seed" add -A >/dev/null 2>&1
git_q "$dir/seed" commit -q -m "feat: another run merged (#2)" >/dev/null 2>&1
git_q "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
git -C "$repo" fetch -q origin >/dev/null 2>&1
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
