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
  if [[ "$out" == "$exp" ]]; then pass=$((pass + 1)); else
    fail=$((fail + 1)); echo "FAIL - $name"
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
