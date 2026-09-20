#!/usr/bin/env bash
# Unit tests for scripts/over-budget.sh — the check that turns a recorded test-command run
# into a yes or no (issue #342, part of PRD #335). timed-test-run.sh records a tier and its
# seconds, tier-usual.sh says what that tier usually costs and time-budget.sh resolves the
# two tunables; this is the one that compares them, so that the conductor's narration has
# something to say a word about.
#
# Contract under test (this step only — the unit tier's fixed ceiling, not yet the ratio):
#   over-budget.sh <tier> <seconds> <usual>
#       → exit 0 when the run is over budget, exit 1 when it is not. Exit 1 is the clean
#         negative CLAUDE.md's "Exit codes are the API" table reserves for a real answer:
#         the check ran and said no.
#   A unit-tier run is over budget when its seconds exceed VERI_UNIT_BUDGET (default 10);
#   at or under that figure it is not.
#
# Every number here is fabricated and passed in as an argument, so nothing waits on a clock
# and the case costs one process per invocation (CLAUDE.md, "Testing idiom" — the seconds a
# run really took are recorded, never asserted on). The `usual` argument is 100 throughout,
# far enough above the seconds that the ratio rule cannot be what answers: this case is
# about the unit tier's own ceiling and must fail if that ceiling is missing, not pass
# because some other comparison happened to agree.
#
# Run: skills/tdd/scripts/tests/over-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK="$HERE/../over-budget.sh"
pass=0 fail=0

report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# `probe <budget> <seconds> <want>` runs the check on a fabricated unit-tier run of
# <seconds> against <budget>, and records a problem unless it exits <want>. An empty
# <budget> means the variable is cleared with `env -u` so the script's own default of 10 s
# answers — cleared rather than merely unset by the caller, which hermetic-suites.test.sh
# requires of every suite here. The `usual` argument is the fixed 100 the header explains.
probe() {
  local budget="$1" seconds="$2" want="$3" code verdict against
  if [[ -n "$budget" ]]; then
    VERI_UNIT_BUDGET="$budget" "$CHECK" unit "$seconds" 100 && code=0 || code=$?
    against="VERI_UNIT_BUDGET=$budget"
  else
    env -u VERI_UNIT_BUDGET "$CHECK" unit "$seconds" 100 && code=0 || code=$?
    against="the default 10 s budget"
  fi
  [[ "$want" == 0 ]] && verdict="over budget" || verdict="not over budget"
  [[ "$code" == "$want" ]] ||
    problems+=("unit $seconds s against $against: want exit $want ($verdict), got $code")
}

# 1. The whole of this step's criterion, as one case: three fabricated unit-tier runs
#    against the default budget of 10 s — one over it, one exactly at it, one under — and a
#    fourth against a budget set low by the environment, so that a check which had hardcoded
#    10 rather than reading VERI_UNIT_BUDGET is not a pass.
name="over-budget.sh: a unit-tier run over VERI_UNIT_BUDGET is over budget, at or under it is not"
problems=()

probe "" 12 0
probe "" 10 1
probe "" 4  1
probe 3  4  0

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
