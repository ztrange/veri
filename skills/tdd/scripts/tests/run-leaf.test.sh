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

finish
