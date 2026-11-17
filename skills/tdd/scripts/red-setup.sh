#!/bin/sh
# red-setup.sh — the setup a verified Red's case needed, and the run's worst step as a refactor candidate: a shim over veri/red_setup.py.
#
# usage:   red-setup.sh record <n> < <red-report>
#          red-setup.sh worst <n> <owed-file>
# Exit:    record: 0 a red-setup event written for the ledger's current step; 3 no SETUP: line (nothing written);
#          2 a malformed SETUP: line, no current step, or bad arguments
#          worst: 0 one testability not-done row recorded (an earlier one replaced); 3 no step's latest count over
#          VERI_SETUP_THRESHOLD (default 3; an earlier row dropped, nothing recorded); 2 a threshold that is not a whole number, or an owed file it cannot write
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/red_setup.py" "$@"
