#!/usr/bin/env bash
# Tests for scripts/stop-requested.sh — the read half of the stop mechanism (#386): an
# operator writes a mode into .tdd/stop and a running conductor asks this script, at its
# checkpoints, whether one is waiting. Run from the run's worktree, it reads .tdd/stop
# relative to it, the way event.sh and supervise.sh spell their own paths.
#
# Fast tier (#336): no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/stop-requested.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STOP="$HERE/../../stop-requested.sh"
pass=0 fail=0

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# run_stop — run the script from the run's worktree, leaving its stdout in `out`, its exit
# code in `code` and its stderr in `err`. Most cases assert on `out` and `code` alone,
# since what a conductor at a checkpoint captures is stdout; the malformed ones read `err`
# too, because "nothing on stdout" and "a diagnostic somewhere" are together what keeps a
# conductor from reading a complaint as a mode.
run_stop() {
  out="$(cd "$work" && "$STOP" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Same
# accounting idiom as red-divergence.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

# 1. each of the three modes a stop request may name comes back on stdout, exit 0 — one
#    case over the three because they are one behaviour: the mode is passed through, not
#    interpreted, and a conductor branches on the word it reads.
problems=""
for mode in at-ledger at-leaf now; do
  printf '%s\n' "$mode" > "$work/.tdd/stop"
  run_stop
  if [[ "$code" != 0 || "$out" != "$mode" ]]; then
    problems+="    $mode: want exit 0 and stdout '$mode', got exit $code and stdout '$out'"$'\n'
  fi
done
verdict "a stop request's mode comes back on stdout, exit 0"

# 2. no stop request at all: nothing on stdout, exit 3 — "nothing to do", not an error, so
#    a conductor's checkpoint tells a missing file apart from a malformed one.
rm -f "$work/.tdd/stop"
run_stop
problems=""
if [[ "$code" != 3 || -n "$out" ]]; then
  problems="    want exit 3 and empty stdout, got exit $code and stdout '$out'"$'\n'
fi
verdict "no stop request: nothing on stdout, exit 3"

# 3. a malformed stop request — a first line that is not one of the three modes, and an
#    empty one — is no answer at all: nothing on stdout, a diagnostic on stderr, exit 2.
#    One case over the three fixtures because they are one behaviour: whatever a conductor
#    capturing stdout reads, it must never be a diagnostic wearing a mode's place. The
#    third fixture is a zero-byte file rather than a bare newline: its first line is empty
#    the same way, but the read that takes it hits end-of-file, so a script that lets that
#    read decide its fate exits on the read's own status with nothing said.
#
# check_malformed <what the fixture already written is> — run the script over it and add a
# line to `problems` unless all three halves hold at once. One function over the three
# fixtures because what is demanded of them is the same; only the fixture differs.
check_malformed() {
  run_stop
  if [[ "$code" != 2 || -n "$out" || -z "$err" ]]; then
    problems+="    $1: want exit 2, empty stdout and a diagnostic on stderr, got exit $code, stdout '$out' and stderr '$err'"$'\n'
  fi
}
problems=""
for line in "bogus" ""; do
  printf '%s\n' "$line" > "$work/.tdd/stop"
  check_malformed "first line '$line'"
done
: > "$work/.tdd/stop"
check_malformed "a zero-byte file"
verdict "a malformed stop request: nothing on stdout, a diagnostic on stderr, exit 2"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
