#!/usr/bin/env bash
# supervise.sh — launch one leaf under a heartbeat + hard-timeout watchdog.
#
# This is the one choke point where stuck-detection policy lives (ADR-0002): every leaf is
# launched through here, never directly. The supervisor spawns the leaf in the background
# and watches it two ways:
#   * heartbeat — activity on the leaf's progress log within a window tells "slow but
#     working" from "hung". A leaf silent past the window is killed.
#   * hard timeout — a leaf that exceeds the time cap is killed even if still noisy.
# Both windows count only time the machine spent awake. The clock is Python's
# clock_gettime(CLOCK_UPTIME_RAW), else the monotonic clock (CLOCK_MONOTONIC): on macOS that is mach_absolute_time(), which does not advance while the
# Mac is asleep, and on Linux it is CLOCK_MONOTONIC, which does not advance while the machine
# is suspended. The wall clock (`date +%s`) keeps running through a suspend, so an hour with
# the lid closed would read as an hour of silence and kill a leaf that never hung — the
# heartbeat slides by whatever the wall clock moved across one poll beyond this clock, and the
# hard timeout is measured on this clock alone.
# The heartbeat is the leaf's; a `verdict-<phase>` supervision is the wrapper around a
# verifier leaf that is already supervised under its own name, so it keeps only the hard
# timeout and never kills for a silence that is the wrapper's rather than the verifier's
# (the reasoning is where `heartbeat_watched` is set, below).
# A killed leaf is retried up to VERI_STUCK_RETRIES times (default 1) on a fresh attempt; if
# it still can't recover it is reported as `killed-stuck`, which the conductor turns into a
# clean bail — unless its log already holds the leaf's closing result record, in which case the
# kill landed on a finished process and the leaf's own outcome is reported instead.
# A kill and a rendered verdict can coexist because the watchdog's only sensor for
# "the leaf is done" is the subshell's rc file, and the leaf's stream finishes before the
# subshell writes `.tdd/<name>.rc` — so between the last line of output and that file
# landing there is a window in which a finished leaf is indistinguishable from a silent
# one, and a kill is not proof that no answer was obtained.
#
# Usage:
#   supervise.sh <name> <cmd> [args...]
#
# The leaf's combined stdout+stderr is captured to `.tdd/<name>.log` (the progress log the
# heartbeat watches) and echoed to this script's stdout on completion, so a verifier leaf
# can be piped straight into parse-verdict.sh.
#
# Status: exit 0 success · 1 leaf-failure · 2 killed-stuck, or a leaf that exited 2 itself.
# A one-line status (with the kill cause) is written to stderr, and the same code is recorded
# in the completion file `.tdd/<name>.exit` on every path — so a leaf launched detached can
# be waited on by polling that file instead of by reading this script's stdout. The one
# exception is a leaf that recorded a code in that file itself, as the verifier's launch
# wrapper does with `verify.sh`'s verdict code: the leaf's own record is the answer and is
# left alone.
#
# Three kinds of event are appended to the run's event log, `.tdd/events.jsonl` (ADR-0014):
# one `launch` — the leaf's name, the command behind it, the model it runs on
# (empty when the run chose none) and the attempt its name encodes — one `retry` per
# relaunch, carrying the cause the watchdog killed the previous attempt for, and one `exit`
# — the 0/1/2 status above, the kill cause when there is one, and how many wall seconds the
# last attempt took. `launch` and `exit` are written once per supervision, not once per
# attempt: a second one would read as a second leaf, and the relaunch is `retry`'s to
# report. A name leaf-role.sh cannot read leaves no line at all, rather than one whose actor
# and attempt were invented.
#
# Tunables (env): VERI_HEARTBEAT silence window secs (default 180) · VERI_TIMEOUT hard cap
# secs (default 900) · VERI_POLL poll interval secs (default 1) · VERI_STUCK_RETRIES extra
# attempts after the first when a leaf is killed-stuck (default 1) · VERI_KILL_POLL the grace
# loop's poll interval secs when a kill is sent, before escalating to KILL (default 0.1, an
# internal knob like VERI_POLL rather than one SKILL.md documents) · VERI_MODEL /
# VERI_MODEL_DEVELOPER / VERI_MODEL_VERIFIER the model this leaf's role runs on, resolved
# through leaf-model.sh and exported to the leaf as VERI_LEAF_MODEL (all unset by default,
# which is no `--model` flag at all).
set -uo pipefail

