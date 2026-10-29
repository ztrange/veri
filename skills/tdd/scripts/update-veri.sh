#!/bin/sh
# update-veri.sh — fast-forward veri's own clone to its upstream default branch: a shim over veri/update_veri.py.
#
# usage: update-veri.sh [--consent yes|no]
# Exit:    2 any other argument, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/update_veri.py" "$@"
