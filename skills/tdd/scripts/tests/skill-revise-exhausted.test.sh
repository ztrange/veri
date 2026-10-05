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

name="$skill_md's exhausted-budget branch launches the exhausted leaf and acts on exhausted-outcome.sh's three answers: replace the step on a split, park it on needs-user, bail revise-exhausted on neither"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does when a step's revise budget runs out could not be established")
else
  grep -qE '\$s/build-develop-prompt\.sh exhausted' <<<"$section" ||
    problems+=("$skill_md's revise section never builds an exhausted-phase prompt, so a step whose budget ran out is bailed without anything asking whether it should have been split")

  if ! grep -qE "$outcome_reader" <<<"$section"; then
    problems+=("$skill_md's revise section never runs exhausted-outcome.sh on the exhausted leaf's report, so which of the three outcomes it reported is decided by reading rather than by exit code")
  else
    outcome="$(window "$section" "$outcome_reader")"
    grep -qE 'exit 0|exits? 0' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 0 is the split, so the conductor cannot tell the split answer from the other two")
    grep -qE 'exit 1|exits? 1' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 1 is the needs-user answer, so a step the leaf escalated is acted on as something else")
    grep -qE 'exit 3|exits? 3' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 3 is neither answer, so the outcome that must bail exactly as today has no branch of its own")
  fi

  if ! grep -qE "$add_ledger_step" <<<"$section"; then
    problems+=("$skill_md's revise section never runs add-ledger-step.sh on a split at exhaustion, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  else
    added="$(window "$section" "$add_ledger_step")"
    grep -qE 'instead-of' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion with a placement other than instead-of, so the step nothing could satisfy stays in the plan alongside the criteria that replaced it")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion without committing it, so the replacement steps are lost the moment the run is resumed from the committed ledger")
    grep -qE 'next-unchecked' <<<"$section" ||
      problems+=("$skill_md's revise section never returns to next-unchecked.sh after replacing the step, so the run does not continue from the first of the criteria it just filed")
  fi

  if ! grep -qE "$needs_user" <<<"$section"; then
    problems+=("$skill_md's revise section never names the needs-user answer, so a leaf that escalates a step to the user is treated as one that volunteered nothing")
  else
    parked="$(window "$section" "$needs_user")"
    grep -qE 'park' <<<"$parked" ||
      problems+=("$skill_md's revise section names the needs-user answer without parking the step on it, so an escalation the leaf made deliberately ends as the same bail as saying nothing")
  fi

  if ! grep -qE "$bail_cause" <<<"$section"; then
    problems+=("$skill_md's revise section no longer names the revise-exhausted cause, so a leaf that volunteered neither answer leaves the conductor to invent a stop for a step it already had one for")
  else
    bailed="$(window "$section" "$bail_cause")"
    grep -qE 'bail' <<<"$bailed" ||
      problems+=("$skill_md's revise section names revise-exhausted without bailing on it, so the outcome that should end the step exactly as today carries on instead")
  fi
fi

report "$name"

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

name="$skill_md's needs-user branch mirrors the parked step to the issue thread, carrying the leaf's answer and the verifier's last rejection reason"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable $unestablished")
elif [[ -z "${branch// /}" ]]; then
  problems+=("$skill_md's revise section has no '$needs_user_open' branch to read — $unestablished")
else
  if ! grep -qE "($issue_mirror)" <<<"$branch"; then
    problems+=("$skill_md's needs-user branch parks the step without posting anything to the issue thread, so the one account of why the run stopped is a leaf log inside a worktree")
  else
    posted="$(window "$branch" "($issue_mirror)")"
    grep -qE 'exhausted-answer' <<<"$posted" ||
      problems+=("$skill_md's needs-user branch posts to the issue thread without carrying .tdd/exhausted-answer.txt, so the user reads that the step was parked and never the leaf's own account of why")
    grep -qE 'reason' <<<"$posted" ||
      problems+=("$skill_md's needs-user branch posts to the issue thread without carrying the verifier's last rejection reason, so the user is asked to decide about a step without the objection that stopped it")
  fi
fi

report "$name"

step_cost='step-cost.sh'

after_wait() {
  awk -v w="wait-leaf.sh $1" \
    '!inside && index($0, w) { inside = 1; next }
     inside && (index($0, "detach-leaf.sh") || index($0, "tick-ledger.sh")) { exit }
     inside' "$skill_path"
}

