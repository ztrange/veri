#!/usr/bin/env bash
# Unit tests for scripts/extract-result.sh — pull the final assistant text out of a
# `claude -p --output-format stream-json` event stream. The stream is JSONL; the last
# `{"type":"result", ..., "result":"<text>"}` event carries the clean final answer (the
# same text claude prints in plain mode), which is what parse-verdict.sh needs to read.
#
# Run: scripts/tests/extract-result.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXTRACT="$HERE/../extract-result.sh"
source "$HERE/lib/harness.sh"
check() {  # check <name> <input> <expected-stdout>
  local name="$1" input="$2" exp="$3" out
  out="$(printf '%s' "$input" | "$EXTRACT")"
  if [[ "$out" == "$exp" ]]; then ok; else
    no "$name"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

check "extracts result text" \
'{"type":"system","subtype":"init","session_id":"x"}
{"type":"assistant","message":{"content":[{"type":"text","text":"VERDICT: PASS"}]}}
{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}' \
'VERDICT: PASS'

check "multiline result unescaped" \
'{"type":"system","subtype":"init"}
{"type":"result","subtype":"success","result":"VERDICT: REJECT\nREASON: asserts an internal helper, not behavior."}' \
'VERDICT: REJECT
REASON: asserts an internal helper, not behavior.'

check "escaped quotes survive" \
'{"type":"result","result":"VERDICT: REJECT\nREASON: the test calls slugify(\"a\") wrongly."}' \
'VERDICT: REJECT
REASON: the test calls slugify("a") wrongly.'

check "last result wins" \
'{"type":"result","result":"first"}
{"type":"result","result":"second"}' \
'second'

name="#624 a developer report beats a later turn with no report line"
out="$(printf '%s' '{"type":"result","result":"Done.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed"}
{"type":"result","result":"That is the second monitor expiring."}' | "$EXTRACT")"
rc=$?
expect_eq "$name (exit)" 0 "$rc"
expect_eq "$name" 'Done.
IMPL_PATH: a.sh
SUITE: GREEN — 19 passed, 0 failed' "$out"

check "#624 a SPLIT: report beats a later turn with no report line" \
'{"type":"result","result":"Too big.\nSPLIT: the first behaviour\nSPLIT: the second behaviour"}
{"type":"result","result":"That is the second monitor expiring."}' \
'Too big.
SPLIT: the first behaviour
SPLIT: the second behaviour'

check "#624 a TEST_PATH: report beats a later turn with no report line" \
'{"type":"result","result":"Red.\nTEST_PATH: tests/a.test.sh\nAGAINST_UNMODIFIED: FAILS"}
{"type":"result","result":"That is the second monitor expiring."}' \
'Red.
TEST_PATH: tests/a.test.sh
AGAINST_UNMODIFIED: FAILS'

check "passthrough non-stream" \
'VERDICT: PASS
REASON: plain text, no stream-json here.' \
'VERDICT: PASS
REASON: plain text, no stream-json here.'

check "json but no result event" \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[]}}' \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[]}}'

finish
