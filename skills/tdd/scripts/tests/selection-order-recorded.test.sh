#!/usr/bin/env bash
# Unit tests for the three root documents' record of the selection order — which band an
# issue is taken in, and the tunable that names the label putting it in the first one.
#
# Contract under test:
#   CONTEXT.md's *Selection layer* entry states the three-band order — priority, then bug,
#   then the rest, ascending within a band; its *Solvable* entry names the bands and says
#   the order never enlarges the set; SKILL.md's `solvable-issues.sh` bullet states the
#   order and names `VERI_PRIORITY_LABEL`; and CLAUDE.md names the tunable, the order, and
#   carries the reorders-not-enlarges sentence. Each fact is asked as a regex, not a fixed
#   string.
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

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"
source "$HERE/lib/claude-md-records.sh"

entry() {
  want="^\\*\\*$1\\*\\*:" awk '
    $0 ~ ENVIRON["want"] { inside = 1; next }
    inside && (/^_Avoid_/ || /^\*\*/ || /^## /) { exit }
    inside' "$context_path" | plain --join
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

name="#1037: entry given 'run\\.sh' starts at the entry where run.sh stands, not the one where runXsh does"
fixture="$(scratch_dir)"
printf -- '**runXsh**:\nwrong\n**run.sh**:\nright\n' > "$fixture/CONTEXT.md"
expect_eq "$name" 'right ' "$(context_path="$fixture/CONTEXT.md" entry 'run\.sh')"

finish
