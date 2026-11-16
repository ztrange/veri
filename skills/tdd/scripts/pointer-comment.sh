#!/bin/sh
# pointer-comment.sh — the issue's one `### 📍 Run state` comment, posted or edited in place: a shim over veri/pointer_comment.py.
#
# usage: pointer-comment.sh <issue-number>
#          States the run's branch, PR, step, phase, last push, machine and resume command.
# Exit:    0 written; 2 a bad argument, or gh gave no answer (one stderr line naming the issue)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/pointer_comment.py" "$@"