pre_commit_leaves=(develop-red verdict-red 'revise-<phase>-<k>' develop-green verdict-green)

name="$skill_md checks $step_cost after develop-red, verify-red, each revise attempt, develop-green and verify-green, before the next leaf launches or the green commit ticks"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — where the cost check runs could not be established")
else
  for leaf in "${pre_commit_leaves[@]}"; do
    window="$(after_wait "$leaf")"
    if [[ -z "${window//[[:space:]]/}" ]]; then
      problems+=("$skill_md never waits on $leaf, or launches the next leaf straight after it — where its cost check would go could not be established")
    elif ! grep -F -- "$step_cost" > /dev/null <<<"$window"; then
      problems+=("$skill_md runs no $step_cost between $leaf exiting and the next leaf's launch or the green commit, so a step that crossed its budget on $leaf spends on without anything asking")
    fi
  done
fi

report "$name"

revise_prose_sentences() {
  revise_lines |
    awk '/^[[:space:]]*```/ { fenced = !fenced; next } !fenced' |
    plain --join |
    awk '{ n = split($0, s, /[.!?] /); for (i = 1; i <= n; i++) print s[i] }'
}

name="$skill_md says in the prose of '$revise_heading', not only in an inline comment, that the revise block runs $step_cost only when the phase is red or green, never for a refactor-phase revise"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the revise block says about its cost check could not be established")
elif ! revise_prose_sentences |
  grep -F -- "$step_cost" | grep -F -- 'refactor' |
  grep -E -- "(^|[^a-z])(never|not|no)([^a-z]|$)|n't" |
  grep -E -- "red or green|red or the green|red and green" > /dev/null; then
  problems+=("no sentence of '$revise_heading' outside its fenced commands names $step_cost and refactor together, says the check does not run for a refactor-phase revise and states that it runs when the phase is red or green — the red-or-green-only rule lives only in an inline comment")
fi

report "$name"

cost_heading="#### The step's cost check"

cost_check_lines() {
  awk -v h="$cost_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^(##|###|####) / { exit } inside' "$skill_path"
}

cost_check_sentences() {
  cost_check_lines |
    plain --join |
    awk '{ n = split($0, s, /[.!?] /); for (i = 1; i <= n; i++) print s[i] }'
}

post_commit_leaves=(develop-refactor verdict-refactor)

name="$skill_md checks $step_cost after neither develop-refactor nor verify-refactor, and '$cost_heading' says why no check follows the green commit"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — where the cost check does not run could not be established")
else
  for leaf in "${post_commit_leaves[@]}"; do
    if ! grep -F -- "wait-leaf.sh $leaf" "$skill_path" > /dev/null; then
      problems+=("$skill_md never waits on $leaf — whether a cost check follows it could not be established")
    elif grep -F -- "$step_cost" > /dev/null <<<"$(after_wait "$leaf")"; then
      problems+=("$skill_md runs $step_cost after $leaf, which runs after the step's green commit, where a crossing can change nothing")
    fi
  done
  cost_check_sentences |
    grep -F -- 'after the green commit' |
    grep -E -- "(^|[^a-z])(none|no|never|not)([^a-z]|$)" |
    grep -F -- 'refactor' |
    grep -E -- "(^|[^a-z])(because|since|so|by then)([^a-z]|$)" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says that no cost check follows a leaf after the green commit, names the refactor loop, and gives the reason")
fi

report "$name"

name="'$cost_heading' says the check runs only once the leaf has exited and its usage event has been harvested"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — when the cost check runs could not be established")
else
  cost_check_sentences |
    grep -F -- 'harvest' |
    grep -F -- 'usage' |
    grep -E -- "(^|[^a-z])exited([^a-z]|$)" |
    grep -E -- "(^|[^a-z])(once|only|after)([^a-z]|$)" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says the check runs only once the leaf has exited and its usage event has been harvested")
fi

report "$name"

name="'$cost_heading' says the check fires at most once per step and is not re-armed"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — how often the cost check fires could not be established")
else
  cost_check_sentences |
    grep -F -- 'at most once per step' > /dev/null ||
    problems+=("no sentence of '$cost_heading' says the check fires at most once per step")
  cost_check_sentences |
    grep -F -- 're-arm' |
    grep -E -- "(^|[^a-z])(not|never|no|nothing)([^a-z]|$)" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says the check is not re-armed once its branch has run")
