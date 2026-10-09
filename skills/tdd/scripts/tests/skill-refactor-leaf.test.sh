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

name="$skill_md's Refactor section launches one leaf per step and refuses verify-refactor over a dirty tree or a non-refactor: commit since the green commit, narrating the count against the budget"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "how the refactor leaf is launched and what is asked of its result could not be established")")
else
  [[ "$section" =~ $one_leaf ]] ||
    problems+=("$skill_md's Refactor section never says one leaf applies the step's transforms, so the conductor is not told that the cold start and the spec re-read are paid once rather than once per transform")
  relaunch="$(phrase 'repeatedly|(each|every|the next) iteration' "$section")"
  [[ -z "$relaunch" ]] ||
    problems+=("$skill_md's Refactor section still launches a leaf per transform — it says '$relaunch' — so the leaf-per-transform cost this issue measured is still prescribed")

  dirty="$(window "$section" 'git status --porcelain')"
  if [[ -z "$dirty" ]]; then
    problems+=("$skill_md's Refactor section never asks git status --porcelain, so the conductor walks into verify-refactor over whatever a killed leaf left uncommitted")
  else
    grep -qE "$refusal" <<<"$dirty" ||
      problems+=("$skill_md's Refactor section asks git status --porcelain without saying a non-empty answer stops it, so the check is asked and its answer is advisory")
  fi

  subjects="$(window "$section" '(--(format|pretty)=%s|subject)')"
  if [[ -z "$subjects" ]]; then
    problems+=("$skill_md's Refactor section never reads the subjects of the commits since the green commit, so a leaf that committed something other than a refactor: goes to verify-refactor unchallenged")
  else
    grep -qE 'refactor:' <<<"$subjects" ||
      problems+=("$skill_md's Refactor section reads commit subjects without saying they must be refactor:, so what the conductor is checking for is left to judgement")
    grep -qE "$refusal" <<<"$subjects" ||
      problems+=("$skill_md's Refactor section never says a non-refactor: commit since the green commit stops it, so the check has no branch and the run continues either way")
  fi

  counted="$(window "$section" 'rev-list --count')"
  if [[ -z "$counted" ]]; then
    problems+=("$skill_md's Refactor section never counts the refactor: commits with git rev-list --count, so what it narrates is the leaf's word for what it did rather than what is in the history")
  else
    grep -qE 'budget|refactor [0-9k]+/' <<<"$counted" ||
      problems+=("$skill_md's Refactor section counts the refactor: commits without narrating them against the budget, so the cost axis this issue is about is not reported at all")
  fi

  grep -qE 'overrun|over the budget|above the budget|exceed' <<<"$section" ||
    problems+=("$skill_md's Refactor section never says a count above the budget is narrated as an overrun, so a leaf that ran past the number it was given reads in the thread as one that did not")
fi

report "$name"

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

name="$context_md's Cycle entry and $claude_md's budget invariant describe one refactor leaf per step and point at the ADR that records it"
problems=()

cycle="$(record "$context_path" '^cycle:')"
invariant="$(record "$claude_path" 'veri_stuck_retries' 'revise_budget' 'veri_refactor_budget')"

if [[ -z "$cycle" ]]; then
  problems+=("$context_md has no Cycle glossary entry to read — what this repository tells the next agent a refactor step is could not be established")
else
  [[ "$cycle" =~ $one_leaf ]] ||
    problems+=("$context_md's Cycle entry never says the refactor step is one leaf, so the glossary still describes the cycle as spending a leaf per transform")
  stale_cycle="$(phrase 'per leaf|until none remain|per leaf invocation' "$cycle")"
  [[ -z "$stale_cycle" ]] ||
    problems+=("$context_md's Cycle entry still says '$stale_cycle', so the entry a reader learns the cycle from is ADR-0010's shape and contradicts the procedure SKILL.md now runs")
fi

if [[ -z "$invariant" ]]; then
  problems+=("$claude_md has no invariant naming all three budgets to read — what VERI_REFACTOR_BUDGET is said to bound could not be established")
else
  [[ "$invariant" =~ $one_leaf ]] ||
    problems+=("$claude_md's budget invariant never says one leaf spends the step's refactor budget, so the cost axis is still explained as a leaf per transform")
  stale_invariant="$(phrase 'asked for one always finds one|one transform per leaf|a transform per leaf' "$invariant")"
  [[ -z "$stale_invariant" ]] ||
    problems+=("$claude_md's budget invariant still explains the budget by '$stale_invariant', which is only true of a leaf asked for a single transform")
