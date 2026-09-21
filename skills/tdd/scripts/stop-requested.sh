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
# A file whose first line is anything else, an empty one included, is no answer at all:
# nothing on stdout, the complaint on stderr, exit 2. Printing it on stdout instead would
# hand a conductor a diagnostic in a mode's place, and it would branch on it. A zero-byte
# file is that same empty first line, but `read` hits end-of-file and returns non-zero, so
# under `set -e` it would end the run at exit 1 — outside this script's four-code API and
# silent besides. `|| mode=""` hands that case to the check below instead.
#
# Usage:   stop-requested.sh
# Exits:   0 a mode was printed | 2 malformed request | 3 no stop request
set -euo pipefail

file=".tdd/stop"

[[ -f "$file" ]] || exit 3

IFS= read -r mode < "$file" || mode=""

case "$mode" in
  at-ledger | at-leaf | now) ;;
  *)
    echo "stop-requested: $file must name a mode — at-ledger, at-leaf or now: '$mode'" >&2
    exit 2
    ;;
esac

printf '%s\n' "$mode"
