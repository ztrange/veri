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

# Everything this script says, it says on stderr under its own name — stdout is the run names
# and nothing else, because an operator's script reads it. The prefix is written once here so
# that copies of a script's own name are not copies to go on saying it after a rename.
complain() {
  echo "stop-run: $1" >&2
}

# Every refusal below is the same two moves — say why, exit 2 — so they are made in one place
# and each site says only what is wrong.
refuse() {
  complain "$1"
  exit 2
}

# The other half of that pair, and deliberately not folded into it: the command was
# understood perfectly and there was simply no live run answering to it, which is this
# repository's exit 3 rather than its 2. The write is what the separation is really for — a
# request left in a finished run's .tdd/stop is not a no-op but a trap, still sitting there
# when that issue is next resumed. They share how they speak, never what they mean.
nothing_to_do() {
  complain "$1"
  exit 3
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
# Outside a repository git prints nothing and the resolution comes back empty, which is not a
# repository holding no live runs but no repository at all — a 2 with the other refusals, never
# the 3 below: an operator's wrapper reading "nothing to do" would stop asking, when what
# happened is that the command was typed in the wrong place.
[[ -n "$main_tree" ]] || refuse "no main working tree here — type this inside the repository"

# pid_in <pid-file> — the number that pid file holds, or nothing and a 1 when it holds none.
# Both readings below start here, and both want the same three cases folded into one answer:
# no file, an unreadable one, and something that is not a number all mean there is no process
# for the caller to go on and ask about. A pid file is written by a process that may have died
# before finishing it, so none of the three is a failure worth reporting on its own.
pid_in() {
  local pid
  pid="$(cat "$1" 2>/dev/null || true)"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  printf '%s' "$pid"
}

# live_run <run-path> — whether a conductor is still running inside this run's worktree, the
# reading issue-worktree.sh:109-116 already makes: `.tdd/conductor.pid` holds a number and
# `kill -0` answers for it. `kill -0` sends no signal; it only says whether there is a process
# to send one to. A pid file with no number in it and a pid nobody answers for are the same
# answer, not live, which is what keeps a run whose conductor has exited out of `--all`: a
# request left in its .tdd/stop would ambush that issue at its next resume rather than
# stopping anything now.
live_run() {
  local pid
  pid="$(pid_in "$1/.tdd/conductor.pid")" || return 1
  kill -0 "$pid" 2>/dev/null
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

# supervising <pid> <leaf-name> — whether that pid is running that leaf's supervisor, the
# check wait-leaf.sh:47-51 already makes and for the same reason: a pid file outlives the
# process it named and the operating system reuses the number, so a pid that answers is not
# evidence of anything on its own. `ps -p <pid> -o args=` prints that process's command line
# and nothing else, and a pid nobody answers for prints nothing at all, so both of the pid
# files a finished run leaves behind — the stale one and the stranger's — fail the same test.
supervising() {
  local args
  args="$(ps -p "$1" -o args= 2>/dev/null)" || return 1
  [[ "$args" == *"supervise.sh $2 "* ]]
}

# stop_leaves <run-path> — `--mode now`'s other half: TERM to each of that run's live leaf
# supervisors, so the stop takes effect at once rather than at the next checkpoint, which
# wait-leaf.sh's own window can hold off for up to nine minutes. Nothing new kills a leaf —
# supervise.sh:350-355 traps TERM, takes the leaf's tree down through kill_tree and records 2
# in the completion file, so the supervisor stays the one place a kill happens.
#
# The leaf's name is the pid file's, so the glob finds the candidates and supervising() is
# what decides: a pid whose process is gone or is something else is skipped in silence, since
# a stale pid file is the ordinary state of a finished leaf and not a failure to report.
# .tdd/conductor.pid is among the files the glob turns up and is refused by that same check,
# a conductor running run-conductor.sh rather than supervise.sh — this never signals it.
stop_leaves() {
  local pidfile name pid
  for pidfile in "$1"/.tdd/*.pid; do
    [[ -f "$pidfile" ]] || continue
    name="$(basename "$pidfile" .pid)"
    pid="$(pid_in "$pidfile")" || continue
    supervising "$pid" "$name" || continue
    kill -TERM "$pid" 2>/dev/null || true
  done
}

# stop_run <run-path> — the whole of what stopping one live run is, so that both callers below
# ask for it in one line and neither can do half of it: the write, and then — for `now` alone —
# the TERM to that run's leaf supervisors. Pairing them here rather than at each caller is what
# holds the rule that a signal only ever goes to a run a write has just reached, never over one
# the command skipped.
stop_run() {
  request_stop "$1"
  [[ "$mode" == now ]] && stop_leaves "$1"
  return 0
}

if (( all == 1 )); then
  stopped=0
  # The glob, not `git worktree list`: a run is a directory under .tdd/wt/, and `[[ -d ]]`
  # also answers the case of a repository with no runs at all, where bash leaves the pattern
  # itself standing as the one word of the loop.
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
