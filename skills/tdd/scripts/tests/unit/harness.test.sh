#!/usr/bin/env bash
# Tests for scripts/tests/lib/harness.sh — the scaffolding every suite sources: counters,
# the `ok`/`no`/`report`/`expect_eq` helpers and the count line.
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/harness.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HARNESS="$HERE/../lib/harness.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

name="sourcing gives zeroed counters and the helpers; report and expect_eq print the FAIL lines and finish the count line"
out="$(
  # shellcheck disable=SC1090
  source "$HARNESS"
  echo "start: $pass $fail ${#problems[@]}"
  ok
  no "plain"
  problems=()
  report "clean"
  problems=("first problem" "second problem")
  report "dirty"
  expect_eq "equal" "a" "a"
  expect_eq "unequal" "a" "b"
  finish
  echo "exit: $?"
)"
if [[ "$out" == "start: 0 0 0"$'\n'"FAIL - plain"$'\n'"FAIL - dirty"$'\n'"    first problem"$'\n'"    second problem"$'\n'"FAIL - unequal"$'\n'*"----"$'\n'"3 passed, 3 failed"$'\n'"exit: 1" ]]; then
  ok
else
  no "$name"
  printf '    got:\n%s\n' "$out"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
