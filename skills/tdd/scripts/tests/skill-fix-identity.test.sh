#!/usr/bin/env bash
# Unit tests for where the /tdd-fix skill ships, what it calls itself, and what it asks the
# user for, read from its skill directory and SKILL.md as text.
#
# Contract under test:
#   skills/tdd-fix/ is a directory, skills/tdd-fix/SKILL.md's frontmatter reads
#   `name: tdd-fix`, and its body says the description argument is optional, that it asks
#   only for what that line did not answer, and that it does so in one short round.
#
# Run: scripts/tests/skill-fix-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd-fix"
want_name="tdd-fix"
skill_md="$skill_dir/SKILL.md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/frontmatter-name.sh"

have_skill_md() {
  [[ -f "$ROOT/$skill_md" ]] && return 0
  problems+=("want a SKILL.md at $skill_md, found none")
  return 1
}

fold_prose() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

body_text() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { inside = 0; body = 1; next }
       body { print }' "$1" | fold_prose
}

issue_body_template() {
  awk '
    /^[[:space:]]*```/ {
      if (inside) { if (found) { printf "%s", buf; exit } ; inside = 0; next }
      inside = 1; buf = ""; found = 0; next
    }
    inside {
      buf = buf $0 "\n"
      if ($0 ~ /^##[[:space:]]+What happened[[:space:]]*$/) found = 1
    }
  ' "$1"
}

criteria_block() {
  awk '/^##[[:space:]]+Acceptance criteria[[:space:]]*$/ { seen = 1; next }
       seen && /^##[^#]/ { exit }
       seen { print }' <<<"$1" | fold_prose
}

have_body() {
  text="$(body_text "$ROOT/$skill_md")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no body after its frontmatter — the $1 could not be read")
  return 1
}

have_template() {
  template="$(issue_body_template "$ROOT/$skill_md")"
  [[ -n "$template" ]] && return 0
  problems+=("$skill_md quotes no issue body: no fenced block in it holds a '## What happened' line")
  return 1
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}


finish
