#!/usr/bin/env bash
# Tests for scripts/stop-run.sh — the operator's stop command, the write half of the stop
# mechanism whose read half is stop-requested.sh.
#
# Contract under test:
#   stop-run.sh, typed from anywhere in the repository, finds the runs under the main
#   working tree's .tdd/wt/*, writes the mode into each live run's .tdd/stop, and — for
#   `--mode now` only — sends TERM to that run's live leaf supervisors.
#
# Run: scripts/tests/stop-run.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"
mkdir -p "$work/skill/scripts"
cp -R "$HERE/../stop-run.sh" "$HERE/../veri" "$work/skill/scripts/"
STOP="$work/skill/scripts/stop-run.sh"
alive=()
cleanup() {
  local pid
  for pid in ${alive[@]+"${alive[@]}"}; do kill "$pid" 2>/dev/null; done
  for pid in ${alive[@]+"${alive[@]}"}; do wait "$pid" 2>/dev/null; done
  rm -rf "$work"
}
on_exit cleanup

repo="$work/repo"
new_repo -b main "$repo" >/dev/null 2>&1
run="$repo/.tdd/wt/5"
mkdir -p "$run/.tdd"

stubbin="$work/stubbin"; mkdir -p "$stubbin"
cat > "$stubbin/supervise.sh" <<'S'
#!/bin/sh
while :; do sleep 0.2; done
S
chmod +x "$stubbin/supervise.sh"

live_supervisor() {
  "$stubbin/supervise.sh" "$2" "$(basename "$1")" &
  supervisor_pid=$!; alive+=("$supervisor_pid")
  printf '%s\n' "$supervisor_pid" > "$1/.tdd/$2.pid"
}

live_supervisor "$run" develop-red
sup_pid="$supervisor_pid"

live_conductor() {
  mkdir -p "$1/.tdd"
  sleep 60 &
  conductor_pid=$!; alive+=("$conductor_pid")
  printf '%s\n' "$conductor_pid" > "$1/.tdd/conductor.pid"
}

reaped_pid() {
  sleep 0 &
  reaped=$!
  wait "$reaped" 2>/dev/null
}

dead_conductor() {
  mkdir -p "$1/.tdd"
  reaped_pid
  printf '%s\n' "$reaped" > "$1/.tdd/conductor.pid"
}

live_conductor "$run"
run_conductor_pid="$conductor_pid"

problems=()

note() { problems+=("${label:+$label: }$1"); }


run_stop_in() {
  local dir="$1"; shift
  out="$(cd "$dir" && "$STOP" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

run_stop() { run_stop_in "$repo" "$@"; }

check_code() { [[ "$code" == "$1" ]] || note "want exit $1, got exit $code (stderr: $err)"; }

check_no_stop() {
  [[ ! -e "$1/.tdd/stop" ]] ||
    note "want no .tdd/stop for $1, found one holding '$(cat "$1/.tdd/stop")'"
}

check_still_answering() {
  kill -0 "$1" 2>/dev/null || note "want $2 $1 untouched, it is gone"
}

check_stop() {
  local path="$1/.tdd/stop" want="$2" written lines
  if [[ ! -f "$path" ]]; then
    note "want $path holding '$want', it was not written"
    return
  fi
  written="$(cat "$path")"
  [[ "$written" == "$want" ]] || note "want $path to hold '$want', it holds '$written'"
  lines="$(grep -c '' "$path")"
  [[ "$lines" == 1 ]] || note "want '$want' as the only line of $path, it has $lines lines"
}

finish
