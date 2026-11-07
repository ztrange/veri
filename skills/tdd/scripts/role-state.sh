#!/bin/sh
# role-state.sh — a role's own state file: a shim over veri/role_state.py.
#
# Usage:   role-state.sh <coord|dev> set <field> <value> | show
# Exit:    0 written or shown; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/role_state.py" "$@"
