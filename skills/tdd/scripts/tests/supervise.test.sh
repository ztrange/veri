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


header_text="$(awk 'NR > 1 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "$SUP" | tr '\n' ' ')"
header_unstated() {
  local where regex
  while IFS='|' read -r where regex; do
    [[ -n "$where" ]] || continue
    grep -qE "$regex" <<< "$header_text" || printf ' %s' "$where"
  done
}


cat > "$stub/leaf-term-sleep" <<'L'
echo $$ > leaf-pid
echo "leaf: started"
exec sleep 60
L
chmod +x "$stub/leaf-term-sleep"

cat > "$stub/leaf-real-lag" <<'L'
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


cat > "$stub/leaf-quiet-wrapper" <<'L'
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

samex_work="$work/live-owner-same-name-exit"
mkdir -p "$samex_work"
mkfifo "$samex_work/release"
cat > "$stub/leaf-held-fail" <<'L'
echo $$ > leaf-pid
read -r _ < release
exit 3
L
chmod +x "$stub/leaf-held-fail"
( cd "$samex_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-held-fail" ) >/dev/null 2>&1 &
samex_sup=$!
for _ in $(seq 1 50); do [[ -s "$samex_work/leaf-pid" ]] && break; sleep 0.1; done
samex_leaf="$(tr -d '[:space:]' < "$samex_work/leaf-pid" 2>/dev/null)"
sup_in "$samex_work" revise-green-1 "$stub/leaf-second" >/dev/null 2>"$samex_work/err"
samex_code=$?
samex_after_refusal="$(cat "$samex_work/.tdd/revise-green-1.exit" 2>/dev/null || echo '<missing>')"
( cd "$samex_work" && env VERI_POLL=0.02 "$SCRIPTS/wait-leaf.sh" revise-green-1 0 ) >/dev/null 2>&1
samex_wait=$?
[[ -z "$samex_leaf" ]] || echo go > "$samex_work/release"
wait "$samex_sup"
samex_final="$(cat "$samex_work/.tdd/revise-green-1.exit" 2>/dev/null || echo '<missing>')"
{ [[ -n "$samex_leaf" ]] && [[ "$samex_code" == 2 ]] && [[ "$samex_after_refusal" == '<missing>' ]] \
  && [[ "$samex_wait" == 3 ]] && [[ "$samex_final" == 1 ]]; } && ok \
  || no "#618: a launch refused because a leaf of the same name is alive writes no .exit for that name, and the live leaf's own code lands there when it finishes (first leaf pid=${samex_leaf:-<never started>}; refusal code=$samex_code want 2; .exit after refusal='$samex_after_refusal' want <missing>; wait-leaf.sh while live=$samex_wait want 3; .exit after the live leaf finished='$samex_final' want 1; stderr='$(cat "$samex_work/err")')"

live_owner_tree() {
  mkdir -p "$1/.tdd"
  printf '%s develop-green\n' "$$" > "$1/.tdd/leaf.owner"
}

refx_work="$work/live-owner-refused-exit"
live_owner_tree "$refx_work"
sup_in "$refx_work" verdict-green "$stub/leaf-second" >/dev/null 2>"$refx_work/err"
refx_code=$?
refx_exit="$(cat "$refx_work/.tdd/verdict-green.exit" 2>/dev/null || echo '<missing>')"
{ [[ "$refx_code" == 2 ]] && [[ "$refx_exit" == 2 ]]; } && ok \
  || no "#618: a launch refused because a leaf under another name is alive exits 2 and writes 2 to .tdd/<refused-name>.exit (code=$refx_code want 2; verdict-green.exit='$refx_exit' want 2; stderr='$(cat "$refx_work/err")')"

refw_work="$work/live-owner-refused-wait"
live_owner_tree "$refw_work"
sup_in "$refw_work" verdict-green "$stub/leaf-second" >/dev/null 2>"$refw_work/err"
( cd "$refw_work" && env VERI_POLL=0.02 "$SCRIPTS/wait-leaf.sh" verdict-green 0 ) >/dev/null 2>"$refw_work/wait-err"
refw_wait=$?
[[ "$refw_wait" == 2 ]] && ok \
  || no "#618: after a launch refused because a leaf under another name is alive, wait-leaf.sh <refused-name> exits 2, not 3 (wait-leaf.sh verdict-green=$refw_wait want 2; .tdd: $(ls "$refw_work/.tdd" | tr '\n' ' '); stderr='$(cat "$refw_work/err" "$refw_work/wait-err")')"

