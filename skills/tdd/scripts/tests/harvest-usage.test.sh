#!/usr/bin/env bash
# Unit tests for scripts/harvest-usage.sh — the harvester that turns a leaf's closing usage
# record into one event-log line.
#
# Contract under test:
#   harvest-usage.sh <leaf-name>  → reads `.tdd/<leaf-name>.log` relative to the directory
#                                   it is run in, and exits 0.
#   the event log                 → gains exactly one `usage` line, carrying the eight
#                                   numbers of the closing `result` record.
#   a log with no such record     → nothing is appended and the harvester says so on stderr,
#                                   naming itself and the leaf.
#
# Run: scripts/tests/harvest-usage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HARVEST="$HERE/../harvest-usage.sh"
RUN_LEAF="$HERE/../run-leaf.sh"

source "$HERE/lib/harness.sh"

event_fields() {
  local dir="$1" event="$2"
  shift 2
  python3 -c '
import sys, json
hits = []
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == sys.argv[2]:
        hits.append(obj)
for key in sys.argv[3:]:
    if len(hits) != 1:
        print("<<%d %s lines>>" % (len(hits), sys.argv[2]))
    else:
        print(hits[0].get(key, "<<missing>>"))
' "$dir/.tdd/events.jsonl" "$event" "$@" 2>/dev/null || printf '<<no event log>>\n%.0s' "$@"
}

event_count() {
  python3 -c '
import sys, json
n = 0
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == sys.argv[2]:
        n += 1
print(n)
' "$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo 0
}

launch_leaf() {
  local stub_dir="$1" work_dir="$2" leaf="$3"
  claude_stub "$stub_dir" "$(cat <<STUB
printf '%s\n' '{"event":"fixture-leaf"}' >> .tdd/events.jsonl
cat "$stub_dir/stream.jsonl"
exit 0
STUB
)"
  mkdir -p "$work_dir/.tdd"
  printf 'do the step.' > "$work_dir/.tdd/$leaf.prompt"
  local code=0
  ( cd "$work_dir" && CLAUDE_BIN="$stub_dir/claude" "$RUN_LEAF" ".tdd/$leaf.prompt" \
      > ".tdd/$leaf.log" 2>&1 ) || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("setup: want the stub leaf $leaf to exit 0 through run-leaf.sh, got $code")
}

has_result_record() {
  grep -q '"type":"result"' "$1/.tdd/$2.log" 2>/dev/null
}

stub="$(scratch_dir)"
work="$(scratch_dir)"

name="a finished leaf: the harvester appends one usage event carrying the wall ms, API ms, turns, four token counts and dollars from that leaf's closing stream-json result record"
problems=()

leaf=verify-refactor

finished_work="$work/finished"

want_duration_ms=228265
want_duration_api_ms=84513
want_num_turns=13
want_total_cost_usd=0.74
want_input_tokens=41
want_output_tokens=8203
want_cache_read_input_tokens=1287431
want_cache_creation_input_tokens=52890

cat > "$stub/stream.jsonl" <<STREAM
{"type":"system","subtype":"init","session_id":"9f2c","tools":["Read","Bash"]}
{"type":"assistant","message":{"content":[{"type":"text","text":"I ran the suite."}]}}
{"type":"result","subtype":"success","is_error":false,"duration_ms":$want_duration_ms,"duration_api_ms":$want_duration_api_ms,"num_turns":$want_num_turns,"result":"VERDICT: PASS\nREASON: the refactor kept the suite green.","session_id":"9f2c","total_cost_usd":$want_total_cost_usd,"usage":{"input_tokens":$want_input_tokens,"cache_creation_input_tokens":$want_cache_creation_input_tokens,"cache_read_input_tokens":$want_cache_read_input_tokens,"output_tokens":$want_output_tokens}}
STREAM

launch_leaf "$stub" "$finished_work" "$leaf"

has_result_record "$finished_work" "$leaf" ||
  problems+=("setup: want the closing result record in .tdd/$leaf.log, not found")

