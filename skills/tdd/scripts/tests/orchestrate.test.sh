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
export SOLVABLE="$work/solvable" LAUNCHES="$work/launches"
printf '%s\n' 101 102 > "$SOLVABLE"
: > "$LAUNCHES"
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
export SOLVABLE="$work/solvable-broken" LAUNCHES="$work/launches-broken"
printf '%s\n' 201 > "$SOLVABLE"
: > "$LAUNCHES"
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
mkdir -p "$streaming"
cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$streaming/"
cat > "$streaming/run-conductor.sh" <<STUB
#!/bin/sh
"$scripts/run-conductor.sh" "\$1"
cat <<'JSON'
{"type":"system","subtype":"init","session_id":"s1"}
{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":7,"cache_creation_input_tokens":3438,"cache_read_input_tokens":50000,"output_tokens":120}}}
{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"ok"}]}}
{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":3,"cache_creation_input_tokens":2000,"cache_read_input_tokens":60000,"output_tokens":45}}}
{"type":"result","subtype":"success","is_error":false,"usage":{"input_tokens":10,"cache_creation_input_tokens":5438,"cache_read_input_tokens":110000,"output_tokens":165}}
JSON
STUB
chmod +x "$streaming"/*.sh
export SOLVABLE="$work/solvable-streaming" LAUNCHES="$work/launches-streaming"
printf '%s\n' 301 > "$SOLVABLE"
: > "$LAUNCHES"
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
mkdir -p "$budget"
cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$budget/"
cat > "$budget/run-conductor.sh" <<STUB
#!/bin/sh
"$scripts/run-conductor.sh" "\$1"
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":40}}}'
i=0
while [ \$i -lt 200 ] && ! grep -Fx 'context 401 150000' "$work/out" > /dev/null; do i=\$((i + 1)); sleep 0.01; done
echo mid-step >> "\$MARKS"
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=401 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
i=0
while [ \$i -lt 200 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
echo after-step-done >> "\$MARKS"
STUB
chmod +x "$budget"/*.sh
export SOLVABLE="$work/solvable-budget" LAUNCHES="$work/launches-budget" MARKS="$work/marks-budget"
export VERI_CONDUCTOR_CTX_BUDGET=100000
printf '%s\n' 401 > "$SOLVABLE"
: > "$LAUNCHES"
: > "$MARKS"
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
mkdir -p "$underbudget"
cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$underbudget/"
cat > "$underbudget/run-conductor.sh" <<STUB
#!/bin/sh
"$scripts/run-conductor.sh" "\$1"
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=501 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":110000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t2","name":"Bash","input":{"command":"true"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":0,"cache_read_input_tokens":150000,"output_tokens":30}}}'
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t2","content":""}]}}'
i=0
while [ \$i -lt 200 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
echo after-step-done >> "\$MARKS"
STUB
chmod +x "$underbudget"/*.sh
export SOLVABLE="$work/solvable-underbudget" LAUNCHES="$work/launches-underbudget" MARKS="$work/marks-underbudget"
unset VERI_CONDUCTOR_CTX_BUDGET
printf '%s\n' 501 > "$SOLVABLE"
: > "$LAUNCHES"
: > "$MARKS"
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
mkdir -p "$atresult"
cp "$scripts/orchestrate.sh" "$scripts/solvable-issues.sh" "$atresult/"
cat > "$atresult/run-conductor.sh" <<STUB
#!/bin/sh
"$scripts/run-conductor.sh" "\$1"
[ "\$(wc -l < "\$LAUNCHES")" -eq 1 ] || exit 0
echo '{"type":"assistant","message":{"role":"assistant","content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"VERI_ISSUE=601 VERI_ACTOR=conductor \$S/event.sh step-done"}}],"usage":{"input_tokens":5,"cache_creation_input_tokens":100,"cache_read_input_tokens":150000,"output_tokens":30}}}'
i=0
while [ \$i -lt 200 ] && ! grep -Fx 'context 601 150100' "$work/out" > /dev/null; do i=\$((i + 1)); sleep 0.01; done
i=0
while [ \$i -lt 50 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
echo before-result >> "\$MARKS"
echo '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t1","content":""}]}}'
i=0
while [ \$i -lt 200 ]; do echo '{"type":"system","subtype":"heartbeat"}'; i=\$((i + 1)); sleep 0.01; done
echo after-step-done >> "\$MARKS"
STUB
chmod +x "$atresult"/*.sh
export SOLVABLE="$work/solvable-atresult" LAUNCHES="$work/launches-atresult" MARKS="$work/marks-atresult"
export VERI_CONDUCTOR_CTX_BUDGET=100000
printf '%s\n' 601 > "$SOLVABLE"
: > "$LAUNCHES"
: > "$MARKS"
orchestrate "$atresult"
unset VERI_CONDUCTOR_CTX_BUDGET
expected="before-result"
actual="$(cat "$MARKS")"
expect_exit0_output

echo
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
