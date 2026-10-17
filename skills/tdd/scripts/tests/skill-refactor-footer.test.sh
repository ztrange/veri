#!/usr/bin/env bash
# Unit test for skills/tdd/SKILL.md's account of the refactor leaf's report footer, held
# against the report lines the built refactor prompt asks for.
#
# Contract under test — one criterion:
#   1. The Refactor section's account of the leaf's report footer names exactly the report
#      lines the built refactor prompt asks for — no line the prompt does not emit, none it
#      emits left out.
#
# Run: scripts/tests/skill-refactor-footer.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

refactor_heading='#### Refactor'

refactor_lines() {
  awk -v h="$refactor_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path"
}

unreadable_problem() {
  printf "%s has no '%s' section to read — %s" "$skill_md" "$refactor_heading" "$1"
}


finish