last_line="$(grep -v '^[[:space:]]*$' "$finished_work/.tdd/$leaf.log" | tail -n 1)"
[[ "$last_line" != *'"type":"result"'* ]] ||
  problems+=("want the closing result record not to be .tdd/$leaf.log's last line (run-leaf.sh appends the extracted text after it), it is")

direct_work="$work/direct"
mkdir -p "$direct_work/.tdd"
cp "$finished_work/.tdd/$leaf.log" "$direct_work/.tdd/$leaf.log"
( cd "$direct_work" && "$HARVEST" "$leaf" ) >/dev/null 2>&1
harvest_code=$?
[[ "$harvest_code" == 0 ]] ||
  problems+=("want exit 0 from the harvester, got $harvest_code")

keys=(duration_ms duration_api_ms num_turns total_cost_usd
      input_tokens output_tokens cache_read_input_tokens cache_creation_input_tokens)
mapfile -t got < <(event_fields "$direct_work" usage "${keys[@]}")
for i in "${!keys[@]}"; do
  key="${keys[$i]}" value="${got[$i]-}"
  var="want_$key"
  [[ "$value" == "${!var}" ]] ||
    problems+=("$key: want $(printf '%q' "${!var}"), got $(printf '%q' "$value")")
done

report "$name"

name="a leaf whose log carries no closing result record: the harvester appends no usage event and says so on stderr, naming itself and the leaf"
problems=()

killed=develop-green
killed_stub="$stub/killed"
killed_work="$work/killed"
mkdir -p "$killed_stub"

{
  printf '%s\n' '{"type":"system","subtype":"init","session_id":"3b71","tools":["Read","Bash"]}'
  printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"Writing the test."}]}}'
  printf '%s'   '{"type":"assistant","message":{"content":[{"type":"te'
} > "$killed_stub/stream.jsonl"

launch_leaf "$killed_stub" "$killed_work" "$killed"

! has_result_record "$killed_work" "$killed" ||
  problems+=("setup: want no closing result record in .tdd/$killed.log, found one")
[[ -s "$killed_work/.tdd/events.jsonl" ]] ||
  problems+=("setup: want the stub leaf's marker line in the event log, found none")

killed_err_text="$( ( cd "$killed_work" && "$HARVEST" "$killed" ) 2>&1 >/dev/null )"

killed_usage_lines="$(event_count "$killed_work" usage)"
[[ "$killed_usage_lines" == 0 ]] ||
  problems+=("want 0 usage lines in the event log, got $killed_usage_lines")

[[ -n "$killed_err_text" ]] ||
  problems+=("want a diagnostic on stderr, got nothing")
[[ "$killed_err_text" == *harvest-usage* ]] ||
  problems+=("want the harvester named on stderr, got: $(printf '%q' "$killed_err_text")")
[[ "$killed_err_text" == *"$killed"* ]] ||
  problems+=("want the leaf named on stderr, got: $(printf '%q' "$killed_err_text")")

report "$name"

name="a leaf name leaf-role.sh refuses: the harvester appends no usage event and exits 2, naming itself and the leaf on stderr"
problems=()

refused=frobnicate-red
refused_work="$work/refused"
mkdir -p "$refused_work/.tdd"
cat > "$refused_work/.tdd/$refused.log" <<'LOG'
{"type":"result","duration_ms":1,"duration_api_ms":1,"num_turns":1,"total_cost_usd":0.01,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}
LOG

refused_err_text="$( ( cd "$refused_work" && "$HARVEST" "$refused" ) 2>&1 >/dev/null )" && refused_code=0 || refused_code=$?

[[ "$refused_code" == 2 ]] ||
  problems+=("want exit 2, got $refused_code")

refused_usage_lines="$(event_count "$refused_work" usage)"
[[ "$refused_usage_lines" == 0 ]] ||
  problems+=("want 0 usage lines in the event log, got $refused_usage_lines")

[[ "$refused_err_text" == *harvest-usage* || "$refused_err_text" == *leaf-role* ]] ||
  problems+=("want harvest-usage or leaf-role named on stderr, got: $(printf '%q' "$refused_err_text")")
[[ "$refused_err_text" == *"$refused"* ]] ||
  problems+=("want the leaf named on stderr, got: $(printf '%q' "$refused_err_text")")

report "$name"

finish
