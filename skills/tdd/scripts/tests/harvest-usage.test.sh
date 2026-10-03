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
unmodeled_record='{"type":"result","duration_ms":1,"duration_api_ms":1,"num_turns":1,"total_cost_usd":0.01,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}'
printf '%s\n' "$unmodeled_record" > "$refused_work/.tdd/$refused.log"

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

name="harvest-usage.sh run through a symlink to the skill directory and from another working directory appends the same usage event and exits as when run in place"
problems=()

usage_event() {
  python3 -c '
import json, sys
for line in open(sys.argv[1]).read().splitlines():
    obj = json.loads(line)
    if obj.get("event") == "usage":
        obj.pop("ts", None)
        obj.pop("awake", None)
        print(json.dumps(obj, sort_keys=True))
' "$1/.tdd/events.jsonl" 2>/dev/null || echo '<<no event log>>'
}

linked_leaf=verify-green
in_place_work="$work/in-place"
linked_work="$work/linked"
modeled=verify-green
modeled_work="$work/modeled"
want_model=claude-opus-5-5
mkdir -p "$modeled_work/.tdd"
cat > "$modeled_work/.tdd/$modeled.log" <<LOG
{"type":"result","duration_ms":1,"duration_api_ms":1,"num_turns":1,"total_cost_usd":0.495,"usage":{"input_tokens":14,"output_tokens":3903,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},"modelUsage":{"$want_model":{"inputTokens":14,"outputTokens":3903,"cacheReadInputTokens":0,"cacheCreationInputTokens":0,"costUSD":0.495,"canonicalModel":"$want_model"}}}
LOG
mkdir -p "$in_place_work/.tdd" "$linked_work/.tdd"
cp "$modeled_work/.tdd/$modeled.log" "$in_place_work/.tdd/$linked_leaf.log"
cp "$modeled_work/.tdd/$modeled.log" "$linked_work/.tdd/$linked_leaf.log"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"

in_place_out="$( cd "$in_place_work" && "$HARVEST" "$linked_leaf" 2>&1 )" && in_place_code=0 || in_place_code=$?
linked_out="$( cd "$linked_work" && "$work/linked-skill/scripts/harvest-usage.sh" "$linked_leaf" 2>&1 )" && linked_code=0 || linked_code=$?
in_place_event="$(usage_event "$in_place_work")"
linked_event="$(usage_event "$linked_work")"

[[ "$in_place_code" == 0 && "$in_place_event" == *'"model": "claude-opus-5-5"'* ]] ||
  problems+=("setup: want the in-place run to exit 0 and append a usage event, got exit $in_place_code and $(printf '%q' "$in_place_event")")
[[ "$linked_code" == "$in_place_code" ]] ||
  problems+=("exit: want $in_place_code as in place, got $linked_code")
[[ "$linked_out" == "$in_place_out" ]] ||
  problems+=("output: want $(printf '%q' "$in_place_out") as in place, got $(printf '%q' "$linked_out")")
[[ "$linked_event" == "$in_place_event" ]] ||
  problems+=("usage event: want $(printf '%q' "$in_place_event") as in place, got $(printf '%q' "$linked_event")")

report "$name"

name="harvest-usage.sh exits 1 with no usage event appended when .tdd/<name>.log is missing, 3 when the log has no closing result record, and 2 with exactly its usage line when given no argument"
problems=()

absent=develop-green
absent_work="$work/absent"
mkdir -p "$absent_work/.tdd"
( cd "$absent_work" && "$HARVEST" "$absent" ) >/dev/null 2>&1 && absent_code=0 || absent_code=$?
[[ "$absent_code" == 1 ]] ||
  problems+=("no log file: want exit 1, got $absent_code")
absent_usage_lines="$(event_count "$absent_work" usage)"
[[ "$absent_usage_lines" == 0 ]] ||
  problems+=("no log file: want 0 usage lines in the event log, got $absent_usage_lines")

( cd "$killed_work" && "$HARVEST" "$killed" ) >/dev/null 2>&1 && unrecorded_code=0 || unrecorded_code=$?
[[ "$unrecorded_code" == 3 ]] ||
  problems+=("no closing result record: want exit 3, got $unrecorded_code")

bare_err_text="$( ( cd "$absent_work" && "$HARVEST" ) 2>&1 >/dev/null )" && bare_code=0 || bare_code=$?
[[ "$bare_code" == 2 ]] ||
  problems+=("no argument: want exit 2, got $bare_code")
[[ "$bare_err_text" == "usage: harvest-usage.sh <leaf-name>" ]] ||
  problems+=("no argument: want exactly $(printf '%q' 'usage: harvest-usage.sh <leaf-name>') on stderr, got $(printf '%q' "$bare_err_text")")

report "$name"

finish
