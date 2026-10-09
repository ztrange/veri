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

name="tier-usual.sh with no argument: exit 2, nothing on stdout, and the one usage line on stderr"
problems=()
work="$(scratch_dir)"

out="$( cd "$work" && "$USUAL" 2>"$work/err" )" && code=0 || code=$?
err="$(cat "$work/err")"

[[ "$code" == 2 ]] ||
  problems+=("want tier-usual.sh to exit 2, it exited $code")

[[ -z "$out" ]] ||
  problems+=("stdout: want nothing, got $(printf '%q' "$out")")

[[ "$err" == "usage: tier-usual.sh <tier>" ]] ||
  problems+=("stderr: want 'usage: tier-usual.sh <tier>', got $(printf '%q' "$err")")

rm -rf "$work"
report "$name"

name="tier-usual.sh <tier> with no test-run event for that tier: exit 2, nothing on stdout"
problems=()
work="$(scratch_dir)"
mkdir -p "$work/.tdd"
{
  ev test-run all 900
  ev leaf-exit fast 900
} > "$work/.tdd/events.jsonl"

out="$( cd "$work" && "$USUAL" fast 2>/dev/null )" && code=0 || code=$?

[[ "$code" == 2 ]] ||
  problems+=("want tier-usual.sh to exit 2, it exited $code")

[[ -z "$out" ]] ||
  problems+=("stdout: want nothing, got $(printf '%q' "$out")")

rm -rf "$work"
report "$name"

name="tier-usual.sh run through a symlink to the skill directory and from another working directory prints the same stdout and exit code as in place, for a tier with test-run events and for a missing argument"
problems=()
work="$(scratch_dir)"
mkdir -p "$work/here/.tdd" "$work/elsewhere/.tdd"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
LINKED="$work/linked-skill/scripts/tier-usual.sh"
{
  ev test-run fast 3
  ev test-run all 900
  ev test-run fast 1
  ev test-run fast 2
} > "$work/here/.tdd/events.jsonl"
cp "$work/here/.tdd/events.jsonl" "$work/elsewhere/.tdd/events.jsonl"

in_place="$( cd "$work/here" && "$USUAL" fast 2>/dev/null )" && in_place_code=0 || in_place_code=$?
linked="$( cd "$work/elsewhere" && "$LINKED" fast 2>/dev/null )" && linked_code=0 || linked_code=$?

[[ "$in_place" == 2.0 && "$in_place_code" == 0 ]] ||
  problems+=("in place, tier fast: want 2.0 and exit 0, got $(printf '%q' "$in_place") and exit $in_place_code")

[[ "$linked" == "$in_place" && "$linked_code" == "$in_place_code" ]] ||
  problems+=("tier fast: in place $(printf '%q' "$in_place") exit $in_place_code, through the symlink $(printf '%q' "$linked") exit $linked_code")

in_place="$( cd "$work/here" && "$USUAL" 2>/dev/null )" && in_place_code=0 || in_place_code=$?
linked="$( cd "$work/elsewhere" && "$LINKED" 2>/dev/null )" && linked_code=0 || linked_code=$?

[[ -z "$in_place" && "$in_place_code" == 2 ]] ||
  problems+=("in place, no argument: want nothing and exit 2, got $(printf '%q' "$in_place") and exit $in_place_code")

[[ "$linked" == "$in_place" && "$linked_code" == "$in_place_code" ]] ||
  problems+=("no argument: in place $(printf '%q' "$in_place") exit $in_place_code, through the symlink $(printf '%q' "$linked") exit $linked_code")

rm -rf "$work"
report "$name"

finish
