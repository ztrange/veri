#!/bin/sh
# preflight.sh — run PREFLIGHT.md's steps for a fresh run: a shim over veri/preflight.py.
#
# Usage:   preflight.sh <n> <slug>
# Exit:    2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/preflight.py" "$@"
