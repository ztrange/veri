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

name="#595: sourcing the harness twice still removes a scratch_dir, runs an on_exit once and leaves no scratch list"
outer="$(mktemp -d)"
out="$(
  # shellcheck disable=SC1090
  source "$HARNESS"
  d="$(scratch_dir)"
  on_exit "echo ran >> '$outer/marker'"
  echo "$d"
  echo "$_harness_scratch"
  # shellcheck disable=SC1090
  source "$HARNESS"
)"
dir="$(sed -n 1p <<< "$out")"
list="$(sed -n 2p <<< "$out")"
runs="$(grep -c ran "$outer/marker" 2>/dev/null)"
if [[ -n "$dir" && ! -e "$dir" ]]; then state=gone; else state=kept; fi
if [[ -n "$list" && ! -e "$list" ]]; then lists=0; else lists=1; fi
actual="runs=${runs:-0} dir=$state lists=$lists"
expected="runs=1 dir=gone lists=0"
if [[ "$actual" == "$expected" ]]; then
  ok
else
  no "$name"
  printf '    expected: %s\n    actual:   %s\n' "$expected" "$actual"
fi
rm -rf "$outer" "$dir" "$list"

name="#595: sourcing the harness a second time keeps the pass/fail counts already reached"
actual="$(
  unset pass fail
  # shellcheck disable=SC1090
  source "$HARNESS"
  ok
  ok
  no "planted" > /dev/null
  # shellcheck disable=SC1090
  source "$HARNESS"
  echo "pass=$pass fail=$fail"
)"
expected="pass=2 fail=1"
if [[ "$actual" == "$expected" ]]; then
  ok
else
  no "$name"
  printf '    expected: %s\n    actual:   %s\n' "$expected" "$actual"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
