#!/usr/bin/env bash
# Unit tests for scripts/lib/background.sh — the one place a background process is started
# and later killed, so that the kill names the pid that was recorded when it started and
# never a job spec (issue #424).
# Zero-dependency plain-shell asserts, same idiom as detach-leaf.test.sh.
#
# Why this exists: a job spec dies with the shell that owns the job table it names, where a
# pid is a system-wide name a kill can use from any shell — `lib/background.sh`'s own header
# carries that mechanism and the ten orphaned busy-loops it cost this machine on 2026-09-22,
# and is the one copy of it. What follows is what only a test can say: how the two halves of
# that claim are watched.
#
# Contract under test (this step only):
#   source lib/background.sh
#   bg_start <record> <cmd> [args...]  → runs the command in the background and records its
#                                        pid in <record>
#   bg_kill  <record>                  → every process recorded in <record> is dead, whether
#                                        or not the shell that started it is still alive
#   a shell that exits with a recorded process still running says so on its own stderr,
#   naming that pid and what started it, rather than leaving it silently — once per survivor
#   however many times that record was started into, and not at all when the record itself is
#   gone by the time the shell exits
#
# Asked by watching a real process rather than by reading the source: the victim is started
# inside a subshell which then EXITS, and the kill is issued from a different subshell
# afterwards. That is the whole discrimination — a `kill %1` in the second shell reaches
# nothing, because its job table never held the victim — and no cheaper probe establishes it.
# What the victim itself is, and why, is `make_victim` below. Nothing here waits on a timer:
# the two waits end on a file appearing and on a pid going away, on the budget `poll_until`
# below explains.
#
# Run: scripts/tests/background-kill.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib/background.sh"

PATIENCE=3


source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

victims=()

end_victim() {
  [[ -n "$1" ]] || return 0
  kill -KILL "$1" 2>/dev/null || true
}

cleanup() {
  local pid
  for pid in "${victims[@]}"; do end_victim "$pid"; done
  rm -rf "$work"
}
on_exit cleanup

poll_until() {
  local cap=$(( $1 * 50 )) looks=0
  shift
  while [[ "$looks" -lt "$cap" ]]; do
    "$@" && return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  "$@"
}

dead() {
  ! kill -0 "$1" 2>/dev/null
}

appeared() {
  poll_until "$2" test -s "$1"
}

gone() {
  poll_until "$2" dead "$1"
}

flat() {
  tr '\n' ' ' < "$1"
}

survived() {
  kill -0 "$1" 2>/dev/null \
    || problems+=("the process bg_start recorded as $1 was already gone when its starting shell exited, so there was nothing to report")
}

named_once() {
  local lines
  lines="$(grep -c -F "$1" "$2" || true)"
  [[ "$lines" -eq 1 ]] \
    || problems+=("the survivor $1 is named on $lines lines of the starting shell's stderr, not 1: stderr said '$(flat "$2")'")
}

make_victim() {
  cat > "$1" <<VICTIM
#!/bin/sh
printf '%s\n' "\$\$" > "$2"
exec sleep 60
VICTIM
  chmod +x "$1"
}

record="$work/started.pids"
self_pid="$work/victim.pid"

victim="$work/victim"
make_victim "$victim" "$self_pid"

problems=()

start_err="$work/start.err"
( source "$LIB" && bg_start "$record" "$victim" ) > /dev/null 2>"$start_err"
start_code=$?

if ! appeared "$record" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start: recorded no pid in $record (exit $start_code, stderr: '$(flat "$start_err")')")
else
  recorded=""
  read -r recorded _ < "$record" || true
  appeared "$self_pid" "$PATIENCE" || true
  actual=""
  read -r actual < "$self_pid" 2>/dev/null || true
  [[ -n "$recorded" && "$recorded" == "$actual" ]] \
    || problems+=("bg_start recorded '$recorded' in $record, but the process it started reported pid '$actual'")

  if [[ "$recorded" =~ ^[0-9]+$ ]]; then
    victims+=("$recorded")
    kill -0 "$recorded" 2>/dev/null \
      || problems+=("the process bg_start recorded as $recorded was already gone before bg_kill was called")

    kill_err="$work/kill.err"
    ( source "$LIB" && bg_kill "$record" ) > /dev/null 2>"$kill_err"
    kill_code=$?

    gone "$recorded" "$PATIENCE" \
      || problems+=("after bg_kill (exit $kill_code, stderr: '$(flat "$kill_err")') the recorded process $recorded is still running — a kill that named a job spec reaches nothing from a shell whose job table never held it")
  fi
