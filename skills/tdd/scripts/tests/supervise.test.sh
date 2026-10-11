#!/usr/bin/env bash
# Tests for scripts/supervise.sh — the programmatic supervisor every leaf is launched
# through, driven against stub leaf scripts on an injected clock.
#
# Contract under test:
#   supervise.sh tells a slow-but-alive leaf (progress-log activity within the heartbeat
#   window) from a hung one (silent past it), caps the wall clock with a hard timeout,
#   kills a stuck leaf, and reports its status plus the captured output.
#   exit 0 success · 1 leaf-failure · 2 killed-stuck.
#
# Run: scripts/tests/supervise.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/.."
SUP="$SCRIPTS/supervise.sh"
source "$HERE/lib/harness.sh"

stub="$(scratch_dir)"
work="$(scratch_dir)"

cat > "$stub/leaf-ok" <<'L'
#!/bin/sh
echo "leaf: starting"; echo "leaf: did the work"; exit 0
L
cat > "$stub/leaf-fail" <<'L'
#!/bin/sh
echo "leaf: starting"; echo "leaf: blew up"; exit 3
L
cat > "$stub/leaf-hang" <<'L'
#!/bin/sh
echo "leaf: starting"; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
cat > "$stub/leaf-slow" <<'L'
#!/bin/sh
: > .test-clock-reads
for i in 1 2 3 4 5 6; do echo "leaf: tick $i"; clock-jump 1; await-poll; done
echo "leaf: done"; exit 0
L
cat > "$stub/leaf-runaway" <<'L'
#!/bin/sh
: > .test-clock-reads
while true; do echo "leaf: busy"; clock-jump 1; await-poll; done
L
cat > "$stub/leaf-flaky" <<'L'
#!/bin/sh
if [ -e .retry-marker ]; then
  echo "leaf: recovered on retry"; exit 0
fi
echo "leaf: starting"; : > .retry-marker; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
chmod +x "$stub"/leaf-*

# hazard: the stub clocks read no real time, only clock_base plus injected jumps, or load counts as awake time (#972).
clock_base=1700000000
realdate="$(command -v date)"
realstat="$(command -v stat)"
cat > "$stub/date" <<D
#!/bin/sh
if [ "\$*" = "+%s" ]; then
  [ -e .test-clock-reads ] && echo r >> .test-clock-reads
  offset="\$(tail -n 1 .test-clock 2>/dev/null | cut -d' ' -f2)"
  printf '%s\n' "\$(( $clock_base + \${offset:-0} ))"
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
        at, value = line.split()[:2]
        if float(at) <= m:
            offset = int(value)
except OSError:
    pass
print(int(m) + offset)' "\$3"
  fi
fi
exec "$realstat" "\$@"
D
latest_clock_py='offset = suspended = 0
try:
    last = open(".test-clock").read().splitlines()[-1].split()
    offset = int(last[1])
    suspended = int(last[2]) if len(last) > 2 else 0
except (OSError, IndexError):
    pass'
cat > "$stub/clock-jump" <<C
#!/bin/sh
exec python3 -c '
import sys, time
$latest_clock_py
if sys.argv[2:] == ["suspend"]:
    suspended += int(sys.argv[1])
with open(".test-clock", "a") as f:
    f.write("%r %d %d\\n" % (time.time(), offset + int(sys.argv[1]), suspended))' "\$@"
C
cat > "$stub/await-poll" <<'C'
#!/bin/sh
n="$(wc -l < .test-clock-reads)"
for _ in $(seq 1 500); do [ "$(wc -l < .test-clock-reads)" -gt "$n" ] && exit 0; sleep 0.01; done
exit 1
C
cat > "$stub/awake-clock" <<C
#!/bin/sh
exec python3 -c '
$latest_clock_py
print($clock_base + offset - suspended)'
C
chmod +x "$stub/date" "$stub/stat" "$stub/clock-jump" "$stub/await-poll" "$stub/awake-clock"

export PATH="$stub:$PATH"
export VERI_AWAKE_CLOCK="$stub/awake-clock"

