#!/usr/bin/env bash
# Tests for scripts/run-affordable.sh — can this run still afford to finish? Run from the
# run's worktree with the number of steps still to go, it projects the run's spend so far
# plus that many steps at the median completed full step's cost against VERI_RUN_BUDGET.
# Every fixture here is a hand-written .tdd/events.jsonl, the log step-cost.sh reads.
#
# Run: scripts/tests/run-affordable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUN_AFFORDABLE="$HERE/../run-affordable.sh"
source "$HERE/lib/harness.sh"
problems=""

work="$(scratch_dir)"
mkdir -p "$work/.tdd"

run_affordable() {
  local assigns=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do assigns+=("$1"); shift; done
  [[ $# -gt 0 ]] && shift
  out="$(cd "$work" && env -u VERI_STEP_BUDGET -u VERI_RUN_BUDGET "${assigns[@]}" \
    "$RUN_AFFORDABLE" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

expect_code() {
  if [[ "$code" != "$1" ]]; then
    problems+="    want exit $1, got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

expect_silent() {
  [[ -z "$out" ]] || problems+="    want empty stdout${1:+ for $1}, got '$out'"$'\n'
}

expect_figure() {
  grep -Fw -- "$2" <<< "$out" > /dev/null ||
    problems+="    want stdout to carry $1 '$2', got '$out'"$'\n'
}

expect_figures() {
  expect_figure "spent" "$1"
  expect_figure "steps remaining" "$2"
  expect_figure "the median" "$3"
  expect_figure "the projection" "$4"
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

step_leaves() {
  local step="$1" d; shift
  for d in "$@"; do
    printf '{"ts": 1, "issue": "453", "actor": "developer", "phase": "red", "step": "%s", "event": "usage", "total_cost_usd": "%s"}\n' \
      "$step" "$d" >> "$work/.tdd/events.jsonl"
  done
}

pin_step() { step_leaves "$1" 0.25 0.25; }

three_full_steps() {
  step_leaves "step one"   0.25 1.00 1.00 1.00 1.00 1.00
  step_leaves "step three" 0.75 1.50 1.50 2.00 2.00 2.00
  step_leaves "step two"   0.50 1.00 1.50 1.50 1.50 1.50
}


finish
