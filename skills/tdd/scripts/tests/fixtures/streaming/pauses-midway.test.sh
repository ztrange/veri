#!/usr/bin/env bash
# A fixture, not a suite: only count-line-guard.test.sh runs it, through `make test`.
# Its first case fails, it then sleeps $PAUSE, then a second case runs and the suite ends with
# its count line and a non-zero exit.
set -uo pipefail

PAUSE=0.2

pass=0 fail=0

fail=$((fail + 1))
echo "FAIL - a suite says something before it is finished"

sleep "$PAUSE"

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
