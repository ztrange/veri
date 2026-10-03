#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/window.sh — the ±250-character context the prose suites read
# around a pattern, sourced, not run.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/window.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/window.sh"
source "$HERE/../lib/harness.sh"

name="two occurrences of a pattern 100 characters apart each get a window of their own"
a="$(printf 'a%.0s' {1..50})"
b="$(printf 'b%.0s' {1..99})"
c="$(printf 'c%.0s' {1..50})"
text="${a}X${b}X${c}"
actual="$(
  # shellcheck disable=SC1090
  source "$LIB"
  windows "$text" 'X'
)"
expect_eq "$name" "$text"$'\n'"$text" "$actual"

name="a pattern that can match the empty string ends instead of looping forever"
out="$(scratch_dir)/windows.out"
(
  # shellcheck disable=SC1090
  source "$LIB"
  ulimit -f 1
  windows 'abc' 'x*' > "$out"
)
expect_eq "$name" "0" "$?"

finish
