#!/usr/bin/env bash
# Unit tests for CLAUDE.md's record of the two test lanes — which lane owes a generated-page
# check and which lane never runs one. Like count-line-guard.test.sh case 5 and
# skill-suite-runs.test.sh this suite's subject is a root document rather than a script:
# what the next agent is told before any guard fires. Zero-dependency plain-shell asserts,
# same idiom as count-line-guard.test.sh.
#
# Why this exists (issue #143): every other half of the lane rule is enforced by something
# that fires — no-docs-reads.test.sh refuses a suite that names a path in the generated
# tree, the Makefile's docs targets exit 2 when `VERI_TEST_CMD` says a development run is
# what typed them, and SKILL.md's launch lines are what put that variable in every leaf's
# environment. None of those is what an agent reads first. CLAUDE.md is, and as it stands it
# says the opposite: "The one trap" sends any agent that touched the page to `make docs`,
# which is now the one command that answers with exit 2, and "Testing idiom" says where a
# docs suite lives without saying that a development suite never opens that tree at all. An
# agent that follows the document and is refused by the guard has been handed a
# contradiction it cannot resolve from either side — it reads as a broken Makefile, and the
# cheapest way out of it is to delete the guard.
#
# Contract under test:
#   CLAUDE.md's "The one trap" section says that the page and its inputs are the
#   documentation lane's work and that a development run never runs the target that rebuilds
#   them; and its "Testing idiom" section says both that a suite here never reads a path in
#   the generated tree — naming no-docs-reads.test.sh, the case that says so — and where the
#   checks that catch prose lag live instead: docs-owed.sh, and docs-fresh at a
#   documentation merge.
#
# Both sections, because the document is read in pieces: an author writing a suite reads the
# testing section and an agent that touched the page reads the trap, and a rule recorded in
# only one of them is absent from the place half the offenders are standing. The regen recipe
# under "Versions are tags, and nothing else" is not asked about here: it types `make docs`
# like any other caller, so it is the trap's sentence about the target that covers it, and a
# third section named in this case would be pinning the document's layout rather than the
# rule.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings: what a section has to record is the claim, and how it is phrased belongs to
# whoever writes it — the protocol count-line-guard.test.sh and suite-lanes.test.sh both use
# on this same document.
#
# No line of code below names a path in the generated tree, which is the rule this case
# exists to see recorded: the document is read at the repository root, and the checks it has
# to name — docs-owed.sh, docs-fresh — are named without one.
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
