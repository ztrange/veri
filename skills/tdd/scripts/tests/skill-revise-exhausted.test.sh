#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do when a step's revise
# budget runs out, read as text.
#
# Contract under test:
#   SKILL.md launches the `exhausted` leaf and acts on each of exhausted-outcome.sh's three
#   answers: exit 0 split, 1 needs the user, 3 neither.
#
# Run: scripts/tests/skill-revise-exhausted.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


revise_heading='## Revising on a REJECT'

revise_lines() {
  awk -v h="$revise_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path"
}

revise_section() {
  revise_lines | plain --join
}
section="$(revise_section)"

unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$revise_heading' section to read —"

outcome_reader='\$s/exhausted-outcome\.sh'
add_ledger_step='\$s/add-ledger-step\.sh'
needs_user='needs_user|needs-user|needs the user'
bail_cause='revise-exhausted'

needs_user_open='exit 1 — the step needs the user'
needs_user_close='exit 3'

needs_user_branch() {
  awk -v o="$needs_user_open" -v c="$needs_user_close" \
    '!inside && index($0, o) { inside = 1 }
     inside && index($0, c) && !index($0, o) { exit }
     inside' "$skill_path" | plain --join
}
branch="$(needs_user_branch)"

issue_mirror='gh issue comment|post a [^.]{0,120}comment'

unestablished="what a parked step leaves the user could not be established"

step_cost='step-cost.sh'

after_wait() {
  awk -v w="wait-leaf.sh $1" \
    '!inside && index($0, w) { inside = 1; next }
     inside && (index($0, "detach-leaf.sh") || index($0, "tick-ledger.sh")) { exit }
     inside' "$skill_path"
}

pre_commit_leaves=(develop-red verdict-red 'revise-<phase>-<k>' develop-green verdict-green)

finish
