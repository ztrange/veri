#!/usr/bin/env bash
# Unit tests for scripts/event.sh — the one-line writer every conductor mark goes through.
#
# Contract under test:
#   event.sh <event> [key=value …]  → appends one line to `.tdd/events.jsonl`, relative to
#                                     the directory it is run in, and exits 0.
#   that line                       → parses as JSON, and carries `ts`, `issue`, `actor`,
#                                     `phase`, `step`, `event` and `attempt`, plus one key
#                                     per `key=value` argument given.
#   `ts`                            → seconds since the epoch.
#   the run context arrives in the environment as `VERI_ISSUE`, `VERI_ACTOR`, `VERI_PHASE`,
#   `VERI_STEP` and `VERI_ATTEMPT`.
#
# Run: scripts/tests/event.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EVENT="$HERE/../event.sh"

source "$HERE/lib/harness.sh"

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

jget() {
  python3 -c '
import sys, json
obj = json.loads(open(sys.argv[1]).read().splitlines()[0])
key = sys.argv[2]
print(obj[key] if key in obj else "<<missing>>")
' "$1" "$2" 2>/dev/null
}

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

want_field() {
  local file="$1" key="$2" expected="$3" got
  got="$(jget "$file" "$key")"
  [[ "$got" == "$expected" ]] ||
    problems+=("$key: want $(printf '%q' "$expected"), got $(printf '%q' "$got")")
}

want_present() {
  local file="$1" key="$2"
  [[ "$(jget "$file" "$key")" != "<<missing>>" ]] ||
    problems+=("$key: want the key present anyway, got it missing")
}

name="event.sh <event> key=value appends one line to .tdd/events.jsonl that parses as JSON and carries ts, issue, actor, phase, step, event and attempt plus every payload given"
problems=()
ctx_work="$(scratch_dir)"
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

name="no run context in the environment: the line is still appended, still parses, and still carries all seven fixed keys"
problems=()
noctx_work="$(scratch_dir)"
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

name="successive calls accumulate: the first creates the log and each later one appends, leaving one line per call in the order they happened"
problems=()
acc_work="$(scratch_dir)"
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
  acc_got="$(jevents "$acc_log" | tr '\n' ' ')"
  acc_got="${acc_got% }"
  [[ "$acc_got" == "$acc_want" ]] ||
    problems+=("want the events $(printf '%q' "$acc_want"), got $(printf '%q' "$acc_got")")
fi
rm -rf "$acc_work"
report "$name"

name="event.sh writes VERI_SKILL_COMMIT from the environment as the fixed key skill_commit, present on every line whether or not the variable is set"
problems=()
sc_work="$(scratch_dir)"
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

unset_work="$(scratch_dir)"
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


normalize_ts() {
  sed -E 's/"ts": [0-9]+/"ts": 0/; s/"awake": [0-9]+/"awake": 0/' <<< "$1"
}

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
esc_work="$(scratch_dir)"
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

  if want_parses "$esc_log"; then
    want_field "$esc_log" reason "$esc_payload"
  fi
fi
rm -rf "$esc_work"
report "$name"

name="#486: event.sh writes an awake-clock reading on every line — the answer of the executable VERI_AWAKE_CLOCK names when set, and time.monotonic()'s whole seconds when it is unset"
problems=()
aw_work="$(scratch_dir)"
cat > "$aw_work/awake-clock" <<'C'
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

name="event.sh run with VERI_AWAKE_CLOCK naming a clock with no #! line that exits 3 exits 3, with .tdd created and nothing appended to .tdd/events.jsonl"
problems=()
ac_work="$(scratch_dir)"
cat > "$ac_work/awake-clock" <<'C'
exit 3
C
chmod +x "$ac_work/awake-clock"
mkdir "$ac_work/run"
( cd "$ac_work/run" && env VERI_AWAKE_CLOCK="$ac_work/awake-clock" "$EVENT" step-start ) >/dev/null 2>&1
ac_code=$?
[[ "$ac_code" == 3 ]] || problems+=("want exit 3 (the clock's own status), got $ac_code")
[[ -d "$ac_work/run/.tdd" ]] || problems+=("want .tdd created before the clock runs, found none")
[[ ! -s "$ac_work/run/.tdd/events.jsonl" ]] ||
  problems+=("want nothing appended to .tdd/events.jsonl, got $(printf '%q' "$(cat "$ac_work/run/.tdd/events.jsonl")")")
rm -rf "$ac_work"
report "$name"

name="event.sh with no argument exits 2 with nothing on stdout, stderr exactly the one line usage: event.sh <event> [key=value …], and no .tdd created"
problems=()
na_work="$(scratch_dir)"
( cd "$na_work" && "$EVENT" ) > "$na_work/out" 2> "$na_work/err"
na_code=$?
[[ "$na_code" == 2 ]] || problems+=("want exit 2, got $na_code")
[[ ! -s "$na_work/out" ]] || problems+=("stdout: want nothing, got $(printf '%q' "$(cat "$na_work/out")")")
na_want="$(printf '%s\n' 'usage: event.sh <event> [key=value …]' | od -c)"
na_got="$(od -c < "$na_work/err")"
[[ "$na_got" == "$na_want" ]] || problems+=("stderr: want exactly the usage line, got $(printf '%q' "$(cat "$na_work/err")")")
[[ ! -e "$na_work/.tdd" ]] || problems+=("want no .tdd created, found one")
rm -rf "$na_work"
report "$name"

