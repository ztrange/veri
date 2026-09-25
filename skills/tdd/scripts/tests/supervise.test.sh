#!/usr/bin/env bash
# Tests for scripts/supervise.sh — the programmatic supervisor, the deterministic
# robustness core (#4). Every leaf is launched through it; it tells a slow-but-alive leaf
# (heartbeat: progress-log activity within a window) from a hung one (silent past the
# window), caps the wall clock with a hard timeout, kills a stuck leaf, and reports a
# clear status (success / failure / killed-stuck) plus the captured output.
#
# Driven against STUB LEAF SCRIPTS (no claude): exit-0, exit-nonzero, hang, slow-but-alive,
# runaway (alive but over the hard timeout), and flaky (hangs once, then succeeds).
# No case waits for real time to pass: the clock is injected (see "The injected clock" below),
# so a hang is seen on the next poll and a lifetime longer than a window costs milliseconds.
#
# Status contract: exit 0 success · 1 leaf-failure · 2 killed-stuck.
#
# Run: scripts/tests/supervise.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The skill's script directory, named because cases 19 and 20 are about it and not about
# `supervise.sh` alone: one asks git what commit it is at, the other copies it whole out of
# any clone. Every script the supervisor reaches for lives in it.
SCRIPTS="$HERE/.."
SUP="$SCRIPTS/supervise.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

stub="$(mktemp -d)"
work="$(mktemp -d)"
# Both temp dirs are removed here, on the one path that runs however the script ends —
# including the Ctrl-C or the `make test` timeout that an `rm` at the foot of a case never
# reaches. Cases 12 to 16 each need a run directory of their own (case 12's reason: the event
# log accumulates across a run), and each takes a NAMED SUBDIRECTORY of `$work` rather than a
# `mktemp -d` of its own — the shape harvest-usage.test.sh uses for its two. So this line does
# not grow a name per case, and the next case that reads the event log is cleaned up by
# existing rather than by remembering to add a sixth `${…:-}` here.
trap 'rm -rf "$stub" "$work"' EXIT

# exit-0: writes progress, finishes cleanly.
cat > "$stub/leaf-ok" <<'L'
#!/bin/sh
echo "leaf: starting"; echo "leaf: did the work"; exit 0
L
# exit-nonzero: writes progress, fails.
cat > "$stub/leaf-fail" <<'L'
#!/bin/sh
echo "leaf: starting"; echo "leaf: blew up"; exit 3
L
# hang: one line of progress, then silent forever (no heartbeat).
cat > "$stub/leaf-hang" <<'L'
#!/bin/sh
echo "leaf: starting"; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
# slow-but-alive: six ticks, each followed by a second of injected silence, so the leaf lives
# six seconds on the supervisor's clock — three windows of case 4's two — and is never silent
# for more than one. It waits for the supervisor to read the clock after every tick, so every
# tick is watched rather than raced past.
cat > "$stub/leaf-slow" <<'L'
#!/bin/sh
: > .test-clock-reads
for i in 1 2 3 4 5 6; do echo "leaf: tick $i"; clock-jump 1; await-poll; done
echo "leaf: done"; exit 0
L
# runaway: stays alive AND keeps emitting (heartbeat fresh) but never exits — only the
# hard timeout can stop it. Each line lands a second later on the injected clock.
cat > "$stub/leaf-runaway" <<'L'
#!/bin/sh
: > .test-clock-reads
while true; do echo "leaf: busy"; clock-jump 1; await-poll; done
L
# flaky: hangs (silent) the FIRST time it runs, succeeds the SECOND — the one leaf here that
# gets past its first attempt, which is what case 13 needs to watch a relaunch. The marker
# lives in cwd, which the supervisor preserves across attempts, so a run in a directory some
# earlier run already flaked in would succeed straight away and never be relaunched: case 13
# gives it a directory of its own for that reason as much as for the event log's.
cat > "$stub/leaf-flaky" <<'L'
#!/bin/sh
if [ -e .retry-marker ]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

# The injected clock. supervise.sh reads time two ways, and both go through PATH: `date +%s`
# for now, and `stat` for when the leaf last wrote to its log (the heartbeat). No case here
# waits for either to move; a stub leaf moves them, with three helpers that work in the leaf's
# cwd, which is the supervisor's:
#   clock-jump <s>  <s> seconds pass. Appended to ./.test-clock as `<real time> <offset>`, so the
#                   file is the clock's whole history: now is the real time plus the latest
#                   offset. A hanging leaf writes a line and then jumps just past its window
#                   (VERI_HEARTBEAT + 1, or 1000 when the default is in force), which is a
#                   silence the next poll sees and still short of every hard timeout here.
#   await-poll      returns once the supervisor has read the clock again, when the leaf has
#                   asked to be counted by creating ./.test-clock-reads.
# The two stubs below answer from that history. `date +%s` adds the latest offset. `stat`, for
# the two spellings supervise.sh uses, adds the offset that was in force when the file was
# last written — so a write made after a jump is "now", and silence is only ever the time
# jumped while nothing was written. A relaunched attempt's fresh log is therefore not silent,
# which an offset applied to `date` alone would make it. Every other `date` and `stat` call is
# the real one; the real paths are baked in because each stub sits on PATH under the name it
# would otherwise re-exec into forever.
realdate="$(command -v date)"
realstat="$(command -v stat)"
cat > "$stub/date" <<D
#!/bin/sh
if [ "\$*" = "+%s" ]; then
  [ -e .test-clock-reads ] && echo r >> .test-clock-reads
  offset="\$(tail -n 1 .test-clock 2>/dev/null | cut -d' ' -f2)"
  printf '%s\n' "\$(( \$("$realdate" +%s) + \${offset:-0} ))"
else
  exec "$realdate" "\$@"
fi
D
cat > "$stub/stat" <<D
#!/bin/sh
if [ "\$#" -eq 3 ]; then
  if [ "\$1 \$2" = "-c %Y" ] || [ "\$1 \$2" = "-f %m" ]; then
    exec python3 -c '
import os, sys
try:
    m = os.stat(sys.argv[1]).st_mtime
except OSError:
    sys.exit(1)
offset = 0
try:
    for line in open(".test-clock"):
        at, value = line.split()
        if float(at) <= m:
            offset = int(value)
except OSError:
    pass
print(int(m) + offset)' "\$3"
  fi
fi
exec "$realstat" "\$@"
D
cat > "$stub/clock-jump" <<'C'
#!/bin/sh
exec python3 -c '
import sys, time
offset = 0
try:
    offset = int(open(".test-clock").read().split()[-1])
except (OSError, IndexError):
    pass
with open(".test-clock", "a") as f:
    f.write("%r %d\n" % (time.time(), offset + int(sys.argv[1])))' "$1"
C
cat > "$stub/await-poll" <<'C'
#!/bin/sh
n="$(wc -l < .test-clock-reads)"
for _ in $(seq 1 500); do [ "$(wc -l < .test-clock-reads)" -gt "$n" ] && exit 0; sleep 0.01; done
exit 1
C
# The awake clock (issue #472): whole seconds the machine spent awake, which the supervisor
# reads from the executable VERI_AWAKE_CLOCK names. A `clock-jump` is awake time, so this stub
# answers real time plus every jump, minus every second `clock-suspend` (case 43) put in
# ./.test-suspended. Named for every case below, so a jump is silence and not a suspend; the
# case that asks for the supervisor's own real clock unsets it.
cat > "$stub/awake-clock" <<'C'
#!/bin/sh
exec python3 -c '
import time
offset = suspended = 0
try:
    offset = int(open(".test-clock").read().split()[-1])
except (OSError, IndexError):
    pass
try:
    suspended = sum(int(x) for x in open(".test-suspended").read().split())
except OSError:
    pass
print(int(time.time()) + offset - suspended)'
C
chmod +x "$stub/date" "$stub/stat" "$stub/clock-jump" "$stub/await-poll" "$stub/awake-clock"

# On PATH for everything this suite starts, so the supervisor reads the injected clock and a
# stub leaf can call the helpers by name.
export PATH="$stub:$PATH"
export VERI_AWAKE_CLOCK="$stub/awake-clock"

# sup <name> <heartbeat> <timeout> <leaf> -> sets $out / $code (runs in $work)
# VERI_STUCK_RETRIES=0 is pinned, not inherited: every case here is about a single attempt,
# so the caller's environment must not be able to add retries (extra killed-stuck attempts
# would change both the stderr transcript and the suite's wall time). VERI_KILL_POLL=0.01 is
# pinned the same way, in every helper below that can reach a killed-stuck leaf: kill_tree's
# grace loop polls a real OS fact (is the process gone yet), not the injected clock, so it is
# real sleep regardless — up to 5 x 0.1s production default, unpinned, on each of this
# suite's ~18 killed-stuck cases.
sup() {
  local name="$1" hb="$2" to="$3" leaf="$4"
  rm -f "$work/.test-clock" "$work/.test-clock-reads"
  out="$( cd "$work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT="$hb" VERI_TIMEOUT="$to" VERI_POLL=0.02 \
            VERI_KILL_POLL=0.01 "$SUP" "$name" "$stub/$leaf" 2>"$work/err" )"
  code=$?
}

# 1. a clean leaf → success (exit 0), and its output is captured/returned
sup ok 5 10 leaf-ok
{ [[ "$code" == 0 ]] && [[ "$out" == *'did the work'* ]]; } && ok \
  || no "exit-0 leaf → success + captured output (code=$code)"

# 2. a failing leaf → failure (exit 1), output still captured
sup fail 5 10 leaf-fail
{ [[ "$code" == 1 ]] && [[ "$out" == *'blew up'* ]]; } && ok \
  || no "exit-nonzero leaf → failure + output (code=$code)"

# 3. a hung (silent) leaf is detected via heartbeat and killed → killed-stuck (exit 2)
sup hang 1 30 leaf-hang
{ [[ "$code" == 2 ]] && grep -qi 'heartbeat\|stuck\|silent' "$work/err"; } && ok \
  || no "hung leaf → killed-stuck via heartbeat (code=$code, err=$(cat "$work/err"))"

# 4. a slow-but-alive leaf keeps its heartbeat and is allowed to finish → success. It lives
#    six seconds on the injected clock against a two-second window, never silent for more
#    than one, so it survives only if activity resets the heartbeat. Before the clock was
#    injected the leaf finished inside its window in real time, and a supervisor measuring
#    silence from launch rather than from the last write passed this case too.
sup slow 2 30 leaf-slow
{ [[ "$code" == 0 ]] && [[ "$out" == *'done'* ]]; } && ok \
  || no "slow-but-alive leaf survives heartbeat → success (code=$code)"

# 5. a leaf that exceeds the hard timeout is killed even while emitting → killed-stuck
sup runaway 30 1 leaf-runaway
{ [[ "$code" == 2 ]] && grep -qi 'timeout\|stuck' "$work/err"; } && ok \
  || no "runaway leaf → killed-stuck via hard timeout (code=$code, err=$(cat "$work/err"))"

# 6. the supervisor reports a clear status line on stderr (observability)
sup ok 5 10 leaf-ok
grep -qiE 'success|ok' "$work/err" && ok || no "emits a status line (err=$(cat "$work/err"))"

# 7. a killed leaf does not leave the stub's child (sleep) running (clean kill)
sup hang 1 30 leaf-hang
if pgrep -f "$stub/leaf-hang" >/dev/null 2>&1; then no "killed leaf left a process behind"; else ok; fi

# 8. how many attempts a hung leaf gets is fixed by this suite, not by the shell that ran
#    `make test`: with VERI_STUCK_RETRIES=3 ambient in the environment, sup() must still run
#    the leaf exactly once — one killed-stuck status line on stderr and no `retry N/M` line.
#    The assignment prefix puts the variable in sup()'s environment for this call only, so
#    no later case sees it.
VERI_STUCK_RETRIES=3 sup hang 1 30 leaf-hang
stuck_lines="$(grep -c 'supervise\[hang\]: killed-stuck' "$work/err")"
retry_lines="$(grep -c 'retry [0-9][0-9]*/[0-9][0-9]*' "$work/err")"
{ [[ "$code" == 2 ]] && [[ "$stuck_lines" -eq 1 ]] && [[ "$retry_lines" -eq 0 ]]; } && ok \
  || no "ambient VERI_STUCK_RETRIES=3 → hung leaf still runs exactly once (code=$code, killed-stuck lines=$stuck_lines, retry lines=$retry_lines)"

# 9. the supervisor records its OWN final code in a completion file at .tdd/<name>.exit, so
#    a leaf launched detached can be waited on by polling that file instead of by reading
#    this process's stdout. Three arms, one per status in the contract: success writes 0; a
#    leaf exiting 3 writes the supervisor's 1, not the leaf's raw 3 (that raw code is what
#    .tdd/<name>.rc carries); and a killed-stuck leaf — which never writes an rc file at
#    all — still writes 2, so the waiter learns the answer instead of waiting out its
#    budget. Fresh names, so no earlier case's file can stand in for a missing one.
#
# recorded_code <name> <heartbeat> <timeout> <leaf> — run one leaf through sup() and echo
# what landed in .tdd/<name>.exit, or '<missing>' if nothing did. The name is written once
# per arm, so the run and the file read cannot drift onto different leaves: naming them
# separately, a typo would read some earlier case's file and pass on it.
recorded_code() { sup "$@"; cat "$work/.tdd/$1.exit" 2>/dev/null || echo '<missing>'; }
eok="$(recorded_code    exit-ok    5 10 leaf-ok)"
efail="$(recorded_code  exit-fail  5 10 leaf-fail)"
estuck="$(recorded_code exit-stuck 1 30 leaf-hang)"
{ [[ "$eok" == 0 ]] && [[ "$efail" == 1 ]] && [[ "$estuck" == 2 ]]; } && ok \
  || no ".tdd/<name>.exit records the supervisor's own final code, killed-stuck included (success=$eok want 0, failure=$efail want 1, killed-stuck=$estuck want 2)"

