#!/bin/sh
# criterion-collisions.sh — name each changed file an acceptance criterion's text names: a shim over veri/criterion_collisions.py.
#
# Usage:   criterion-collisions.sh <spec-file> <base-sha>
# Exit:    0 none; 1 some printed; 2 bad arguments or no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/criterion_collisions.py" "$@"
