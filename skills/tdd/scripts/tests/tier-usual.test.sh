#!/usr/bin/env bash
# Unit tests for scripts/tier-usual.sh — what one tier's test-command run usually costs,
# computed from the `test-run` lines timed-test-run.sh already writes (issue #342, part of
# PRD #335). A recorded `seconds` is only a number until there is something to compare it
# against; the usual is that something, and it is the median of the tier's last 10 runs.
# Zero-dependency plain-shell asserts, same idiom as timed-test-run.test.sh next door.
#
# Contract under test (this step only — the figure, not yet the comparison it feeds):
#   tier-usual.sh <tier>  → exit 0, and on stdout the median of the `seconds` on the last 10
#                           `test-run` lines of `.tdd/events.jsonl` whose `tier` is <tier>.
#
# The log is read relative to the directory the script runs in — `.tdd/events.jsonl`, the way
# event.sh writes it (event.sh:60) and the way metrics.sh reads it — so the case below writes
# a hand-made log into a temp directory and runs the script there. Every figure in it is
# fabricated: nothing here times anything, so the answer is arithmetic over injected data
# rather than a duration this machine happened to take (CLAUDE.md, "Testing idiom").
#
# Run: skills/tdd/scripts/tests/tier-usual.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
USUAL="$HERE/../tier-usual.sh"

source "$HERE/lib/harness.sh"

ev() {
  printf '{"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green", "step": "1", "event": "%s", "attempt": "1", "skill_commit": "abc1234", "tier": "%s", "suites": "one.test.sh", "seconds": "%s"}\n' \
    "$1" "$2" "$3"
}

name="tier-usual.sh <tier>: the usual is the median of that tier's last 10 test-run events' seconds"
problems=()
work="$(mktemp -d)"
mkdir -p "$work/.tdd"
{
  ev test-run fast 100
  ev test-run fast 200
  ev test-run fast 7
  ev test-run fast 3
  ev test-run all 900
  ev test-run fast 10
  ev test-run fast 1
  ev leaf-exit fast 900
  ev test-run fast 9
  ev test-run fast 5
  ev test-run fast 2
  ev test-run fast 8
  ev test-run fast 4
  ev test-run fast 6
} > "$work/.tdd/events.jsonl"

out="$( cd "$work" && "$USUAL" fast 2>/dev/null )" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want tier-usual.sh to exit 0, it exited $code")

[[ "$out" == 5.5 ]] ||
  problems+=("usual for tier fast: want 5.5, got $(printf '%q' "$out")")

rm -rf "$work"
report "$name"

finish
