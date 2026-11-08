#!/bin/sh
# dispatch.sh — run the dev session's launch-and-wait loop: a shim over veri/dispatch.py.
#
# Usage:   dispatch.sh --target <N>
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/dispatch.py" "$@"
