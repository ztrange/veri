#!/usr/bin/env bash
# Unit tests for what the conductor does when a step's revise budget runs out — like
# skill-green-split.test.sh and skill-red-untestable.test.sh this suite belongs to no single
# script: its subject is skills/tdd/SKILL.md, read as text, the way the session that follows
# it reads it. Zero-dependency plain-shell asserts, same idiom, picked up by `make test`'s
# glob by existing.
#
# Why this exists (issue #408): exhausting `REVISE_BUDGET` goes straight to a
# `revise-exhausted` bail today, and the step's work is lost — although a step no blind
# verifier can be satisfied about in two attempts is usually a step carrying more than one
# behaviour, the very condition `SPLIT:` exists for. build-develop-prompt.sh now renders an
# `exhausted` phase and exhausted-outcome.sh resolves that leaf's report to one of three
# answers (exit 0 split · 1 needs the user · 3 neither). This suite pins the branch in
# SKILL.md that launches that leaf and acts on those three answers.
#
# Run: scripts/tests/skill-revise-exhausted.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path resolved
# for the probes to read, so a message can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# plain — stdin with emphasis marks and backticks dropped, the case folded and the lines
# joined onto one, because `SPLIT:` and **split** are the same word and a claim that wraps
# across two lines is still one claim.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# The heading the section is found by, spelled once: the probes look for it and the
# fail-closed message names it.
revise_heading='## Revising on a REJECT'

# revise_lines — the raw lines after that heading, up to the next heading of any level.
revise_lines() {
  awk -v h="$revise_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path"
}

# revise_section — those lines normalised through `plain`.
revise_section() {
  revise_lines | plain
}
section="$(revise_section)"

# unreadable — empty unless the section could not be read at all, in which case it is the
# half of the failure message the case would otherwise have to invent. Fail closed rather
# than probing an empty string, which would let "the section is gone" read as "it is right".
unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$revise_heading' section to read —"

# win <text> <extended-regex> — <text> within 250 characters either side of the first match,
# or the empty string when there is none: the text a reader meets while working out what to
# do about that answer. The text it reads is a parameter because the cases below read two of
# them — the whole revise section, and one outcome's bullet sliced out of it — and a second
# spelling of this window is a second place for the bound to be got wrong. 250 rather than a
# rounder, larger number because BSD grep — the one on the development machine this
# repository holds itself portable to — refuses an interval whose bound is over 255.
win() {
  head -1 < <(grep -oE ".{0,250}$2.{0,250}" <<<"$1")
}

# The three things the section is probed for by name, spelled once each for the guard that
# looks for them and the window read around them, the way skill-green-split.test.sh spells its
# own `add-ledger-step.sh` probe: a suite re-pointed at a renamed script or a reworded answer
# cannot then go on telling a reader it searched for both spellings. `$s` and not `$S` because
# `plain` folds the section's case; the `$` and the `.` are escaped because these are extended
# regexes and not paths.
outcome_reader='\$s/exhausted-outcome\.sh'
add_ledger_step='\$s/add-ledger-step\.sh'
needs_user='needs_user|needs-user|needs the user'
# The bail cause the third outcome keeps, likewise spelled once: it is both the token the
# section must still carry and the anchor the window around it is read from.
bail_cause='revise-exhausted'

name="$skill_md's exhausted-budget branch launches the exhausted leaf and acts on exhausted-outcome.sh's three answers: replace the step on a split, park it on needs-user, bail revise-exhausted on neither"
problems=()

if [[ -n "$unreadable" ]]; then
  problems+=("$unreadable what the conductor does when a step's revise budget runs out could not be established")
