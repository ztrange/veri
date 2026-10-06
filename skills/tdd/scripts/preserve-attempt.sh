#!/bin/sh
# preserve-attempt.sh — snapshot the worktree to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>: a shim over veri/preserve_attempt.py.
#
# The snapshot goes through a scratch index, so the caller's index, HEAD and branch are left untouched.
# A fifth argument, the mark, also copies .tdd/<phase>.log and .tdd/<phase>.out under .tdd/attempts/.
#
# usage: preserve-attempt.sh <issue> <step> <phase> <attempt> [<mark>]
# Exit:    0 preserved; 1 the ref write or a copy failed; 2 bad arguments, or a git failure taking the snapshot
exec python3 "$(dirname "$0")/veri/preserve_attempt.py" "$@"
