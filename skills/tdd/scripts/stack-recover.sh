#!/bin/sh
# stack-recover.sh — after a GitHub outage, push the stack's offline joins and the stack: a shim over
# veri/stack_recover.py.
#
# usage:   stack-recover.sh   (no arguments, run in the target repository's clone)
# Exit:    0 pushed, printing `<tip-sha> <tracking-pr-url>`; 1 a refused lease or a stack origin moved; 2 while
#          .tdd/github-outage exists, any argument, or no answer; 3 nothing joined offline or no stack named
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_recover.py" "$@"
