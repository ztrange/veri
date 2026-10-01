#!/usr/bin/env bash
# time-budget.sh — the two tunables that decide whether a recorded test-command run is
# worth a word in the narration. tier-usual.sh says what a
# tier usually costs; these say how far past usual — or past a fixed ceiling for the unit
# tier, which has a budget in its own right rather than only a history — is far enough.
#
# Usage:   time-budget.sh          # prints the resolved seconds, then the resolved ratio
#
# VERI_UNIT_BUDGET (default 10) is seconds: the unit tier is the fast one, and a fast tier
# that stopped being fast is over budget whatever its history says. VERI_TIME_WARN_RATIO
# (default 1.5) is a multiplier on the tier's usual, and applies to every tier.
#
# The no-argument call is the preflight one, at the point `refactor-budget.sh 0` already
# occupies in SKILL.md step 5: a misconfigured run is refused before any leaf is launched
# rather than mid-loop. A value that is not a number is exactly that misconfiguration, so
# it fails closed the way refactor-budget.sh does — a diagnostic naming the variable at
# fault on stderr, exit 2, and nothing at all on stdout, so a conductor capturing stdout
# cannot read a diagnostic as a budget. Both are validated before either is printed, for
# that last reason.
set -euo pipefail

source "$(dirname "$0")/lib/exit-contract.sh"

budget="${VERI_UNIT_BUDGET:-10}"
ratio="${VERI_TIME_WARN_RATIO:-1.5}"

number='^[0-9]+(\.[0-9]+)?$'

if [[ ! "$budget" =~ $number ]]; then
  echo "time-budget: VERI_UNIT_BUDGET must be a number of seconds: $budget" >&2
  exit 2
fi

if [[ ! "$ratio" =~ $number ]]; then
  echo "time-budget: VERI_TIME_WARN_RATIO must be a number: $ratio" >&2
  exit 2
fi

echo "$budget"
echo "$ratio"
