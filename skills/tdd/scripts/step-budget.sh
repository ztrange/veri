#!/usr/bin/env bash
# step-budget.sh — the two money budgets: VERI_STEP_BUDGET, what
# one step may spend, and VERI_RUN_BUDGET, what the whole run may.
#
# Usage:   step-budget.sh          # prints the resolved step budget, then the resolved run budget
#
# The shape is time-budget.sh's, for the same reason: the no-argument call is the preflight
# one, at the point `refactor-budget.sh 0` already occupies in SKILL.md step 5.
set -euo pipefail

[[ $# -eq 0 ]] || { echo "usage: step-budget.sh (takes no arguments)" >&2; exit 2; }

step="${VERI_STEP_BUDGET-12}"
run="${VERI_RUN_BUDGET-120}"

number='^[0-9]+(\.[0-9]+)?$'

require_number() {
  if [[ ! "$2" =~ $number ]]; then
    echo "step-budget: $1 must be a non-negative decimal number: $2" >&2
    exit 2
  fi
}

require_number VERI_STEP_BUDGET "$step"
require_number VERI_RUN_BUDGET "$run"

echo "$step"
echo "$run"
