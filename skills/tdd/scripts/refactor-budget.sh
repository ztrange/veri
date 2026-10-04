#!/bin/sh
# refactor-budget.sh — bound the refactor loop: a shim over veri/refactor_budget.py.
#
# Given the number of transforms done so far as <count>, say whether another one may run, against
# VERI_REFACTOR_BUDGET (default 5); with --issue, the per-issue structural pass is bounded instead,
# by VERI_ISSUE_REFACTOR_BUDGET (default 3). A one-line status goes to stdout either way.
#
# usage: refactor-budget.sh [--issue] <count>   # <count> a whole number >= 0
# Exit:    0 <count> is below the budget; 2 a budget or <count> that is not a whole number >= 0,
#          nothing on stdout; 3 the budget is spent
exec python3 "$(dirname "$0")/veri/refactor_budget.py" "$@"
