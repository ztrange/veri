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

check "#624 a SUITE:-only report beats a later turn with no report line" \
'{"type":"result","result":"Tidied.\nSUITE: GREEN — 19 passed, 0 failed"}
{"type":"result","result":"That is the second monitor expiring."}' \
'Tidied.
SUITE: GREEN — 19 passed, 0 failed'

check "#624 of two records that both carry a report line, the later one wins" \
'{"type":"result","result":"First.\nIMPL_PATH: a.sh\nSUITE: GREEN — 19 passed, 0 failed"}
{"type":"result","result":"Second.\nIMPL_PATH: b.sh\nSUITE: GREEN — 20 passed, 0 failed"}' \
'Second.
IMPL_PATH: b.sh
SUITE: GREEN — 20 passed, 0 failed'

check "#624 with no report or VERDICT: line in any record, the last record wins" \
'{"type":"result","result":"First turn."}
{"type":"result","result":"Second turn.\nNothing to report."}
{"type":"result","result":"Third turn.\nStill no report."}' \
'Third turn.
Still no report.'

check "#624 a VERDICT: record still beats a later record without one" \
'{"type":"result","result":"VERDICT: PASS\nREASON: the case pins the behaviour."}
{"type":"result","result":"That is the second monitor expiring."}' \
'VERDICT: PASS
REASON: the case pins the behaviour.'

check "#624 a developer report with no result record passes through unchanged" \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[{"type":"text","text":"IMPL_PATH: a.sh"}]}}
Done.
IMPL_PATH: a.sh
SUITE: GREEN — 19 passed, 0 failed' \
'{"type":"system","subtype":"init"}
{"type":"assistant","message":{"content":[{"type":"text","text":"IMPL_PATH: a.sh"}]}}
Done.
IMPL_PATH: a.sh
SUITE: GREEN — 19 passed, 0 failed'

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

name="extract-result.sh run through a symlink to the skill directory and from another working directory writes the same stdout and exit code as when run in place"
work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
stream='{"type":"system","subtype":"init"}
{"type":"result","result":"VERDICT: PASS\nREASON: linked."}'
in_place="$(printf '%s' "$stream" | "$EXTRACT")"; in_place_code=$?
linked="$(cd "$work/elsewhere" && printf '%s' "$stream" | "$work/linked-skill/scripts/extract-result.sh")"; linked_code=$?
if [[ "$linked" == "$in_place" && "$linked_code" -eq "$in_place_code" && "$in_place" == *"REASON: linked."* ]]; then ok; else
  no "$name"
  diff <(printf '%s\nexit %s\n' "$in_place" "$in_place_code") <(printf '%s\nexit %s\n' "$linked" "$linked_code") | sed 's/^/    /'
fi

name="a result record whose result is a number exits 1 with a traceback on stderr, and an extra argument is ignored, stdin still being extracted with exit 0"
work="$(scratch_dir)"
problems=()
printf '%s' '{"type":"result","result":5}' | "$EXTRACT" > "$work/num.out" 2> "$work/num.err"; num_code=$?
[[ "$num_code" -eq 1 ]] || problems+=("number: exit $num_code, expected 1")
grep -F 'Traceback' "$work/num.err" > /dev/null || problems+=("number: no traceback on stderr: $(cat "$work/num.err")")
arg_out="$(printf '%s' '{"type":"result","result":"VERDICT: PASS\nREASON: extra arg."}' | "$EXTRACT" extra-argument)"; arg_code=$?
[[ "$arg_code" -eq 0 ]] || problems+=("extra argument: exit $arg_code, expected 0")
[[ "$arg_out" == $'VERDICT: PASS\nREASON: extra arg.' ]] || problems+=("extra argument: stdout '$arg_out'")
report "$name"

finish
