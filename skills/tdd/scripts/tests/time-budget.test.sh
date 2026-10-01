#!/usr/bin/env bash
# Unit tests for scripts/time-budget.sh — the two tunables that decide whether a recorded
# test-command run counts as over budget.
#
# Contract under test:
#   time-budget.sh          → exit 0, and on stdout the two resolved tunables, one per line:
#                             VERI_UNIT_BUDGET's seconds first, VERI_TIME_WARN_RATIO's
#                             ratio second. Unset, they are 10 and 1.5.
#   a non-numeric value for either → exit 2, nothing on stdout, and a diagnostic on stderr
#                             naming the variable at fault.
#
# Run: skills/tdd/scripts/tests/time-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../time-budget.sh"

source "$HERE/lib/harness.sh"

name="time-budget.sh: unset tunables resolve to 10 and 1.5; a non-numeric one exits 2 naming the variable"
problems=()

out="$( env -u VERI_UNIT_BUDGET -u VERI_TIME_WARN_RATIO "$BUDGET" 2>/dev/null )" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want time-budget.sh with both tunables unset to exit 0, it exited $code")

[[ "$out" == $'10\n1.5' ]] ||
  problems+=("defaults: want '10' then '1.5', got $(printf '%q' "$out")")

err="$( VERI_UNIT_BUDGET=ten "$BUDGET" 2>&1 >/dev/null )" && code=0 || code=$?

[[ "$code" == 2 ]] ||
  problems+=("want VERI_UNIT_BUDGET=ten to exit 2, it exited $code")

[[ "$err" == *VERI_UNIT_BUDGET* ]] ||
  problems+=("VERI_UNIT_BUDGET=ten: want a diagnostic naming VERI_UNIT_BUDGET, got $(printf '%q' "$err")")

out="$( VERI_UNIT_BUDGET=ten "$BUDGET" 2>/dev/null )" || true

[[ -z "$out" ]] ||
  problems+=("VERI_UNIT_BUDGET=ten: want nothing on stdout, got $(printf '%q' "$out")")

err="$( VERI_TIME_WARN_RATIO=1,5 "$BUDGET" 2>&1 >/dev/null )" && code=0 || code=$?

[[ "$code" == 2 ]] ||
  problems+=("want VERI_TIME_WARN_RATIO=1,5 to exit 2, it exited $code")

[[ "$err" == *VERI_TIME_WARN_RATIO* ]] ||
  problems+=("VERI_TIME_WARN_RATIO=1,5: want a diagnostic naming VERI_TIME_WARN_RATIO, got $(printf '%q' "$err")")

out="$( VERI_TIME_WARN_RATIO=1,5 "$BUDGET" 2>/dev/null )" || true

[[ -z "$out" ]] ||
  problems+=("VERI_TIME_WARN_RATIO=1,5: want nothing on stdout, got $(printf '%q' "$out")")

report "$name"

finish