fi

[[ -n "$(adr_pointer "$cycle $invariant")" ]] ||
  problems+=("neither $context_md's Cycle entry nor $claude_md's budget invariant names an ADR other than the superseded 0010, so nothing in either record points a reader at the decision that replaced one transform per leaf")

report "$name"

add_ledger_step='\$s/add-ledger-step\.sh'

name="$skill_md's Refactor section passes the flags' behaviours to one add-ledger-step.sh call after the step, and commits the grown ledger with the refactor-pending clear"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "what becomes of the leaf's NEW_STEP: lines could not be established")")
else
  calls="$(grep -oE "$add_ledger_step" <<<"$section" | grep -c '')"
  if [[ "$calls" -eq 0 ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the leaf's NEW_STEP: lines are narrated and nothing grows the plan — the triangulating step the leaf refused to write by hand is owed to nobody")
  elif [[ "$calls" -gt 1 ]]; then
    problems+=("$skill_md's Refactor section runs add-ledger-step.sh $calls times, so a step's NEW_STEP: values are inserted a call at a time and the growth budget is read once per value rather than once for the step")
  else
    added="$(window "$section" "$add_ledger_step")"
    grep -qE "'<[^>]*behaviou?r>'" <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying the texts are the flags' behaviours, so what the inserted step says is left to judgement")
    grep -qE "after ['\"]?(<step>|\\$\\(\\\$s/next-pending-refactor\\.sh)" <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without anchoring the insertion after the step just refactored, so the triangulating step lands somewhere other than next to the code it triangulates")
  fi

  cleared="$(window "$section" 'clear-refactor-pending\.sh')"
  if [[ -z "$cleared" ]]; then
    problems+=("$skill_md's Refactor section never clears the refactor-pending mark, so the commit the grown ledger is supposed to ride does not exist to be read for")
  else
    grep -qE 'add-ledger-step' <<<"$cleared" ||
      problems+=("$skill_md's Refactor section commits the cleared ledger without the steps add-ledger-step.sh inserted into it, so a step added for triangulation is lost the moment the run is resumed from the committed ledger")
  fi
fi

report "$name"

name="$skill_md's Refactor section narrates add-ledger-step.sh exit 1 as owed steps and does not bail on it"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "what the conductor does when the plan-growth budget cannot hold the leaf's NEW_STEP: values could not be established")")
else
  owed_claim="$(either_order 'exit 1' 'owed' '.{0,120}')"
  if ! grep -qE "$owed_claim" <<<"$section"; then
    problems+=("$skill_md's Refactor section never says what add-ledger-step.sh exit 1 means, so a conductor meeting the plan-growth budget's refusal is left to read it as the failure every other non-zero exit in this phase is, and the NEW_STEP: values it filed as owed steps go unmentioned")
  else
    clause="$(window "$section" "$owed_claim" 150)"
    bailed="$(phrase 'bail|abort' "$clause")"
    [[ -z "$bailed" ]] ||
      problems+=("$skill_md's Refactor section says '$bailed' where it narrates add-ledger-step.sh exit 1, so a ledger whose growth budget is full ends a run whose step verified PASS — the owed steps are recorded and the plan simply did not grow, which is nothing to stop for")
  fi
fi

report "$name"

name="$skill_md's Refactor section passes the passing verify-refactor verdict's uncovered-spec flags to the same add-ledger-step.sh call as the leaf's"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "what becomes of the verify-refactor verdict's NEW_STEP: lines could not be established")")
else
  added="$(window "$section" "$add_ledger_step")"
  if [[ -z "$added" ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the verifier's NEW_STEP: proposals are narrated and nothing grows the plan — the edge case it stopped REJECTing for is proposed to nobody")
  else
    grep -qE 'verif|verdict' <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh over the leaf's NEW_STEP: values alone, so the passing verify-refactor verdict's own values never reach the ledger — the unhandled edge case the verifier stopped REJECTing for is proposed to nobody")
  fi
fi

report "$name"

denial_word='no|never|neither|without|not'

denial="($denial_word)[^.]{0,80}"

amendment='amend|ledger (step|line)|add-ledger-step|grow'

name="$skill_md's Refactor section answers an overfit flag with one triangulating red/green pair inside the step, adding no ledger step and no second step-done, and resumes that step's refactor loop with the budget it had left"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "what the conductor does with an overfit flag could not be established")")
else
  flagged="$(wins 'overfit')"
  if [[ -z "$flagged" ]]; then
    problems+=("$(unnamed_class_problem overfit "the conductor branches on its own judgement rather than on the leaf's word")")
  else
    grep -qE "$(either_order 'triangulat[a-z]*' 'verify-(red|green)' '[^.]{0,200}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says an overfit flag is answered by a triangulating red and green pair, so the case the leaf named is either built unverified or not built at all")

    grep -qE "$denial($amendment)" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the plan does not grow for it, so the triangulation becomes a ledger step with a refactor loop of its own — the #107 chain this issue is against")
    grep -qE "$denial(second )?step.done" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the step is not mirrored done a second time, so one step reports itself finished twice and the issue thread stops saying how many steps ran")

    grep -qE "$(either_order '(resum|return|back)' 'budget' '[^.]{0,160}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says the step resumes its own refactor loop with the budget it had left after the triangulation, so the tidying the flag interrupted is either abandoned or restarted with a budget the step has already spent")
  fi
