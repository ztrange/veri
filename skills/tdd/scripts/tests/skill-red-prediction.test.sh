#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to narrate out of the red
# leaf's prediction, read as text.
#
# Contract under test:
#   SKILL.md's Red phase tells the conductor to put both halves in the `### 🔴 Red` comment
#   — the predicted failure, and whether the observed one matched it. Any wording that
#   carries the two facts passes.
#
# Run: scripts/tests/skill-red-prediction.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


doc_text() {
  awk -v h="$1" -v from="$2" '
    !in_s && index($0, h) == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain --join
}

section() {
  text="$(doc_text "$1" "$2")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

red_section()    { section '#### Red' "$@"; }
revise_section() { section '## Revising on a REJECT' "$@"; }

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

exit_0_or_2='exit(s| code)? 0 (or|\|) 2|0 or 2|\b0\b[^.]*\b2\b'


finish
