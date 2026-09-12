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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
