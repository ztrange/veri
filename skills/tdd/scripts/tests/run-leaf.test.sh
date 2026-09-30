#!/usr/bin/env bash
# Tests for scripts/run-leaf.sh — the leaf invocation, driven against a stub `claude` on
# PATH (no real subprocess, no model call). run-leaf runs claude in --output-format
# stream-json so the leaf streams events (the supervisor's heartbeat), then appends the
# clean final result via extract-result.sh. It does NOT own a progress log — since #4 the
# supervisor (supervise.sh) is the single launch choke point and owns `.tdd/<name>.log`.
#
# The stub `claude` records its argv to $ARGV_OUT, emits a minimal stream-json stream whose
# result event carries $FAKE_RESULT, and exits $FAKE_CODE.
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
[[ "$out" == *'VERDICT: PASS'* ]] && ok || no "returns extracted result text"

[[ "$out" == *'"type":"result"'* ]] && ok || no "streams raw events for heartbeat"

grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && grep -q -- 'stream-json' "$work/argv" && ok || no "passes prompt via -p in stream-json"

run "$work/prompt.txt" 'VERDICT: REJECT' 1 >/dev/null; code=$?
[[ "$code" == 1 ]] && ok || no "propagates leaf exit status (got $code)"

run "$work/prompt.txt" ok 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

run "$work/prompt.txt" ok 0 >/dev/null
[[ ! -e "$work/.tdd" ]] && ok || no "does not own a .tdd log"

finish
