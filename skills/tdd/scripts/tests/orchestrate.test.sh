#!/usr/bin/env bash
# Tests for scripts/orchestrate.sh — the loop above the conductor (issue #217): it asks
# solvable-issues.sh which issues veri may take, launches one conductor per issue through
# run-conductor.sh, and stops once nothing is left to take.
#
# The two scripts it drives are replaced by stubs in a scratch copy of the scripts
# directory, beside the real orchestrate.sh, so no case reaches `gh`, git or a model:
#   - solvable-issues.sh prints the issue numbers left in $SOLVABLE, one per line, and exits
#     3 printing nothing once that file is empty — the real script's "nothing to do".
#   - run-conductor.sh appends the issue it was handed to $LAUNCHES, and takes that issue
#     out of $SOLVABLE, the way a finished run leaves the solvable set.
# A stubbed solvable-issues.sh answers 3 after 20 calls whatever $SOLVABLE holds, so a loop
# that never stops fails its case rather than hanging the suite.
#
# Run: scripts/tests/orchestrate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

scripts="$work/scripts"
mkdir -p "$scripts"
cp "$HERE/../orchestrate.sh" "$scripts/orchestrate.sh" 2>/dev/null

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

# orchestrate <dir>: run the orchestrate.sh copied into <dir> from the scratch root, with no
# stdin, its stdout and stderr in $work/out and $work/err; sets rc to its exit status.
orchestrate() {
  (cd "$work" && "$1/orchestrate.sh") < /dev/null > "$work/out" 2> "$work/err"
  rc=$?
}

