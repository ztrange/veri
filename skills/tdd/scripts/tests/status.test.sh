#!/usr/bin/env bash
# Unit tests for scripts/status.sh — the aggregation layer over every run in a repository.
# Run from a target repo, it discovers runs from `.tdd/wt/*` under the repository's main
# working tree and renders each one.
#
# Contract under test:
#   status.sh            print every run under .tdd/wt/*, exit 0;
#                        print "no runs" and exit 3 when there are none.
#
# Run: scripts/tests/status.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STATUS="$HERE/../status.sh"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

repo() {  # repo <name> -> path
  local dir="$work/$1"
  new_repo -b main "$dir" >/dev/null 2>&1
  echo "$dir"
}

fabricate_run() {  # fabricate_run <repo> <n> <branch> -> path
  local dir="$1/.tdd/wt/$2"
  new_repo -b "$3" "$dir" >/dev/null 2>&1
  mkdir -p "$dir/.tdd"
  echo "$dir"
}

run_in() {  # run_in <dir> [script args…]; sets $out and $code
  local dir="$1"; shift
  out="$(cd "$dir" && "$STATUS" "$@" 2>/dev/null)" && code=0 || code=$?
}

err_in() {  # err_in <dir> [script args…]; sets $err and $code
  local dir="$1"; shift
  err="$(cd "$dir" && "$STATUS" "$@" 2>&1 >/dev/null)" && code=0 || code=$?
}

expect_nothing_missing() {  # expect_nothing_missing <case name>; reads $missing, $out, $code
  if [[ ${#missing[@]} -eq 0 && "$code" -eq 0 ]]; then ok; else
    no "$1"
    printf 'missing: %s\n' "${missing[@]:-}"
    printf 'output:\n%s\nexit %s\n' "$out" "$code"
  fi
}

finish
