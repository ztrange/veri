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
STOP="$HERE/../stop-run.sh"

work="$(scratch_dir)"
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

problems=()
run_stop --mode now 5
check_code 0
[[ "$out" == *5* ]] || note "want the run named on stdout, got '$out'"
check_stop "$run" now

report "--mode now <n> writes now as the only line of that run's .tdd/stop, names the run on stdout and exits 0"

dead="$repo/.tdd/wt/9"
dead_conductor "$dead"

problems=()

label="an issue with no worktree"
run_stop 404
check_code 3
[[ ! -e "$repo/.tdd/wt/404" ]] ||
  note "want nothing written for a run that does not exist, found $repo/.tdd/wt/404"

label="an issue whose conductor is not live"
run_stop 9
check_code 3
check_no_stop "$dead"

label="--all with no live run"
quiet="$work/quiet"
new_repo -b main "$quiet" >/dev/null 2>&1
quiet_dead="$quiet/.tdd/wt/9"
dead_conductor "$quiet_dead"
run_stop_in "$quiet" --all
check_code 3
check_no_stop "$quiet_dead"

report "an issue with no worktree, an issue whose conductor names no live process, and --all with no live run each exit 3 and write no .tdd/stop"

problems=()
label=""
rm -f "$run/.tdd/stop"

live_supervisor "$run" develop-green
green_sup="$supervisor_pid"

sleep 60 &
impostor=$!; alive+=("$impostor")
printf '%s\n' "$impostor" > "$run/.tdd/verify-green.pid"

reaped_pid; stale_pid="$reaped"
printf '%s\n' "$stale_pid" > "$run/.tdd/verify-refactor.pid"

gone() {
  local pid="$1" i
  for (( i = 0; i < 40; i++ )); do
    kill -0 "$pid" 2>/dev/null || return 0
    sleep 0.05
  done
  return 1
}

run_stop --mode now 5
check_code 0
gone "$green_sup" ||
  note "want the develop-green supervisor $green_sup signalled, it is still answering"
check_still_answering "$impostor" "the pid running something other than a supervisor"

report "--mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs supervise.sh <name>, and to no pid whose process is gone or runs something else"

problems=()
label=""
rm -f "$run/.tdd/stop"

pybin="$work/pybin"; mkdir -p "$pybin/veri"
cat > "$pybin/veri/supervise.py" <<'S'
#!/bin/sh
while :; do sleep 0.2; done
S
chmod +x "$pybin/veri/supervise.py"
"$pybin/veri/supervise.py" develop-refactor 5 &
py_sup=$!; alive+=("$py_sup")
printf '%s\n' "$py_sup" > "$run/.tdd/develop-refactor.pid"

run_stop --mode now 5
check_code 0
gone "$py_sup" ||
  note "want the develop-refactor supervisor $py_sup, spelled veri/supervise.py, signalled, it is still answering"

report "--mode now <n> sends TERM to the pid in <run>/.tdd/<name>.pid whose process runs veri/supervise.py <name>"

problems=()

live_supervisor "$run" develop-red
quiet_sup="$supervisor_pid"

for gentle in at-ledger at-leaf; do
  label="--mode $gentle"
  rm -f "$run/.tdd/stop"
  run_stop --mode "$gentle" 5
  check_code 0
  check_stop "$run" "$gentle"
  check_still_answering "$quiet_sup" "the live supervisor"
done
label=""

report "--mode at-ledger <n> and --mode at-leaf <n> write the mode and signal nothing"

problems=()
label=""

conductor_run="$repo/.tdd/wt/11"
mkdir -p "$conductor_run/.tdd"
marker="$work/conductor-signalled"
rm -f "$marker"

trapbin="$work/trapbin"; mkdir -p "$trapbin"
cat > "$trapbin/supervise.sh" <<'S'
#!/bin/sh
trap 'echo signalled > "$MARKER"; exit 0' TERM
while :; do sleep 0.05; done
S
chmod +x "$trapbin/supervise.sh"