# conductor_stub <dir>: make <dir> a scratch scripts directory holding the real
# orchestrate.sh, the suite's solvable-issues.sh stub and a run-conductor.sh that first hands
# its issue to the suite's base stub, for the bookkeeping, then runs the body read on stdin.
# The body may call `heartbeats <n>`, which streams <n> heartbeat lines ~10 ms apart, and
# `await_context <line>`, which waits up to ~2 s for orchestrate.sh to have printed <line>.
conductor_stub() {
  mkdir -p "$1"
  cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$1/"
  {
    printf '#!/bin/sh\n"%s/run-conductor.sh" "$1"\n' "$scripts"
    cat <<PRELUDE
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

# seed <tag> <issue>...: point $SOLVABLE, $LAUNCHES and $MARKS at fresh files for the case
# <tag>, the solvable set holding <issue>... one per line and the other two empty.
seed() {
  export SOLVABLE="$work/solvable-$1" LAUNCHES="$work/launches-$1" MARKS="$work/marks-$1"
  shift
  printf '%s\n' "$@" > "$SOLVABLE"
  : > "$LAUNCHES"
  : > "$MARKS"
}

# expect_exit0_output: pass the case $name when orchestrate.sh exited 0 and $actual equals
# $expected; otherwise fail it, showing the exit, the diff and orchestrate.sh's stderr.
expect_exit0_output() {
  if [[ "$rc" -eq 0 && "$actual" == "$expected" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    echo "    exit: $rc (expected 0)"
    diff <(printf '%s\n' "$expected") <(printf '%s\n' "$actual") | sed 's/^/    /'
    sed 's/^/    stderr: /' "$work/err"
  fi
}

# 1. Every issue the solvable set holds gets one conductor, launched through
#    run-conductor.sh with that issue's number, and the loop exits 0 once the set is empty.
name="launches one conductor per solvable issue through run-conductor.sh and exits 0 on an empty set"
seed basic 101 102
orchestrate "$scripts"
expected="$(printf '%s\n' 101 102)"
actual="$(cat "$LAUNCHES")"
expect_exit0_output

# 2. A solvable-issues.sh that exits with anything but 0 or 3 gave no answer about the
#    solvable set, so orchestrate.sh launches nothing and exits 2. The stub here exits 2 on
#    its first call and 3 on every later one, so a loop that ignores the 2 still ends.
name="exits 2 without launching a conductor when solvable-issues.sh exits other than 0 or 3"
broken="$work/broken"
mkdir -p "$broken"
cp "$scripts/orchestrate.sh" "$scripts/run-conductor.sh" "$broken/"
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
launched="$(wc -l < "$LAUNCHES" | tr -d ' ')"
if [[ "$rc" -eq 2 && "$launched" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  echo "    exit: $rc (expected 2)"
  echo "    launches: $launched (expected 0)"
  sed 's/^/    stderr: /' "$work/err"
fi

# 3. The conductor's context is each assistant event's cache_read_input_tokens +
#    cache_creation_input_tokens, computed per event as the launched stream arrives: every
#    assistant event yields one `context <issue> <tokens>` line on orchestrate.sh's stdout.
#    The stub's stream closes on a {"type":"result"} record whose usage carries its own
#    cache_read + cache_creation total (115438), so a context read from that record would
#    print that number and not the two per-event ones, and a parser that did not filter on
#    the assistant type would print it as a third line; input_tokens and output_tokens are
#    present and must not be counted, and a non-assistant event yields no line.
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

# 4. A conductor whose context crosses VERI_CONDUCTOR_CTX_BUDGET mid-step is left running
#    until the step's step-done mark, and stopped once that mark is seen. With the budget at
#    100000, the stub's first incarnation streams an assistant event at 150000, then waits —
#    up to ~2 s, polling orchestrate.sh's stdout — until orchestrate.sh has printed that
#    event's context line, so the event is known to have been read, and only then writes
#    `mid-step` (a conductor stopped on crossing the budget never gets there). It then streams
#    the step-done mark as a real conductor does — the Bash call to `event.sh step-done` and
#    its result — and keeps streaming heartbeat lines for ~2 s before writing `after-step-done`:
#    a conductor that is stopped, by a signal or by its stream being closed, never writes it.
#    Every later incarnation just leaves the solvable set, so the loop ends.
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
export VERI_CONDUCTOR_CTX_BUDGET=100000
orchestrate "$budget"
unset VERI_CONDUCTOR_CTX_BUDGET
expected="mid-step"
actual="$(cat "$MARKS")"
expect_exit0_output

# 5. A step-done seen while the context is under the budget does not stop the conductor, and
#    does not arm a stop for later: with VERI_CONDUCTOR_CTX_BUDGET unset, so its default
#    applies, the stub's first incarnation streams the step-done mark at 110000 — under the
#    default, over 100000 — then an assistant event at 150000 that is no step-done, then that
#    event's tool result, and keeps streaming heartbeat lines for ~2 s before writing
#    `after-step-done`. A conductor stopped at the under-budget step-done, or at the tool
#    result that follows the later crossing, never writes it.
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

# 6. Over the budget, a conductor is stopped after the step-done call's result, not at the
#    call itself: the call is streamed before its Bash command runs, and a conductor writes
#    more before that result arrives. With the budget at 100000, the stub's first incarnation
#    streams the step-done call at 150100, waits — up to ~2 s, polling orchestrate.sh's
#    stdout — until orchestrate.sh has printed that event's context line, then streams
#    heartbeat lines for ~0.5 s before writing `before-result` and the call's result, then
#    heartbeats for ~2 s more before writing `after-step-done`. A conductor stopped at the
#    call dies in the first heartbeats and never writes `before-result`.
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
export VERI_CONDUCTOR_CTX_BUDGET=100000
orchestrate "$atresult"
unset VERI_CONDUCTOR_CTX_BUDGET
expected="before-result"
actual="$(cat "$MARKS")"
expect_exit0_output

# 7. A conductor whose context never crosses VERI_CONDUCTOR_CTX_BUDGET is never stopped and
#    never restarted, however many steps it finishes. With the budget at 100000, the stub's
#    first incarnation streams two step-done marks — each the Bash call to `event.sh
#    step-done` and its result — at 60000 and at 99100, both under the budget, then heartbeat
#    lines for ~0.5 s before writing `after-step-done`: a conductor stopped at either mark
#    never writes it. Every launch appends its issue to $LAUNCHES, so a restart shows there as
#    a second `701`.
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
export VERI_CONDUCTOR_CTX_BUDGET=100000
orchestrate "$never"
unset VERI_CONDUCTOR_CTX_BUDGET
expected="$(printf '%s\n' after-step-done 701)"
actual="$(cat "$MARKS" "$LAUNCHES")"
expect_exit0_output

echo
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