else
  # 1. The leaf. Without it the last REJECT goes straight to the bail it does today and
  #    nothing ever asks the leaf which of the two conditions the step is in.
  grep -qE '\$s/build-develop-prompt\.sh exhausted' <<<"$section" ||
    problems+=("$skill_md's revise section never builds an exhausted-phase prompt, so a step whose budget ran out is bailed without anything asking whether it should have been split")

  # 2. The reader. The leaf answers in free-form prose around its report lines, and
  #    exhausted-outcome.sh is what resolves that to one of the three outcomes — a
  #    conductor reading the report itself makes the branch a judgement per run.
  if ! grep -qE "$outcome_reader" <<<"$section"; then
    problems+=("$skill_md's revise section never runs exhausted-outcome.sh on the exhausted leaf's report, so which of the three outcomes it reported is decided by reading rather than by exit code")
  else
    outcome="$(win "$section" "$outcome_reader")"
    grep -qE 'exit 0|exits? 0' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 0 is the split, so the conductor cannot tell the split answer from the other two")
    grep -qE 'exit 1|exits? 1' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 1 is the needs-user answer, so a step the leaf escalated is acted on as something else")
    grep -qE 'exit 3|exits? 3' <<<"$outcome" ||
      problems+=("$skill_md's revise section runs exhausted-outcome.sh without saying exit 3 is neither answer, so the outcome that must bail exactly as today has no branch of its own")
  fi

  # 3. The split branch: the criteria the leaf named take the place of the step that could
  #    not be satisfied — `instead-of`, not `before`, because the step itself is what was
  #    wrong — and the run carries on from the first of them.
  if ! grep -qE "$add_ledger_step" <<<"$section"; then
    problems+=("$skill_md's revise section never runs add-ledger-step.sh on a split at exhaustion, so the criteria the leaf named are narrated and the plan the run reads is unchanged")
  else
    added="$(win "$section" "$add_ledger_step")"
    grep -qE 'instead-of' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion with a placement other than instead-of, so the step nothing could satisfy stays in the plan alongside the criteria that replaced it")
    grep -qE 'commit' <<<"$added" ||
      problems+=("$skill_md's revise section grows the ledger at exhaustion without committing it, so the replacement steps are lost the moment the run is resumed from the committed ledger")
    grep -qE 'next-unchecked' <<<"$section" ||
      problems+=("$skill_md's revise section never returns to next-unchecked.sh after replacing the step, so the run does not continue from the first of the criteria it just filed")
  fi

  # 4. The needs-user branch: a leaf that says the step needs a decision the run has no
  #    authority to make is answered by parking the step, not by bailing it as a
  #    methodology failure.
  if ! grep -qE "$needs_user" <<<"$section"; then
    problems+=("$skill_md's revise section never names the needs-user answer, so a leaf that escalates a step to the user is treated as one that volunteered nothing")
  else
    parked="$(win "$section" "$needs_user")"
    grep -qE 'park' <<<"$parked" ||
      problems+=("$skill_md's revise section names the needs-user answer without parking the step on it, so an escalation the leaf made deliberately ends as the same bail as saying nothing")
  fi

  # 5. And the third outcome, unchanged: neither answer is still the bail the section does
  #    today, with the same cause token a human's classification is read from.
  if ! grep -qE "$bail_cause" <<<"$section"; then
    problems+=("$skill_md's revise section no longer names the revise-exhausted cause, so a leaf that volunteered neither answer leaves the conductor to invent a stop for a step it already had one for")
  else
    bailed="$(win "$section" "$bail_cause")"
    grep -qE 'bail' <<<"$bailed" ||
      problems+=("$skill_md's revise section names revise-exhausted without bailing on it, so the outcome that should end the step exactly as today carries on instead")
  fi
fi

report "$name"

# The needs-user branch again, this time for what the user is left with. Parking stops the
# run; unless the stop is written on the issue thread the only account of *why* is a leaf log
# inside a worktree, which is exactly the reading this criterion exists to spare them.
#
# The branch is longer than the 250 characters `win` reads either side of a match, and the
# claim spans the whole of it — the answer file is named at the top of the bullet and the
# park several lines down — so this case slices the bullet itself rather than a window:
# from the line that opens it to the line that opens the next outcome's.
needs_user_open='exit 1 — the step needs the user'
needs_user_close='exit 3'

