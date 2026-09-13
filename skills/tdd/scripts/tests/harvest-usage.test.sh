#!/usr/bin/env bash
# Unit tests for scripts/harvest-usage.sh — the harvester (issue #107, ADR-0014:
# observability is a per-run event log written by the scripts, not a service).
# Zero-dependency plain-shell asserts, same idiom as event.test.sh.
#
# The other writers mark what they can see as it happens; this one is the reader of what a
# leaf already wrote down. `claude -p --output-format stream-json` closes every run with a
# `{"type":"result", …}` record carrying the leaf's own accounting — how long it took, how
# much of that was the API, how many turns, how many tokens of each of the four kinds, and
# what it cost — and until now nothing in a run picked those numbers up (ADR-0014's context:
# "Time and cost were already on disk in every leaf's closing usage record, but nothing
# harvested them"). The harvester turns one leaf's record into one `usage` line in the run's
# event log, so a reader of that log has the whole run's cost without opening six .log files.
#
# Contract under test (this step only — a finished leaf, with a record to read):
#   harvest-usage.sh <leaf-name>  → reads `.tdd/<leaf-name>.log` relative to the directory
#                                   it is run in (the issue's worktree, the way supervise.sh
#                                   already spells that same path), and exits 0.
#   the event log                 → gains exactly one `usage` line, carrying the eight
#                                   numbers of the closing `result` record.
#
# It takes the NAME, not the log path, for the reason leaf-role.sh's header already gives:
# the writers only ever receive the name, because the name is also what the actor, phase and
# attempt on the line are derived from, and a path would make the script spell the leaf twice.
#
# The payload keys are the record's own — `duration_ms`, `duration_api_ms`, `num_turns`,
# `total_cost_usd` and the four `usage.*` counts, unnested. Renaming them would put a
# translation table between the log and the stream that somebody has to keep true; leaving
# them as they arrived means a reader who has seen one has seen the other.
#
# Run: scripts/tests/harvest-usage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
HARVEST="$HERE/../harvest-usage.sh"
SUP="$HERE/../supervise.sh"
RUN_LEAF="$HERE/../run-leaf.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which of the eight numbers came out wrong rather than just that one did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# event_field <dir> <event> <key> — the value of <key> on the one <event> line of the event
# log a run in <dir> wrote, or a diagnostic in `<<…>>` when there is no such line, more than
# one, or no log at all. The probe supervise.test.sh uses for its `launch`, `retry` and `exit`
# cases, spelled the same way here for `usage`: python3 rather than jq, the dependency
# extract-result.sh already execs in production.
#
# A run directory rather than a file path, so where the log lands under it —
# `.tdd/events.jsonl`, relative to the harvester's cwd — is stated once.
#
# Demanding exactly one match is half of this case's pin and not just a convenience: the
# criterion says ONE usage event per finished leaf, so a harvester that wrote a line per
# `result`-shaped record it passed, or one per token kind, is caught here rather than read
# past. The supervisor's own `launch` and `exit` marks share this file, which is why the probe
# selects by event name instead of asserting on the file's only line.
#
# `print` of the parsed value, not of the raw text, so the assertions below are about the
# NUMBER and not about its spelling: `228265` and `"228265"` both read as 228265, the way
# event.test.sh leaves `ts` comparable whether it is written as a JSON number or as digits in
# a string. What the event log must not lose is the count; whether event.sh's key=value
# payload stringifies it on the way through is that writer's business, not this one's.
event_field() {
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
if len(hits) != 1:
    print("<<%d %s lines>>" % (len(hits), sys.argv[2]))
else:
    print(hits[0].get(sys.argv[3], "<<missing>>"))
' "$1/.tdd/events.jsonl" "$2" "$3" 2>/dev/null || echo '<<no event log>>'
}

stub="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stub" "$work"' EXIT

# 1. The step's whole criterion, as one case: a leaf runs to completion, and the harvester
#    turns the record that leaf closed with into one `usage` line carrying its eight numbers.
#
#    The leaf is a real launch through supervise.sh against a `CLAUDE_BIN` stub, not a log
#    file written by hand, because the thing the harvester reads is not the stub's stdout —
#    it is `.tdd/<name>.log`, which run-leaf.sh builds by streaming the leaf's events and
#    then APPENDING the extracted result text after them (run-leaf.sh:44-49). So the record
#    is never the last line of the file it has to be found in, and a harvester that read the
#    tail would pass against a hand-written fixture and fail against every real leaf. Driving
#    the real launcher is what puts that wrinkle in front of it.
#
#    The name is `verify-refactor` because that is the leaf the issue measured these numbers
#    on (#98's), so the case and the numbers in it have the same provenance.
#
#    Every number is distinct and none is a round figure, so a harvester that crossed two
#    wires — API ms for wall ms, cache reads for cache writes — is caught rather than passed.
#    Four of them come from the nested `usage` object and four from the record's top level,
#    which is the one shape-detail of the record worth a case: read as one flat dictionary,
#    the four token counts come back missing.
#
#    The cost is a float and the rest whole numbers, the way a real record has them, so a
#    harvester that forced the payload through an integer conversion loses 0.74 to 0 here.
name="a finished leaf: the harvester appends one usage event carrying the wall ms, API ms, turns, four token counts and dollars from that leaf's closing stream-json result record"
problems=()

