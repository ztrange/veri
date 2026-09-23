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
# The victim reports its own pid so the record can be checked to be that process and not a
# number that merely looks like one; it is `sleep 60`, not a busy loop, so a broken helper
# leaves an idle process for the trap below rather than a spinner like the ones that made
# this issue. Nothing here waits on a timer: the two waits end on a file appearing and on a
# pid going away, on the budget `poll_until` below explains.
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
# The victim outlives the shell that started it by design, so a run that ends before the kill
# — a failing case, an interrupt — must not leave it behind: this suite's own cleanup kills
# it by the pid it read, which is the same rule the helper under test is here to enforce.
cleanup() {
  local pid
  for pid in "${victim_pid:-}" "${victim2_pid:-}" "${victim3a_pid:-}" "${victim3b_pid:-}" "${victim4_pid:-}"; do
    if [[ -n "$pid" ]]; then kill -KILL "$pid" 2>/dev/null || true; fi
  done
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

# 1. A recorded pid kills a process whose starting shell is gone.
record="$work/started.pids"
self_pid="$work/victim.pid"

# The victim: `#!/bin/sh`, like every stub in these suites, since Homebrew's bash costs three
# times as much to start. It reports its own pid and then `exec`s the sleep, so the pid in the
# file is the pid of the process that is still running when the kill arrives.
victim="$work/victim"
cat > "$victim" <<VICTIM
#!/bin/sh
printf '%s\n' "\$\$" > "$self_pid"
exec sleep 60
VICTIM
chmod +x "$victim"

problems=()
victim_pid=""

# The starting shell, and it exits: a subshell that sources the helper, starts the victim
# through it, and returns. From here on there is no job table anywhere that holds the victim.
start_err="$work/start.err"
( source "$LIB" && bg_start "$record" "$victim" ) > /dev/null 2>"$start_err"
start_code=$?

if ! appeared "$record" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start: recorded no pid in $record (exit $start_code, stderr: '$(tr '\n' ' ' < "$start_err")')")
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
    victim_pid="$recorded"
    # The premise: the victim is alive when the kill goes out. Without it a case could go
    # green over a process that had already died of something else.
    kill -0 "$recorded" 2>/dev/null \
      || problems+=("the process bg_start recorded as $recorded was already gone before bg_kill was called")

    # The kill, from a shell that never started it — where a job spec names nothing.
    kill_err="$work/kill.err"
    ( source "$LIB" && bg_kill "$record" ) > /dev/null 2>"$kill_err"
    kill_code=$?

    gone "$recorded" "$PATIENCE" \
      || problems+=("after bg_kill (exit $kill_code, stderr: '$(tr '\n' ' ' < "$kill_err")') the recorded process $recorded is still running — a kill that named a job spec reaches nothing from a shell whose job table never held it")
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
cat > "$victim2" <<VICTIM2
#!/bin/sh
printf '%s\n' "\$\$" > "$self_pid2"
exec sleep 60
VICTIM2
chmod +x "$victim2"

problems=()
victim2_pid=""

exit_err="$work/abandoned.err"
( source "$LIB" && bg_start "$record2" "$victim2" ) > /dev/null 2>"$exit_err"
exit_code=$?

if ! appeared "$record2" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start: recorded no pid in $record2 (exit $exit_code, stderr: '$(tr '\n' ' ' < "$exit_err")')")
else
  read -r victim2_pid _ < "$record2" || true
  said="$(tr '\n' ' ' < "$exit_err")"

  # The premise: the victim really did outlive the shell that started it. Without it the case
  # could go green over a report about a process that had already died on its own.
  if [[ "$victim2_pid" =~ ^[0-9]+$ ]] && ! kill -0 "$victim2_pid" 2>/dev/null; then
    problems+=("the process bg_start recorded as $victim2_pid was already gone when its starting shell exited, so there was nothing to report")
  fi

  grep -F "$victim2_pid" "$exit_err" > /dev/null \
    || problems+=("the shell that started pid $victim2_pid exited while it was still running and did not name it: stderr said '$said'")
  grep -F "$victim2" "$exit_err" > /dev/null \
    || problems+=("the report does not name what started the survivor ('$victim2'): stderr said '$said'")

  kill -KILL "$victim2_pid" 2>/dev/null || true
fi

report "a process still running when its starting shell exits is reported on that shell's stderr, naming its pid and what started it"

# make_victim <path> <pid-file> — a background process that reports its own pid and then
# `exec`s a sleep, so the pid in the file is the pid still running when the kill arrives.
# `#!/bin/sh`, like every stub in these suites, since Homebrew's bash costs three times as
# much to start.
make_victim() {
  cat > "$1" <<VICTIM
#!/bin/sh
printf '%s\n' "\$\$" > "$2"
exec sleep 60
VICTIM
  chmod +x "$1"
}

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
victim3a_pid=""
victim3b_pid=""

pair_err="$work/pair.err"
( source "$LIB" && bg_start "$record3" "$victim3a" && bg_start "$record3" "$victim3b" ) \
  > /dev/null 2>"$pair_err"
pair_code=$?

if ! appeared "$record3" "$PATIENCE"; then
  problems+=("sourcing $LIB and calling bg_start twice on one record: recorded nothing in $record3 (exit $pair_code, stderr: '$(tr '\n' ' ' < "$pair_err")')")
else
  { read -r victim3a_pid _; read -r victim3b_pid _; } < "$record3" || true
  said3="$(tr '\n' ' ' < "$pair_err")"

  if [[ ! "$victim3a_pid" =~ ^[0-9]+$ || ! "$victim3b_pid" =~ ^[0-9]+$ ]]; then
    problems+=("two bg_start calls on one record left '$victim3a_pid' and '$victim3b_pid' in $record3, not two pids")
  else
    # The premise: both really did outlive the shell that started them, so both were there
    # to be reported. Without it the count below could be right for the wrong reason.
    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do
      kill -0 "$probe_pid" 2>/dev/null \
        || problems+=("the process bg_start recorded as $probe_pid was already gone when its starting shell exited, so there was nothing to report")
    done

    for probe_pid in "$victim3a_pid" "$victim3b_pid"; do
      lines="$(grep -c -F "$probe_pid" "$pair_err" || true)"
      [[ "$lines" -eq 1 ]] \
        || problems+=("the survivor $probe_pid is named on $lines lines of the starting shell's stderr, not 1 — a record started into twice is reported twice over: stderr said '$said3'")
    done
  fi

  kill -KILL "$victim3a_pid" 2>/dev/null || true
  kill -KILL "$victim3b_pid" 2>/dev/null || true
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

if [[ -e "$record4" ]]; then
  problems+=("the case never reached the state it is about: $record4 still exists after the shell that made it exited (exit $removed_code)")
fi
if [[ -s "$removed_err" ]]; then
  problems+=("a shell whose record was removed before it exited still said something on stderr: '$(tr '\n' ' ' < "$removed_err")' — a record it can no longer read is not a survivor to report")
fi

report "a shell whose record file is gone by the time it exits reports nothing, rather than failing to read it on the caller's stderr"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
