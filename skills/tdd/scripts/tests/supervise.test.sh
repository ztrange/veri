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
# Every temp dir this suite makes is removed here, on the one path that runs however the
# script ends — including the Ctrl-C or the `make test` timeout that an `rm` at the foot of
# a case never reaches. `$launch_work`, `$retry_work` and `$exit_work` are cases 12, 13 and
# 14's and are made 270 lines down, so they are named with `${…:-}`: unset until then, and
# `rm -rf ""` is a silent no-op (POSIX: `-f` ignores an operand that does not exist), so an
# early exit cleans the ones that do exist.
trap 'rm -rf "$stub" "$work" "${launch_work:-}" "${retry_work:-}" "${exit_work:-}"' EXIT

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
#     A work directory of its own: the event log accumulates across a whole run, and every
#     case above shares `$work`, so a probe there would be reading whichever launch some
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

# Every variable this case owns is prefixed with the event it is about, and case 13's with
# its own — so the two read as the siblings they are, and each says at a glance which of
# `event_field`'s two event arguments its assertions are about.
launch_work="$(mktemp -d)"
# The name and the command are each written once, then used both to launch and to expect —
# the shape `$launch_cmd` already had. Spelled a second time in the assertion instead, the
# name could drift from the launched one and the case would go green on a leaf it never ran;
# and the expected attempt below is 2 only because THIS name ends in `-2`.
launch_name=revise-green-2
launch_cmd=(env VERI_TIMEOUT=1200 "$stub/leaf-ok")
( cd "$launch_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 VERI_TIMEOUT=10 VERI_POLL=0.2 \
    "$SUP" "$launch_name" "${launch_cmd[@]}" ) >/dev/null 2>&1
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

retry_work="$(mktemp -d)"
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

exit_work="$(mktemp -d)"
exit_window=2

# exit_run <arm> <heartbeat> <leaf> — supervise one leaf in its own directory under
# $exit_work, named for the arm. The leaf is called `develop-red` in every arm: leaf-role.sh
# has to be able to read the name or nothing is logged at all (supervise.sh:141-154), and
# nothing in this case is about which name it is. The hard timeout is well clear of every
# arm, so the stuck arm dies on the heartbeat and its cause says so.
exit_run() {
  mkdir -p "$exit_work/$1"
  ( cd "$exit_work/$1" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT="$2" VERI_TIMEOUT=30 \
      VERI_POLL=0.2 "$SUP" develop-red "$stub/$3" ) >/dev/null 2>&1
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
