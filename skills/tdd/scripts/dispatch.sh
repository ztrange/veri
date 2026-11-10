#!/bin/sh
# dispatch.sh — run the dev session's launch-and-wait loop: a shim over veri/dispatch.py.
#
# Usage:   dispatch.sh --target <N>   (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing)
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/dispatch.py" "$@"
