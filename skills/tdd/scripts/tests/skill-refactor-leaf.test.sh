#!/usr/bin/env bash
# Unit test for the shape of the refactor phase skills/tdd/SKILL.md prescribes. Like
# skill-suite-runs.test.sh and skill-leaf-launch.test.sh this suite belongs to no single
# script: its subject is the procedure, read as text, the way the session that follows it
# reads it. Zero-dependency plain-shell asserts, same idiom, picked up by `make test`'s
# glob by existing.
#
# Why this exists (issue #150): ADR-0010 ran one transform per leaf so a break could be
# traced to one change, and the conductor paid a cold `claude -p` start and a re-read of
# the spec and the touched files for every transform. Measured: #144's refactor loops plus
# verify-refactor took 2,147 of that run's 3,735 leaf-seconds, and one #137 step's five
# transforms took 49 minutes between them. Tracing a break to one change needs a commit per
# transform and a suite run between transforms; it does not need a leaf each.
#
# So the leaf now applies the whole budget and commits each transform itself, and the
# conductor's job changes from producing that result to CHECKING it. That check is the only
# thing standing between a killed or a disobedient leaf and a verify-refactor run on a state
# nobody looked at: the transform a dying leaf left on disk is uncommitted work no verifier
# has seen, and a commit since the green one whose subject is not `refactor:` is production
# code smuggled past the blind verifier of the phase that was supposed to be
# behavior-preserving. Neither is visible to verify-refactor, which judges the settled tree.
#
# Contract under test — ten criteria, the procedure, the account of it, what the leaf's
# report grows, what a growth budget too full to hold it means, whose proposals that
# growth carries, where an overfit flag is answered, which flag class grows the plan, where
# a beyond-spec flag goes instead, how often one step may triangulate, and which report
# lines the plan grows from, one case each:
#   1. SKILL.md's Refactor section launches ONE leaf for the step rather than one per
#      transform; before verify-refactor it asks `git status --porcelain` and refuses to go
#      on while the tree is dirty; it asks the subjects of the commits since the green
#      commit and refuses to go on when one of them is not a `refactor:`; and it counts
#      those commits with `git rev-list --count` and narrates the count against the budget,
#      saying so when the count is over it rather than leaving the overrun out.
#   2. CONTEXT.md's **Cycle** entry and CLAUDE.md's three-budgets invariant describe that
#      same shape — one refactor leaf for the step, not a transformation per leaf — and
#      point a reader at the ADR that now records it.
#   3. SKILL.md's Refactor section passes the leaf's `NEW_STEP:` values to one
#      `add-ledger-step.sh … after '<STEP>'` call once verify-refactor has PASSed, and the
#      ledger those steps landed in rides the commit that clears the refactor-pending mark
#      (issue #361).
#   4. That section narrates `add-ledger-step.sh` exit 1 — the plan-growth budget is full, so
#      nothing was inserted and every value was filed under the ledger's `## Owed steps`
#      heading — as the owed steps it is, and does not bail on it (issue #361).
##   5. That same one call carries the passing verify-refactor verdict's own `NEW_STEP:`
#      values as well as the leaf's, so the unhandled edge case the refactor verifier now
#      proposes instead of REJECTing for reaches the plan (issue #362).
#   6. That section answers an `overfit` flag with one triangulating red/green pair inside
#      the step that raised it — no ledger step, no second `### ✅ Step done` — and then
#      resumes that step's own refactor loop with the budget it had left (issue #175).
#   7. That section amends the plan from an `uncovered-spec` flag and from **no other**
#      flag class, and the one add-ledger-step.sh call is fed that class's behaviours
#      (issue #175).
#   8. That section narrates a `beyond-spec` flag as a follow-up — in the `### 🛠️ Refactor`
#      comment and in the PR body — and neither plans nor builds it in this run (issue #175).
##   9. That section runs a step's triangulation at most once, narrating a flag raised inside
#      that triangulation's own refactor loop about the same code rather than triangulating
#      it a second time (issue #175).
#  10. SKILL.md grows the plan from the refactor leaf's FLAGS: classes alone: the one
#      add-ledger-step.sh call is fed from flags' behaviours, and nowhere does the document
#      read a NEW_STEP: or CANDIDATES: line of the leaf's into the plan (issue #175). Which
#      class those flags are is case 7's question alone, so a document that grants the
#      amendment to the wrong class fails case 7 and no other.
#
# That the section's account of the leaf's report footer names exactly the lines the built
# refactor prompt asks for is skill-refactor-footer.test.sh's case, not one here: it runs
# build-develop-prompt.sh, and the two guards that replant this suite into a tree holding
# only the documents it reads would see it red there for a reason no plant put there.
#
# Case 1 is one criterion — the conductor launches one leaf and checks its result instead of
# producing it — and its probes are its parts: a document that launched one leaf and then
# walked into verify-refactor over a dirty tree would be exactly as wrong as one that still
# looped leaves, and a reader repairing either repairs the same section. `problems` says
# which part is missing.
#
# Each probe accepts any wording that carries its fact — how the document phrases it is the
# writer's — but the refusals are asked of the text AROUND their own check rather than of
# the section at large: this section already tells the conductor to stop, to bail and to
# narrate, for the leaf's own exit 2 and for the triage's answers, and a probe that read the
# whole section would be answered by those sentences and pass a document that never says
# what a dirty tree means.
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

plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

refactor_heading='#### Refactor'

flat() {
  plain | tr '\n' ' '
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

# hazard: BSD grep refuses an interval bound over 255.
windows() {
  local radius="${2:-250}"
  grep -oE ".{0,$radius}$1.{0,$radius}" <<<"$section"
}

# hazard: fed by a pipe, head's early exit would hand grep's SIGPIPE up under pipefail.
win() {
  head -1 < <(windows "$@")
}

phrase() {
  head -1 < <(grep -oE "$1" <<<"$2")
}

wins() {
  windows "$@" | tr '\n' ' '
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

  dirty="$(win 'git status --porcelain')"
  if [[ -z "$dirty" ]]; then
    problems+=("$skill_md's Refactor section never asks git status --porcelain, so the conductor walks into verify-refactor over whatever a killed leaf left uncommitted")
  else
    grep -qE "$refusal" <<<"$dirty" ||
      problems+=("$skill_md's Refactor section asks git status --porcelain without saying a non-empty answer stops it, so the check is asked and its answer is advisory")
  fi

  subjects="$(win '(--(format|pretty)=%s|subject)')"
  if [[ -z "$subjects" ]]; then
    problems+=("$skill_md's Refactor section never reads the subjects of the commits since the green commit, so a leaf that committed something other than a refactor: goes to verify-refactor unchallenged")
  else
    grep -qE 'refactor:' <<<"$subjects" ||
      problems+=("$skill_md's Refactor section reads commit subjects without saying they must be refactor:, so what the conductor is checking for is left to judgement")
    grep -qE "$refusal" <<<"$subjects" ||
      problems+=("$skill_md's Refactor section never says a non-refactor: commit since the green commit stops it, so the check has no branch and the run continues either way")
  fi

  counted="$(win 'rev-list --count')"
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
    # The texts are a flag's behaviour; which class of flag is case 7's question, so a plant
    # that hands the amendment to the wrong class fails there and not here too.
    added="$(win "$add_ledger_step")"
    grep -qE "'<[^>]*behaviou?r>'" <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without saying the texts are the flags' behaviours, so what the inserted step says is left to judgement")
    # The anchor is the step's title, spelled `<STEP>` or read out of the ledger (#437).
    grep -qE "after ['\"]?(<step>|\\$\\(\\\$s/next-pending-refactor\\.sh)" <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh without anchoring the insertion after the step just refactored, so the triangulating step lands somewhere other than next to the code it triangulates")
  fi

  cleared="$(win 'clear-refactor-pending\.sh')"
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
  # The claim, found by what it says rather than by where it sits: an exit 1 spoken of in
  # the same clause as the owed steps it files. 120 characters either way is about one
  # clause, which is what keeps this from matching the other two exit 1s this section
  # carries — the rejected push's and the REJECT verdict's, neither of which has the word
  # `owed` anywhere near it.
  owed_claim="$(either_order 'exit 1' 'owed' '.{0,120}')"
  if ! grep -qE "$owed_claim" <<<"$section"; then
    problems+=("$skill_md's Refactor section never says what add-ledger-step.sh exit 1 means, so a conductor meeting the plan-growth budget's refusal is left to read it as the failure every other non-zero exit in this phase is, and the NEW_STEP: values it filed as owed steps go unmentioned")
  else
    # And that the clause does not end the run. The window is the claim with about a clause
    # either side of it, not the section: `win`'s default 250 would reach the REJECT and
    clause="$(win "$owed_claim" 150)"
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
  added="$(win "$add_ledger_step")"
  if [[ -z "$added" ]]; then
    problems+=("$skill_md's Refactor section never runs add-ledger-step.sh, so the verifier's NEW_STEP: proposals are narrated and nothing grows the plan — the edge case it stopped REJECTing for is proposed to nobody")
  else
    grep -qE 'verif|verdict' <<<"$added" ||
      problems+=("$skill_md's Refactor section runs add-ledger-step.sh over the leaf's NEW_STEP: values alone, so the passing verify-refactor verdict's own values never reach the ledger — the unhandled edge case the verifier stopped REJECTing for is proposed to nobody")
  fi
fi

report "$name"

# 6. One criterion — an `overfit` flag is answered inside the step that raised it — and so
#    one case. Issue #175 measured what the absence costs: six `plan: amend` commits on
#    `origin/main` were made from refactor flags, and #107's three ran from 01:31 to past
#    03:06 for three one-line `fix:` commits and seventeen `refactor:` ones, because a step
#    made from a flag has a refactor loop of its own and that loop flagged the next sibling.
#    The flag now carries its class, so `overfit` — the code passes this step's test without
#    implementing the behaviour this step's criterion states — is this step's own debt: one
#    triangulating red and green pair here, and then the refactor loop this step was already
#    in, with what was left of its budget. Its four probes are its parts, and a document
#    missing any one of them routes the flag somewhere it costs a whole step: a pair with no
#    "and no new ledger line" is the amendment this issue is against, and a pair that never
#    comes back is a refactor loop abandoned mid-budget.
#
#    Asked of the text around the word `overfit` rather than of the section at large — the
#    way case 1 asks its refusals — because this section already talks about triangulation,
#    about ledger steps and about what a step owes, and a probe reading the whole of it would
#    be answered by the PASS branch's `add-ledger-step.sh` sentences and pass a document that
#    still turns every flag into a plan amendment.
# The words this document denies with, spelled once for the three probes that ask for one —
# case 6's two and case 8's — the way `refusal` above is spelled once for case 1's two. All
# three owe the same thing beyond the verb or noun each names: that the section says the flag
# does NOT buy it. Two lists for that one question is how they drift — case 8's carried
# `neither` where case 6's carried `without` — and a probe widened on its own then accepts a
# wording the others still reject, leaving the next writer several answers to "what counts as
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
    # a. The pair itself, and that it is verified: a triangulating test written inside the
    #    step is still a red and a green the blind verifiers see, which is what tells this
    #    apart from the leaf hand-generalizing the code it flagged.
    grep -qE "$(either_order 'triangulat[a-z]*' 'verify-(red|green)' '[^.]{0,200}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says an overfit flag is answered by a triangulating red and green pair, so the case the leaf named is either built unverified or not built at all")

    # b. And that the pair is all it is. The whole cost this issue measured is the flag
    #    becoming a ledger step, so a document that runs the pair AND amends the plan has
    #    paid for it twice.
    grep -qE "$denial($amendment)" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the plan does not grow for it, so the triangulation becomes a ledger step with a refactor loop of its own — the #107 chain this issue is against")
    grep -qE "$denial(second )?step.done" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section answers an overfit flag without saying the step is not mirrored done a second time, so one step reports itself finished twice and the issue thread stops saying how many steps ran")

    # c. And that the step goes back to where it was. The refactor loop was interrupted by
    #    the flag, not ended by it, and a loop resumed with a fresh budget would let one flag
    #    buy a second step's worth of transforms.
    grep -qE "$(either_order '(resum|return|back)' 'budget' '[^.]{0,160}')" <<<"$flagged" ||
      problems+=("$skill_md's Refactor section never says the step resumes its own refactor loop with the budget it had left after the triangulation, so the tidying the flag interrupted is either abandoned or restarted with a budget the step has already spent")
  fi
fi

report "$name"

# 7. One criterion — the plan grows from an `uncovered-spec` flag and from no other class —
#    and so one case. The classes the leaf now reports are three, and only one of them is a
#    step the plan is missing: `uncovered-spec` names a behaviour the spec requires that no
#    ledger step covers, which is the gap the planner is already asked to catch at scoping
#    time. `overfit` is this step's own debt (case 6) and `beyond-spec` is not this run's
#    work at all, so a document that amends the plan from a flag without saying which class
#    buys it is the document #175 measured: six `plan: amend` commits on `origin/main`, none
#    of them behaviour the issue's spec asked for. Two probes, because either alone passes a
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

  grown="$(win "$add_ledger_step")"
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
    # a. It is narrated as a follow-up, in the comment the step accounts for itself in.
    grep -qE "$(either_order 'follow.?up' '(🛠️ )?refactor comment|narrat|post' '[^.]{0,200}')" <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never says a beyond-spec flag is narrated as a follow-up in the 🛠️ Refactor comment, so what the leaf found is neither built nor said out loud and the run ends having dropped it")

    # b. And it outlives the run, in the body the human deciding the merge reads.
    grep -qE 'pr body|body of the (draft )?pr|pull request body' <<<"$beyond" ||
      problems+=("$skill_md's Refactor section never carries a beyond-spec flag into the PR body, so the follow-up is buried in one step's comment and the human deciding the merge never sees it")

    # c. And narration is ALL it earns. A flag narrated and also planned has cost exactly
    #    what this issue measured, whatever the comment said about it.
    #
    #    Asked with the denial word ADJACENT to the verb rather than through `$denial`'s
    #    `[^.]{0,80}` gap, which case 6 uses. The gap is right for those two — what
    #    they deny is a noun phrase a writer may put words in front of — but here it reads
    #    the bullet's own rationale instead of its rule: "without costing it a step: one
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
    # a. The ceiling itself: once per step, not once per flag.
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
  grown="$(win "$add_ledger_step")"
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

finish
