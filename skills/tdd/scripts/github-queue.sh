#!/bin/sh
# github-queue.sh — the issue writes a live run queued while GitHub was down, replayed in order: a shim over
# veri/github_queue.py.
#
# Usage:   github-queue.sh replay
# Exit:    0 every entry landed and the queue is gone; 2 an entry got no answer (named; it and the rest stay queued),
#          an unreadable entry, or bad arguments; 3 no queue
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/github_queue.py" "$@"
