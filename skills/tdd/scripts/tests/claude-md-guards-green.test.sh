#!/usr/bin/env bash
# Unit test for the four suites that hold CLAUDE.md to what it says:
#
#   claude-md-counts.test.sh     the script and suite counts the document states
#   lane-rule-recorded.test.sh   the two-lane rule in "The one trap"
#   count-line-guard.test.sh     the "Testing idiom" count-line rule
#   docs-targets-refuse.test.sh  the development-run refusal
#
# Contract under test:
#   Each of those four is in the roster `make test` runs, read off `make -n test`. The
#   roster is a glob, so a guard drops out of it by being renamed or moved, and nothing
#   else would notice.
#
#   It does not re-run the four guards: `make test` already runs them, and a guard a
#   CLAUDE.md trim breaks turns that run red with its own `FAIL - …` line, naming itself.
#
# Run: skills/tdd/scripts/tests/claude-md-guards-green.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"

suites_dir="skills/tdd/scripts/tests"

GUARDS=(
  claude-md-counts.test.sh
  lane-rule-recorded.test.sh
  count-line-guard.test.sh
  docs-targets-refuse.test.sh
)


source "$HERE/lib/harness.sh"


finish
