#!/bin/sh
# role-growth.sh — the dev session's context growth since recovery: a shim over veri/role_growth.py.
#
# Usage:   role-growth.sh dev [--lane <lane>]
# Exit:    0 read; 2 no reading could be made, or a role other than dev
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/role_growth.py" "$@"
