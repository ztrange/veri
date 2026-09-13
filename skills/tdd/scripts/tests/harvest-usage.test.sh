#!/usr/bin/env bash
# Unit tests for scripts/harvest-usage.sh — the harvester (issue #107, ADR-0014:
# observability is a per-run event log written by the scripts, not a service).
# Zero-dependency plain-shell asserts, same idiom as event.test.sh.
#
# The other writers mark what they can see as it happens; this one is the reader of what a
# leaf already wrote down — ADR-0014's context: "Time and cost were already on disk in every
# leaf's closing usage record, but nothing harvested them".
#
# What that closing record holds, why the harvester takes the leaf's NAME rather than its log
# path, and why the payload keys are the record's own and unrenamed are stated in the script's
# own header (harvest-usage.sh:8-23), and deliberately not restated here. They were, until this
# refactor, in both files word for word: one rationale in two copies is two things to keep
# true, and the copy that goes stale is always the one in the file nobody opens when the design
# changes.
#
# Contract under test:
#   harvest-usage.sh <leaf-name>  → reads `.tdd/<leaf-name>.log` relative to the directory
#                                   it is run in (the issue's worktree, the way supervise.sh
#                                   already spells that same path), and exits 0.
#   the event log                 → gains exactly one `usage` line, carrying the eight
#                                   numbers of the closing `result` record.
#   a log with no such record     → nothing is appended and the harvester says so on stderr,
#                                   naming itself and the leaf.
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

# event_count <dir> <event> — how many <event> lines a run in <dir> wrote to its event log,
# and 0 when it wrote no log at all. `event_field` above is the probe for reading a value off
# the one line that must exist; case 2's assertion is that NO such line exists, which that
# probe can only report as the text of a diagnostic — comparing against `<<0 usage lines>>`
# would make this suite's own error spelling load-bearing.
#
# A missing log counting as 0 is why case 2 also probes that the log is there at all: without
# that, a harvester that deleted the whole file, or a supervise.sh that never wrote one, would
# read here as "appended nothing" and pass.
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

# launch_leaf <stub-dir> <work-dir> <leaf> — run <leaf> to completion in <work-dir> against a
# stub `claude` that prints <stub-dir>/stream.jsonl, and complain into `problems` unless the
# supervisor exited 0. Both cases need the same two files out of it —
# `<work-dir>/.tdd/<leaf>.log` for the harvester to read, and `<work-dir>/.tdd/events.jsonl`
# for it to append to (or not) — and differ only in the stream the stub prints, which each
# writes itself beforehand.
#
# The launch probe lives here rather than in each case because a failed launch means the same
# thing to both — no log, so nothing the harvester is asked about is being measured — and both
# reported it in the same words. It appends to the caller's `problems` the way
# docs-gap-adr.test.sh's must_say does, so report() below closes over it unchanged; the leaf's
# name goes in the message because the helper no longer knows which case it is serving.
#
# Through supervise.sh, never run-leaf.sh directly, because that is how every leaf in a real
# run is launched and therefore how `.tdd/<name>.log` really comes to exist: run-leaf.sh
# builds it by streaming the leaf's events and then APPENDING the extracted result text after
# them (run-leaf.sh:44-49). So the record is never the last line of the file it has to be
# found in, and a harvester that read the tail would pass against a hand-written fixture and
# fail against every real leaf. Driving the real launcher is what puts that wrinkle in front
# of it.
#
# The stub ignores its argv and prints that stream, the way a leaf that finished does; its
# heredoc is unquoted, so <stub-dir> is baked into the script rather than read from whatever
# environment supervise.sh hands the leaf. For the same reason the prompt's text is written
# here and is arbitrary: nothing downstream of the stub ever reads it.
#
# The watchdog knobs are pinned rather than inherited so this suite's wall time is its own
# answer (hermetic-suites.test.sh's concern); the stub returns at once, so they never fire.
launch_leaf() {
  local stub_dir="$1" work_dir="$2" leaf="$3"
  cat > "$stub_dir/claude" <<STUB
#!/usr/bin/env bash
cat "$stub_dir/stream.jsonl"
exit 0
STUB
  chmod +x "$stub_dir/claude"
  mkdir -p "$work_dir/.tdd"
  printf 'do the step.' > "$work_dir/.tdd/$leaf.prompt"
  local code=0
  ( cd "$work_dir" && env CLAUDE_BIN="$stub_dir/claude" VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=5 \
      VERI_TIMEOUT=10 VERI_POLL=0.2 "$SUP" "$leaf" "$RUN_LEAF" ".tdd/$leaf.prompt" \
    ) >/dev/null 2>&1 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("setup: want the stub leaf $leaf to exit 0 through supervise.sh, got $code")
}

stub="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stub" "$work"' EXIT

# 1. The step's whole criterion, as one case: a leaf runs to completion, and the harvester
#    turns the record that leaf closed with into one `usage` line carrying its eight numbers.
#
#    The leaf is a real launch through supervise.sh against a `CLAUDE_BIN` stub, not a log
#    file written by hand: launch_leaf's header above gives the reason, which is that the file
#    the harvester reads is not the stub's stdout but the log run-leaf.sh assembles from it.
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

