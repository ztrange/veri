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
source "$HERE/../lib/harness.sh"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/.tdd"

# run_stop [args…] — run the script from the run's worktree with the arguments given,
# leaving its stdout in `out`, its exit code in `code` and its stderr in `err`. Most cases assert on `out` and `code` alone,
# since what a conductor at a checkpoint captures is stdout; the malformed ones read `err`
# too, because "nothing on stdout" and "a diagnostic somewhere" are together what keeps a
# conductor from reading a complaint as a mode.
run_stop() {
  out="$(cd "$work" && "$STOP" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

# verdict <name> — report one case from the `problems` the case just filled: empty is a
# pass, otherwise a FAIL line naming the case and the indented lines it collected. Same
# accounting idiom as red-divergence.test.sh's verdict().
verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
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

# 4. --clear removes the stop request and exits 0, and exits 0 when there was none to
#    remove. One case over the two states because idempotence is the behaviour: both
#    callers — the stop sequence at its end, and the claim at a run's first step — must be
#    able to clear without first asking whether there is anything there.
problems=""
printf '%s\n' "at-ledger" > "$work/.tdd/stop"
run_stop --clear
if [[ "$code" != 0 || -e "$work/.tdd/stop" ]]; then
  exists="gone"; [[ -e "$work/.tdd/stop" ]] && exists="still there"
  problems+="    with a stop request: want exit 0 and .tdd/stop gone, got exit $code and the file $exists"$'\n'
fi
rm -f "$work/.tdd/stop"
run_stop --clear
if [[ "$code" != 0 ]]; then
  problems+="    with no stop request: want exit 0, got exit $code"$'\n'
fi
verdict "--clear removes a stop request and exits 0, with or without one to remove"

# 5. any other argument is not an argument this script takes: exit 2, and .tdd/stop left
#    exactly as it was. The second half is what keeps a typo from acting: an unrecognised
#    word must neither be read as a mode nor clear a request an operator is waiting on.
#
# check_refused <label> [args…] — write a stop request, run the script with the arguments
# given and add a line to `problems` unless it exits 2 and leaves that request untouched.
# One function over both refusal cases because what is demanded of them is the same; only
# the argument list differs.
check_refused() {
  local label="$1"; shift
  printf '%s\n' "at-ledger" > "$work/.tdd/stop"
  run_stop "$@"
  local left; left="$(cat "$work/.tdd/stop" 2>/dev/null || echo "<gone>")"
  if [[ "$code" != 2 || "$left" != "at-ledger" ]]; then
    problems+="    $label: want exit 2 and .tdd/stop still 'at-ledger', got exit $code and '$left'"$'\n'
  fi
}
problems=""
check_refused "--bogus" --bogus
verdict "any other argument exits 2 and leaves .tdd/stop as it was"

# 6. --clear carries no argument of its own, so a word after it is as unrecognised as one
#    in its place: exit 2, and .tdd/stop left exactly as it was. The clearing is what makes
#    this its own case — a script that branches on the first argument alone reads `--clear`
#    and removes the file, so the typo silently throws away a request an operator is
#    waiting on rather than being refused.
problems=""
check_refused "--clear --bogus" --clear --bogus
verdict "--clear with a trailing argument exits 2 and leaves .tdd/stop as it was"

# 7. Where this suite lives and what its header says, asked of the suite itself. The fast
#    tier is a directory — `make unit` globs skills/tdd/scripts/tests/unit/*.test.sh, so a
#    suite runs there by being there, and unit-tier.test.sh case 1 pins that every suite on
#    disk under it is named by the target. What that leaves unasked is the half a human
#    owes: the admission bar is judged by reading a suite's source, so the header has to
#    say which bar it clears, in the words the bar is written in — no git, no network, no
#    servers, no real sleep, no nested suites. A suite whose header only counts its own
#    usage tells the next reader what it does, not what it promises.
problems=""
tier_dir="skills/tdd/scripts/tests/unit"
self="$HERE/$(basename "$0")"
case "$HERE" in
  */"$tier_dir") ;;
  *) problems+="    want this suite under $tier_dir/, found it in $HERE"$'\n' ;;
esac
# The header: the comment lines after the shebang, up to the first line that is not one —
# the same slice unit-tier.test.sh reads a moved suite's usage count from.
header="$(sed -n '2,$p' "$self" | sed '/^#/!q' | grep '^#')"
for phrase in "fast tier" "no git" "no network" "no server" "no real sleep" "no nested suite"; do
  grep -qi -- "$phrase" <<< "$header" ||
    problems+="    this suite's header does not say '$phrase', so it does not state the bar it clears"$'\n'
done
verdict "this suite lives in the fast tier's directory and its header states the bar it clears"

finish
