#!/usr/bin/env bash
# Tests for scripts/stop-requested.sh — the read half of the stop mechanism: an operator
# writes a mode into .tdd/stop and a running conductor asks this script, at its checkpoints,
# whether one is waiting. Run from the run's worktree, it reads .tdd/stop relative to it.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/stop-requested.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STOP="$HERE/../../stop-requested.sh"
source "$HERE/../lib/harness.sh"

work="$(scratch_dir)"
mkdir -p "$work/.tdd"

run_stop() {
  out="$(cd "$work" && "$STOP" "$@" 2>"$work/stderr")" && code=0 || code=$?
  err="$(cat "$work/stderr")"
}

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
}

problems=""
for mode in at-ledger at-leaf now; do
  printf '%s\n' "$mode" > "$work/.tdd/stop"
  run_stop
  if [[ "$code" != 0 || "$out" != "$mode" ]]; then
    problems+="    $mode: want exit 0 and stdout '$mode', got exit $code and stdout '$out'"$'\n'
  fi
done
verdict "a stop request's mode comes back on stdout, exit 0"

rm -f "$work/.tdd/stop"
run_stop
problems=""
if [[ "$code" != 3 || -n "$out" ]]; then
  problems="    want exit 3 and empty stdout, got exit $code and stdout '$out'"$'\n'
fi
verdict "no stop request: nothing on stdout, exit 3"

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

problems=""
run_stop --bogus
want="usage: stop-requested.sh [--clear]"
if [[ "$code" != 2 || -n "$out" || "$err" != "$want" ]]; then
  problems+="    --bogus: want exit 2, empty stdout and stderr '$want', got exit $code, stdout '$out' and stderr '$err'"$'\n'
fi
verdict "--bogus exits 2 with exactly the usage line on stderr and nothing on stdout"

problems=""
printf '%s\n' "bogus" > "$work/.tdd/stop"
run_stop
want="stop-requested: .tdd/stop must name a mode — at-ledger, at-leaf or now: 'bogus'"
if [[ "$code" != 2 || -n "$out" || "$err" != "$want" ]]; then
  problems+="    bogus: want exit 2, empty stdout and stderr '$want', got exit $code, stdout '$out' and stderr '$err'"$'\n'
fi
rm -f "$work/.tdd/stop"
verdict "a malformed stop request is refused on stderr with today's message, naming the modes"

problems=""
home="$work/home"; run="$work/run"
mkdir -p "$home/.tdd" "$run/.tdd"
ln -s "$(cd "$HERE/../.." && pwd)" "$home/scripts"
printf '%s\n' "at-leaf" > "$home/.tdd/stop"
printf '%s\n' "now" > "$run/.tdd/stop"
out="$(cd "$run" && "$home/scripts/stop-requested.sh" 2>"$work/stderr")" && code=0 || code=$?
if [[ "$code" != 0 || "$out" != "now" ]]; then
  problems+="    read: want exit 0 and stdout 'now', got exit $code and stdout '$out'"$'\n'
fi
out="$(cd "$run" && "$home/scripts/stop-requested.sh" --clear 2>"$work/stderr")" && code=0 || code=$?
if [[ "$code" != 0 || -e "$run/.tdd/stop" ]]; then
  exists="gone"; [[ -e "$run/.tdd/stop" ]] && exists="still there"
  problems+="    --clear: want exit 0 and the working directory's .tdd/stop gone, got exit $code and the file $exists"$'\n'
fi
beside="$(cat "$home/.tdd/stop" 2>/dev/null || echo "<gone>")"
if [[ "$beside" != "at-leaf" ]]; then
  problems+="    the .tdd/stop beside the skill: want it still 'at-leaf', got '$beside'"$'\n'
fi
verdict "run through a symlink to the scripts directory, stop-requested.sh reads and clears the working directory's .tdd/stop, never one beside the skill"

problems=""
tier_dir="skills/tdd/scripts/tests/unit"
self="$HERE/$(basename "$0")"
case "$HERE" in
  */"$tier_dir") ;;
  *) problems+="    want this suite under $tier_dir/, found it in $HERE"$'\n' ;;
esac
header="$(sed -n '2,$p' "$self" | sed '/^#/!q' | grep '^#')"
for phrase in "fast tier" "no git" "no network" "no server" "no real sleep" "no nested suite"; do
  grep -qi -- "$phrase" <<< "$header" ||
    problems+="    this suite's header does not say '$phrase', so it does not state the bar it clears"$'\n'
done
verdict "this suite lives in the fast tier's directory and its header states the bar it clears"

finish
