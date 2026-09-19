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

# ev <event> <tier> <seconds> — one log line in the shape event.sh writes: the eight fixed
# keys first, the payload after. Only `event`, `tier` and `seconds` vary between the lines
# below, because only those three decide which lines the answer is computed from.
ev() {
  printf '{"ts": 1700000000, "issue": "342", "actor": "developer", "phase": "green", "step": "1", "event": "%s", "attempt": "1", "skill_commit": "abc1234", "tier": "%s", "suites": "one.test.sh", "seconds": "%s"}\n' \
    "$1" "$2" "$3"
}

# 1. The whole of this step's criterion, as one case. The fixture holds, for tier `fast`,
#    twelve `test-run` lines: two old ones at 100 s and 200 s, then ten at 1–10 s in a
#    shuffled order. The answer is the median of the LAST TEN only — sorted, that is
#    1…10, whose two middle values are 5 and 6, so 5.5 — and each of the three ways the
#    answer could be got wrong changes it:
#      · counting all twelve would make it 6.5, so the window is pinned;
#      · reading the lines in file order rather than by value would make it 9.5 (the two
#        middle of `7 3 10 1 9 5 2 8 4 6`), so the sort is pinned;
#      · a median defined as one of the two middles would be 5 or 6, so the even-count
#        rule — the mean of the two — is pinned.
#    Two lines that must NOT count are mixed in: a `test-run` for another tier and a
#    non-`test-run` event of this tier, both at 900 s, either of which would drag the
#    answer well off 5.5 if it were counted.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
