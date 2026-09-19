#!/usr/bin/env bash
# Unit tests for scripts/timed-test-run.sh — the wrapper every test-command run a leaf or
# the conductor makes goes through, so that a run's tier, the suites it covered and the wall
# seconds it took are recorded in `.tdd/events.jsonl` instead of living only in a log a human
# reads by eye (issue #342, part of PRD #335).
# Zero-dependency plain-shell asserts, same idiom as event.test.sh.
#
# Contract under test (this step only — one wrapped run, one line):
#   timed-test-run.sh <tier> <suites> <cmd> [args …]
#                        → runs `<cmd> [args …]`, appends exactly one `test-run` line to
#                          `.tdd/events.jsonl` through event.sh (so the eight fixed keys come
#                          with it), and exits with the command's OWN status.
#   that line            → carries `tier` and `suites` verbatim as given, plus `seconds`, the
#                          wall time the command took.
#
# `seconds` is asserted as present and as a whole number, never as a value: the seconds are
# recorded for a reader to compare against a tier's usual, and a suite that pinned a duration
# would be asserting cost rather than behaviour (CLAUDE.md, "Testing idiom").
#
# The command's own status is the load-bearing half of the wrapper's promise: a test command
# exits 1 when the suite it ran failed, and every caller here branches on that. A wrapper that
# swallowed it — or that returned event.sh's status instead — would turn a red suite green.
#
# Run: scripts/tests/timed-test-run.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TIMED="$HERE/../timed-test-run.sh"
pass=0 fail=0

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

# jget <file> <key> — the value of <key> on the file's first line, or `<<missing>>`. The same
# `json.loads` read metrics.sh makes of this log, so a value read back here is what a reader
# of the run would get, not merely what bytes landed. python3 rather than jq: the repo already
# depends on the interpreter and not on jq.
jget() {
  python3 -c '
import sys, json
obj = json.loads(open(sys.argv[1]).read().splitlines()[0])
key = sys.argv[2]
print(obj[key] if key in obj else "<<missing>>")
' "$1" "$2" 2>/dev/null
}

# 1. The whole of this step's criterion, as one case: one wrapped run writes one `test-run`
#    line carrying its tier, its suites and its seconds, and hands the caller back the
#    command's own status.
#
#    The command is `sh -c 'exit 7'` — neither 0 nor 1, so a wrapper that reports its own
#    success, or event.sh's, or a plain "the command failed", is caught rather than passed.
#    The suites argument holds two paths separated by a space, which is what a caller already
#    has in hand: affected-suites.sh prints one suite path per line and a caller joins them.
#    `env` sets the run context for this child only, so the answer is a fact about the script
#    and not about whatever the shell running `make test` exported (hermetic-suites.test.sh's
#    concern).
name="timed-test-run.sh <tier> <suites> <cmd>: runs the command, writes one test-run event carrying tier, suites and seconds, and exits with the command's own status"
problems=()
work="$(mktemp -d)"
log="$work/.tdd/events.jsonl"
suites='skills/tdd/scripts/tests/unit/next-unchecked.test.sh skills/tdd/scripts/tests/event.test.sh'
( cd "$work" && env VERI_ISSUE=342 VERI_ACTOR=developer VERI_PHASE=green VERI_STEP=1 \
    VERI_ATTEMPT=1 "$TIMED" fast "$suites" sh -c 'exit 7' ) >/dev/null 2>&1 && code=0 || code=$?

[[ "$code" == 7 ]] ||
  problems+=("want the command's own exit status 7, got $code")

if [[ ! -f "$log" ]]; then
  problems+=("want one line appended to .tdd/events.jsonl, but no such file under $work")
else
  # Exactly one line for exactly one run: a wrapper that marked both a start and an end would
  # make every reader of this log count each run twice.
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

  # Present and a whole number of seconds — the value itself is the run's to report and this
  # suite's never to pin.
  got_seconds="$(jget "$log" seconds)"
  [[ "$got_seconds" =~ ^[0-9]+$ ]] ||
    problems+=("seconds: want a whole number of seconds, got $(printf '%q' "$got_seconds")")
fi
rm -rf "$work"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
