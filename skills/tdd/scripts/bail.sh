#!/bin/sh
# bail.sh — BAIL.md sub-steps 1-8 in one call: a shim over veri/bail.py.
#
# Usage:   bail.sh <n> <cause> <phase> --note-file <path> [--attempt <k>]
# Exit:    2 bad arguments, a usage line on stderr, no call made
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/bail.py" "$@"
