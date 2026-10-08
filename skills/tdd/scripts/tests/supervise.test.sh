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

sup ok 5 10 leaf-ok
{ [[ "$code" == 0 ]] && [[ "$out" == *'did the work'* ]]; } && ok \
  || no "exit-0 leaf → success + captured output (code=$code)"

sup fail 5 10 leaf-fail
{ [[ "$code" == 1 ]] && [[ "$out" == *'blew up'* ]]; } && ok \
  || no "exit-nonzero leaf → failure + output (code=$code)"

sup hang 1 30 leaf-hang
{ [[ "$code" == 2 ]] && grep -qi 'heartbeat\|stuck\|silent' "$work/err"; } && ok \
  || no "hung leaf → killed-stuck via heartbeat (code=$code, err=$(cat "$work/err"))"

sup slow 2 30 leaf-slow
{ [[ "$code" == 0 ]] && [[ "$out" == *'done'* ]]; } && ok \
  || no "slow-but-alive leaf survives heartbeat → success (code=$code)"

sup runaway 30 1 leaf-runaway
{ [[ "$code" == 2 ]] && grep -qi 'timeout\|stuck' "$work/err"; } && ok \
  || no "runaway leaf → killed-stuck via hard timeout (code=$code, err=$(cat "$work/err"))"

sup ok 5 10 leaf-ok
grep -qiE 'success|ok' "$work/err" && ok || no "emits a status line (err=$(cat "$work/err"))"

sup hang 1 30 leaf-hang
if pgrep -f "$stub/leaf-hang" >/dev/null 2>&1; then no "killed leaf left a process behind"; else ok; fi

VERI_STUCK_RETRIES=3 sup hang 1 30 leaf-hang
stuck_lines="$(grep -c 'supervise\[hang\]: killed-stuck' "$work/err")"
retry_lines="$(grep -c 'retry [0-9][0-9]*/[0-9][0-9]*' "$work/err")"
{ [[ "$code" == 2 ]] && [[ "$stuck_lines" -eq 1 ]] && [[ "$retry_lines" -eq 0 ]]; } && ok \
  || no "ambient VERI_STUCK_RETRIES=3 → hung leaf still runs exactly once (code=$code, killed-stuck lines=$stuck_lines, retry lines=$retry_lines)"

recorded_code() { sup "$@"; cat "$work/.tdd/$1.exit" 2>/dev/null || echo '<missing>'; }
eok="$(recorded_code    exit-ok    5 10 leaf-ok)"
efail="$(recorded_code  exit-fail  5 10 leaf-fail)"
estuck="$(recorded_code exit-stuck 1 30 leaf-hang)"
{ [[ "$eok" == 0 ]] && [[ "$efail" == 1 ]] && [[ "$estuck" == 2 ]]; } && ok \
  || no ".tdd/<name>.exit records the supervisor's own final code, killed-stuck included (success=$eok want 0, failure=$efail want 1, killed-stuck=$estuck want 2)"

ROOT="$(cd "$HERE/../../../.." && pwd)"

stated() {
  local hit
  [[ -f "$1" ]] || { echo '<no-file>'; return; }
  hit="$(head -1 < <(tr '\n' ' ' < "$1" | grep -oE "$2"))"
  [[ -n "$hit" ]] || { echo '<none>'; return; }
  printf '%s' "$hit" | grep -oE '[0-9]+' | tail -1
}

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

launch_work="$work/launch"
launch_name=revise-green-2
launch_cmd=(env VERI_TIMEOUT=1200 "$stub/leaf-ok")
sup_run "$launch_work" "$SUP" "$launch_name" "${launch_cmd[@]}"
launch_code=$?
launch_got_name="$(event_field    "$launch_work" launch name)"
launch_got_cmd="$(event_field     "$launch_work" launch cmd)"
launch_got_attempt="$(event_field "$launch_work" launch attempt)"
{ [[ "$launch_code" == 0 ]] \
  && [[ "$launch_got_name"    == "$launch_name" ]] \
  && [[ "$launch_got_cmd"     == "${launch_cmd[*]}" ]] \
  && [[ "$launch_got_attempt" == 2 ]]; } && ok \
  || no "a launched leaf appends a launch event naming the leaf, its command and the attempt (code=$launch_code, name=$launch_got_name, cmd=$launch_got_cmd, attempt=$launch_got_attempt)"

heartbeat_kill() { [[ "$1" == "no heartbeat for "*" (window ${2}s)" ]]; }


retry_work="$work/retry"
mkdir -p "$retry_work"
retry_window=1
( cd "$retry_work" && env -u VERI_STUCK_RETRIES VERI_HEARTBEAT="$retry_window" \
    VERI_TIMEOUT=30 VERI_POLL=0.02 VERI_KILL_POLL=0.01 \
    "$SUP" develop-red "$stub/leaf-flaky" ) >/dev/null 2>&1
retry_code=$?
retry_cause="$(event_field "$retry_work" retry cause)"
{ [[ "$retry_code" == 0 ]] \
  && heartbeat_kill "$retry_cause" "$retry_window"; } && ok \
  || no "a relaunched killed-stuck leaf appends one retry event carrying the kill cause (code=$retry_code, cause=$retry_cause)"


exit_work="$work/exit"
exit_window=2

exit_run() {
  sup_run "$exit_work/$1" VERI_HEARTBEAT="$2" "$SUP" develop-red "$stub/$3"
}

exit_run ok    5              leaf-ok
exit_run fail  5              leaf-fail
exit_run stuck "$exit_window" leaf-hang

