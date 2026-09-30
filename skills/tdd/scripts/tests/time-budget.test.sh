#!/usr/bin/env bash
# Unit tests for scripts/time-budget.sh — the two tunables that decide whether a recorded
# test-command run counts as over budget (issue #342, part of PRD #335). tier-usual.sh says
# what a tier usually costs; these say how far past usual, or past a fixed ceiling for the
# unit tier, is far enough to be worth a word in the narration.
#
# Contract under test (this step only — the tunables, not yet the comparison they feed):
#   time-budget.sh          → exit 0, and on stdout the two resolved tunables, one per line:
#                             VERI_UNIT_BUDGET's seconds first, VERI_TIME_WARN_RATIO's
#                             ratio second. Unset, they are 10 and 1.5.
#   a non-numeric value for either → exit 2, nothing on stdout, and a diagnostic on stderr
#                             naming the variable at fault.
#
# The no-argument call is the preflight one: it is the point `refactor-budget.sh 0` already
# occupies in SKILL.md step 5, where a misconfigured run is refused before any leaf is
# launched rather than mid-loop (CLAUDE.md, "Four budgets on four axes"). Failing closed
# with nothing on stdout is refactor-budget.sh's own rule, for its own reason: a conductor
# capturing stdout must not be able to read a diagnostic as a budget.
#
# Nothing here times anything — the tunables are read from the environment, so the case is
# arithmetic-free and costs one process per invocation (CLAUDE.md, "Testing idiom").
#
# Run: skills/tdd/scripts/tests/time-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../time-budget.sh"
pass=0 fail=0

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
