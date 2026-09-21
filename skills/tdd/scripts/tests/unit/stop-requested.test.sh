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

# 1. each of the three modes a stop request may name comes back on stdout, exit 0 — one
#    case over the three because they are one behaviour: the mode is passed through, not
#    interpreted, and a conductor branches on the word it reads.
problems=""
for mode in at-ledger at-leaf now; do
  printf '%s\n' "$mode" > "$work/.tdd/stop"
  out="$(cd "$work" && "$STOP" 2>/dev/null)" && code=0 || code=$?
  if [[ "$code" != 0 || "$out" != "$mode" ]]; then
    problems+="    $mode: want exit 0 and stdout '$mode', got exit $code and stdout '$out'"$'\n'
  fi
done
if [[ -z "$problems" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1)); echo "FAIL - a stop request's mode comes back on stdout, exit 0"
  printf '%s' "$problems"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
