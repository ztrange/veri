#!/bin/sh
# red-setup.sh — the setup a verified Red's case needed, and the run's worst step as a refactor candidate: a shim over veri/red_setup.py.
#
# usage:   red-setup.sh record <n> < <red-report>
#          red-setup.sh worst <n> <owed-file>
# Exit:    record: 0 a red-setup event written for the ledger's current step; 3 no SETUP: line (nothing written);
#          2 a malformed SETUP: line, no current step, or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/red_setup.py" "$@"
