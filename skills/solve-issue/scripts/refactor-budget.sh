#!/usr/bin/env bash
# refactor-budget.sh — bound the refactor loop, so a step costs the same on every run.
#
# Given the number of transforms done so far as $1, say whether another one may run:
# exit 0 while <count> is below VERI_REFACTOR_BUDGET (default 2), exit 3 once the budget
# is spent. A one-line status goes to stdout either way, so the conductor can mirror it.
#
# Usage:   refactor-budget.sh <count>
set -euo pipefail

count="${1:-}"
budget="${VERI_REFACTOR_BUDGET:-2}"

if [[ "$count" -lt "$budget" ]]; then
  echo "refactor $count/$budget — another transform may run"
else
  echo "refactor $count/$budget — budget spent"
  exit 3
fi
