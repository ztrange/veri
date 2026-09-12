#!/usr/bin/env bash
# Tests for scripts/supervise.sh — the programmatic supervisor, the deterministic
# robustness core (#4). Every leaf is launched through it; it tells a slow-but-alive leaf
# (heartbeat: progress-log activity within a window) from a hung one (silent past the
# window), caps the wall clock with a hard timeout, kills a stuck leaf, and reports a
# clear status (success / failure / killed-stuck) plus the captured output.
#
# Driven against STUB LEAF SCRIPTS (no claude): exit-0, exit-nonzero, hang, slow-but-alive,
# and runaway (alive but over the hard timeout). Timings are compressed via the env knobs
# VERI_HEARTBEAT / VERI_TIMEOUT / VERI_POLL so the suite stays fast.
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
#     `VERI_HEARTBEAT`'s default is a number written down in five places: once as code
#     (`heartbeat="${VERI_HEARTBEAT:-N}"`) and four times as prose — the script's own
#     `Tunables (env)` header, SKILL.md's launcher entry, and two spots in
#     docs/wt/commentary.py (supervise.sh's contract table, and the note that explains why
#     the silence window can be so much shorter than the hard timeout). Changing the
#     constant alone leaves four sentences confidently stating the old figure, and nothing
#     in the repo notices: the walkthrough is generated from the scripts, so `make docs`
#     happily rebuilds a page whose hand-written commentary contradicts the source it sits
#     next to. This is the same guarantee `make docs-check` already gives the revise budget
#     ("the page and SKILL.md both say N", docs/check-walkthrough.py) applied to this one.
#
#     The case lives here rather than under `docs/tests/` for the reason wait-leaf.test.sh
#     case 4 gives: `make docs-check` is deliberately not part of `make test` (Makefile,
#     "Neither is part of `test` on purpose"), so a case parked there would not run in the
#     suite this script's own behaviour is verified against.
#
#     Each site is located by a regex that ends at the figure it asks about, and a site
#     whose pattern can no longer be found reports `<none>` — a rewording that moves a
#     statement out of the check's sight is drift too, and must fail rather than pass
#     silently. One statement is knowingly out of reach: commentary.py spells the figure
#     out in words once ("a hang trips in two seconds instead of forty-five"), which no
#     regex here can compare against a number.
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
# the figure as much as the four sentences do, and it is the one the others must match.
encoded="$(stated "$SUP" 'VERI_HEARTBEAT:-[0-9]+')"

prose_misses=""
[[ "$encoded" =~ ^[0-9]+$ ]] || prose_misses=" supervise.sh:no-VERI_HEARTBEAT-default-found"
while IFS='|' read -r where file regex; do
  [[ -n "$where" ]] || continue
  got="$(stated "$ROOT/$file" "$regex")"
  [[ "$got" == "$encoded" ]] || prose_misses="$prose_misses $where:says-$got"
done <<'SITES'
supervise.sh-header|skills/solve-issue/scripts/supervise.sh|VERI_HEARTBEAT silence window secs \(default [0-9]+
SKILL.md-tunables|skills/solve-issue/SKILL.md|VERI_HEARTBEAT.{0,3}\(silence window s, +default [0-9]+
commentary.py-contract|docs/wt/commentary.py|VERI_HEARTBEAT</code> [0-9]+s
commentary.py-streaming-note|docs/wt/commentary.py|[0-9]+-second silence window
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