launch_leaf "$stub" "$work" "$leaf"

# A probe about the fixture rather than about the harvester, so a broken setup says so instead
# of showing eight wrong numbers: the log the leaf left really does hold the record the
# harvester is being asked to read. That the leaf finished at all is launch_leaf's own probe.
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

# 2. The step's criterion: a leaf whose log holds no closing `result` record. The harvester
#    appends nothing, and says so on stderr — so the numbers that leaf never reported are
#    absent from the log rather than present as zeros.
#
#    A killed leaf is where this really happens: the watchdog SIGKILLs it mid-stream, so its
#    log stops wherever the last write landed and no accounting was ever emitted. That shape
#    is what the fixture below reproduces — two whole events and then a line cut off in the
#    middle — rather than the kill itself, because what the harvester can see is the log, and
#    a truncated log is the same log however it came to be truncated. Driving a real kill here
#    would buy no assertion and spend the watchdog's wall time to do it.
#
#    Run through supervise.sh and inside a run that already has an event log, for the reason
#    the probe's header gives: `.tdd/events.jsonl` at this point holds the supervisor's own
#    `launch` and `exit` lines, so "appended nothing" is being asserted against a file that
#    exists and has lines in it. A case whose log was empty for want of any writer at all
#    would pass on a harvester that appended eight zeros.
#
#    Its own directories under the two the first case used, so the leaf, the log and the event
#    log are this case's alone — a count of `usage` lines is meaningless in a directory where
#    another case already harvested one — and so the existing trap still cleans both up.
#
#    The exit status is deliberately not pinned. The criterion names two observable things,
#    the empty log and the diagnostic, and says nothing about the code; the ledger's steps
#    that wanted one said so (`leaf-role.sh` … "exit 2"). Choosing a code here would pin an
#    answer this step never asked for.
name="a leaf whose log carries no closing result record: the harvester appends no usage event and says so on stderr, naming itself and the leaf"
problems=()

killed=develop-green
killed_stub="$stub/killed"
killed_work="$work/killed"
mkdir -p "$killed_stub"

# The killed leaf's log: two events it managed to emit, then a line that stops mid-key. No
# `result` record, because the kill came before the leaf could close one. Single-quoted, so
# nothing in the JSON is read by the shell, and `printf '%s'` for the last one — no trailing
# newline, which is what a stream cut off mid-write leaves behind.
{
  printf '%s\n' '{"type":"system","subtype":"init","session_id":"3b71","tools":["Read","Bash"]}'
  printf '%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"Writing the test."}]}}'
  printf '%s'   '{"type":"assistant","message":{"content":[{"type":"te'
} > "$killed_stub/stream.jsonl"

launch_leaf "$killed_stub" "$killed_work" "$killed"

# Two probes about the fixture, so a setup that drifted says so rather than being read as the
# harvester behaving: the log the leaf left really does hold no `result` record, and the event
# log exists with the supervisor's own lines in it. That the leaf ran at all is launch_leaf's
# own probe.
grep -q '"type":"result"' "$killed_work/.tdd/$killed.log" 2>/dev/null &&
  problems+=("setup: want no closing result record in .tdd/$killed.log, found one")
[[ -s "$killed_work/.tdd/events.jsonl" ]] ||
  problems+=("setup: want supervise.sh's own lines in the event log, found none")

# The harvest, with stderr kept rather than discarded — it is half of what this case pins.
#
# `2>&1 >/dev/null`, in that order, the way issue-worktree.test.sh:119-121 captures a refusal:
# stderr is pointed at where stdout currently goes (the command substitution's capture), then
# stdout is sent to /dev/null. So the variable holds the diagnostic alone. The temp file this
# replaces existed only to carry stderr the three lines from the run to the `cat` that read it
# back, and needed a `rm` of its own because it was the one file in this suite the trap on
# `$stub` and `$work` did not cover.
killed_err_text="$( ( cd "$killed_work" && "$HARVEST" "$killed" ) 2>&1 >/dev/null )"

# Nothing appended. Zero `usage` lines, not "no numbers in the one it wrote": a line of eight
# zeros, or of eight empty strings, is exactly the reading of a killed leaf the criterion
# forbids, and both would satisfy a probe that only asked about the values.
killed_usage_lines="$(event_count "$killed_work" usage)"
[[ "$killed_usage_lines" == 0 ]] ||
  problems+=("want 0 usage lines in the event log, got $killed_usage_lines")

# And said so. The diagnostic must carry both the harvester and the leaf, for the reason
# leaf-role.test.sh's refusal_probe gives: one run harvests six leaves, so a message that
# names neither leaves a reader unable to tell which leaf went unaccounted for, or what it was
# that declined to account for it. A crash trace names neither, which is the distance between
# "appends nothing" and "appends nothing and says so".
[[ -n "$killed_err_text" ]] ||
  problems+=("want a diagnostic on stderr, got nothing")
[[ "$killed_err_text" == *harvest-usage* ]] ||
  problems+=("want the harvester named on stderr, got: $(printf '%q' "$killed_err_text")")
[[ "$killed_err_text" == *"$killed"* ]] ||
  problems+=("want the leaf named on stderr, got: $(printf '%q' "$killed_err_text")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
