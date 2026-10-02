#!/usr/bin/env bash
# Unit tests for scripts/lib/candidate-line.sh — the CANDIDATES line's classes, sourced, not
# run. The suite sources the module and calls its functions in-process.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/candidate-line.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/candidate-line.sh"
source "$HERE/../lib/harness.sh"

classify() {
  (
    source "$LIB"
    unset TEST_ONLY_TRANSFORM
    test_only_candidate "$1"
    status=$?
    printf '%s %s' "$status" "${TEST_ONLY_TRANSFORM-<unset>}"
  ) 2>&1
}

problems=()
for pair in \
  'CANDIDATES: test-only | fold the two fixtures into one|0 fold the two fixtures into one' \
  'CANDIDATES: structural | extract the parser|1 <unset>' \
  'CANDIDATES: cosmetic | rename x to count|1 <unset>' \
  'CANDIDATES: none|1 <unset>'; do
  line="${pair%|*}"
  want="${pair##*|}"
  got="$(classify "$line")"
  [[ "$got" == "$want" ]] || problems+=("'$line': want '$want', got '$got'")
done
report "test_only_candidate takes a test-only line and its transform, and refuses structural, cosmetic and none (#683)"

finish
