#!/usr/bin/env bash
# Tests for scripts/preserve-attempt.sh — the side-ref snapshot a troubled step leaves behind,
# so the tree a rejected or stuck leaf produced is still readable after the run.
#
# Contract under test:
#   preserve-attempt.sh <issue> <step> <phase> <attempt>   # run from the issue's worktree
#       commits the worktree as it stands to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>
#
# Run: scripts/tests/preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"
mkdir -p "$work/skill/scripts"
cp -R "$HERE/../preserve-attempt.sh" "$HERE/../veri" "$work/skill/scripts/"
PRESERVE="$work/skill/scripts/preserve-attempt.sh"

ident=(GIT_AUTHOR_NAME=veri GIT_AUTHOR_EMAIL=veri@example.test
       GIT_COMMITTER_NAME=veri GIT_COMMITTER_EMAIL=veri@example.test)

git_q() { local repo="$1"; shift; env "${ident[@]}" git -C "$repo" "$@"; }

REF="refs/veri/attempts/409/3/develop-green-1"

ref_resolves() { git_q "$1" rev-parse --verify --quiet "${2:-$REF}^{commit}" >/dev/null 2>&1; }

attempts_dir() { printf '%s/.tdd/attempts' "$1"; }

copies_in() { ls "$(attempts_dir "$1")" 2>/dev/null | tr '\n' ' '; }

copy_path() { printf '%s/%s-develop-green-1-%s.%s' "$(attempts_dir "$1")" "$2" "$3" "$4"; }

copy_text() { if [[ -f "$1" ]]; then cat "$1"; else echo "<missing>"; fi; }

unborn_repo() {
  mkdir -p "$1"
  new_repo -b main "$1" >/dev/null 2>&1
}

make_repo() {
  unborn_repo "$1"
  printf 'committed\n' > "$1/stop-run.sh"
  git_q "$1" add stop-run.sh >/dev/null 2>&1
  git_q "$1" commit -q -m "initial" >/dev/null 2>&1
}

REJECTED="rejected work"

dirty_repo() {
  make_repo "$1"
  printf '%s\n' "$REJECTED" > "$1/stop-run.sh"
}

write_ledger() {
  local repo="$1"; shift
  local box='x' step
  mkdir -p "$repo/.tdd"
  { printf '# Plan for #409\n\n'
    for step in "$@"; do printf -- '- [%s] %s\n' "$box" "$step"; box=' '; done
  } > "$repo/.tdd/issue-409.md"
  git_q "$repo" add .tdd/issue-409.md >/dev/null 2>&1
  git_q "$repo" commit -q -m "plan: scope #409" >/dev/null 2>&1
}

leaf_output() {
  local repo="$1" log_text="$2" out_text="${3:-}"
  mkdir -p "$repo/.tdd"
  printf '%s\n' "$log_text" > "$repo/.tdd/develop-green.log"
  if [[ -n "$out_text" ]]; then printf '%s\n' "$out_text" > "$repo/.tdd/develop-green.out"; fi
}

preserve() {
  local repo="$1"; shift
  ( cd "$repo" && env "${ident[@]}" "$PRESERVE" "$@" )
}

finish
