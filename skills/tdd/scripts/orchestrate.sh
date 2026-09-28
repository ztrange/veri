#!/usr/bin/env bash
# orchestrate.sh — the loop above the conductor: ask solvable-issues.sh which
# issues veri may take, launch one conductor for the first of them through run-conductor.sh,
# and ask again, until nothing is left to take.
#
# Usage:   orchestrate.sh
#
# It is a script rather than an agent so that its own context stays O(1): an agent looping
# over conductors would accumulate context exactly the way the conductors it launches do.
#
# The solvable set is asked afresh after every launch rather than read once, because a
# finished run leaves the set and that is how the loop learns it finished.
#
# While a conductor runs, its stream-json stdout is read line by line as it arrives, and every
# assistant event prints `context <issue> <tokens>`: that request's cache_read_input_tokens +
# cache_creation_input_tokens, which is the context it re-read. No closing result record is
# needed — harvest-usage.sh reads that one, and only at the end.
#
# A conductor whose context has crossed VERI_CONDUCTOR_CTX_BUDGET (tokens, default 120000,
# ~2.2x a conductor's 53k first request) is stopped only at a step boundary: once its stream
# shows the Bash call to `event.sh step-done` and that call's result, orchestrate.sh stops
# reading and SIGTERMs the conductor's process group. Never mid-leaf — a leaf killed in Red
# or Green leaves work a resume does not reset.
#
# Closing the stream is not itself the stop. A write to a pipe no one reads raises SIGPIPE
# only where SIGPIPE is fatal, and it is not everywhere: on CI's Linux the stopped conductor's
# writes came back as plain `echo: I/O error` and it ran on to the end of its step, so the
# case pinning "stopped after step-done" was green on this Mac and red there. The stop is
# therefore an explicit signal to a recorded pid, which is why the launch goes through
# bg_start and a session of its own rather than a pipeline.
#
# A conductor that halts with a question writes it to .tdd/parked/<n>.md. orchestrate.sh
# prints `parked <n>`, leaves that run's branch and ledger as they are, and skips the issue on
# every later pass, so the night goes on with the next solvable issue.
#
# Exit 0 once solvable-issues.sh answers 3 (nothing to take) or every issue it names is
# parked; exit 2, launching nothing, when
# it exits with anything but 0 or 3, since then no answer about the solvable set was obtained,
# or when VERI_CONDUCTOR_CTX_BUDGET is not a whole number.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

. "$HERE/lib/background.sh"

budget="${VERI_CONDUCTOR_CTX_BUDGET:-120000}"
if [[ ! "$budget" =~ ^[0-9]+$ ]]; then
  echo "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: $budget" >&2
  exit 2
fi

watch_context() {
  local line read_re='"cache_read_input_tokens":([0-9]+)' create_re='"cache_creation_input_tokens":([0-9]+)'
  local cache_read context=0 step_done=0
  while IFS= read -r line; do
    if [[ $step_done -eq 1 && $line == *'"type":"user"'* ]]; then
      [[ $context -gt $budget ]] && return 0
      step_done=0
    fi
    [[ $line == *'"type":"assistant"'* ]] || continue
    [[ $line == *'event.sh step-done'* ]] && step_done=1
    [[ $line =~ $read_re ]] || continue
    cache_read=${BASH_REMATCH[1]}
    [[ $line =~ $create_re ]] || continue
    context=$((cache_read + BASH_REMATCH[1]))
    echo "context $1 $context"
  done
}

# hazard: macOS ships no setsid binary, so python3's os.setsid stands in.
launch() {
  exec > "$2"
  exec python3 -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
    "$HERE/run-conductor.sh" "$1"
}

stop() {
  kill -TERM -"$1" 2>/dev/null || kill -TERM "$1" 2>/dev/null || true
}

parked() { [[ -e ".tdd/parked/$1.md" ]]; }

while :; do
  issues="$("$HERE/solvable-issues.sh")"
  rc=$?
  [[ $rc -eq 3 ]] && exit 0
  if [[ $rc -ne 0 ]]; then
    echo "orchestrate.sh: solvable-issues.sh exited $rc; no answer about the solvable set" >&2
    exit 2
  fi
  issue=
  while IFS= read -r n; do
    parked "$n" || { issue=$n; break; }
  done <<< "$issues"
  [[ -n "$issue" ]] || exit 0
  run="$(mktemp -d)"
  mkfifo "$run/stream"
  : > "$run/bg"
  bg_start "$run/bg" launch "$issue" "$run/stream"
  read -r pid _ < "$run/bg"
  watch_context "$issue" < "$run/stream"
  stop "$pid"
  rm -rf "$run"
  parked "$issue" && echo "parked $issue"
done
