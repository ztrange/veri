#!/usr/bin/env bash
# Unit tests for scripts/veri/blocked_by.py — the one reading of an issue body's `## Blocked by`
# section.
#
# Contract under test:
#   veri/blocked_by.py  blockers(<body>, <repo slug>) → the issue numbers named under
#                       `## Blocked by`, as `#<n>` or as https://github.com/<slug>/issues/<n>
#
# Run: scripts/tests/blocked-by.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../lib"
VERI="$HERE/../veri"
source "$HERE/lib/harness.sh"


finish
