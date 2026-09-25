#!/usr/bin/env bash
# Unit tests for the three root documents' record of the selection order — which band an
# issue is taken in, and the tunable that names the label putting it in the first one. Like
# model-knobs-recorded.test.sh and lane-rule-recorded.test.sh this suite's subject is a
# document rather than a script: what an operator and the next agent are told before any
# issue is selected. Zero-dependency plain-shell asserts, same idiom as
# model-knobs-recorded.test.sh.
#
# Why this exists (issue #113): `solvable-issues.sh` now prints its scope as priority
# first, then `bug`, then the rest, each band ascending — and the whole steering mechanism
# the band buys is `gh issue edit <n> --add-label priority` typed from a shell or a phone.
# An operator who cannot find the label's name, or who reads three documents still saying
# the order is plain ascending, has a knob that exists and a record that denies it. The two
# places the order is stated are CONTEXT.md's *Selection layer* and *Solvable* entries —
# the glossary every other document defers to — and SKILL.md's `solvable-issues.sh` bullet,
# which is where the script's own contract and its `VERI_GH_JSON` tunable already live.
# CLAUDE.md is the first thing an agent reads.
#
# And the sentence that stops the band being read as a fifth condition is not decoration:
# priority reorders the solvable set, it never enlarges it. The four conditions run first
# and the sort runs on what survives, so a priority issue that is blocked, claimed or not
# opted in is still not printed. A document naming the label without that sentence invites
# exactly the change the spec calls the case most likely to be got wrong — a label that
# opts an issue in by accident.
#
# Contract under test:
#   CONTEXT.md's *Selection layer* entry states the three-band order — priority, then bug,
#   then the rest, ascending within a band; its *Solvable* entry names the bands and says
#   the order never enlarges the set; SKILL.md's `solvable-issues.sh` bullet states the
#   order and names `VERI_PRIORITY_LABEL`; and CLAUDE.md names the tunable, the order, and
#   carries the reorders-not-enlarges sentence.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings: what a document has to record is the claim, and how it is phrased belongs to
# whoever writes it — the protocol model-knobs-recorded.test.sh and lane-rule-recorded.test.sh
# both use on these documents.
#
# Not asked here: that CLAUDE.md's script and suite counts moved when this suite landed.
# claude-md-counts.test.sh is the case that holds every count in that document to the files
# on disk, and this file arriving in the tree is what makes it answer.
#
# Run: skills/tdd/scripts/tests/selection-order-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The three documents. Each twice — the path as a failure message spells it, and the same
# path resolved for the probes to read — so a message can never name a file the probes did
# not open. The pairing model-knobs-recorded.test.sh uses, for the same reason.
context_md="CONTEXT.md"
context_path="$ROOT/$context_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

pass=0 fail=0

# report, plain, records, bullet and says: the helpers the *-recorded.test.sh suites
# share (issue #225). `bullet` reads "$skill_path"; `says` reads the passage_ globals.
# shellcheck source=record-helpers.sh
source "$HERE/record-helpers.sh"

