#!/bin/sh
# role-growth.sh — a role's context growth since recovery: a shim over veri/role_growth.py.
#
# Usage:   role-growth.sh <coord|dev> [--lane <lane>]
# Exit:    0 read; 2 no reading could be made
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/role_growth.py" "$@"
