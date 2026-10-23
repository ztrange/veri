#!/bin/sh
# session-cost.sh — what a day of Claude sessions cost, read from the session transcripts: a shim over veri/session_cost.py.
#
# usage: session-cost.sh --since <ISO date> [--json] [<transcript.jsonl> ...]
# Exit:  0 the day's cost printed; 1 a transcript record the reader could not parse; 2 a missing --since, no such transcript, no transcripts found, or no known model
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/session_cost.py" "$@"
