#!/bin/sh
# ready-check.sh — report whether veri can run in a repository: a shim over veri/ready_check.py.
#
# Usage:   ready-check.sh [--no-suites] [repo-root]   (--no-suites: run no test tier, as preflight's call)
# Exit:    0 ready; 1 a row failed; 2 no answer — not a git repository, bad arguments;
#          3 a test tier is still running (last line `waiting on ready-<tier>`) — call again
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ready_check.py" "$@"
