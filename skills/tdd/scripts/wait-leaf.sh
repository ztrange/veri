#!/usr/bin/env bash
# wait-leaf.sh — the foreground half of a detached leaf launch.
#
# `supervise.sh` is launched detached (nohup … &) so that a print-mode conductor, which
# never receives background-task notifications, cannot end its turn with the leaf orphaned.
# This script is what the conductor calls next: it blocks in the foreground, polling for the
# completion file `.tdd/<name>.exit` that the supervisor writes with its own final code, and
# exits with that code as soon as the file lands. The file is normally absent when the wait
# begins, so this polls rather than looking once.
#
# Usage:
#   wait-leaf.sh <name> [max-seconds]
#
# Status: whatever the supervisor recorded — 0 success · 1 leaf-failure · 2 killed-stuck —
# or 3 once <max-seconds> pass with no completion file, meaning nothing to report yet and
# the conductor should simply call again.
#
# Tunables (env): VERI_POLL poll interval secs (default 1).
set -uo pipefail

[[ -n "${1:-}" ]] || { echo "usage: wait-leaf.sh <name> [max-seconds]" >&2; exit 2; }
name="$1"
max="${2:-540}"
poll="${VERI_POLL:-1}"

exitfile=".tdd/$name.exit"
pidfile=".tdd/$name.pid"
deadline=$(( $(date +%s) + max ))

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/number-in.sh"

recorded_code() { number_in "$exitfile"; }

supervising() {
  local args
  args="$(ps -p "$1" -o args= 2>/dev/null)" || return 1
  [[ "$args" == *"supervise.sh $name "* ]]
}

while :; do
  ec="$(recorded_code)" && exit "$ec"
  if pid="$(number_in "$pidfile")" && ! supervising "$pid"; then
    ec="$(recorded_code)" && exit "$ec"
    echo "wait-leaf.sh: supervisor for leaf '$name' (pid $pid) exited without recording a status" >&2
    exit 2
  fi
  (( $(date +%s) >= deadline )) && break
  sleep "$poll"
done

exit 3
