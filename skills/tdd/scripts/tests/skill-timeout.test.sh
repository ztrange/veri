#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a conductor to do with the run's hard
# timeout, read as text.
#
# Contract under test:
#   SKILL.md's preflight section times the green-baseline run it already does, hands that
#   measurement to `leaf-timeout.sh`, and exports the result as `VERI_TIMEOUT` so every
#   leaf of the run is launched under it.
#   SKILL.md's plan-comment step says that comment states the timeout and the baseline it
#   was derived from.
#
# Run: scripts/tests/skill-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"


source "$HERE/lib/harness.sh"


finish
