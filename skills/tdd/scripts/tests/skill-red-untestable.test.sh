#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md's Red section handles a criterion no lightweight,
# behavior-level test can pin, read as text.
#
# Contract under test:
#   1. SKILL.md's Red section states what a valid test is: behaviour over mechanism (no
#      process/fork count or timing assertion), with the in-process-spy carve-out for a call
#      count the criterion itself names.
#   2. SKILL.md's Red section's verify sub-step branches on `AGAINST_UNMODIFIED: UNTESTABLE`
#      by skipping verify-red and verify-pin and bailing immediately, with cause
#      `untestable-criterion`.
#   3. SKILL.md's Bailing section lists `untestable-criterion` as a **process** failure
#      cause, alongside `revise-exhausted`.
#   4. SKILL.md's Red section's verify sub-step sends a `⟦ci-repair⟧` step reporting `PASSES`
#      on to Green with the CI log as its red evidence, and never to verify-pin or to the
#      `test: pin` tick-and-commit.
#
# Run: scripts/tests/skill-red-untestable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


doc_text() {
  h="$1" from="${2:-}" awk '
    BEGIN { h = ENVIRON["h"]; from = ENVIRON["from"] }
    !in_s && index($0, h) == 1 { in_s = 1; if (from == "") want = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && from != "" && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain --join
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

finish
