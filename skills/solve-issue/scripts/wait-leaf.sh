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
deadline=$(( $(date +%s) + max ))

while :; do
  if [[ -f "$exitfile" ]]; then
    # A file seen between its creation and its write reads back empty; that is not a status,
    # so keep polling rather than exiting on it. Only a plain code ends the wait.
    ec=""
    read -r ec < "$exitfile" 2>/dev/null || true
    [[ "$ec" =~ ^[0-9]+$ ]] && exit "$ec"
  fi
  (( $(date +%s) >= deadline )) && break
  sleep "$poll"
done

exit 3
