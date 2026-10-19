#!/usr/bin/env bash
# Unit tests for which python3 run-suite.sh runs a tests/py/test_*.py file with when VERI_VENV
# is unset.
#
# Run: skills/tdd/scripts/tests/run-suite-venv.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

finish
