#!/usr/bin/env bash
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the wall-clock cap is killed even if still noisy.
# A killed leaf is reported as `killed-stuck`; the conductor turns that into a clean bail
# (retry arrives in #5).
#
# Usage:
#   supervise.sh <name> <cmd> [args...]
#
# The leaf's combined stdout+stderr is captured to `.tdd/<name>.log` (the progress log the
# heartbeat watches) and echoed to this script's stdout on completion, so a verifier leaf
# can be piped straight into parse-verdict.sh.
#
# Status: exit 0 success · 1 leaf-failure · 2 killed-stuck. A one-line status (with the
# kill cause) is written to stderr.
#
# Tunables (env): VERI_HEARTBEAT silence window secs (default 45) · VERI_TIMEOUT hard cap
# secs (default 900) · VERI_POLL poll interval secs (default 1).
set -uo pipefail

name="${1:?usage: supervise.sh <name> <cmd> [args...]}"
shift
[[ $# -ge 1 ]] || { echo "supervise: missing <cmd>" >&2; exit 2; }

heartbeat="${VERI_HEARTBEAT:-45}"
timeout="${VERI_TIMEOUT:-900}"
poll="${VERI_POLL:-1}"

mkdir -p .tdd
log=".tdd/$name.log"
rcfile=".tdd/$name.rc"
: > "$log"
rm -f "$rcfile"

mtime_of() {  # seconds-since-epoch of $1's last modification, portable across BSD/GNU
  stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null || echo 0
}
now() { date +%s; }

# Launch the leaf in its own process group (job-control monitor mode) so we can kill the
# whole tree — including any grandchild like `sleep` — in one signal. A trailing rc file
# marks natural completion without blocking the watch loop on `wait`.
set -m
( "$@" >"$log" 2>&1; echo $? > "$rcfile" ) &
pid=$!
set +m

t0="$(now)"
status="" reason="" rc=0

kill_tree() {
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  # brief grace, then make sure it is gone
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 0.1; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

while :; do
  if [[ -f "$rcfile" ]]; then
    rc="$(cat "$rcfile" 2>/dev/null || echo 1)"
    if [[ "$rc" == "0" ]]; then status="success"; else status="failure"; fi
    break
  fi
  t="$(now)"
  if (( t - t0 >= timeout )); then
    status="killed-stuck"; reason="hard timeout ${timeout}s exceeded"; kill_tree; break
  fi
  silence=$(( t - $(mtime_of "$log") ))
  if (( silence >= heartbeat )); then
    status="killed-stuck"; reason="no heartbeat for ${silence}s (window ${heartbeat}s)"
    kill_tree; break
  fi
  sleep "$poll"
done

wait "$pid" 2>/dev/null || true

case "$status" in
  success)      ec=0 ;;
  failure)      ec=1 ;;
  killed-stuck) ec=2 ;;
  *)            ec=2; status="killed-stuck"; reason="${reason:-unknown}" ;;
esac

echo "supervise[$name]: $status${reason:+ — $reason}" >&2
cat "$log"
exit "$ec"
