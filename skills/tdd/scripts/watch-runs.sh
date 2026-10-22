#!/bin/sh
# watch-runs.sh — block until a conductor that was live at start exits, then print one line: a shim over veri/watch_runs.py.
#
# Usage:   watch-runs.sh [--target <N>] [--max-wait <seconds>]
# Exit:    0 an actionable line printed; 2 bad arguments; 3 timeout
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/watch_runs.py" "$@"
