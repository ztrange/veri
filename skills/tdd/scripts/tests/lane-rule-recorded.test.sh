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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document under test. Absolute only: nothing prints this path — a failure names the
# section, since there is one CLAUDE.md and its location is not the thing in doubt.
CLAUDE_MD="$ROOT/CLAUDE.md"

# The two headings, exactly as the document spells them, so a failure can say which section
# was not there rather than reporting every fact missing from a section that was renamed.
TRAP_HEADING='## The one trap'
IDIOM_HEADING='## Testing idiom'

# Prose naming the other lane, as an ERE — the lane itself, a run in it, or the merge that
# ends one. Both probes below ask for it, because both facts are the same claim about where
# this work belongs seen from two sections, and written out twice the two lists drifted into
# different orders while asking the identical question. Named once so the next fact that has
# to name the lane asks it the same way, and so a wording this repository starts using is
# added in one place rather than in whichever probe noticed first.
DOCS_LANE='docs[ -]lane|documentation lane|docs issue|docs merge'

pass=0 fail=0

# report and plain: the helpers the *-recorded.test.sh suites share (issue #225). This
# suite's `says` asks a different question and stays below, defined after the source.
# shellcheck source=record-helpers.sh
source "$HERE/record-helpers.sh"

# section <heading> — that section of the document as one line: from the heading to the next
# `## `, normalised through `plain` and with its line breaks turned into spaces. Read by
# heading rather than by matching the whole document because each fact below has a place it
# belongs — a sentence about the lane three sections up in the command table would answer
# for prose the section an agent is actually reading does not have. Joined onto one line
# because CLAUDE.md wraps mid-sentence, and a claim split over a line break has to still
# read as one sentence.
section() {
  awk -v heading="$1" '$0 == heading { f = 1; next } f && /^## / { exit } f' "$CLAUDE_MD" |
    plain | tr '\n' ' '
}

# need_section <heading> — that section of the document into the globals `section_heading` and
# `section_text`, or one problem naming the heading and a non-zero return. The reader and the
# fail-closed check are one step because they are one question: a caller that computed the text
# itself could pass one section's prose under another's heading and every failure below would
# name the wrong repair. Globals rather than a return value because bash has no way to hand back
# a string, and the two prose suites this one follows — count-line-guard.test.sh,
# skill-suite-runs.test.sh — both park the section under test in one for exactly that reason.
#
# The `section_` prefix is the whole of what marks those two as one pair written here and read
# in `says`: a global is in scope everywhere, so the name is the only place that can say which
# function fills it and that the heading is the one the text was read from rather than any of
# the other headings this file holds.
#
# Fail closed: an empty string matches no regex, so every fact asked of a section that is not
# there would be reported missing — true, but it names three edits when the repair is that a
# heading moved.
section_heading="" section_text=""
need_section() {
  section_heading="$1"
  section_text="$(section "$section_heading")"
  [[ -n "${section_text// /}" ]] && return 0
  problems+=("CLAUDE.md has no '$section_heading' section to read, so nothing states the lane rule where the agent reading that section would find it")
  return 1
}

# says <fact> <regex>... — one fact the section `need_section` last read has to carry, written
# as the regexes any wording carrying it would match: all of them have to match, and one problem
# naming the section and the fact is appended if any does not. The section is named from
# `$section_heading`, since a failure has to say which of the two is the one missing the
# sentence.
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

# probe_trap_records_whose_work_the_page_is — the half of the rule that lives where the
# contradiction is. This is the section that tells an agent which file to edit to change the
# page and then to run the target that rebuilds it, so this is the section that has to say
# whose work that is: the documentation lane's, and never a development run's. Three regexes
# — the lane, who is being refused, and the refusal — because prose that named the lane
# without saying a development run does not do it would read as a note about where the files
# live rather than as the rule.
probe_trap_records_whose_work_the_page_is() {
  need_section "$TRAP_HEADING" || return

  says "that the page and its inputs are the other lane's work, and that a development run never runs the target that rebuilds them" \
    "$DOCS_LANE" \
    'develop|leaf|veri run|tdd run' \
    'never|refus|exit 2'
}

# probe_idiom_records_the_rule_and_the_checks — the section an author writing a suite in this
# directory reads, and the two facts it owes them: the rule, and the answer to the "then
# nobody would notice" the rule invites. One probe rather than two, because a probe is the
# unit that reads a section and then asks of it — the shape count-line-guard.test.sh's
# probe_idiom_records_the_check uses, where two facts also hang off one read.
probe_idiom_records_the_rule_and_the_checks() {
  need_section "$IDIOM_HEADING" || return

  # `no-docs-reads` by name, because the address is what the rule is worth: an author whose
  # suite is refused has to be able to find the case that refused it, and that name is also
  # the only part of this fact the section does not already contain in some other sentence.
  says "that a suite here never reads a path in the generated tree, nor which case says so by name" \
    'never|must not|does not|no suite' \
    'read|open|reach' \
    'no-docs-reads'

  # The half that keeps the rule from reading as a gap in the coverage: prose is allowed to
  # lag behind code, and what catches the lag is docs-owed.sh's report and docs-fresh's
  # failure at a documentation merge. Both names, and the lane they run in, because the
  # answer to "then nobody would notice" is those two commands and the merge they run at.
  says "where the checks that catch prose lagging behind code live instead — docs-owed.sh, and docs-fresh at a documentation merge" \
    'docs-owed' \
    'docs-fresh' \
    "$DOCS_LANE"
}

# 1. One criterion, one case: the document records the rule, and where the checks it moves
#    out of the development lane went. One case rather than three, because what the next
#    agent needs is not three sentences but a document that does not contradict the guards
#    — a partial record is the same failure, and the problem lines say which sentence is
#    missing from which section.
name="CLAUDE.md states the lane rule in both sections an agent reads: the page is the other lane's work and a development run never runs a docs target, a suite here never reads the generated tree, and docs-owed.sh and docs-fresh are what catch prose lag"
problems=()

probe_trap_records_whose_work_the_page_is
probe_idiom_records_the_rule_and_the_checks

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
