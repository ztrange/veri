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

# want_parses <file> — one probe, appended to the caller's `problems`: the file's first line
# is a JSON object. Asserted on its own, ahead of every field probe, so a line that is not
# JSON at all says so once instead of showing seven missing keys — and its true/false is also
# the caller's cue to skip those probes, since they all read that same line and would each
# report the same broken line again. python3 rather than jq: extract-result.sh already execs
# python3 in production, so the interpreter is a dependency the repo has, and jq is not.
want_parses() {
  python3 -c '
import sys, json
line = open(sys.argv[1]).read().splitlines()[0]
obj = json.loads(line)
if not isinstance(obj, dict):
    raise SystemExit("not a JSON object")
' "$1" 2>/dev/null && return 0
  problems+=("want the line to parse as a JSON object, got: $(printf '%q' "$(head -1 "$1")")")
  return 1
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

# jevents <file> — print the `event` value of every line in the file, in file order, one per
# line: the log read the way a reader of a whole run reads it, rather than `jget`'s single
# first line. A line that is not a JSON object prints `<<unparseable>>` and a line without the
# key prints `<<missing>>`, so a broken line is visible in its own position instead of
# collapsing the sequence and being mistaken for a missing call.
jevents() {
  python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        print("<<unparseable>>")
        continue
    print(obj.get("event", "<<missing>>") if isinstance(obj, dict) else "<<unparseable>>")
' "$1" 2>/dev/null
}

# want_field <file> <key> <expected> — one field probe, appended to the caller's `problems`.
want_field() {
  local file="$1" key="$2" expected="$3" got
  got="$(jget "$file" "$key")"
  [[ "$got" == "$expected" ]] ||
    problems+=("$key: want $(printf '%q' "$expected"), got $(printf '%q' "$got")")
}

# want_present <file> <key> — one probe, appended to the caller's `problems`: <key> is on the
# line at all. The weaker half of `want_field`, and what a fixed key is asserted with when its
# value is not this suite's to say — the whole of the promise there is that a reader never has
# to tell an absent key from an unknown value, so presence is the pin and the value is not.
want_present() {
  local file="$1" key="$2"
  [[ "$(jget "$file" "$key")" != "<<missing>>" ]] ||
    problems+=("$key: want the key present anyway, got it missing")
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

  if want_parses "$ctx_log"; then
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
elif want_parses "$noctx_log"; then
  for key in ts issue actor phase step event attempt; do
    want_present "$noctx_log" "$key"
  done
  want_field "$noctx_log" event resume
fi
rm -rf "$noctx_work"
report "$name"

# 3. The log accumulates. One call is one line, but a run is many calls, and what makes the
#    file a log rather than a note is that the second call adds to what the first wrote: the
#    conductor's marks arrive as separate processes, each one a fresh `event.sh`, so a writer
#    that opened the file for writing instead of for appending would leave a file holding
#    only whichever mark came last — the same file, the same single parseable line, and every
#    probe of case 1 still green. Three calls with three distinct event names, made in a
#    directory that has no `.tdd` at all, so the first call is also the one that has to create
#    the log; the pin is the whole sequence in the order the calls were made, which a
#    truncating writer cannot produce and a writer that prepended would produce reversed.
name="successive calls accumulate: the first creates the log and each later one appends, leaving one line per call in the order they happened"
problems=()
acc_work="$(mktemp -d)"
acc_log="$acc_work/.tdd/events.jsonl"
acc_want="step-start pin step-done"

for ev in step-start pin step-done; do
  ( cd "$acc_work" && env VERI_ISSUE=107 VERI_ACTOR=conductor VERI_PHASE=red VERI_STEP=3 \
      VERI_ATTEMPT=1 "$EVENT" "$ev" ) >/dev/null 2>&1 ||
    problems+=("want exit 0 from the $ev call, got $?")
done

if [[ ! -f "$acc_log" ]]; then
  problems+=("want the log created by the first call, but no .tdd/events.jsonl under $acc_work")
else
  # The `event` field of each line, joined with spaces so one probe reports the whole
  # sequence: `tr` turns the newlines into spaces and `${acc_got% }` drops the trailing one
  # the last newline leaves behind.
  acc_got="$(jevents "$acc_log" | tr '\n' ' ')"
  acc_got="${acc_got% }"
  [[ "$acc_got" == "$acc_want" ]] ||
    problems+=("want the events $(printf '%q' "$acc_want"), got $(printf '%q' "$acc_got")")
fi
rm -rf "$acc_work"
report "$name"

# 4. The skill commit is a fixed key, and it comes from the environment (issue #165). A run
#    executes whatever is installed at `~/.claude/skills/tdd`, a symlink into a clone that
#    `main` moves under it, so which commit a leaf was launched under is a fact only the log
#    can carry. It arrives the way the other run-wide context does — in the environment, as
#    `VERI_SKILL_COMMIT` — and not on the command line, so no caller has to remember to pass
#    it and every line of the run answers the question the same way.
#
#    `fixed` is the whole of the pin, and it is what makes the two halves below one case: a
#    payload key is present when the caller passed it, while a fixed key is present on every
#    line whatever the environment holds. So the call with the variable set must write that
#    sha, and the call with it unset must still carry the key — a writer that emitted it only
#    when set would leave a reader unable to tell a skill whose commit is not known from a
#    line written before this key existed, which is exactly the ambiguity case 2 refuses for
#    the other seven. The unset half probes presence only, not a value: what an unresolvable
#    commit should read as is the resolver's question, not the writer's.
#
#    `env` sets and unsets for these children only, so the answer is a fact about the script
#    rather than about whatever the shell running `make test` exported (hermetic-suites.test.sh's
#    concern, and #87's bail). The sha is a real-looking 40 hex digits and distinct from every
#    other value on the line, so a writer that put it under the wrong key is caught.
name="event.sh writes VERI_SKILL_COMMIT from the environment as the fixed key skill_commit, present on every line whether or not the variable is set"
problems=()
sc_work="$(mktemp -d)"
sc_log="$sc_work/.tdd/events.jsonl"
sc_sha="9f3c1ab7d0e4f52618bc90a7de4415f0b2c83d61"

( cd "$sc_work" && env VERI_ISSUE=165 VERI_ACTOR=conductor VERI_PHASE=red VERI_STEP=1 \
    VERI_ATTEMPT=1 VERI_SKILL_COMMIT="$sc_sha" "$EVENT" launch ) >/dev/null 2>&1 ||
  problems+=("want exit 0 from the call with VERI_SKILL_COMMIT set, got $?")

if [[ ! -f "$sc_log" ]]; then
  problems+=("want the line appended to .tdd/events.jsonl, but no such file under $sc_work")
elif want_parses "$sc_log"; then
  want_field "$sc_log" skill_commit "$sc_sha"
fi

# The second call goes to its own directory, so `jget`'s first line is the line this half
# wrote rather than the one above it.
unset_work="$(mktemp -d)"
unset_log="$unset_work/.tdd/events.jsonl"
( cd "$unset_work" && env -u VERI_SKILL_COMMIT "$EVENT" launch ) >/dev/null 2>&1 ||
  problems+=("want exit 0 from the call with VERI_SKILL_COMMIT unset, got $?")

if [[ ! -f "$unset_log" ]]; then
  problems+=("want the line appended anyway, but no .tdd/events.jsonl under $unset_work")
elif want_parses "$unset_log"; then
  want_present "$unset_log" skill_commit
fi
rm -rf "$sc_work" "$unset_work"
report "$name"


# 5. Escaping is the one thing a payload cannot be trusted to arrive without (issue #290): a
#    verifier's reason is English a model wrote, and a step's title or a kill cause can carry
#    any of it. A payload here is not asked merely to PARSE — a JSON encoder has more than one
#    valid way to escape the same string, and this pins the one THIS writer must produce,
#    byte for byte, because #290's whole premise is that a bash rewrite of what used to be
#    `python3 -c '... json.dumps(line) ...'` may change how the line is COMPOSED (no more
#    interpreter) but not what it reads as, down to the byte: `metrics.sh` and every suite
#    here keep reading the file the same way, whichever writer produced a given line.
#
#    The payload carries, in one string, every class of byte `json.dumps(str,
#    ensure_ascii=True)` — python's default, which is what this line has always been checked
#    against — treats specially: a double quote and a backslash (the two characters JSON
#    escaping exists for at all), a newline and a tab (the two-character short escapes,
#    `\n` `\t`), a control byte with no short escape (`\x01`, which must become `\u0001`),
#    and two non-ASCII characters — `é` (a single UTF-16 code unit, `\u00e9`) and an emoji
#    past the Basic Multilingual Plane (`😀`, which `ensure_ascii` can only spell as a UTF-16
#    SURROGATE PAIR, `\ud83d\ude00` — there is no single `\uXXXX` for a code point above
#    0xffff). A writer that got any one of these wrong would still often produce valid JSON —
#    a different but still-legal escaping, or a truncated string that happens to close — so
#    "parses" alone is not this case's pin.
#
#    `reference_line` is a live python3 process building the SAME dict, in the SAME field
#    order, through `json.dumps` itself — the independent oracle event.sh used to call
#    directly and now only has to still agree with. `ts` is blanked to `0` on both sides
#    (`normalize_ts`) before the comparison, since it is the one field neither side can pin to
#    a shared value — a whole-number-of-seconds probe is case 1's job, not this one's.
normalize_ts() {
  # sed rather than a third python3 call: the ts field is always `"ts": <digits>` at a fixed
  # position (event.sh writes it first), so a text substitution is exact and does not risk
  # re-serializing the very line this case is pinning the bytes of.
  # `awake` (#486) follows `ts` and is blanked the same way, for the same reason.
  sed -E 's/"ts": [0-9]+/"ts": 0/; s/"awake": [0-9]+/"awake": 0/' <<< "$1"
}

# reference_line <issue> <actor> <phase> <step> <event> <attempt> <skill_commit> [key=value …]
# — the dict event.sh's OLD python3 block built, in the same field order, dumped by a live
# python3 rather than composed here: the oracle this case checks the bash rewrite against has
# to be independent of it, or a bug shared by both would go uncaught.
reference_line() {
  python3 -c '
import json, sys

d = {
    "ts": 0,
    "awake": 0,
    "issue": sys.argv[1],
    "actor": sys.argv[2],
    "phase": sys.argv[3],
    "step": sys.argv[4],
    "event": sys.argv[5],
    "attempt": sys.argv[6],
    "skill_commit": sys.argv[7],
}
for arg in sys.argv[8:]:
    key, _, value = arg.partition("=")
    d[key] = value
print(json.dumps(d))
' "$@"
}

name="a payload with a double quote, a backslash, a newline, a tab, a control byte and two non-ASCII characters (one past the Basic Multilingual Plane) round-trips through event.sh into a line byte-identical to json.dumps's own, and metrics.sh's own json.loads reads it back unchanged"
problems=()
esc_work="$(mktemp -d)"
esc_log="$esc_work/.tdd/events.jsonl"
esc_payload=$'a "quoted" \ word
next line	indented  café 😀 end'

( cd "$esc_work" && env VERI_ISSUE=290 VERI_ACTOR=developer VERI_PHASE=green VERI_STEP=9     VERI_ATTEMPT=1 VERI_SKILL_COMMIT=deadbeef "$EVENT" step-start "reason=$esc_payload" ) >/dev/null 2>&1
esc_code=$?
[[ "$esc_code" == 0 ]] || problems+=("want exit 0, got $esc_code")

if [[ ! -f "$esc_log" ]]; then
  problems+=("want the line appended to .tdd/events.jsonl, but no such file under $esc_work")
else
  esc_got_line="$(sed -n 1p "$esc_log")"
  esc_want_line="$(reference_line 290 developer green 9 step-start 1 deadbeef "reason=$esc_payload")"
  esc_got_norm="$(normalize_ts "$esc_got_line")"
  esc_want_norm="$(normalize_ts "$esc_want_line")"
  [[ "$esc_got_norm" == "$esc_want_norm" ]] ||
    problems+=("want the line byte-identical to json.dumps's own (ts blanked): got $(printf '%q' "$esc_got_norm"), want $(printf '%q' "$esc_want_norm")")

  # metrics.sh reads this file through the same `json.loads`, one line at a time
  # (metrics.sh:151-160-ish) — `jget` is that same read, so a value read back through it is
  # what metrics.sh itself would see, not merely what this suite's own probes accept.
  if want_parses "$esc_log"; then
    want_field "$esc_log" reason "$esc_payload"
  fi
fi
rm -rf "$esc_work"
report "$name"

# #486: every line carries `awake`, a reading of the clock that does not advance while the
# machine sleeps, so metrics.sh can tell a slow span from one the machine slept through. Two
# probes, one per half of the criterion: with VERI_AWAKE_CLOCK naming an executable, the reading
# is that executable's answer (a stub printing a fixed number, so no sleep is needed); with it
# unset, the reading is supervise.sh's own awake clock, python's time.monotonic() — bracketed
# by a read taken just before and one just after the call, since a real clock cannot be pinned
# to one value.
name="#486: event.sh writes an awake-clock reading on every line — the answer of the executable VERI_AWAKE_CLOCK names when set, and time.monotonic()'s whole seconds when it is unset"
problems=()
aw_work="$(mktemp -d)"
cat > "$aw_work/awake-clock" <<'C'
#!/bin/sh
echo 424242
C
chmod +x "$aw_work/awake-clock"
mkdir "$aw_work/stub" "$aw_work/real"

( cd "$aw_work/stub" && env VERI_AWAKE_CLOCK="$aw_work/awake-clock" "$EVENT" step-start ) >/dev/null 2>&1
aw_code=$?
[[ "$aw_code" == 0 ]] || problems+=("VERI_AWAKE_CLOCK set: want exit 0, got $aw_code")
if [[ -f "$aw_work/stub/.tdd/events.jsonl" ]] && want_parses "$aw_work/stub/.tdd/events.jsonl"; then
  aw_got="$(jget "$aw_work/stub/.tdd/events.jsonl" awake)"
  [[ "$aw_got" == 424242 ]] ||
    problems+=("VERI_AWAKE_CLOCK set: awake: want 424242 (the injected clock's answer), got $(printf '%q' "$aw_got")")
else
  problems+=("VERI_AWAKE_CLOCK set: want a line in .tdd/events.jsonl, found none")
fi

aw_before="$(python3 -c 'import time; print(int(time.monotonic()))')"
( cd "$aw_work/real" && env -u VERI_AWAKE_CLOCK "$EVENT" step-start ) >/dev/null 2>&1
aw_code=$?
aw_after="$(python3 -c 'import time; print(int(time.monotonic()))')"
[[ "$aw_code" == 0 ]] || problems+=("VERI_AWAKE_CLOCK unset: want exit 0, got $aw_code")
if [[ -f "$aw_work/real/.tdd/events.jsonl" ]] && want_parses "$aw_work/real/.tdd/events.jsonl"; then
  aw_got="$(jget "$aw_work/real/.tdd/events.jsonl" awake)"
  if [[ "$aw_got" =~ ^[0-9]+$ ]] && (( aw_before <= aw_got && aw_got <= aw_after )); then
    :
  else
    problems+=("VERI_AWAKE_CLOCK unset: awake: want time.monotonic()'s whole seconds, between $aw_before and $aw_after, got $(printf '%q' "$aw_got")")
  fi
else
  problems+=("VERI_AWAKE_CLOCK unset: want a line in .tdd/events.jsonl, found none")
fi
rm -rf "$aw_work"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
