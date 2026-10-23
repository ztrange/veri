#!/bin/sh
# step-cost.sh — what one step of the run has spent on leaves so far, read off the run's `usage` events: a shim over veri/step_cost.py.
#
# usage: step-cost.sh <step-text> | --run | --steps    (run from the run's worktree)
#          <step-text> sums the usage events whose step is <step-text>, to two decimals.
#          --run sums every usage event; --steps prints one `<dollars> <leaves>` line per step, in first-mention order.
# Exit:    0 a figure printed; 2 a bad argument, or .tdd/events.jsonl unreadable; 3 nothing to do — no usage event for it
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/step_cost.py" "$@"
