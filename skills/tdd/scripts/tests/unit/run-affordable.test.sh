#!/usr/bin/env bash
# Tests for scripts/run-affordable.sh — can this run still afford to finish? Run from the
# run's worktree with the number of steps still to go, it projects the run's spend so far
# plus that many steps at the median completed full step's cost against VERI_RUN_BUDGET.
# Every fixture here is a hand-written .tdd/events.jsonl, the log step-cost.sh reads.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
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
three_full_steps
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 0
expect_silent
verdict "a projection within VERI_RUN_BUDGET exits 0 printing nothing"

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
run_affordable -- two
expect_code 2
expect_silent "<steps-remaining> 'two'"
printf '%s\n' "run-affordable.sh: <steps-remaining> is not a whole number: 'two'" \
  "usage: run-affordable.sh <steps-remaining> (a whole number)" > "$work/want-stderr"
cmp -s "$work/want-stderr" "$work/stderr" ||
  problems+="    want stderr '$(cat "$work/want-stderr")', got '$err'"$'\n'
verdict "run-affordable.sh two exits 2 with nothing on stdout and the refusal then the usage line on stderr"

: > "$work/.tdd/events.jsonl"
three_full_steps
run_affordable VERI_RUN_BUDGET=50 -- 4
in_place="$code $out"
in_place_work="$work"
links="$(scratch_dir)"
ln -s "$(cd "$HERE/../../.." && pwd)" "$links/skill"
work="$(scratch_dir)"
mkdir -p "$work/.tdd"
cp "$in_place_work/.tdd/events.jsonl" "$work/.tdd/events.jsonl"
RUN_AFFORDABLE="$links/skill/scripts/run-affordable.sh" run_affordable VERI_RUN_BUDGET=50 -- 4
expect_code 1
expect_figures 22.50 4 7.50 52.50
[[ "$code $out" == "$in_place" ]] ||
  problems+="    want '$in_place' as in place, got '$code $out' through the symlink"$'\n'
rm "$work/.tdd/events.jsonl"
RUN_AFFORDABLE="$links/skill/scripts/run-affordable.sh" run_affordable VERI_RUN_BUDGET=50 -- 4
expect_code 2
expect_silent "a directory with no event log"
grep -F -- "cannot read .tdd/events.jsonl in $work " <<< "$err" > /dev/null ||
  problems+="    want stderr naming '$work', got '$err'"$'\n'
work="$in_place_work"
verdict "run through a symlink to the skill directory from another working directory, it answers as in place and reads that directory's event log"

finish
