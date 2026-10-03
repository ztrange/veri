#!/usr/bin/env bash
# Tests for scripts/structural-predicate.sh — the check a structural-pass candidate's
# predicate must pass before a transform leaf is launched for it.
#
# Contract under test:
#   structural-predicate.sh <record> reads a predicate leaf's report on stdin and, when its
#   `PREDICATE:` command fails against the current tree, writes that command to <record>.
#
# Run: scripts/tests/structural-predicate.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SP="$HERE/../structural-predicate.sh"

source "$HERE/lib/harness.sh"

name="#691 a PREDICATE: command that fails on the current tree is written to <record>, exit 0"
problems=()
tree="$(scratch_dir)"
record="$tree/predicate"
predicate="test -e lib/shared-opening.md"
code=0
(cd "$tree" && "$SP" "$record" >/dev/null 2>&1 <<REPORT) || code=$?
Read the candidate and the files it names.
PREDICATE: $predicate
REPORT
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from structural-predicate.sh, got $code")
if [[ ! -f "$record" ]]; then
  problems+=("structural-predicate.sh wrote no record at $record")
else
  [[ "$(cat "$record")" == "$predicate" ]] ||
    problems+=("record holds '$(cat "$record")', want the reported command '$predicate'")
fi
report "$name"

finish
