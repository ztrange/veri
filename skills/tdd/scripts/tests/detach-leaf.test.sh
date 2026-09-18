#!/usr/bin/env bash
# Unit tests for scripts/detach-leaf.sh — the launcher every leaf launch goes through, which
# runs its argv as a new session leader and returns at once (issue #161).
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists: `nohup … &` was the detach in SKILL.md's *Launching a leaf* since #86, and
# `nohup` only makes the child ignore SIGHUP. It leaves the child in the PROCESS GROUP of the
# Bash call that launched it, so a harness that signals that group when the call ends takes
# the leaf with it. Observed 2026-09-12 23:43 UTC on a conductor for #123: the Bash call came
# back `Exit code 144`, `.tdd/verdict-red.exit` was never written, and `verify.sh red` was
# gone. A leaf killed that way writes no completion file, `wait-leaf.sh` then returns exit 3
# forever, and SKILL.md:88-89 tells the conductor that means "still running" — so the run
# stalls with nothing to say why.
#
# Contract under test (this step only):
#   detach-leaf.sh <cmd> [args...]  → the launched process keeps running, and writes its
#                                     completion file, after a TERM is sent to the process
#                                     group of the shell that launched it.
#
# Asked by watching it rather than by reading the script: a harness shell is put in a process
# group of its OWN (`set -m` gives a background job its own pgid), it launches two children
# there — one through the launcher, one with the plain `nohup … &` this replaces — and one
# TERM to that group decides both. The `nohup` child is the premise, not a second criterion:
# without it a TERM that reached nothing at all would leave the launcher's child alive and
# this case green over a signal that was never delivered. Neither child writes until the
# suite says so, with a GO file it creates only after the TERM, so both are alive when the
# signal lands however loaded the machine is, and nothing here waits on a timer. A launcher
# that runs the leaf in the FOREGROUND blocks the harness on that same GO, which never comes,
# so the harness never reports its launches returned — the failure the timed launch used to
# catch, now caught without a timer.
#
# Run: scripts/tests/detach-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETACH="$HERE/../detach-leaf.sh"

# How long, at most, anything here waits, in seconds. Every wait ends on a file or a pid
# instead of a timer, so a passing run never reaches it: it bounds only how long a broken
# launcher can make the case take before it reports.
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
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# The two completion files, named the way supervise.sh names its own — `.tdd/<name>.exit`,
# holding a status — because that is the file wait-leaf.sh polls for and the thing whose
# absence stalls a run. `0` rather than a bare touch: an empty file is not a status, and
# wait-leaf.sh goes on polling past one, so "wrote its completion file" has to mean a
# readable code landed in it.
DETACHED_EXIT="$work/.tdd/detached-leaf.exit"
CONTROL_EXIT="$work/.tdd/control-leaf.exit"

# Everything else the probes read is a file too, and for the same reason the comment on the
# probe below gives: the harness is another process, and the signalling runs in a subshell
# whose output is discarded, so neither can hand a variable back. Naming them here says which
# five channels there are, and keeps the reader from having to notice that the `$work/why-no-term`
# a probe reports on is the one the subshell three functions up wrote.
LAUNCHED_MARKER="$work/launched"       # harness: both launches have returned
DETACHED_PID="$work/detached.pid"      # child: the launcher's child is running, in its session
CONTROL_PID="$work/control.pid"        # child: the nohup control is running
GO="$work/go"                          # suite: the TERM has been sent; the children may write
ALIVE_AT_TERM="$work/alive-at-term"    # subshell: which children were running when it was sent
HARNESS_PGID="$work/harness.pgid"      # subshell: the process group the harness landed in
TERM_SENT="$work/term.sent"            # subshell: the signal went out
WHY_NO_TERM="$work/why-no-term"        # subshell: …or it did not, and this is what stopped it

# The leaf both children run, as one script: record its pid, wait for GO, then write a status
# into its exit file. One script rather than two, because the two children have to differ in
# nothing but how they were launched: a wait or a status that drifted between them would leave
# the comparison at the end of this suite deciding something other than the criterion. The pid
# is written first thing, and the launcher's child runs this only after `setsid` has made it a
# session leader, so its pid file appearing is the proof that it has left the harness's group —
# the moment the TERM may go out. The wait for GO is capped, so a child nobody releases does
# not outlive the suite. A file run by `bash` rather than a `bash -c` string, so nothing in it
# has to survive being quoted into the harness below.
LEAF="$work/leaf.sh"
cat > "$LEAF" <<L
printf '%s\\n' "\$\$" > "\$2"
n=0
while [ ! -e "$GO" ] && [ "\$n" -lt $(( PATIENCE * 50 )) ]; do sleep 0.02; n=\$((n + 1)); done
printf '0\\n' > "\$1"
L

