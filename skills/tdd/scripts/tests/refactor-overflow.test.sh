#!/usr/bin/env bash
# Tests for scripts/refactor-overflow.sh — files the structural candidates a run's closing
# pass could not reach as one issue naming the parent issue. Driven against a stub `gh` on PATH.
#
# Contract under test:
#   refactor-overflow.sh <n> <owed-file> <reached>
#
# Run: scripts/tests/refactor-overflow.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

finish
