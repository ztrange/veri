#!/bin/sh
# comment.sh — post a routine comment rendered from the run's journal and ledger: a shim over veri/comment.py.
#
# usage: comment.sh <issue> <kind> [--note-file <path>]   (kinds include bailed, stopped)
#
# Exit:    0 posted; 2 bad arguments, or GitHub gave no answer
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/comment.py" "$@"
