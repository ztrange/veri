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

name="a result record whose result is a number exits 2 with one stderr line and no traceback, and an extra argument is ignored, stdin still being extracted with exit 0"
work="$(scratch_dir)"
problems=()
printf '%s' '{"type":"result","result":5}' | "$EXTRACT" > "$work/num.out" 2> "$work/num.err"; num_code=$?
[[ "$num_code" -eq 2 ]] || problems+=("number: exit $num_code, expected 2")
[[ "$(wc -l < "$work/num.err" | tr -d ' ')" == 1 ]] || problems+=("number: want one stderr line, got: $(cat "$work/num.err")")
if grep -F 'Traceback' "$work/num.err" > /dev/null; then problems+=("number: traceback on stderr: $(cat "$work/num.err")"); fi
arg_out="$(printf '%s' '{"type":"result","result":"VERDICT: PASS\nREASON: extra arg."}' | "$EXTRACT" extra-argument)"; arg_code=$?
[[ "$arg_code" -eq 0 ]] || problems+=("extra argument: exit $arg_code, expected 0")
[[ "$arg_out" == $'VERDICT: PASS\nREASON: extra arg.' ]] || problems+=("extra argument: stdout '$arg_out'")
report "$name"

finish
