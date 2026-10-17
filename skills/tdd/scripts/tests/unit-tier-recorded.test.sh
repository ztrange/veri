#!/usr/bin/env bash
# Unit tests for CLAUDE.md's record of the fast test tier — which directory it is, and what
# a suite has to be to live there.
#
# Contract under test:
#   CLAUDE.md's "Testing idiom" section names skills/tdd/scripts/tests/unit/ as the fast
#   tier, and states the admission bar in one passage: about 100 ms per case, and no git,
#   network, servers, real waits or nested suites. Each fact is asked as a regex, not a
#   fixed string.
#
# Run: skills/tdd/scripts/tests/unit-tier-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
section_name="Testing idiom"

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"

section_records() {
  awk -v want="## $section_name" '
    $0 == want { inside = 1; next }
    inside && /^## / { exit }
    inside' "$claude_path" | records
}

passage_text=""

read_section() {
  passage_text="$(section_records)"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md has no '## $section_name' section to read")
  return 1
}

says() {
  local fact="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$passage_text"
  problems+=("$claude_md's '$section_name' section does not say $fact")
}

finish
