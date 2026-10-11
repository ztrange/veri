#!/usr/bin/env bash
# Unit tests for scripts/detach-leaf.sh — runs its argv as a new session leader and returns
# at once.
#
# Contract under test:
#   Every case moved to tests/py/test_detach_leaf.py; this suite holds none.
#
# Run: scripts/tests/detach-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

finish