name="event.sh with .tdd a regular file in the working directory exits 1 and leaves that file byte-identical"
problems=()
tf_work="$(scratch_dir)"
printf 'not a directory\n' > "$tf_work/.tdd"
cp "$tf_work/.tdd" "$tf_work/tdd.before"
( cd "$tf_work" && env VERI_AWAKE_CLOCK=/usr/bin/true "$EVENT" step-start ) >/dev/null 2>&1
tf_code=$?
[[ "$tf_code" == 1 ]] || problems+=("want exit 1, got $tf_code")
if [[ -f "$tf_work/.tdd" ]] && cmp -s "$tf_work/.tdd" "$tf_work/tdd.before"; then
  :
else
  problems+=(".tdd: want the regular file left byte-identical, got $(ls -ld "$tf_work/.tdd" 2>&1)")
fi
rm -rf "$tf_work"
report "$name"

name="#563: event.sh's awake reading is the system-wide awake clock, so it advances across processes under a python3 whose time.monotonic() restarts per process"
problems=()
rs_work="$(scratch_dir)"
rs_real="$(command -v python3)"
cat > "$rs_work/python3" <<P
if [ "\$1" = -c ]; then
  shift
  exec "$rs_real" -c 'import sys, time
_read, _born = time.monotonic, time.monotonic()
time.monotonic = lambda: _read() - _born
_code = sys.argv[1]
sys.argv = sys.argv[:1] + sys.argv[2:]
exec(_code)' "\$@"
fi
exec "$rs_real" "\$@"
P
{ printf '%s\n' '#!/bin/sh'; cat "$rs_work/python3"; } > "$rs_work/python3.new" && mv "$rs_work/python3.new" "$rs_work/python3"
chmod +x "$rs_work/python3"
rs_clock='import time; print(int(time.clock_gettime(getattr(time, "CLOCK_UPTIME_RAW", time.CLOCK_MONOTONIC))))'
mkdir "$rs_work/run"
rs_before="$("$rs_real" -c "$rs_clock")"
( cd "$rs_work/run" && env -u VERI_AWAKE_CLOCK PATH="$rs_work:$PATH" "$EVENT" step-start ) >/dev/null 2>&1
rs_code=$?
rs_after="$("$rs_real" -c "$rs_clock")"
[[ "$rs_code" == 0 ]] || problems+=("want exit 0, got $rs_code")
if [[ -f "$rs_work/run/.tdd/events.jsonl" ]] && want_parses "$rs_work/run/.tdd/events.jsonl"; then
  rs_got="$(jget "$rs_work/run/.tdd/events.jsonl" awake)"
  if [[ "$rs_got" =~ ^[0-9]+$ ]] && (( rs_before <= rs_got && rs_got <= rs_after )); then
    :
  else
    problems+=("awake: want the system-wide awake clock's whole seconds, between $rs_before and $rs_after, got $(printf '%q' "$rs_got")")
  fi
else
  problems+=("want a line in .tdd/events.jsonl, found none")
fi
rm -rf "$rs_work"
report "$name"

name="#726: event.sh refuses a structural-pass mark whose stopped= is not one of the three reasons with exit 2, naming the value and the three allowed ones, and appends nothing"
problems=()
sp_work="$(scratch_dir)"
sp_err="$( cd "$sp_work" && env VERI_ISSUE=612 VERI_ACTOR=conductor VERI_AWAKE_CLOCK=/usr/bin/true \
    "$EVENT" structural-pass transforms=0 budget=10 stopped=test-files-only 2>&1 >/dev/null )" && sp_code=0 || sp_code=$?
[[ "$sp_code" == 2 ]] || problems+=("want exit 2, got $sp_code")
for sp_word in test-files-only candidates-done budget-spent nothing-structural; do
  [[ "$sp_err" == *"$sp_word"* ]] ||
    problems+=("stderr: want it to name $sp_word, got $(printf '%q' "$sp_err")")
done
[[ ! -s "$sp_work/.tdd/events.jsonl" ]] ||
  problems+=("want nothing appended to .tdd/events.jsonl, got $(printf '%q' "$(cat "$sp_work/.tdd/events.jsonl")")")
report "$name"

name="#726: event.sh refuses a structural-pass mark carrying no stopped= with exit 2, naming the three allowed reasons, and appends nothing"
problems=()
ns_work="$(scratch_dir)"
ns_err="$( cd "$ns_work" && env VERI_ISSUE=134 VERI_ACTOR=conductor VERI_AWAKE_CLOCK=/usr/bin/true \
    "$EVENT" structural-pass transforms=0 budget=10 2>&1 >/dev/null )" && ns_code=0 || ns_code=$?
[[ "$ns_code" == 2 ]] || problems+=("want exit 2, got $ns_code")
for ns_word in candidates-done budget-spent nothing-structural; do
  [[ "$ns_err" == *"$ns_word"* ]] ||
    problems+=("stderr: want it to name $ns_word, got $(printf '%q' "$ns_err")")
done
[[ ! -s "$ns_work/.tdd/events.jsonl" ]] ||
  problems+=("want nothing appended to .tdd/events.jsonl, got $(printf '%q' "$(cat "$ns_work/.tdd/events.jsonl")")")
report "$name"

name="#726: event.sh refuses a structural-pass mark with stopped=budget-spent whose transforms is not equal to its budget with exit 2, and appends nothing"
problems=()
bs_work="$(scratch_dir)"
( cd "$bs_work" && env VERI_ISSUE=496 VERI_ACTOR=conductor VERI_AWAKE_CLOCK=/usr/bin/true \
    "$EVENT" structural-pass transforms=0 budget=10 stopped=budget-spent >/dev/null 2>&1 ) && bs_code=0 || bs_code=$?
[[ "$bs_code" == 2 ]] || problems+=("want exit 2, got $bs_code")
[[ ! -s "$bs_work/.tdd/events.jsonl" ]] ||
  problems+=("want nothing appended to .tdd/events.jsonl, got $(printf '%q' "$(cat "$bs_work/.tdd/events.jsonl")")")
report "$name"

finish
