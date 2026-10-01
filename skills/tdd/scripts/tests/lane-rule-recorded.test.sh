#!/usr/bin/env bash
# Unit tests for CLAUDE.md's record of the two test lanes — which lane owes a generated-page
# check and which lane never runs one.
#
# Contract under test:
#   CLAUDE.md's "The one trap" section says that the page and its inputs are the
#   documentation lane's work and that a development run never runs the target that rebuilds
#   them; and its "Testing idiom" section says both that a suite here never reads a path in
#   the generated tree — naming no-docs-reads.test.sh — and where the checks that catch
#   prose lag live instead: docs-owed.sh, and docs-fresh at a documentation merge.
#
# Run: skills/tdd/scripts/tests/lane-rule-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

CLAUDE_MD="$ROOT/CLAUDE.md"

TRAP_HEADING='## The one trap'
IDIOM_HEADING='## Testing idiom'

DOCS_LANE='docs[ -]lane|documentation lane|docs issue|docs merge'

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"

section() {
  awk -v heading="$1" '$0 == heading { f = 1; next } f && /^## / { exit } f' "$CLAUDE_MD" |
    plain | tr '\n' ' '
}

section_heading="" section_text=""
need_section() {
  section_heading="$1"
  section_text="$(section "$section_heading")"
  [[ -n "${section_text// /}" ]] && return 0
  problems+=("CLAUDE.md has no '$section_heading' section to read, so nothing states the lane rule where the agent reading that section would find it")
  return 1
}

says() {
  local fact="$1" re
  shift
  for re in "$@"; do
    [[ "$section_text" =~ $re ]] || {
      problems+=("CLAUDE.md's '$section_heading' section does not say $fact")
      return
    }
  done
}

probe_trap_records_whose_work_the_page_is() {
  need_section "$TRAP_HEADING" || return

  says "that the page and its inputs are the other lane's work, and that a development run never runs the target that rebuilds them" \
    "$DOCS_LANE" \
    'develop|leaf|veri run|tdd run' \
    'never|refus|exit 2'
}

probe_idiom_records_the_rule_and_the_checks() {
  need_section "$IDIOM_HEADING" || return

  says "that a suite here never reads a path in the generated tree, nor which case says so by name" \
    'never|must not|does not|no suite' \
    'read|open|reach' \
    'no-docs-reads'

  says "where the checks that catch prose lagging behind code live instead — docs-owed.sh, and docs-fresh at a documentation merge" \
    'docs-owed' \
    'docs-fresh' \
    "$DOCS_LANE"
}

name="CLAUDE.md states the lane rule in both sections an agent reads: the page is the other lane's work and a development run never runs a docs target, a suite here never reads the generated tree, and docs-owed.sh and docs-fresh are what catch prose lag"
problems=()

probe_trap_records_whose_work_the_page_is
probe_idiom_records_the_rule_and_the_checks

report "$name"

finish
