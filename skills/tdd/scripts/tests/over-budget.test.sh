#!/usr/bin/env bash
# Unit tests for scripts/over-budget.sh — the check that turns a recorded test-command run
# into a yes or no.
#
# Contract under test:
#   over-budget.sh <tier> <seconds> <usual>
#       → exit 0 when the run is over budget, exit 1 when it is not, exit 2 with nothing on
#         stdout for a missing argument (stderr: the usage line) or a refused tunable.
#   A unit-tier run is over budget when its seconds exceed VERI_UNIT_BUDGET (default 10);
#   at or under that figure it is not. A run of any tier is over budget when its seconds
#   exceed VERI_TIME_WARN_RATIO (default 1.5) times that tier's usual; at or under that
#   product it is not.
#   An over-budget run also prints exactly one line, carrying the ⏱ the conductor pastes
#   into that phase's narration; a run that is not over budget prints nothing. SKILL.md
#   tells the conductor to paste that line and to branch on nothing.
#
# Run: skills/tdd/scripts/tests/over-budget.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

finish