# The harness: the shell whose process group is about to be signalled. It launches the two
# children — the `nohup` control first, so the launcher's child is never the older of the
# two — writes a marker saying both launches have returned, and then sleeps, so the group is
# unambiguously alive when the TERM arrives. Failing to run the launcher at all (it does not exist yet, or exits non-zero)
# still reaches the marker: this shell declares no `set -e`, so the case reports a missing
# completion file rather than hanging on a marker that never lands.
harness="$work/harness.sh"
cat > "$harness" <<H
#!/usr/bin/env bash
set -uo pipefail
nohup bash "$LEAF" "$CONTROL_EXIT" "$CONTROL_PID" > /dev/null 2>&1 &
"$DETACH" bash "$LEAF" "$DETACHED_EXIT" "$DETACHED_PID" > /dev/null 2>&1
printf '%s\n' launched > "$LAUNCHED_MARKER"
sleep 60
H
chmod +x "$harness"

# pgid_of <pid> — the process group id <pid> belongs to, or empty if it has none (it exited,
# or `ps` does not know it). `ps -o pgid=` prints that one column with no header, right-padded,
# which is what the `tr` strips. Three questions in this suite are that same one: which group
# is the suite in, which group did the harness get, and which group is named in the failure
# message a reader has to be able to compare against the other two.
pgid_of() { ps -o pgid= -p "$1" | tr -d ' '; }

# reported <file> <if-nothing> — what one of the five report-back files above has to say, or
# <if-nothing> when it holds nothing. Every failure message in this suite quotes one of them,
# and each was asking for it as a bare `cat … 2>/dev/null` whose own fallback only covers the
# file being absent: an empty one makes `cat` succeed, print nothing, and the `|| echo none`
# never fire, so the message would read `…as ` and leave the reader guessing which it was.
reported() { [[ -s "$1" ]] && cat "$1" || printf '%s\n' "$2"; }

# appeared <file> <seconds> — true once <file> holds something, polled fifty times a second up
# to a budget. The harness has to say its launches returned and the children their pids before
# the signal goes out, and the launcher's child has to have written once released. A passing
# run returns on the first look that finds the file; the budget is only how long a failing one
# takes to say so.
appeared() {
  local looks=0 cap=$(( $2 * 50 ))
  while [[ "$looks" -lt "$cap" ]]; do
    [[ -s "$1" ]] && return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  [[ -s "$1" ]]
}

# gone <pid> <seconds> — true once <pid> is no longer a running process, polled the same way.
# A killed child is not gone the instant the signal is sent, and its parent may not have
# reaped it yet, so the answer is waited for rather than read once.
gone() {
  local looks=0 cap=$(( $2 * 50 ))
  while [[ "$looks" -lt "$cap" ]]; do
    kill -0 "$1" 2>/dev/null || return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  ! kill -0 "$1" 2>/dev/null
}

# probe_term_hit_the_launching_shells_group — stand the harness up in its own process group,
# wait for it to say both children are launched, and TERM that group.
#
# `set -m` turns on job control, which is what puts a background job in a process group of
# its own (pgid == pid); without it the harness would share this suite's group and the kill
# would take the suite down with it. That is asserted rather than assumed before anything is
# signalled — a `ps` that answered with nothing, or with this suite's own group, means the
# isolation did not happen and the right move is to refuse to send the signal at all.
#
# The whole sequence runs in a subshell with stderr discarded so job control's asynchronous
# `Terminated: 15` notice does not land in the middle of the suite's output; what the parent
# needs back therefore travels in files rather than in variables.
probe_term_hit_the_launching_shells_group() {
  local suite_pgid
  suite_pgid="$(pgid_of $$)"
  (
    set -m
    "$harness" &
    hpid=$!
    set +m

    appeared "$LAUNCHED_MARKER" "$PATIENCE" || printf 'never-launched\n' > "$WHY_NO_TERM"
    # The child is detached by the launcher and not by this suite, so there is a moment after
    # the launch returns in which it has not finished moving itself out of this group, and a
    # signal inside that moment would be timing the launcher's startup rather than asking the
    # criterion. The child's pid file ends that moment: it writes it only once it is running
    # in its own session. Which children are alive is recorded as the signal goes out.
    appeared "$DETACHED_PID" "$PATIENCE" && appeared "$CONTROL_PID" "$PATIENCE" ||
      printf 'children-never-started\n' > "$WHY_NO_TERM"
    for child in "$DETACHED_PID" "$CONTROL_PID"; do
      kill -0 "$(cat "$child" 2>/dev/null)" 2>/dev/null && basename "$child" >> "$ALIVE_AT_TERM"
    done

    pg="$(pgid_of "$hpid")"
    printf '%s\n' "${pg:-none}" > "$HARNESS_PGID"
    if [[ ! "$pg" =~ ^[0-9]+$ ]]; then
      printf 'no-pgid\n' > "$WHY_NO_TERM"
    elif [[ "$pg" == "$suite_pgid" ]]; then
      printf 'shares-this-suites-group\n' > "$WHY_NO_TERM"
    elif [[ -s "$WHY_NO_TERM" ]]; then
      : # the launches never reported in; nothing to signal
    else
      kill -TERM -"$pg" && printf 'sent\n' > "$TERM_SENT"
    fi
    # When no signal went out the harness is still sitting in its `sleep 60`, and waiting on
    # it would make a failing run cost a minute. It is ended instead — its whole group when
    # that group is its own, only the harness itself when it is not, since the suite's own
    # group must never be signalled.
    if [[ ! -s "$TERM_SENT" ]]; then
      if [[ "$pg" =~ ^[0-9]+$ && "$pg" != "$suite_pgid" ]]; then kill -KILL -"$pg"; else kill -KILL "$hpid"; fi
    fi
    wait "$hpid"
  ) > /dev/null 2>&1

  [[ -s "$TERM_SENT" ]] ||
    problems+=("no TERM was sent to the launching shell's process group, so nothing below was asked: $(reported "$WHY_NO_TERM" unknown) (its pgid read back as $(reported "$HARNESS_PGID" none), this suite's is $(pgid_of $$))")
}

