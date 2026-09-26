#!/usr/bin/env bash
# orchestrate.sh — the loop above the conductor (issue #217): ask solvable-issues.sh which
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
# reading, and the conductor dies on its next write to the closed stream. Never mid-leaf —
# a leaf killed in Red or Green leaves work a resume does not reset (#194).
#
# Exit 0 once solvable-issues.sh answers 3 (nothing to take); exit 2, launching nothing, when
# it exits with anything but 0 or 3, since then no answer about the solvable set was obtained,
# or when VERI_CONDUCTOR_CTX_BUDGET is not a whole number.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

budget="${VERI_CONDUCTOR_CTX_BUDGET:-120000}"
if [[ ! "$budget" =~ ^[0-9]+$ ]]; then
  echo "orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: $budget" >&2
  exit 2
fi

# watch_context <issue>: read a conductor's stream-json on stdin and print one
# `context <issue> <tokens>` line per assistant event, as each event arrives. Returns, closing
# the stream, at the first step-done result seen while the context is over the budget.
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

while :; do
  issues="$("$HERE/solvable-issues.sh")"
  rc=$?
  [[ $rc -eq 3 ]] && exit 0
  if [[ $rc -ne 0 ]]; then
    echo "orchestrate.sh: solvable-issues.sh exited $rc; no answer about the solvable set" >&2
    exit 2
  fi
  issue="${issues%%$'\n'*}"
  "$HERE/run-conductor.sh" "$issue" | watch_context "$issue"
done
