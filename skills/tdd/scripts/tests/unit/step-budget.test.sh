#!/usr/bin/env bash
# Tests for scripts/step-budget.sh — the resolver for the two money budgets (#449, part of
# #447): VERI_STEP_BUDGET, what one step may spend, and VERI_RUN_BUDGET, what the whole run
# may. Called with no arguments it prints the step budget then the run budget, one per line,
# the shape time-budget.sh has, so preflight can refuse a bad value before a leaf launches.
#
# Fast tier (#336): no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/step-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEP_BUDGET="$HERE/../../step-budget.sh"
pass=0 fail=0 problems=""

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# run_budget [env assignments…] -- [args…] — run the script with both budget names cleared
# from the environment, then the assignments given, so an operator's ambient VERI_* cannot
# change what a case sees; leaves its stdout in `out`, its exit code in `code` and its
# stderr in `err`.
run_budget() {
  local assigns=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do assigns+=("$1"); shift; done
  [[ $# -gt 0 ]] && shift
  out="$(env -u VERI_STEP_BUDGET -u VERI_RUN_BUDGET "${assigns[@]}" "$STEP_BUDGET" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# expect <code> <stdout> — add to the case's `problems` for the run just made: nothing when it
# exited <code> with exactly <stdout>, otherwise one indented line saying what it did instead.
expect() {
  if [[ "$code" != "$1" || "$out" != "$2" ]]; then
    problems+="    want exit $1 and stdout '$2', got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Then
# empty it for the next case. Same accounting idiom as step-cost.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
  problems=""
}

# 1. neither name set: the defaults, the step budget first and the run budget second, each on
#    its own line, exit 0.
run_budget --
expect 0 $'12\n120'
verdict "neither budget set prints 12 then 120, each on its own line, exit 0"

# 2. both names set, to decimals and to values unlike each other and unlike the defaults: each
#    printed back as given, the step budget first and the run budget second, exit 0.
run_budget VERI_STEP_BUDGET=7.5 VERI_RUN_BUDGET=42.25 --
expect 0 $'7.5\n42.25'
verdict "a set VERI_STEP_BUDGET then a set VERI_RUN_BUDGET, decimals included, printed in that order"

# 3. VERI_STEP_BUDGET set to a word, not a non-negative decimal number, with VERI_RUN_BUDGET
#    left at its default: exit 2, nothing on stdout, and the stderr diagnostic names the
#    variable at fault.
run_budget VERI_STEP_BUDGET=twelve --
expect 2 ''
if [[ "$err" != *VERI_STEP_BUDGET* ]]; then
  problems+="    want stderr naming VERI_STEP_BUDGET, got '$err'"$'\n'
fi
verdict "a VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
