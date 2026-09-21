#!/usr/bin/env bash
# stop-requested.sh — has an operator asked this run to stop, and how?
#
# Run from the run's worktree, it reads `.tdd/stop` relative to it, the way event.sh and
# supervise.sh spell their own paths. The file's first line is the mode: `at-ledger`,
# `at-leaf` or `now`. The mode goes to stdout, exit 0 — a conductor at a checkpoint
# captures stdout and branches on the word, so nothing but the mode is ever printed there.
# The mode is passed through, not interpreted: what a conductor does with it is its own.
#
# Usage:   stop-requested.sh
set -euo pipefail

file=".tdd/stop"

IFS= read -r mode < "$file"
printf '%s\n' "$mode"