refo_work="$work/live-owner-refused-owner"
live_owner_tree "$refo_work"
refo_before="$(cat "$refo_work/.tdd/leaf.owner")"
sup_in "$refo_work" verdict-green "$stub/leaf-second" >/dev/null 2>"$refo_work/err"
refo_ran="no"; [[ -e "$refo_work/second-ran" ]] && refo_ran="yes"
refo_after="$(cat "$refo_work/.tdd/leaf.owner" 2>/dev/null || echo '<missing>')"
{ [[ "$refo_ran" == no ]] && [[ "$refo_after" == "$refo_before" ]]; } && ok \
  || no "#618: a refused launch does not run its command and leaves .tdd/leaf.owner naming the live leaf, unchanged (command ran=$refo_ran want no; leaf.owner='$refo_after' want '$refo_before'; stderr='$(cat "$refo_work/err")')"

live_work="$work/live-owner-unfinished"
live_owner_tree "$live_work"
sup_in "$live_work" verdict-green "$stub/leaf-second" >/dev/null 2>"$live_work/err"
live_code=$?
live_err="$(cat "$live_work/err")"
{ [[ "$live_code" == 2 ]] && [[ "$live_err" == *"develop-green (pid $$)"* ]]; } && ok \
  || no "#618: a launch is still refused, naming the live leaf and its pid, when the recorded leaf is alive and .tdd/<owner-name>.exit does not exist (code=$live_code want 2; stderr='$live_err' want it to name develop-green and pid $$)"

woke_with_own_exit() {
  local susp_rc
  susp_rc="$(cat "$work/.tdd/$1.rc" 2>/dev/null || echo '<missing>')"
  rm -f "$work/.test-suspended"
  { [[ "$code" == 1 ]] && [[ "$susp_rc" == 3 ]] && [[ "$out" == *'awake again'* ]]; } && ok \
    || no "$2 (code=$code want 1, rc=$susp_rc want 3, err=$(cat "$work/err"))"
}

cat > "$stub/clock-suspend" <<'C'
clock-jump "$1" suspend && echo "$1" >> .test-suspended
C
cat > "$stub/leaf-suspended" <<'L'
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

rm -f "$work/.test-suspended" "$work/.tdd/suspended.rc"
unset VERI_AWAKE_CLOCK
sup suspended 2 30 leaf-suspended
export VERI_AWAKE_CLOCK="$stub/awake-clock"
woke_with_own_exit suspended "#472: with VERI_AWAKE_CLOCK unset, a leaf silent only across a 3s suspend against a 2s heartbeat is not killed and finishes with its own exit code"

cat > "$stub/leaf-suspended-timeout" <<'L'
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

cat > "$stub/leaf-awake-silent" <<'L'
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

cat > "$stub/leaf-awake-runaway" <<'L'
: > .test-clock-reads
echo "leaf: starting"
clock-jump 1; await-poll; await-poll
echo "leaf: busy"
clock-jump 1; await-poll; await-poll
: > .test-inside-window
for i in 1 2 3 4 5 6 7 8 9 10; do echo "leaf: busy $i"; clock-jump 1; await-poll; done
exit 0
L
chmod +x "$stub/leaf-awake-runaway"
rm -f "$work/.test-suspended" "$work/.test-inside-window"
sup awake-runaway 30 4 leaf-awake-runaway
runaway_inside="$([[ -e "$work/.test-inside-window" ]] && echo yes || echo no)"
rm -f "$work/.test-inside-window"
{ [[ "$code" == 2 ]] && [[ "$runaway_inside" == yes ]] \
  && grep -F 'hard timeout 4s exceeded' "$work/err" > /dev/null; } && ok \
  || no "#472: a noisy leaf running 2s then on past a 4s VERI_TIMEOUT of awake time (no suspend) survives the first and is killed on the hard timeout (code=$code want 2, survived inside the timeout=$runaway_inside want yes, err=$(cat "$work/err"))"

# hazard: load is simulated, never waited for: loaded_py's time.time() runs 3s late once .test-loaded exists.
loaded_py="$(scratch_dir)"
cat > "$loaded_py/python3" <<P
#!/bin/sh
if [ "\$1" = -c ]; then
  shift
  exec "$(command -v python3)" -c 'import os, sys, time
