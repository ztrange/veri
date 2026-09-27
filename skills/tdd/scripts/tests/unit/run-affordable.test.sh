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
pass=0 fail=0 problems=""

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# run_affordable [env assignments…] -- [args…] — run the script from the run's worktree with
# both budget names cleared from the environment, then the assignments given, so an
# operator's ambient VERI_* cannot change what a case sees; leaves its stdout in `out`, its
# exit code in `code` and its stderr in `err`.
run_affordable() {
  local assigns=()
  while [[ $# -gt 0 && "$1" != "--" ]]; do assigns+=("$1"); shift; done
  [[ $# -gt 0 ]] && shift
  out="$(cd "$work" && env -u VERI_STEP_BUDGET -u VERI_RUN_BUDGET "${assigns[@]}" \
    "$RUN_AFFORDABLE" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# expect_code <code> — add to the case's `problems` unless the run just made exited <code>.
expect_code() {
  if [[ "$code" != "$1" ]]; then
    problems+="    want exit $1, got exit $code and stdout '$out' (stderr '$err')"$'\n'
  fi
}

# expect_figure <what> <figure> — add to the case's `problems` unless stdout carries <figure>
# as a word of its own; <what> names the figure in the line.
expect_figure() {
  grep -Fw -- "$2" <<< "$out" > /dev/null ||
    problems+="    want stdout to carry $1 '$2', got '$out'"$'\n'
}

# expect_figures <spent> <remaining> <median> <projection> — expect_figure for each of the
# four figures a projection over the ceiling prints, in the order the script prints them.
expect_figures() {
  expect_figure "spent" "$1"
  expect_figure "steps remaining" "$2"
  expect_figure "the median" "$3"
  expect_figure "the projection" "$4"
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

# step_leaves <step> <dollars…> — the `usage` events of one completed step, one per leaf,
# each carrying the dollars given, appended to the fixture log. Six leaves make a full step
# and two a pin (pin_step): the count is what run-affordable.sh tells them apart by.
step_leaves() {
  local step="$1" d; shift
  for d in "$@"; do
    printf '{"ts": 1, "issue": "453", "actor": "developer", "phase": "red", "step": "%s", "event": "usage", "total_cost_usd": "%s"}\n' \
      "$step" "$d" >> "$work/.tdd/events.jsonl"
  done
}

# pin_step <step> — the two `usage` events of one pin, a step already satisfied: its red leaf
# and its verify-pin, at 0.25 each, so the step costs 0.50 against a full step's six leaves.
pin_step() { step_leaves "$1" 0.25 0.25; }

# 1. three completed full steps of six leaves each, costing 5.25, 7.50 and 9.75: spent is
#    22.50 and the median full step 7.50, so four steps still to go project 22.50 + 4 × 7.50
#    = 52.50, over a 50 ceiling. The run cannot afford to finish: exit 1, and stdout carries
#    the four figures it decided on — spent, steps remaining, median and projection. No
#    figure is another's substring, so each is read on its own.
: > "$work/.tdd/events.jsonl"
step_leaves "step one"   0.25 1.00 1.00 1.00 1.00 1.00
step_leaves "step two"   0.50 1.00 1.50 1.50 1.50 1.50
step_leaves "step three" 0.75 1.50 1.50 2.00 2.00 2.00
run_affordable VERI_RUN_BUDGET=50 -- 4
expect_code 1
expect_figures 22.50 4 7.50 52.50
verdict "a projection over VERI_RUN_BUDGET exits 1 printing spent, steps remaining, median and projection"

# 2. four completed full steps, logged out of cost order at 9.00, 3.00, 7.00 and 5.00: the
#    median of an even count is the mean of the middle two once sorted, (5.00 + 7.00) / 2 =
#    6.00, so five steps to go project 24.00 + 5 × 6.00 = 54.00 over a 50 ceiling — exit 1.
#    Read in log order the middle two are 3.00 and 7.00, a 5.00 median and a 49.00
#    projection under the ceiling; so the sort and the even-count mean are both what this
#    case needs.
: > "$work/.tdd/events.jsonl"
step_leaves "step one"   1.50 1.50 1.50 1.50 1.50 1.50
step_leaves "step two"   0.50 0.50 0.50 0.50 0.50 0.50
step_leaves "step three" 1.00 1.20 1.20 1.20 1.20 1.20
step_leaves "step four"  0.50 0.90 0.90 0.90 0.90 0.90
run_affordable VERI_RUN_BUDGET=50 -- 5
expect_code 1
expect_figures 24.00 5 6.00 54.00
verdict "the median of an even count of steps logged out of order is the mean of the sorted middle two"

# 3. case 1's three completed full steps — spent 22.50, median 7.50 — with three steps to go
#    project 22.50 + 3 × 7.50 = 45.00, within a 50 ceiling. The run can afford to finish:
#    exit 0, and stdout is empty, so a caller reads the answer from the code alone.
: > "$work/.tdd/events.jsonl"
step_leaves "step one"   0.25 1.00 1.00 1.00 1.00 1.00
step_leaves "step two"   0.50 1.00 1.50 1.50 1.50 1.50
step_leaves "step three" 0.75 1.50 1.50 2.00 2.00 2.00
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 0
[[ -z "$out" ]] || problems+="    want empty stdout, got '$out'"$'\n'
verdict "a projection within VERI_RUN_BUDGET exits 0 printing nothing"

# 4. three completed full steps costing 6.00, 8.00 and 10.00 among five pins of two leaves
#    at 0.50 each: spent is 24.00 + 2.50 = 26.50 and the median full step 8.00, so three
#    steps to go project 26.50 + 3 × 8.00 = 50.50, over a 50 ceiling — exit 1. A median over
#    all eight steps is the mean of two pins, 0.50, projecting 28.00 under the ceiling; so
#    only a median over the full steps, told apart by their leaf count, parks this run.
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

# 5. no completed full step, so there is no median to project with: first a log of two pins
#    and nothing else, then a log holding no `usage` event at all. Each exits 3 — nothing to
#    decide, not an answer — with stdout empty, so a caller never reads a figure off it.
: > "$work/.tdd/events.jsonl"
pin_step "pin one"
pin_step "pin two"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 3
[[ -z "$out" ]] || problems+="    want empty stdout for a log of pins only, got '$out'"$'\n'
printf '{"ts": 1, "issue": "453", "actor": "conductor", "event": "phase-start"}\n' > "$work/.tdd/events.jsonl"
run_affordable VERI_RUN_BUDGET=50 -- 3
expect_code 3
[[ -z "$out" ]] || problems+="    want empty stdout for a log with no usage, got '$out'"$'\n'
verdict "no completed full step, only pins or no usage at all, exits 3 printing nothing"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
