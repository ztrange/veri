#!/bin/sh
# plan-reverify.sh — decide whether a resume must re-verify the plan: a shim over veri/plan_reverify.py.
#
# usage: plan-reverify.sh <ledger-file>
# Exit:    0 verify-plan owed (a plan: commit at or after the last verify-plan PASS, or no PASS)
#          2 a missing argument, a ledger not named issue-<n>, or no plan: commit in history
#          3 unchanged (no plan: commit at or after the last verify-plan PASS)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/plan_reverify.py" "$@"
