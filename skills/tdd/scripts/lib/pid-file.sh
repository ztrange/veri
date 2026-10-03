#!/usr/bin/env bash
# lib/pid-file.sh — sourced, not run: defines `supervising`.
#
# supervising <pid> <name> — return 0 when <pid> is alive and is the supervisor of leaf
# <name>, 1 otherwise.
supervising() {
  local args
  args="$(ps -p "$1" -o args= 2>/dev/null)" || return 1
  [[ "$args" == *"supervise.sh $2 "* ]]
}
