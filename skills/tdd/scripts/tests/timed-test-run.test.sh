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
METRICS="$HERE/../metrics.sh"
USUAL="$HERE/../tier-usual.sh"

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
work="$(mktemp -d)"
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

name="a log carrying timed-test-run.sh's own test-run marks renders at least one row under the report's per-tier section"
problems=()
work="$(mktemp -d)"
wrapped "$work" 373 green fast 'skills/tdd/scripts/tests/event.test.sh' true ||
  problems+=("want the wrapped run to exit 0 like the command it ran, it did not")

report_out="$work/report.md"
( cd "$work" && "$METRICS" 373 ) > "$report_out" 2>/dev/null && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want metrics.sh to exit 0 over the log the wrapper wrote, it exited $code")

tiers="$(python3 -c '
import sys
heading = "#### Test-command seconds, by tier"
lines = open(sys.argv[1]).read().splitlines()
if heading not in lines:
    sys.exit("<<no such heading>>")
rows = []
for line in lines[lines.index(heading) + 1:]:
    if line.startswith("####"):
        break
    if not line.startswith("|"):
        continue
    cells = [c.strip() for c in line.strip("|").split("|")]
    if cells[0] in ("tier", "---"):
        continue
    rows.append(cells[0])
print(" ".join(rows))
' "$report_out" 2>&1)"

[[ -n "$tiers" ]] ||
  problems+=("want at least one row under the per-tier section, the report has the heading and nothing under it")
[[ " $tiers " == *" fast "* ]] ||
  problems+=("want a row for the tier the wrapper recorded (fast), the section rows are $(printf '%q' "$tiers")")

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the report was: $(printf '%q' "$(cat "$report_out")")")
rm -rf "$work"
report "$name"


name="a log carrying timed-test-run.sh's own test-run marks gives tier-usual.sh a figure to answer with"
problems=()
work="$(mktemp -d)"
for _ in 1 2; do
  wrapped "$work" 373 green fast 'skills/tdd/scripts/tests/event.test.sh' true ||
    problems+=("want the wrapped run to exit 0 like the command it ran, it did not")
done

usual="$( cd "$work" && "$USUAL" fast 2>/dev/null )" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want tier-usual.sh to exit 0 over the log the wrapper wrote, it exited $code")

[[ "$usual" =~ ^[0-9]+(\.[0-9]+)?$ ]] ||
  problems+=("usual for tier fast: want a number computed from the marks, got $(printf '%q' "$usual")")

[[ "${#problems[@]}" -eq 0 ]] ||
  problems+=("the log was: $(printf '%q' "$(cat "$work/.tdd/events.jsonl" 2>&1)")")
rm -rf "$work"
report "$name"


name="timed-test-run.sh records the command's own exit status on the test-run event, so a reader can say whether that run passed"
problems=()
for want in 7 0; do
  work="$(mktemp -d)"
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


finish
