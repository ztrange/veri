#!/usr/bin/env bash
# demo-classified-bail.sh — show that a forced system failure and a forced process failure
# produce correctly classified bail comments (#7).
#
# Deterministic, no model call: for each bail cause the conductor can hit, it runs the real
# classify-bail.sh and renders the bail-comment header the conductor would post — proving a
# plumbing failure is labelled `system` and a methodology failure is labelled `process`,
# and that an unknown cause errors rather than mislabelling.
#
# Usage:  fixtures/demo-classified-bail.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
S="$(cd "$HERE/.." && pwd)/skills/tdd/scripts"

fail=0

# show <label> <cause> <phase> <expected-classification>
show() {
  local label="$1" cause="$2" phase="$3" want="$4" got
  got="$("$S/classify-bail.sh" "$cause")"
  printf '>> forced %s (cause: %s)\n' "$label" "$cause"
  printf '   bail comment → "### ⛔ Bailed — %s (%s failure)"\n' "$phase" "$got"
  if [[ "$got" == "$want" ]]; then
    printf '   ✓ classified as %s\n\n' "$got"
  else
    printf '   ✗ expected %s, got %s\n\n' "$want" "$got"; fail=1
  fi
}

# A forced SYSTEM failure (plumbing broke): the supervisor killed a hung leaf past its budget.
show "system failure — hung developer leaf" killed-stuck "green" system
# A forced SYSTEM failure: the verifier produced no readable verdict.
show "system failure — no readable verdict" no-verdict "verify-red" system
# A forced PROCESS failure (methodology spoke): the revise budget was spent, still REJECT.
show "process failure — revise budget exhausted" revise-exhausted "verify-green" process

# An unknown cause must error, never mislabel.
printf '>> unknown cause (cause: wat)\n'
if "$S/classify-bail.sh" wat >/dev/null 2>&1; then
  printf '   ✗ unknown cause did not error\n'; fail=1
else
  printf '   ✓ errored (exit %s) instead of mislabelling\n\n' "$?"
fi

if [[ "$fail" -eq 0 ]]; then
  echo "✅ every forced failure was classified correctly (system vs process)."
else
  echo "❌ a classification was wrong — investigate."; exit 1
fi
