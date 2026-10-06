#!/usr/bin/env bash
# Unit tests for the partials under scripts/prompts/ — where each {{INCLUDE:<file>}} token
# sits in the template or partial that names it.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/prompt-partials.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPTS="$HERE/../../prompts"
source "$HERE/../lib/harness.sh"

opens_cleanly() {
  local prior="$1" line trimmed
  line="${prior##*$'\n'}"
  [[ "$line" =~ ^[[:space:]]*([0-9]+\.|[-*])[[:space:]]+$ ]] && return 0
  trimmed="${prior%"${prior##*[![:space:]]}"}"
  [[ -z "$trimmed" ]] && return 0
  [[ "${prior:${#trimmed}}" == *$'\n'*$'\n'* ]] && return 0
  [[ "$trimmed" =~ [.!?](\*\*|\)|\")?$ ]]
}

name="#1014 every {{INCLUDE:<file>}} under prompts/ opens its partial at a sentence's start: after a sentence's end, a blank line, a list marker or the file's start"
problems=()
include_re='\{\{INCLUDE:[^}]*\}\}'
for tpl in "$PROMPTS"/*.md; do
  rest="$(<"$tpl")"
  before=""
  while [[ "$rest" =~ $include_re ]]; do
    token="${BASH_REMATCH[0]}"
    before+="${rest%%"$token"*}"
    rest="${rest#*"$token"}"
    if ! opens_cleanly "$before"; then
      newlines="${before//[!$'\n']/}"
      problems+=("${tpl##*/}:$(( ${#newlines} + 1 )) $token after: ${before##*$'\n'}")
    fi
    before+="$token"
  done
done
report "$name"

closes_cleanly() {
  local text="$1" trimmed line
  trimmed="${text%"${text##*[![:space:]]}"}"
  [[ -z "$trimmed" ]] && return 0
  line="${trimmed##*$'\n'}"
  [[ "$line" =~ ^[[:space:]]*(#|\`\`\`) ]] && return 0
  [[ "$line" =~ ^(    |$'\t') ]] && return 0
  [[ "$line" =~ ^[A-Z_]+:\  ]] && return 0
  [[ "$line" =~ ^\{\{[A-Z_]+\}\}$ ]] && return 0
  [[ "$trimmed" =~ [.!?](\*\*|\)|\")?$ ]]
}

name="#1014 every _*.md partial under prompts/ closes at a sentence's end: after a sentence's end, a heading, a report line, a code block or a lone placeholder"
problems=()
for partial in "$PROMPTS"/_*.md; do
  text="$(<"$partial")"
  if ! closes_cleanly "$text"; then
    problems+=("${partial##*/} ends: ${text##*$'\n'}")
  fi
done
report "$name"

finish
