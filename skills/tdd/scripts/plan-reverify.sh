#!/bin/sh
# plan-reverify.sh — decide whether a resume must re-verify the plan: a shim over veri/plan_reverify.py.
#
# usage: plan-reverify.sh <ledger-file>
# Exit:    0 verify-plan owed; 2 a missing argument
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/plan_reverify.py" "$@"
