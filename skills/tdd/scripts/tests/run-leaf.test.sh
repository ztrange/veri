#!/usr/bin/env bash
# Tests for scripts/run-leaf.sh — the leaf invocation, driven against a stub `claude` on
# PATH that records its argv to $ARGV_OUT, emits a minimal stream-json stream whose result
# event carries $FAKE_RESULT, and exits $FAKE_CODE.
#
# Contract under test:
#   run-leaf.sh runs claude with `--output-format stream-json`, then appends the clean
#   final result via extract-result.sh; it owns no progress log.
#
# Run: scripts/tests/run-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF="$HERE/../run-leaf.sh"
source "$HERE/lib/harness.sh"

stubdir="$(scratch_dir)"
work="$(scratch_dir)"
claude_stub "$stubdir" "$(cat <<'STUB'
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"assistant","message":{"content":[{"type":"text","text":"%s"}]}}\n' "${FAKE_RESULT:-ok}"
printf '{"type":"result","subtype":"success","is_error":false,"result":"%s"}\n' "${FAKE_RESULT:-ok}"
exit "${FAKE_CODE:-0}"
STUB
)"

run() {  # run <prompt-file> <fake-result> <fake-code> [extra args...]
  local pf="$1" res="$2" fcode="$3"; shift 3
  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$work/argv" \
      FAKE_RESULT="$res" FAKE_CODE="$fcode" \
      "$LEAF" "$pf" "$@" )
}

printf 'Verify the test for issue 3.' > "$work/prompt.txt"

out="$(run "$work/prompt.txt" 'VERDICT: PASS' 0)"
grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && grep -q -- 'stream-json' "$work/argv" && ok || no "passes prompt via -p in stream-json"

run "$work/prompt.txt" ok 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

problems=()
sig="$(scratch_dir)"
mkdir -p "$sig/tools"
for tool in pkill killall; do
  printf '#!/bin/sh\nprintf "%%s\\n" "$*" > "%s/%s-ran"\n' "$sig" "$tool" > "$sig/tools/$tool"
  chmod +x "$sig/tools/$tool"
done
claude_stub "$sig" "$(cat <<'STUB'
pkill -n -f 'exp-sleep 60' > "$SIG_DIR/pkill-out" 2>&1
killall exp-sleep > "$SIG_DIR/killall-out" 2>&1
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env PATH="$sig/tools:$PATH" CLAUDE_BIN="$sig/claude" SIG_DIR="$sig" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
for tool in pkill killall; do
  [[ ! -e "$sig/$tool-ran" ]] \
    || problems+=("the leaf's $tool reached the signalling tool, with arguments '$(cat "$sig/$tool-ran")'")
  for phrase in 'signal only processes you started' 'by the pid you recorded'; do
    grep -iF "$phrase" "$sig/$tool-out" > /dev/null 2>&1 \
      || problems+=("the leaf's $tool printed no '$phrase': '$(cat "$sig/$tool-out" 2>&1)'")
  done
done
report "refuses a leaf's pkill and killall before they signal anything, naming the rule: signal only processes you started, by the pid you recorded (#1427)"

problems=()
pg="$(scratch_dir)"
mkdir -p "$pg/tools"
printf '#!/bin/sh\nprintf "%%s\\n" "$*" >> "%s/pgrep-ran"\n' "$pg" > "$pg/tools/pgrep"
printf '#!/bin/sh\npgrep -g 0\nprintf "%%s\\n" "$?" > "%s/suite-exit"\n' "$pg" > "$pg/suite.sh"
chmod +x "$pg/tools/pgrep" "$pg/suite.sh"
claude_stub "$pg" "$(cat <<'STUB'
{ kill $(pgrep -f 'exp-sleep 60'); } > "$PG_DIR/kill-out" 2>&1
"$PG_DIR/suite.sh"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env PATH="$pg/tools:$PATH" CLAUDE_BIN="$pg/claude" PG_DIR="$pg" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
leaf_lookup="$(grep -F -- '-f exp-sleep 60' "$pg/pgrep-ran" 2>/dev/null)"
[[ -z "$leaf_lookup" ]] \
  || problems+=("the leaf's kill \$(pgrep …) reached the process lookup, with arguments '$leaf_lookup'")
for phrase in 'signal only processes you started' 'by the pid you recorded'; do
  grep -iF "$phrase" "$pg/kill-out" > /dev/null 2>&1 \
    || problems+=("the leaf's kill \$(pgrep …) printed no '$phrase': '$(cat "$pg/kill-out" 2>&1)'")
done
grep -Fx -- '-g 0' "$pg/pgrep-ran" > /dev/null 2>&1 \
  || problems+=("a script the leaf ran had its pgrep -g refused: calls seen '$(cat "$pg/pgrep-ran" 2>&1)'")
[[ "$(cat "$pg/suite-exit" 2>&1)" == 0 ]] \
  || problems+=("a script the leaf ran saw its pgrep -g exit '$(cat "$pg/suite-exit" 2>&1)', not 0")
report "refuses a leaf's kill \$(pgrep …) naming the rule, while a script the leaf runs still reaches pgrep -g (#1427)"

problems=()
own="$(scratch_dir)"
claude_stub "$own" "$(cat <<'STUB'
bash -c 'sleep 30 & pid=$!
env kill "$pid" 2> "$OWN_DIR/kill-err"; status=$?
printf "%s\n" "$status" > "$OWN_DIR/kill-exit"
[ "$status" = 0 ] || /bin/kill "$pid"
wait "$pid"; printf "%s\n" "$?" > "$OWN_DIR/wait-exit"'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
)"
( cd "$work" && env CLAUDE_BIN="$own/claude" OWN_DIR="$own" \
    "$LEAF" "$work/prompt.txt" > /dev/null 2>&1 )
[[ "$(cat "$own/kill-exit" 2>&1)" == 0 ]] \
  || problems+=("the leaf's kill of a pid it recorded exited '$(cat "$own/kill-exit" 2>&1)', not 0: '$(cat "$own/kill-err" 2>&1)'")
[[ "$(cat "$own/wait-exit" 2>&1)" == 143 ]] \
  || problems+=("the process the leaf started ended with '$(cat "$own/wait-exit" 2>&1)', not 143 (SIGTERM)")
report "a leaf can still kill <pid> a process it started and recorded the pid of (#1427)"

finish