# needs_user_branch — that slice, normalised through `plain` like the section is. The open
# marker carries its em dash so the one-line summary of all three outcomes above ("exit 1
# the step needs the user and is parked") cannot be mistaken for the branch itself.
needs_user_branch() {
  awk -v o="$needs_user_open" -v c="$needs_user_close" \
    '!inside && index($0, o) { inside = 1 }
     inside && index($0, c) && !index($0, o) { exit }
     inside' "$skill_path" | plain
}
branch="$(needs_user_branch)"

# The mirror, spelled once for the guard and the window both: the two ways this document
# tells the conductor to write on the issue thread — the bare `gh issue comment <n> --body`
# of *Starting*, and the "post a `### …` comment" every narration section uses.
issue_mirror='gh issue comment|post a [^.]{0,120}comment'

# The claim both fail-closed messages end in, spelled once: the two ways this case can fail
# to read anything — no section at all, or a section with no such branch — leave the reader
# with the same thing unestablished, and a second spelling is one that can drift from it.
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
    posted="$(win "$branch" "($issue_mirror)")"
    grep -qE 'exhausted-answer' <<<"$posted" ||
      problems+=("$skill_md's needs-user branch posts to the issue thread without carrying .tdd/exhausted-answer.txt, so the user reads that the step was parked and never the leaf's own account of why")
    grep -qE 'reason' <<<"$posted" ||
      problems+=("$skill_md's needs-user branch posts to the issue thread without carrying the verifier's last rejection reason, so the user is asked to decide about a step without the objection that stopped it")
  fi
fi

report "$name"

# The step budget (#451), whose crossing is answered by a leaf built on the exhausted one's
# pattern. step-cost.sh (#448), step-budget.sh (#449) and the over-budget prompt (#450) exist,
# and nothing calls them: a step is only ever stopped at its budget if the procedure asks
# step-cost.sh after each leaf that runs before the step's green commit — after that commit
# there is nothing left for a crossing to change.

# The cost check, spelled once for the probe and the message both.
step_cost='step-cost.sh'

# after_wait <leaf> — the raw lines after `wait-leaf.sh <leaf>` (the leaf has exited), up to
# the next leaf launched (`detach-leaf.sh`) or the green commit's tick (`tick-ledger.sh`),
# whichever comes first: what the conductor does between this leaf's answer and the next thing
# that spends money or closes the step. Empty when the document never waits on that leaf.
after_wait() {
  awk -v w="wait-leaf.sh $1" \
    '!inside && index($0, w) { inside = 1; next }
     inside && (index($0, "detach-leaf.sh") || index($0, "tick-ledger.sh")) { exit }
     inside' "$skill_path"
}

# The five leaves that run before a step's green commit, by the name each is waited on under.
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

# The shared revise block serves red, green and refactor alike, and only the first two run
# before the green commit, so its cost check must be skipped for a refactor-phase revise. An
# inline comment in the fenced command is the only place that said so; a conductor reading
# the section's prose is told nothing, so the rule has to be a sentence of that prose.

# Naming step-cost.sh, refactor and a negation is not yet the rule: "step-cost.sh is not
# refactor-safe" holds all three and never says when the check does run. So the same sentence
# must also state the condition — the phase being revised is red or green.

