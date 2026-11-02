#!/bin/sh
# rerun-alone.sh — rerun the test files a red run names, each alone: a shim over veri/rerun_alone.py.
#
# Usage:   rerun-alone.sh <alone-cmd> <red-output-file>
# Exit:    0 every file passes alone; 2 bad arguments, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/rerun_alone.py" "$@"
