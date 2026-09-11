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

# 3. a budget that is not a whole number ≥ 0 is a system failure, not a decision: the
#    script fails closed like classify-bail.sh does on an unrecognised cause — exit 2
#    ("no answer could be obtained"), a diagnostic on stderr, and nothing on stdout, so a
#    conductor mirroring stdout cannot mistake a misconfigured run for a real status.
#    Non-numeric and negative are the two ways to get it wrong, one criterion, so they are
#    one case; `problems` says which value broke.
name="a non-numeric or negative VERI_REFACTOR_BUDGET exits 2 with a diagnostic on stderr and no status on stdout"
problems=()
for bad in two -1; do
  # Separate the two streams into their own files: the case is about which stream carries
  # what, so they must not be merged.
  out="$(mktemp)" err="$(mktemp)"
  VERI_REFACTOR_BUDGET="$bad" "$BUDGET" 0 >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want no status on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("VERI_REFACTOR_BUDGET=$bad: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
done

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
