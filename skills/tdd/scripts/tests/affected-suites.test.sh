#!/usr/bin/env bash
# Unit tests for scripts/affected-suites.sh — prints the suites one change affects.
#
# Contract under test:
#   affected-suites.sh <base>..<head>, run inside the repository
#                       → exit 0, and one suite path per line, sorted, with no duplicate.
#
# Run: scripts/tests/affected-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
AFFECTED="$HERE/../affected-suites.sh"
source "$HERE/lib/harness.sh"
source "$HERE/../lib/missing-argument-exit.sh"

work="$(scratch_dir)"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

commit_all() {
  git_q "$1" add -A >/dev/null 2>&1
  git_q "$1" commit -q -m "$2" >/dev/null 2>&1
}

commit_base() { commit_all "$repo" "base"; base="$(git -C "$repo" rev-parse HEAD)"; }
commit_head() { commit_all "$repo" "head"; head="$(git -C "$repo" rev-parse HEAD)"; }

make_repo() {
  repo="$work/$1"
  new_repo -b main "$repo" >/dev/null 2>&1
  s="$repo/skills/tdd/scripts"
}

run_affected() { cd "$repo" && "$AFFECTED" "${1:-$base..$head}"; }

expect_suites() {
  local name="$1" expected out code
  shift
  expected="$(printf '%s\n' "$@")"
  out="$(run_affected 2>/dev/null)"; code=$?
  if [[ "$code" == 0 && "$out" == "$expected" ]]; then ok; else
    no "$name (code=$code)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

expect_suites_unwidened() {
  local name="$1" expected out code err errf="$work/unwidened.err"
  shift
  expected="$(printf '%s\n' "$@")"
  out="$(run_affected 2>"$errf")"; code=$?
  err="$(cat "$errf")"
  if [[ "$code" == 0 && "$out" == "$expected" && "$err" != *widening* ]]; then ok; else
    no "$name (code=$code, stderr=${err:-<empty>})"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

foo_tree() {
  mkdir -p "$s/tests"
  printf 'foo\n' > "$s/foo.sh"
  printf '# foo suite\n' > "$s/tests/foo.test.sh"
}

foo_bar_tree() {
  foo_tree
  printf 'bar\n' > "$s/bar.sh"
  printf '# bar suite\n' > "$s/tests/bar.test.sh"
}

make_repo no-range
foo_tree
commit_base
offender="$(cd "$repo" && named_usage_offender "$HERE/.." affected-suites.sh no-range)"; code=$?
if [[ "$code" == 0 ]]; then ok; else
  no "affected-suites.sh with an argument that is not a <base>..<head> range exits 2 with its own usage text on stderr ($offender)"
fi

finish