exit_ok_status="$(event_field    "$exit_work/ok"    exit status)"
exit_ok_secs="$(event_field      "$exit_work/ok"    exit secs)"
exit_fail_status="$(event_field  "$exit_work/fail"  exit status)"
exit_stuck_status="$(event_field "$exit_work/stuck" exit status)"
exit_stuck_cause="$(event_field  "$exit_work/stuck" exit cause)"
exit_stuck_secs="$(event_field   "$exit_work/stuck" exit secs)"

{ [[ "$exit_ok_status"    == 0 ]] && [[ "$exit_ok_secs" =~ ^[0-9]+$ ]] \
  && [[ "$exit_fail_status"  == 1 ]] \
  && [[ "$exit_stuck_status" == 2 ]] \
  && heartbeat_kill "$exit_stuck_cause" "$exit_window" \
  && [[ "$exit_stuck_secs" =~ ^[0-9]+$ ]] && (( exit_stuck_secs >= exit_window )); } && ok \
  || no "a supervised leaf appends one exit event carrying the 0/1/2 status, the kill cause and the attempt's wall seconds (success status=$exit_ok_status want 0, secs=$exit_ok_secs; failure status=$exit_fail_status want 1; killed-stuck status=$exit_stuck_status want 2, cause=$exit_stuck_cause, secs=$exit_stuck_secs want >=$exit_window)"

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

usage_work="$work/usage"
usage_turns=7
cat > "$stub/leaf-result" <<L
#!/bin/sh
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
echo '{"type":"result","subtype":"success","is_error":false,"duration_ms":91234,"duration_api_ms":40118,"num_turns":$usage_turns,"result":"done","session_id":"4d1a","total_cost_usd":0.31,"usage":{"input_tokens":37,"cache_creation_input_tokens":41002,"cache_read_input_tokens":903117,"output_tokens":5140}}'
exit 0
L
chmod +x "$stub/leaf-result"
sup_run "$usage_work" "$SUP" develop-red "$stub/leaf-result"
usage_code=$?
usage_got_turns="$(event_field "$usage_work" usage num_turns)"
{ [[ "$usage_code" == 0 ]] && [[ "$usage_got_turns" == "$usage_turns" ]]; } && ok \
  || no "a leaf whose log ends in a result record leaves exactly one usage event carrying that record's numbers (code=$usage_code, num_turns=$usage_got_turns want $usage_turns)"


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

killed_work="$work/killed"
killed_window=1
sup_run "$killed_work" VERI_HEARTBEAT="$killed_window" "$SUP" develop-red "$stub/leaf-hang"
killed_code=$?
killed_usage="$(event_count "$killed_work" usage)"
killed_recorded="$(cat "$killed_work/.tdd/develop-red.exit" 2>/dev/null || echo '<missing>')"
{ [[ "$killed_usage" == 0 ]] \
  && [[ "$killed_code" == 2 ]] \
  && [[ "$killed_recorded" == 2 ]]; } && ok \
  || no "a killed leaf leaves no usage event and the supervisor still exits 2 and records 2 (usage lines=$killed_usage want 0, code=$killed_code want 2, .exit=$killed_recorded want 2)"

harvest_fail_work="$work/harvest-fail"
cat > "$stub/leaf-bad-result" <<'L'
#!/bin/sh
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"leaf: ran the suite"}]}}'
echo '{"type":"result","subtype":"success","is_error":false,"duration_ms":91234,"duration_api_ms":40118,"num_turns":7,"result":"done","session_id":"4d1a","total_cost_usd":0.31}'
exit 0
L
chmod +x "$stub/leaf-bad-result"
sup_run "$harvest_fail_work" "$SUP" develop-red "$stub/leaf-bad-result"
harvest_fail_code=$?
harvest_fail_usage="$(event_count "$harvest_fail_work" usage)"
harvest_fail_recorded="$(cat "$harvest_fail_work/.tdd/develop-red.exit" 2>/dev/null || echo '<missing>')"
{ [[ "$harvest_fail_usage" == 0 ]] \
  && [[ "$harvest_fail_code" == 0 ]] \
  && [[ "$harvest_fail_recorded" == 0 ]]; } && ok \
  || no "a failing harvester leaves the supervisor's exit code and completion file unchanged (usage lines=$harvest_fail_usage want 0, code=$harvest_fail_code want 0, .exit=$harvest_fail_recorded want 0)"

# hazard: BSD env reads a -u after an assignment as the utility to run, so unset in a subshell.
sup_run_no_model() {
  ( unset VERI_MODEL VERI_MODEL_DEVELOPER VERI_MODEL_VERIFIER
    sup_run "$@" )
}

model_work="$work/model"
model_value=sonnet

model_run() {
  local arm="$1"; shift
  sup_run_no_model "$model_work/$arm" "$@" "$SUP" develop-red "$stub/leaf-ok"
}

model_run set VERI_MODEL="$model_value"
model_set_code=$?
model_run unset
model_unset_code=$?
model_set_got="$(event_field   "$model_work/set"   launch model)"
model_unset_got="$(event_field "$model_work/unset" launch model)"
{ [[ "$model_set_code" == 0 ]] && [[ "$model_unset_code" == 0 ]] \
  && [[ "$model_set_got"   == "$model_value" ]] \
  && [[ "$model_unset_got" == "" ]]; } && ok \
  || no "the launch event carries the resolved model, and an empty one when the run chose none (VERI_MODEL=$model_value: code=$model_set_code model=$model_set_got want $model_value; none set: code=$model_unset_code model=$(printf '%q' "$model_unset_got") want '')"

argv_work="$work/argv"
argv_model=sonnet
argv_prompt='pin the argv'
mkdir -p "$argv_work"
printf '%s' "$argv_prompt" > "$argv_work/prompt.txt"

cat > "$stub/claude-argv" <<'L'
#!/bin/sh
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
L
chmod +x "$stub/claude-argv"

