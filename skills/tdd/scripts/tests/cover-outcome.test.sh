#!/usr/bin/env bash
# Unit tests for scripts/cover-outcome.sh — the pure transform that reads a cover leaf's
# report on stdin and says whether the code a refactor step will move is covered, so the
# conductor can go on to Transform or refuse the step.
#
# Contract under test:
#   stdin  = the cover leaf's report (the COVERED:/CAUGHT_BY:/MUTATION: lines at its end)
#   stdout = on COVERED: yes, the test the report's CAUGHT_BY: line names
#   exit   = 0 COVERED: yes · 1 COVERED: no · 2 no readable COVERED: line
#
# Run: scripts/tests/cover-outcome.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
COVER_OUTCOME="$HERE/../cover-outcome.sh"
source "$HERE/lib/harness.sh"

run_on() {
  out="$(printf '%s' "$1" | "$COVER_OUTCOME" 2>/dev/null)" && code=0 || code=$?
}

verdict() {
  local name="$1" p
  if (( ${#problems[@]} )); then
    no "$name"
    for p in "${problems[@]}"; do echo "    $p"; done
  else
    ok
  fi
}

caught_by='widget.test.sh: a stubbed widget stays blue'
mutation='widget.sh: painted the widget red'

finish
