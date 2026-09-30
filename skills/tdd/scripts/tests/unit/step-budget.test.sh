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

# expect_err_names <name> — add to the case's `problems` unless the run just made named
# <name> on stderr.
expect_err_names() {
  if [[ "$err" != *"$1"* ]]; then
    problems+="    want stderr naming $1, got '$err'"$'\n'
  fi
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Then
# empty it for the next case. Same accounting idiom as step-cost.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
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
expect_err_names VERI_STEP_BUDGET
verdict "a VERI_STEP_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout"

# 4. VERI_RUN_BUDGET set to a negative number, not a non-negative decimal number, with
#    VERI_STEP_BUDGET left at its default: exit 2, nothing on stdout, and the stderr
#    diagnostic names the variable at fault.
run_budget VERI_RUN_BUDGET=-5 --
expect 2 ''
expect_err_names VERI_RUN_BUDGET
verdict "a VERI_RUN_BUDGET that is not a non-negative decimal number exits 2, names it on stderr, prints nothing on stdout"

# 5. both names invalid at once: exit 2 and nothing at all on stdout — both are validated
#    before either is printed, so the run is never handed the first figure and then a failure.
run_budget VERI_STEP_BUDGET=twelve VERI_RUN_BUDGET=-5 --
expect 2 ''
verdict "both budgets invalid at once exits 2 and prints nothing on stdout, not the first figure then a failure"

# 6. each name exported as the empty string, the other left unset: exit 2 and nothing on
#    stdout, never the default — an operator who exported the name meant to set it.
run_budget VERI_STEP_BUDGET= --
expect 2 ''
expect_err_names VERI_STEP_BUDGET
run_budget VERI_RUN_BUDGET= --
expect 2 ''
expect_err_names VERI_RUN_BUDGET
verdict "either budget exported as the empty string exits 2 rather than falling back to its default"

# 7. each name set to 0, the other left unset: exit 0 and the 0 printed back in its own line,
#    the other at its default — 0 is legal, how the over-budget reaction is exercised by hand.
run_budget VERI_STEP_BUDGET=0 --
expect 0 $'0\n120'
run_budget VERI_RUN_BUDGET=0 --
expect 0 $'12\n0'
verdict "a budget of 0 is accepted for either variable and printed back"

# 8. any argument at all, here a number the way `refactor-budget.sh 0` is called: exit 2 — the
#    script answers one question and has nothing to select.
run_budget -- 0
if [[ "$code" != 2 ]]; then
  problems+="    want exit 2, got exit $code and stdout '$out' (stderr '$err')"$'\n'
fi
verdict "any argument exits 2"

# 9. this suite lives in the fast tier's directory, and its header comment — the comment lines
#    after the shebang, up to the first line that is not one, read the way unit-tier.test.sh
#    reads a header — states the bar it clears.
BAR='no git, no network, no servers, no real sleep, no nested suites'
self="$HERE/$(basename "$0")"
[[ "$self" == */skills/tdd/scripts/tests/unit/step-budget.test.sh ]] ||
  problems+="    want the suite under skills/tdd/scripts/tests/unit/, got '$self'"$'\n'
header="$(sed -n '2,$p' "$self" | sed '/^#/!q' | grep '^#')"
[[ "$header" == *"$BAR"* ]] ||
  problems+="    want the header to state '$BAR', got '$header'"$'\n'
verdict "the suite lives in tests/unit/ and its header states the fast-tier bar it clears"

finish
