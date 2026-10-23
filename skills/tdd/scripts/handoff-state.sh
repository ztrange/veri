#!/bin/sh
# handoff-state.sh — print a snapshot of the run state for a context reset: a shim over veri/handoff_state.py.
#
# Usage:   handoff-state.sh
# Exit:    0 the snapshot printed; 2 no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/handoff_state.py" "$@"
