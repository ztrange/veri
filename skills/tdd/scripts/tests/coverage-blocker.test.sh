#!/usr/bin/env bash
# Tests for scripts/coverage-blocker.sh — files an unlabelled coverage issue for a refactor
# issue Cover answered `COVERED: no`, and names it under the refactor issue's `## Blocked by`.
# Driven against a stub `gh` on PATH.
#
# Contract under test:
#   coverage-blocker.sh <refactor-issue-number>
#   GH_REPO=owner/name coverage-blocker.sh <refactor-issue-number>
#
# Run: scripts/tests/coverage-blocker.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BLOCKER="$HERE/../coverage-blocker.sh"
source "$HERE/lib/harness.sh"

finish
