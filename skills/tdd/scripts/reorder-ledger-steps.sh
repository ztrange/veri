#!/bin/sh
# reorder-ledger-steps.sh — move one unchecked ledger step after another, in place: a shim over veri/reorder_ledger_steps.py.
#
# usage: reorder-ledger-steps.sh <ledger-file> <step-substring> before|after <anchor-substring>
# Exit:    0 the step moved
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reorder_ledger_steps.py" "$@"
