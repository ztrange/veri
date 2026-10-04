#!/usr/bin/env bash
# Unit tests for scripts/timed-test-run.sh — the wrapper every test-command run a leaf or
# the conductor makes goes through, recording the run in `.tdd/events.jsonl`.
#
# Contract under test:
#   timed-test-run.sh <tier> <suites> <cmd> [args …]
#                        → runs `<cmd> [args …]`, appends exactly one `test-run` line to
#                          `.tdd/events.jsonl` through event.sh (so the eight fixed keys come
#                          with it), and exits with the command's own status.
#   that line            → carries `tier` and `suites` verbatim as given, plus `seconds`, the
#                          wall time the command took, as a whole number.
#
# Run: scripts/tests/timed-test-run.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TIMED="$HERE/../timed-test-run.sh"

source "$HERE/lib/harness.sh"

jget() {
  python3 -c '
import sys, json
obj = json.loads(open(sys.argv[1]).read().splitlines()[0])
key = sys.argv[2]
print(obj[key] if key in obj else "<<missing>>")
' "$1" "$2" 2>/dev/null
}

wrote_log() {
  log="$1/.tdd/events.jsonl"
  [[ -f "$log" ]] && return 0
  problems+=("want one line appended to .tdd/events.jsonl, but no such file under $1")
  return 1
}

wrapped() {
  local tree="$1" issue="$2" phase="$3" tier="$4" suites="$5"
  shift 5
  ( cd "$tree" && env VERI_ISSUE="$issue" VERI_ACTOR=developer VERI_PHASE="$phase" \
      VERI_STEP=1 VERI_ATTEMPT=1 "$TIMED" "$tier" "$suites" "$@" ) >/dev/null 2>&1
}

name="timed-test-run.sh <tier> <suites> <cmd>: runs the command, writes one test-run event carrying tier, suites and seconds, and exits with the command's own status"
problems=()
work="$(scratch_dir)"
suites='skills/tdd/scripts/tests/unit/next-unchecked.test.sh skills/tdd/scripts/tests/event.test.sh'
wrapped "$work" 342 green fast "$suites" sh -c 'exit 7' && code=0 || code=$?

[[ "$code" == 7 ]] ||
  problems+=("want the command's own exit status 7, got $code")

if wrote_log "$work"; then
  lines="$(wc -l < "$log" | tr -d ' ')"
  [[ "$lines" == 1 ]] ||
    problems+=("want exactly 1 line in .tdd/events.jsonl, got $lines")

  got_event="$(jget "$log" event)"
  [[ "$got_event" == test-run ]] ||
    problems+=("event: want test-run, got $(printf '%q' "$got_event")")

  got_tier="$(jget "$log" tier)"
  [[ "$got_tier" == fast ]] ||
    problems+=("tier: want fast, got $(printf '%q' "$got_tier")")

  got_suites="$(jget "$log" suites)"
  [[ "$got_suites" == "$suites" ]] ||
    problems+=("suites: want $(printf '%q' "$suites"), got $(printf '%q' "$got_suites")")

  got_seconds="$(jget "$log" seconds)"
  [[ "$got_seconds" =~ ^[0-9]+$ ]] ||
    problems+=("seconds: want a whole number of seconds, got $(printf '%q' "$got_seconds")")
fi
rm -rf "$work"
report "$name"


name="timed-test-run.sh records the command's own exit status on the test-run event, so a reader can say whether that run passed"
problems=()
for want in 7 0; do
  work="$(scratch_dir)"
  wrapped "$work" 383 red fast 'skills/tdd/scripts/tests/event.test.sh' sh -c "exit $want" &&
    code=0 || code=$?

  [[ "$code" == "$want" ]] ||
    problems+=("want the command's own exit status $want back from the wrapper, got $code")

  if wrote_log "$work"; then
    got_status="$(jget "$log" status)"
    [[ "$got_status" == "$want" ]] ||
      problems+=("status for a command that exited $want: want $want, got $(printf '%q' "$got_status")")
  fi
  rm -rf "$work"
done
report "$name"


