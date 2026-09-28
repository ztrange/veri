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

# How long, at most, anything here waits, in seconds. A passing run never reaches it.
PATIENCE=3

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

work="$(mktemp -d)"

# Every pid a case has started, appended as soon as the case knows it, so the cleanup below
# needs no roster of its own to keep in step with the cases.
victims=()

# end_victim <pid> — make sure <pid> is not running, quietly. A pid that is already gone, or
# an empty one a case never got, is not an error: the point of the call is that nothing is
# left running.
end_victim() {
  [[ -n "$1" ]] || return 0
  kill -KILL "$1" 2>/dev/null || true
}

# The victim outlives the shell that started it by design, so a run that ends before the kill
# — a failing case, an interrupt — must not leave it behind: this suite's own cleanup kills
# it by the pid it read, which is the same rule the helper under test is here to enforce.
cleanup() {
  local pid
  for pid in "${victims[@]}"; do end_victim "$pid"; done
  rm -rf "$work"
}
trap cleanup EXIT

# poll_until <seconds> <cmd> [args…] — true once <cmd> succeeds, looked at fifty times a
# second up to a budget and returning on the first look that succeeds. The budget only bounds
# how long a failing run takes to say so: a passing run never reaches it.
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

# dead <pid> — true once <pid> is no longer a running process. A killed process is not gone
# the instant the signal is sent, which is why callers poll this rather than read it once.
dead() {
  ! kill -0 "$1" 2>/dev/null
}

# appeared <file> <seconds> — true once <file> holds something.
appeared() {
  poll_until "$2" test -s "$1"
}

# gone <pid> <seconds> — true once <pid> is no longer a running process.
gone() {
  poll_until "$2" dead "$1"
}

# flat <file> — <file>'s contents on one line. A problem message is printed as one indented
# line, so a multi-line stderr quoted raw inside it would break out of that shape.
flat() {
  tr '\n' ' ' < "$1"
}

# survived <pid> — a case's premise that <pid> really did outlive the shell that started it,
# so there was something for that shell to report. Without it a case could go green over a
# report about a process that had already died on its own. It appends to `problems` rather
# than returning a status, the way the assertions it sits among do.
survived() {
  kill -0 "$1" 2>/dev/null \
    || problems+=("the process bg_start recorded as $1 was already gone when its starting shell exited, so there was nothing to report")
}

# named_once <pid> <stderr-file> — <pid> is named on exactly one line of <stderr-file>, so a
# survivor reported twice over is told apart from one reported once.
named_once() {
  local lines
  lines="$(grep -c -F "$1" "$2" || true)"
  [[ "$lines" -eq 1 ]] \
    || problems+=("the survivor $1 is named on $lines lines of the starting shell's stderr, not 1: stderr said '$(flat "$2")'")
}

# make_victim <path> <pid-file> — a background process that reports its own pid and then
# `exec`s a sleep, so the pid in the file is the pid still running when the kill arrives, and
# the record can be checked to be that process rather than a number that merely looks like one.
# It is a sleep and not a busy loop, so a broken helper leaves an idle process for the trap
# above rather than a spinner like the ones that made this issue. `#!/bin/sh`, like every stub
# in these suites, since Homebrew's bash costs three times as much to start.
make_victim() {
  cat > "$1" <<VICTIM
#!/bin/sh
printf '%s\n' "\$\$" > "$2"
exec sleep 60
VICTIM
  chmod +x "$1"
}

# 1. A recorded pid kills a process whose starting shell is gone.
record="$work/started.pids"
self_pid="$work/victim.pid"

victim="$work/victim"
make_victim "$victim" "$self_pid"

problems=()

# The starting shell, and it exits: a subshell that sources the helper, starts the victim
# through it, and returns. From here on there is no job table anywhere that holds the victim.
start_err="$work/start.err"
( source "$LIB" && bg_start "$record" "$victim" ) > /dev/null 2>"$start_err"
start_code=$?

if ! appeared "$record" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start: recorded no pid in $record (exit $start_code, stderr: '$(flat "$start_err")')")
else
  # The first field of the first recorded line, so a record that also names what started the
  # process reads the same way as one that holds the bare number.
  recorded=""
  read -r recorded _ < "$record" || true
  appeared "$self_pid" "$PATIENCE" || true
  actual=""
  read -r actual < "$self_pid" 2>/dev/null || true
  [[ -n "$recorded" && "$recorded" == "$actual" ]] \
    || problems+=("bg_start recorded '$recorded' in $record, but the process it started reported pid '$actual'")

  if [[ "$recorded" =~ ^[0-9]+$ ]]; then
    victims+=("$recorded")
    # The premise: the victim is alive when the kill goes out. Without it a case could go
    # green over a process that had already died of something else.
    kill -0 "$recorded" 2>/dev/null \
      || problems+=("the process bg_start recorded as $recorded was already gone before bg_kill was called")

    # The kill, from a shell that never started it — where a job spec names nothing.
    kill_err="$work/kill.err"
    ( source "$LIB" && bg_kill "$record" ) > /dev/null 2>"$kill_err"
    kill_code=$?

    gone "$recorded" "$PATIENCE" \
      || problems+=("after bg_kill (exit $kill_code, stderr: '$(flat "$kill_err")') the recorded process $recorded is still running — a kill that named a job spec reaches nothing from a shell whose job table never held it")
  fi
fi

report "a background process bg_start started is killed by its recorded pid, so bg_kill ends it from a shell that is not the one that started it"

# 2. A process still running when the shell that started it exits is reported by that shell,
# naming the pid and what started it. Asked the only way it can be: a subshell sources the
# helper, starts the victim and then RETURNS without killing it, and the case reads what that
# subshell wrote to its own stderr as it went. Nothing else here waits on the victim — the
# report is written at the exit, so it is on the file the moment the subshell is reaped.
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

# 3. One record started into twice is reported once per survivor, not once per call. The
# report walks the records this shell started something into, so a record remembered twice
# would be read twice and every survivor in it named twice — two processes, four lines. The
# case counts the lines that name each pid, which is the only thing that tells the two apart.
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
    # Both, since the count below could otherwise be right for the wrong reason.
    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do survived "$probe_pid"; done

    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do named_once "$probe_pid" "$pair_err"; done
  fi

  end_victim "$victim3a_pid"
  end_victim "$victim3b_pid"
fi

report "a record started into twice names each survivor once when the starting shell exits, not once per bg_start call"

# 4. A record that is gone by the time the shell exits is passed over silently. The ordinary
# shape of a caller is bg_start, bg_kill, then throw the scratch directory away — and the
# report runs after all three, on a path that no longer exists. Reading it anyway is the
# shell's own "No such file or directory" on the caller's stderr, at the one moment the
# caller has already finished and cannot answer for it.
# The victim is a bare `sleep`, not one of the reporting stubs above: this case kills it
# before the shell exits, so a pid file it wrote for itself would be a race it never needs
# to win. What cleanup needs instead is the record, and the shell copies it aside on its way
# past so a bg_kill that failed still leaves a pid this suite can end.
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

# 5. A shell that armed its own EXIT trap before bg_start still runs it at exit, and still
# reports the survivor. The earlier trap writes a marker file, so whether it ran is read off
# the disk after the subshell is reaped.
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

# 6. The same shell as case 5, calling bg_start three times: twice into one record, then into
# a second. Each survivor is named on exactly one line and the earlier trap appends exactly
# one line to its marker, whichever call armed what.
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

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