USAGE="usage: supervise.sh <name> <cmd> [args...]"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"

require_args 1 "$@"
name="$1"
shift
(( $# >= 1 )) || refuse "supervise: missing <cmd>"

source "$HERE/lib/leaf-model.sh"
source "$HERE/lib/preserve.sh"
source "$HERE/lib/number-in.sh"
source "$HERE/lib/awake-seconds.sh"

heartbeat="${VERI_HEARTBEAT:-180}"
timeout="${VERI_TIMEOUT:-}"
settled_timeout=".tdd/issue-${VERI_ISSUE:-}-timeout"
if [[ -z "$timeout" && -n "${VERI_ISSUE:-}" ]]; then
  run_root="$(git rev-parse --show-toplevel 2>/dev/null)" && settled_timeout="$run_root/$settled_timeout"
fi
if [[ -z "$timeout" && -n "${VERI_ISSUE:-}" && -f "$settled_timeout" ]]; then
  timeout="$(<"$settled_timeout")"
  if [[ ! "$timeout" =~ ^[0-9]+$ ]] || (( 10#$timeout < 1 )); then
    echo "supervise: $settled_timeout must hold a whole number of seconds >= 1: '$timeout'" >&2
    exit 2
  fi
fi
timeout="${timeout:-900}"
poll="${VERI_POLL:-1}"
retries="${VERI_STUCK_RETRIES:-1}"

heartbeat_watched=1
case "$name" in verdict-*) heartbeat_watched=0 ;; esac

kill_poll="${VERI_KILL_POLL:-0.1}"
if [[ ! "$kill_poll" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
  echo "supervise: VERI_KILL_POLL must be a non-negative number: $kill_poll" >&2
  exit 2
fi

mkdir -p .tdd
log=".tdd/$name.log"
rcfile=".tdd/$name.rc"
exitfile=".tdd/$name.exit"
pidfile=".tdd/$name.pid"

now() { date +%s; }

awake_clock="${VERI_AWAKE_CLOCK:-awake_seconds}"

# hazard: GNU stat reads -f as --file-system and prints to stdout, so try each spelling into its own assignment.
mtime_of() {
  local m
  m="$(stat -c %Y "$1" 2>/dev/null)" || m="$(stat -f %m "$1" 2>/dev/null)" || m=""
  case "$m" in ''|*[!0-9]*) m="$(now)" ;; esac
  printf '%s\n' "$m"
}

kill_tree() {
  kill -TERM -"$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
  for _ in 1 2 3 4 5; do kill -0 "$pid" 2>/dev/null || return 0; sleep "$kill_poll"; done
  kill -KILL -"$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
}

terminal_outcome() {
  PYTHONPATH="$HERE/veri" python3 -c '
import sys
from leaf_log import result_records

records = result_records(open(sys.argv[1]))
if not records:
    sys.exit(1)
print("failure" if records[-1].get("is_error") else "success")
' "$1"
}

recover_finished_leaf() {
  local outcome result_tmp
  [[ "$status" == "killed-stuck" ]] || return 0
  outcome="$(terminal_outcome "$log")" || return 0

  echo "supervise[$name]: killed after the leaf had already written its result ($reason) — reporting the leaf's own $outcome" >&2
  result_tmp="$(mktemp)"
  if "$HERE/extract-result.sh" < "$log" > "$result_tmp" 2>/dev/null; then
    { printf '\n'; cat "$result_tmp"; } >> "$log"
  fi
  rm -f "$result_tmp"
  status="$outcome"; reason=""
}

attempt_once() {
  local t0 a0 t silence last_m seen_at m prev_t prev_a a asleep
  : > "$log"
  rm -f "$rcfile"

  t0="$(now)"
  a0="$("$awake_clock")"
  prev_t="$t0" prev_a="$a0"

  # hazard: set -m gives the leaf its own process group, so kill -TERM -pid reaches grandchildren.
  set -m
  ( "$@" >"$log" 2>&1; echo $? > "$rcfile" ) &
  pid=$!
  set +m

  status="" reason="" rc=0
  if (( heartbeat_watched )); then last_m="$(mtime_of "$log")"; seen_at="$t0"; fi

  while :; do
    if [[ -f "$rcfile" ]]; then
      rc="$(cat "$rcfile" 2>/dev/null || echo 1)"
      if [[ "$rc" == "0" ]]; then status="success"; else status="failure"; fi
      break
    fi
    t="$(now)"
    a="$("$awake_clock")"
    asleep=$(( (t - prev_t) - (a - prev_a) ))
    seen_at=$(( ${seen_at:-0} + asleep ))
    prev_t="$t" prev_a="$a"
    if (( a - a0 >= timeout )); then
      status="killed-stuck"; reason="hard timeout ${timeout}s exceeded"; kill_tree; break
    fi
    if (( heartbeat_watched )); then
      m="$(mtime_of "$log")"
      if [[ "$m" != "$last_m" ]]; then last_m="$m"; seen_at="$t"; fi
      silence=$(( t - seen_at ))
      if (( silence > heartbeat )); then
        status="killed-stuck"; reason="no heartbeat for ${silence}s (window ${heartbeat}s)"
        kill_tree; break
      fi
    fi
    sleep "$poll"
  done

  recover_finished_leaf

  wait "$pid" 2>/dev/null || true
  secs=$(( $("$awake_clock") - a0 ))
}

role="$(leaf_role "$name")" || role=""

model="$(leaf_model "$name")" || model=""

export VERI_LEAF_MODEL="$model"

skill_commit="$(git -C "$HERE" rev-parse HEAD 2>/dev/null)" || skill_commit=""
export VERI_SKILL_COMMIT="${skill_commit:-${VERI_SKILL_COMMIT:-unknown}}"

mark() {
  [[ -n "$role" ]] || return 0
  env $role "$HERE/event.sh" "$@"
}

ownerfile=".tdd/leaf.owner"
owns_tree="$heartbeat_watched"
case "$name" in conductor-*) owns_tree=0 ;; esac
if [[ -s "$ownerfile" ]]; then
  read -r owner_pid owner_name < "$ownerfile"
  if [[ ! -e ".tdd/$owner_name.exit" ]] && kill -0 "$owner_pid" 2>/dev/null; then
    echo "supervise: refusing to launch $name: leaf ${owner_name:-?} (pid $owner_pid) is still alive in this worktree" >&2
    [[ "$owner_name" == "$name" ]] || printf '2\n' > "$exitfile"
    exit 2
  fi
fi
[[ "$owns_tree" == 0 ]] || printf '%s %s\n' "$$" "$name" > "$ownerfile"

mark launch name="$name" cmd="$*" model="$model"

echo $$ > "$pidfile"

rm -f "$exitfile"

on_signal() {
  [[ -z "${pid:-}" ]] || kill_tree
  printf '2\n' > "$exitfile"
  exit 2
}
trap on_signal TERM INT HUP

preserve_killed_attempt() {
  local attempt="$1"
  [[ "$status" == "killed-stuck" ]] || return 0
  [[ -n "${VERI_ISSUE:-}" && -n "${VERI_STEP:-}" ]] || return 0
  git rev-parse --verify -q HEAD >/dev/null 2>&1 || return 0
  preserve_attempt "supervise[$name]" "$VERI_ISSUE" "$VERI_STEP" "$name" "$attempt" stuck
}

tries=0
while :; do
  attempt_once "$@"
  preserve_killed_attempt "$(( tries + 1 ))"
  [[ "$status" == "killed-stuck" ]] || break
  (( tries >= retries )) && break
  tries=$(( tries + 1 ))
  mark retry cause="$reason"
  echo "supervise[$name]: retry $tries/$retries after killed-stuck" >&2
done

case "$status" in
  success)      ec=0 ;;
  failure)      ec=1; [[ "$rc" != 2 ]] || ec=2 ;;
  killed-stuck) ec=2 ;;
  *)            ec=2; status="killed-stuck"; reason="${reason:-unknown}" ;;
esac

"$HERE/harvest-usage.sh" "$name" >&2 || true

echo "supervise[$name]: $status${reason:+ — $reason}" >&2
payload=(status="$ec")
[[ -z "$reason" ]] || payload+=(cause="$reason")
payload+=(secs="$secs")
mark exit "${payload[@]}"
cat "$log"
number_in "$exitfile" >/dev/null || printf '%s\n' "$ec" > "$exitfile"
exit "$(to_contract "$ec")"
