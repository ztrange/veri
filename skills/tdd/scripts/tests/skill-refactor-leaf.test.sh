#!/usr/bin/env bash
# Unit tests for the shape of the refactor phase skills/tdd/SKILL.md prescribes, read as
# text.
#
# Contract under test — one case each:
#   1. SKILL.md's Refactor section launches ONE leaf for the step rather than one per
#      transform; before verify-refactor it asks `git status --porcelain` and refuses to go
#      on while the tree is dirty; it asks the subjects of the commits since the green
#      commit and refuses to go on when one of them is not a `refactor:`; and it counts
#      those commits with `git rev-list --count` and narrates the count against the budget,
#      saying so when the count is over it rather than leaving the overrun out.
#   2. CONTEXT.md's **Cycle** entry and CLAUDE.md's budgets invariant describe that same
#      shape — one refactor leaf for the step, not a transformation per leaf — and point a
#      reader at the ADR that now records it.
#   3. SKILL.md's Refactor section passes the leaf's `NEW_STEP:` values to one
#      `add-ledger-step.sh … after '<STEP>'` call once verify-refactor has PASSed, and the
#      ledger those steps landed in rides the commit that clears the refactor-pending mark.
#   4. That section narrates `add-ledger-step.sh` exit 1 — the plan-growth budget is full, so
#      nothing was inserted and every value was filed under the ledger's `## Owed steps`
#      heading — as the owed steps it is, and does not bail on it.
#   5. That same one call carries the passing verify-refactor verdict's own `NEW_STEP:`
#      values as well as the leaf's.
#   6. That section answers an `overfit` flag with one triangulating red/green pair inside
#      the step that raised it — no ledger step, no second `### ✅ Step done` — and then
#      resumes that step's own refactor loop with the budget it had left.
#   7. That section amends the plan from an `uncovered-spec` flag and from **no other**
#      flag class, and the one add-ledger-step.sh call is fed that class's behaviours.
#   8. That section narrates a `beyond-spec` flag as a follow-up — in the `### 🛠️ Refactor`
#      comment and in the PR body — and neither plans nor builds it in this run.
#   9. That section runs a step's triangulation at most once, narrating a flag raised inside
#      that triangulation's own refactor loop about the same code rather than triangulating
#      it a second time.
#  10. SKILL.md grows the plan from the refactor leaf's FLAGS: classes alone: the one
#      add-ledger-step.sh call is fed from flags' behaviours, and nowhere does the document
#      read a NEW_STEP: or CANDIDATES: line of the leaf's into the plan.
#  11. That section does not bail when no ledger step carries the uncovered-spec
#      behaviour's criterion k yet, since add-ledger-step.sh --criterion accepts it.
#  12. That section's sub-step 4 sends each uncovered-spec behaviour into the
#      add-ledger-step.sh call for the criterion it serves, one call per criterion, rather
#      than into one shared call.
#  13. That section says each per-criterion add-ledger-step.sh call emits its own step-added
#      event, anchored on the step and carrying added=<that call's count>.
#
# Run: scripts/tests/skill-refactor-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

context_md="CONTEXT.md"
context_path="$ROOT/$context_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

one_leaf='(one|a single) (refactor |developer |transform )?leaf'


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


refactor_heading='#### Refactor'

flat() {
  plain --join
}

refactor_section() {
  awk -v h="$refactor_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" | flat
}
section="$(refactor_section)"

unreadable_section() {
  [[ -z "${section// /}" ]]
}

unreadable_problem() {
  printf "%s has no '%s' section to read — %s" "$skill_md" "$refactor_heading" "$1"
}

unnamed_class_problem() {
  printf "%s's Refactor section never names the %s class the leaf's FLAGS: line carries, so %s — the six plan: amend commits this issue counted" "$skill_md" "$1" "$2"
}

phrase() {
  head -1 < <(grep -oE "$1" <<<"$2")
}

wins() {
  windows "$section" "$@" | tr '\n' ' '
}

either_order() {
  printf '((%s)%s(%s)|(%s)%s(%s))' "$1" "$3" "$2" "$2" "$3" "$1"
}

refusal='refus|do(es)? not (go on|continue|proceed)|don.t (go on|continue)|not continue|bail'

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$1" | plain
}

record() {
  local path="$1"; shift
  local rec re ok
  while IFS= read -r rec; do
    ok=1
    for re in "$@"; do [[ "$rec" =~ $re ]] || { ok=0; break; }; done
    [[ "$ok" -eq 1 ]] && { printf '%s' "$rec"; return; }
  done < <(records_of "$path")
}

adr_pointer() {
  local ref digits
  while IFS= read -r ref; do
    digits="${ref##*[!0-9]}"
    [[ "$((10#$digits))" -eq 10 ]] && continue
    printf '%s' "$ref"
    return
  done < <(grep -oE 'adr[- ]?[0-9]+' <<<"$1")
}

add_ledger_step='\$s/add-ledger-step\.sh'

denial_word='no|never|neither|without|not'

denial="($denial_word)[^.]{0,80}"

amendment='amend|ledger (step|line)|add-ledger-step|grow'

finish
