#!/usr/bin/env bash
# Tests for scripts/orchestrate.sh — the loop above the conductor: it asks
# solvable-issues.sh which issues veri may take, launches one conductor per issue through
# run-conductor.sh, and stops once nothing is left to take.
#
# Contract under test:
#   orchestrate.sh  → one run-conductor.sh launch per solvable issue; exit 0 once
#                     solvable-issues.sh exits 3; exit 2, launching nothing, when it exits
#                     other than 0 or 3.
#   VERI_CONDUCTOR_CTX_BUDGET (default 120000, a whole number or exit 2)
#                   → a conductor whose context crosses it is stopped after its next step-done
#                     result and relaunched for the same issue with the same argv.
#   A conductor exiting 0 with an unchecked ledger step is relaunched; one that wrote
#   `.tdd/parked/<n>.md` is recorded as parked and the next solvable issue is taken.
#
# Run: scripts/tests/orchestrate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

work="$(scratch_dir)"

scripts="$work/scripts"
mkdir -p "$scripts"
cp "$HERE/../orchestrate.sh" "$scripts/orchestrate.sh" 2>/dev/null
cp -R "$HERE/../lib" "$HERE/../veri" "$scripts/"

cat > "$scripts/solvable-issues.sh" <<'STUB'
#!/bin/sh
calls=$(($(cat "$SOLVABLE.calls" 2>/dev/null || echo 0) + 1))
echo "$calls" > "$SOLVABLE.calls"
[ "$calls" -le 20 ] || exit 3
[ -s "$SOLVABLE" ] || exit 3
cat "$SOLVABLE"
STUB

