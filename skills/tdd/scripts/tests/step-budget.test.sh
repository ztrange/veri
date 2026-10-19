#!/usr/bin/env bash
# Tests for scripts/step-budget.sh — the resolver for the two money budgets:
# VERI_STEP_BUDGET, what one step may spend, and VERI_RUN_BUDGET, what the whole run may.
# Called with no arguments it prints the step budget then the run budget, one per line.
#
# Run: scripts/tests/step-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEP_BUDGET="$HERE/../step-budget.sh"
source "$HERE/lib/harness.sh"
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

self="$HERE/$(basename "$0")"
[[ "$self" == */skills/tdd/scripts/tests/step-budget.test.sh ]] ||
  problems+="    want the suite under skills/tdd/scripts/tests/, got '$self'"$'\n'
verdict "the suite lives in tests/, with the suites that run their script through its entry point"

finish
