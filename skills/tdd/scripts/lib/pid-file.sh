#!/usr/bin/env bash
# lib/pid-file.sh — sourced, not run: defines `supervising` and `live_conductor`.
# Needs lib/number-in.sh sourced first.
#
# supervising <pid> <name> — return 0 when <pid> is alive and is the supervisor of leaf
# <name>, 1 otherwise.
#
# live_conductor <run-dir> — print the pid in <run-dir>/.tdd/conductor.pid and return 0 when
# that process is alive, return 1 with nothing printed otherwise.
supervising() {
  local args
  args="$(ps -p "$1" -o args= 2>/dev/null)" || return 1
  [[ "$args" == *"supervise.sh $2 "* ]]
}

live_conductor() {
  local pid
  pid="$(number_in "$1/.tdd/conductor.pid")" || return 1
  [[ "$pid" =~ [1-9] ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  printf '%s\n' "$pid"
}
