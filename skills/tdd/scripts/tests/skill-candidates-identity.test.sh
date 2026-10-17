#!/usr/bin/env bash
# Unit tests for where the /tdd-candidates skill ships, what it calls itself, and what it says
# its job is, read from its skill directory and SKILL.md as text.
#
# Contract under test:
#   skills/tdd-candidates/ is a directory, skills/tdd-candidates/SKILL.md's frontmatter reads
#   `name: tdd-candidates`, and its body says it shapes and files candidates, and that it does
#   not survey, rank or judge them.
#
# Run: scripts/tests/skill-candidates-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd-candidates"
want_name="tdd-candidates"
skill_md="$skill_dir/SKILL.md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/frontmatter-name.sh"

body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

not_filed='(not|never|nothing)[^.]{0,20}files?'

paged_lookup='gh api --paginate[^.]{0,80}/issues'

says_near() {
  says "$1[^.]{0,$3}$2|$2[^.]{0,$3}$1" "$4"
}

has_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
}

text=""
[[ -f "$ROOT/$skill_md" ]] && text="$(body_text "$ROOT/$skill_md")"

finish
