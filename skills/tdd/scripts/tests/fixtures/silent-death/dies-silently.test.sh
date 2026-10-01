#!/usr/bin/env bash
# A fixture, not a suite: only count-line-guard.test.sh runs it, through `make test`.
# Its second case compares a word as a number under `set -u`, which kills the script before
# its count line; the EXIT trap makes it exit 0 on any bash.
set -uo pipefail
trap 'exit 0' EXIT

pass=0 fail=0

if [[ "veri" == "veri" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - a word equals itself"
fi

read -r made budget <<< "COMMENTARY OWED:"
if [[ "$made" -le 3 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - commentary owed is within budget"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
