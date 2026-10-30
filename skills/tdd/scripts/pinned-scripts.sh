#!/bin/sh
# pinned-scripts.sh — print the directory holding one run's pinned scripts: a shim over veri/pinned_scripts.py.
#
# Usage:   pinned-scripts.sh <issue-number>
# Exit:    0 printed; 2 absent (stderr names the pin and the git archive recovery), or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pinned_scripts.py" "$@"
