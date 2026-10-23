#!/bin/sh
# tier-usual.sh — what one tier's test-command run usually costs: a shim over veri/tier_usual.py.
#
# Prints the median `seconds` of the tier's last 10 `test-run` events in `.tdd/events.jsonl`,
# read relative to the working directory; an even window prints the mean of its two middles.
#
# usage: tier-usual.sh <tier>
# Exit:    0 the median on stdout; 1 no answer from the log (no test-run event for the tier, a missing
#          or malformed log), nothing on stdout; 2 a missing argument
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/tier_usual.py" "$@"
