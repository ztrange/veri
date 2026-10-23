#!/bin/sh
# step-budget.sh — the two money budgets: a shim over veri/step_budget.py.
#
# VERI_STEP_BUDGET (default 12) is what one step may spend, VERI_RUN_BUDGET (default 120) what the
# whole run may; each must be a non-negative decimal number.
#
# usage: step-budget.sh (takes no arguments)
#          prints the resolved step budget, then the resolved run budget, one per line.
# Exit:    0 both printed; 2 an argument, or a budget that is not a non-negative decimal number,
#          nothing on stdout
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/step_budget.py" "$@"
