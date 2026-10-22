#!/bin/sh
# ledger-growth.sh — check a ledger's growth against the plan commit's: a shim over veri/ledger_growth.py.
#
# usage: ledger-growth.sh <plan-ledger-file> <ledger-file>
# Exit:    0 every step line the plan did not hold carries ⟦added⟧;
#          1 a step line the plan did not hold lacks ⟦added⟧, named on stderr;
#          2 a missing argument or an unreadable file
exec python3 "$(dirname "$0")/veri/ledger_growth.py" "$@"
