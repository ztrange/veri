#!/bin/sh
# holds-step.sh — the HOLDS gate of a Red whose report says `AGAINST_UNMODIFIED: HOLDS`: a shim over veri/holds_step.py.
#
# Runs each named case through the repo's `veri: one test file:` command, in the current directory.
#
# Usage:   holds-step.sh <n> <step-start-sha> <id>…
# Exit:    0 every named case passes; 1 a named case fails; 2 the worktree differs from <step-start-sha>, a tracked file changed or an untracked one present (no case run), or bad arguments (a usage line)
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/holds_step.py" "$@"
