#!/usr/bin/env bash
# A fixture, not a suite: only count-line-guard.test.sh runs it, through `make test`.
# One case passes, the suite reaches its count line, reports nothing failed and exits 0.
set -uo pipefail

pass=0 fail=0

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