_read = time.time
time.time = lambda: _read() + (3 if os.path.exists(".test-loaded") else 0)
_code = sys.argv[1]
sys.argv = sys.argv[:1] + sys.argv[2:]
exec(_code)' "\$@"
fi
exec "$(command -v python3)" "\$@"
P
cat > "$stub/leaf-loaded-runaway" <<'L'
: > .test-clock-reads
echo "leaf: starting"
clock-jump 1; await-poll; await-poll
echo "leaf: busy"
: > .test-loaded; await-poll; await-poll
clock-jump 1; await-poll; await-poll
: > .test-inside-window
for i in 1 2 3 4 5 6 7 8 9 10; do echo "leaf: busy $i"; clock-jump 1; await-poll; done
exit 0
L
chmod +x "$loaded_py/python3" "$stub/leaf-loaded-runaway"
rm -f "$work/.test-suspended" "$work/.test-inside-window" "$work/.test-loaded"
PATH="$loaded_py:$PATH" sup loaded-runaway 30 4 leaf-loaded-runaway
loaded_inside="$([[ -e "$work/.test-inside-window" ]] && echo yes || echo no)"
rm -rf "$work/.test-inside-window" "$work/.test-loaded" "$loaded_py"
{ [[ "$code" == 2 ]] && [[ "$loaded_inside" == yes ]] \
  && grep -F 'hard timeout 4s exceeded' "$work/err" > /dev/null; } && ok \
  || no "#972: the #472 awake-runaway leaf, with load stretching the real wall time between its injected clock jumps by 3s, still survives inside a 4s VERI_TIMEOUT and is killed on the hard timeout (code=$code want 2, survived inside the timeout=$loaded_inside want yes, err=$(cat "$work/err"))"

cat > "$stub/leaf-asleep-an-hour" <<'L'
: > .test-clock-reads
echo "leaf: starting"
clock-suspend 3600
await-poll; await-poll
echo "leaf: awake again"; exit 3
L
chmod +x "$stub/leaf-asleep-an-hour"
rm -f "$work/.test-suspended" "$work/.tdd/asleep-an-hour.rc"
sup asleep-an-hour 180 900 leaf-asleep-an-hour
woke_with_own_exit asleep-an-hour "#472: a leaf asleep an hour across a simulated suspend, against the default 180s heartbeat and 900s VERI_TIMEOUT, is killed by neither and finishes with its own exit code"

clock_misses="$(header_unstated <<'CLAIMS'
clock-source|monotonic
macos|macOS.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}macOS
linux|Linux.{0,200}(suspend|sleep)|(suspend|sleep).{0,200}Linux
pauses-in-suspend|(not advance|stop[a-z]* advancing|pause[a-z]*|stand[a-z]* still|stop[a-z]*).{0,160}(suspend|asleep|sleep)
CLAIMS
)"

[[ -z "$clock_misses" ]] && ok \
  || no "#472: supervise.sh's header names the watchdog's clock source and why it pauses while the machine is suspended, for macOS and Linux (unstated:$clock_misses)"

cat > "$stub/leaf-slept-through" <<'L'
echo "leaf: starting"
: > .test-clock-reads
clock-jump 2
echo "leaf: busy"
clock-suspend 100
await-poll; await-poll; await-poll
echo "leaf: awake again"; exit 0
L
chmod +x "$stub/leaf-slept-through"
awake_spent=2
slept_exit_ok() {
  [[ "$1" == 0 ]] && [[ "$2" =~ ^[0-9]+$ ]] && (( $2 >= awake_spent && $2 <= awake_spent + 1 ))
}
slept_work="$work/slept"
sup_run "$slept_work" VERI_HEARTBEAT=30 VERI_TIMEOUT=30 "$SUP" develop-red "$stub/leaf-slept-through"
slept_status="$(event_field "$slept_work" exit status)"
slept_secs="$(event_field   "$slept_work" exit secs)"
slept_exit_ok "$slept_status" "$slept_secs" && ok \
  || no "#486: a leaf awake ${awake_spent}s and suspended 100s reports the awake seconds as its exit event's secs, not the wall seconds (status=$slept_status want 0, secs=$slept_secs want $awake_spent..$(( awake_spent + 1 )))"

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

across_work="$work/slept-across"
mkdir -p "$across_work"
cat > "$across_work/awake-spy" <<C
suspended=no; running=yes
[ -e .test-suspended ] && suspended=yes
[ -e .tdd/develop-red.rc ] && running=no
echo "\$suspended \$running" >> .test-awake-spy
exec "$stub/awake-clock"
C
chmod +x "$across_work/awake-spy"
sup_run "$across_work" VERI_AWAKE_CLOCK="$across_work/awake-spy" VERI_HEARTBEAT=30 VERI_TIMEOUT=30 \
  "$SUP" develop-red "$stub/leaf-slept-through"
across_status="$(event_field "$across_work" exit status)"
across_secs="$(event_field   "$across_work" exit secs)"
across_polls="$(grep -c '^yes yes$' "$across_work/.test-awake-spy" 2>/dev/null)"
{ [[ "$across_polls" =~ ^[0-9]+$ ]] && (( across_polls >= 2 )) \
  && slept_exit_ok "$across_status" "$across_secs"; } && ok \
  || no "#512: case 50's slept-through leaf stays suspended across two watchdog polls before it exits 0, and still reports status 0 with secs in the awake range (polls while suspended=$across_polls want >=2, status=$across_status want 0, secs=$across_secs want $awake_spent..$(( awake_spent + 1 )))"

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
