#!/bin/sh
# drop-ledger-step.sh — remove one unchecked ledger step, in place: a shim over veri/drop_ledger_step.py.
#
# usage: drop-ledger-step.sh <ledger-file> <step-substring>
# Exit:    0 the step was removed
#          1 no unchecked step matches, or more than one
#          2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/drop_ledger_step.py" "$@"
