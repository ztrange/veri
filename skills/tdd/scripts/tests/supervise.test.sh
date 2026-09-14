#!/usr/bin/env bash
# Tests for scripts/supervise.sh — the programmatic supervisor, the deterministic
# robustness core (#4). Every leaf is launched through it; it tells a slow-but-alive leaf
# (heartbeat: progress-log activity within a window) from a hung one (silent past the
# window), caps the wall clock with a hard timeout, kills a stuck leaf, and reports a
# clear status (success / failure / killed-stuck) plus the captured output.
#
# Driven against STUB LEAF SCRIPTS (no claude): exit-0, exit-nonzero, hang, slow-but-alive,
# runaway (alive but over the hard timeout), and flaky (hangs once, then succeeds).
# Timings are compressed via the env knobs VERI_HEARTBEAT / VERI_TIMEOUT / VERI_POLL so the
# suite stays fast.
#
# Status contract: exit 0 success · 1 leaf-failure · 2 killed-stuck.
#
# Run: scripts/tests/supervise.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUP="$HERE/../supervise.sh"
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
#!/usr/bin/env bash
echo "leaf: starting"; echo "leaf: did the work"; exit 0
L
# exit-nonzero: writes progress, fails.
cat > "$stub/leaf-fail" <<'L'
#!/usr/bin/env bash
echo "leaf: starting"; echo "leaf: blew up"; exit 3
L
# hang: one line of progress, then silent forever (no heartbeat).
cat > "$stub/leaf-hang" <<'L'
#!/usr/bin/env bash
echo "leaf: starting"; sleep 60; echo "unreachable"
L
# slow-but-alive: emits a heartbeat line every 0.3s for ~1.8s, then finishes.
cat > "$stub/leaf-slow" <<'L'
#!/usr/bin/env bash
for i in 1 2 3 4 5 6; do echo "leaf: tick $i"; sleep 0.3; done
echo "leaf: done"; exit 0
L
# runaway: stays alive AND keeps emitting (heartbeat fresh) but never exits — only the
# hard timeout can stop it.
cat > "$stub/leaf-runaway" <<'L'
#!/usr/bin/env bash
while true; do echo "leaf: busy"; sleep 0.2; done
L
# flaky: hangs (silent) the FIRST time it runs, succeeds the SECOND — the one leaf here that
# gets past its first attempt, which is what case 13 needs to watch a relaunch. The marker
# lives in cwd, which the supervisor preserves across attempts, so a run in a directory some
# earlier run already flaked in would succeed straight away and never be relaunched: case 13
# gives it a directory of its own for that reason as much as for the event log's.
cat > "$stub/leaf-flaky" <<'L'
#!/usr/bin/env bash
if [[ -e .retry-marker ]]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

# sup <name> <heartbeat> <timeout> <leaf> -> sets $out / $code (runs in $work)
# VERI_STUCK_RETRIES=0 is pinned, not inherited: every case here is about a single attempt,
# so the caller's environment must not be able to add retries (extra killed-stuck attempts
# would change both the stderr transcript and the suite's wall time).
sup() {
  local name="$1" hb="$2" to="$3" leaf="$4"
  out="$( cd "$work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT="$hb" VERI_TIMEOUT="$to" VERI_POLL=0.2 \
            "$SUP" "$name" "$stub/$leaf" 2>"$work/err" )"
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

# 4. a slow-but-alive leaf keeps its heartbeat and is allowed to finish → success.
#    Window is 2s, not 1s: the supervisor's clock is whole-second (`date +%s`), so a leaf
#    emitting every 0.3s can read as 1s "silent" at a second boundary. Real windows are
#    tens of seconds, where this granularity is irrelevant; the test honours it.
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
  hit="$(tr '\n' ' ' < "$1" | grep -oE "$2" | head -1)"
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
#     Waiting out a real 180s silence would cost the suite three minutes, so the clock is
#     injected rather than the wait endured. A `date` stub placed first on PATH answers
#     `+%s` with the real time plus $TEST_CLOCK_SKEW seconds; the log's mtime is read
#     through `stat`, which is NOT stubbed and so stays real. The supervisor computes
#     `silence = now - mtime_of(log)`, so it reads ~$TEST_CLOCK_SKEW from the very first
#     poll, and any window shorter than the skew fires at once. The hard timeout is
#     untouched by this: it compares two skewed readings (`t - t0`), so the constant skew
#     cancels and it still measures real elapsed seconds — which is what stops the arms
#     below hanging for 30s when no heartbeat kill comes.
#
#     Both arms hang the same leaf under a 200s skew, so the only difference between them
#     is where the window comes from: absent → the script's default, present → the caller's
#     number. `env -u VERI_HEARTBEAT` unsets it for the child rather than trusting the
#     suite's own environment to be clean, the same hermeticity case 8 insists on.
realdate="$(command -v date)"
cat > "$stub/date" <<D
#!/usr/bin/env bash
# \`date +%s\` answers \$TEST_CLOCK_SKEW seconds into the future; every other invocation is
# the real \`date\`, untouched. The real path is baked in at generation time because this
# stub sits on PATH as \`date\` itself and would otherwise re-exec into itself forever.
if [[ "\$*" == "+%s" ]]; then
  printf '%s\n' "\$(( \$("$realdate" +%s) + \${TEST_CLOCK_SKEW:-0} ))"
else
  exec "$realdate" "\$@"
fi
D
chmod +x "$stub/date"

# How far into the future the stub reports the clock, shared by both arms. It has to clear
# the largest window either arm expects — 180, the default — or the unset arm would poll a
# silence below its own window and never be killed at all, and the case would then read
# '<no-heartbeat-kill>' rather than a number. That constraint is the reason for the value,
# so it is named here next to it instead of being a bare 200 repeated at the call sites.
skew=200

# killed_window <name> <heartbeat|''> — hang a leaf under the skewed clock and echo the
# window the supervisor said it killed on, or '<no-heartbeat-kill>' if it died some other
# way (the hard timeout) or not at all. An empty second argument leaves VERI_HEARTBEAT
# unset in the child, which is the whole point of the first arm.
killed_window() {
  local name="$1" hb="${2-}"
  local -a hbenv
  if [[ -n "$hb" ]]; then hbenv=(VERI_HEARTBEAT="$hb"); else hbenv=(-u VERI_HEARTBEAT); fi
  ( cd "$work" && env "${hbenv[@]}" PATH="$stub:$PATH" TEST_CLOCK_SKEW="$skew" \
      VERI_STUCK_RETRIES=0 VERI_TIMEOUT=5 VERI_POLL=0.2 \
      "$SUP" "$name" "$stub/leaf-hang" >/dev/null 2>"$work/err-$name" )
  grep -oE 'window [0-9]+s' "$work/err-$name" | head -1 | grep -oE '[0-9]+' \
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
  ( cd "$dir" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 VERI_TIMEOUT=10 VERI_POLL=0.2 \
      "$@" ) >/dev/null 2>&1
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
    VERI_TIMEOUT=30 VERI_POLL=0.2 \
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
#!/usr/bin/env bash
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
#!/usr/bin/env bash
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
