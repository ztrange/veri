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
ROOT="$(cd "$HERE/../../../.." && pwd)"

context_md="CONTEXT.md"
context_path="$ROOT/$context_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

pass=0 fail=0

source "$HERE/record-helpers.sh"

entry() {
  awk -v want="^\\\\*\\\\*$1\\\\*\\\\*:" '
    $0 ~ want { inside = 1; next }
    inside && (/^_Avoid_/ || /^\*\*/ || /^## /) { exit }
    inside' "$context_path" | plain | tr '\n' ' '
}

PRIORITY_BAND='priority'                                  # the band, and the label naming it
BUG_BAND='bug'                                            # the band that already existed
ASCENDING='ascending|by number|lowest number|increasing|numeric'
ORDERED='first|before|then|band|ahead'                    # that the bands are an order at all
TUNABLE='veri_priority_label'
NOT_ENLARGE='enlarge|reorder|re-order|only.*order|never.*solvable|not.*solvable|still.*not printed'

passage_text="" passage_from=""

need_passage() {
  passage_from="$1"
  passage_text="$2"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$3")
  return 1
}

need_entry() {
  need_passage "$context_md's $1 entry" "$(entry "$1")" \
    "$context_md has no '$1' glossary entry to read, so the order is unstated where every other document defers to it"
}

need_solvable_bullet() {
  need_passage "$skill_md's solvable-issues.sh bullet" "$(bullet '^[-*] .*solvable-issues\.sh')" \
    "$skill_md has no top-level 'solvable-issues.sh' bullet to read, so the order and the tunable an operator looks up beside VERI_GH_JSON could not be found"
}

need_claude_md_records() {
  need_passage "$claude_md" "$(records < "$claude_path")" \
    "$claude_md could not be read, so nothing could be asked of what it records"
}

states_the_order() {
  says "$1 — priority, then bug, then the rest, each band ascending by number" \
    "$PRIORITY_BAND" "$BUG_BAND" "$ORDERED" "$ASCENDING"
}

probe_context_selection_layer_states_the_order() {
  need_entry "Selection layer" || return

  states_the_order "states the three-band order"
}

probe_context_solvable_bounds_the_order() {
  need_entry "Solvable" || return

  says "that the order runs over the solvable set and never enlarges it — a priority or bug issue still has to pass the four conditions" \
    "$PRIORITY_BAND" "$BUG_BAND" "$NOT_ENLARGE"
}

probe_skill_bullet_states_order_and_tunable() {
  need_solvable_bullet || return

  states_the_order "states the three-band order"

  says "which tunable names the priority label — VERI_PRIORITY_LABEL" "$TUNABLE"
}

probe_claude_md_names_the_tunable_and_the_bound() {
  need_claude_md_records || return

  says "the three-band order and the tunable that names the priority label — VERI_PRIORITY_LABEL" \
    "$TUNABLE" "$PRIORITY_BAND" "$BUG_BAND" "$ORDERED" "$ASCENDING"

  says "that priority reorders the solvable set and does not enlarge it" \
    "$PRIORITY_BAND" "$NOT_ENLARGE"
}

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
