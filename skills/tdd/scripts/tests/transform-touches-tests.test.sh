#!/usr/bin/env bash
# Unit tests for scripts/transform-touches-tests.sh — rejects a refactor-kind transform whose
# commits change a test file.
#
# Contract under test:
#   transform-touches-tests.sh <base-sha>, run inside the repository
#       → exit 1, naming the test file, when any commit in <base-sha>..HEAD changes one
#       → exit 0 when none does
#
# Run: scripts/tests/transform-touches-tests.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOUCHES="$HERE/../transform-touches-tests.sh"
source "$HERE/lib/harness.sh"

finish
