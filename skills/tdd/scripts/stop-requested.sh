#!/usr/bin/env bash
# stop-requested.sh — has an operator asked this run to stop, and how?
#
# Run from the run's worktree, it reads `.tdd/stop` relative to it, the way event.sh and
# supervise.sh spell their own paths. The file's first line is the mode: `at-ledger`,
# `at-leaf` or `now`. The mode goes to stdout, exit 0 — a conductor at a checkpoint
# captures stdout and branches on the word, so nothing but the mode is ever printed there.
# The mode is passed through, not interpreted: what a conductor does with it is its own.
#
# No file is no request: nothing on stdout, exit 3 — nothing to do, not an error.
#
# Usage:   stop-requested.sh
# Exits:   0 a mode was printed | 3 no stop request
set -euo pipefail

file=".tdd/stop"

[[ -f "$file" ]] || exit 3

IFS= read -r mode < "$file"
printf '%s\n' "$mode"
