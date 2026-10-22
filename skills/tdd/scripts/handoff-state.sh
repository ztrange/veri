#!/bin/sh
# handoff-state.sh — print a snapshot of the run state for a context reset: a shim over veri/handoff_state.py.
#
# Usage:   handoff-state.sh
# Exit:    0 the snapshot printed; 2 no answer
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/handoff_state.py" "$@"
