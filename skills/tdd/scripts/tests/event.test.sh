#!/usr/bin/env bash
# Unit tests for scripts/event.sh — the one-line writer every conductor mark goes through,
# and the first clock in the system (issue #107, ADR-0014: observability is a per-run event
# log written by the scripts, not a service).
# Zero-dependency plain-shell asserts, same idiom as leaf-timeout.test.sh.
#
# Contract under test (this step only — one `event.sh` call, one line):
#   event.sh <event> [key=value …]  → appends one line to `.tdd/events.jsonl`, relative to
#                                     the directory it is run in (the issue's worktree, the
#                                     way supervise.sh already spells `.tdd/<name>.log`),
#                                     and exits 0.
#   that line                       → parses as JSON, and carries `ts`, `issue`, `actor`,
#                                     `phase`, `step`, `event` and `attempt`, plus one key
#                                     per `key=value` argument given.
#   `ts`                            → seconds since the epoch. The issue leaves the choice
#                                     open ("seconds since the epoch, or ISO-8601 — pick
#                                     one and pin it"); this suite picks the epoch count,
#                                     which is what supervise.sh's own `now()` already
#                                     reads out of `date +%s`, so the log and the watchdog
#                                     measure in the same unit and a reader subtracts two
#                                     marks without parsing a calendar.
#
# The run context — which issue, which actor, which phase, which step, which attempt — is
# NOT on the command line: it arrives in the environment as `VERI_ISSUE`, `VERI_ACTOR`,
# `VERI_PHASE`, `VERI_STEP` and `VERI_ATTEMPT`. Two reasons, both already precedents here.
# It is what the criterion's own shape says — those seven fields, "plus every key=value
# payload given" — so the payload stays the caller's to choose and the context stays the
# run's. And it is how the conductor already hands a run-wide fact to every child: SKILL.md
# preflight exports VERI_TIMEOUT once "in the conductor's own shell … for every supervise.sh
# in every phase of every cycle below; nothing else has to pass it". A mark the procedure
# prescribes beside an issue comment has to be short enough to be followed.
#
# Run: scripts/tests/event.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EVENT="$HERE/../event.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
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

# parses <file> — true when the file's first line is a JSON object. python3 rather than jq:
# extract-result.sh already execs python3 in production, so the interpreter is a dependency
# the repo has, and jq is not. Asserted on its own, ahead of every field probe, so a line
# that is not JSON at all says so once instead of showing seven missing keys.
parses() {
  python3 -c '
import sys, json
line = open(sys.argv[1]).read().splitlines()[0]
obj = json.loads(line)
if not isinstance(obj, dict):
    raise SystemExit("not a JSON object")
' "$1" 2>/dev/null
}

# jget <file> <key> — print the value of <key> from the JSON object on the file's first
# line, or the literal `<<missing>>` when the key is absent. `print()` of the parsed value
# rather than the raw text, so the comparison is against what a reader of the log would get
# — an escaped quote or backslash in a payload has to survive the round trip, not merely
# appear in the bytes. It also leaves `ts` comparable whether it is written as a JSON number
# or as a string of digits: the unit is the pin, the spelling is not.
jget() {
  python3 -c '
import sys, json
obj = json.loads(open(sys.argv[1]).read().splitlines()[0])
key = sys.argv[2]
print(obj[key] if key in obj else "<<missing>>")
' "$1" "$2" 2>/dev/null
}

# want_field <file> <key> <expected> — one field probe, appended to the caller's `problems`.
want_field() {
  local file="$1" key="$2" expected="$3" got
  got="$(jget "$file" "$key")"
  [[ "$got" == "$expected" ]] ||
    problems+=("$key: want $(printf '%q' "$expected"), got $(printf '%q' "$got")")
}

