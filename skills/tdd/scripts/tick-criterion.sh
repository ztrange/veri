#!/bin/sh
# tick-criterion.sh — tick one acceptance-criterion checkbox in an issue body: a shim over veri/tick_criterion.py.
#
# Pure text transform: reads the issue body on stdin and writes the updated body to
# stdout. Flips the FIRST unchecked GitHub task-list item ("- [ ]") whose text contains
# <matcher> (a literal substring; empty matcher matches the first unchecked box) to
# "- [x]". All other lines are passed through verbatim.
#
# Exit: 0 if a box was ticked, 3 if no unchecked box matched (body emitted unchanged).
#
# Usage: tick-criterion.sh <matcher>  < body.md > new-body.md
exec python3 "$(dirname "$0")/veri/tick_criterion.py" "$@"
