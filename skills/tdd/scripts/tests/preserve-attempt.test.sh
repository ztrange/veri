#!/usr/bin/env bash
# Tests for scripts/preserve-attempt.sh — the side-ref snapshot a troubled step leaves behind,
# so the tree a rejected or stuck leaf produced is still readable after the run (issue #409).
#
# Contract under test:
#   preserve-attempt.sh <issue> <step> <phase> <attempt>   # run from the issue's worktree
#       commits the worktree as it stands to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>
#
# The subject is git's own storage, so this suite is not in the fast tier: the behaviour under
# test IS a real repository's refs, and a fake git could not answer `git show`. Every case runs
# against a throwaway `git init` repo with one commit, and asks git rather than the filesystem —
# a file written under .git by hand would pass a filesystem check and be no commit at all.
#
# Run: scripts/tests/preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PRESERVE="$HERE/../preserve-attempt.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The identity every commit this suite causes is made under, stated once: the suite must not
# depend on whatever user.name/user.email the machine running it carries (CI carries none).
# In the environment rather than as `git -c` flags because half the commits are git's own,
# made inside the script under test, which takes no flags from here.
ident=(GIT_AUTHOR_NAME=veri GIT_AUTHOR_EMAIL=veri@example.test
       GIT_COMMITTER_NAME=veri GIT_COMMITTER_EMAIL=veri@example.test)

# git_q <repo> <args…> — git run against <repo> under that identity.
git_q() { local repo="$1"; shift; env "${ident[@]}" git -C "$repo" "$@"; }

# new_repo <path> — a throwaway repo at <path>, on `main`, carrying one commit that tracks
# stop-run.sh. -b main names the default branch rather than inheriting init.defaultBranch.
new_repo() {
  mkdir -p "$1"
  git init -q -b main "$1" >/dev/null 2>&1
  printf 'committed\n' > "$1/stop-run.sh"
  git_q "$1" add stop-run.sh >/dev/null 2>&1
  git_q "$1" commit -q -m "initial" >/dev/null 2>&1
}

# preserve <repo> <args…> — call the script from <repo>, under the same identity: the commit
# it makes is git's, and a machine with no configured user (CI) must not decide whether this
# case can run at all.
preserve() {
  local repo="$1"; shift
  ( cd "$repo" && env "${ident[@]}" "$PRESERVE" "$@" )
}

# 1. the worktree as it stands lands on a ref named by issue, step, phase and attempt, and
#    `git show` reads that commit's tree back — the rejected file, which no commit on the
#    branch ever carried
repo="$work/repo"
new_repo "$repo"
printf 'rejected work\n' > "$repo/stop-run.sh"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref="refs/veri/attempts/409/3/develop-green-1"
git_q "$repo" rev-parse --verify --quiet "$ref^{commit}" >/dev/null 2>&1; resolved=$?
shown="$(git_q "$repo" show "$ref:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$shown" == "rejected work" ]]; } \
  && ok || no "commits the worktree to $ref and git show reads it back (code=$code resolved=$resolved shown='$shown')"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
