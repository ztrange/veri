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

PATIENCE=3

pass=0 fail=0

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

DETACHED_EXIT="$work/.tdd/detached-leaf.exit"
CONTROL_EXIT="$work/.tdd/control-leaf.exit"

LAUNCHED_MARKER="$work/launched"       # harness: both launches have returned
DETACHED_PID="$work/detached.pid"      # child: the launcher's child is running, in its session
CONTROL_PID="$work/control.pid"        # child: the nohup control is running
GO="$work/go"                          # suite: the TERM has been sent; the children may write
ALIVE_AT_TERM="$work/alive-at-term"    # subshell: which children were running when it was sent
HARNESS_PGID="$work/harness.pgid"      # subshell: the process group the harness landed in
TERM_SENT="$work/term.sent"            # subshell: the signal went out
WHY_NO_TERM="$work/why-no-term"        # subshell: …or it did not, and this is what stopped it

LEAF="$work/leaf.sh"
cat > "$LEAF" <<L
printf '%s\\n' "\$\$" > "\$2"
n=0
while [ ! -e "$GO" ] && [ "\$n" -lt $(( PATIENCE * 50 )) ]; do sleep 0.02; n=\$((n + 1)); done
printf '0\\n' > "\$1"
L

harness="$work/harness.sh"
cat > "$harness" <<H
#!/usr/bin/env bash
set -uo pipefail
nohup sh "$LEAF" "$CONTROL_EXIT" "$CONTROL_PID" > /dev/null 2>&1 &
"$DETACH" sh "$LEAF" "$DETACHED_EXIT" "$DETACHED_PID" > /dev/null 2>&1
printf '%s\n' launched > "$LAUNCHED_MARKER"
sleep 60
H
chmod +x "$harness"

pgid_of() { ps -o pgid= -p "$1" | tr -d ' '; }

reported() { [[ -s "$1" ]] && cat "$1" || printf '%s\n' "$2"; }

appeared() {
  local looks=0 cap=$(( $2 * 50 ))
  while [[ "$looks" -lt "$cap" ]]; do
    [[ -s "$1" ]] && return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  [[ -s "$1" ]]
}

gone() {
  local looks=0 cap=$(( $2 * 50 ))
  while [[ "$looks" -lt "$cap" ]]; do
    kill -0 "$1" 2>/dev/null || return 0
    looks=$((looks + 1))
    sleep 0.02
  done
  ! kill -0 "$1" 2>/dev/null
}

probe_term_hit_the_launching_shells_group() {
  local suite_pgid
  suite_pgid="$(pgid_of $$)"
  (
    set -m
    "$harness" &
    hpid=$!
    set +m

    appeared "$LAUNCHED_MARKER" "$PATIENCE" || printf 'never-launched\n' > "$WHY_NO_TERM"
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
    if [[ ! -s "$TERM_SENT" ]]; then
      if [[ "$pg" =~ ^[0-9]+$ && "$pg" != "$suite_pgid" ]]; then kill -KILL -"$pg"; else kill -KILL "$hpid"; fi
    fi
    wait "$hpid"
  ) > /dev/null 2>&1

  [[ -s "$TERM_SENT" ]] ||
    problems+=("no TERM was sent to the launching shell's process group, so nothing below was asked: $(reported "$WHY_NO_TERM" unknown) (its pgid read back as $(reported "$HARNESS_PGID" none), this suite's is $(pgid_of $$))")
}

probe_the_signal_landed_on_a_running_child() {
  local alive
  alive="$(sort "$ALIVE_AT_TERM" 2>/dev/null | tr '\n' ' ')"
  [[ "$alive" == "control.pid detached.pid " ]] ||
    problems+=("want both children running when the TERM was sent, got: ${alive:-neither}; a launcher that runs the leaf in the foreground never hands control back, so the harness never reports its launches returned ($(reported "$WHY_NO_TERM" none))")
}

probe_detached_child_wrote_its_completion_file() {
  gone "$(cat "$CONTROL_PID" 2>/dev/null)" "$PATIENCE"
  : > "$GO"
  appeared "$DETACHED_EXIT" "$PATIENCE" ||
    problems+=("the child launched through detach-leaf.sh wrote no completion file after the TERM; $DETACHED_EXIT is $( [[ -e "$DETACHED_EXIT" ]] && echo empty || echo absent )")
  [[ "$(reported "$DETACHED_EXIT" none)" == 0 ]] ||
    problems+=("its completion file does not hold the status the child wrote; want 0, got: $(printf '%q' "$(reported "$DETACHED_EXIT" none)")")
}

probe_the_term_was_fatal_in_that_group() {
  local cpid
  cpid="$(cat "$CONTROL_PID" 2>/dev/null)"
  [[ "$cpid" =~ ^[0-9]+$ ]] && ! kill -0 "$cpid" 2>/dev/null ||
    problems+=("the nohup-launched control child is still running after the TERM (pid ${cpid:-unknown}), so the signal says nothing about detaching")
  [[ ! -s "$CONTROL_EXIT" ]] ||
    problems+=("the nohup-launched control child survived the TERM too, so the signal says nothing about detaching: $CONTROL_EXIT holds $(printf '%q' "$(reported "$CONTROL_EXIT" none)")")
}

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
