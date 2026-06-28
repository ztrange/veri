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
pass=0 fail=0
check() {  # check <name> <input> <expected-stdout>
  local name="$1" input="$2" exp="$3" out
  out="$(printf '%s' "$input" | "$EXTRACT")"
  if [[ "$out" == "$exp" ]]; then pass=$((pass + 1)); else
    fail=$((fail + 1)); echo "FAIL - $name"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

# 1. extracts the result event's text, ignoring system/assistant/other events
check "extracts result text" \
'{"type":"system","subtype":"init","session_id":"x"}
{"type":"assistant","message":{"content":[{"type":"text","text":"VERDICT: PASS"}]}}
{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS"}' \
'VERDICT: PASS'

# 2. a multi-line result (JSON-escaped \n) is unescaped to real newlines
check "multiline result unescaped" \
'{"type":"system","subtype":"init"}
{"type":"result","subtype":"success","result":"VERDICT: REJECT\nREASON: asserts an internal helper, not behavior."}' \
'VERDICT: REJECT
REASON: asserts an internal helper, not behavior.'

# 3. embedded quotes/braces in the result survive (real JSON unescaping, not a regex)
check "escaped quotes survive" \
'{"type":"result","result":"VERDICT: REJECT\nREASON: the test calls slugify(\"a\") wrongly."}' \
'VERDICT: REJECT
REASON: the test calls slugify("a") wrongly.'

# 4. the LAST result event wins if more than one appears
check "last result wins" \
'{"type":"result","result":"first"}
{"type":"result","result":"second"}' \
'second'

# 5. passthrough fallback: input that is not a stream-json result is returned unchanged,
#    so a plain-text leaf (or a stub) still works end to end
check "passthrough non-stream" \
'VERDICT: PASS
REASON: plain text, no stream-json here.' \
'VERDICT: PASS
REASON: plain text, no stream-json here.'

# 6. JSONL with no result event at all → passthrough unchanged
check "json but no result event" \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[]}}' \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[]}}'

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
