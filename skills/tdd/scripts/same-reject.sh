#!/bin/sh
# same-reject.sh — compare two rejections' REASON: lines: a shim over veri/same_reject.py.
#
# usage: same-reject.sh <previous-reason-file> <current-reason-file>
# Exit:    0 the REASON: lines are equal after collapsing whitespace; 1 they differ;
#          2 a missing argument, a missing file, or a file with no REASON: line
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/same_reject.py" "$@"
