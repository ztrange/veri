#!/bin/sh
# watch-runs.sh — block until a conductor that was live at start exits, then print one line: a shim over veri/watch_runs.py.
#
# Usage:   watch-runs.sh [--target <N>] [--max-wait <seconds>]
#          With --target, the queue is read at most once per VERI_WATCH_QUEUE_INTERVAL seconds (default 60).
#          On a rate-limit refusal it waits until the reset, making no gh call meanwhile.
# Exit:    0 an actionable line printed; 2 bad arguments, or the rate-limit reset is unobtainable or beyond --max-wait; 3 timeout
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/watch_runs.py" "$@"
