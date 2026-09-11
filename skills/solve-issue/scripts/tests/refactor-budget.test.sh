#!/usr/bin/env bash
# Unit tests for scripts/refactor-budget.sh — bounds the refactor loop so a step costs
# the same on every run: given the number of transforms done so far, it says whether
# another leaf may run.
# Zero-dependency plain-shell asserts, same idiom as classify-bail.test.sh.
#
# Contract under test (issue #42):
#   refactor-budget.sh <count>  → exit 0 while <count> is below VERI_REFACTOR_BUDGET
#                                 (default 2), exit 3 once the budget is spent;
#                                 a one-line status on stdout either way, so the
#                                 conductor can mirror it (`refactor 2/2 — budget spent`).
#   VERI_REFACTOR_BUDGET=0      → exit 3 at count 0: the refactor loop is switched off.
#
# Run: scripts/tests/refactor-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../refactor-budget.sh"
pass=0 fail=0

# 1. with the default budget — VERI_REFACTOR_BUDGET unset, so the script's own default
#    of 2 applies — counts 0 and 1 mean "another transform may run" (exit 0) and count 2
#    means "budget spent" (exit 3). Every answer prints a one-line status.
#    The three probes are one criterion, so they are reported as one case; `problems`
#    collects what went wrong in each so the FAIL line says which count broke.
name="default budget: counts 0 and 1 exit 0, count 2 exits 3, each with a one-line status"
problems=()
for probe in "0 0" "1 0" "2 3"; do
  count="${probe% *}" exp_code="${probe#* }"
  # env -u clears the variable for the child only, so the test never depends on — nor
  # disturbs — whatever the surrounding run has set.
  out="$(env -u VERI_REFACTOR_BUDGET "$BUDGET" "$count" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == "$exp_code" ]] ||
    problems+=("count $count: want exit $exp_code, got $code")
  # Command substitution has already eaten any trailing newline, so "exactly one line"
  # is: not empty, and no newline left inside.
  [[ -n "$out" && "$out" != *$'\n'* ]] ||
    problems+=("count $count: want a one-line status on stdout, got: $(printf '%q' "$out")")
done

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

# 2. a budget of 0 switches the refactor loop off entirely: even before any transform has
#    run — count 0 — the budget is already spent, so the very first ask gets exit 3 and no
#    leaf ever launches. The one-line status is case 1's business; this case pins the exit.
name="VERI_REFACTOR_BUDGET=0: count 0 exits 3, so the refactor loop never runs"
VERI_REFACTOR_BUDGET=0 "$BUDGET" 0 >/dev/null 2>&1 && code=0 || code=$?
if [[ "$code" == 3 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (want exit 3, got $code)"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
