#!/bin/sh
# dispatch.sh — run the dev session's launch-and-wait loop: a shim over veri/dispatch.py.
#
# Usage:   dispatch.sh [--target <N>]   (N a whole number >= 0; --target 0 holds dispatch: keeps watching and reporting exits, launches nothing)
#
# No --target: N and the launch order come from .tdd/role-dev.state in the main working tree: its last n= line,
# overridden by an unexpired timed-n line, and each override line pulls the issue it names to the front.
# Exit:    2 bad arguments, or no --target and .tdd/role-dev.state unreadable
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/dispatch.py" "$@"
