#!/bin/sh
# mutation-probe.sh — mutate a file, run a command against the mutation, restore the file: a shim over veri/mutation_probe.py.
#
# Usage:   mutation-probe.sh <file> <old> <new> -- <command…>
# Exit:    2 bad arguments, or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/mutation_probe.py" "$@"
