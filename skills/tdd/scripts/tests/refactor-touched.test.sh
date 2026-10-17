#!/usr/bin/env bash
# Unit tests for scripts/refactor-touched.sh — prints the files a step's green commit
# touched, as the bounds of that step's refactor.
#
# Contract under test:
#   refactor-touched.sh <commit>, run inside the repository
#                       → exit 0, and the commit's touched files in `git diff --name-only`
#                         order, comma- or newline-separated, with `.tdd/issue-<n>.md` left out.
#
# Run: scripts/tests/refactor-touched.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOUCHED="$HERE/../refactor-touched.sh"
source "$HERE/lib/harness.sh"

finish