# revise_prose_sentences — the revise section with its fenced blocks dropped, normalised
# through `plain`, one sentence per line: what the section says outside its commands.
revise_prose_sentences() {
  revise_lines |
    awk '/^[[:space:]]*```/ { fenced = !fenced; next } !fenced' |
    plain |
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

# The other half of the placement: the leaves after the green commit — the refactor leaf and
# its blind verifier — are followed by no cost check, and the check's own section says why, so
# a reader who notices the gap does not "fix" it by adding one.

# The heading the cost check's section is found by, spelled once for the probe and the message.
cost_heading="#### The step's cost check"

# cost_check_lines — that section's raw lines, up to the next heading of level two to four:
# the commands are probed as written, `$S` and all, and a sub-heading inside the section does
# not end it.
cost_check_lines() {
  awk -v h="$cost_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^(##|###|####) / { exit } inside' "$skill_path"
}

# cost_check_sentences — those lines normalised through `plain`, one sentence per line.
cost_check_sentences() {
  cost_check_lines |
    plain |
    awk '{ n = split($0, s, /[.!?] /); for (i = 1; i <= n; i++) print s[i] }'
}

# The two leaves that run after a step's green commit, by the name each is waited on under.
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

# When in a leaf's life the check runs: only once that leaf has exited and supervise.sh has
# harvested its `usage` event, which step-cost.sh sums — a check run while the leaf is still
# going, or before its accounting is on disk, reads a figure short of what the step has spent.

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

# How often the check fires: at most once per step. Once its crossing branch has run, the
# check is disarmed for the rest of the step and nothing re-arms it, so a step that goes on to
# cost three times its budget is not asked about again at every remaining leaf.

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

# What exit 3 means: step-cost.sh exits 3 when no leaf of this step has reported a usage
# event yet, and that is nothing to act on — not a crossing, so the branch does not run.

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

# The crossing branch: on a crossing the run asks one leaf what to do, built on the exhausted
# leaf's pattern — the `over-budget` prompt, launched through supervise.sh like every other
# leaf so stuck-detection still covers it, and its prose answer resolved by
# exhausted-outcome.sh to an exit code rather than read and judged per run.

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

# The over-budget leaf's split (exit 0), which is the revise-exhausted path's split exactly:
# the step's uncommitted work is thrown away first, so it cannot become the first replacement
# step's inherited start; the criteria replace the step in ONE add-ledger-step.sh call, so
# VERI_STEP_GROWTH is spent on them all or on none; and the ledger is committed before the run
# goes on, because the committed ledger is what a resumed run reads.

# first_line <fixed-string> — the number of the first line of the cost check's section that
# holds <fixed-string>, or nothing when none does: the order the branch's commands are written
# in is the order the conductor runs them in.
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

# The over-budget split meets the same growth budget the other two plan-growing paths do:
# add-ledger-step.sh exit 1 (VERI_STEP_GROWTH reached) is a step-too-big bail, as it already is
# for a Green leaf's volunteered split and the revise-exhausted split — all three are plan
# growth, so none of them may grow the plan past that budget.

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

# The over-budget leaf's exit 1: the step needs the user. Parked — the run stops there, with
# the leaf's answer and the two figures that made it a crossing (what the step has spent, and
# the step budget) in hand, and the plan left as it is so the user's decision picks the run
# back up — the same park the revise-exhausted path takes.

# over_budget_exit <code> — the cost check section's `exit <code>` bullet, from its own line
# up to the first line that is not indented under it, normalised through `plain`.
over_budget_exit() {
  cost_check_lines |
    awk -v code="$1" '$0 ~ "^- \\*\\*exit " code { inside = 1; print; next } inside && !/^  / { exit } inside' |
    plain
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

# The over-budget leaf's exit 3: neither answer. This is where the over-budget path parts
# from the revise-exhausted one, whose exit 3 bails as a process failure. Here nothing has
# failed — every verdict may be a PASS and the step is merely dear — so the crossing is
# recorded and the step goes on to finish, and the bullet says so in so many words: not a bail,
# and why.

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

# Why a crossing is not a failure, stated once: the exit branches above each act on it, but a
# reader should not have to derive from them that an expensive step has not failed, nor that
# the check leaves every script's exit code meaning what it already meant — 1 is still a
# process failure, 2 still a system one, 3 still nothing to do.

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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
