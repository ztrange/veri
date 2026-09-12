#!/usr/bin/env bash
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the wall-clock cap is killed even if still noisy.
# A killed leaf is retried up to VERI_STUCK_RETRIES times (default 1) on a fresh attempt; if
# it still can't recover it is reported as `killed-stuck`, which the conductor turns into a
# clean bail.
#
# Usage:
#   supervise.sh <name> <cmd> [args...]
#
# The leaf's combined stdout+stderr is captured to `.tdd/<name>.log` (the progress log the
# heartbeat watches) and echoed to this script's stdout on completion, so a verifier leaf
# can be piped straight into parse-verdict.sh.
#
# Status: exit 0 success · 1 leaf-failure · 2 killed-stuck. A one-line status (with the
# kill cause) is written to stderr, and the same code is recorded in the completion file
# `.tdd/<name>.exit` on every path — so a leaf launched detached can be waited on by
# polling that file instead of by reading this script's stdout.
#
# Tunables (env): VERI_HEARTBEAT silence window secs (default 45) · VERI_TIMEOUT hard cap
# secs (default 900) · VERI_POLL poll interval secs (default 1) · VERI_STUCK_RETRIES extra
# attempts after the first when a leaf is killed-stuck (default 1).
set -uo pipefail

name="${1:?usage: supervise.sh <name> <cmd> [args...]}"
shift
[[ $# -ge 1 ]] || { echo "supervise: missing <cmd>" >&2; exit 2; }

heartbeat="${VERI_HEARTBEAT:-45}"
timeout="${VERI_TIMEOUT:-900}"
poll="${VERI_POLL:-1}"
retries="${VERI_STUCK_RETRIES:-1}"

mkdir -p .tdd
log=".tdd/$name.log"
rcfile=".tdd/$name.rc"
exitfile=".tdd/$name.exit"

now() { date +%s; }

# Seconds-since-epoch of $1's last modification — the heartbeat sensor. There is no portable
# `stat`: GNU/coreutils spells it `stat -c %Y`, BSD/macOS spells it `stat -f %m`. The two
# must be tried one at a time, into a variable, with the answer validated — NOT chained with
# `||` inside one `$( )`. On GNU, `-f` is not a format flag at all; it means --file-system,
# so `stat -f %m FILE` reads `%m` as a second *filename* and prints a `  File: "…"` block to
# stdout for the real one before exiting non-zero. Chained, that block joins the fallback's
# digits in the same substitution and reaches the caller's `$(( ))`, where `set -u` kills the
# supervisor on the unset word `File`. Assigning each attempt separately overwrites instead
# of appending, and the digit test rejects anything that is not a plain count of seconds.
mtime_of() {
  local m
  m="$(stat -c %Y "$1" 2>/dev/null)" || m="$(stat -f %m "$1" 2>/dev/null)" || m=""
  # No readable mtime (neither spelling, or the log vanished) → report "just touched". The
  # heartbeat then never fires and the hard timeout, which needs only `date`, still bounds
  # the leaf. The opposite default (0) would read as decades of silence and kill every leaf.
  case "$m" in ''|*[!0-9]*) m="$(now)" ;; esac
  printf '%s\n' "$m"
}

kill_tree() {
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  # brief grace, then make sure it is gone
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep 0.1; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

# Run the leaf once on a fresh log/rc, watching for stuck/timeout. Sets status/reason/rc.
attempt_once() {
  : > "$log"
  rm -f "$rcfile"

  # Launch the leaf in its own process group (job-control monitor mode) so we can kill the
  # whole tree — including any grandchild like `sleep` — in one signal. A trailing rc file
  # marks natural completion without blocking the watch loop on `wait`.
  set -m
  ( "$@" >"$log" 2>&1; echo $? > "$rcfile" ) &
  pid=$!
  set +m

  t0="$(now)"
  status="" reason="" rc=0

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
    # Strict '>' so the whole-second clock's ±1s over-read at a second boundary (see the
    # slow-leaf note in supervise.test.sh) can't spuriously kill an active/just-relaunched
    # leaf; a genuine hang keeps climbing past the window and is still killed.
    if (( silence > heartbeat )); then
      status="killed-stuck"; reason="no heartbeat for ${silence}s (window ${heartbeat}s)"
      kill_tree; break
    fi
    sleep "$poll"
  done

  wait "$pid" 2>/dev/null || true
}

# First attempt plus up to $retries extra attempts. A normal result (success/failure)
# short-circuits; only killed-stuck is retried.
tries=0
while :; do
  attempt_once "$@"
  [[ "$status" == "killed-stuck" ]] || break
  (( tries >= retries )) && break
  tries=$(( tries + 1 ))
  echo "supervise[$name]: retry $tries/$retries after killed-stuck" >&2
done

case "$status" in
  success)      ec=0 ;;
  failure)      ec=1 ;;
  killed-stuck) ec=2 ;;
  *)            ec=2; status="killed-stuck"; reason="${reason:-unknown}" ;;
esac

echo "supervise[$name]: $status${reason:+ — $reason}" >&2
cat "$log"
# The completion file: this supervisor's OWN status code, on every path including
# killed-stuck (where the leaf's subshell never gets to write `.tdd/<name>.rc` at all).
# A leaf launched detached is waited on by polling this, so it must carry the 0/1/2 of the
# exit-code contract rather than the leaf's raw code that `.rc` records.
printf '%s\n' "$ec" > "$exitfile"
exit "$ec"
