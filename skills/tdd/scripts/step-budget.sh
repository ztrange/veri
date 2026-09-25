#!/usr/bin/env bash
# step-budget.sh — the two money budgets (issue #449, part of #447): VERI_STEP_BUDGET, what
# one step may spend, and VERI_RUN_BUDGET, what the whole run may.
#
# Usage:   step-budget.sh          # prints the resolved step budget, then the resolved run budget
#
# The shape is time-budget.sh's, for the same reason: the no-argument call is the preflight
# one, at the point `refactor-budget.sh 0` already occupies in SKILL.md step 5.
set -euo pipefail

step="${VERI_STEP_BUDGET-12}"
run="${VERI_RUN_BUDGET-120}"

number='^[0-9]+(\.[0-9]+)?$'

if [[ ! "$step" =~ $number ]]; then
  echo "step-budget: VERI_STEP_BUDGET must be a non-negative decimal number: $step" >&2
  exit 2
fi
if [[ ! "$run" =~ $number ]]; then
  echo "step-budget: VERI_RUN_BUDGET must be a non-negative decimal number: $run" >&2
  exit 2
fi

echo "$step"
echo "$run"