name="timed-test-run.sh refuses fewer than three arguments, an empty <tier> or an empty <cmd>: exit 2, the usage line alone on stderr, nothing on stdout, no event written"
problems=()
want_err="usage: timed-test-run.sh <tier> <suites> <cmd> [args …]"
for shape in '' 'all' "all ''" "all '' ''" "'' '' true"; do
  work="$(scratch_dir)"
  eval "args=($shape)"
  ( cd "$work" && "$TIMED" ${args+"${args[@]}"} ) > "$work/out" 2> "$work/err" &&
    code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("args ($shape): want exit 2, got $code")
  [[ ! -s "$work/out" ]] ||
    problems+=("args ($shape): want nothing on stdout, got $(printf '%q' "$(cat "$work/out")")")
  got_err="$(cat "$work/err")"
  [[ "$got_err" == "$want_err" && "$(wc -l < "$work/err" | tr -d ' ')" == 1 ]] ||
    problems+=("args ($shape): want stderr exactly $(printf '%q' "$want_err"), got $(printf '%q' "$got_err")")
  [[ ! -e "$work/.tdd/events.jsonl" ]] ||
    problems+=("args ($shape): want no .tdd/events.jsonl, one was written")
  rm -rf "$work"
done
report "$name"


name="timed-test-run.sh, run through a symlink to the skill directory and from another working directory, answers as in place: the command's own status, the same stdout and stderr, event.sh found, and its one test-run line in the caller's .tdd/events.jsonl"
problems=()
here_tree="$(scratch_dir)"
far_tree="$(scratch_dir)"
links="$(scratch_dir)"
ln -s "$HERE/../.." "$links/skill"
cmd=(sh -c 'echo out; echo err >&2; exit 5')

( cd "$here_tree" && env VERI_ISSUE=804 VERI_ACTOR=developer VERI_PHASE=red VERI_STEP=1 \
    VERI_ATTEMPT=1 "$TIMED" fast 'x.test.sh' "${cmd[@]}" ) \
  > "$here_tree/out" 2> "$here_tree/err" && here_code=0 || here_code=$?
( cd "$far_tree" && env VERI_ISSUE=804 VERI_ACTOR=developer VERI_PHASE=red VERI_STEP=1 \
    VERI_ATTEMPT=1 "$links/skill/scripts/timed-test-run.sh" fast 'x.test.sh' "${cmd[@]}" ) \
  > "$far_tree/out" 2> "$far_tree/err" && far_code=0 || far_code=$?

[[ "$here_code" == 5 && "$far_code" == 5 ]] ||
  problems+=("want the command's own exit status 5 both ways, got $here_code in place and $far_code through the link")
[[ "$(cat "$far_tree/out")" == "$(cat "$here_tree/out")" && "$(cat "$far_tree/out")" == out ]] ||
  problems+=("stdout: want $(printf '%q' "$(cat "$here_tree/out")") as in place, got $(printf '%q' "$(cat "$far_tree/out")")")
[[ "$(cat "$far_tree/err")" == "$(cat "$here_tree/err")" && "$(cat "$far_tree/err")" == err ]] ||
  problems+=("stderr: want $(printf '%q' "$(cat "$here_tree/err")") as in place, got $(printf '%q' "$(cat "$far_tree/err")")")

if wrote_log "$far_tree"; then
  lines="$(wc -l < "$log" | tr -d ' ')"
  [[ "$lines" == 1 ]] ||
    problems+=("want exactly 1 line in the caller's .tdd/events.jsonl, got $lines")
  got_event="$(jget "$log" event)"
  got_status="$(jget "$log" status)"
  [[ "$got_event" == test-run && "$got_status" == 5 ]] ||
    problems+=("want a test-run line with status 5, got event $(printf '%q' "$got_event") status $(printf '%q' "$got_status")")
fi
[[ ! -e "$links/.tdd" && ! -e "$HERE/../../.tdd" ]] ||
  problems+=("want the line under the caller's working directory only, a .tdd appeared beside the skill")
rm -rf "$here_tree" "$far_tree" "$links"
report "$name"


finish
