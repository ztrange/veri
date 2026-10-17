#!/usr/bin/env bash
# Unit tests for scripts/refactor-budget.sh — given the number of transforms done so far,
# it says whether another refactor leaf may run.
#
# Contract under test:
#   refactor-budget.sh <count>  → exit 0 while <count> is below VERI_REFACTOR_BUDGET
#                                 (default 5), exit 3 once the budget is spent;
#                                 a one-line status on stdout either way
#                                 (`refactor 5/5 — budget spent`).
#   VERI_REFACTOR_BUDGET=0      → exit 3 at count 0: the refactor loop is switched off.
#
# Run: scripts/tests/refactor-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUDGET="$HERE/../refactor-budget.sh"

source "$HERE/lib/harness.sh"


finish
