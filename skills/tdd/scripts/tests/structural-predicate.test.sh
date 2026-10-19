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

finish
