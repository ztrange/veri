#!/usr/bin/env bash
# Unit tests for `make watch` — a developer convenience that polls the tracked files
# and reruns `make unit` when one changes. Not a suite and not a gate.
#
#   the suite's lane → `make -n test` lists this suite and `make -n unit` does not: each
#                    target's roster read off its own expanded recipe, which runs nothing.
#
# Run: scripts/tests/watch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

source "$HERE/lib/harness.sh"

name="watch.test.sh: run by make test's glob, not by make unit's"
problems=()
roster() { make --no-print-directory -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }
grep -qx 'skills/tdd/scripts/tests/watch.test.sh' < <(roster test) ||
  problems+=("make -n test does not list skills/tdd/scripts/tests/watch.test.sh")
in_unit="$(roster unit | grep '/watch\.test\.sh$')"
[[ -z "$in_unit" ]] || problems+=("make -n unit lists $in_unit; want it absent from the fast tier")
report "$name"

finish
