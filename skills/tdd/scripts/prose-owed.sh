#!/bin/sh
# prose-owed.sh — print each prose unit that owes a grade: a shim over veri/prose_owed.py.
#
# Usage:   prose-owed.sh <repo-root>
# Exit:    0 nothing owed; 1 something printed; 2 bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/prose_owed.py" "$@"
