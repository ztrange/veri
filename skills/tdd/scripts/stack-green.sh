#!/bin/sh
# stack-green.sh — the newest commit of the stack branch that ends an issue and that CI passed, where a slice may be
# cut: a shim over veri/stack_green.py.
#
# usage:   stack-green.sh   (run in the target repository's clone; no arguments)
# Exit:    0 its sha printed: the newest commit of origin/<default>..origin/<stack>, read after a fetch, that is an issue
#          end (no issue named in a subject at or before it is named after it; a subject naming none belongs to the
#          nearest earlier issue) and is tested (its check runs, read from GitHub by sha, all completed, each success,
#          neutral or skipped, at least one success); 3 no commit qualifies (one stderr line), the newest 20 issue
#          ends read at most; 2 GitHub gave no answer, stack-branch.sh did not exit 0, or bad arguments
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_green.py" "$@"