fi

report "$name"

name="'$cost_heading' says $step_cost exit 3 (no leaf of the step has reported yet) is not a crossing"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what $step_cost exit 3 means could not be established")
else
  exit_3_sentences="$(cost_check_sentences | grep -F -- 'exit 3')"
  grep -F -- 'not a crossing' <<<"$exit_3_sentences" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says $step_cost exit 3 is not a crossing")
  grep -E -- 'no leaf .*(reported|usage)' <<<"$exit_3_sentences" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says exit 3 means no leaf of the step has reported yet")
fi

report "$name"

name="'$cost_heading' builds the over-budget prompt, launches its leaf through supervise.sh, and reads its answer with exhausted-outcome.sh, never by eye"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — how a crossing is answered could not be established")
else
  lines="$(cost_check_lines)"
  grep -F -- 'build-develop-prompt.sh over-budget' <<<"$lines" > /dev/null ||
    problems+=("'$cost_heading' never builds an over-budget prompt, so a crossing asks no leaf what to do about it")
  launch="$(grep -F -- 'detach-leaf.sh $S/supervise.sh' <<<"$lines" | grep -F -- 'over-budget')"
  if [[ -z "$launch" ]]; then
    problems+=("'$cost_heading' never launches an over-budget leaf through detach-leaf.sh \$S/supervise.sh, the way the exhausted leaf is launched")
  else
    leaf="$(head -1 < <(sed -E 's/.*supervise\.sh ([^ ]+).*/\1/' <<<"$launch"))"
    grep -F -- "wait-leaf.sh $leaf" <<<"$lines" > /dev/null ||
      problems+=("'$cost_heading' launches $leaf but never waits on it with wait-leaf.sh")
    grep -F -- "exhausted-outcome.sh < .tdd/$leaf.out" <<<"$lines" > /dev/null ||
      problems+=("'$cost_heading' never reads $leaf's answer with exhausted-outcome.sh < .tdd/$leaf.out, so which answer it gave is a judgement made per run")
  fi
  if grep -F -- 'run-leaf.sh' <<<"$lines" | grep -vF -- 'supervise.sh' > /dev/null; then
    problems+=("'$cost_heading' launches a leaf with run-leaf.sh outside supervise.sh, so nothing watches it for being stuck")
  fi
  cost_check_sentences |
    grep -F -- 'by eye' |
    grep -E -- "(^|[^a-z])(never|not)([^a-z]|$)" > /dev/null ||
    problems+=("no sentence of '$cost_heading' says the over-budget leaf's answer is read with the script, never by eye")
fi

report "$name"

first_line() {
  head -1 < <(cost_check_lines | grep -nF -- "$1" | cut -d: -f1)
}

name="'$cost_heading' on the over-budget split restores the tree (git reset --hard HEAD, git clean -f -- <test-path>), then grows the plan in one add-ledger-step.sh instead-of call, then commits it before the run goes on"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the over-budget split does could not be established")
else
  reset_at="$(first_line 'git reset --hard HEAD')"
  clean_at="$(first_line 'git clean -f -- <test-path>')"
  grow_lines="$(cost_check_lines | grep -nF -- '$S/add-ledger-step.sh' | grep -F -- 'instead-of' | cut -d: -f1)"
  grow_calls="$(grep -c . <<< "$grow_lines")"
  grow_at="$(head -1 <<< "$grow_lines")"
  commit_at="$(first_line 'git commit')"
  [[ -n "$reset_at" ]] ||
    problems+=("'$cost_heading' never runs git reset --hard HEAD, so the over-budget split grows the plan on top of the step's uncommitted work")
  [[ -n "$clean_at" ]] ||
    problems+=("'$cost_heading' never runs git clean -f -- <test-path>, so the untracked test file Red created survives the over-budget split")
  if [[ "$grow_calls" -ne 1 ]]; then
    problems+=("'$cost_heading' runs add-ledger-step.sh instead-of $grow_calls times, not once, so the over-budget split does not replace the step in one call")
  else
    [[ -n "$reset_at" && -n "$clean_at" && "$reset_at" -lt "$grow_at" && "$clean_at" -lt "$grow_at" ]] ||
      problems+=("'$cost_heading' grows the plan before restoring the tree (reset at line '${reset_at}', clean at '${clean_at}', add-ledger-step.sh at '${grow_at}')")
    [[ -n "$commit_at" && "$commit_at" -gt "$grow_at" ]] ||
      problems+=("'$cost_heading' never commits the plan after add-ledger-step.sh instead-of (commit at line '${commit_at}', add-ledger-step.sh at '${grow_at}'), so a resumed run reads the plan without the replacement steps")
  fi
