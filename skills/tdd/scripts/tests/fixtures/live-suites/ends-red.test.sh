#!/usr/bin/env bash
# A fixture, not a suite: only count-line-guard.test.sh runs it, through `make test`.
# One case fails, the suite prints its FAIL line, reaches its count line and exits non-zero.
set -uo pipefail

pass=0 fail=0

if [[ "veri" == "something else" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals a word it differs from"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
