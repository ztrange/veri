#!/bin/sh
# metrics.sh — what one issue's run cost, read back out of `.tdd/events.jsonl` in the working directory: a shim over veri/metrics.py.
#
# usage: metrics.sh <issue-number>
#        The planned-step count is read from `.tdd/issue-<issue-number>.md`; arguments after the first are ignored.
# Exit:    0 the markdown report on stdout; 1 a missing or malformed log, or a report cut short — a traceback on stderr;
#          2 no issue number, or an empty one — nothing on stdout
#
# With no event of the issue in the local log, the report is read from the events origin's refs/veri/runs/<n>
# carries (push-branch.sh pushes them), so another machine's run is reported here too.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/metrics.py" "$@"
