#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Zero-dependency plain-shell asserts, same idiom as parse-verdict.test.sh.
#
# Contract under test (THIS step, issue #18):
#   classify-bail.sh killed-stuck  → first stdout line `system`, exit 0
#   classify-bail.sh no-verdict    → first stdout line `system`, exit 0
# (Other causes are later steps and are not pinned here.)
#
# Run: scripts/tests/classify-bail.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../classify-bail.sh"
pass=0 fail=0

# check <name> <cause> <expected-exit> <expected-first-line>
check() {
  local name="$1" cause="$2" exp_code="$3" exp_out="$4" out code first
  out="$("$CLASSIFY" "$cause")" && code=0 || code=$?
  first="$(printf '%s\n' "$out" | head -n1)"
  if [[ "$code" == "$exp_code" && "$first" == "$exp_out" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$first") | sed 's/^/    /'
  fi
}

# 1. a killed-stuck cause classifies as system
check "killed-stuck is system" killed-stuck 0 system

# 2. a no-verdict cause classifies as system
check "no-verdict is system" no-verdict 0 system

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