fi

report "a background process bg_start started is killed by its recorded pid, so bg_kill ends it from a shell that is not the one that started it"

record2="$work/abandoned.pids"
self_pid2="$work/victim2.pid"

victim2="$work/victim2"
make_victim "$victim2" "$self_pid2"

problems=()

exit_err="$work/abandoned.err"
( source "$LIB" && bg_start "$record2" "$victim2" ) > /dev/null 2>"$exit_err"
exit_code=$?

if ! appeared "$record2" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start: recorded no pid in $record2 (exit $exit_code, stderr: '$(flat "$exit_err")')")
else
  read -r victim2_pid _ < "$record2" || true
  victims+=("$victim2_pid")
  said="$(flat "$exit_err")"

  if [[ "$victim2_pid" =~ ^[0-9]+$ ]]; then survived "$victim2_pid"; fi

  grep -F "$victim2_pid" "$exit_err" > /dev/null \
    || problems+=("the shell that started pid $victim2_pid exited while it was still running and did not name it: stderr said '$said'")
  grep -F "$victim2" "$exit_err" > /dev/null \
    || problems+=("the report does not name what started the survivor ('$victim2'): stderr said '$said'")

  end_victim "$victim2_pid"
fi

report "a process still running when its starting shell exits is reported on that shell's stderr, naming its pid and what started it"

record3="$work/pair.pids"
self_pid3a="$work/victim3a.pid"
self_pid3b="$work/victim3b.pid"
victim3a="$work/victim3a"
victim3b="$work/victim3b"
make_victim "$victim3a" "$self_pid3a"
make_victim "$victim3b" "$self_pid3b"

problems=()

pair_err="$work/pair.err"
( source "$LIB" && bg_start "$record3" "$victim3a" && bg_start "$record3" "$victim3b" ) \
  > /dev/null 2>"$pair_err"
pair_code=$?

if ! appeared "$record3" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start twice on one record: recorded nothing in $record3 (exit $pair_code, stderr: '$(flat "$pair_err")')")
else
  { read -r victim3a_pid _; read -r victim3b_pid _; } < "$record3" || true
  victims+=("$victim3a_pid" "$victim3b_pid")

  if [[ ! "$victim3a_pid" =~ ^[0-9]+$ || ! "$victim3b_pid" =~ ^[0-9]+$ ]]; then
    problems+=("two bg_start calls on one record left '$victim3a_pid' and '$victim3b_pid' in $record3, not two pids")
  else
    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do survived "$probe_pid"; done

    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do named_once "$probe_pid" "$pair_err"; done
  fi

  end_victim "$victim3a_pid"
  end_victim "$victim3b_pid"
fi

report "a record started into twice names each survivor once when the starting shell exits, not once per bg_start call"

record4="$work/removed.pids"
kept4="$work/removed.copy"

problems=()
victim4_pid=""

removed_err="$work/removed.err"
( source "$LIB" && bg_start "$record4" sleep 60 && cp "$record4" "$kept4" \
    && bg_kill "$record4" && rm -f "$record4" ) > /dev/null 2>"$removed_err"
removed_code=$?

read -r victim4_pid _ < "$kept4" 2>/dev/null || true
victims+=("$victim4_pid")

if [[ -e "$record4" ]]; then
  problems+=("the case never reached the state it is about: $record4 still exists after the shell that made it exited (exit $removed_code)")
