#!/bin/sh
# ready-check.sh — report whether veri can run in a repository: a shim over veri/ready_check.py.
#
# Usage:   ready-check.sh [--no-suites] [--no-permissions] [repo-root]   (preflight's call passes the options)
# Exit:    0 ready; 1 a row failed; 2 no answer — not a git repository, bad arguments;
#          3 a test tier is still running (last line `waiting on ready-<tier>`) — call again
#
# --no-suites runs no test tier; --no-permissions skips the permission rows and their probes, as preflight's
# call does while its .tdd/permissions-checked record is current.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/ready_check.py" "$@"
