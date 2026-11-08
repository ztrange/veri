#!/bin/sh
# role-state.sh — a role's own state file: a shim over veri/role_state.py.
#
# Usage:   role-state.sh <coord|dev> [--lane <lane>] set <n|lane> <value>
#                       | add <decision|message|override|timed-n> <text>
#                       | drop <decision|message|override|timed-n> <id> | show | recovered
# Exit:    0 written or shown; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/role_state.py" "$@"
