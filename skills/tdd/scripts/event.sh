#!/bin/sh
# event.sh — append one line to the run's event log, .tdd/events.jsonl under the working directory: a shim over veri/event.py.
#
# usage: event.sh <event> [key=value …]
# Exit:    0 the line was appended; 1 .tdd or the log could not be written, or the awake clock exited 1;
#          2 a missing <event>, a refused structural-pass mark, or no answer; 3 the awake clock exited 3
exec python3 "$(dirname "$0")/veri/event.py" "$@"
