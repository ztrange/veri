#!/bin/sh
# comment.sh — post a routine comment rendered from the run's journal and ledger: a shim over veri/comment.py.
#
# usage: comment.sh <issue> <kind> [--note-file <path>] [--pr]   (kinds include bailed, stopped, revise <phase> <k>; --pr only with bailed)
#
# Exit:    0 posted, or queued while GitHub is down (prints queued <key>); 2 bad arguments, or GitHub gave no answer outside an outage
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/comment.py" "$@"