leaf=verify-refactor

# Each number written once, in a variable the stub's record and the assertion below both
# read. Spelled a second time in the expectation instead, the two could drift and the case
# would go green on a number the leaf never reported.
want_duration_ms=228265
want_duration_api_ms=84513
want_num_turns=13
want_total_cost_usd=0.74
want_input_tokens=41
want_output_tokens=8203
want_cache_read_input_tokens=1287431
want_cache_creation_input_tokens=52890

# The leaf's event stream: two ordinary events and then the closing record. The heredoc
# delimiter is unquoted so the `$want_*` above expand into the JSON; `\n` inside the result
# string survives as the two characters it is, since an unquoted heredoc only acts on `\$`,
# `` \` ``, `\\` and a backslash-newline.
cat > "$stub/stream.jsonl" <<STREAM
{"type":"system","subtype":"init","session_id":"9f2c","tools":["Read","Bash"]}
{"type":"assistant","message":{"content":[{"type":"text","text":"I ran the suite."}]}}
{"type":"result","subtype":"success","is_error":false,"duration_ms":$want_duration_ms,"duration_api_ms":$want_duration_api_ms,"num_turns":$want_num_turns,"result":"VERDICT: PASS\nREASON: the refactor kept the suite green.","session_id":"9f2c","total_cost_usd":$want_total_cost_usd,"usage":{"input_tokens":$want_input_tokens,"cache_creation_input_tokens":$want_cache_creation_input_tokens,"cache_read_input_tokens":$want_cache_read_input_tokens,"output_tokens":$want_output_tokens}}
STREAM

# The stub claude: ignores its argv and prints that stream, the way a leaf that finished
# does. Its own heredoc is unquoted too, so `$stub` is baked into the script rather than
# read from whatever environment supervise.sh hands the leaf.
cat > "$stub/claude" <<STUB
#!/usr/bin/env bash
cat "$stub/stream.jsonl"
exit 0
STUB
chmod +x "$stub/claude"

mkdir -p "$work/.tdd"
printf 'verify the refactor.' > "$work/.tdd/$leaf.prompt"

# The launch. Through supervise.sh, never run-leaf.sh directly, because that is how every
# leaf in a real run is launched and therefore how `.tdd/<name>.log` really comes to exist.
# The watchdog knobs are pinned rather than inherited so this suite's wall time is its own
# answer (hermetic-suites.test.sh's concern); the stub returns at once, so they never fire.
( cd "$work" && env CLAUDE_BIN="$stub/claude" VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 \
    VERI_TIMEOUT=10 VERI_POLL=0.2 "$SUP" "$leaf" "$RUN_LEAF" ".tdd/$leaf.prompt" \
  ) >/dev/null 2>&1
launch_code=$?

# Two probes about the fixture rather than about the harvester, so a broken setup says so
# instead of showing eight wrong numbers: the leaf finished, and the log it left really does
# hold the record the harvester is being asked to read.
[[ "$launch_code" == 0 ]] ||
  problems+=("setup: want the stub leaf to exit 0 through supervise.sh, got $launch_code")
grep -q '"type":"result"' "$work/.tdd/$leaf.log" 2>/dev/null ||
  problems+=("setup: want the closing result record in .tdd/$leaf.log, not found")

# The harvest itself, run in the worktree the way every other writer is.
( cd "$work" && "$HARVEST" "$leaf" ) >/dev/null 2>&1
harvest_code=$?
[[ "$harvest_code" == 0 ]] ||
  problems+=("want exit 0 from the harvester, got $harvest_code")

# The eight numbers, each read once into the comparison and the failure message both. The
# loop names each key beside the `want_<key>` variable holding its expectation, so the key
# in the event log and the key in this case cannot drift apart: `${!var}` is an indirect
# expansion — it reads the variable whose NAME is in `$var`, which is how `want_duration_ms`
# is reached from the string `duration_ms`.
for key in duration_ms duration_api_ms num_turns total_cost_usd \
           input_tokens output_tokens cache_read_input_tokens cache_creation_input_tokens; do
  var="want_$key"
  got="$(event_field "$work" usage "$key")"
  [[ "$got" == "${!var}" ]] ||
    problems+=("$key: want $(printf '%q' "${!var}"), got $(printf '%q' "$got")")
done

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
