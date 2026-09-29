#!/usr/bin/env bash
# Tests for scripts/run-affordable.sh — can this run still afford to finish (#453, part of
# #447)? Run from the run's worktree with the number of steps still to go, it projects the
# run's spend so far plus that many steps at the median completed full step's cost against
# VERI_RUN_BUDGET. Every fixture here is a hand-written .tdd/events.jsonl, the log
# step-cost.sh reads, so nothing a leaf does is needed.
#
# Fast tier (#336): no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/run-affordable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUN_AFFORDABLE="$HERE/../../run-affordable.sh"
source "$HERE/../lib/harness.sh"
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
  step_leaves "step two"   0.50 1.00 1.50 1.50 1.50 1.50
  step_leaves "step three" 0.75 1.50 1.50 2.00 2.00 2.00
}

: > "$work/.tdd/events.jsonl"
three_full_steps
run_affordable VERI_RUN_BUDGET=50 -- 4
expect_code 1
expect_figures 22.50 4 7.50 52.50
verdict "a projection over VERI_RUN_BUDGET exits 1 printing spent, steps remaining, median and projection"

: > "$work/.tdd/events.jsonl"
step_leaves "step one"   1.50 1.50 1.50 1.50 1.50 1.50
step_leaves "step two"   0.50 0.50 0.50 0.50 0.50 0.50
step_leaves "step three" 1.00 1.20 1.20 1.20 1.20 1.20
step_leaves "step four"  0.50 0.90 0.90 0.90 0.90 0.90
run_affordable VERI_RUN_BUDGET=50 -- 5
expect_code 1
expect_figures 24.00 5 6.00 54.00
verdict "the median of an even count of steps logged out of order is the mean of the sorted middle two"

: > "$work/.tdd/events.jsonl"
three_full_steps
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 0
expect_silent
verdict "a projection within VERI_RUN_BUDGET exits 0 printing nothing"

: > "$work/.tdd/events.jsonl"
pin_step  "pin one"
step_leaves "step one"   1.00 1.00 1.00 1.00 1.00 1.00
pin_step  "pin two"
pin_step  "pin three"
step_leaves "step two"   1.00 1.00 1.50 1.50 1.50 1.50
pin_step  "pin four"
step_leaves "step three" 1.50 1.50 1.75 1.75 1.75 1.75
pin_step  "pin five"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 1
expect_figures 26.50 3 8.00 50.50
verdict "the median is over completed full steps only, so a log of mostly pins still projects at the full-step median"

: > "$work/.tdd/events.jsonl"
pin_step "pin one"
pin_step "pin two"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 3
expect_silent "a log of pins only"
printf '{"ts": 1, "issue": "453", "actor": "conductor", "event": "phase-start"}\n' > "$work/.tdd/events.jsonl"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 3
expect_silent "a log with no usage"
verdict "no completed full step, only pins or no usage at all, exits 3 printing nothing"

: > "$work/.tdd/events.jsonl"
three_full_steps
for arg in "" two 1.5; do
  run_affordable VERI_RUN_BUDGET=50 -- ${arg:+"$arg"}
  expect_code 2
  expect_silent "<steps-remaining> '${arg:-missing}'"
done
verdict "a missing or non-whole-number <steps-remaining> exits 2 printing nothing"

rm -f "$work/.tdd/events.jsonl"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 2
expect_silent "a missing event log"
verdict "a missing .tdd/events.jsonl exits 2 printing nothing"

: > "$work/.tdd/events.jsonl"
three_full_steps
for budget in fifty -5 ""; do
  run_affordable VERI_RUN_BUDGET="$budget" -- 3
  expect_code 2
  expect_silent "VERI_RUN_BUDGET '$budget'"
done
verdict "a VERI_RUN_BUDGET that is not a non-negative decimal number exits 2 printing nothing"

: > "$work/.tdd/events.jsonl"
step_leaves "step one"   1.00 1.00 1.00 1.00 1.00 0.50
step_leaves "step two"   1.00 1.00 1.00 1.00 1.00 0.80
step_leaves "step three" 1.00 1.00 1.00 1.00 1.00 1.00
step_leaves "step four"  1.00 1.00 1.00 1.00 1.00 1.10
step_leaves "step five"  1.00 1.00 1.00 1.00 1.00 1.20
step_leaves "step six"   1.00 1.00 1.00 1.00 1.00 1.40
step_leaves "step seven" 1.00 1.00 1.00 1.00 1.00 1.56
step_leaves "step eight" 1.00 1.00 1.00 1.00 1.00 1.80
run_affordable VERI_RUN_BUDGET=60 -- 1
expect_code 0
expect_silent "a run at 8 of 9 steps"
verdict "a run at 8 of 9 steps with one median step left and a ceiling above the projection exits 0"

: > "$work/.tdd/events.jsonl"
step_leaves "step one" 1.00 1.00 1.00 1.00 1.00 2.00
step_leaves "step two" 1.00 1.00 1.00 1.00 2.00 2.00
run_affordable VERI_RUN_BUDGET=50 -- 10
expect_code 1
expect_figures 15.00 10 7.50 90.00
verdict "a run early in a long plan whose projection exceeds VERI_RUN_BUDGET exits 1 while spent is still under it"

finish