fi

report "$name"

name="'$cost_heading' says that add-ledger-step.sh exit 1 on the over-budget split is a bail with cause step-too-big"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the over-budget split does when the plan may not grow could not be established")
elif ! cost_check_sentences |
  grep -F -- 'add-ledger-step.sh exit 1' |
  grep -F -- 'step-too-big' |
  grep -E -- "(^|[^a-z])bail" > /dev/null; then
  problems+=("no sentence of '$cost_heading' names add-ledger-step.sh exit 1 and a step-too-big bail together, so what the over-budget split does when VERI_STEP_GROWTH refuses the insertion is left to the reader")
fi

report "$name"

over_budget_exit() {
  cost_check_lines |
    awk -v code="$1" '$0 ~ "^- \\*\\*exit " code { inside = 1; print; next } inside && !/^  / { exit } inside' |
    plain --join
}

name="'$cost_heading' parks the step on the over-budget leaf's exit 1, carrying the leaf's answer and the spent and budget figures, and leaves the plan unchanged"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the over-budget leaf's exit 1 does could not be established")
else
  bullet="$(over_budget_exit 1)"
  if [[ -z "${bullet// /}" ]]; then
    problems+=("'$cost_heading' has no **exit 1** bullet, so what the run does when the over-budget leaf says the step needs the user is left to the reader")
  else
    grep -E -- "(^|[^a-z])park" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 1 bullet never parks the step")
    grep -E -- "over-budget-answer\.txt|leaf's answer" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 1 bullet does not carry the leaf's answer (.tdd/over-budget-answer.txt)")
    grep -E -- "(^|[^a-z])spent" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 1 bullet does not carry what the step has spent")
    grep -E -- "step[- ]budget" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 1 bullet does not carry the step budget")
    grep -E -- "plan[^.]*(as it is|unchanged)" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 1 bullet does not say the plan is left as it is")
  fi
fi

report "$name"

name="'$cost_heading' records the crossing and continues the step on the over-budget leaf's exit 3, and says it is not a bail because nothing has failed"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the over-budget leaf's exit 3 does could not be established")
else
  bullet="$(over_budget_exit 3)"
  if [[ -z "${bullet// /}" ]]; then
    problems+=("'$cost_heading' has no **exit 3** bullet, so what the run does when the over-budget leaf gives neither answer is left to the reader")
  else
    grep -E -- "record[a-z]* the crossing" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 3 bullet does not record the crossing")
    grep -E -- "(carr(y|ies) on|continues?|goes on|finish(es)?)[^.]*step|step[^.]*(carr(y|ies) on|continues|goes on|finishes)" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 3 bullet does not say the step continues")
    grep -E -- "not a bail" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 3 bullet does not say in so many words that it is not a bail")
    grep -E -- "nothing has failed|not a failure" <<<"$bullet" > /dev/null ||
      problems+=("'$cost_heading''s exit 3 bullet does not say why it is not a bail: nothing has failed")
  fi
fi

report "$name"

name="'$cost_heading' states once why a crossing is not a failure, and that no exit code changes meaning"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what the section says a crossing is could not be established")
else
  not_failure="$(cost_check_sentences |
    grep -F -- 'crossing' |
    grep -E -- "not a failure" |
    grep -E -- "(^|[^a-z])(because|since)([^a-z]|$)")"
  not_failure_count="$(grep -c . <<<"$not_failure")"
  if [[ "$not_failure_count" -eq 0 ]]; then
    problems+=("no sentence of '$cost_heading' says a crossing is not a failure and gives the reason")
  elif [[ "$not_failure_count" -gt 1 ]]; then
    problems+=("'$cost_heading' says why a crossing is not a failure in $not_failure_count sentences, not once")
  fi
  cost_check_sentences |
    grep -F -- 'exit code' |
    grep -E -- "(^|[^a-z])(no|none|nor|never|not)([^a-z]|$)" |
    grep -F -- 'mean' > /dev/null ||
    problems+=("no sentence of '$cost_heading' says that no exit code changes meaning")