cat > "$scripts/run-conductor.sh" <<'STUB'
#!/bin/sh
echo "$1" >> "$LAUNCHES"
grep -vx -- "$1" "$SOLVABLE" > "$SOLVABLE.next"
mv "$SOLVABLE.next" "$SOLVABLE"
STUB
chmod +x "$scripts"/*.sh

orchestrate() {
  (cd "$work" && "$1/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
  rc=$?
}

conductor_stub() {
  mkdir -p "$1"
  cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$1/"
  cp -R "$scripts/lib" "$scripts/veri" "$1/"
  {
    printf '#!/bin/sh\n"%s/run-conductor.sh" "$1"\n' "$scripts"
    cat <<PRELUDE
# A stopped conductor must be stopped by a signal, not by its writes failing, so this stub
# IGNORES SIGPIPE — the state CI's Linux was observed in, where a write to the closed stream
# came back as plain \`echo: I/O error\` and the conductor ran on. On this Mac SIGPIPE is fatal
# and would end the stub whatever orchestrate.sh did, so without this line the cases below
# cannot go red here at all, and the regression they exist for is only visible on CI. This is
# a stub imitating a platform, not a suite repairing its own pipeline (#422).
trap '' PIPE
echo \$\$ >> "\$MARKS.pid"
heartbeats() {
  i=0
  while [ \$i -lt \$1 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
}
await_context() {
  i=0
  while [ \$i -lt 200 ] && ! grep -Fx "\$1" "$work/out" > /dev/null; do i=\$((i + 1)); sleep 0.01; done
}
PRELUDE
    cat
  } > "$1/run-conductor.sh"
  chmod +x "$1"/*.sh
}

await_gone() {
  local i=0 pid alive=1
  [[ -r "$MARKS.pid" ]] || return 0
  while [[ $i -lt 400 && $alive -eq 1 ]]; do
    alive=0
    while read -r pid; do kill -0 "$pid" 2>/dev/null && alive=1; done < "$MARKS.pid"
    [[ $alive -eq 1 ]] || break
    sleep 0.01
    i=$((i + 1))
  done
}

seed() {
  export SOLVABLE="$work/solvable-$1" LAUNCHES="$work/launches-$1" MARKS="$work/marks-$1"
  shift
  printf '%s\n' "$@" > "$SOLVABLE"
  : > "$LAUNCHES"
  : > "$MARKS"
}

expect_exit0_output() {
  if [[ "$rc" -eq 0 && "$actual" == "$expected" ]]; then
    ok
  else
    no "$name"
    echo "    exit: $rc (expected 0)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/    /'
    sed 's/^/    stderr: /' "$work/err"
  fi
}

expect_exit2_no_launch() {
  launched="$(wc -l < "$LAUNCHES" | tr -d ' ')"
  if [[ "$rc" -eq 2 && "$launched" -eq 0 ]] && { [[ $# -eq 0 ]] || grep -F -- "$1" "$work/err" > /dev/null; }; then
    ok
  else
    no "$name"
    echo "    exit: $rc (expected 2)"
    echo "    launches: $launched (expected 0)"
    [[ $# -eq 0 ]] || echo "    stderr naming $1: expected"
    sed 's/^/    stderr: /' "$work/err"
  fi
}

name="launches one conductor per solvable issue through run-conductor.sh and exits 0 on an empty set"
seed basic 101 102
orchestrate "$scripts"
expected="$(printf '%s\n' 101 102)"
actual="$(cat "$LAUNCHES")"
expect_exit0_output

name="exits 2 without launching a conductor when solvable-issues.sh exits other than 0 or 3"
broken="$work/broken"
mkdir -p "$broken"
cp "$scripts/orchestrate.sh" "$scripts/run-conductor.sh" "$broken/"
cp -R "$scripts/lib" "$scripts/veri" "$broken/"
cat > "$broken/solvable-issues.sh" <<'STUB'
#!/bin/sh
calls=$(($(cat "$SOLVABLE.calls" 2>/dev/null || echo 0) + 1))
echo "$calls" > "$SOLVABLE.calls"
[ "$calls" -eq 1 ] && exit 2
exit 3
STUB
chmod +x "$broken"/*.sh
seed broken 201
orchestrate "$broken"
expect_exit2_no_launch

name="reports each assistant event's cache_read + cache_creation tokens as the conductor's context, and none from the result record"
streaming="$work/streaming"
conductor_stub "$streaming" <<STUB
cat <<'JSON'
{"type":"system","subtype":"init","session_id":"s1"}
{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":7,"cache_creation_input_tokens":3438,"cache_read_input_tokens":50000,"output_tokens":120}}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"ok"}]}}
{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":3,"cache_creation_input_tokens":2000,"cache_read_input_tokens":60000,"output_tokens":45}}}
{"type":"result","subtype":"success","is_error":false,"usage":{"input_tokens":10,"cache_creation_input_tokens":5438,"cache_read_input_tokens":110000,"output_tokens":165}}
JSON
STUB
seed streaming 301
orchestrate "$streaming"
expected="$(printf '%s\n' 'context 301 53438' 'context 301 62000')"
actual="$(grep '^context ' "$work/out")"
expect_exit0_output

name="a conductor over VERI_CONDUCTOR_CTX_BUDGET mid-step is not stopped until step-done, and is stopped after it"
budget="$work/budget"
conductor_stub "$budget" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":40}}}'
await_context 'context 401 150000'
echo mid-step >> "\$MARKS"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=401 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
heartbeats 200
echo after-step-done >> "\$MARKS"
STUB
seed budget 401
VERI_CONDUCTOR_CTX_BUDGET=100000 orchestrate "$budget"
await_gone
expected="mid-step"
actual="$(cat "$MARKS")"
expect_exit0_output

name="a step-done under VERI_CONDUCTOR_CTX_BUDGET's default does not stop the conductor, then or at a later non-step-done crossing"
underbudget="$work/underbudget"
conductor_stub "$underbudget" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=501 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":110000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Bash","input":{"command":"true"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":""}]}}'
heartbeats 200
echo after-step-done >> "\$MARKS"
STUB
seed underbudget 501
unset VERI_CONDUCTOR_CTX_BUDGET
orchestrate "$underbudget"
expected="after-step-done"
actual="$(cat "$MARKS")"
expect_exit0_output

name="a conductor over VERI_CONDUCTOR_CTX_BUDGET is stopped after the step-done call's result, not at the call"
atresult="$work/atresult"
conductor_stub "$atresult" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=601 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
await_context 'context 601 150100'
heartbeats 50
echo before-result >> "\$MARKS"
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
heartbeats 200
echo after-step-done >> "\$MARKS"
STUB
seed atresult 601
VERI_CONDUCTOR_CTX_BUDGET=100000 orchestrate "$atresult"
await_gone
expected="before-result"
actual="$(cat "$MARKS")"
expect_exit0_output

name="a conductor that never crosses VERI_CONDUCTOR_CTX_BUDGET is never stopped or restarted"
never="$work/never"
conductor_stub "$never" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=701 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":60000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Bash","input":{"command":"VERI_ISSUE=701 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":99000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":""}]}}'
heartbeats 50
echo after-step-done >> "\$MARKS"
STUB
seed never 701
VERI_CONDUCTOR_CTX_BUDGET=100000 orchestrate "$never"
expected="$(printf '%s\n' after-step-done 701)"
actual="$(cat "$MARKS" "$LAUNCHES")"
expect_exit0_output

name="refuses a VERI_CONDUCTOR_CTX_BUDGET that is not a whole number with exit 2 before any conductor launches"
seed badbudget 801
VERI_CONDUCTOR_CTX_BUDGET=120k orchestrate "$scripts"
expect_exit2_no_launch VERI_CONDUCTOR_CTX_BUDGET

name="refuses VERI_CONDUCTOR_CTX_BUDGET=120k with exit 2, no launch, nothing on stdout and exactly one line naming it on stderr"
seed exactbudget 802
VERI_CONDUCTOR_CTX_BUDGET=120k orchestrate "$scripts"
printf 'orchestrate.sh: VERI_CONDUCTOR_CTX_BUDGET must be a whole number of tokens: 120k\n' > "$work/err.expected"
launched="$(wc -l < "$LAUNCHES" | tr -d ' ')"
if [[ "$rc" -eq 2 && "$launched" -eq 0 && ! -s "$work/out" ]] && cmp -s "$work/err.expected" "$work/err"; then
  ok
else
  no "$name"
  echo "    exit: $rc (expected 2)"
  echo "    launches: $launched (expected 0)"
  sed 's/^/    stdout: /' "$work/out"
  diff "$work/err.expected" "$work/err" | sed 's/^/    /'
fi

name="with VERI_CONDUCTOR_CTX_BUDGET unset, a conductor crossing 120000 is stopped after its next step-done"
defaultbudget="$work/defaultbudget"
conductor_stub "$defaultbudget" <<STUB
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":1,"cache_read_input_tokens":120000,"output_tokens":40}}}'
await_context 'context 901 120001'
echo mid-step >> "\$MARKS"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=901 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":1,"cache_read_input_tokens":120000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
heartbeats 200
echo after-step-done >> "\$MARKS"
STUB
seed defaultbudget 901
unset VERI_CONDUCTOR_CTX_BUDGET
orchestrate "$defaultbudget"
await_gone
expected="mid-step"
actual="$(cat "$MARKS")"
expect_exit0_output

name="a conductor stopped over VERI_CONDUCTOR_CTX_BUDGET is relaunched for the same issue with the same argv"
relaunch="$work/relaunch"
conductor_stub "$relaunch" <<STUB
{ printf 'argv %s:' "\$#"; printf ' [%s]' "\$@"; echo; } >> "\$MARKS"
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo 1001 >> "\$SOLVABLE"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=1001 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
heartbeats 200
echo after-step-done >> "\$MARKS"
STUB
seed relaunch 1001
VERI_CONDUCTOR_CTX_BUDGET=100000 orchestrate "$relaunch"
await_gone
expected="$(printf '%s\n' 'argv 1: [1001]' 'argv 1: [1001]')"
actual="$(cat "$MARKS")"
expect_exit0_output

name="a conductor exiting 0 with its issue still solvable and an unchecked ledger step is relaunched, not treated as done"
exitzero="$work/exitzero"
conductor_stub "$exitzero" <<STUB
[ "\$1" = 1101 ] && [ "\$(grep -cx 1101 "\$LAUNCHES")" -eq 1 ] || exit 0
{ echo 1101; cat "\$SOLVABLE"; } > "\$SOLVABLE.next"
mv "\$SOLVABLE.next" "\$SOLVABLE"
exit 0
STUB
seed exitzero 1101 1102
mkdir -p "$work/.tdd"
printf '%s\n' '# Plan' '- [x] first step' '- [ ] second step' > "$work/.tdd/issue-1101.md"
orchestrate "$exitzero"
expected="$(printf '%s\n' 1101 1101 1102)"
actual="$(cat "$LAUNCHES")"
expect_exit0_output

name="a conductor that wrote .tdd/parked/<n>.md is recorded as parked, its ledger left intact, and skipped for the next solvable issue"
parked="$work/parked"
conductor_stub "$parked" <<STUB
[ "\$1" = 1201 ] || exit 0
mkdir -p .tdd/parked
echo 'Which test command should this run use?' > .tdd/parked/1201.md
{ echo 1201; cat "\$SOLVABLE"; } > "\$SOLVABLE.next"
mv "\$SOLVABLE.next" "\$SOLVABLE"
STUB
seed parked 1201 1202
mkdir -p "$work/.tdd"
printf '%s\n' '# Plan' '- [x] first step' '- [ ] second step' > "$work/.tdd/issue-1201.md"
orchestrate "$parked"
expected="$(printf '%s\n' 'parked 1201' 1201 1202 '# Plan' '- [x] first step' '- [ ] second step')"
actual="$(grep '^parked ' "$work/out"; cat "$LAUNCHES" "$work/.tdd/issue-1201.md")"
expect_exit0_output

name="launches run-conductor.sh <issue> as the leader of its own session, stdin /dev/null, stderr orchestrate's, SIGINT, SIGQUIT, SIGPIPE and SIGXFSZ ignored, and SIGTERMs that pid at the stop"
launchstate="$work/launchstate"
mkdir -p "$launchstate"
cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$launchstate/"
cp -R "$scripts/lib" "$scripts/veri" "$launchstate/"
cat > "$launchstate/run-conductor.sh" <<'STUB'
#!/usr/bin/env bash
echo $$ >> "$MARKS.pid"
{ printf 'argv %s:' "$#"; printf ' [%s]' "$@"; echo; } >> "$MARKS"
trap -p >> "$MARKS"
python3 -c 'import os, sys
print("session leader" if os.getsid(0) == int(sys.argv[1]) else "session %d, not %s" % (os.getsid(0), sys.argv[1]))
print("stdin /dev/null" if os.path.samestat(os.fstat(0), os.stat("/dev/null")) else "stdin not /dev/null")' $$ >> "$MARKS"
echo "conductor $1 on stderr" >&2
echo "$1" >> "$LAUNCHES"
grep -vx -- "$1" "$SOLVABLE" > "$SOLVABLE.next"
mv "$SOLVABLE.next" "$SOLVABLE"
trap 'echo "TERM to $$" >> "$MARKS"; exit 0' TERM
exec > /dev/null
i=0
while [ $i -lt 400 ]; do sleep 0.01; i=$((i + 1)); done
echo "never stopped" >> "$MARKS"
STUB
chmod +x "$launchstate"/*.sh
seed launchstate 1301
orchestrate "$launchstate"
await_gone
pid="$(cat "$MARKS.pid" 2>/dev/null)"
expected="$(printf '%s\n' 'argv 1: [1301]' "trap -- '' SIGINT" "trap -- '' SIGQUIT" "trap -- '' SIGPIPE" "trap -- '' SIGXFSZ" \
  'session leader' 'stdin /dev/null' "TERM to $pid" 'conductor 1301 on stderr')"
actual="$(cat "$MARKS" "$work/err")"
expect_exit0_output

name="run through a symlink to its scripts directory from another working directory, launches that directory's run-conductor.sh, asks its solvable-issues.sh and reads .tdd/parked/ in the working directory"
realskill="$work/realskill"
mkdir -p "$realskill/.tdd/parked" "$work/elsewhere/.tdd/parked"
cp "$scripts/orchestrate.sh" "$realskill/"
cp -R "$scripts/lib" "$scripts/veri" "$realskill/"
{ printf '#!/bin/sh\necho "solvable-issues.sh linked" >> "$MARKS"\n'; tail -n +2 "$scripts/solvable-issues.sh"; } > "$realskill/solvable-issues.sh"
{ printf '#!/bin/sh\necho "run-conductor.sh linked $1" >> "$MARKS"\n'; tail -n +2 "$scripts/run-conductor.sh"; } > "$realskill/run-conductor.sh"
chmod +x "$realskill"/*.sh
ln -s "$realskill" "$work/link"
: > "$work/elsewhere/.tdd/parked/1401.md"
: > "$realskill/.tdd/parked/1402.md"
seed symlinked 1401 1402
(cd "$work/elsewhere" && "$work/link/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
rc=$?
expected="$(printf '%s\n' 'solvable-issues.sh linked' 'run-conductor.sh linked 1402' 'solvable-issues.sh linked' 1402)"
actual="$(cat "$MARKS" "$LAUNCHES" "$work/out")"
expect_exit0_output

echo
finish
