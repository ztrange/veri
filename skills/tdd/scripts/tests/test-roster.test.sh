#!/usr/bin/env bash
# Unit tests for the roster of `make test`. Like make-test-env.test.sh this suite has no
# script as its subject: its subject is the recipe, read off `make -n`, which expands the
# suite list and runs nothing.
#
# Contract under test:
#   1. `make test` with no TESTS override lists every suite in tests/ and in tests/unit/.
#
# Run: skills/tdd/scripts/tests/test-roster.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

TIERS='skills/tdd/scripts/tests skills/tdd/scripts/tests/unit'

plan="$(make -C "$ROOT" -n test 2>&1 < /dev/null)"

missing=()
for tier in $TIERS; do
  for f in "$ROOT/$tier"/*.test.sh; do
    rel="$tier/${f##*/}"
    [[ " $(printf '%s' "$plan" | tr -s '[:space:];' ' ') " == *" $rel "* ]] || missing+=("$rel")
  done
done

problems=()
[[ "${#missing[@]}" -eq 0 ]] || problems+=("make -n test omits: ${missing[*]}")
report "make test with no TESTS override runs every suite in tests/ and tests/unit/"

finish
