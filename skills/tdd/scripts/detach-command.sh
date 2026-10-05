#!/usr/bin/env bash
# detach-command.sh — run a long command in a session of its own, then wait on it.
#
# Usage:   detach-command.sh start <name> <cmd> [args…]
#          detach-command.sh wait <name> [max-seconds]
#
# start  returns 0 at once; the command's output goes to .tdd/<name>.out and its exit code
#        to .tdd/<name>.exit when it ends.
# wait   polls every VERI_POLL seconds (default 1) for at most max-seconds (default 60).
#
# Exit codes (wait):
#   0  the command finished and recorded 0
#   1  the command finished and recorded a non-zero code; that code is printed on stdout
#   2  the command died without recording a code, or bad arguments
#   3  no completion file yet — call again
set -uo pipefail

source "$(cd "$(dirname "$0")" && pwd)/lib/exit-contract.sh"
source "$(cd "$(dirname "$0")" && pwd)/lib/detach.sh"
USAGE="usage: detach-command.sh start <name> <cmd> [args…] | wait <name> [max-seconds]"

[[ $# -ge 2 ]] || refuse
mode="$1"; name="$2"; shift 2
exit_file=".tdd/$name.exit"
pid_file=".tdd/$name.pid"

exit_if_recorded() {
  [[ -f "$exit_file" ]] || return 0
  local code; code="$(cat "$exit_file")"
  [[ "$code" == 0 ]] && exit 0
  echo "$code"
  exit 1
}

case "$mode" in
  start)
    [[ $# -gt 0 ]] || refuse
    rm -f "$exit_file"
    detach_exec sh -c '"$@"; rc=$?; echo "$rc" > "$0.tmp"; mv "$0.tmp" "$0"' "$exit_file" "$@" \
      > ".tdd/$name.out" 2>&1 < /dev/null &
    echo $! > "$pid_file"
    ;;
  wait)
    max="${1:-60}"
    [[ "$max" =~ ^[0-9]+$ ]] || refuse
    poll="${VERI_POLL:-1}"
    start=$SECONDS
    while :; do
      exit_if_recorded
      if ! kill -0 "$(cat "$pid_file" 2>/dev/null)" 2>/dev/null; then
        exit_if_recorded
        exit 2
      fi
      (( SECONDS - start >= max )) && exit 3
      sleep "$poll"
    done
    ;;
  *) refuse ;;
esac
