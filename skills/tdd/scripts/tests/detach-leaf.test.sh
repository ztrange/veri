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
# this case green over a signal that was never delivered. Both children sleep before writing,
# so both are still alive when the signal lands — and the launch is timed, because a launcher
# that runs the leaf in the FOREGROUND makes the harness wait out that sleep and the signal
# then reaches two children that are already gone, which reads as a pass on both counts.
#
# Run: scripts/tests/detach-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DETACH="$HERE/../detach-leaf.sh"

# Seconds each child sleeps before writing its completion file. It has to outlast the gap
# between the launch and the TERM — a child that had already finished would leave a file
# behind whatever the signal did, and the case would pass without detaching anything.
LINGER=3

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
LAUNCH_SECONDS="$work/launch.seconds"  # harness: how long the launcher took to hand control back
HARNESS_PGID="$work/harness.pgid"      # subshell: the process group the harness landed in
TERM_SENT="$work/term.sent"            # subshell: the signal went out
WHY_NO_TERM="$work/why-no-term"        # subshell: …or it did not, and this is what stopped it

# leaf_body <exit-file> — what both children run: sleep past the moment the TERM lands, then
# write a status into <exit-file>. One string rather than two, because the two children have to
# differ in nothing but how they were launched: a sleep or a status that drifted between them
# would leave the comparison at the end of this suite deciding something other than the
# criterion. `printf '%s\n' "…"` rather than `echo`, so the `\n` the child is to print reaches
# the harness file as two characters instead of being interpreted here.
leaf_body() { printf '%s\n' "sleep $LINGER; printf '0\\n' > $1"; }

# The harness: the shell whose process group is about to be signalled. It launches the two
# children — the `nohup` control first, so the launcher's child is never the older of the
# two — records how long the launcher took to hand control back, writes a marker saying both
# launches have returned, and then sleeps, so the group is unambiguously alive when the TERM
# arrives. Failing to run the launcher at all (it does not exist yet, or exits non-zero)
# still reaches the marker: this shell declares no `set -e`, so the case reports a missing
# completion file rather than hanging on a marker that never lands.
#
# `$SECONDS` — bash's count of seconds since this shell started — is what times the launch.
# bash 3.2 has no `$EPOCHSECONDS`, and this needs no wall clock: the harness starts at the
# launch, so its own age when the launcher returns is the launch's duration.
harness="$work/harness.sh"
cat > "$harness" <<H
#!/usr/bin/env bash
set -uo pipefail
nohup bash -c "$(leaf_body "$CONTROL_EXIT")" > /dev/null 2>&1 &
"$DETACH" bash -c "$(leaf_body "$DETACHED_EXIT")" > /dev/null 2>&1
printf '%s\n' "\$SECONDS" > "$LAUNCH_SECONDS"
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

# appeared <file> <seconds> — true once <file> holds something, polled ten times a second up
# to a budget. Every wait in this suite is that one question: the harness has to say both
# children are launched before the signal goes out, the launcher's child has to have written
# within the budget, and the control child has to still have written nothing once one has
# passed — the last of those reading the answer the other way round, as `! appeared`.
appeared() {
  local looks=0 cap=$(( $2 * 10 ))
  while [[ "$looks" -lt "$cap" ]]; do
    [[ -s "$1" ]] && return 0
    looks=$((looks + 1))
    sleep 0.1
  done
  [[ -s "$1" ]]
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

    appeared "$LAUNCHED_MARKER" 30 || printf 'never-launched\n' > "$WHY_NO_TERM"
    # Half a second between the launcher handing control back and the signal. The child is
    # detached by the launcher and not by this suite, so there is a moment after the launch
    # returns in which it has not finished moving itself out of this group; signalling inside
    # that moment would be timing the launcher's startup rather than asking the criterion.
    # It costs nothing against the child's own $LINGER-second sleep, which is what keeps the
    # signal landing on a process that is still running.
    sleep 0.5

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
    wait "$hpid"
  ) > /dev/null 2>&1

  [[ -s "$TERM_SENT" ]] ||
    problems+=("no TERM was sent to the launching shell's process group, so nothing below was asked: $(cat "$WHY_NO_TERM" 2>/dev/null || echo unknown) (its pgid read back as $(cat "$HARNESS_PGID" 2>/dev/null || echo none), this suite's is $(pgid_of $$))")
}

# probe_the_signal_landed_on_a_running_child — the other premise, and the one that cost an
# hour to find. A launcher that runs its argv in the FOREGROUND — `exec python3 -c '…
# os.setsid(); os.execvp(…)'`, the shim the issue quotes, without backgrounding it — detaches
# the child perfectly well and still fails this issue: the harness blocks until the child has
# finished, so the marker lands late, the TERM is sent to a group whose children are already
# gone, and BOTH completion files are there. The criterion below would read that as a pass
# and the control probe as a survival, neither of which happened. So the launch is timed, and
# a launcher that did not hand control back well inside the child's own sleep is reported as
# what it is rather than as one of the two.
probe_the_signal_landed_on_a_running_child() {
  local elapsed
  elapsed="$(cat "$LAUNCH_SECONDS" 2>/dev/null)"
  [[ "$elapsed" =~ ^[0-9]+$ ]] ||
    { problems+=("the harness never recorded how long the launch took, so nothing says the TERM reached a live child"); return; }
  [[ "$elapsed" -lt "$LINGER" ]] ||
    problems+=("detach-leaf.sh took ${elapsed}s to return, which is the child's whole ${LINGER}s sleep: it ran the leaf in the foreground instead of detaching and returning, so the TERM below was sent after both children had already finished")
}

# probe_detached_child_wrote_its_completion_file — the criterion. The budget is generous
# against the child's own sleep because what is being timed is a machine under load, not the
# behaviour: either the child survived and writes at $LINGER seconds, or it was killed and no
# budget produces the file.
probe_detached_child_wrote_its_completion_file() {
  appeared "$DETACHED_EXIT" 12 ||
    problems+=("the child launched through detach-leaf.sh wrote no completion file after the TERM; $DETACHED_EXIT is $( [[ -e "$DETACHED_EXIT" ]] && echo empty || echo absent )")
  [[ "$(cat "$DETACHED_EXIT" 2>/dev/null)" == 0 ]] ||
    problems+=("its completion file does not hold the status the child wrote; want 0, got: $(printf '%q' "$(cat "$DETACHED_EXIT" 2>/dev/null)")")
}

# probe_the_term_was_fatal_in_that_group — the premise. The control child was launched the
# way SKILL.md launched every leaf before this change, into the same group, and it must be
# gone: a TERM that killed nothing would leave the probe above green while proving nothing.
# It is asked after that probe rather than before so the two share one wait — by the time the
# launcher's child has written, the control's own sleep is long spent — with a further
# $LINGER seconds of grace on top, so "still nothing" is a fact and not an early look.
probe_the_term_was_fatal_in_that_group() {
  ! appeared "$CONTROL_EXIT" "$LINGER" ||
    problems+=("the nohup-launched control child survived the TERM too, so the signal says nothing about detaching: $CONTROL_EXIT holds $(printf '%q' "$(cat "$CONTROL_EXIT" 2>/dev/null)")")
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
