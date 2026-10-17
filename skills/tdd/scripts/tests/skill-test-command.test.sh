#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor about the run's test command,
# read as text.
#
# Contract under test:
#   Preflight reads the issue body and hands it to detect-test-command.sh as `--issue`,
#   in that order, so the issue's own command is in hand before the baseline run.
#   The section that defines <test-cmd> for every leaf detects it the same way.
#   The plan comment states the test command the run will use.
#
# Run: scripts/tests/skill-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

finish