sup() {
  local name="$1" hb="$2" to="$3" leaf="$4"
  rm -f "$work/.test-clock" "$work/.test-clock-reads"
  out="$( cd "$work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT="$hb" VERI_TIMEOUT="$to" VERI_POLL=0.02 \
            VERI_KILL_POLL=0.01 "$SUP" "$name" "$stub/$leaf" 2>"$work/err" )"
  code=$?
}

sup hang 1 30 leaf-hang
if pgrep -f "$stub/leaf-hang" >/dev/null 2>&1; then no "killed leaf left a process behind"; else ok; fi



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

sup_run() {
  local dir="$1"; shift
  mkdir -p "$dir"
  ( cd "$dir" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 VERI_TIMEOUT=10 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$@" ) >/dev/null 2>&1
}

heartbeat_kill() { [[ "$1" == "no heartbeat for "*" (window ${2}s)" ]]; }


usage_turns=7
cat > "$stub/leaf-result" <<L
#!/bin/sh
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
echo '{"type":"result","subtype":"success","is_error":false,"duration_ms":91234,"duration_api_ms":40118,"num_turns":$usage_turns,"result":"done","session_id":"4d1a","total_cost_usd":0.31,"usage":{"input_tokens":37,"cache_creation_input_tokens":41002,"cache_read_input_tokens":903117,"output_tokens":5140}}'
exit 0
L
chmod +x "$stub/leaf-result"

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


result_hang_stub() {
  local name="$1" subtype="$2" is_error="$3" text="$4" prelude="${5:-}"
  cat > "$stub/$name" <<L
$prelude
printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
printf '%s\n' '{"type":"result","subtype":"$subtype","is_error":$is_error,"duration_ms":164524,"duration_api_ms":44600,"num_turns":12,"result":"$text","session_id":"4d1a","total_cost_usd":0.31,"usage":{"input_tokens":37,"cache_creation_input_tokens":41002,"cache_read_input_tokens":903117,"output_tokens":5140}}'
clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"
sleep 60
L
  chmod +x "$stub/$name"
}


sup_direct() {
  local dir="$1" leaf="$2" window="$3"; shift 3
  mkdir -p "$dir"
  ( cd "$dir" && env "$@" VERI_HEARTBEAT="$window" VERI_TIMEOUT=30 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$SUP" verify-red "$stub/$leaf" )
}


leaf_rc() { cat "$1/.tdd/verify-red.rc" 2>/dev/null || echo '<missing>'; }


cat > "$stub/leaf-term-sleep" <<'L'
echo $$ > leaf-pid
echo "leaf: started"
exec sleep 60
L
chmod +x "$stub/leaf-term-sleep"

sup_in() {
  local dir="$1"; shift
  ( cd "$dir" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$SUP" "$@" )
}

cat > "$stub/leaf-second" <<'L'
: > second-ran
exit 0
L
chmod +x "$stub/leaf-second"

cat > "$stub/clock-suspend" <<'C'
clock-jump "$1" suspend && echo "$1" >> .test-suspended
C
chmod +x "$stub/clock-suspend"

suspend_probe="$(scratch_dir)"
mkdir -p "$suspend_probe/spy" "$suspend_probe/cwd"
cat > "$suspend_probe/awake-read" <<C
echo "\$("$stub/awake-clock") $clock_base" >> .test-awake-reads
C
cat > "$suspend_probe/spy/clock-jump" <<C
"$stub/clock-jump" "\$@" || exit \$?
"$suspend_probe/awake-read"
C
chmod +x "$suspend_probe/awake-read" "$suspend_probe/spy/clock-jump"
( cd "$suspend_probe/cwd" && PATH="$suspend_probe/spy:$PATH" "$stub/clock-suspend" 100 \
    && "$suspend_probe/awake-read" )
suspend_code=$?
suspend_reads="$(cat "$suspend_probe/cwd/.test-awake-reads" 2>/dev/null)"
suspend_ahead="$(awk '$1 > $2 { print "awake=" $1 " unjumped=" $2 }' <<<"$suspend_reads")"
rm -rf "$suspend_probe"
{ [[ "$suspend_code" == 0 ]] && [[ -n "$suspend_reads" ]] && [[ -z "$suspend_ahead" ]]; } && ok \
  || no "#512: clock-suspend 100 never lets the awake clock read higher than the true awake seconds during its run (code=$suspend_code want 0, readings ahead of the unjumped clock: '${suspend_ahead//$'\n'/; }' want none, all readings: '${suspend_reads//$'\n'/; }')"

atomic_probe="$(scratch_dir)"
mkdir -p "$atomic_probe/spy" "$atomic_probe/cwd"
cat > "$atomic_probe/both-read" <<C
echo "\$("$stub/awake-clock") \$("$stub/date" +%s) $clock_base" >> .test-both-reads
C
cat > "$atomic_probe/spy/clock-jump" <<C
"$atomic_probe/both-read"
"$stub/clock-jump" "\$@" || exit \$?
"$atomic_probe/both-read"
C
chmod +x "$atomic_probe/both-read" "$atomic_probe/spy/clock-jump"
( cd "$atomic_probe/cwd" && PATH="$atomic_probe/spy:$PATH" "$stub/clock-suspend" 100 \
    && "$atomic_probe/both-read" )
atomic_code=$?
atomic_reads="$(cat "$atomic_probe/cwd/.test-both-reads" 2>/dev/null)"
atomic_torn="$(awk '{ moved = ($2 - $3 >= 50); slept = ($2 - $1 >= 50) }
  moved != slept { print "awake=" $1 " wall=" $2 " unjumped=" $3 }' <<<"$atomic_reads")"
atomic_last="$(awk 'END { print (($2 - $3 >= 50) && ($2 - $1 >= 50)) ? "both" : "not both" }' \
  <<<"$atomic_reads")"
rm -rf "$atomic_probe"
{ [[ "$atomic_code" == 0 ]] && [[ -z "$atomic_torn" ]] && [[ "$atomic_last" == both ]]; } && ok \
  || no "#512: clock-suspend 100 moves the wall clock and the awake clock together, so no reading during its run sees one moved without the other (code=$atomic_code want 0, torn readings: '${atomic_torn//$'\n'/; }' want none, last reading: $atomic_last want both, all readings (awake wall unjumped): '${atomic_reads//$'\n'/; }')"

restart_py="$(scratch_dir)"
realpy="$(command -v python3)"
cat > "$restart_py/python3" <<P
if [ "\$1" = -c ]; then
  shift
  exec "$realpy" -c 'import sys, time
_read, _born = time.monotonic, time.monotonic()
time.monotonic = lambda: _read() - _born
_code = sys.argv[1]
sys.argv = sys.argv[:1] + sys.argv[2:]
exec(_code)' "\$@"
fi
exec "$realpy" "\$@"
P
{ printf '%s\n' '#!/bin/sh'; cat "$restart_py/python3"; } > "$restart_py/python3.new" && mv "$restart_py/python3.new" "$restart_py/python3"
printf '%s\n' '#!/bin/sh' 'echo "leaf: starting"; sleep 4; echo "leaf: finished on its own"' > "$restart_py/leaf-quiet"
chmod +x "$restart_py/python3" "$restart_py/leaf-quiet"
restart_work="$work/restart-clock"
mkdir -p "$restart_work"
restart_run() {
  ( cd "$restart_work" && env -u VERI_AWAKE_CLOCK PATH="$restart_py:$PATH" VERI_STUCK_RETRIES=0 \
      VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$@" "$SUP" develop-red "$restart_py/leaf-quiet" ) >/dev/null 2>"$restart_work/err"
}
restart_run VERI_HEARTBEAT=999 VERI_TIMEOUT=1
restart_timeout_code=$?
restart_timeout_err="$(cat "$restart_work/err")"
restart_run VERI_HEARTBEAT=1 VERI_TIMEOUT=999
restart_heartbeat_code=$?
restart_heartbeat_err="$(cat "$restart_work/err")"
rm -rf "$restart_py"
{ [[ "$restart_timeout_code" == 2 ]] && [[ "$restart_timeout_err" == *'hard timeout'* ]] \
  && [[ "$restart_heartbeat_code" == 2 ]] && [[ "$restart_heartbeat_err" == *'no heartbeat'* ]]; } && ok \
  || no "#563: under a python3 whose time.monotonic() restarts per process, a 4s-quiet leaf is still killed by a 1s hard timeout and by a 1s heartbeat (timeout code=$restart_timeout_code want 2, err=$restart_timeout_err; heartbeat code=$restart_heartbeat_code want 2, err=$restart_heartbeat_err)"

settled_work="$(scratch_dir)"
mkdir -p "$settled_work/.tdd"
printf '3\n' > "$settled_work/.tdd/issue-954-timeout"
cat > "$stub/leaf-busy-ten" <<'L'
#!/bin/sh
: > .test-clock-reads
for i in 1 2 3 4 5 6 7 8 9 10; do echo "leaf: busy $i"; clock-jump 1; await-poll; done
echo "leaf: finished on its own"; exit 0
L
chmod +x "$stub/leaf-busy-ten"
( cd "$settled_work" && env -u VERI_TIMEOUT -u VERI_STEP VERI_ISSUE=954 VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-busy-ten" ) >/dev/null 2>"$settled_work/err"
settled_code=$?
{ [[ "$settled_code" == 2 ]] && grep -F 'hard timeout 3s exceeded' "$settled_work/err" > /dev/null; } && ok \
  || no "#954: with VERI_TIMEOUT unset and .tdd/issue-954-timeout recording a settled 3s for VERI_ISSUE=954, a leaf busy for 10s is killed-stuck on 'hard timeout 3s exceeded', not run under the 900s default (code=$settled_code want 2, err=$(cat "$settled_work/err"))"

unissued_work="$(scratch_dir)"
mkdir -p "$unissued_work/.tdd"
printf '3\n' > "$unissued_work/.tdd/issue--timeout"
( cd "$unissued_work" && env -u VERI_TIMEOUT -u VERI_STEP -u VERI_ISSUE VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-busy-ten" ) >/dev/null 2>"$unissued_work/err"
unissued_code=$?
[[ "$unissued_code" == 0 ]] && ok \
  || no "#954: with VERI_ISSUE unset, a .tdd/issue--timeout recording 3s is no settled timeout, so a leaf busy for 10s finishes under the 900s default (code=$unissued_code want 0, err=$(cat "$unissued_work/err"))"

subdir_work="$(scratch_dir)"
new_repo -b main "$subdir_work" >/dev/null 2>&1
mkdir -p "$subdir_work/.tdd" "$subdir_work/src/deep"
printf '3\n' > "$subdir_work/.tdd/issue-954-timeout"
( cd "$subdir_work/src/deep" && env -u VERI_TIMEOUT -u VERI_STEP VERI_ISSUE=954 VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-busy-ten" ) >/dev/null 2>"$subdir_work/err"
subdir_code=$?
{ [[ "$subdir_code" == 2 ]] && grep -F 'hard timeout 3s exceeded' "$subdir_work/err" > /dev/null; } && ok \
  || no "#954: launched from src/deep, a subdirectory of the run worktree, with VERI_TIMEOUT unset and the worktree root's .tdd/issue-954-timeout recording a settled 3s, a leaf busy for 10s is killed-stuck on 'hard timeout 3s exceeded', not run under the 900s default (code=$subdir_code want 2, err=$(cat "$subdir_work/err"))"

explicit_work="$(scratch_dir)"
mkdir -p "$explicit_work/.tdd"
printf '3\n' > "$explicit_work/.tdd/issue-954-timeout"
( cd "$explicit_work" && env -u VERI_STEP VERI_TIMEOUT=5 VERI_ISSUE=954 VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-busy-ten" ) >/dev/null 2>"$explicit_work/err"
explicit_code=$?
{ [[ "$explicit_code" == 2 ]] && grep -F 'hard timeout 5s exceeded' "$explicit_work/err" > /dev/null; } && ok \
  || no "#954: an explicit VERI_TIMEOUT=5 wins over .tdd/issue-954-timeout recording a settled 3s, so a leaf busy for 10s is killed-stuck on 'hard timeout 5s exceeded' (code=$explicit_code want 2, err=$(cat "$explicit_work/err"))"
finish
