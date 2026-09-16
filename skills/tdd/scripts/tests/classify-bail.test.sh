#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Zero-dependency plain-shell asserts, same idiom as parse-verdict.test.sh.
#
# Contract under test (issue #18):
#   classify-bail.sh killed-stuck     → first stdout line `system`,  exit 0
#   classify-bail.sh no-verdict       → first stdout line `system`,  exit 0
#   classify-bail.sh revise-exhausted → first stdout line `process`, exit 0
#   classify-bail.sh reconcile-failed → first stdout line `system`,  exit 0
#   classify-bail.sh <unrecognised>   → error on stderr, exit non-zero
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

# check_nonzero <name> <cause> — an unrecognised cause must exit non-zero (an error),
# never a silent or default classification.
check_nonzero() {
  local name="$1" cause="$2" code
  "$CLASSIFY" "$cause" >/dev/null 2>&1 && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (want non-zero exit, got $code)"
  fi
}

# 1. a killed-stuck cause classifies as system
check "killed-stuck is system" killed-stuck 0 system

# 2. a no-verdict cause classifies as system
check "no-verdict is system" no-verdict 0 system

# 3. a revise-exhausted cause classifies as process
check "revise-exhausted is process" revise-exhausted 0 process

# 4. an unrecognised cause is an error, not a silent/default classification
check_nonzero "unknown cause exits non-zero" wat

# 5. a reconcile-failed cause classifies as system (issue #232): where the branch lives
#    broke, not the methodology
check "reconcile-failed is system" reconcile-failed 0 system

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