# probe_the_signal_landed_on_a_running_child — the other premise, and the one that cost an
# hour to find. A launcher that runs its argv in the FOREGROUND — `exec python3 -c '…
# os.setsid(); os.execvp(…)'`, the shim the issue quotes, without backgrounding it — detaches
# the child perfectly well and still fails this issue: the harness blocks until the child has
# finished. Here the child is waiting for a GO that only comes after the TERM, so the harness
# never reports its launches returned and no signal is sent: probe_term reports it as
# `never-launched`. What this probe adds is the positive half: both children were running, by
# pid, at the moment the signal went out, so neither completion file can predate it.
probe_the_signal_landed_on_a_running_child() {
  local alive
  alive="$(sort "$ALIVE_AT_TERM" 2>/dev/null | tr '\n' ' ')"
  [[ "$alive" == "control.pid detached.pid " ]] ||
    problems+=("want both children running when the TERM was sent, got: ${alive:-neither}; a launcher that runs the leaf in the foreground never hands control back, so the harness never reports its launches returned ($(reported "$WHY_NO_TERM" none))")
}

# probe_detached_child_wrote_its_completion_file — the criterion. The control child is waited
# out of existence first, then GO is created, so a control that survived could write too and
# the probe after this one would see it. The launcher's child either survived and writes as
# soon as it sees GO, or it was killed and no wait produces the file.
probe_detached_child_wrote_its_completion_file() {
  gone "$(cat "$CONTROL_PID" 2>/dev/null)" "$PATIENCE"
  : > "$GO"
  appeared "$DETACHED_EXIT" "$PATIENCE" ||
    problems+=("the child launched through detach-leaf.sh wrote no completion file after the TERM; $DETACHED_EXIT is $( [[ -e "$DETACHED_EXIT" ]] && echo empty || echo absent )")
  [[ "$(reported "$DETACHED_EXIT" none)" == 0 ]] ||
    problems+=("its completion file does not hold the status the child wrote; want 0, got: $(printf '%q' "$(reported "$DETACHED_EXIT" none)")")
}

# probe_the_term_was_fatal_in_that_group — the premise. The control child was launched the
# way SKILL.md launched every leaf before this change, into the same group, and it must be
# gone: a TERM that killed nothing would leave the probe above green while proving nothing.
# It is asked after that probe, so GO has been out as long as the launcher's child needed to
# write: a control that had survived would have written by then too. Its pid is asked as well,
# which answers without waiting at all.
probe_the_term_was_fatal_in_that_group() {
  local cpid
  cpid="$(cat "$CONTROL_PID" 2>/dev/null)"
  [[ "$cpid" =~ ^[0-9]+$ ]] && ! kill -0 "$cpid" 2>/dev/null ||
    problems+=("the nohup-launched control child is still running after the TERM (pid ${cpid:-unknown}), so the signal says nothing about detaching")
  [[ ! -s "$CONTROL_EXIT" ]] ||
    problems+=("the nohup-launched control child survived the TERM too, so the signal says nothing about detaching: $CONTROL_EXIT holds $(printf '%q' "$(reported "$CONTROL_EXIT" none)")")
}

# 1. The whole of this step's criterion, as one case: a process started through the launcher
#    keeps running, and writes its completion file, after a TERM is sent to the process group
#    of the shell that launched it. Four probes — the signal was sent, it landed while both
#    children were still running, the launcher's child outlived it and wrote, the same signal
#    killed the `nohup` shape it replaces — each arguing for itself above.
name="a child launched through detach-leaf.sh writes its completion file after a TERM to the launching shell's process group, where a nohup-launched child in that group does not"
problems=()

probe_term_hit_the_launching_shells_group
probe_the_signal_landed_on_a_running_child
probe_detached_child_wrote_its_completion_file
probe_the_term_was_fatal_in_that_group

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
