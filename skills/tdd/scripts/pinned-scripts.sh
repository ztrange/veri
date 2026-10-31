#!/bin/sh
# pinned-scripts.sh — print the directory holding run <n>'s pinned scripts: a shim over veri/pinned_scripts.py.
#
# Usage:   pinned-scripts.sh <n>
# Exit:    0 the directory printed; 2 no argument, or the directory is absent
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pinned_scripts.py" "$@"
