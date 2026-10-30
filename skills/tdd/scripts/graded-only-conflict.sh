#!/bin/sh
# graded-only-conflict.sh — does HEAD conflict with origin's default branch only in GRADED files?: a shim over veri/graded_only_conflict.py.
#
# Usage:   graded-only-conflict.sh
# Exit:    0 yes; 1 no conflict, or one touching any other path; 2 no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/graded_only_conflict.py" "$@"
