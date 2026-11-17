#!/bin/sh
# metrics.sh — what one issue's run cost, read back out of `.tdd/events.jsonl` in the working directory: a shim over veri/metrics.py.
#
# usage: metrics.sh <issue-number> [--json]
#        The planned-step count is read from `.tdd/issue-<issue-number>.md`. --json prints the same figures as one
#        JSON object (keys run, phases, steps, conductor, total) in place of the markdown report.
# Exit:    0 the report, or the object, on stdout;
#          2 no issue number, an empty one, any other argument after it, or a missing or unreadable log — one line on
#          stderr, nothing on stdout
#
# With no event of the issue in the local log, the report is read from the events origin's refs/veri/runs/<n>
# carries (push-branch.sh pushes them), so another machine's run is reported here too.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/metrics.py" "$@"
