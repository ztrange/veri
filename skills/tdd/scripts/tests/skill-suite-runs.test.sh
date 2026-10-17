#!/usr/bin/env bash
# Unit test for what skills/tdd/SKILL.md and this repository's CLAUDE.md say about which
# leaves run the full test suite, read as text.
#
# Contract under test:
#   SKILL.md's Red phase says its leaf runs the suite holding the new case; its Refactor
#   loop says the transform leaf runs the suites covering the touched files.
#   CLAUDE.md names which leaves run the full suite, and no longer claims every leaf runs it
#   after every edit.
#
# Run: scripts/tests/skill-suite-runs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


doc_text() {
  from="$3" awk -v h="$2" '
    BEGIN { from = ENVIRON["from"] }
    !in_s && index($0, h) == 1 { in_s = 1; want = (from == "" ? 1 : 0); next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$1" | plain --join
}

text=""
need_text() {
  text="$(doc_text "$skill_path" "$1" "${2-}")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no '$1' section to read — what that phase's leaf runs could not be established")
  return 1
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

paragraphs() {
  awk 'BEGIN { RS = "" } { gsub(/\n/, " "); print }' "$1" | plain
}

need_idiom() {
  text="$(paragraphs "$claude_path" | grep -E '^a suite whose subject is the docs pipeline')"
  [[ -n "$text" ]] && return 0
  problems+=("$claude_md has no paragraph opening 'a suite whose subject is the docs pipeline' to read")
  return 1
}


finish
