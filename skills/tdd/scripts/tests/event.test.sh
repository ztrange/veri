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

name="event.sh run through a symlink to the skill's scripts directory from another working directory appends its line to that working directory's .tdd/events.jsonl and creates nothing beside the scripts"
problems=()
sl_work="$(scratch_dir)"
sl_scripts="$(cd "$HERE/.." && pwd)"
ln -s "$sl_scripts" "$sl_work/linked-scripts"
mkdir "$sl_work/run"
printf '#!/bin/sh\necho 7\n' > "$sl_work/awake-clock"
chmod +x "$sl_work/awake-clock"
sl_before="$(ls -A "$sl_scripts")"
( cd "$sl_work/run" && env VERI_AWAKE_CLOCK="$sl_work/awake-clock" "$sl_work/linked-scripts/event.sh" symlinked-mark ) >/dev/null 2>&1
sl_code=$?
sl_after="$(ls -A "$sl_scripts")"
[[ "$sl_code" == 0 ]] || problems+=("want exit 0, got $sl_code")
if [[ -f "$sl_work/run/.tdd/events.jsonl" ]]; then
  sl_events="$(jevents "$sl_work/run/.tdd/events.jsonl")"
  [[ "$sl_events" == symlinked-mark ]] ||
    problems+=("want one line, event symlinked-mark, got $(printf '%q' "$sl_events")")
else
  problems+=("want a line in the working directory's .tdd/events.jsonl, found none")
fi
[[ "$sl_after" == "$sl_before" ]] ||
  problems+=("want nothing created beside the scripts, got $(diff <(printf '%s\n' "$sl_before") <(printf '%s\n' "$sl_after") | tr '\n' ' ')")
rm -rf "$sl_work"
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

finish