fi

report "$name"

name="$skill_md's Refactor section amends the plan from an uncovered-spec flag and from no other flag class"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "which flag class grows the plan could not be established")")
else
  uncovered="$(wins 'uncovered-spec')"
  if [[ -z "$uncovered" ]]; then
    problems+=("$(unnamed_class_problem uncovered-spec "no flag is routed to a plan amendment by its class and the conductor amends from whichever flag it reads")")
  else
    grep -qE "$amendment" <<<"$uncovered" ||
      problems+=("$skill_md's Refactor section names the uncovered-spec class without saying it is what amends the plan, so a behaviour the spec requires and no step covers is narrated and never planned")

    grep -qE '(only|alone|no other|the one (flag|class))' <<<"$uncovered" ||
      problems+=("$skill_md's Refactor section amends the plan from an uncovered-spec flag without saying that no other flag class does, so an overfit or beyond-spec flag still becomes a ledger step with a refactor loop of its own")
  fi

  grown="$(window "$section" "$add_ledger_step")"
  if [[ -n "$grown" ]] && ! grep -F 'uncovered-spec' >/dev/null <<<"$grown"; then
    problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying its texts are the uncovered-spec flags' behaviours, so the plan grows from a class other than the one allowed to grow it")
  fi
fi

report "$name"

name="$skill_md's Refactor section narrates a beyond-spec flag as a follow-up in the Refactor comment and in the PR body, planning and building neither"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "where a beyond-spec flag goes could not be established")")
else
  beyond="$(wins 'beyond-spec')"
  if [[ -z "$beyond" ]]; then
    problems+=("$(unnamed_class_problem beyond-spec "the class the spec never asked for is routed on the conductor's own judgement, the way the classes were before the leaf carried them")")
  else
    grep -qE "$(either_order 'follow.?up' '(🛠️ )?refactor comment|narrat|post' '[^.]{0,200}')" <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never says a beyond-spec flag is narrated as a follow-up in the 🛠️ Refactor comment, so what the leaf found is neither built nor said out loud and the run ends having dropped it")

    grep -qE 'pr body|body of the (draft )?pr|pull request body' <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never carries a beyond-spec flag into the PR body, so the follow-up is buried in one step's comment and the human deciding the merge never sees it")

    grep -qE "($denial_word) (planned|plan|built|build)" <<<"$beyond" ||
      problems+=("$skill_md's Refactor section narrates a beyond-spec flag without saying it is neither planned nor built in this run, so the run still builds behaviour the issue's spec never asked for")
  fi
fi

report "$name"

name="$skill_md's Refactor section runs a step's triangulation at most once, narrating a flag raised inside that triangulation's own refactor loop about the same code rather than triangulating it again"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "whether a step's triangulation runs more than once could not be established")")
else
  triangulation="$(wins 'triangulat')"
  if [[ -z "$triangulation" ]]; then
    problems+=("$skill_md's Refactor section never mentions triangulation at all, so there is no ceiling on it to read and an overfit flag raised inside one is answered with another")
  else
    grep -qE "at most once|only once|once (per|a) step|(${denial_word}) ((a )?(second|further|another) (triangulat[a-z]*|time)|triangulat[a-z]* (it |them )?(again|a second time))" <<<"$triangulation" ||
      problems+=("$skill_md's Refactor section puts no ceiling on a step's triangulation, so the loop it resumes can flag the same code again and buy a second pair — the #107 chain this issue is against, moved inside one step")

    grep -qE "$(either_order 'narrat' '(again|a second (time|triangulation)|same code)' '[^.]{0,200}')" <<<"$triangulation" ||
      problems+=("$skill_md's Refactor section never says a flag raised inside a triangulation's own refactor loop about the same code is narrated, so what the second flag found is dropped without a word")
  fi
