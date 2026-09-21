#!/usr/bin/env bash
# stop-run.sh — the operator's stop command: ask a run to stop, where its conductor looks.
#
# The write half of the stop mechanism whose read half stop-requested.sh is (#386). Typed
# from anywhere in the repository, it names either one issue's run or `--all` of them, and
# `--mode` says when the stop takes effect: `at-ledger` (the default), `at-leaf` or `now`.
#
# Every refusal below writes nothing and signals nothing, and all of them are decided before
# any run is looked at: a stop request left behind by a command that was not understood
# would ambush that run at its next checkpoint, and a TERM sent over a typo would take a
# leaf down for one. So an unknown `--mode` value, both an issue and `--all`, neither of
# them, and an issue argument that is not a positive integer each print nothing on stdout,
# say why on stderr and exit 2.
#
# Usage:   stop-run.sh [--mode at-ledger|at-leaf|now] <issue>
#          stop-run.sh [--mode at-ledger|at-leaf|now] --all
# Exits:   2 arguments that name no run, or no mode this script knows
#          3 nothing to do — no live run answered to what was named
set -euo pipefail

# Every refusal below is the same two moves — say why on stderr, exit 2 — so they are made
# in one place and each site says only what is wrong. The `stop-run: ` prefix lives here for
# the same reason: four copies of a script's own name are four chances for one of them to go
# on saying it after a rename.
refuse() {
  echo "stop-run: $1" >&2
  exit 2
}

mode="at-ledger"
issue=""
all=0

while (( $# > 0 )); do
  case "$1" in
    # `$2` is read only once it is known to exist: under `set -u` the expansion itself
    # would kill the script before the contract below could refuse, and bash's complaint
    # names this file and a line number instead of saying what the operator got wrong.
    --mode)
      (( $# >= 2 )) || refuse "--mode needs a value — at-ledger, at-leaf or now"
      mode="$2"; shift 2 ;;
    --all) all=1; shift ;;
    *) issue="$1"; shift ;;
  esac
done

case "$mode" in
  at-ledger | at-leaf | now) ;;
  *) refuse "unknown mode — want at-ledger, at-leaf or now: '$mode'" ;;
esac

# Exactly one of the two ways of naming runs. Both is a contradiction — `--all` is every
# live run, so an issue beside it says nothing about which the operator meant — and neither
# names no run at all.
if [[ -n "$issue" ]] && (( all == 1 )); then
  refuse "name an issue or --all, not both"
fi
if [[ -z "$issue" ]] && (( all == 0 )); then
  refuse "name an issue, or --all"
fi

# An issue is a worktree name under .tdd/wt/, so anything but a positive integer names no
# run that could exist.
if [[ -n "$issue" && ! "$issue" =~ ^[1-9][0-9]*$ ]]; then
  refuse "<issue> must be a positive integer: '$issue'"
fi

# Finding the runs and writing the mode into each live one is the next step's work; until it
# is written, a well-formed call has found no live run to leave a request with.
exit 3