fi
if [[ -s "$removed_err" ]]; then
  problems+=("a shell whose record was removed before it exited still said something on stderr: '$(flat "$removed_err")' — a record it can no longer read is not a survivor to report")
fi

report "a shell whose record file is gone by the time it exits reports nothing, rather than failing to read it on the caller's stderr"

record5="$work/trapped.pids"
self_pid5="$work/victim5.pid"
marker5="$work/caller-trap.ran"
victim5="$work/victim5"
make_victim "$victim5" "$self_pid5"

problems=()

trapped_err="$work/trapped.err"
( trap "touch '$marker5'" EXIT; source "$LIB" && bg_start "$record5" "$victim5" ) \
  > /dev/null 2>"$trapped_err"
trapped_code=$?

if ! appeared "$record5" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start under a caller's EXIT trap: recorded no pid in $record5 (exit $trapped_code, stderr: '$(flat "$trapped_err")')")
else
  read -r victim5_pid _ < "$record5" || true
  victims+=("$victim5_pid")
  said5="$(flat "$trapped_err")"

  if [[ "$victim5_pid" =~ ^[0-9]+$ ]]; then survived "$victim5_pid"; fi

  [[ -e "$marker5" ]] \
    || problems+=("the EXIT trap the caller set before bg_start never ran: $marker5 was not created (exit $trapped_code, stderr: '$said5')")
  grep -F "$victim5_pid" "$trapped_err" > /dev/null \
    || problems+=("the shell that set its own EXIT trap before bg_start exited with pid $victim5_pid still running and did not name it: stderr said '$said5'")

  end_victim "$victim5_pid"
fi

report "#536: a shell that set an EXIT trap before bg_start still runs that trap at exit, and still reports a survivor"

record6a="$work/repeat-a.pids"
record6b="$work/repeat-b.pids"
marker6="$work/caller-trap-repeat.ran"
victim6a1="$work/victim6a1"
victim6a2="$work/victim6a2"
victim6b="$work/victim6b"
make_victim "$victim6a1" "$work/victim6a1.pid"
make_victim "$victim6a2" "$work/victim6a2.pid"
make_victim "$victim6b" "$work/victim6b.pid"

problems=()

repeat_err="$work/repeat.err"
( trap "echo ran >> '$marker6'" EXIT; source "$LIB" && bg_start "$record6a" "$victim6a1" \
    && bg_start "$record6a" "$victim6a2" && bg_start "$record6b" "$victim6b" ) \
  > /dev/null 2>"$repeat_err"
repeat_code=$?

if ! appeared "$record6a" "$PATIENCE" || ! appeared "$record6b" "$PATIENCE"; then
  problems+=("three bg_start calls under a caller's EXIT trap recorded nothing in $record6a or $record6b (exit $repeat_code, stderr: '$(flat "$repeat_err")')")
else
  victim6a1_pid="" victim6a2_pid="" victim6b_pid=""
  { read -r victim6a1_pid _; read -r victim6a2_pid _; } < "$record6a" || true
  read -r victim6b_pid _ < "$record6b" || true
  victims+=("$victim6a1_pid" "$victim6a2_pid" "$victim6b_pid")

  for probe_pid in "$victim6a1_pid" "$victim6a2_pid" "$victim6b_pid"; do
    if [[ ! "$probe_pid" =~ ^[0-9]+$ ]]; then
      problems+=("the records hold '$probe_pid' where a pid was expected")
      continue
    fi
    survived "$probe_pid"
    named_once "$probe_pid" "$repeat_err"
  done

  ran="$(grep -c -F ran "$marker6" 2>/dev/null || true)"
  [[ "${ran:-0}" -eq 1 ]] \
    || problems+=("the EXIT trap the caller set before bg_start ran ${ran:-0} times, not 1 (exit $repeat_code)")

  for probe_pid in "$victim6a1_pid" "$victim6a2_pid" "$victim6b_pid"; do end_victim "$probe_pid"; done
fi

report "#536: a shell that set an EXIT trap and calls bg_start again, on the same record and on a second, names each survivor once and runs its own trap once"

finish