fi

report "$name"

name="$skill_md grows the plan from the refactor leaf's FLAGS: classes alone, reading no NEW_STEP: or CANDIDATES: line of the leaf's into it"
problems=()

whole="$(flat <"$skill_path")"

if unreadable_section; then
  problems+=("$(unreadable_problem "what the plan is grown from could not be established")")
else
  grown="$(window "$section" "$add_ledger_step")"
  if [[ -z "$grown" ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so no flag is ever planned")
  else
    grep -E "'<[^>]*leaf[^>]* [a-z]+-[a-z]+ behaviou?r>'" >/dev/null <<<"$grown" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying its texts come from the leaf's FLAGS: lines, so the plan grows from something other than the classed flags that are allowed to grow it")
  fi
fi

leaf_new_step="$(phrase "$(either_order "leaf's" 'new_step' '[^.]{0,30}')" "$whole")"
[[ -z "$leaf_new_step" ]] ||
  problems+=("$skill_md still reads a NEW_STEP: line from the refactor leaf — it says '$leaf_new_step' — a line the built refactor prompt never asks for, so the conductor grows the plan from a report line no leaf writes")

candidate_growth="$(phrase "$(either_order 'candidates:' "($amendment)" '[^.]{0,80}')" "$whole")"
[[ -z "$candidate_growth" ]] ||
  problems+=("$skill_md grows the plan from the leaf's CANDIDATES: lines — it says '$candidate_growth' — so leftover tidying becomes ledger steps with refactor loops of their own")

report "$name"

name="$skill_md's Refactor section does not bail when no ledger step carries criterion k yet, since add-ledger-step.sh --criterion accepts it (#1292)"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "what the conductor does with a criterion no ledger step carries could not be established")")
else
  uncarried_bail="$(phrase "$(either_order 'bail' 'carr[a-z]* criterion' '[^.]{0,200}')" "$section")"
  [[ -z "$uncarried_bail" ]] ||
    problems+=("$skill_md's Refactor section still bails on a criterion no ledger step carries — it says '$uncarried_bail' — so a behaviour serving a criterion the plan never covered ends the run, though add-ledger-step.sh --criterion now tags that step and no Bailing cause fits it")
fi

report "$name"

name="$skill_md's Refactor sub-step 4 sends each uncovered-spec behaviour into the add-ledger-step.sh call for the criterion it serves, one call per criterion, not into one shared call (#1292)"
problems=()

if unreadable_section; then
  problems+=("$(unreadable_problem "which add-ledger-step.sh call an uncovered-spec flag's behaviour goes into could not be established")")
else
  opening='an uncovered-spec flag is the one class that grows the plan'
  substep=""
  [[ "$section" == *"$opening"* ]] && substep="$opening${section#*"$opening"}" && substep="${substep%%a beyond-spec flag is narrated*}"
  if [[ -z "$substep" ]]; then
    problems+=("$skill_md's Refactor section has no sub-step 4 opening 'an uncovered-spec flag is the one class that grows the plan', so where its behaviours go could not be established")
  else
    shared="$(phrase "the same[^.]{0,80}add-ledger-step\\.sh[^.]{0,80}call" "$substep")"
    [[ -z "$shared" ]] ||
      problems+=("$skill_md's Refactor sub-step 4 still sends every uncovered-spec behaviour into one shared call — it says '$shared' — so behaviours serving different criteria are tagged with one --criterion and the plan is mis-tagged")
    grep -E 'one call per criterion|call for the criterion (it|the behaviour) serves' >/dev/null <<<"$substep" ||
      problems+=("$skill_md's Refactor sub-step 4 never says a behaviour goes into the add-ledger-step.sh call for the criterion it serves, one call per criterion, so it disagrees with the one-call-per-criterion rule beside the PASS branch's calls")
  fi
fi

report "$name"

finish
