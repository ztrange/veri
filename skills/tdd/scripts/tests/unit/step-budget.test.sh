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
source "$HERE/../lib/harness.sh"
problems=""

work="$(scratch_dir)"

run_budget() {
  local assigns=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do assigns+=("$1"); shift; done
  [[ $# -gt 0 ]] && shift
  out="$(env -u VERI_STEP_BUDGET -u VERI_RUN_BUDGET "${assigns[@]}" "$STEP_BUDGET" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

expect() {
  if [[ "$code" != "$1" || "$out" != "$2" ]]; then
    problems+="    want exit $1 and stdout '$2', got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

expect_err_names() {
  if [[ "$err" != *"$1"* ]]; then
    problems+="    want stderr naming $1, got '$err'"$'\n'
  fi
}

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
  problems=""
}

run_budget --
expect 0 $'12\n120'
verdict "neither budget set prints 12 then 120, each on its own line, exit 0"

run_budget VERI_STEP_BUDGET=7.5 VERI_RUN_BUDGET=42.25 --
expect 0 $'7.5\n42.25'
verdict "a set VERI_STEP_BUDGET then a set VERI_RUN_BUDGET, decimals included, printed in that order"

run_budget VERI_STEP_BUDGET=twelve --
expect 2 ''
expect_err_names VERI_STEP_BUDGET
verdict "a VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout"

run_budget VERI_RUN_BUDGET=-5 --
expect 2 ''
expect_err_names VERI_RUN_BUDGET
verdict "a VERI_RUN_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout"

run_budget VERI_STEP_BUDGET=twelve VERI_RUN_BUDGET=-5 --
expect 2 ''
verdict "both budgets invalid at once exits 2 and prints nothing on stdout, not the first figure then a failure"

run_budget VERI_STEP_BUDGET= --
expect 2 ''
expect_err_names VERI_STEP_BUDGET
run_budget VERI_RUN_BUDGET= --
expect 2 ''
expect_err_names VERI_RUN_BUDGET
verdict "either budget exported as the empty string exits 2 rather than falling back to its default"

run_budget VERI_STEP_BUDGET=0 --
expect 0 $'0\n120'
run_budget VERI_RUN_BUDGET=0 --
expect 0 $'12\n0'
verdict "a budget of 0 is accepted for either variable and printed back"

run_budget -- 0
if [[ "$code" != 2 ]]; then
  problems+="    want exit 2, got exit $code and stdout '$out' (stderr '$err')"$'\n'
fi
verdict "any argument exits 2"

BAR='no git, no network, no servers, no real sleep, no nested suites'
self="$HERE/$(basename "$0")"
[[ "$self" == */skills/tdd/scripts/tests/unit/step-budget.test.sh ]] ||
  problems+="    want the suite under skills/tdd/scripts/tests/unit/, got '$self'"$'\n'
header="$(sed -n '2,$p' "$self" | sed '/^#/!q' | grep '^#')"
[[ "$header" == *"$BAR"* ]] ||
  problems+="    want the header to state '$BAR', got '$header'"$'\n'
verdict "the suite lives in tests/unit/ and its header states the fast-tier bar it clears"

finish
