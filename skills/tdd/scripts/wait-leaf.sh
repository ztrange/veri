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

name="${1:?usage: wait-leaf.sh <name> [max-seconds]}"
max="${2:-540}"
poll="${VERI_POLL:-1}"

exitfile=".tdd/$name.exit"
pidfile=".tdd/$name.pid"
deadline=$(( $(date +%s) + max ))

# recorded_code — echo the supervisor's final code, or fail when the file holds no status
# yet. A file seen between its creation and its write reads back empty, and an empty read is
# not a status, so that case fails here too and the caller keeps polling. Only a plain code
# ends the wait.
recorded_code() {
  local ec=""
  [[ -f "$exitfile" ]] || return 1
  read -r ec < "$exitfile" 2>/dev/null || true
  [[ "$ec" =~ ^[0-9]+$ ]] || return 1
  printf '%s\n' "$ec"
}

while :; do
  ec="$(recorded_code)" && exit "$ec"
  # A supervisor that died never writes its completion file, so a recorded pid that no
  # longer runs ends the wait with 2 — after one last look, in case it wrote just before.
  if [[ -f "$pidfile" ]]; then
    read -r pid < "$pidfile" 2>/dev/null || true
    if [[ "${pid:-}" =~ ^[0-9]+$ ]] && ! kill -0 "$pid" 2>/dev/null; then
      ec="$(recorded_code)" && exit "$ec"
      echo "wait-leaf.sh: supervisor for leaf '$name' (pid $pid) exited without recording a status" >&2
      exit 2
    fi
  fi
  (( $(date +%s) >= deadline )) && break
  sleep "$poll"
done

exit 3