fi

report "$name"

supervisor_exit_2() {
  cost_check_lines |
    awk 'BEGIN { RS = "" } { p = $0; gsub(/[*`]/, "", p); if (tolower(p) ~ /supervisor exit 2/) print }' |
    plain --join
}

name="'$cost_heading' says a supervisor exit 2 on the over-budget leaf is a killed-stuck bail, and the step's budget stays crossed rather than re-arming"
problems=()

if [[ ! -r "$skill_path" ]]; then
  problems+=("$skill_md could not be read — what a supervisor exit 2 on the over-budget leaf does could not be established")
else
  paragraph="$(supervisor_exit_2)"
  if [[ -z "${paragraph// /}" ]]; then
    problems+=("'$cost_heading' has no paragraph naming a supervisor exit 2, so what the run does when the over-budget leaf never answers is left to the reader")
  else
    grep -F -- 'killed-stuck' <<<"$paragraph" > /dev/null ||
      problems+=("'$cost_heading''s supervisor exit 2 paragraph does not name the killed-stuck cause")
    grep -E -- "(^|[^a-z])bail" <<<"$paragraph" > /dev/null ||
      problems+=("'$cost_heading''s supervisor exit 2 paragraph does not say the step is bailed")
    grep -E -- "(stays|remains) crossed|(not|never|no|nothing)[^.]*re-arm" <<<"$paragraph" > /dev/null ||
      problems+=("'$cost_heading''s supervisor exit 2 paragraph does not say the step's budget stays crossed rather than re-arming")
  fi
fi

report "$name"

name="#880: $skill_md's '$revise_heading' covers the diff phase: the revise leaf is built with revise diff, the re-verify is the blind diff verifier against the same base sha as the original verify-diff verdict, and its PASS is ticked as the ⟦diff-checked⟧ PASS bullet describes"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable how a REJECT on a ⟦diff-checked⟧ step is revised could not be established")
else
  grep -F -- '$s/build-develop-prompt.sh revise diff' <<<"$section" > /dev/null ||
    problems+=("$skill_md's revise section never builds the revise leaf with build-develop-prompt.sh revise diff, so a REJECT on a ⟦diff-checked⟧ step has no revise leaf to launch")
  if ! grep -E -- 'run-verdict\.sh [^|]* diff [^|]*<base-sha>' <<<"$section" > /dev/null; then
    problems+=("$skill_md's revise section never re-verifies a diff revise with run-verdict.sh ... diff ... <base-sha>, so the blind diff verifier is not what judges the revised work")
  fi
  revise_prose_sentences |
    grep -E -- 'verify-diff|verdict-diff' |
    grep -F -- 'same' |
    grep -F -- 'base' > /dev/null ||
    problems+=("no sentence of '$revise_heading' says the diff re-verify runs against the same base sha as the original verify-diff verdict")
  revise_prose_sentences |
    grep -F -- '⟦diff-checked⟧' |
    grep -F -- 'pass' |
    grep -F -- 'tick' > /dev/null ||
    problems+=("no sentence of '$revise_heading' says a recovered diff PASS is ticked as the ⟦diff-checked⟧ PASS bullet describes")
fi

report "$name"

name="#880: $skill_md's '$revise_heading' re-verifies a diff revise with both base shas the original verify-diff verdict ran against: run-verdict.sh --step \"<STEP>\" diff <spec-file> <branch-base-sha> <step-base-sha>, the step base sha the one recorded before the step's develop-diff leaf"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable which base shas a diff revise is re-verified against could not be established")
else
  grep -E -- 'run-verdict\.sh --step "<step>" (--fast-cmd [^ ]+ )?diff <spec-file> <branch-base-sha> <step-base-sha>' <<<"$section" > /dev/null ||
    problems+=("$skill_md's revise section never re-verifies a diff revise with run-verdict.sh --step \"<STEP>\" diff <spec-file> <branch-base-sha> <step-base-sha>, so the re-verify does not get the two base shas verify-diff takes")
  revise_prose_sentences |
    grep -F -- 'step base sha' |
    grep -F -- 'develop-diff' |
    grep -E -- 'record|before' > /dev/null ||
    problems+=("no sentence of '$revise_heading' says the step base sha is the one recorded before the step's develop-diff leaf")
fi

report "$name"

finish