# 1. The whole of this step's criterion, as one case: one call writes one parseable line
#    that carries the run's context, the event's name and the caller's payload.
#
#    The call is a real one — the mark SKILL.md will prescribe beside the "Step start"
#    comment, in the middle of a run: issue 107, step 3, phase red, attempt 2 (a revise, so
#    not the value a default could accidentally match). Every field is a distinct string, so
#    a writer that put the phase where the step goes is caught rather than passed.
#
#    The two payload arguments are the ones the later steps will actually pass, and each
#    carries the character that makes the "parses as JSON" half of the criterion do work:
#    `cmd` holds spaces and an embedded `=` — the command supervise.sh ran, which splits on
#    the FIRST `=` only, or the value arrives truncated at `VERI_TIMEOUT` — and `reason`
#    holds a double quote and a backslash, which is verify.sh's verdict reason, a line of
#    English written by a model. Concatenating either into a JSON line unescaped produces a
#    file that a reader cannot parse at all, and it is the payload, not the writer, that
#    decides when that happens.
#
#    `env` sets the five context variables for this child only: the answer must be a fact
#    about the script and not about whatever the shell running `make test` exported
#    (hermetic-suites.test.sh's concern, and #87's bail).
#
#    `ts` is probed as a window rather than a value: `before` and `after` bracket the call,
#    so a whole number of seconds inside them is a real clock reading, while a constant, a
#    millisecond count and an ISO-8601 stamp each fall outside or fail the digits test.
name="event.sh <event> key=value appends one line to .tdd/events.jsonl that parses as JSON and carries ts, issue, actor, phase, step, event and attempt plus every payload given"
problems=()
ctx_work="$(mktemp -d)"
ctx_log="$ctx_work/.tdd/events.jsonl"
before="$(date +%s)"
( cd "$ctx_work" && env VERI_ISSUE=107 VERI_ACTOR=conductor VERI_PHASE=red VERI_STEP=3 \
    VERI_ATTEMPT=2 "$EVENT" step-start \
    'cmd=env VERI_TIMEOUT=1200 run-leaf.sh .tdd/develop-red.prompt' \
    'reason=the leaf wrote "no" and a stray \ backslash' ) >/dev/null 2>&1 && code=0 || code=$?
after="$(date +%s)"

[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")

if [[ ! -f "$ctx_log" ]]; then
  problems+=("want the line appended to .tdd/events.jsonl, but no such file under $ctx_work")
else
  # Exactly one line for exactly one call — and `wc -l` counts newlines, so a writer that
  # left the terminator off scores 0 here, which is the same bug as the next event landing
  # on the end of this one.
  lines="$(wc -l < "$ctx_log" | tr -d ' ')"
  [[ "$lines" == 1 ]] ||
    problems+=("want exactly 1 line in .tdd/events.jsonl, got $lines")

  if ! parses "$ctx_log"; then
    problems+=("want the line to parse as a JSON object, got: $(printf '%q' "$(head -1 "$ctx_log")")")
  else
    ts="$(jget "$ctx_log" ts)"
    if [[ ! "$ts" =~ ^[0-9]+$ ]]; then
      problems+=("ts: want a whole number of seconds since the epoch, got $(printf '%q' "$ts")")
    elif (( ts < before || ts > after )); then
      problems+=("ts: want seconds since the epoch within [$before, $after], got $ts")
    fi
    want_field "$ctx_log" issue   107
    want_field "$ctx_log" actor   conductor
    want_field "$ctx_log" phase   red
    want_field "$ctx_log" step    3
    want_field "$ctx_log" event   step-start
    want_field "$ctx_log" attempt 2
    want_field "$ctx_log" cmd     'env VERI_TIMEOUT=1200 run-leaf.sh .tdd/develop-red.prompt'
    want_field "$ctx_log" reason  'the leaf wrote "no" and a stray \ backslash'
  fi
fi
rm -rf "$ctx_work"
report "$name"

# 2. The other half of the same criterion: the seven fixed keys are the line's promise, not
#    a summary of what the caller happened to set. A reader that groups by phase or counts
#    attempts must find them on every line, so a call made with none of the context in the
#    environment still writes all seven — whatever value it can give them — while a writer
#    that emits only the fields it has env for leaves its reader to tell "phase absent" from
#    "phase unknown", which is the ambiguity the harvester's `absence is not zero` rule
#    exists to refuse elsewhere in this issue.
name="no run context in the environment: the line is still appended, still parses, and still carries all seven fixed keys"
problems=()
noctx_work="$(mktemp -d)"
noctx_log="$noctx_work/.tdd/events.jsonl"
( cd "$noctx_work" && env -u VERI_ISSUE -u VERI_ACTOR -u VERI_PHASE -u VERI_STEP -u VERI_ATTEMPT \
    "$EVENT" resume ) >/dev/null 2>&1
if [[ ! -f "$noctx_log" ]]; then
  problems+=("want the line appended anyway, but no .tdd/events.jsonl under $noctx_work")
elif ! parses "$noctx_log"; then
  problems+=("want the line to parse as a JSON object, got: $(printf '%q' "$(head -1 "$noctx_log")")")
else
  for key in ts issue actor phase step event attempt; do
    [[ "$(jget "$noctx_log" "$key")" != "<<missing>>" ]] ||
      problems+=("want the key $key present anyway, got it missing")
  done
  want_field "$noctx_log" event resume
fi
rm -rf "$noctx_work"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
