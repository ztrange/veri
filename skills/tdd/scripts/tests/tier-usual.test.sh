#!/usr/bin/env bash
# Unit tests for scripts/tier-usual.sh — what one tier's test-command run usually costs,
# computed from the `test-run` lines timed-test-run.sh writes.
#
# Contract under test:
#   tier-usual.sh <tier>  → exit 0, and on stdout the median of the `seconds` on the last 10
#                           `test-run` lines of `.tdd/events.jsonl` whose `tier` is <tier>.
#   the log               → `.tdd/events.jsonl`, read relative to the directory the script
#                           runs in.
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
work="$(scratch_dir)"
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
