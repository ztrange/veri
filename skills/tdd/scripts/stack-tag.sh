#!/bin/sh
# stack-tag.sh — cut the tags of a landed slice, one per issue that changed behaviour: a shim over veri/stack_tag.py.
#
# usage:   stack-tag.sh <slice-pr-url> [--message <n>=<text>]...   (run in the target repository's clone)
# Exit:    0 every owed tag cut or already there; 1 reserved: no path returns it yet; 2 no answer, or bad arguments; 3 no issue owes a tag
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_tag.py" "$@"