# 10. the default supervise.sh encodes and the prose that states it must not drift apart.
#     `VERI_HEARTBEAT`'s default is a number written down three times in this lane: once as
#     code (`heartbeat="${VERI_HEARTBEAT:-N}"`) and twice as prose — the script's own
#     `Tunables (env)` header and SKILL.md's launcher entry. Changing the constant alone
#     leaves both sentences confidently stating the old figure, and nothing else in this
#     lane notices.
#
#     The figure is stated twice more in docs/wt/commentary.py, and those two statements are
#     NOT this case's (#143). A suite here that reads that file puts the page's prose on the
#     development lane's critical path: `make test` is what preflight reads its baseline
#     off, what every Green leaf runs and what both blind verifiers run, so rewording a
#     figure would turn a TDD run red over a file no development change touched (ADR 0016).
#     Those two sites moved to docs/tests/commentary-figures.test.sh (#146), which
#     `make docs-test` globs, and no-docs-reads.test.sh is what keeps them from coming back.
#
#     Each site is located by a regex that ends at the figure it asks about, and a site
#     whose pattern can no longer be found reports `<none>` — a rewording that moves a
#     statement out of the check's sight is drift too, and must fail rather than pass
#     silently.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# stated <file> <extended-regex> — the figure the first match of <regex> states, or
# '<none>' / '<no-file>' when there is nothing to read. Newlines are squashed to spaces
# first, because the prose below wraps at ~90 columns and a statement split across two
# lines is still one statement; the figure is the LAST run of digits in the match, which is
# why every regex here stops at it.
stated() {
  local hit
  [[ -f "$1" ]] || { echo '<no-file>'; return; }
  hit="$(head -1 < <(tr '\n' ' ' < "$1" | grep -oE "$2"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

# The code site, read through that same helper: `heartbeat="${VERI_HEARTBEAT:-N}"` states
# the figure as much as the two sentences do, and it is the one the others must match.
encoded="$(stated "$SUP" 'VERI_HEARTBEAT:-[0-9]+')"

prose_misses=""
[[ "$encoded" =~ ^[0-9]+$ ]] || prose_misses=" supervise.sh:no-VERI_HEARTBEAT-default-found"
while IFS='|' read -r where file regex; do
  [[ -n "$where" ]] || continue
  got="$(stated "$ROOT/$file" "$regex")"
  [[ "$got" == "$encoded" ]] || prose_misses="$prose_misses $where:says-$got"
done <<'SITES'
supervise.sh-header|skills/tdd/scripts/supervise.sh|VERI_HEARTBEAT silence window secs \(default [0-9]+
SKILL.md-tunables|skills/tdd/SKILL.md|VERI_HEARTBEAT.{0,3}\(silence window s, +default [0-9]+
SITES

[[ -z "$prose_misses" ]] && ok \
  || no "the heartbeat default encoded in supervise.sh and every prose statement of it agree (encoded=$encoded, drift:$prose_misses)"

# 11. the silence window a leaf actually gets when VERI_HEARTBEAT is unset is 180s, and an
#     explicit VERI_HEARTBEAT still wins over it. Case 10 compares numbers written down in
#     files; this one asks the running supervisor, which answers in the kill line it writes
#     to stderr — `no heartbeat for Ns (window Ms)`, where M is the window in force.
#
#     Waiting out a real 180s silence would cost the suite three minutes, so it is not
#     waited: the hanging leaf jumps the injected clock (near the top of this file) past its
#     window — 1000s when VERI_HEARTBEAT is unset, which clears the 180s default. The hard
#     timeout is set above that jump so it cannot be the kill that answers.
#
#     Both arms hang the same leaf, so the only difference between them is where the window
#     comes from: absent → the script's default, present → the caller's number.
#     `env -u VERI_HEARTBEAT` unsets it for the child rather than trusting the suite's own
#     environment to be clean, the same hermeticity case 8 insists on.

# killed_window <name> <heartbeat|''> — hang a leaf and echo the
# window the supervisor said it killed on, or '<no-heartbeat-kill>' if it died some other
# way (the hard timeout) or not at all. An empty second argument leaves VERI_HEARTBEAT
# unset in the child, which is the whole point of the first arm.
killed_window() {
  local name="$1" hb="${2-}"
  local -a hbenv
  if [[ -n "$hb" ]]; then hbenv=(VERI_HEARTBEAT="$hb"); else hbenv=(-u VERI_HEARTBEAT); fi
  rm -f "$work/.test-clock"
  ( cd "$work" && env "${hbenv[@]}" \
      VERI_STUCK_RETRIES=0 VERI_TIMEOUT=5000 VERI_POLL=0.02 \
      "$SUP" "$name" "$stub/leaf-hang" >/dev/null 2>"$work/err-$name" )
  head -1 < <(grep -oE 'window [0-9]+s' "$work/err-$name") | grep -oE '[0-9]+' \
    || echo '<no-heartbeat-kill>'
}

default_window="$(killed_window hb-default  '')"
explicit_window="$(killed_window hb-explicit 5)"
{ [[ "$default_window" == 180 ]] && [[ "$explicit_window" == 5 ]]; } && ok \
  || no "VERI_HEARTBEAT unset → a 180s window, explicit VERI_HEARTBEAT=5 → a 5s window (unset gave ${default_window}, explicit gave ${explicit_window})"

# 12. every leaf the supervisor launches leaves a `launch` line in the run's event log —
#     `.tdd/events.jsonl`, written through event.sh — naming the leaf, the command it ran and
#     the attempt number (issue #107, ADR-0014). The supervisor is the only place that knows
#     those three: it is the one choke point every leaf goes through (this file's header), so
#     a log missing a launch is a leaf nothing recorded starting.
#
#     The leaf is named `revise-green-2`, not a fresh invented name, because the attempt
#     number the line must carry is the one the NAME carries — leaf-role.sh reads a trailing
#     `-<digits>` as the attempt and everything else as attempt 1 (leaf-role.sh:86-92). A
#     `develop-red` leaf's line would read 1 whether the writer derived it or hardcoded it;
#     under this name only a derived one says 2.
#
#     The command is `env VERI_TIMEOUT=1200 <leaf>` because that is the shape a real launch
#     has — the conductor passes the leaf's timeout in exactly that prefix, and event.sh's own
#     header quotes `cmd=env VERI_TIMEOUT=1200 run-leaf.sh .tdd/develop-red.prompt` as the
#     payload it has to keep intact (event.sh:41). The expected value is that argv joined by
#     spaces, the same spelling.
#
#     A run directory of its own — a subdirectory of `$work`, so the trap at the top of the
#     file covers it already: the event log accumulates across a whole run, and every case
#     above works directly in `$work`, so a probe there would be reading whichever launch some
#     earlier case happened to write last. For the same reason the probe picks the log's
#     `launch` line rather than asserting on the file's only line — the `retry` and `exit`
#     marks land in this same file and must not turn this case red.
#
# event_field <dir> <event> <key> — the value of <key> on the one <event> line of the event
# log a run in <dir> wrote, or a diagnostic in `<<…>>` when there is no such line, more than
# one, or no log at all. python3 rather than jq, the dependency event.test.sh and
# extract-result.sh already rely on.
#
# A run directory rather than a file path, so where the log lands under it — `.tdd/events.jsonl`,
# relative to the leaf's cwd, which is the whole of the issue spec's "in the issue's worktree" —
# is stated once here instead of once per case. Cases 12 and 13 then name only the directory
# they gave the supervisor, and neither can go green against a path the other does not use.
#
# The event is a parameter because cases 12 and 13 ask the same question of `launch` and of
# `retry`, and one probe answering both is one probe to trust: a bug in the counting or in
# the JSON parse cannot now be fixed in the copy one case reads and left standing in the
# other's. Exactly one match is demanded in both, which says two things at once — the log
# holds a line of that kind, and it holds only one, so a `launch` written per attempt or a
# `retry` written per poll would be caught rather than read past.
event_field() {
  python3 -c '
import sys, json
hits = []
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == sys.argv[2]:
        hits.append(obj)
if len(hits) != 1:
    print("<<%d %s lines>>" % (len(hits), sys.argv[2]))
else:
    print(hits[0].get(sys.argv[3], "<<missing>>"))
' "$1/.tdd/events.jsonl" "$2" "$3" 2>/dev/null || echo '<<no event log>>'
}

# sup_run <dir> <argv…> — run one supervision to completion in <dir>, under this suite's
# compressed watchdog knobs, with its output discarded; the caller reads its status from `$?`.
# The knobs are pinned rather than inherited for `sup`'s reason above: a budget of retries in
# the shell that ran `make test` would otherwise change both the wall time and, here, how many
# marks the event log ends up holding. Cases 12, 15 and 16 all want exactly that launch, and
# spelled it out one each; the quartet then had to be kept in step across three copies, and a
# fourth case reading the event log would have made a fourth.
#
# Not `sup` itself, which is every earlier case's helper: that one runs in the shared `$work`,
# and a case that reads the event log needs a directory of its own (case 12's reason). The
# directory is this helper's first argument for the same reason it is `event_field`'s.
#
# <argv…> is the whole command, `"$SUP"` included, rather than a leaf name plus its arguments:
# `env` applies leading `VAR=VALUE` words left to right and stops at the first word that is not
# one, so a caller needing extra context in the child's environment — case 15's VERI_ISSUE and
# VERI_STEP — puts it in front of `"$SUP"` and this helper needs no parameter for it.
#
# The directory is created here rather than by each caller because the callers name one under
# `$work` instead of making one with `mktemp -d`, and a `cd` into a directory that does not
# exist would fail silently into `>/dev/null 2>&1` — leaving the case reading an event log some
# other run wrote.
sup_run() {
  local dir="$1"; shift
  mkdir -p "$dir"
  ( cd "$dir" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 VERI_TIMEOUT=10 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$@" ) >/dev/null 2>&1
}

# Every variable this case owns is prefixed with the event it is about, and case 13's with
# its own — so the two read as the siblings they are, and each says at a glance which of
# `event_field`'s two event arguments its assertions are about.
launch_work="$work/launch"
# The name and the command are each written once, then used both to launch and to expect —
# the shape `$launch_cmd` already had. Spelled a second time in the assertion instead, the
# name could drift from the launched one and the case would go green on a leaf it never ran;
# and the expected attempt below is 2 only because THIS name ends in `-2`.
launch_name=revise-green-2
launch_cmd=(env VERI_TIMEOUT=1200 "$stub/leaf-ok")
sup_run "$launch_work" "$SUP" "$launch_name" "${launch_cmd[@]}"
launch_code=$?
# Each field read once, into a variable the assertion and the failure message share — the
# capture-then-compare shape cases 9 and 11 already use. Read twice, the line a failure
# reports would be a second reading of the log rather than the one that failed.
launch_got_name="$(event_field    "$launch_work" launch name)"
launch_got_cmd="$(event_field     "$launch_work" launch cmd)"
launch_got_attempt="$(event_field "$launch_work" launch attempt)"
{ [[ "$launch_code" == 0 ]] \
  && [[ "$launch_got_name"    == "$launch_name" ]] \
  && [[ "$launch_got_cmd"     == "${launch_cmd[*]}" ]] \
  && [[ "$launch_got_attempt" == 2 ]]; } && ok \
  || no "a launched leaf appends a launch event naming the leaf, its command and the attempt (code=$launch_code, name=$launch_got_name, cmd=$launch_got_cmd, attempt=$launch_got_attempt)"

# heartbeat_kill <cause> <window> — does <cause> read as the watchdog's diagnosis of a
# heartbeat kill on a <window>-second silence window? Cases 13 and 14 both ask it, of the
# `retry` mark's cause and of the `exit` mark's, so the wording is pinned here once: spelled
# out in each, a loosened or mistyped pattern could be fixed in the copy one case reads and
# left standing in the other's — the same reason `event_field` above serves both.
#
# The FIRST number in the supervisor's wording is the elapsed silence, which the poll interval
# makes a race, so this globs over that one and pins the words plus the window the wording
# carries (supervise.sh:125). The pattern is a literal inside the function rather than a string
# the callers expand, so it stays a glob without either caller having to leave a `$var`
# unquoted on the right of `==`.
heartbeat_kill() { [[ "$1" == "no heartbeat for "*" (window ${2}s)" ]]; }

# 13. relaunching a killed-stuck leaf leaves a `retry` line in the same log, carrying the
#     cause the watchdog killed the attempt for (issue #107, ADR-0014: "the supervisor
#     writes every leaf launch, attempt and exit (with the kill cause)"). Nothing else can
#     say it: the cause is the watchdog's own diagnosis, and the one status line the
#     supervisor prints at the end reports the LAST attempt's reason — which on a leaf that
#     recovered is no reason at all, so a recovered run otherwise leaves no record anywhere
#     of why it had to be relaunched. The `launch` mark above cannot cover it either: that
#     one is written once per supervision, outside the retry loop, so a second attempt
#     passes it by (supervise.sh:165-168).
#
#     This is the only case in this file that lets the leaf reach a second attempt, so it
#     is also the only one that does not go through `sup` — the helper pins
#     VERI_STUCK_RETRIES=0 (line 76 above). Here the variable is cleared with `env -u`
#     instead, so the DEFAULT budget of 1 retry is what produces the relaunch and a value
#     exported by the shell that ran `make test` cannot suppress it.
#
#     The expected cause is the heartbeat window's, because that is how this leaf dies:
#     `$retry_window` against a 60s silent sleep, well inside the 30s hard cap. That window
#     is written once and then used both to run the leaf and to expect its cause — case 12's
#     shape, and here it is what makes the assertion legible: the number in `(window Ns)` is
#     the one the supervisor was handed, not a constant that happens to agree with it. The
#     wording itself is `heartbeat_kill`'s to know, above.
#     The log is read through `event_field` above, the probe case 12 also uses; here the
#     one line it demands says as well that a budget of one retry wrote one mark, not one
#     per attempt.

# This case launches the supervisor itself rather than through `sup_run`, so the directory
# `sup_run` would have made is made here.
retry_work="$work/retry"
mkdir -p "$retry_work"
retry_window=1
( cd "$retry_work" && env -u VERI_STUCK_RETRIES VERI_HEARTBEAT="$retry_window" \
    VERI_TIMEOUT=30 VERI_POLL=0.02 VERI_KILL_POLL=0.01 \
    "$SUP" develop-red "$stub/leaf-flaky" ) >/dev/null 2>&1
retry_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11 and
# 12's shape. Read twice, a failure would report a second reading of the log, not the one
# that failed. The exit code is asserted alongside so a case that went green on a leaf which
# never actually recovered would still be caught.
retry_cause="$(event_field "$retry_work" retry cause)"
{ [[ "$retry_code" == 0 ]] \
  && heartbeat_kill "$retry_cause" "$retry_window"; } && ok \
  || no "a relaunched killed-stuck leaf appends one retry event carrying the kill cause (code=$retry_code, cause=$retry_cause)"

# 14. every supervision ends with one `exit` line in the same log, carrying the three things
#     only the supervisor holds at that moment (issue #107, ADR-0014): the 0/1/2 status of
#     the exit-code contract, the cause when the watchdog killed the leaf, and how many wall
#     seconds the attempt took. The status is the supervisor's OWN code — the number case 9
#     watches land in `.tdd/<name>.exit` — not the leaf's raw exit code, so the arms below
#     run the same three leaves case 9 does and expect 0, 1 and 2 in the log for them.
#     The wall seconds are the first duration anything in a run records at all (the issue's
#     "today nothing in a run records when anything began"), so nothing else in the log can
#     be subtracted to recover them.
#
#     Three arms, one per status, each in a directory of its own under one temp dir: the
#     event log accumulates across a run, so two arms sharing a directory would read each
#     other's `exit` line — and `event_field` demands exactly one, which is also what pins
#     this mark as written once per supervision rather than once per poll or per attempt.
#
#     Only the killed-stuck arm asserts a cause, because it is the only arm that has one;
#     what a run with no kill writes in its place the criterion leaves open ("the kill cause
#     when there is one"), so this case does not invent an answer for it. The cause expected
#     is the heartbeat window's, read through `heartbeat_kill` above — case 13's predicate,
#     so neither case can go green on a wording the other would reject.
#
#     The seconds are pinned as a count that exists and is plain digits on a fast leaf, and
#     on the stuck arm as one that has reached the window the leaf was killed on: a silence
#     of more than `$exit_window` seconds has to have elapsed before the kill (supervise.sh:120-127),
#     so a hardcoded 0 or a field carrying something other than elapsed time fails there.

exit_work="$work/exit"
exit_window=2

# exit_run <arm> <heartbeat> <leaf> — supervise one leaf in its own directory under
# $exit_work, named for the arm. The leaf is called `develop-red` in every arm: leaf-role.sh
# has to be able to read the name or nothing is logged at all (supervise.sh:141-154), and
# nothing in this case is about which name it is.
#
# Through `sup_run` above, so the pinned watchdog quartet is written down once for every case
# that reads the event log rather than a fifth time here — this arm-runner was the last copy of
# it left. The one knob this case chooses for itself rides in front of `"$SUP"`, the same
# calling convention case 15 uses for VERI_ISSUE/VERI_STEP: `env` applies leading assignments
# left to right and the last of a repeated name wins, so a `VERI_HEARTBEAT` here overrides the
# helper's. The helper's hard timeout is well clear of every arm — the stuck arm is killed a
# `$exit_window` of seconds in — so that arm dies on the heartbeat and its cause says so.
exit_run() {
  sup_run "$exit_work/$1" VERI_HEARTBEAT="$2" "$SUP" develop-red "$stub/$3"
}

exit_run ok    5              leaf-ok
exit_run fail  5              leaf-fail
exit_run stuck "$exit_window" leaf-hang

# Each field read once, into a variable the assertion and the failure message share — cases
# 9, 11, 12 and 13's shape.
exit_ok_status="$(event_field    "$exit_work/ok"    exit status)"
exit_ok_secs="$(event_field      "$exit_work/ok"    exit secs)"
exit_fail_status="$(event_field  "$exit_work/fail"  exit status)"
exit_stuck_status="$(event_field "$exit_work/stuck" exit status)"
exit_stuck_cause="$(event_field  "$exit_work/stuck" exit cause)"
exit_stuck_secs="$(event_field   "$exit_work/stuck" exit secs)"

# The digit test on `$exit_stuck_secs` comes before the comparison and short-circuits it:
# `(( ))` on a diagnostic like `<<0 exit lines>>` is an arithmetic syntax error, not a false.
{ [[ "$exit_ok_status"    == 0 ]] && [[ "$exit_ok_secs" =~ ^[0-9]+$ ]] \
  && [[ "$exit_fail_status"  == 1 ]] \
  && [[ "$exit_stuck_status" == 2 ]] \
  && heartbeat_kill "$exit_stuck_cause" "$exit_window" \
  && [[ "$exit_stuck_secs" =~ ^[0-9]+$ ]] && (( exit_stuck_secs >= exit_window )); } && ok \
  || no "a supervised leaf appends one exit event carrying the 0/1/2 status, the kill cause and the attempt's wall seconds (success status=$exit_ok_status want 0, secs=$exit_ok_secs; failure status=$exit_fail_status want 1; killed-stuck status=$exit_stuck_status want 2, cause=$exit_stuck_cause, secs=$exit_stuck_secs want >=$exit_window)"

# 15. the two marks the supervisor writes per supervision carry the RUN's context as well as
#     the leaf's: the issue being solved and the step of its plan the leaf is working on
#     (issue #163). leaf-role.sh can derive the actor, phase and attempt from the leaf's name,
#     but nothing in a name says which issue or which step — that context exists only in the
#     environment the conductor launched the leaf in, and the supervisor's job is to pass it
#     through, not to invent it. Without it a reader can attribute a leaf to a step only by
#     interleaving its timestamp with the conductor's own `step-start` marks.
#
#     `VERI_ISSUE` and `VERI_STEP` are the names event.sh already reads (event.sh:48-50), so
#     what this case pins is that they survive the hop from this suite's `env` into the
#     `mark` helper's child (supervise.sh:153-157) — the one place a `-i`, an explicit
#     variable list or a `mark` that spelled the context itself would silently drop them.
#
#     Both marks are asserted, not just the `launch`: they are written from different points
#     in the script (before the retry loop and after it), so a context that reached one is no
#     evidence the other has it.
#
#     The two values are deliberately unlike every other number on the line — the step is 4,
#     not the 1 the attempt carries or the 0 the success status does — so a mark that read
#     some other field into these keys is caught rather than agreeing by coincidence. Written
#     once each into a variable used both to launch and to expect, cases 12 and 13's shape:
#     spelled a second time in the assertion, the expectation could drift off the launch.
#
#     A directory of its own, for case 12's reason: the event log accumulates across a run,
#     and `event_field` demands exactly one line of the kind it is asked for.
ctx_work="$work/ctx"
ctx_issue=163
ctx_step=4
sup_run "$ctx_work" VERI_ISSUE="$ctx_issue" VERI_STEP="$ctx_step" \
    "$SUP" develop-red "$stub/leaf-ok"
ctx_code=$?
ctx_launch_issue="$(event_field "$ctx_work" launch issue)"
ctx_launch_step="$(event_field  "$ctx_work" launch step)"
ctx_exit_issue="$(event_field   "$ctx_work" exit   issue)"
ctx_exit_step="$(event_field    "$ctx_work" exit   step)"
{ [[ "$ctx_code" == 0 ]] \
  && [[ "$ctx_launch_issue" == "$ctx_issue" ]] && [[ "$ctx_launch_step" == "$ctx_step" ]] \
  && [[ "$ctx_exit_issue"   == "$ctx_issue" ]] && [[ "$ctx_exit_step"   == "$ctx_step" ]]; } && ok \
  || no "VERI_ISSUE/VERI_STEP in the supervisor's environment reach its launch and exit events (code=$ctx_code, launch issue=$ctx_launch_issue want $ctx_issue step=$ctx_launch_step want $ctx_step, exit issue=$ctx_exit_issue want $ctx_issue step=$ctx_exit_step want $ctx_step)"

# 16. a finished leaf's own accounting reaches the event log with nobody asking for it: the
#     supervisor is what runs harvest-usage.sh, so a leaf whose log ends in the stream-json
#     `result` record a `claude -p` run closes with leaves exactly one `usage` line (issue
#     #163). The harvester has existed and been tested since #107, but nothing in a run ever
#     called it, so those numbers sat in the .log files and reached no reader.
#
#     This script is where the call belongs because it owns `.tdd/<name>.log` and is the one
#     choke point every leaf goes through (this file's header). A harvest asked for in the
#     conductor's prose instead would be missing from exactly the leaves the prose forgot,
#     which is the shape of the bug #163 reports.
#
#     The stub is written here rather than beside the leaf-* stubs at the top of the file
#     because the number the assertion reads has to be the number the stub printed — case
#     11's `date` stub is built at its point of use for the same reason. `num_turns` is the
#     field probed: it comes from the record's top level, and no other number on a `usage`
#     line could be mistaken for 7.
#
#     Exactly one line is half the criterion, and `event_field` is what pins it: asked for a
#     key it reports `<<N usage lines>>` for every N but 1, so a harvest run per attempt, or a
#     second one added elsewhere later, fails here rather than being read past. The
#     supervisor's own exit code is asserted beside it because the harvest happens on its way
#     out: a leaf that finished clean must still report 0.
#
#     A directory of its own, for case 12's reason — the event log accumulates across a run.
usage_work="$work/usage"
usage_turns=7
# The closing record a finished leaf's log ends in, printed by a stub leaf of this suite's
# usual shape. The heredoc is unquoted so `$usage_turns` expands into the JSON; nothing else
# inside it is a shell expansion.
cat > "$stub/leaf-result" <<L
#!/bin/sh
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
echo '{"type":"result","subtype":"success","is_error":false,"duration_ms":91234,"duration_api_ms":40118,"num_turns":$usage_turns,"result":"done","session_id":"4d1a","total_cost_usd":0.31,"usage":{"input_tokens":37,"cache_creation_input_tokens":41002,"cache_read_input_tokens":903117,"output_tokens":5140}}'
exit 0
L
chmod +x "$stub/leaf-result"
sup_run "$usage_work" "$SUP" develop-red "$stub/leaf-result"
usage_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11, 12,
# 13 and 15's shape.
usage_got_turns="$(event_field "$usage_work" usage num_turns)"
{ [[ "$usage_code" == 0 ]] && [[ "$usage_got_turns" == "$usage_turns" ]]; } && ok \
  || no "a leaf whose log ends in a result record leaves exactly one usage event carrying that record's numbers (code=$usage_code, num_turns=$usage_got_turns want $usage_turns)"


# event_count <dir> <event> — how many <event> lines the event log a run in <dir> wrote
# holds, or '<<no event log>>' when there is no log at all. `event_field` above answers the
# question cases 12 to 16 ask — what the one line of a kind says — and mentions a count only
# in the diagnostic it prints when that assumption fails. Case 17 asks about a count of ZERO,
# which is a fact the log states rather than a failure to read it, so it gets a probe whose
# answer is the number: read through `event_field`, the case would be asserting on the
# wording of a diagnostic, and a clearer wording there would turn it red for nothing.
#
# The same parse as `event_field`'s, and the same two arguments — a run directory and an
# event name — so the two read as the siblings they are and neither states where the log
# lands under a run directory differently from the other.
event_count() {
  python3 -c '
import sys, json
n = 0
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == sys.argv[2]:
        n += 1
print(n)
' "$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo '<<no event log>>'
}

# 17. a killed leaf leaves NO `usage` line, and the harvest that found nothing to report
#     leaves the supervisor's own answer exactly as it was: exit 2, and 2 in the completion
#     file `.tdd/<name>.exit` (issue #163). Case 16 pins the harvest on the path where the
#     leaf finished and wrote its closing record; this is the other path, the one a killed
#     leaf takes — its log stops wherever the last write landed, so there is no `result`
#     record in it and harvest-usage.sh reports "nothing to do" (harvest-usage.sh:88-93).
#
#     Both halves matter and neither implies the other. A harvester that invented a `usage`
#     line out of an absent record would satisfy the exit code and still put a row of
#     fabricated numbers in front of a reader of #108's per-step cost. A harvester that
#     correctly wrote nothing but let its own non-zero status reach this script's answer
#     would turn a leaf the watchdog killed — a clean, classifiable killed-stuck — into some
#     other code, and `classify-bail.sh` reads that code to choose the label a human sees.
#     The completion file is asserted beside the exit code for case 9's reason: a detached
#     leaf is waited on by polling that file, so the two are separate promises and a harvest
#     running between the status line and the `printf` could break the second alone.
#
#     The leaf is `leaf-hang` under a one-second window, the way case 3 kills one: the
#     watchdog's heartbeat, well inside `sup_run`'s 10s hard cap, so the kill is quick and
#     the reason it happened is not what this case is about. The window rides in front of
#     `"$SUP"` rather than being spelled into a fresh helper — `exit_run`'s convention, where
#     `env` takes the last of a repeated name and the caller's number wins over the pinned 5.
#
#     A directory of its own under `$work`, for case 12's reason: the event log accumulates
#     across a run, and a count of `usage` lines taken anywhere else would be counting some
#     other case's leaf — case 16's, which leaves exactly the line this one denies.
killed_work="$work/killed"
killed_window=1
sup_run "$killed_work" VERI_HEARTBEAT="$killed_window" "$SUP" develop-red "$stub/leaf-hang"
killed_code=$?
# Each fact read once, into a variable the assertion and the failure message share — cases 9,
# 11, 12, 13, 15 and 16's shape. '<missing>' is case 9's spelling for a completion file that
# was never written, so a run that wrote none reports that rather than an empty string.
killed_usage="$(event_count "$killed_work" usage)"
killed_recorded="$(cat "$killed_work/.tdd/develop-red.exit" 2>/dev/null || echo '<missing>')"
{ [[ "$killed_usage" == 0 ]] \
  && [[ "$killed_code" == 2 ]] \
  && [[ "$killed_recorded" == 2 ]]; } && ok \
  || no "a killed leaf leaves no usage event and the supervisor still exits 2 and records 2 (usage lines=$killed_usage want 0, code=$killed_code want 2, .exit=$killed_recorded want 2)"

# 18. a harvest that FAILS — not one that found nothing — still leaves the supervisor's own
#     answer exactly as it was: exit 0, and 0 in the completion file `.tdd/<name>.exit`
#     (issue #163). Case 17 is the harvester's clean negative, the exit 3 it reports on a
#     killed leaf's truncated log; this is the other kind of non-zero, the one that says the
#     harvester itself broke — a closing record that is there but missing one of the eight
#     keys it reads, which harvest-usage.sh passes on rather than folding into its
#     "nothing to do" arm (harvest-usage.sh:110-115).
#
#     That distinction is the whole of the case. The harvest runs on the supervisor's way
#     out, between the last attempt and both of the things a caller reads the answer from, so
#     a call written without discarding its status would let a bug in a reader of .log files
#     decide a leaf's verdict: a leaf that passed would come back 1 and the conductor would
#     record a red step that never happened. What a run is measured by must not be able to
#     fail the run.
#
#     The leaf exits 0 so "unchanged" has something to be unchanged from, and so that the
#     number asserted is not one the harvester could also have produced: against a killed
#     leaf's 2 or a failing leaf's 1, a leaked status of the harvester's own would be
#     indistinguishable from the supervisor's own answer.
#
#     `usage` lines are counted beside the two, at zero, as this case's guard on its own
#     premise: the stub's log HOLDS a result record, so the harvester cannot be taking case
#     17's nothing-to-do path, and a run that appended a line anyway would be one where
#     nothing failed at all — leaving the two assertions above pinning nothing.
#
#     A directory of its own under `$work`, for case 12's reason.
harvest_fail_work="$work/harvest-fail"
# A closing record with no `usage` object — the shortest log that makes the harvester raise
# rather than report. Written here rather than beside the leaf-* stubs at the top for case
# 16's reason, next to the case whose premise it is; the heredoc is quoted, since unlike case
# 16's nothing inside it has to expand.
cat > "$stub/leaf-bad-result" <<'L'
#!/bin/sh
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
echo '{"type":"result","subtype":"success","is_error":false,"duration_ms":91234,"duration_api_ms":40118,"num_turns":7,"result":"done","session_id":"4d1a","total_cost_usd":0.31}'
exit 0
L
chmod +x "$stub/leaf-bad-result"
sup_run "$harvest_fail_work" "$SUP" develop-red "$stub/leaf-bad-result"
harvest_fail_code=$?
# Each fact read once, into the variable the assertion and the failure message share — cases
# 9, 11, 12, 13, 15, 16 and 17's shape.
harvest_fail_usage="$(event_count "$harvest_fail_work" usage)"
harvest_fail_recorded="$(cat "$harvest_fail_work/.tdd/develop-red.exit" 2>/dev/null || echo '<missing>')"
{ [[ "$harvest_fail_usage" == 0 ]] \
  && [[ "$harvest_fail_code" == 0 ]] \
  && [[ "$harvest_fail_recorded" == 0 ]]; } && ok \
  || no "a failing harvester leaves the supervisor's exit code and completion file unchanged (usage lines=$harvest_fail_usage want 0, code=$harvest_fail_code want 0, .exit=$harvest_fail_recorded want 0)"

# sup_run_no_model <dir> <argv…> — `sup_run` above, with none of the run's three model
# variables set: whatever the shell that typed `make test` chose, the child sees them unset
# unless the caller puts its own assignment in front of `"$SUP"`. Issue #87's rule, and issue
# #171's own — a suite's answer is a fact about the script, not about the caller's
# environment — and cases 19 and 20 both need it, so it is written down here once rather than
# in each arm-runner.
#
# The unsetting has to happen in a subshell rather than through `env -u`: `sup_run` applies its
# pinned assignments through `env`, and BSD `env` reads a `-u` after those as the utility to
# run. Inside that subshell the unsetting precedes `env`, so an arm's own value — riding in
# front of `"$SUP"` the way case 17's heartbeat does — is applied after it and an ambient
# `VERI_MODEL_DEVELOPER` cannot outrank the arm and turn a case red for the caller's shell.
sup_run_no_model() {
  ( unset VERI_MODEL VERI_MODEL_DEVELOPER VERI_MODEL_VERIFIER
    sup_run "$@" )
}

# 19. the `launch` mark says which model the leaf ran on — the value leaf-model.sh resolves
#     from the run's three model variables, or `""` when that run chose none (issue #171).
#     The supervisor is where it is resolved, beside the role it already reads
#     (supervise.sh:141): that is the one choke point every leaf goes through, so a model
#     recorded here cannot be missing from the leaves some other caller forgot, and the value
#     the log reports is the same one the launch will carry rather than a second reading of
#     the environment.
#
#     Without the key, a run log cannot compare verdicts, revise counts or cost between
#     models at all — which is the whole point of the issue: the first experiment is moving
#     verifier leaves to a cheaper model and keeping it only if the verdict distribution
#     holds, and that comparison joins on this field.
#
#     Both halves are asserted in one case because the key's promise is that it is ALWAYS
#     written (event.sh's rule for context keys): "no model" has to read as an empty value
#     and not as an absent key, or a reader cannot tell a run that chose no model from a
#     writer that forgot to say. `event_field` reports `<<missing>>` for a key the line does
#     not carry, so the empty half is a real assertion and not a comparison that passes on
#     absence.
#
#     A `develop-red` leaf, and a value written once into a variable used both to launch and
#     to expect — cases 12, 15 and 16's shape. A directory per probe, for case 12's reason:
#     the event log accumulates across a run, and `event_field` demands exactly one line of
#     the kind it is asked for.
model_work="$work/model"
model_value=sonnet

# model_run <arm> [assignment…] — supervise one `develop-red` leaf in its own directory under
# $model_work, named for the arm, through `sup_run_no_model` above so the arm sets the only
# model variable the child sees. Case 14's arm-runner shape, and for its reason: what the two
# arms share — the leaf, the name and the directory scheme — is written down once, so the arms
# differ by exactly the thing the case is about.
model_run() {
  local arm="$1"; shift
  sup_run_no_model "$model_work/$arm" "$@" "$SUP" develop-red "$stub/leaf-ok"
}

model_run set VERI_MODEL="$model_value"
model_set_code=$?
model_run unset
model_unset_code=$?
# Each field read once, into a variable the assertion and the failure message share — cases
# 9, 11, 12, 13, 15, 16, 17 and 18's shape.
model_set_got="$(event_field   "$model_work/set"   launch model)"
model_unset_got="$(event_field "$model_work/unset" launch model)"
{ [[ "$model_set_code" == 0 ]] && [[ "$model_unset_code" == 0 ]] \
  && [[ "$model_set_got"   == "$model_value" ]] \
  && [[ "$model_unset_got" == "" ]]; } && ok \
  || no "the launch event carries the resolved model, and an empty one when the run chose none (VERI_MODEL=$model_value: code=$model_set_code model=$model_set_got want $model_value; none set: code=$model_unset_code model=$(printf '%q' "$model_unset_got") want '')"

# 20. the resolved model reaches the leaf's own `claude` argv as `--model <value>` — and the
#     argv is byte-identical to today's when the run chose no model (issue #171). Case 19
#     pins what the run LOG says the leaf ran on; this one pins what the leaf was actually
#     run with, and the two are not the same claim: a `model=sonnet` line over a `claude`
#     invocation that never carried the flag would report an experiment nobody ran, and the
#     verdict distribution it was kept or dropped on would be the old model's.
#
#     The unset arm is asserted against the WHOLE argv, not against the absence of a
#     `--model` word: "no override" has to leave the command line exactly as it is today,
#     and an extra flag, a reordering or a dropped `--verbose` would all be invisible to a
#     grep for one word. The set arm is asserted as the adjacent pair instead — the flag and
#     its value, in that order — because where in the line it lands is the implementation's
#     business and pinning its position here would make a legal spelling red.
#
#     The leaf is `run-leaf.sh` itself rather than one of this file's stubs, since the argv
#     under test is built there; the `claude` behind it is a stub recording its arguments,
#     the shape run-leaf.test.sh already uses. A directory per arm, for case 12's reason,
#     and a value written once and used both to launch and to expect — cases 12, 15, 16 and
#     19's shape.
argv_work="$work/argv"
argv_model=sonnet
argv_prompt='pin the argv'
mkdir -p "$argv_work"
printf '%s' "$argv_prompt" > "$argv_work/prompt.txt"

# The recording `claude`: argv one word per line, then the minimal stream-json stream
# run-leaf.sh's own suite emits, so extract-result.sh at the foot of run-leaf finds a result
# to append and the supervision ends 0 rather than on a parse failure this case is not about.
cat > "$stub/claude-argv" <<'L'
#!/bin/sh
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
L
chmod +x "$stub/claude-argv"

# argv_run <arm> [assignment…] — supervise one `develop-red` leaf whose command is run-leaf.sh
# against the recording stub, in its own directory under $argv_work, through
# `sup_run_no_model` above for case 19's reason. The stub and the file it records into are
# pinned in front of the arm's own assignment, which `env` therefore applies last.
argv_run() {
  local arm="$1"; shift
  sup_run_no_model "$argv_work/$arm" CLAUDE_BIN="$stub/claude-argv" ARGV_OUT="$argv_work/$arm.argv" \
    "$@" "$SUP" develop-red "$HERE/../run-leaf.sh" "$argv_work/prompt.txt"
}

argv_run set VERI_MODEL="$argv_model"
argv_set_code=$?
argv_run unset
argv_unset_code=$?
# Today's argv, spelled out: what run-leaf.sh builds for a leaf no model was chosen for
# (run-leaf.sh:44). Written as the same one-word-per-line rendering the stub records, so the
# comparison is of the whole command line and not of a summary of it.
argv_today="$(printf '%s\n' -p "$argv_prompt" --output-format stream-json --verbose)"
# Each fact read once, into the variable the assertion and the failure message share — cases
# 9, 11, 12, 13, 15, 16, 17, 18 and 19's shape.
argv_set_got="$(cat   "$argv_work/set.argv"   2>/dev/null || echo '<<no argv>>')"
argv_unset_got="$(cat "$argv_work/unset.argv" 2>/dev/null || echo '<<no argv>>')"
{ [[ "$argv_set_code" == 0 ]] && [[ "$argv_unset_code" == 0 ]] \
  && [[ "$argv_set_got"   == *"--model"$'\n'"$argv_model"* ]] \
  && [[ "$argv_unset_got" == "$argv_today" ]]; } && ok \
  || no "a supervised leaf's claude argv carries --model only when the run chose a model (VERI_MODEL=$argv_model: code=$argv_set_code argv=$(printf '%q' "$argv_set_got") want a --model/$argv_model pair; none set: code=$argv_unset_code argv=$(printf '%q' "$argv_unset_got") want $(printf '%q' "$argv_today"))"
# 21. the `launch` line carries the commit of the SKILL that launched the leaf, in
#     `skill_commit` — the eighth fixed key event.sh writes, whose point that script's header
#     states (issue #165). event.sh reads the sha from `VERI_SKILL_COMMIT`, and the supervisor
#     is what has to put it there: this is the one choke point every leaf goes through, and
#     the only place that knows where the running scripts live.
#
#     The expectation is read from the scripts' OWN directory — `git -C` on `$SUP`'s
#     directory, not on the cwd — and the supervision runs in a temp directory under `$work`
#     that is no git repository at all. So a resolution that asked the leaf's worktree
#     instead of the skill's would answer with this repo only by accident of the suite living
#     in it; run from `$work` it answers nothing, and the case is red.
#
#     A nested `env -u VERI_SKILL_COMMIT` clears the variable for the supervisor, the
#     hermeticity cases 8 and 11 insist on: the sha must be one the supervisor resolved, not
#     one the shell that ran `make test` happened to export. Nested rather than a `-u` handed
#     to `sup_run`, because `env` stops reading options at the first `VAR=VALUE` word and the
#     helper's pinned quartet comes first — a `-u` after it is read as the command to run.
#
#     A directory of its own under `$work`, for case 12's reason — the event log accumulates
#     across a run, and `event_field` demands exactly one line of the kind it is asked for.
skill_work="$work/skill"
skill_want="$(git -C "$SCRIPTS" rev-parse HEAD 2>/dev/null || echo '<no-sha>')"
sup_run "$skill_work" env -u VERI_SKILL_COMMIT "$SUP" develop-red "$stub/leaf-ok"
skill_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11,
# 12, 13, 15, 16, 17, 18, 19 and 20's shape.
skill_got="$(event_field "$skill_work" launch skill_commit)"
{ [[ "$skill_code" == 0 ]] \
  && [[ "$skill_want" =~ ^[0-9a-f]{40}$ ]] \
  && [[ "$skill_got" == "$skill_want" ]]; } && ok \
  || no "a launch event carries the skill's own commit in skill_commit (code=$skill_code, skill_commit=$skill_got want $skill_want)"

# 20. a skill that is not in a git clone records the literal `unknown`, not an empty value
#     (issue #165). Case 19 pins the sha when there is one; the skill need not be installed
#     from a clone at all — a copied directory, a tarball, a vendored `scripts/` — and there
#     the resolution has no answer to give. Why the absence is spelled rather than left empty
#     is supervise.sh's own header, at the assignment this case drives.
#
#     What is this case's to say is why it is the SUPERVISOR's and not event.sh's:
#     event.test.sh's case 4 pins that the key is on the line whatever the environment holds,
#     and leaves what an unresolvable commit should READ as to the resolver — this script is
#     the resolver, the one place that knows where the running scripts live.
#
#     The skill is made unresolvable by moving it, not by breaking git: `$SCRIPTS`'s `.sh`
#     files are copied into a directory under `$work`, which is a `mktemp -d` and so no git
#     repository — and the copy is what runs, so `$HERE` inside it is the directory git is
#     asked about. The glob is what keeps the copy whole as scripts are added to the skill,
#     rather than a list of the ones this supervisor happens to reach for today. `cp`
#     preserves the execute bit. `lib/` is copied too, the shape event-log.test.sh and
#     main-working-tree.test.sh already use for status.sh and solvable-issues.sh: supervise.sh
#     now sources lib/leaf-model.sh (which sources lib/leaf-role.sh in turn) instead of
#     forking leaf-role.sh/leaf-model.sh, so a copy of the flat `.sh` files alone is no longer
#     a complete copy of what the supervisor needs to run. `lib/json-escape.sh` joins the copy
#     for the same reason (issue #290): event.sh, which the `launch` mark below still reaches
#     through this copy, now sources it too, and a copy missing it fails the mark silently
#     (supervise.sh's `mark` has no `||` to report event.sh's own failure) rather than writing
#     the `unknown` this case is pinning.
#
#     The precondition is asserted rather than assumed: if `$TMPDIR` ever sat inside a clone,
#     git would resolve a sha there and the case would pass on a condition it never created.
#     `nogit_resolves` records what git says of the copy, and `<none>` is the only value that
#     makes the rest of the assertion mean what it claims.
#
#     A directory of its own for the run, for case 12's reason — the event log accumulates
#     across a run, and `event_field` demands exactly one line of the kind it is asked for.
nogit_skill="$work/nogit-skill"
mkdir -p "$nogit_skill/lib"
cp "$SCRIPTS"/*.sh "$nogit_skill/"
cp "$SCRIPTS/lib/leaf-role.sh" "$SCRIPTS/lib/leaf-model.sh" "$SCRIPTS/lib/json-escape.sh" "$nogit_skill/lib/"
nogit_resolves="$(git -C "$nogit_skill" rev-parse HEAD 2>/dev/null || echo '<none>')"
nogit_work="$work/nogit-run"
sup_run "$nogit_work" env -u VERI_SKILL_COMMIT "$nogit_skill/supervise.sh" develop-red "$stub/leaf-ok"
nogit_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11,
# 12, 13, 15, 16, 17, 18 and 19's shape.
nogit_got="$(event_field "$nogit_work" launch skill_commit)"
{ [[ "$nogit_code" == 0 ]] \
  && [[ "$nogit_resolves" == '<none>' ]] \
  && [[ "$nogit_got" == unknown ]]; } && ok \
  || no "a skill outside a git clone records skill_commit as the literal unknown (code=$nogit_code, git says=$nogit_resolves want <none>, skill_commit=$nogit_got want unknown)"


# result_hang_stub <stub-name> <subtype> <is_error> <result-text> [prelude] — the one leaf
# shape cases 23 to 26 are all driven by: print an assistant line, print the closing result
# record the case is about, then sleep. The sleep is the premise those cases share and assert
# on — the leaf's subshell never gets to write `.tdd/<name>.rc`, so only the watchdog can end
# the supervision and the kill always lands on a stream that already finished.
#
# Written here rather than beside the leaf-* stubs at the top of the file, for case 16's
# reason: next to the cases whose premise it is. What each case varies is the record alone,
# so that is what it passes — the subtype and `is_error` pair a real `claude -p` closes with,
# and the result text the recovery has to carry through. The eight numbers around them are
# held here once: a full record, so the harvest on the supervisor's way out takes case 16's
# path rather than case 18's and nothing these cases are not about can decide the code they
# read. `prelude` is a line run before the stream, which only case 25 needs.
#
# The heredoc is unquoted so those four expand into the JSON, case 16's spelling; nothing
# else inside it is a shell expansion, and a `\n` in the result text reaches the file as the
# two characters a stream-json string escapes a newline with.
result_hang_stub() {
  local name="$1" subtype="$2" is_error="$3" text="$4" prelude="${5:-}"
  cat > "$stub/$name" <<L
#!/bin/sh
$prelude
printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
printf '%s\n' '{"type":"result","subtype":"$subtype","is_error":$is_error,"duration_ms":164524,"duration_api_ms":44600,"num_turns":12,"result":"$text","session_id":"4d1a","total_cost_usd":0.31,"usage":{"input_tokens":37,"cache_creation_input_tokens":41002,"cache_read_input_tokens":903117,"output_tokens":5140}}'
clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"
sleep 60
L
  chmod +x "$stub/$name"
}


# sup_direct <dir> <leaf> <window> [env-arg…] — the supervisor launched STRAIGHT, in a run
# directory of its own, on the compressed windows cases 25 to 27 share: a `$window`-second
# heartbeat, a 30 s hard cap well past it, and `sup`'s 0.2 s poll. Its stdio is left alone,
# which is why it is not `sup_run`: each of those cases wants a different one — /dev/null,
# a captured stdout, a stderr file of its own — and `sup_run` sends both to /dev/null.
#
# The retry budget is the caller's word rather than a pinned one, passed through as the
# leading arguments to `env`: `VERI_STUCK_RETRIES=0` where the case wants one attempt,
# `-u VERI_STUCK_RETRIES` where it wants the DEFAULT budget to produce the retry it forbids
# (case 25, case 13's spelling). That is the one axis those cases differ on, and pinning it
# here would make case 25 vacuous.
#
# `verify-red` is the name throughout, the leaf #207 lost a rendered verdict on.
sup_direct() {
  local dir="$1" leaf="$2" window="$3"; shift 3
  mkdir -p "$dir"
  ( cd "$dir" && env "$@" VERI_HEARTBEAT="$window" VERI_TIMEOUT=30 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$SUP" verify-red "$stub/$leaf" )
}


# leaf_rc <dir> — the LEAF subshell's own exit code, as recorded in `<dir>/.tdd/verify-red.rc`,
# or `<missing>` when nothing wrote one (case 9's spelling for a file that was never written).
# Cases 23 and 24 both read it as the guard on their own premise: their stub sleeps forever, so
# only the watchdog can end the supervision, and a `.rc` present at all would mean the
# supervisor took its ordinary success/failure path and the case pinned nothing about the
# recovery. `verify-red` is the leaf name throughout, `sup_direct`'s reason.
leaf_rc() { cat "$1/.tdd/verify-red.rc" 2>/dev/null || echo '<missing>'; }


# 23. a leaf the watchdog KILLS whose progress log already holds a terminal result record is
#     reported with the leaf's own outcome — exit 0 for a record that says `is_error: false` —
#     and not as killed-stuck (issue #212). Case 3 pins the other half, the hung leaf that
#     produced nothing and is still exit 2; this is the leaf that worked, finished its stream
#     and was killed anyway, which is what #207's `verify-red` did: 165 s of work, a complete
#     `VERDICT: PASS` in the log, and an exit 2 the conductor could only read as "no answer
#     could be obtained" and bail on.
#
#     The distinction the case defends is the load-bearing one in this codebase: exit 2 means
#     the plumbing broke, exit 1 that the methodology spoke. A rendered verdict reported as
#     killed-stuck puts a process answer under a system label, so every `no-verdict` bail in a
#     run log becomes unreadable — nothing in it tells "the verifier never answered" from "the
#     verifier answered and we killed it". Whatever the heartbeat window is, a finished stream
#     is not a stuck one.
#
#     The stub prints the record and then sleeps, so the leaf's subshell never gets to write
#     `.tdd/<name>.rc` and only the watchdog can end the supervision. That absent rc file is
#     read through `leaf_rc` above as this case's guard on its own premise: with one there, the
#     supervisor would have taken its ordinary success path and the case would be pinning
#     nothing at all.
#
#     The window rides in front of `"$SUP"` — case 17's convention, where `env` takes the last
#     of a repeated name — and is one second, well inside `sup_run`'s 10 s hard cap, so the
#     kill is the heartbeat's and quick. A directory of its own under `$work`, for case 12's
#     reason.
result_kill_work="$work/result-kill"
result_hang_stub leaf-result-hang success false 'VERDICT: PASS'
sup_run "$result_kill_work" VERI_HEARTBEAT=1 "$SUP" verify-red "$stub/leaf-result-hang"
result_kill_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11, 12,
# 13 and 15 to 22's shape.
result_kill_rc="$(leaf_rc "$result_kill_work")"
{ [[ "$result_kill_code" == 0 ]] \
  && [[ "$result_kill_rc" == '<missing>' ]]; } && ok \
  || no "a killed leaf whose log holds a terminal result record is reported with the leaf's own outcome, not killed-stuck (code=$result_kill_code want 0, .rc=$result_kill_rc want <missing>)"


# 24. the same killed-but-finished leaf whose terminal result record says the run FAILED is
#     reported exit 1, not exit 0 (issue #212). Case 23 pins the `is_error: false` half; this
#     is the other side of the same record, and the two together are what "the leaf's own
#     outcome" means — a recovery that reported every finished leaf as a success would turn a
#     verifier's REJECT, or a developer leaf that blew up, into a green the conductor carries
#     on from.
#
#     Exit 1 is a clean negative in this repository's contract — the leaf ran and failed, a
#     real answer — and it is the code the leaf itself would have exited on had the watchdog
#     let it live: `is_error` is the record's own word for how the run ended.
#
#     Same stub shape as case 23 — print the record, then sleep, so the leaf's subshell never
#     writes `.tdd/<name>.rc` and only the watchdog can end the supervision — and the absent
#     rc file is read through `leaf_rc` for case 23's reason: with one there, the supervisor
#     would have taken its ordinary failure path and the case would pin nothing. A directory
#     of its own under `$work`, for case 12's reason, and the one-second window in front of
#     `"$SUP"` for case 17's.
error_kill_work="$work/error-kill"
# `subtype` says `error_during_execution` beside `is_error: true`, the pair a `claude -p` run
# that ended badly closes its stream with, so the record under test is one a real leaf writes.
result_hang_stub leaf-error-hang error_during_execution true 'the suite did not finish'
sup_run "$error_kill_work" VERI_HEARTBEAT=1 "$SUP" verify-red "$stub/leaf-error-hang"
error_kill_code=$?
# Read once, into the variable the assertion and the failure message share — cases 9, 11, 12,
# 13, 15 to 22 and 23's shape.
error_kill_rc="$(leaf_rc "$error_kill_work")"
{ [[ "$error_kill_code" == 1 ]] \
  && [[ "$error_kill_rc" == '<missing>' ]]; } && ok \
  || no "a killed leaf whose terminal result record is an error is reported exit 1, not exit 0 (code=$error_kill_code want 1, .rc=$error_kill_rc want <missing>)"


# 25. the recovery of case 23 happens on the FIRST attempt, so the leaf is launched exactly
#     once and no `retry` mark is written (issue #212). Cases 23 and 24 pin the code the
#     supervision ends on; they cannot see how many leaves it cost to get there, because a
#     recovery applied only after the retry loop had run its budget out would end on exactly
#     the same code. This is the case that tells the two apart.
#
#     What is at stake is the price of the bug rather than its correctness: a verifier leaf
#     that already rendered its verdict is relaunched from scratch, works for another two or
#     three minutes and is killed again on the same too-tight window, and the answer the run
#     finally reports was sitting in the first attempt's log. The retry budget exists for a
#     leaf that never answered (VERI_STUCK_RETRIES is the liveness axis); spending it on one
#     that did is spending it on the wrong axis.
#
#     The DEFAULT budget is what runs here — `env -u VERI_STUCK_RETRIES`, case 13's spelling,
#     so a value exported by the shell that ran `make test` can neither add the retry this
#     case forbids nor suppress one the supervisor would have made. That is also why this
#     case goes through `sup_direct` rather than `sup` or `sup_run`: both pin the budget to
#     0, which would make the assertion vacuous.
#
#     Two observations, because "launched once" and "no retry" are the same fact seen from
#     the leaf's side and from the run log's: the stub appends a line per invocation to a
#     counter file in its cwd — which the supervisor preserves across attempts, case 13's
#     leaf-flaky marker relies on the same — and `event_field` is asked for the `retry` mark,
#     where a log holding none answers `<<0 retry lines>>` rather than a cause. The exit code
#     is asserted beside them so a case that went green on a leaf which never recovered at all
#     would still be caught.
result_once_work="$work/result-once"
# Case 23's stub plus the counter as its prelude, and the same sleep behind it: the leaf must
# never write `.tdd/<name>.rc`, so only the watchdog can end each attempt and a second attempt
# would be killed exactly like the first.
result_hang_stub leaf-result-hang-counted success false 'VERDICT: PASS' 'echo attempt >> .attempts'
sup_direct "$result_once_work" leaf-result-hang-counted 1 -u VERI_STUCK_RETRIES >/dev/null 2>&1
result_once_code=$?
# Each read once, into the variable the assertion and the failure message share — cases 9,
# 11, 12, 13, 15 to 24's shape. `wc -l` is fed on stdin and stripped of blanks because the
# BSD spelling pads its count with leading spaces, and `[[ … == 1 ]]` would then miss.
result_once_attempts="$(wc -l < "$result_once_work/.attempts" 2>/dev/null | tr -d ' ')"
result_once_retry="$(event_field "$result_once_work" retry cause)"
{ [[ "$result_once_code" == 0 ]] \
  && [[ "$result_once_attempts" == 1 ]] \
  && [[ "$result_once_retry" == '<<0 retry lines>>' ]]; } && ok \
  || no "a leaf recovered from its terminal result record is launched exactly once, with no stuck-retry (code=$result_once_code want 0, attempts=$result_once_attempts want 1, retry=$result_once_retry want <<0 retry lines>>)"


# 26. a recovered leaf's captured stdout ends with the CLEAN result text, so parse-verdict.sh
#     reads its verdict off this supervisor's stdout (issue #212). Cases 23 to 25 pin the code
#     the supervision ends on and what it cost; none of them looks at what it printed. But the
#     code alone is not what a verify-* leaf is for — `verify.sh` pipes supervise.sh's stdout
#     straight into parse-verdict.sh, so a recovery that reports exit 0 while printing a log
#     parse-verdict.sh cannot read hands the conductor a leaf that succeeded with no verdict,
#     which is exit 2 again by another route.
#
#     The gap is run-leaf.sh's: it appends the clean result text after the raw stream, so the
#     captured output ends with a parseable VERDICT block — and a killed leaf never reaches
#     that line. What survives in `.tdd/<name>.log` is stream-json only, where the verdict is
#     a `\n`-escaped string INSIDE a `{"type":"result", …}` object on one line. parse-verdict.sh
#     matches `VERDICT:` at the start of a line, so that line is invisible to it: the text is
#     in the log and unreadable. The recovery therefore owes the same append the leaf would
#     have made.
#
#     Asserted through parse-verdict.sh itself rather than by grepping the output for the
#     word, because the criterion is that the real reader can read it — a `VERDICT:` the parser
#     rejects would pass a grep. Its stderr is folded into the captured reason so a refusal
#     ("no VERDICT: line found") reaches the failure message instead of being swallowed.
#
#     Same stub shape as case 23 — the record, then a sleep, so only the watchdog can end the
#     supervision — with a two-line verdict block in the `result` field, the shape a real
#     verifier closes its stream with. Through `sup_direct` rather than `sup_run`, which sends
#     stdout to /dev/null; the pinned VERI_STUCK_RETRIES=0 is the budget it is handed.
result_text_work="$work/result-text"
result_hang_stub leaf-verdict-hang success false 'VERDICT: PASS\nREASON: the new case fails on the eight session-handle checks'
result_text_out="$(sup_direct "$result_text_work" leaf-verdict-hang 1 VERI_STUCK_RETRIES=0 2>/dev/null)"
# Read once, into the variables the assertion and the failure message share — cases 9, 11, 12,
# 13, 15 to 25's shape. The verdict code is parse-verdict.sh's own contract: 0 PASS, 1 REJECT,
# 2 nothing it could recognise.
result_text_reason="$(printf '%s\n' "$result_text_out" | "$SCRIPTS/parse-verdict.sh" 2>&1)"
result_text_code=$?
{ [[ "$result_text_code" == 0 ]] \
  && [[ "$result_text_reason" == *'eight session-handle checks'* ]]; } && ok \
  || no "a recovered leaf's captured stdout ends with the clean result text, so parse-verdict.sh reads its verdict (verdict code=$result_text_code want 0, reason=$result_text_reason want the leaf's REASON text)"



# 27. a leaf the watchdog kills whose log holds NO terminal result record is still killed and
#     still reported exit 2, with the watchdog's kill cause on stderr (issue #212). Cases 23
#     to 26 are the recovery; this is the boundary it must not cross. The leaf here has done
#     everything a working one does except finish — it is a real `claude -p` stream, one
#     stream-json record after another — and then it goes silent. That is exactly the hang the
#     watchdog exists for, and the answer it owes is the one it always owed: no answer could be
#     obtained.
#
#     Case 3 pins the same code on `leaf-hang`, whose log is one line of plain text, so it
#     cannot see the sensor the recovery reads with: a no-op is what a script with no recovery
#     at all does too. This leaf's log is a stream of well-formed JSON objects that any looser
#     sensor — output present, valid JSON present, an assistant record present — would read as
#     an answer, and the exit 0 that followed would report a leaf that never answered as one
#     that succeeded. The only record it does not hold is the closing `{"type":"result", …}`,
#     which is the whole of what "the leaf finished" means.
#
#     The kill cause is asserted beside the code because the code alone does not make a bail
#     classifiable: `classify-bail.sh` turns the supervisor's stderr into the label a human
#     reads, and a recovery that silently cleared `reason` on the way past would leave a bare
#     `killed-stuck` with nothing saying what the watchdog saw. The wording is read through
#     `heartbeat_kill` above, cases 13 and 14's probe, so a change to it is caught in one place.
#
#     Through `sup_direct` rather than `sup`, whose single `$work/err` is shared with every
#     other case that uses it; this case's stderr is its own file under its own directory,
#     case 12's reason. VERI_STUCK_RETRIES=0 is the budget it is handed — one attempt, so the
#     transcript holds exactly one status line. The `mkdir` stays here as well as in the
#     helper because the shell opens that stderr file BEFORE the helper runs, so the
#     directory has to exist a moment earlier than the helper would make it.
nores_work="$work/no-result"
mkdir -p "$nores_work"
# The stream a leaf that hangs mid-run leaves behind: a system init record and an assistant
# record, both well-formed JSON, and then silence. No `{"type":"result", …}` line — the leaf
# never got that far, which is the premise of the case.
cat > "$stub/leaf-noresult-hang" <<'L'
#!/bin/sh
echo '{"type":"system","subtype":"init","session_id":"4d1a","model":"claude-opus-5"}'
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: reading the suite"}]}}'
clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"
sleep 60
L
chmod +x "$stub/leaf-noresult-hang"
nores_window=1
sup_direct "$nores_work" leaf-noresult-hang "$nores_window" VERI_STUCK_RETRIES=0 \
  >/dev/null 2>"$nores_work/err"
nores_code=$?
# Each read once, into the variable the assertion and the failure message share — cases 9,
# 11, 12, 13 and 15 to 26's shape. The cause is taken off the supervisor's own status line by
# stripping its prefix, so a run that printed no such line at all leaves `<no status line>`
# rather than an empty string that a loose pattern might still accept.
nores_status="$(grep '^supervise\[verify-red\]: killed-stuck' "$nores_work/err" || echo '<no status line>')"
nores_cause="${nores_status#supervise\[verify-red\]: killed-stuck — }"
{ [[ "$nores_code" == 2 ]] \
  && heartbeat_kill "$nores_cause" "$nores_window"; } && ok \
  || no "a killed leaf whose log holds no terminal result record is still exit 2 with its kill cause on stderr (code=$nores_code want 2, status line=$nores_status want a killed-stuck line whose cause reads 'no heartbeat for Ns (window ${nores_window}s)')"

# 28. supervise.sh's HEADER records the mechanism behind cases 23 to 27, not just the rule
#     (issue #212). The rule — a killed leaf whose log holds a terminal result record is
#     reported with its own outcome — is already there; what a reader cannot get from it is
#     WHY a kill and a rendered verdict can coexist at all, which is that the leaf's stream
#     finishes before the subshell's `.tdd/<name>.rc` is written. The watchdog's only sensor
#     for "the leaf is done" is that file, so the window between the two is one in which a
#     finished leaf still looks unfinished, and a kill landing there is not proof that no
#     answer was obtained.
#
#     Pinned as prose because prose is where it lives: nothing in the running script says it,
#     and the recovery reads as a defensive coincidence without it — the next reader to find
#     `recover_finished_leaf` surprising deletes it, and the run log goes back to reporting a
#     rendered verdict as exit 2. Case 10's shape, one table of sites and a miss reported by
#     name, with two differences: the header is extracted first, so a sentence added anywhere
#     below it — in `recover_finished_leaf`'s own comment, say — does not answer for it, and
#     the patterns ask for a statement rather than a figure, so a site is a hit or a miss and
#     there is no number to compare.
#
#     The regexes are deliberately loose on wording and tight on the two claims, each bounded
#     so it cannot span the whole header and match two unrelated sentences as one.
header_text="$(awk 'NR > 1 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "$SUP" | tr '\n' ' ')"
header_misses=""
while IFS='|' read -r where regex; do
  [[ -n "$where" ]] || continue
  grep -qE "$regex" <<< "$header_text" || header_misses="$header_misses $where"
done <<'CLAIMS'
stream-finishes-before-rc|(finish|complete)[a-z]* .{0,120}before .{0,80}(rc file|rcfile|\.rc)
kill-is-not-proof|kill.{0,160}not proof
CLAIMS

[[ -z "$header_misses" ]] && ok \
  || no "supervise.sh's header records that a leaf's stream can finish before its rc file is written, so a kill is not proof that no answer was obtained (unstated:$header_misses)"

# 29. supervise.sh records its OWN pid in .tdd/<name>.pid before it launches the leaf (issue
#     #173), so wait-leaf.sh can tell a supervisor that died without writing its completion
#     file from one that is still watching a slow leaf. "Before the launch" is observed from
#     inside the leaf: the stub copies whatever `.tdd/develop-red.pid` holds at the moment it
#     runs into a file of its own, or `<missing>` when there is none — so a pid file written
#     after the leaf started, or never, reads as absent.
#
#     The supervisor is started in the background and `exec`ed, so `$!` is the pid of
#     supervise.sh itself rather than of a wrapping subshell, and that is the value the leaf
#     must have seen. A directory of its own under `$work`, for case 12's reason.
pid_work="$work/pid-record"
mkdir -p "$pid_work"
cat > "$stub/leaf-pid-seen" <<'L'
#!/bin/sh
cat .tdd/develop-red.pid 2>/dev/null > pid-seen || echo '<missing>' > pid-seen
exit 0
L
chmod +x "$stub/leaf-pid-seen"
( cd "$pid_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 VERI_TIMEOUT=10 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-pid-seen" ) >/dev/null 2>&1 &
pid_sup=$!
wait "$pid_sup"
pid_seen="$(tr -d '[:space:]' < "$pid_work/pid-seen" 2>/dev/null || echo '<no leaf run>')"
[[ "$pid_seen" == "$pid_sup" ]] && ok \
  || no "supervise.sh records its own pid in .tdd/<name>.pid before it launches the leaf (leaf saw=$pid_seen want $pid_sup)"


# 30. supervise.sh sent TERM writes 2 to its completion file, exits 2 and leaves no leaf
#     process behind (issue #173). The leaf runs in a process group of its own (`set -m`), so a
#     signal addressed to the supervisor never reaches it: without a handler the supervisor
#     dies wherever it is, `.tdd/<name>.exit` is never written, and the leaf keeps running
#     with no watchdog at all. TERM stands for the three signals the handler covers.
#
#     The stub records its own pid and `exec`s into a long sleep, so the recorded pid IS the
#     leaf process for its whole life. The supervisor is `exec`ed in the background, case 29's
#     shape, so `$!` is supervise.sh itself and TERM is addressed to it alone. Every wait is
#     bounded, and a leaf that did survive is killed here so the suite leaves nothing behind.
term_work="$work/term-handler"
mkdir -p "$term_work"
cat > "$stub/leaf-term-sleep" <<'L'
#!/bin/sh
echo $$ > leaf-pid
echo "leaf: started"
exec sleep 60
L
chmod +x "$stub/leaf-term-sleep"
( cd "$term_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
term_sup=$!
for _ in $(seq 1 50); do [[ -s "$term_work/leaf-pid" ]] && break; sleep 0.1; done
term_leaf="$(tr -d '[:space:]' < "$term_work/leaf-pid" 2>/dev/null)"
kill -TERM "$term_sup" 2>/dev/null
wait "$term_sup"
term_code=$?
term_exit="$({ tr -d '[:space:]' < "$term_work/.tdd/develop-red.exit"; } 2>/dev/null || echo '<missing>')"
term_alive="no"
if [[ -n "$term_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$term_leaf" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$term_leaf" 2>/dev/null; then term_alive="yes"; kill -KILL "$term_leaf" 2>/dev/null; fi
else
  term_alive="<leaf never started>"
fi
{ [[ "$term_code" == 2 ]] && [[ "$term_exit" == 2 ]] && [[ "$term_alive" == no ]]; } && ok \
  || no "supervise.sh sent TERM writes 2 to its completion file, exits 2 and leaves no leaf process behind (code=$term_code want 2, exit file=$term_exit want 2, leaf alive=$term_alive want no)"

# 31. a leaf name leaf-role.sh refuses degrades gracefully: the leaf still runs to completion
#     and the supervisor still reports its real status, but nothing is marked to the event
#     log rather than a line whose actor was invented (supervise.sh:231-233's own comment).
#
#     Regression pin for the perf refactor that moves leaf-role.sh's mapping, and
#     leaf-model.sh's (which asks leaf-role.sh too), into sourced library functions called
#     from supervise.sh:233 and :241 in place of the two
#     `"$HERE/leaf-role.sh" "$name" ... || role=""` / `"$HERE/leaf-model.sh" "$name" ...
#     || model=""` subprocess calls: today a name neither script recognises leaves `$role`
#     and `$model` empty exactly the way the trailing `||` reads a subprocess's exit 2, and
#     `mark` (supervise.sh:283) then writes nothing to `.tdd/events.jsonl` for either the
#     `launch` or the `exit` line. A sourced function that raised (`exit` instead of
#     `return`) where the subprocess used to just fail would take the whole supervision
#     down instead of degrading it this way.
#
#     `leaf-ok`, the same clean stub case 1 uses, because this case is about the SUPERVISION
#     around an unrecognised name, not about the leaf's own outcome — a leaf that failed or
#     hung would leave two reasons this could go red instead of one.
name_work="$work/unknown-name"
sup_run "$name_work" "$SUP" frobnicate-red "$stub/leaf-ok"
name_code=$?
name_launch_events="$(event_count "$name_work" launch)"
{ [[ "$name_code" == 0 ]] \
  && [[ "$name_launch_events" == 0 || "$name_launch_events" == '<<no event log>>' ]]; } && ok \
  || no "a leaf name leaf-role.sh refuses still runs the leaf to completion but marks no launch event (code=$name_code want 0, launch events=$name_launch_events want 0 or no event log)"

# 32. VERI_KILL_POLL — kill_tree's grace-loop poll, the interval it sleeps between checking
#     whether a killed leaf's process group has actually gone away (up to 5 checks, real
#     sleep: it polls `kill -0`, an OS fact, not the injected clock cases above jump). This
#     suite already pins it to 0.02 in sup() below, so ~18 killed-stuck cases here do not
#     each pay up to 5 x the 0.1s production default in real wall time; this case is the
#     tunable's own contract, the way case 3 in refactor-budget.test.sh pins
#     VERI_REFACTOR_BUDGET's. A non-numeric or negative value is a misconfigured run, not a
#     decision (same fail-closed rule as VERI_REFACTOR_BUDGET): exit 2, a diagnostic on
#     stderr, and nothing on stdout, so a conductor mirroring stdout cannot mistake a
#     misconfigured run for a real status. `leaf-ok` (case 1's stub) is never reached, so a
#     leaf that ran would put its own output on stdout ahead of any real status — the
#     probe refactor-budget.test.sh's case 3 already uses.
kp_work="$work/kill-poll-bad"; mkdir -p "$kp_work"
kp_problems=()
for bad in two -1; do
  kp_out="$(mktemp)" kp_err="$(mktemp)"
  ( cd "$kp_work" && env VERI_KILL_POLL="$bad" "$SUP" badpoll "$stub/leaf-ok" ) >"$kp_out" 2>"$kp_err"
  kp_code=$?
  [[ "$kp_code" == 2 ]] ||
    kp_problems+=("VERI_KILL_POLL=$bad: want exit 2, got $kp_code")
  [[ ! -s "$kp_out" ]] ||
    kp_problems+=("VERI_KILL_POLL=$bad: want no status on stdout, got: $(cat "$kp_out")")
  [[ -s "$kp_err" ]] ||
    kp_problems+=("VERI_KILL_POLL=$bad: want a diagnostic on stderr, got nothing")
  rm -f "$kp_out" "$kp_err"
done
{ [[ "${#kp_problems[@]}" -eq 0 ]]; } && ok \
  || no "a non-numeric or negative VERI_KILL_POLL exits 2 with a diagnostic and no status on stdout (${kp_problems[*]})"

# 33. the silence the supervisor measures is the silence this suite INJECTED, whatever real
#     time did in between (issue #300). Case 4's premise is that a slow-but-alive leaf's
#     heartbeat never depends on real elapsed time; this case is that premise made
#     observable. The leaf writes one line, then makes its own progress log look 60 REAL
#     seconds old — the cheap stand-in for a scheduling delay, no wait involved — and only
#     then injects 1 s of silence onto the clock, well inside its 5 s window. A supervisor
#     reading the injected clock sees 1 s and lets the leaf finish; one that reads any real
#     elapsed time at all sees ~61 s and kills it as stuck. `.tdd/reallag.log` is the log
#     `sup reallag` gives it, named here because the leaf has to reach its own log to age it.
cat > "$stub/leaf-real-lag" <<'L'
#!/bin/sh
: > .test-clock-reads
echo "leaf: starting"
python3 -c '
import os, sys
s = os.stat(sys.argv[1])
os.utime(sys.argv[1], (s.st_atime - 60, s.st_mtime - 60))' .tdd/reallag.log
clock-jump 1
await-poll
echo "leaf: done"; exit 0
L
chmod +x "$stub/leaf-real-lag"
sup reallag 5 30 leaf-real-lag
{ [[ "$code" == 0 ]] && [[ "$out" == *'done'* ]]; } && ok \
  || no "60s of real lag on the leaf's log is not silence: 1s injected against a 5s window → success (code=$code want 0, err=$(cat "$work/err"))"

# 34. the discipline cases 4 and 33 rest on is guarded rather than merely practised (issue
#     #300): a case here that reaches its silence by real waiting instead of by an injected
#     clock jump fails this run, named. Case 4 failed about one run in ten for exactly that
#     shape — a silence produced by real elapsed time, read as a stall when a scheduling delay
#     landed near a whole-second boundary — and the fix is only as durable as the next stub
#     leaf written without a jump, which nothing in a green run would otherwise say.
#
#     The audit is asked twice, which is what makes the answer mean anything. Over THIS suite
#     as committed it must be silent: the real waits still here — case 30's leaf, which must
#     be a live process for a signal to be sent to it, and the kill-grace polls that watch an
#     OS fact rather than the clock — are deliberate, so silence over this file says its
#     exemption table records them with a reason rather than that the audit found nothing to
#     look at. Over a planted suite holding two stub leaves it must speak: one jumps the clock
#     before going quiet, one simply waits, and only the second is a silence real time
#     produces. Naming both, or neither, would pass a rule that says nothing.
#
#     The wait verb is assembled from two halves below rather than written out. A line of this
#     suite spelling it inside a stub-leaf body is the very thing the audit exists to catch,
#     and a case that tripped its own subject would leave the rule unachievable —
#     docs-read-guard.test.sh keeps its own subject's path out of its source for the same
#     reason.
AUDIT="$HERE/real-clock-audit.sh"
audit_work="$work/clock-audit"
mkdir -p "$audit_work"
audit_problems=()
wait_verb="sl""eep"

planted="$audit_work/planted.test.sh"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  "cat > \"\$stub/leaf-jumped\" <<'L'" \
  '#!/bin/sh' \
  "echo \"leaf: starting\"; clock-jump 4; $wait_verb 60" \
  'L' \
  "cat > \"\$stub/leaf-real-silence\" <<'L'" \
  '#!/bin/sh' \
  "echo \"leaf: starting\"; $wait_verb 4; echo \"leaf: back\"" \
  'L' \
  'sup jumped 1 30 leaf-jumped' \
  'sup realsilence 3 30 leaf-real-silence' \
  > "$planted"

if [[ ! -x "$AUDIT" ]]; then
  audit_problems+=("no executable clock audit at $AUDIT")
else
  audit_self_out="$("$AUDIT" "$HERE/supervise.test.sh" 2>&1)"
  audit_self_code=$?
  # What a problem line quotes: the audit's own output with its newlines turned into `/`, so a
  # finding over several lines stays on the one FAIL line this suite prints. The matches below
  # read the unflattened capture, which is what the audit actually said.
  audit_self_said="${audit_self_out//$'\n'//}"
  [[ "$audit_self_code" == 0 ]] ||
    audit_problems+=("over this suite as committed the audit exited $audit_self_code, want 0: $audit_self_said")
  [[ -z "$audit_self_out" ]] ||
    audit_problems+=("over this suite as committed the audit named something, want nothing: $audit_self_said")

  audit_out="$("$AUDIT" "$planted" 2>&1)"
  audit_code=$?
  audit_said="${audit_out//$'\n'//}"
  [[ "$audit_code" == 1 ]] ||
    audit_problems+=("over the planted suite the audit exited $audit_code, want 1: $audit_said")
  [[ "$audit_out" == *"planted.test.sh"* ]] ||
    audit_problems+=("over the planted suite the audit does not name the file it read: $audit_said")
  [[ "$audit_out" == *"leaf-real-silence"* ]] ||
    audit_problems+=("over the planted suite the audit does not name leaf-real-silence, whose silence is real waiting: $audit_said")
  [[ "$audit_out" != *"leaf-jumped"* ]] ||
    audit_problems+=("over the planted suite the audit names leaf-jumped, which injects its silence onto the clock: $audit_said")
fi
{ [[ "${#audit_problems[@]}" -eq 0 ]]; } && ok \
  || no "a stub leaf whose silence is real waiting is named by the clock audit, a deliberate real-clock dependence recorded with a reason is not (${audit_problems[*]})"

# 35. a killed-stuck leaf's attempt is preserved — the one the supervisor RELAUNCHED past as
#     well as the one it finally gave up on (issue #409). Both are evidence a human will want:
#     the tree the leaf left is never committed to the work branch, and `.tdd/develop-red.log`
#     is truncated at the top of every attempt (supervise.sh's `: > "$log"`), so the first
#     attempt's work and output exist nowhere else the moment the relaunch begins. The
#     supervisor is the only place either can be caught: it is where a kill is decided, and the
#     retry loop is its own.
#
#     Both halves are asserted in one case because "both" is the whole of the criterion: a
#     preservation written only at the foot of the script would leave the relaunched attempt
#     lost, and one written only before the relaunch would lose the attempt the run ended on.
#     Two refs and two copies is what says they were kept apart rather than one overwriting the
#     other under a shared name.
#
#     What each preserved thing IS, rather than merely that something was written: the leaf
#     counts its own attempts into a tracked `attempts.txt` and names the number in its output,
#     so the ref for the first attempt holds a one-line file and the second a two-line one, and
#     each preserved log carries its own attempt's line. A preservation that snapshotted the
#     same moment twice would satisfy a count and fail here.
#
#     The refs are counted and read rather than named, and the copies are found by the prefix
#     preserve-attempt.sh's own contract builds (`<step>-<phase>-<attempt>-<mark>`): how the two
#     attempts are told apart inside that name, and which mark ends it, are that script's to say
#     and preserve-attempt.test.sh's to pin. The numbers are sorted before comparison for the
#     same reason — the order `for-each-ref` and `ls` return is alphabetical, not chronological.
#
#     A real git repository, since the subject is a real ref: one commit, then the leaf's work on
#     top of it, the shape a step is killed in. `.tdd/` is ignored the way ensure-run-state-ignored.sh
#     installs it in a real run, and `.test-clock*` beside it — the injected clock's own history,
#     written into the leaf's cwd, which is nothing the preserved tree should carry.
#
#     Not through `sup_run`, for case 13's reason: that helper pins VERI_STUCK_RETRIES=0 and
#     there would be no relaunch to preserve. `env -u` instead, so the DEFAULT budget of one
#     retry produces exactly two attempts and the shell that ran `make test` cannot change how
#     many.
preserve_work="$work/preserve"
preserve_issue=409
preserve_step=6
preserve_window=1
mkdir -p "$preserve_work"
git init -q -b main "$preserve_work" >/dev/null 2>&1
git -C "$preserve_work" config user.name veri
git -C "$preserve_work" config user.email veri@example.test
printf '.tdd/\n.test-clock*\n' > "$preserve_work/.gitignore"
printf 'the step this leaf never finished\n' > "$preserve_work/src.txt"
git -C "$preserve_work" add -A >/dev/null 2>&1
git -C "$preserve_work" commit -q -m "initial" >/dev/null 2>&1

# The leaf that hangs on EVERY attempt, counting itself into the tree it leaves behind. Written
# here rather than beside the leaf-* stubs at the top of the file, for case 16's reason: next to
# the case whose premise it is. `leaf-hang` cannot stand in — it leaves both attempts byte-
# identical, so nothing could tell one preserved tree from the other.
cat > "$stub/leaf-hang-counting" <<'L'
#!/bin/sh
echo run >> attempts.txt
echo "leaf: attempt $(wc -l < attempts.txt | tr -d ' ')"
clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60
L
chmod +x "$stub/leaf-hang-counting"

( cd "$preserve_work" && env -u VERI_STUCK_RETRIES \
    VERI_ISSUE="$preserve_issue" VERI_STEP="$preserve_step" \
    VERI_HEARTBEAT="$preserve_window" VERI_TIMEOUT=30 VERI_POLL=0.02 VERI_KILL_POLL=0.01 \
    "$SUP" develop-red "$stub/leaf-hang-counting" ) >/dev/null 2>&1
preserve_code=$?

# Each fact read once, into the variable the assertion and the failure message share — every
# case above this one's shape.
preserve_refs="$(git -C "$preserve_work" for-each-ref --format='%(refname)' \
  "refs/veri/attempts/$preserve_issue/$preserve_step/" 2>/dev/null)"
preserve_ref_count="$(printf '%s\n' "$preserve_refs" | grep -c . || true)"
# How many attempts each preserved tree had seen — the line count of the file the leaf appends
# to once per attempt. `xargs` joins the sorted numbers into one word-spaced line and answers
# the empty string when there is nothing, which is what an unpreserved run reports.
preserve_trees="$(while read -r ref; do
    [[ -n "$ref" ]] || continue
    git -C "$preserve_work" show "$ref:attempts.txt" 2>/dev/null | grep -c . || true
  done <<< "$preserve_refs" | sort | xargs)"
# The preserved logs, found by the prefix the step and the leaf's name build. `ls` rather than a
# glob into an array, case 27 of verify.test.sh's reason: an unmatched glob comes back as the
# pattern itself, which reads as a found file.
preserve_copies="$(ls "$preserve_work/.tdd/attempts/$preserve_step-develop-red-"*.log 2>/dev/null || true)"
preserve_copy_count="$(printf '%s\n' "$preserve_copies" | grep -c . || true)"
preserve_logged="$(while read -r f; do
    [[ -n "$f" ]] || continue
    head -1 < <(grep -oE 'leaf: attempt [0-9]+' "$f") | grep -oE '[0-9]+' || true
  done <<< "$preserve_copies" | sort | xargs)"
{ [[ "$preserve_code" == 2 ]] \
  && [[ "$preserve_ref_count" == 2 ]] && [[ "$preserve_trees" == "1 2" ]] \
  && [[ "$preserve_copy_count" == 2 ]] && [[ "$preserve_logged" == "1 2" ]]; } && ok \
  || no "a killed-stuck leaf preserves the relaunched attempt and the final one, each as its own tree and log (code=$preserve_code want 2; refs=$preserve_ref_count want 2 under refs/veri/attempts/$preserve_issue/$preserve_step/, attempts per tree='$preserve_trees' want '1 2'; log copies=$preserve_copy_count want 2, attempt each logged='$preserve_logged' want '1 2')"


# 36. a verification whose leaf is working while the launch wrapper around it stays silent is
#     not killed for that silence (issue #415). Routing the verifier through this supervisor put
#     a `supervise.sh verdict-<phase>` around SKILL.md's `bash -c` wrapper, and that wrapper
#     sends verify.sh's stdout to `.tdd/verify-<phase>.reason` and its stderr to
#     `.tdd/verify-<phase>.err` — so it writes nothing at all to the log THIS supervision
#     watches, however hard the verifier leaf inside it is working. A heartbeat window measured
#     over that silence kills every verification that outlives it, which would make the fix for
#     a stalled wait a new way to lose a working one: the leaf inside is already supervised
#     under `verify-<phase>`, and supervising the wrapper must add no second window.
#
#     The stub is that wrapper in miniature: the verification's progress goes to
#     `.tdd/verify-red.log`, where the `supervise.sh verify-red` inside verify.sh puts it, the
#     verdict text to the reason file, and verify.sh's own verdict code to
#     `.tdd/verdict-red.exit`, the record the conductor's wait reads. Both land only if the
#     wrapper is allowed to reach its last line, which is what this case is asking.
#     Case 4's arithmetic, one level out: six seconds of injected life against a two-second
#     window, never more than one second between the inner leaf's writes, so the verification
#     survives only if the wrapper's own silence is not what is measured.
#
#     A run directory of its own, the shape case 35 takes and for the same kind of reason:
#     cases 23 to 27 run under the name `verify-red` in `$work`, so the log this leaf's progress
#     lands in already exists there, and an earlier case's writes to it must not be able to
#     stand in for progress this one made.
cat > "$stub/leaf-quiet-wrapper" <<'L'
#!/bin/sh
: > .test-clock-reads
mkdir -p .tdd
for i in 1 2 3 4 5 6; do
  echo "verifier: tick $i" >> .tdd/verify-red.log
  clock-jump 1; await-poll
done
printf 'The test pins the criterion as observable behavior.\n' > .tdd/verify-red.reason
echo 0 > .tdd/verdict-red.exit
exit 0
L
chmod +x "$stub/leaf-quiet-wrapper"

quiet_wrapper_work="$work/quiet-wrapper"
mkdir -p "$quiet_wrapper_work"
( cd "$quiet_wrapper_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=2 VERI_TIMEOUT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" verdict-red "$stub/leaf-quiet-wrapper" ) \
  > /dev/null 2> "$quiet_wrapper_work/err"
quiet_wrapper_code=$?
quiet_wrapper_recorded="$(cat "$quiet_wrapper_work/.tdd/verdict-red.exit" 2>/dev/null || echo '<missing>')"
quiet_wrapper_reason="$(cat "$quiet_wrapper_work/.tdd/verify-red.reason" 2>/dev/null)"
{ [[ "$quiet_wrapper_code" == 0 ]] && [[ "$quiet_wrapper_recorded" == 0 ]] \
  && [[ "$quiet_wrapper_reason" == 'The test pins the criterion as observable behavior.' ]]; } && ok \
  || no "a working verification is not killed for its wrapper's silence: 6s of inner progress against a 2s window → the verdict the verifier recorded (code=$quiet_wrapper_code want 0, recorded=$quiet_wrapper_recorded want 0, reason='$quiet_wrapper_reason' want the verifier's own line, err=$(cat "$quiet_wrapper_work/err"))"

# 37. a launch is refused while a leaf supervised under a DIFFERENT name is still alive in the
#     same worktree (issue #471). In #446 the conductor started `verify-green` while
#     `revise-green-1` was still running, and the two wrote one tree at once; nothing in the
#     launcher looked past its own leaf's pidfile. So the second supervision must answer
#     exit 2 — no answer could be obtained, the plumbing's code — start no leaf of its own,
#     and say on stderr which leaf owns the worktree and under which pid.
#
#     The pid is the first supervisor's own, the value `.tdd/<name>.pid` carries (case 29) and
#     wait-leaf.sh reads as the leaf's. The first supervisor is `exec`ed in the background,
#     case 29's shape, so `$!` is supervise.sh itself; its leaf is case 30's own stub, which
#     records its pid and `exec`s into a long sleep, so it is alive for as long as the case
#     needs it — and is already recorded, with that reason, in the clock audit's exemptions. The second
#     stub only leaves a marker, so "no second leaf started" is a file that must not exist. The
#     first supervisor is sent TERM afterwards, whose handler takes the leaf down with it (case
#     30), and a leaf that did survive is killed here. A run directory of its own, for case
#     12's reason.
owner_work="$work/live-owner"
mkdir -p "$owner_work"
cat > "$stub/leaf-second" <<'L'
#!/bin/sh
: > second-ran
exit 0
L
chmod +x "$stub/leaf-second"
( cd "$owner_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
owner_sup=$!
for _ in $(seq 1 50); do [[ -s "$owner_work/leaf-pid" ]] && break; sleep 0.1; done
owner_leaf="$(tr -d '[:space:]' < "$owner_work/leaf-pid" 2>/dev/null)"
( cd "$owner_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" verify-green "$stub/leaf-second" ) >/dev/null 2>"$owner_work/err"
owner_code=$?
owner_second="no"; [[ -e "$owner_work/second-ran" ]] && owner_second="yes"
owner_err="$(cat "$owner_work/err")"
kill -TERM "$owner_sup" 2>/dev/null
wait "$owner_sup"
if [[ -n "$owner_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$owner_leaf" 2>/dev/null || break; sleep 0.1; done
  kill -0 "$owner_leaf" 2>/dev/null && kill -KILL "$owner_leaf" 2>/dev/null
fi
{ [[ -n "$owner_leaf" ]] && [[ "$owner_code" == 2 ]] && [[ "$owner_second" == no ]] \
  && [[ "$owner_err" == *revise-green-1* ]] && [[ "$owner_err" =~ (^|[^0-9])$owner_sup([^0-9]|$) ]]; } && ok \
  || no "#471: a launch under one name is refused while a leaf supervised under another name is alive in the same worktree (first leaf pid=${owner_leaf:-<never started>}; code=$owner_code want 2, second leaf ran=$owner_second want no, stderr='$owner_err' want it to name revise-green-1 and pid $owner_sup)"

# 38. the same refusal when the live leaf and the new launch share a NAME (issue #471): a
#     second `revise-green-1` started while the first is still alive in the worktree. The
#     name is no licence — `.tdd/<name>.pid` is the one trace the two would share, and a
#     second supervision under that name would overwrite it and start a second writer on the
#     same tree. So: exit 2, no second leaf, stderr naming the live leaf and its pid. Case
#     37's shape and stubs throughout, with its cleanup; a run directory of its own.
same_work="$work/live-owner-same-name"
mkdir -p "$same_work"
( cd "$same_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
same_sup=$!
for _ in $(seq 1 50); do [[ -s "$same_work/leaf-pid" ]] && break; sleep 0.1; done
same_leaf="$(tr -d '[:space:]' < "$same_work/leaf-pid" 2>/dev/null)"
( cd "$same_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-second" ) >/dev/null 2>"$same_work/err"
same_code=$?
same_second="no"; [[ -e "$same_work/second-ran" ]] && same_second="yes"
same_err="$(cat "$same_work/err")"
kill -TERM "$same_sup" 2>/dev/null
wait "$same_sup"
if [[ -n "$same_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$same_leaf" 2>/dev/null || break; sleep 0.1; done
  kill -0 "$same_leaf" 2>/dev/null && kill -KILL "$same_leaf" 2>/dev/null
fi
{ [[ -n "$same_leaf" ]] && [[ "$same_code" == 2 ]] && [[ "$same_second" == no ]] \
  && [[ "$same_err" == *revise-green-1* ]] && [[ "$same_err" =~ (^|[^0-9])$same_sup([^0-9]|$) ]]; } && ok \
  || no "#471: a launch is refused while a leaf supervised under the same name is alive in the same worktree (first leaf pid=${same_leaf:-<never started>}; code=$same_code want 2, second leaf ran=$same_second want no, stderr='$same_err' want it to name revise-green-1 and pid $same_sup)"

# 39. the refusal survives SKILL.md's launch recipe (issue #471). Every recipe begins
#     `rm -f .tdd/<name>.exit .tdd/<name>.pid`, and for a revise relaunch under the live
#     leaf's own name that line deletes the very pidfile the live supervision wrote — the
#     trace #446's conductor removed before launching over a running leaf. So the record the
#     refusal reads must be one that line does not touch: after the rm, the relaunch is still
#     exit 2, starts no leaf, and names the live leaf and its pid. Case 38's shape and stubs,
#     with the recipe's rm run between the two launches; a run directory of its own.
rm_work="$work/live-owner-after-rm"
mkdir -p "$rm_work"
( cd "$rm_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
rm_sup=$!
for _ in $(seq 1 50); do [[ -s "$rm_work/leaf-pid" ]] && break; sleep 0.1; done
rm_leaf="$(tr -d '[:space:]' < "$rm_work/leaf-pid" 2>/dev/null)"
( cd "$rm_work" && rm -f .tdd/revise-green-1.exit .tdd/revise-green-1.pid )
( cd "$rm_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-second" ) >/dev/null 2>"$rm_work/err"
rm_code=$?
rm_second="no"; [[ -e "$rm_work/second-ran" ]] && rm_second="yes"
rm_err="$(cat "$rm_work/err")"
kill -TERM "$rm_sup" 2>/dev/null
wait "$rm_sup"
if [[ -n "$rm_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$rm_leaf" 2>/dev/null || break; sleep 0.1; done
  kill -0 "$rm_leaf" 2>/dev/null && kill -KILL "$rm_leaf" 2>/dev/null
fi
{ [[ -n "$rm_leaf" ]] && [[ "$rm_code" == 2 ]] && [[ "$rm_second" == no ]] \
  && [[ "$rm_err" == *revise-green-1* ]] && [[ "$rm_err" =~ (^|[^0-9])$rm_sup([^0-9]|$) ]]; } && ok \
  || no "#471: a launch is still refused after the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid while the first leaf is alive (first leaf pid=${rm_leaf:-<never started>}; code=$rm_code want 2, second leaf ran=$rm_second want no, stderr='$rm_err' want it to name revise-green-1 and pid $rm_sup)"

# 40. a record left by a supervised leaf whose process is gone refuses nothing (issue #471).
#     A supervisor that dies — SIGKILL, which no handler sees — never gets to clear what it
#     recorded, so the worktree keeps a trace of a leaf that is no longer there. That trace
#     must not become a permanent block: the next launch runs its leaf and answers as it
#     would have with no record at all. Case 37's stubs: the first supervisor is KILLed rather
#     than TERMed, so its own cleanup cannot run, and its leaf is killed after it, so neither
#     pid is alive. The record is read before the relaunch so the case cannot pass on a
#     worktree that was never claimed. The relaunch is the revise relaunch's shape: the same
#     name, after SKILL.md's pre-launch rm. A run directory of its own.
dead_work="$work/dead-owner"
mkdir -p "$dead_work"
( cd "$dead_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
dead_sup=$!
for _ in $(seq 1 50); do [[ -s "$dead_work/leaf-pid" ]] && break; sleep 0.1; done
dead_leaf="$(tr -d '[:space:]' < "$dead_work/leaf-pid" 2>/dev/null)"
kill -KILL "$dead_sup" 2>/dev/null
wait "$dead_sup" 2>/dev/null
if [[ -n "$dead_leaf" ]]; then
  kill -KILL "$dead_leaf" 2>/dev/null
  for _ in $(seq 1 20); do kill -0 "$dead_leaf" 2>/dev/null || break; sleep 0.1; done
fi
dead_record="$(cat "$dead_work/.tdd/leaf.owner" 2>/dev/null || echo '<missing>')"
( cd "$dead_work" && rm -f .tdd/revise-green-1.exit .tdd/revise-green-1.pid )
( cd "$dead_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-second" ) >/dev/null 2>"$dead_work/err"
dead_code=$?
dead_second="no"; [[ -e "$dead_work/second-ran" ]] && dead_second="yes"
{ [[ -n "$dead_leaf" ]] && [[ "$dead_record" == "$dead_sup revise-green-1" ]] \
  && [[ "$dead_code" == 0 ]] && [[ "$dead_second" == yes ]]; } && ok \
  || no "#471: a record left by a supervised leaf whose process is gone does not refuse the next launch (first leaf pid=${dead_leaf:-<never started>}; record='$dead_record' want '$dead_sup revise-green-1'; code=$dead_code want 0, second leaf ran=$dead_second want yes, stderr='$(cat "$dead_work/err")')"

# 41. a launch after the previous supervised leaf FINISHED runs as today (issue #471): the
#     ownership rule refuses only a live leaf, so the ordinary sequence of a run is untouched.
#     A leaf finishes; SKILL.md's recipe removes its files and relaunches it under the same
#     name, the revise relaunch's shape; that one finishes and a leaf under a different name
#     follows. Each launch exits 0 and runs its leaf, which appends its argument to `ran`, so
#     the file must read the three in order. The record is read after the first launch so the
#     case cannot pass on a worktree that was never claimed. A run directory of its own.
done_work="$work/finished-owner"
mkdir -p "$done_work"
cat > "$stub/leaf-mark" <<'L'
#!/bin/sh
echo "$1" >> ran
exit 0
L
chmod +x "$stub/leaf-mark"
( cd "$done_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-mark" first ) >/dev/null 2>"$done_work/err1"
done_code1=$?
done_record="$(cat "$done_work/.tdd/leaf.owner" 2>/dev/null || echo '<missing>')"
( cd "$done_work" && rm -f .tdd/revise-green-1.exit .tdd/revise-green-1.pid )
( cd "$done_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-mark" second ) >/dev/null 2>"$done_work/err2"
done_code2=$?
( cd "$done_work" && rm -f .tdd/verify-green.exit .tdd/verify-green.pid )
( cd "$done_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" verify-green "$stub/leaf-mark" third ) >/dev/null 2>"$done_work/err3"
done_code3=$?
done_ran="$(tr '\n' ' ' < "$done_work/ran" 2>/dev/null)"
{ [[ "$done_record" == *' revise-green-1' ]] && [[ "$done_code1" == 0 ]] && [[ "$done_code2" == 0 ]] \
  && [[ "$done_code3" == 0 ]] && [[ "$done_ran" == 'first second third ' ]]; } && ok \
  || no "#471: a launch after the previous supervised leaf finished runs as today, under the same name and a different one (record='$done_record' want '<pid> revise-green-1'; codes=$done_code1/$done_code2/$done_code3 want 0/0/0; ran='$done_ran' want 'first second third '; stderr='$(cat "$done_work/err2" "$done_work/err3" 2>/dev/null)')"

# 42. a supervised launch made from INSIDE a live supervised leaf is not refused (issue #471):
#     SKILL.md's verify recipe supervises `verdict-<phase>` around run-verdict.sh, and verify.sh
#     inside it launches the verifier through supervise.sh as `verify-<phase>` — so while the
#     wrapper is alive, the verifier's own launch is the one leaf of the worktree, not a second
#     writer over a live one. The wrapper here is a stub that does what verify.sh does: it
#     launches `verify-green` through the supervisor under test and records that launch's exit
#     code. Both must exit 0, the inner leaf must run, and nothing may be refused on stderr.
#     Case 41's leaf-mark stub; a run directory of its own.
nest_work="$work/nested-verifier"
mkdir -p "$nest_work"
cat > "$stub/leaf-verdict-wrapper" <<'L'
#!/bin/sh
"$NEST_SUP" verify-green "$NEST_LEAF" inner 2> inner-err
echo $? > inner-code
exit 0
L
chmod +x "$stub/leaf-verdict-wrapper"
( cd "$nest_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 NEST_SUP="$SUP" NEST_LEAF="$stub/leaf-mark" \
    "$SUP" verdict-green "$stub/leaf-verdict-wrapper" ) >/dev/null 2>"$nest_work/err"
nest_code=$?
nest_inner="$(cat "$nest_work/inner-code" 2>/dev/null || echo '<missing>')"
nest_ran="$(tr '\n' ' ' < "$nest_work/ran" 2>/dev/null)"
nest_err="$(cat "$nest_work/err" "$nest_work/inner-err" 2>/dev/null)"
{ [[ "$nest_code" == 0 ]] && [[ "$nest_inner" == 0 ]] && [[ "$nest_ran" == 'inner ' ]] \
  && [[ "$nest_err" != *refusing* ]]; } && ok \
  || no "#471: a verify-green launch made from inside a live verdict-green supervision is not refused (wrapper code=$nest_code want 0; inner code=$nest_inner want 0; ran='$nest_ran' want 'inner '; stderr='$nest_err' want no refusal)"

# woke_with_own_exit <name> <case> — the suspend cases' one verdict: the supervisor reported
# the leaf's own failure (exit 1, 3 in <name>.rc) after it woke, never killed-stuck (exit 2).
woke_with_own_exit() {
  local susp_rc
  susp_rc="$(cat "$work/.tdd/$1.rc" 2>/dev/null || echo '<missing>')"
  rm -f "$work/.test-suspended"
  { [[ "$code" == 1 ]] && [[ "$susp_rc" == 3 ]] && [[ "$out" == *'awake again'* ]]; } && ok \
    || no "$2 (code=$code want 1, rc=$susp_rc want 3, err=$(cat "$work/err"))"
}

# 43. time the machine spends SUSPENDED is not leaf silence (issue #472). A laptop asleep for an
#     hour read as a leaf silent for an hour, because the heartbeat was measured on the wall
#     clock: the leaf was killed as stuck and its retries spent asleep too. The clock here
#     simulates a suspend with no real sleep: `clock-suspend <s>` moves the wall clock (`date
#     +%s`, and the offset the `stat` stub adds) by <s> while the awake clock does not move,
#     and `clock-jump`, unchanged, is awake time — both clocks move. The awake clock is the
#     executable VERI_AWAKE_CLOCK names, which prints whole awake seconds: this stub answers
#     real time plus every jump minus every suspend. The leaf writes a line, is suspended one
#     second past its 2 s window with nothing written, waits for the supervisor to read the
#     clock twice across that gap, then writes again and exits 3 — so the supervisor must
#     report the leaf's own failure (exit 1, 3 in .rc), never killed-stuck (exit 2).
cat > "$stub/clock-suspend" <<'C'
#!/bin/sh
clock-jump "$1" && echo "$1" >> .test-suspended
C
cat > "$stub/leaf-suspended" <<'L'
#!/bin/sh
: > .test-clock-reads
echo "leaf: starting"
clock-suspend "$(( ${VERI_HEARTBEAT:-999} + 1 ))"
await-poll; await-poll
echo "leaf: awake again"; exit 3
L
chmod +x "$stub/clock-suspend" "$stub/leaf-suspended"
rm -f "$work/.test-suspended"
sup suspended 2 30 leaf-suspended
woke_with_own_exit suspended "#472: a leaf silent only across a 3s suspend against a 2s heartbeat is not killed and finishes with its own exit code"

# 44. a run nobody configured measures awake time too (issue #472). Case 43 names the awake
#     clock; here VERI_AWAKE_CLOCK is unset, so the supervisor must fall back to a REAL clock
#     that does not advance while the machine is suspended. The stubbed `date` and `stat` are
#     the wall clock and jump past the window; the real awake clock the supervisor reads does
#     not see that jump, which is exactly what a suspend looks like to it. The same leaf as
#     case 43 must therefore finish with its own exit code, never killed-stuck.
rm -f "$work/.test-suspended" "$work/.tdd/suspended.rc"
unset VERI_AWAKE_CLOCK
sup suspended 2 30 leaf-suspended
export VERI_AWAKE_CLOCK="$stub/awake-clock"
woke_with_own_exit suspended "#472: with VERI_AWAKE_CLOCK unset, a leaf silent only across a 3s suspend against a 2s heartbeat is not killed and finishes with its own exit code"

# 45. time the machine spends SUSPENDED does not count toward the hard timeout either (issue
#     #472). The same injected clock as case 43, with the windows swapped: a 30 s heartbeat the
#     leaf never nears, and a 2 s VERI_TIMEOUT the leaf's suspend of one second past it would
#     cross on the wall clock while its awake time stays well under it. The leaf waits for the
#     supervisor to read the clock twice across the suspend, then exits 3 — so the supervisor
#     must report the leaf's own failure (exit 1, 3 in .rc), never killed-stuck (exit 2).
cat > "$stub/leaf-suspended-timeout" <<'L'
#!/bin/sh
: > .test-clock-reads
echo "leaf: starting"
clock-suspend "$(( ${VERI_TIMEOUT:-999} + 1 ))"
await-poll; await-poll
echo "leaf: awake again"; exit 3
L
chmod +x "$stub/leaf-suspended-timeout"
rm -f "$work/.test-suspended" "$work/.tdd/suspended-timeout.rc"
sup suspended-timeout 30 2 leaf-suspended-timeout
woke_with_own_exit suspended-timeout "#472: a leaf whose run spans a 3s suspend past a 2s VERI_TIMEOUT, awake time under it, is not killed for the timeout and finishes with its own exit code"

# 46. a leaf silent while the machine is AWAKE is still killed at the same threshold as today
#     (issue #472). Cases 43 to 45 take suspended time out of the windows; this one pins that
#     awake silence is not taken out with it. The injected clock never suspends here: every
#     second is a `clock-jump`, which moves the awake clock and the wall clock together. The
#     leaf writes a line, is silent one second against a 2 s window — inside it, so it must
#     survive, and marks ./.test-inside-window once the supervisor has polled across that — then
#     is silent two more, three in all, past the window, and hangs. The supervisor must kill it
#     as stuck on the heartbeat (exit 2, `no heartbeat … (window 2s)`) and not before the mark.
cat > "$stub/leaf-awake-silent" <<'L'
#!/bin/sh
: > .test-clock-reads
echo "leaf: starting"
clock-jump 1
await-poll; await-poll
: > .test-inside-window
clock-jump 2
sleep 60; echo "unreachable"
L
chmod +x "$stub/leaf-awake-silent"
rm -f "$work/.test-suspended" "$work/.test-inside-window"
sup awake-silent 2 30 leaf-awake-silent
awake_inside="$([[ -e "$work/.test-inside-window" ]] && echo yes || echo no)"
rm -f "$work/.test-inside-window"
{ [[ "$code" == 2 ]] && [[ "$awake_inside" == yes ]] \
  && grep -E 'no heartbeat for [0-9]+s \(window 2s\)' "$work/err" > /dev/null; } && ok \
  || no "#472: a leaf silent 1s then 3s of awake time (no suspend) against a 2s heartbeat survives the first and is killed as stuck on the heartbeat (code=$code want 2, survived inside the window=$awake_inside want yes, err=$(cat "$work/err"))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
