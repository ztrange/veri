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

# full_step <step> <dollars…> — the `usage` events of one completed step, one per leaf, each
# carrying the dollars given, appended to the fixture log.
full_step() {
  local step="$1" d; shift
  for d in "$@"; do
    printf '{"ts": 1, "issue": "453", "actor": "developer", "phase": "red", "step": "%s", "event": "usage", "total_cost_usd": "%s"}\n' \
      "$step" "$d" >> "$work/.tdd/events.jsonl"
  done
}

# 1. three completed full steps of six leaves each, costing 5.25, 7.50 and 9.75: spent is
#    22.50 and the median full step 7.50, so four steps still to go project 22.50 + 4 × 7.50
#    = 52.50, over a 50 ceiling. The run cannot afford to finish: exit 1, and stdout carries
#    the four figures it decided on — spent, steps remaining, median and projection. No
#    figure is another's substring, so each is read on its own.
: > "$work/.tdd/events.jsonl"
full_step "step one"   0.25 1.00 1.00 1.00 1.00 1.00
full_step "step two"   0.50 1.00 1.50 1.50 1.50 1.50
full_step "step three" 0.75 1.50 1.50 2.00 2.00 2.00
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
full_step "step one"   1.50 1.50 1.50 1.50 1.50 1.50
full_step "step two"   0.50 0.50 0.50 0.50 0.50 0.50
full_step "step three" 1.00 1.20 1.20 1.20 1.20 1.20
full_step "step four"  0.50 0.90 0.90 0.90 0.90 0.90
run_affordable VERI_RUN_BUDGET=50 -- 5
expect_code 1
expect_figures 24.00 5 6.00 54.00
verdict "the median of an even count of steps logged out of order is the mean of the sorted middle two"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
