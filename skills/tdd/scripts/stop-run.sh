#!/usr/bin/env bash
# stop-run.sh — the operator's stop command: ask a run to stop, where its conductor looks.
#
# The write half of the stop mechanism whose read half stop-requested.sh is. Typed
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
source "$lib/main-working-tree.sh"

complain() {
  echo "stop-run: $1" >&2
}

USAGE="usage: stop-run.sh [--mode at-ledger|at-leaf|now] <issue> | --all"

refuse() {
  complain "$1"
  echo "$USAGE" >&2
  exit 2
}

nothing_to_do() {
  complain "$1"
  exit 3
}

mode="at-ledger"
issue=""
all=0

while (( $# > 0 )); do
  case "$1" in
    # hazard: under set -u an absent `$2` kills the script before the refusal can speak.
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

if [[ -n "$issue" ]] && (( all == 1 )); then
  refuse "name an issue or --all, not both"
fi
if [[ -z "$issue" ]] && (( all == 0 )); then
  refuse "name an issue, or --all"
fi

if [[ -n "$issue" && ! "$issue" =~ ^[1-9][0-9]*$ ]]; then
  refuse "<issue> must be a positive integer: '$issue'"
fi

main_tree="$(main_working_tree)"
[[ -n "$main_tree" ]] || refuse "no main working tree here — type this inside the repository"

pid_in() {
  local pid
  pid="$(cat "$1" 2>/dev/null || true)"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  printf '%s' "$pid"
}

live_run() {
  local pid
  pid="$(pid_in "$1/.tdd/conductor.pid")" || return 1
  kill -0 "$pid" 2>/dev/null
}

request_stop() {
  printf '%s\n' "$mode" > "$1/.tdd/stop"
  echo "$1"
}

supervising() {
  local args
  args="$(ps -p "$1" -o args= 2>/dev/null)" || return 1
  [[ "$args" == *"supervise.sh $2 "* ]]
}

stop_leaves() {
  local pidfile name pid
  for pidfile in "$1"/.tdd/*.pid; do
    [[ -f "$pidfile" ]] || continue
    name="$(basename "$pidfile" .pid)"
    [[ "$name" != conductor ]] || continue
    pid="$(pid_in "$pidfile")" || continue
    supervising "$pid" "$name" || continue
    kill -TERM "$pid" 2>/dev/null || true
  done
}

stop_run() {
  request_stop "$1"
  [[ "$mode" == now ]] && stop_leaves "$1"
  return 0
}

if (( all == 1 )); then
  stopped=0
  # hazard: an unmatched glob stays its literal text, which `[[ -d ]]` then rejects.
  for candidate in "$main_tree"/.tdd/wt/*; do
    [[ -d "$candidate" ]] || continue
    if live_run "$candidate"; then
      stop_run "$candidate"
      stopped=1
    fi
  done
  (( stopped == 1 )) || nothing_to_do "no live run to stop"
else
  target="$main_tree/.tdd/wt/$issue"
  live_run "$target" ||
    nothing_to_do "no live run for issue $issue"
  stop_run "$target"
fi
