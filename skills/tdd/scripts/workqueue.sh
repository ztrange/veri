#!/bin/sh
# workqueue.sh — the only writer of `.tdd/workqueue`, the file that assigns issues to named
# workers and records what happened to each: a shim over veri/workqueue.py.
#
# The file lives under the repository's MAIN working tree, so every worktree of the clone
# reads and writes the one queue. One item per line, tab-separated:
#
#   <worker>	<issue>	<state>	<detail>
#
# usage: workqueue.sh assign <worker> <issue>...
#        workqueue.sh next <worker>
#        workqueue.sh start <worker> <issue>
#        workqueue.sh done <worker> <issue> <merge-sha>
#        workqueue.sh park <worker> <issue> <reason>
#        workqueue.sh show [<worker>]
# Exit:    0 done, 1 `start`/`done`/`park` naming no item of that worker's in the state it
#          moves from, 3 `next` found nothing launchable, 2 an unknown subcommand, an `assign`
#          naming no worker or no issue, an empty issue, or naming one issue twice, a `done`
#          with no merge sha, a `park` reason holding a tab or a newline, an issue already
#          queued or running for any worker, or a lock not taken within
#          VERI_WORKQUEUE_LOCK_WAIT seconds — refused before anything is written, so the file
#          is left byte-identical
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/workqueue.py" "$@"
