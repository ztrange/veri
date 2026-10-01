#!/usr/bin/env bash
# refactor-budget.sh — bound the refactor loop, so a step costs the same on every run.
#
# Given the number of transforms done so far as $1, say whether another one may run:
# exit 0 while <count> is below VERI_REFACTOR_BUDGET (default 5), exit 3 once the budget
# is spent. A one-line status goes to stdout either way, so the conductor can mirror it.
#
# A budget that is not a whole number >= 0 is a misconfigured run, not a decision: fail
# closed like classify-bail.sh does on an unrecognised cause — a diagnostic on stderr and
# exit 2, with nothing on stdout, so a conductor mirroring stdout cannot mistake it for a
# real status.
#
# The count gets the same treatment, for the same reason: a malformed call is not a
# decision either.
#
# With --issue, the per-issue structural pass is bounded instead, by
# VERI_ISSUE_REFACTOR_BUDGET (default 10).
#
# Usage:   refactor-budget.sh [--issue] <count>   # <count> a whole number >= 0
set -euo pipefail

USAGE="usage: refactor-budget.sh [--issue] <count>"
budget_var=VERI_REFACTOR_BUDGET
budget="${VERI_REFACTOR_BUDGET:-5}"
if [[ "${1:-}" == --issue ]]; then
  shift
  budget_var=VERI_ISSUE_REFACTOR_BUDGET
  budget="${VERI_ISSUE_REFACTOR_BUDGET:-10}"
fi
count="${1:-}"

if [[ ! "$budget" =~ ^[0-9]+$ ]]; then
  echo "refactor-budget: $budget_var must be a whole number >= 0: $budget" >&2
  exit 2
fi

if [[ ! "$count" =~ ^[0-9]+$ ]]; then
  echo "refactor-budget: <count> must be a whole number >= 0: $count" >&2
  echo "$USAGE" >&2
  exit 2
fi

if [[ "$count" -lt "$budget" ]]; then
  echo "refactor $count/$budget — another transform may run"
else
  echo "refactor $count/$budget — budget spent"
  exit 3
fi