argv_run() {
  local arm="$1"; shift
  sup_run_no_model "$argv_work/$arm" CLAUDE_BIN="$stub/claude-argv" ARGV_OUT="$argv_work/$arm.argv" \
    "$@" "$SUP" develop-red "$HERE/../run-leaf.sh" "$argv_work/prompt.txt"
}

argv_run set VERI_MODEL="$argv_model"
argv_set_code=$?
argv_run unset
argv_unset_code=$?
argv_today="$(printf '%s\n' -p "$argv_prompt" --output-format stream-json --verbose)"
argv_set_got="$(cat   "$argv_work/set.argv"   2>/dev/null || echo '<<no argv>>')"
argv_unset_got="$(cat "$argv_work/unset.argv" 2>/dev/null || echo '<<no argv>>')"
{ [[ "$argv_set_code" == 0 ]] && [[ "$argv_unset_code" == 0 ]] \
  && [[ "$argv_set_got"   == *"--model"$'\n'"$argv_model"* ]] \
  && [[ "$argv_unset_got" == "$argv_today" ]]; } && ok \
  || no "a supervised leaf's claude argv carries --model only when the run chose a model (VERI_MODEL=$argv_model: code=$argv_set_code argv=$(printf '%q' "$argv_set_got") want a --model/$argv_model pair; none set: code=$argv_unset_code argv=$(printf '%q' "$argv_unset_got") want $(printf '%q' "$argv_today"))"

session_work="$work/session"
session_vars=(CLAUDECODE CLAUDE_CODE_SESSION_ID CLAUDE_CODE_HOST_SESSION_ID
  CLAUDE_CODE_MESSAGING_SOCKET CLAUDE_CODE_MESSAGING_TOKEN CLAUDE_PID
  CLAUDE_CODE_CHILD_SESSION CLAUDE_CODE_ENTRYPOINT CLAUDE_AUTO_BACKGROUND_TASKS)
session_env=()
for v in "${session_vars[@]}"; do session_env+=("$v=from-the-conductor"); done
cat > "$stub/claude-env" <<'L'
#!/bin/sh
env > "$ENV_OUT"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
L
chmod +x "$stub/claude-env"
sup_run_no_model "$session_work" "${session_env[@]}" CLAUDE_BIN="$stub/claude-env" \
  ENV_OUT="$session_work/claude.env" "$SUP" develop-red "$HERE/../run-leaf.sh" "$argv_work/prompt.txt"
session_leaked=()
if [[ -f "$session_work/claude.env" ]]; then
  for v in "${session_vars[@]}"; do
    grep -E "^$v=" "$session_work/claude.env" > /dev/null && session_leaked+=("$v")
  done
else
  session_leaked=("<the leaf's claude was never started>")
