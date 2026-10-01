#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to write on the subject line
# of a bug run's commits and PR, read as text.
#
# Contract under test:
#   SKILL.md's Green section says a bug step's green commit takes a `fix:` subject, and its
#   Draft PR step says a bug run's PR title starts with the `fix:` prefix.
#
# Run: scripts/tests/skill-bug-fix-subject.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain
}

green_heading='#### Green'
pr_heading='### 4. Draft PR'

# hazard: BSD grep refuses an interval bound over 255.
window() {
  head -1 < <(grep -oE ".{0,250}$2.{0,250}" <<<"$1")
}

probe_fix_line() {
  local heading="$1" unestablished="$2" absent="$3" unqualified="$4" text
  text="$(section "$heading")"
  if [[ -z "${text// /}" ]]; then
    problems+=("$skill_md has no '$heading' section to read — $unestablished")
  elif ! grep -qE 'fix:' <<<"$text"; then
    problems+=("$absent")
  else
    grep -qE 'bug' <<<"$(window "$text" 'fix:')" || problems+=("$unqualified")
  fi
}

name="$skill_md gives a bug step's green commit a fix: subject and a bug run's PR title a fix: prefix"
problems=()

probe_fix_line "$green_heading" \
  "what subject a bug step's green commit takes could not be established" \
  "$skill_md's '$green_heading' section never names a fix: subject, so a bug step's green commit lands as feat: and the capability index reads a repaired regression as a new capability" \
  "$skill_md's '$green_heading' section names a fix: subject without saying it is a bug step's, so the conductor is given a second subject line and nothing that says which steps take it"

probe_fix_line "$pr_heading" \
  "what prefix a bug run's PR title takes could not be established" \
  "$skill_md's '$pr_heading' section never names the fix: prefix, so a bug run opens a PR whose title announces a capability the run did not add" \
  "$skill_md's '$pr_heading' section names the fix: prefix without saying it is a bug run's, so the conductor cannot tell which runs title their PR that way"

report "$name"

finish
