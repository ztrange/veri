#!/bin/sh
# restore-production.sh — leave the worktree with no change beyond HEAD except the given test paths: a shim over veri/restore_production.py.
#
# usage: restore-production.sh <test-path>...
# Exit:    0 restored; 2 a missing argument, or git refused
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/restore_production.py" "$@"
