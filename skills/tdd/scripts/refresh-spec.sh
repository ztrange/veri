#!/bin/sh
# refresh-spec.sh — re-capture the blind spec and rewrite <spec-file> when it changed: a shim over veri/refresh_spec.py.
#
# Usage:   refresh-spec.sh <n> <spec-file>
# Exit:    0 rewritten to the live capture; 1 the criteria checkbox count differs, file untouched;
#          2 bad arguments, or no answer from gh; 3 identical, nothing to do
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/refresh_spec.py" "$@"
