#!/bin/sh
# script-help.sh — print one script's SCRIPTS.md entry: a shim over veri/script_help.py.
#
# usage: script-help.sh <name>
# Exit:    2 no argument
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/script_help.py" "$@"
