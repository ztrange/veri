#!/usr/bin/env bash
# Tests for scripts/run-verdict.sh — every case now runs in-process, in tests/py/test_run_verdict.py.
#
# Run: scripts/tests/run-verdict.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/lib/harness.sh"

finish
