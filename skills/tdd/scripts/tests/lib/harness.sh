#!/usr/bin/env bash
# Sourced by suites: counters, the ok/no/report/expect_eq helpers and the count line.
# Usage: source "$HERE/lib/harness.sh"; ...; finish
# finish exits non-zero (returns 1) when any assertion failed.

pass=0
fail=0
problems=()

ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

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

expect_eq() {
  if [[ "$2" == "$3" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $1"
    printf '    expected: %s\n    actual:   %s\n' "$2" "$3"
  fi
}

finish() {
  echo "----"
  echo "$pass passed, $fail failed"
  [[ "$fail" -eq 0 ]]
}
