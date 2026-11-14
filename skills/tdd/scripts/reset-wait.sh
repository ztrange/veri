#!/bin/sh
# reset-wait.sh — block until a role's reset event: a shim over veri/reset_wait.py.
#
# Usage:   reset-wait.sh marker|recovered|idle <coord|dev> [--lane <lane>] [<seconds>]
# Exit:    0 the event came; 1 not recovered in time; 2 bad arguments; 3 no marker
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/reset_wait.py" "$@"
