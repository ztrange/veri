#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   classify-bail.sh killed-stuck         → first stdout line `system`,  exit 0
#   classify-bail.sh no-verdict           → first stdout line `system`,  exit 0
#   classify-bail.sh revise-exhausted     → first stdout line `process`, exit 0
#   classify-bail.sh reconcile-failed     → first stdout line `system`,  exit 0
#   classify-bail.sh untestable-criterion → first stdout line `process`, exit 0
#   classify-bail.sh step-too-big         → first stdout line `process`, exit 0
#   classify-bail.sh rebase-unresolved    → first stdout line `process`, exit 0
#   classify-bail.sh uncovered            → first stdout line `process`, exit 0
#   classify-bail.sh <unrecognised>       → error on stderr, exit non-zero
#
# Run: scripts/tests/unit/classify-bail.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../../classify-bail.sh"
source "$HERE/../lib/harness.sh"

check() {
  local name="$1" cause="$2" exp_code="$3" exp_out="$4" out code first
  out="$("$CLASSIFY" "$cause")" && code=0 || code=$?
  first="$(head -n1 <<< "$out")"
  if [[ "$code" == "$exp_code" && "$first" == "$exp_out" ]]; then
    ok
  else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$first") | sed 's/^/    /'
  fi
}

check_nonzero() {
  local name="$1" cause="$2" code
  "$CLASSIFY" "$cause" >/dev/null 2>&1 && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    ok
  else
    no "$name (want non-zero exit, got $code)"
  fi
}

check "killed-stuck is system" killed-stuck 0 system

check "no-verdict is system" no-verdict 0 system

check "revise-exhausted is process" revise-exhausted 0 process

check_nonzero "unknown cause exits non-zero" wat

check "reconcile-failed is system" reconcile-failed 0 system

check "untestable-criterion is process" untestable-criterion 0 process

check "step-too-big is process" step-too-big 0 process

check "rebase-unresolved is process" rebase-unresolved 0 process

stop_name="stop words are unknown causes, exit 2"
stop_bad=""
for cause in stopped stop at-ledger at-leaf now; do
  out="$("$CLASSIFY" "$cause" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 && -z "$out" ]] || stop_bad+="    $cause: want exit 2 and no stdout, got exit $code, stdout '$out'"$'\n'
done
if [[ -z "$stop_bad" ]]; then
  ok
else
  no "$stop_name"
  printf '%s' "$stop_bad"
fi

budget_name="budget crossing words are unknown causes, exit 2"
budget_bad=""
for cause in step-over-budget over-budget; do
  out="$("$CLASSIFY" "$cause" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 && -z "$out" ]] || budget_bad+="    $cause: want exit 2 and no stdout, got exit $code, stdout '$out'"$'\n'
done
if [[ -z "$budget_bad" ]]; then
  ok
else
  no "$budget_name"
  printf '%s' "$budget_bad"
fi

check "uncovered is process" uncovered 0 process

finish
