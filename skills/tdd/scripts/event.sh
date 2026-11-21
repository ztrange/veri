#!/bin/sh
# event.sh — append one line to the run's event log, .tdd/events.jsonl under the working directory: a shim over veri/event.py.
# The line's issue is VERI_ISSUE, else VERI_STATE_LABEL_ISSUE (the conductor's export), and an event with an issue
# also reaches that issue's run journal.
#
# With VERI_STATE_LABEL_ISSUE set, a bail labels that issue `bailed` and takes `pr-ready` off; a stop labels it `stopped`
# (each only when the repository has the label: veri never creates it);
# a resume takes `bailed` and `stopped` off (run-conductor.sh already took them and `pr-ready` off at launch).
#
# usage: event.sh <event> [key=value …]
# Exit:    0 the line was appended; 1 .tdd or the log could not be written, or the awake clock exited 1;
#          2 a missing <event>, a refused structural-pass mark, or no answer; 3 the awake clock exited 3
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/event.py" "$@"