fi
[[ ${#session_leaked[@]} == 0 ]] && ok \
  || no "a leaf launched as supervise.sh <name> run-leaf.sh starts claude without the caller's session variables (#621) (reached it: ${session_leaked[*]})"
skill_work="$work/skill"
skill_want="$(git -C "$SCRIPTS" rev-parse HEAD 2>/dev/null || echo '<no-sha>')"
sup_run "$skill_work" env -u VERI_SKILL_COMMIT "$SUP" develop-red "$stub/leaf-ok"
skill_code=$?
skill_got="$(event_field "$skill_work" launch skill_commit)"
{ [[ "$skill_code" == 0 ]] \
  && [[ "$skill_want" =~ ^[0-9a-f]{40}$ ]] \
  && [[ "$skill_got" == "$skill_want" ]]; } && ok \
  || no "a launch event carries the skill's own commit in skill_commit (code=$skill_code, skill_commit=$skill_got want $skill_want)"

nogit_skill="$work/nogit-skill"
mkdir -p "$nogit_skill/lib"
cp "$SCRIPTS"/*.sh "$nogit_skill/"
cp "$SCRIPTS"/lib/*.sh "$nogit_skill/lib/"
nogit_resolves="$(git -C "$nogit_skill" rev-parse HEAD 2>/dev/null || echo '<none>')"
nogit_work="$work/nogit-run"
sup_run "$nogit_work" env -u VERI_SKILL_COMMIT "$nogit_skill/supervise.sh" develop-red "$stub/leaf-ok"
nogit_code=$?
nogit_got="$(event_field "$nogit_work" launch skill_commit)"
{ [[ "$nogit_code" == 0 ]] \
  && [[ "$nogit_resolves" == '<none>' ]] \
  && [[ "$nogit_got" == unknown ]]; } && ok \
  || no "a skill outside a git clone records skill_commit as the literal unknown (code=$nogit_code, git says=$nogit_resolves want <none>, skill_commit=$nogit_got want unknown)"


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


result_kill_work="$work/result-kill"
result_hang_stub leaf-result-hang success false 'VERDICT: PASS'
sup_run "$result_kill_work" VERI_HEARTBEAT=1 "$SUP" verify-red "$stub/leaf-result-hang"
result_kill_code=$?
result_kill_rc="$(leaf_rc "$result_kill_work")"
{ [[ "$result_kill_code" == 0 ]] \
  && [[ "$result_kill_rc" == '<missing>' ]]; } && ok \
  || no "a killed leaf whose log holds a terminal result record is reported with the leaf's own outcome, not killed-stuck (code=$result_kill_code want 0, .rc=$result_kill_rc want <missing>)"


error_kill_work="$work/error-kill"
result_hang_stub leaf-error-hang error_during_execution true 'the suite did not finish'
sup_run "$error_kill_work" VERI_HEARTBEAT=1 "$SUP" verify-red "$stub/leaf-error-hang"
error_kill_code=$?
error_kill_rc="$(leaf_rc "$error_kill_work")"
{ [[ "$error_kill_code" == 1 ]] \
  && [[ "$error_kill_rc" == '<missing>' ]]; } && ok \
  || no "a killed leaf whose terminal result record is an error is reported exit 1, not exit 0 (code=$error_kill_code want 1, .rc=$error_kill_rc want <missing>)"


result_once_work="$work/result-once"
result_hang_stub leaf-result-hang-counted success false 'VERDICT: PASS' 'echo attempt >> .attempts'
sup_direct "$result_once_work" leaf-result-hang-counted 1 -u VERI_STUCK_RETRIES >/dev/null 2>&1
result_once_code=$?
result_once_attempts="$(wc -l < "$result_once_work/.attempts" 2>/dev/null | tr -d ' ')"
result_once_retry="$(event_field "$result_once_work" retry cause)"
{ [[ "$result_once_code" == 0 ]] \
  && [[ "$result_once_attempts" == 1 ]] \
  && [[ "$result_once_retry" == '<<0 retry lines>>' ]]; } && ok \
  || no "a leaf recovered from its terminal result record is launched exactly once, with no stuck-retry (code=$result_once_code want 0, attempts=$result_once_attempts want 1, retry=$result_once_retry want <<0 retry lines>>)"


result_text_work="$work/result-text"
result_hang_stub leaf-verdict-hang success false 'VERDICT: PASS\nREASON: the new case fails on the eight session-handle checks'
result_text_out="$(sup_direct "$result_text_work" leaf-verdict-hang 1 VERI_STUCK_RETRIES=0 2>/dev/null)"
result_text_reason="$(printf '%s\n' "$result_text_out" | "$SCRIPTS/parse-verdict.sh" 2>&1)"
result_text_code=$?
{ [[ "$result_text_code" == 0 ]] \
  && [[ "$result_text_reason" == *'eight session-handle checks'* ]]; } && ok \
  || no "a recovered leaf's captured stdout ends with the clean result text, so parse-verdict.sh reads its verdict (verdict code=$result_text_code want 0, reason=$result_text_reason want the leaf's REASON text)"



nores_work="$work/no-result"
mkdir -p "$nores_work"
cat > "$stub/leaf-noresult-hang" <<'L'
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
nores_status="$(grep '^supervise\[verify-red\]: killed-stuck' "$nores_work/err" || echo '<no status line>')"
nores_cause="${nores_status#supervise\[verify-red\]: killed-stuck — }"
{ [[ "$nores_code" == 2 ]] \
  && heartbeat_kill "$nores_cause" "$nores_window"; } && ok \
  || no "a killed leaf whose log holds no terminal result record is still exit 2 with its kill cause on stderr (code=$nores_code want 2, status line=$nores_status want a killed-stuck line whose cause reads 'no heartbeat for Ns (window ${nores_window}s)')"

header_text="$(awk 'NR > 1 { if ($0 !~ /^#/) exit; sub(/^# ?/, ""); print }' "$SUP" | tr '\n' ' ')"
header_unstated() {
  local where regex
  while IFS='|' read -r where regex; do
    [[ -n "$where" ]] || continue
    grep -qE "$regex" <<< "$header_text" || printf ' %s' "$where"
  done
}
header_misses="$(header_unstated <<'CLAIMS'
stream-finishes-before-rc|(finish|complete)[a-z]* .{0,120}before .{0,80}(rc file|rcfile|\.rc)
kill-is-not-proof|kill.{0,160}not proof
CLAIMS
)"

[[ -z "$header_misses" ]] && ok \
  || no "supervise.sh's header records that a leaf's stream can finish before its rc file is written, so a kill is not proof that no answer was obtained (unstated:$header_misses)"

pid_work="$work/pid-record"
mkdir -p "$pid_work"
cat > "$stub/leaf-pid-seen" <<'L'
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


term_work="$work/term-handler"
mkdir -p "$term_work"
cat > "$stub/leaf-term-sleep" <<'L'
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

intr_problems=()
for intr_sig in INT HUP; do
  intr_work="$work/signal-$intr_sig"
  mkdir -p "$intr_work"
  # Without job control an async command starts with SIGINT ignored; set -m keeps it at its default.
  set -m
  ( cd "$intr_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
  intr_sup=$!
  set +m
  for _ in $(seq 1 50); do [[ -s "$intr_work/leaf-pid" ]] && break; sleep 0.1; done
  intr_leaf="$(tr -d '[:space:]' < "$intr_work/leaf-pid" 2>/dev/null)"
  kill -"$intr_sig" "$intr_sup" 2>/dev/null
  wait "$intr_sup"
  intr_code=$?
  intr_exit="$({ tr -d '[:space:]' < "$intr_work/.tdd/develop-red.exit"; } 2>/dev/null || echo '<missing>')"
  intr_alive="no"
  if [[ -n "$intr_leaf" ]]; then
    for _ in $(seq 1 20); do kill -0 "$intr_leaf" 2>/dev/null || break; sleep 0.1; done
    if kill -0 "$intr_leaf" 2>/dev/null; then intr_alive="yes"; kill -KILL "$intr_leaf" 2>/dev/null; fi
  else
    intr_alive="<leaf never started>"
  fi
  { [[ "$intr_code" == 2 ]] && [[ "$intr_exit" == 2 ]] && [[ "$intr_alive" == no ]]; } \
    || intr_problems+=("$intr_sig: code=$intr_code want 2, exit file=$intr_exit want 2, leaf alive=$intr_alive want no")
done
[[ "${#intr_problems[@]}" -eq 0 ]] && ok \
  || no "supervise.sh sent INT or HUP does what TERM does: writes 2 to its completion file, exits 2 and leaves no leaf process behind (${intr_problems[*]})"

waitlive_work="$work/wait-live-supervisor"
mkdir -p "$waitlive_work"
( cd "$waitlive_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
waitlive_sup=$!
for _ in $(seq 1 50); do [[ -s "$waitlive_work/leaf-pid" ]] && break; sleep 0.1; done
waitlive_leaf="$(tr -d '[:space:]' < "$waitlive_work/leaf-pid" 2>/dev/null)"
( cd "$waitlive_work" && env VERI_POLL=0.02 "$SCRIPTS/wait-leaf.sh" develop-red 0 ) >/dev/null 2>"$waitlive_work/wait-err"
waitlive_code=$?
waitlive_err="$(cat "$waitlive_work/wait-err")"
kill -TERM "$waitlive_sup" 2>/dev/null
wait "$waitlive_sup"
if [[ -n "$waitlive_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$waitlive_leaf" 2>/dev/null || break; sleep 0.1; done
  kill -0 "$waitlive_leaf" 2>/dev/null && kill -KILL "$waitlive_leaf" 2>/dev/null
fi
{ [[ -n "$waitlive_leaf" ]] && [[ "$waitlive_code" == 3 ]] && [[ -z "$waitlive_err" ]]; } && ok \
  || no "wait-leaf.sh <name> 0 against a live supervisor of that leaf exits 3, not 2, with nothing on stderr (leaf pid=${waitlive_leaf:-<never started>}; code=$waitlive_code want 3; stderr='$waitlive_err' want empty)"

name_work="$work/unknown-name"
sup_run "$name_work" "$SUP" frobnicate-red "$stub/leaf-ok"
name_code=$?
name_launch_events="$(event_count "$name_work" launch)"
{ [[ "$name_code" == 0 ]] \
  && [[ "$name_launch_events" == 0 || "$name_launch_events" == '<<no event log>>' ]]; } && ok \
  || no "a leaf name leaf-role.sh refuses still runs the leaf to completion but marks no launch event (code=$name_code want 0, launch events=$name_launch_events want 0 or no event log)"

vrole_work="$work/verdict-role"
mkdir -p "$vrole_work"
( cd "$vrole_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" verdict-plan "$stub/leaf-ok" ) >/dev/null 2>"$vrole_work/err"
vrole_code=$?
vrole_exit="$(cat "$vrole_work/.tdd/verdict-plan.exit" 2>/dev/null || echo '<missing>')"
vrole_launch="$(event_count "$vrole_work" launch)"
vrole_exits="$(event_count "$vrole_work" exit)"
vrole_role_lines="$(grep -c '^leaf-role:' "$vrole_work/err")"
{ [[ "$vrole_code" == 0 ]] && [[ "$vrole_exit" == 0 ]] && [[ "$vrole_role_lines" == 0 ]] \
  && [[ "$vrole_launch" == 0 || "$vrole_launch" == '<<no event log>>' ]] \
  && [[ "$vrole_exits" == 0 || "$vrole_exits" == '<<no event log>>' ]]; } && ok \
  || no "#956: supervise.sh verdict-plan writes no leaf-role: line to stderr, exits 0, records 0 in .tdd/verdict-plan.exit and appends no launch or exit event (code=$vrole_code want 0, exit file=$vrole_exit want 0, leaf-role lines=$vrole_role_lines want 0, launch events=$vrole_launch want 0 or no event log, exit events=$vrole_exits want 0 or no event log, err=$(cat "$vrole_work/err"))"

vharv_work="$work/verdict-harvest"
mkdir -p "$vharv_work"
( cd "$vharv_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" verdict-plan "$stub/leaf-ok" ) >/dev/null 2>"$vharv_work/err"
vharv_lines="$(grep -c '^harvest-usage.sh:' "$vharv_work/err")"
[[ "$vharv_lines" == 0 ]] && ok \
  || no "#956: supervise.sh verdict-plan whose log holds no closing result record writes no harvest-usage.sh: line to stderr (harvest-usage lines=$vharv_lines want 0, err=$(cat "$vharv_work/err"))"

vbogus_work="$work/bogus-role"
mkdir -p "$vbogus_work"
( cd "$vbogus_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" bogus-x "$stub/leaf-ok" ) >/dev/null 2>"$vbogus_work/err"
vbogus_lines="$(grep -c "^leaf-role: leaf name 'bogus-x' has an unknown leading word" "$vbogus_work/err")"
(( vbogus_lines >= 1 )) && ok \
  || no "#956: supervise.sh bogus-x, neither a known role nor verdict-*, still writes the leaf-role: unknown leading word line to stderr (leaf-role lines=$vbogus_lines want >= 1, err=$(cat "$vbogus_work/err"))"

rharv_problems=()
for rharv_name in develop-red verify-plan; do
  rharv_work="$work/role-harvest-$rharv_name"
  mkdir -p "$rharv_work"
  ( cd "$rharv_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
      VERI_KILL_POLL=0.01 "$SUP" "$rharv_name" "$stub/leaf-ok" ) >/dev/null 2>"$rharv_work/err"
  rharv_lines="$(grep -c "^harvest-usage.sh: no closing result record in .tdd/$rharv_name.log" "$rharv_work/err")"
  (( rharv_lines == 1 )) \
    || rharv_problems+=("$rharv_name: harvest-usage lines=$rharv_lines want 1, err=$(cat "$rharv_work/err")")
done
[[ "${#rharv_problems[@]}" -eq 0 ]] && ok \
  || no "#956: a develop-* or verify-* supervision whose log holds no closing result record still writes the harvest-usage.sh: no closing result record line to stderr (${rharv_problems[*]})"

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

preserve_work="$work/preserve"
preserve_issue=409
preserve_step=6
preserve_window=1
mkdir -p "$preserve_work"
new_repo -b main "$preserve_work" >/dev/null 2>&1
git -C "$preserve_work" config user.name veri
git -C "$preserve_work" config user.email veri@example.test
printf '.tdd/\n.test-clock*\n' > "$preserve_work/.gitignore"
printf 'the step this leaf never finished\n' > "$preserve_work/src.txt"
git -C "$preserve_work" add -A >/dev/null 2>&1
git -C "$preserve_work" commit -q -m "initial" >/dev/null 2>&1

cat > "$stub/leaf-hang-counting" <<'L'
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

preserve_refs="$(git -C "$preserve_work" for-each-ref --format='%(refname)' \
  "refs/veri/attempts/$preserve_issue/$preserve_step/" 2>/dev/null)"
preserve_ref_count="$(printf '%s\n' "$preserve_refs" | grep -c . || true)"
preserve_trees="$(while read -r ref; do
    [[ -n "$ref" ]] || continue
    git -C "$preserve_work" show "$ref:attempts.txt" 2>/dev/null | grep -c . || true
  done <<< "$preserve_refs" | sort | xargs)"
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

owner_work="$work/live-owner"
mkdir -p "$owner_work"
cat > "$stub/leaf-second" <<'L'
: > second-ran
exit 0
L
chmod +x "$stub/leaf-second"
( cd "$owner_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
owner_sup=$!
for _ in $(seq 1 50); do [[ -s "$owner_work/leaf-pid" ]] && break; sleep 0.1; done
owner_leaf="$(tr -d '[:space:]' < "$owner_work/leaf-pid" 2>/dev/null)"
sup_in "$owner_work" verify-green "$stub/leaf-second" >/dev/null 2>"$owner_work/err"
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

same_work="$work/live-owner-same-name"
mkdir -p "$same_work"
( cd "$same_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
same_sup=$!
for _ in $(seq 1 50); do [[ -s "$same_work/leaf-pid" ]] && break; sleep 0.1; done
same_leaf="$(tr -d '[:space:]' < "$same_work/leaf-pid" 2>/dev/null)"
sup_in "$same_work" revise-green-1 "$stub/leaf-second" >/dev/null 2>"$same_work/err"
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

rm_work="$work/live-owner-after-rm"
mkdir -p "$rm_work"
( cd "$rm_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" revise-green-1 "$stub/leaf-term-sleep" ) >/dev/null 2>&1 &
rm_sup=$!
for _ in $(seq 1 50); do [[ -s "$rm_work/leaf-pid" ]] && break; sleep 0.1; done
rm_leaf="$(tr -d '[:space:]' < "$rm_work/leaf-pid" 2>/dev/null)"
( cd "$rm_work" && rm -f .tdd/revise-green-1.exit .tdd/revise-green-1.pid )
sup_in "$rm_work" revise-green-1 "$stub/leaf-second" >/dev/null 2>"$rm_work/err"
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
sup_in "$dead_work" revise-green-1 "$stub/leaf-second" >/dev/null 2>"$dead_work/err"
dead_code=$?
dead_second="no"; [[ -e "$dead_work/second-ran" ]] && dead_second="yes"
{ [[ -n "$dead_leaf" ]] && [[ "$dead_record" == "$dead_sup revise-green-1" ]] \
  && [[ "$dead_code" == 0 ]] && [[ "$dead_second" == yes ]]; } && ok \
  || no "#471: a record left by a supervised leaf whose process is gone does not refuse the next launch (first leaf pid=${dead_leaf:-<never started>}; record='$dead_record' want '$dead_sup revise-green-1'; code=$dead_code want 0, second leaf ran=$dead_second want yes, stderr='$(cat "$dead_work/err")')"

done_work="$work/finished-owner"
mkdir -p "$done_work"
cat > "$stub/leaf-mark" <<'L'
echo "$1" >> ran
exit 0
L
chmod +x "$stub/leaf-mark"
sup_in "$done_work" revise-green-1 "$stub/leaf-mark" first >/dev/null 2>"$done_work/err1"
done_code1=$?
done_record="$(cat "$done_work/.tdd/leaf.owner" 2>/dev/null || echo '<missing>')"
( cd "$done_work" && rm -f .tdd/revise-green-1.exit .tdd/revise-green-1.pid )
sup_in "$done_work" revise-green-1 "$stub/leaf-mark" second >/dev/null 2>"$done_work/err2"
done_code2=$?
( cd "$done_work" && rm -f .tdd/verify-green.exit .tdd/verify-green.pid )
sup_in "$done_work" verify-green "$stub/leaf-mark" third >/dev/null 2>"$done_work/err3"
done_code3=$?
done_ran="$(tr '\n' ' ' < "$done_work/ran" 2>/dev/null)"
{ [[ "$done_record" == *' revise-green-1' ]] && [[ "$done_code1" == 0 ]] && [[ "$done_code2" == 0 ]] \
  && [[ "$done_code3" == 0 ]] && [[ "$done_ran" == 'first second third ' ]]; } && ok \
  || no "#471: a launch after the previous supervised leaf finished runs as today, under the same name and a different one (record='$done_record' want '<pid> revise-green-1'; codes=$done_code1/$done_code2/$done_code3 want 0/0/0; ran='$done_ran' want 'first second third '; stderr='$(cat "$done_work/err2" "$done_work/err3" 2>/dev/null)')"

nest_work="$work/nested-verifier"
mkdir -p "$nest_work"
cat > "$stub/leaf-verdict-wrapper" <<'L'
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

fin_work="$work/live-owner-finished-exit"
live_owner_tree "$fin_work"
printf '0\n' > "$fin_work/.tdd/develop-green.exit"
sup_in "$fin_work" verdict-green "$stub/leaf-second" >/dev/null 2>"$fin_work/err"
fin_code=$?
fin_ran="no"; [[ -e "$fin_work/second-ran" ]] && fin_ran="yes"
{ [[ "$fin_code" == 0 ]] && [[ "$fin_ran" == yes ]]; } && ok \
  || no "#618: a launch under another name is not refused when the recorded leaf is alive but .tdd/<owner-name>.exit already exists (code=$fin_code want 0; command ran=$fin_ran want yes; stderr='$(cat "$fin_work/err")')"

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

bad_settled_work="$(scratch_dir)"
mkdir -p "$bad_settled_work/.tdd"
bad_settled_problems=()
for bad in '' 0 abc 1.5; do
  printf '%s\n' "$bad" > "$bad_settled_work/.tdd/issue-954-timeout"
  ( cd "$bad_settled_work" && env -u VERI_TIMEOUT -u VERI_STEP VERI_ISSUE=954 VERI_STUCK_RETRIES=0 \
      VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-ok" ) >/dev/null 2>"$bad_settled_work/err"
  bad_settled_code=$?
  [[ "$bad_settled_code" == 2 ]] ||
    bad_settled_problems+=("record '$bad': want exit 2, got $bad_settled_code")
  grep -F '.tdd/issue-954-timeout' "$bad_settled_work/err" > /dev/null ||
    bad_settled_problems+=("record '$bad': want stderr naming .tdd/issue-954-timeout, got: $(cat "$bad_settled_work/err")")
done
{ [[ "${#bad_settled_problems[@]}" -eq 0 ]]; } && ok \
  || no "#954: with VERI_TIMEOUT unset, a .tdd/issue-954-timeout record that is empty or not a whole number >= 1 is refused with exit 2 and a stderr line naming the file, not read as 900 or misread (${bad_settled_problems[*]})"

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

usage_line='usage: supervise.sh <name> <cmd> [args...]'
refusal_problems=()
for refusal_args in none empty name-only; do
  refusal_work="$(scratch_dir)"
  refusal_io="$(scratch_dir)"
  case "$refusal_args" in
    none) ( cd "$refusal_work" && "$SUP" ) >"$refusal_io/out" 2>"$refusal_io/err" ;;
    empty) ( cd "$refusal_work" && "$SUP" "" ) >"$refusal_io/out" 2>"$refusal_io/err" ;;
    name-only) ( cd "$refusal_work" && "$SUP" develop-red ) >"$refusal_io/out" 2>"$refusal_io/err" ;;
  esac
  refusal_code=$?
  refusal_want_err="$usage_line"
  [[ "$refusal_args" == name-only ]] && refusal_want_err="supervise: missing <cmd>"$'\n'"$usage_line"
  [[ "$refusal_code" == 2 ]] || refusal_problems+=("$refusal_args: want exit 2, got $refusal_code")
  [[ ! -s "$refusal_io/out" ]] || refusal_problems+=("$refusal_args: want no stdout, got '$(cat "$refusal_io/out")'")
  [[ "$(cat "$refusal_io/err"; echo .)" == "$refusal_want_err"$'\n.' ]] \
    || refusal_problems+=("$refusal_args: want stderr '$refusal_want_err', got '$(cat "$refusal_io/err")'")
  [[ ! -e "$refusal_work/.tdd" ]] || refusal_problems+=("$refusal_args: want no .tdd, found one")
done
{ [[ "${#refusal_problems[@]}" -eq 0 ]]; } && ok \
  || no "supervise.sh with no argument or an empty <name> exits 2 with stderr exactly the usage line, and with develop-red alone exits 2 with stderr exactly 'supervise: missing <cmd>' then the usage line, nothing on stdout and no .tdd created (${refusal_problems[*]})"

linked_home="$(scratch_dir)"
ln -s "$(cd "$SCRIPTS/.." && pwd)" "$linked_home/skill"
linked_sup="$linked_home/skill/scripts/supervise.sh"
linked_caller="$(scratch_dir)"
new_repo -b main "$linked_caller" >/dev/null 2>&1
printf '.tdd/\n.test-clock*\n' > "$linked_caller/.gitignore"
git -C "$linked_caller" add -A >/dev/null 2>&1
git -C "$linked_caller" commit -q -m initial >/dev/null 2>&1
linked_issue=1073
linked_step=5
linked_want_commit="$(git -C "$SCRIPTS" rev-parse HEAD 2>/dev/null || echo '<no-sha>')"
linked_beside_before="$(ls -d "$SCRIPTS/.tdd" "$SCRIPTS/../.tdd" "$linked_home/.tdd" 2>/dev/null)"
linked_problems=()
sup_run "$linked_caller" env -u VERI_SKILL_COMMIT "$linked_sup" develop-red "$stub/leaf-result"
linked_ok_code=$?
( cd "$linked_caller" && env -u VERI_SKILL_COMMIT VERI_STUCK_RETRIES=0 \
    VERI_ISSUE="$linked_issue" VERI_STEP="$linked_step" VERI_HEARTBEAT=1 VERI_TIMEOUT=30 \
    VERI_POLL=0.02 VERI_KILL_POLL=0.01 "$linked_sup" develop-green "$stub/leaf-hang" ) >/dev/null 2>&1
linked_kill_code=$?
[[ "$linked_ok_code" == 0 ]] || linked_problems+=("result leaf: want exit 0, got $linked_ok_code")
[[ "$linked_kill_code" == 2 ]] || linked_problems+=("hung leaf: want exit 2, got $linked_kill_code")
for linked_event in launch exit; do
  linked_n="$(event_count "$linked_caller" "$linked_event")"
  [[ "$linked_n" == 2 ]] || linked_problems+=("$linked_event events in the caller's .tdd/events.jsonl: want 2, got $linked_n")
done
linked_usage="$(event_field "$linked_caller" usage num_turns)"
[[ "$linked_usage" == "$usage_turns" ]] || linked_problems+=("usage event num_turns: want $usage_turns, got $linked_usage")
linked_commits="$(python3 -c '
import sys, json
for line in open(sys.argv[1]):
    obj = json.loads(line)
    if obj.get("event") == "launch":
        print(obj.get("skill_commit", "<missing>"))
' "$linked_caller/.tdd/events.jsonl" 2>/dev/null | sort -u | xargs)"
[[ "$linked_want_commit" =~ ^[0-9a-f]{40}$ && "$linked_commits" == "$linked_want_commit" ]] \
  || linked_problems+=("launch skill_commit: want $linked_want_commit, got '$linked_commits'")
linked_refs="$(git -C "$linked_caller" for-each-ref --format='%(refname)' \
  "refs/veri/attempts/$linked_issue/$linked_step/" 2>/dev/null | grep -c . || true)"
[[ "$linked_refs" == 1 ]] || linked_problems+=("preserved attempts under refs/veri/attempts/$linked_issue/$linked_step/: want 1, got $linked_refs")
for linked_file in develop-red.log develop-red.exit develop-red.pid develop-green.log develop-green.exit develop-green.pid; do
  [[ -f "$linked_caller/.tdd/$linked_file" ]] || linked_problems+=("want .tdd/$linked_file under the caller, missing")
done
linked_beside_after="$(ls -d "$SCRIPTS/.tdd" "$SCRIPTS/../.tdd" "$linked_home/.tdd" 2>/dev/null)"
[[ "$linked_beside_after" == "$linked_beside_before" ]] \
  || linked_problems+=("want no .tdd beside the skill, found: $linked_beside_after")
{ [[ "${#linked_problems[@]}" -eq 0 ]]; } && ok \
  || no "supervise.sh run through a symlink to the skill directory from another working directory answers as in place: events, usage and the preserved attempt land in the caller's .tdd, skill_commit is the skill clone's HEAD, and no .tdd appears beside the skill (${linked_problems[*]})"


childtree_work="$work/hang-with-child"
mkdir -p "$childtree_work"
cat > "$stub/leaf-hang-child" <<'L'
#!/bin/sh
echo $$ > leaf-pid
sleep 60 &
echo $! > child-pid
echo "leaf: starting"; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60; echo "unreachable"
L
chmod +x "$stub/leaf-hang-child"
( cd "$childtree_work" && env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=1 VERI_TIMEOUT=30 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-hang-child" ) >/dev/null 2>&1
childtree_code=$?
childtree_alive=()
for childtree_file in leaf-pid child-pid; do
  childtree_pid="$(tr -d '[:space:]' < "$childtree_work/$childtree_file" 2>/dev/null)"
  if [[ -z "$childtree_pid" ]]; then childtree_alive+=("$childtree_file: never recorded"); continue; fi
  for _ in $(seq 1 20); do kill -0 "$childtree_pid" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$childtree_pid" 2>/dev/null; then
    childtree_alive+=("$childtree_file: pid $childtree_pid still alive")
    kill -KILL "$childtree_pid" 2>/dev/null
  fi
done
{ [[ "$childtree_code" == 2 ]] && [[ "${#childtree_alive[@]}" -eq 0 ]]; } && ok \
  || no "a hung leaf that started a background child of its own and recorded its pid leaves neither the leaf nor the child alive after the heartbeat kill (code=$childtree_code want 2; ${childtree_alive[*]:-none alive})"


termign_work="$work/term-ignored"
mkdir -p "$termign_work"
cat > "$stub/leaf-hang-pid" <<'L'
#!/bin/sh
echo $$ > leaf-pid
echo "leaf: starting"; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; exec sleep 60
L
chmod +x "$stub/leaf-hang-pid"
( trap '' TERM; cd "$termign_work" && exec env VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=1 VERI_TIMEOUT=30 VERI_POLL=0.02 \
    VERI_KILL_POLL=0.01 "$SUP" develop-red "$stub/leaf-hang-pid" ) >/dev/null 2>&1 &
termign_sup=$!
for _ in $(seq 1 100); do kill -0 "$termign_sup" 2>/dev/null || break; sleep 0.1; done
termign_code="<still running after 10s>"
if ! kill -0 "$termign_sup" 2>/dev/null; then wait "$termign_sup"; termign_code=$?; fi
termign_exit="$({ tr -d '[:space:]' < "$termign_work/.tdd/develop-red.exit"; } 2>/dev/null || echo '<missing>')"
termign_leaf="$(tr -d '[:space:]' < "$termign_work/leaf-pid" 2>/dev/null)"
termign_alive="no"
if [[ -n "$termign_leaf" ]]; then
  for _ in $(seq 1 20); do kill -0 "$termign_leaf" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$termign_leaf" 2>/dev/null; then termign_alive="yes"; kill -KILL "$termign_leaf" 2>/dev/null; fi
else
  termign_alive="<leaf never started>"
fi
if kill -0 "$termign_sup" 2>/dev/null; then wait "$termign_sup"; fi
{ [[ "$termign_code" == 2 ]] && [[ "$termign_exit" == 2 ]] && [[ "$termign_alive" == no ]]; } && ok \
  || no "a supervisor started with TERM ignored, whose silent leaf is killed for silence, leaves no leaf process alive after the KILL escalation and exits 2 with 2 in .tdd/<name>.exit (code=$termign_code want 2, exit file=$termign_exit want 2, leaf alive=$termign_alive want no)"

finish
