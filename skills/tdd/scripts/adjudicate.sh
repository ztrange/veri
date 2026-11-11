#!/bin/sh
# adjudicate.sh — the exit-2 judgment budget and record: a shim over veri/adjudicate.py.
#
# Reads VERI_ADJUDICATE_BUDGET (default 2).
#
# usage: adjudicate.sh --check-budget | left <n> | record <n> <cause> <leaf-output>
# Exit:    2 no argument or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/adjudicate.py" "$@"