# entry <term> — one CONTEXT.md glossary entry as a single normalised line: from its
# `**<term>**:` heading to the `_Avoid_` line that closes it, the next entry's heading or
# the next `## `. Read by term rather than file-wide because each fact below has a place it
# belongs: the order stated under *Bug* would answer for a glossary whose *Selection layer*
# entry — the one every other document defers to for what selection does — still says the
# scope is printed ascending. One line because CONTEXT.md wraps mid-sentence.
entry() {
  awk -v want="^\\\\*\\\\*$1\\\\*\\\\*:" '
    $0 ~ want { inside = 1; next }
    inside && (/^_Avoid_/ || /^\*\*/ || /^## /) { exit }
    inside' "$context_path" | plain | tr '\n' ' '
}

# The claims, as the regexes that carry them. Written once each because four passages ask
# for the same things, and four copies would drift into asking four different questions.
PRIORITY_BAND='priority'                                  # the band, and the label naming it
BUG_BAND='bug'                                            # the band that already existed
ASCENDING='ascending|by number|lowest number|increasing|numeric'
ORDERED='first|before|then|band|ahead'                    # that the bands are an order at all
TUNABLE='veri_priority_label'
NOT_ENLARGE='enlarge|reorder|re-order|only.*order|never.*solvable|not.*solvable|still.*not printed'

# passage_text / passage_from — the passage a probe last read and the label a failure names
# it by, filled by the readers below and read by `says`. Globals because bash has no way to
# hand back a string; the `passage_` prefix is what marks the pair as one thing written by a
# reader and read by a claim, the convention model-knobs-recorded.test.sh follows.
passage_text="" passage_from=""

# need_passage <label> <text> <problem> — the three readers below are one shape: put a
# passage and the name a failure calls it by into the globals, and fail closed when the
# passage is not there. Written once here so the fail-closed check cannot come to mean
# three different things; each reader still derives its own label and its own problem, so
# no caller can report a passage under a name the probe did not read.
#
# Fail closed rather than letting the claims run: an empty string matches no regex, so
# every fact asked of a passage that is not there would be reported missing — true, but it
# names several edits when the repair is that one entry was renamed.
need_passage() {
  passage_from="$1"
  passage_text="$2"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

# need_entry <term> — that CONTEXT.md entry into those globals.
need_entry() {
  need_passage "$context_md's $1 entry" "$(entry "$1")" \
    "$context_md has no '$1' glossary entry to read, so the order is unstated where every other document defers to it"
}

# need_solvable_bullet — SKILL.md's `solvable-issues.sh` bullet into the same globals.
need_solvable_bullet() {
  need_passage "$skill_md's solvable-issues.sh bullet" "$(bullet '^[-*] .*solvable-issues\.sh')" \
    "$skill_md has no top-level 'solvable-issues.sh' bullet to read, so the order and the tunable an operator looks up beside VERI_GH_JSON could not be found"
}

# need_claude_md_records — all of CLAUDE.md's records into the same globals, for the claims
# that are about what a document says rather than about where it says it. CLAUDE.md is read
# whole on purpose: the step asks that the document record the order and the tunable, not
# that either sit under a heading this suite picked.
need_claude_md_records() {
  need_passage "$claude_md" "$(records < "$claude_path")" \
    "$claude_md could not be read, so nothing could be asked of what it records"
}

# states_the_order <what> — the three-band order in one record of the passage last read:
# both bands named, that they are an order, and that a band is walked ascending. Written
# once because three of the four passages owe it.
states_the_order() {
  says "$1 — priority, then bug, then the rest, each band ascending by number" \
    "$PRIORITY_BAND" "$BUG_BAND" "$ORDERED" "$ASCENDING"
}

# probe_context_selection_layer_states_the_order — the entry that says what the selection
# layer prints. It already says "bugs first and then ascending", which is now the middle
# band described as the first one.
probe_context_selection_layer_states_the_order() {
  need_entry "Selection layer" || return

  states_the_order "states the three-band order"
}

# probe_context_solvable_bounds_the_order — the entry that defines the four conditions, and
# therefore the one place the band has to be bounded: it names the bands and says the order
# runs on what the conditions leave rather than adding to it. Asked here rather than of the
# *Selection layer* entry because this is the entry a reader is in when they ask whether the
# label makes an issue takeable.
probe_context_solvable_bounds_the_order() {
  need_entry "Solvable" || return

  says "that the order runs over the solvable set and never enlarges it — a priority or bug issue still has to pass the four conditions" \
    "$PRIORITY_BAND" "$BUG_BAND" "$NOT_ENLARGE"
}

# probe_skill_bullet_states_order_and_tunable — the bullet that carries the script's
# contract, where `VERI_GH_JSON` is already listed and where the word "ascending" stands
# today with nothing in front of it.
probe_skill_bullet_states_order_and_tunable() {
  need_solvable_bullet || return

  states_the_order "states the three-band order"

  says "which tunable names the priority label — VERI_PRIORITY_LABEL" "$TUNABLE"
}

# probe_claude_md_names_the_tunable_and_the_bound — the document an agent reads first, and
# the two facts it owes: the order with the variable that names its first band, and the
# sentence that keeps the band from being read as a fifth condition.
probe_claude_md_names_the_tunable_and_the_bound() {
  need_claude_md_records || return

  says "the three-band order and the tunable that names the priority label — VERI_PRIORITY_LABEL" \
    "$TUNABLE" "$PRIORITY_BAND" "$BUG_BAND" "$ORDERED" "$ASCENDING"

  says "that priority reorders the solvable set and does not enlarge it" \
    "$PRIORITY_BAND" "$NOT_ENLARGE"
}

# 1. One criterion, one case: the order and its tunable are recorded in the three documents
#    that are read before an issue is selected. One case rather than four, because a reader
#    given the order without the variable, or the variable without the bound on it, has been
#    handed the same unusable record — and the problem lines say which sentence is missing
#    from which document.
name="$context_md's Selection layer and Solvable entries, $skill_md's solvable-issues.sh bullet and $claude_md record the three-band order and VERI_PRIORITY_LABEL, and say priority reorders the solvable set without enlarging it"
problems=()

probe_context_selection_layer_states_the_order
probe_context_solvable_bounds_the_order
probe_skill_bullet_states_order_and_tunable
probe_claude_md_names_the_tunable_and_the_bound

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
