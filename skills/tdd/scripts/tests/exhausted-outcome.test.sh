#!/usr/bin/env bash
# Unit tests for scripts/exhausted-outcome.sh — reads the report of the leaf sent when a
# step's revise budget ran out, and says which of the three outcomes that report holds.
#
# Contract under test:
#   stdin  = the exhausted leaf's full raw output (free-form reasoning + its report lines)
#   stdout = the SPLIT: criteria, one per line · or the needs-user answer · or nothing
#   exit   = 0 split · 1 needs the user · 3 neither (nothing to do, not an error)
#
# Run: scripts/tests/exhausted-outcome.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUTCOME="$HERE/../exhausted-outcome.sh"
source "$HERE/lib/harness.sh"

out="" code=0
run() { out="$(printf '%s' "$1" | "$OUTCOME")" && code=0 || code=$?; }

finish
