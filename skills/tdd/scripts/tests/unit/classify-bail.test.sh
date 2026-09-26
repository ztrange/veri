#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Zero-dependency plain-shell asserts, same idiom as parse-verdict.test.sh.
#
# Contract under test (issue #18, extended by #331):
#   classify-bail.sh killed-stuck         → first stdout line `system`,  exit 0
#   classify-bail.sh no-verdict           → first stdout line `system`,  exit 0
#   classify-bail.sh revise-exhausted     → first stdout line `process`, exit 0
#   classify-bail.sh reconcile-failed     → first stdout line `system`,  exit 0
#   classify-bail.sh untestable-criterion → first stdout line `process`, exit 0
#   classify-bail.sh step-too-big         → first stdout line `process`, exit 0
#   classify-bail.sh rebase-unresolved    → first stdout line `process`, exit 0
#   classify-bail.sh <unrecognised>       → error on stderr, exit non-zero
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/classify-bail.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../../classify-bail.sh"
pass=0 fail=0

# check <name> <cause> <expected-exit> <expected-first-line>
check() {
  local name="$1" cause="$2" exp_code="$3" exp_out="$4" out code first
  out="$("$CLASSIFY" "$cause")" && code=0 || code=$?
  first="$(head -n1 <<< "$out")"
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

# 6. an untestable-criterion cause classifies as process (issue #331): a Red developer leaf
#    found no way to pin the step's criterion as a lightweight, behavior-level test, which
#    is the methodology speaking, not the plumbing breaking — the same category
#    revise-exhausted gets and for the same reason.
check "untestable-criterion is process" untestable-criterion 0 process

# 7. a step-too-big cause classifies as process (issue #363): a Green developer leaf found the
#    step needs more than one new behaviour at once and the split steps would not fit the plan's
#    growth budget, so the step cannot go on — the methodology speaking, not the plumbing.
check "step-too-big is process" step-too-big 0 process

# 9. a rebase-unresolved cause classifies as process (issue #238): a rebase onto a moved
#    default branch could not be resolved within budget — two green branches that do not
#    combine is a finding about the work, not the plumbing breaking.
check "rebase-unresolved is process" rebase-unresolved 0 process

# 8. a stop is not a bail (issue #390): `stopped`, `stop` and the three stop modes are unknown
#    causes, exit 2 with nothing on stdout. A stop has no system/process category, and giving
#    it one would make every bail label in a run log ambiguous — so this pins the script as
#    unchanged. One case: the five names are one contract.
stop_name="stop words are unknown causes, exit 2"
stop_bad=""
for cause in stopped stop at-ledger at-leaf now; do
  out="$("$CLASSIFY" "$cause" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 && -z "$out" ]] || stop_bad+="    $cause: want exit 2 and no stdout, got exit $code, stdout '$out'"$'\n'
done
if [[ -z "$stop_bad" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $stop_name"
  printf '%s' "$stop_bad"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
