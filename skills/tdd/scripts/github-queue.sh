#!/bin/sh
# github-queue.sh — the issue writes a live run queued while GitHub was down, replayed in order, and the Landed
# comments of an offline-joined stack once it lands: a shim over veri/github_queue.py.
#
# Usage:   github-queue.sh replay | close-landed <tip-sha>
# Exit:    0 every entry landed and the queue is gone; 2 an entry got no answer (named; it and the rest stay queued),
#          an unreadable entry, or bad arguments; close-landed also 2 when the fetch, the landed range or a PR read
#          gets no answer or a Veri-Joined trailer is garbled; 3 no queue, or no Veri-Joined commit landed
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/github_queue.py" "$@"