MARKER="$marker" "$trapbin/supervise.sh" conductor 11 &
fake_conductor=$!; alive+=("$fake_conductor")
printf '%s\n' "$fake_conductor" > "$conductor_run/.tdd/conductor.pid"

run_stop --mode now 11
check_code 0
check_stop "$conductor_run" now

signalled=0
for (( i = 0; i < 12; i++ )); do
  if [[ -e "$marker" ]]; then signalled=1; break; fi
  sleep 0.05
done
(( signalled == 0 )) ||
  note "want the conductor $fake_conductor untouched, it took a TERM"

report "stop-run.sh never signals the pid in .tdd/conductor.pid"

problems=()
label=""
rm -f "$run/.tdd/stop"

run_stop --mode bogus 5
check_code 2
[[ "${err%%$'\n'*}" == "stop-run: unknown mode — want at-ledger, at-leaf or now: 'bogus'" ]] ||
  note "want today's unknown-mode refusal first on stderr, got '$err'"
check_no_stop "$run"

run_stop
check_code 2
[[ "${err##*$'\n'}" == "usage: stop-run.sh [--mode at-ledger|at-leaf|now] <issue> | --all" ]] ||
  note "want today's usage line last on stderr, got '${err##*$'\n'}'"

report "stop-run.sh refuses an unknown mode with today's message first on stderr and no argument with today's usage line last on stderr, each exiting 2"

problems=()
label=""

linked="$work/linked-scripts"
ln -s "$HERE/.." "$linked"
elsewhere="$work/elsewhere"
new_repo -b main "$elsewhere" >/dev/null 2>&1
far_issue=31337
far_run="$elsewhere/.tdd/wt/$far_issue"
live_conductor "$far_run"
deep="$elsewhere/some/sub/dir"; mkdir -p "$deep"
skill_main="$(git -C "$HERE" worktree list --porcelain | sed -n '1s/^worktree //p')"

out="$(cd "$deep" && "$linked/stop-run.sh" "$far_issue" 2>"$work/stderr")" && code=0 || code=$?
err="$(cat "$work/stderr")"
check_code 0
check_stop "$far_run" at-ledger
[[ "$out" != *$'\n'* && "$out" -ef "$far_run" ]] ||
  note "want $far_run alone on stdout, got '$out'"
[[ -n "$skill_main" && ! -e "$skill_main/.tdd/wt/$far_issue" ]] ||
  note "want nothing written under the skill's own repository '$skill_main', found $skill_main/.tdd/wt/$far_issue"

report "stop-run.sh, run through a symlink to the skill's scripts directory from a subdirectory of another repository, stops that repository's run and writes nothing under the skill's own"

problems=()
label=""
rm -f "$run/.tdd/stop"

decoy="$work/decoy"
new_repo -b main "$decoy" >/dev/null 2>&1
decoy_run="$decoy/.tdd/wt/5"
live_conductor "$decoy_run"
live_supervisor "$decoy_run" develop-red
decoy_sup="$supervisor_pid"
mutant="$decoy/skills/tdd/scripts"
mkdir -p "$mutant"
cp -R "$HERE/../veri" "$mutant/veri"
awk '/^exec python3/ { print "cd \"$(dirname \"$0\")\"" } { print }' "$HERE/../stop-run.sh" > "$mutant/stop-run.sh"
chmod +x "$mutant/stop-run.sh"

real_stop="$STOP"
STOP="$mutant/stop-run.sh"
run_stop --mode now --all
STOP="$real_stop"

check_no_stop "$decoy_run"
check_still_answering "$decoy_sup" "the decoy repository's live supervisor"
[[ "$code" != 0 || "$out" != *"$decoy"* ]] ||
  note "want a subject that resolved the decoy repository to fail the case, it exited 0 naming '$out'"

report "#1158: a stop-run.sh that resolves its main tree from its own directory, not the suite's scratch repository, writes no .tdd/stop and signals no supervisor outside that repository"

finish
