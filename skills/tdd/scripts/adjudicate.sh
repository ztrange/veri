#!/bin/sh
# adjudicate.sh — the exit-2 judgment budget and record: a shim over veri/adjudicate.py.
#
# Reads VERI_ADJUDICATE_BUDGET (default 2) and VERI_DEVIATION_BUDGET (default 1).
#
# usage: adjudicate.sh --check-budget | left <n> | deviation-left <n> | record <n> <cause> <leaf-output>
# Exit:    0 retry or budget left, 1 bail or route, 2 no argument or no answer,
#          3 budget spent, 4 deviate (a cause ADJUDICATE.md's Waivable rules names)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/adjudicate.py" "$@"
