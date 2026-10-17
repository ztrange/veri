#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md has the conductor run its own long commands: the
# preflight baseline and the full-suite gate go through detach-command.sh, never a bare
# `make test` or detect-test-command.sh --tier command the conductor might background.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Contract under test:
#   Every procedure line that runs `make test`, or names detect-test-command.sh --tier
#   fast|all's command, also names detach-command.sh; one that does not is reported as
#   SKILL.md:<line>.
#
# Run: scripts/tests/skill-detach-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"
finish
