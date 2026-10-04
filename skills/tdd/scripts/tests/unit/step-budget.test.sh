#!/usr/bin/env bash
# Tests for scripts/step-budget.sh — the resolver for the two money budgets:
# VERI_STEP_BUDGET, what one step may spend, and VERI_RUN_BUDGET, what the whole run may.
# Called with no arguments it prints the step budget then the run budget, one per line.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
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

run_budget -- 0
expect 2 ''
if [[ "$err" != 'usage: step-budget.sh (takes no arguments)' ]]; then
  problems+="    want stderr 'usage: step-budget.sh (takes no arguments)' alone, got '$err'"$'\n'
fi
verdict "an argument exits 2 with nothing on stdout and the usage line alone on stderr"

ln -s "$(cd "$HERE/../../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
linked_matches() {
  local in_out="$out" in_code="$code" linked linked_code
  linked="$(cd "$work/elsewhere" && env -u VERI_STEP_BUDGET -u VERI_RUN_BUDGET "$@" "$work/linked-skill/scripts/step-budget.sh" "${args[@]}" 2>/dev/null)" && linked_code=0 || linked_code=$?
  if [[ "$linked" != "$in_out" || "$linked_code" != "$in_code" ]]; then
    problems+="    in place: exit $in_code, stdout '$in_out'; through the symlink from elsewhere: exit $linked_code, stdout '$linked'"$'\n'
  fi
}
args=()
run_budget --
expect 0 $'12\n120'
linked_matches
run_budget VERI_STEP_BUDGET=twelve --
expect 2 ''
linked_matches VERI_STEP_BUDGET=twelve
args=(0)
run_budget -- 0
expect 2 ''
linked_matches
verdict "step-budget.sh run through a symlink to the skill directory and from another working directory answers no argument, VERI_STEP_BUDGET=twelve and the argument 0 as it does in place"

BAR='no git, no network, no servers, no real sleep, no nested suites'
self="$HERE/$(basename "$0")"
[[ "$self" == */skills/tdd/scripts/tests/unit/step-budget.test.sh ]] ||
  problems+="    want the suite under skills/tdd/scripts/tests/unit/, got '$self'"$'\n'
header="$(sed -n '2,$p' "$self" | sed '/^#/!q' | grep '^#')"
[[ "$header" == *"$BAR"* ]] ||
  problems+="    want the header to state '$BAR', got '$header'"$'\n'
verdict "the suite lives in tests/unit/ and its header states the fast-tier bar it clears"

finish
