#!/bin/sh
# role-state.sh — the dev session's own state file: a shim over veri/role_state.py.
#
# Usage:   role-state.sh dev [--lane <lane>] set <n|lane> <value>
#                       | add <decision|message|override|timed-n> <text>
#                       | drop <decision|message|override|timed-n> <id> | show | recovered
# Exit:    0 written or shown; 2 bad arguments (a role other than dev included)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/role_state.py" "$@"
