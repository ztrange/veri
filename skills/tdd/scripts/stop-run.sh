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

lib="$(dirname "$0")/lib"
# shellcheck source=lib/main-working-tree.sh
source "$lib/main-working-tree.sh"

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

# The runs live under the MAIN working tree, never the checkout this was typed in: a
# conductor's worktree is itself under .tdd/wt/, so resolving from here would look for runs
# inside one run (#166, the rule status.sh:158-164 already follows).
main_tree="$(main_working_tree)"

# live_run <run-path> — whether a conductor is still running inside this run's worktree, the
# reading issue-worktree.sh:109-116 already makes: `.tdd/conductor.pid` holds a number and
# `kill -0` answers for it. `kill -0` sends no signal; it only says whether there is a process
# to send one to. Every other case — no file, an unreadable one, something that is not a
# number, a pid nobody answers for — is the same answer, not live, which is what keeps a run
# whose conductor has exited out of `--all`: a request left in its .tdd/stop would ambush that
# issue at its next resume rather than stopping anything now.
live_run() {
  local pid
  pid="$(cat "$1/.tdd/conductor.pid" 2>/dev/null || true)"
  [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null
}

# request_stop <run-path> — the write, and the one line of stdout that says it happened. The
# mode is the only line of the file, because stop-requested.sh reads it as one word, and `>`
# rather than `>>` because the last write is the request that stands. Naming the run on stdout
# is how an operator learns which runs the command actually reached, so the two belong
# together: a write nobody is told about is indistinguishable from a run that was skipped.
request_stop() {
  printf '%s\n' "$mode" > "$1/.tdd/stop"
  echo "$1"
}

if (( all == 1 )); then
  # The glob, not `git worktree list`: a run is a directory under .tdd/wt/, and `[[ -d ]]`
  # also answers the case of a repository with no runs at all, where bash leaves the pattern
  # itself standing as the one word of the loop.
  for candidate in "$main_tree"/.tdd/wt/*; do
    [[ -d "$candidate" ]] || continue
    if live_run "$candidate"; then
      request_stop "$candidate"
    fi
  done
else
  request_stop "$main_tree/.tdd/wt/$issue"
fi
