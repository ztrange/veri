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
  if [[ -n "${victim_pid:-}" ]]; then kill -KILL "$victim_pid" 2>/dev/null || true; fi
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

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
