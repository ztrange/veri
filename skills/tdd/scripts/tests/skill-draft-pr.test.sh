#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do at the draft PR step,
# and wherever else it pushes the branch, read as text.
#
# Contract under test:
#   1. No instruction of SKILL.md's `### 4. Draft PR` step pushes the branch: it readies a PR
#      whose branch is already on the remote. Which PR commands the step runs is case 10's.
#   2. SKILL.md's Green PASS and verify-refactor PASS branches each run `push-branch.sh`,
#      so the branch reaches the remote at both of the points that write the ledger.
#   3. SKILL.md's Draft PR step names `detect-test-command.sh --tier all`'s command, run
#      exactly once, as the branch's only full-suite gate.
#   4. SKILL.md's Draft PR step answers a red result on that full run by adding a repair step
#      to the ledger rather than bailing; the same step says a unit-tier test is added when
#      the failure exposes a gap, and that the verifier judges the fix against the full
#      command.
#   5. SKILL.md's Draft PR step bails on a second red result on the full run after a repair
#      step, naming every suite still red rather than only the first.
#   6. SKILL.md's Draft PR step puts `refactor-owed.sh render`'s output in the PR body, from
#      the run's own owed file, and omits the section when that render exits 3.
#   7. SKILL.md's Draft PR step copies the ledger's `## Owed steps` bullets into the PR
#      body under a `## Owed steps` heading of its own.
#   8. SKILL.md's `### 2. Scope & plan` step pushes the branch and opens the draft PR —
#      `Closes #<n>` in the body, a title marking the work in progress — after the plan
#      commit and before the Plan comment.
#   9. SKILL.md's Green PASS branch, the one place a step is ticked, edits the PR body with
#      the done-of-total step count read from the run's ledger.
#  10. SKILL.md's Draft PR step creates no PR: it retitles the open one, rewrites its body
#      and marks it ready for review.
#  11. SKILL.md's `## Resume` section reuses the open PR its branch already carries and never
#      opens a second one.
#  12. SKILL.md's `## Bailing` section leaves that PR open carrying the bail diagnostic —
#      it neither closes it nor still says to open none.
#  13. SKILL.md's step 1.2 no longer explains the pid lock by saying the draft PR is opened
#      once every step is green.
#  14. SKILL.md's Draft PR step runs `rebase-onto-default.sh` after its dirty-tree and
#      pending-refactor check and before the `done` mark, the metrics commit and
#      `gh pr ready`; its exit 3 continues unchanged and its exit 2 bails with `no-verdict`.
#  15. SKILL.md's Draft PR step, after a rebase that changed the tree, runs the full test
#      command once on the rebased tip, bails on red with the PR left a draft, and on green
#      pushes with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare
#      force.
#  16. SKILL.md's Draft PR step, on `rebase-onto-default.sh` exit 1, launches a develop-rebase
#      leaf through `supervise.sh`, then a blind verify-rebase through `run-verdict.sh`, revises
#      on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS.
#  17. SKILL.md's Draft PR step, on a conflicted rebase not resolved within budget — a
#      `REBASE: FAILED`, `REVISE_BUDGET` exhausted, or a killed leaf — resets the branch to
#      `<pre-rebase-sha>`, leaves the PR a draft and bails with a comment naming every
#      conflicting file.
#  18. SKILL.md's Draft PR step, after `gh pr ready`, waits on `wait-ci.sh` and then
#      reads the readied PR's statusCheckRollup fail-closed: an empty rollup is never a pass, and a conclusion other than SUCCESS,
#      NEUTRAL or SKIPPED counts as failed.
#  19. SKILL.md's Draft PR step never counts a pending check as green, and bounds its CI
#      wait: a check still pending when the bound runs out bails with a cause
#      `classify-bail.sh` classifies.
#  20. SKILL.md's Draft PR step bounds the command that waits on the readied PR's checks
#      itself: `wait-ci.sh` with no max-seconds, or one under a tool call's 600, and no
#      `gh pr checks` after `gh pr ready`.
#  21. SKILL.md's Draft PR step waits on the readied PR's checks and reads their rollup before
#      the `done` mark and the `metrics:` commit, so a red CI result or a `ci-timeout` bail is
#      never reached by a run that already recorded itself done.
#  22. SKILL.md's Draft PR command block itself bails with cause `ci-timeout` on `wait-ci.sh`'s
#      exit 2, between the wait and the `done` mark, and its prose says so.
#  23. SKILL.md's Draft PR step answers a failed CI check by reading `gh run view --log-failed`,
#      appending a repair step that quotes the failing suite and its `FAIL -` line, committing
#      it and returning to the cycle loop, all before the `done` mark.
#  24. SKILL.md's Draft PR step bails on a second red CI result after a CI repair step: its
#      command block runs a bail between the `--log-failed` read and the `done` mark, with a
#      cause `classify-bail.sh` maps to `system` or `process`, and its prose says so.
#  25. SKILL.md's Draft PR step waits on CI by calling `wait-ci.sh` after `gh pr ready` and
#      again on its exit 3, with no wait loop inside one command block and no pending test
#      that reads `.status` alone.
#  26. SKILL.md's Draft PR step stops at a `ci-timeout` or `ci-red` bail: neither the `done`
#      mark nor the `metrics:` commit follows the bail in its command block, and its prose
#      sends the run to *Bailing*.
#  27. SKILL.md's Draft PR step appends its CI repair step with a `⟦ci-repair⟧` text and
#      recognises a second red by that mark on a ledger line, not by the repair step's prose.
#  28. SKILL.md's Draft PR step leaves no CI run on the readied PR that nothing reads: every push
#      its command lines make after the first `wait-ci.sh` call has a `wait-ci.sh` call after
#      it.
#  29. SKILL.md's Draft PR step passes every `wait-ci.sh` call the sha it just pushed, read
#      with `git rev-parse HEAD` after its last push, as the head it waits for.
#  30. SKILL.md's Draft PR step bails on the `metrics:` push's CI wait with a command in its
#      block — `ci-red` on exit 1, `ci-timeout` on exit 2 — not only in prose.
#  31. SKILL.md reads the default branch, reads and comments on the issue, and creates, views,
#      edits, readies and comments on the PR without `gh repo view`, `gh issue view|comment`
#      or `gh pr create|view|edit|ready|comment`: it readies the PR through lib/github.sh's
#      `gh_pr_ready` and reaches the rest through `gh api`, reading REST's `default_branch`.
#  32. SKILL.md's Draft PR step calls `wait-ci.sh` with no fixed total-seconds, and its prose
#      states the bound's rule — twice the mean of the last 5 completed CI runs, capped at 10
#      minutes, 540 s fallback — rather than a number standing for it.
#  33. SKILL.md's Draft PR step answers a red full run with an `add-ledger-step.sh` command
#      appending a repair step marked `⟦suite-repair⟧` that names the failing suite and its
#      `FAIL -` line, then a `git add` and `git commit` of the ledger.
#  34. SKILL.md's Draft PR step bails on a second red full run with a command keyed on a
#      `⟦suite-repair⟧` line already in the ledger, and still names every suite still red.
#  35. SKILL.md's Draft PR step keys its `ci-red` bail on `⟦ci-repair⟧` only, and states that a
#      ledger holding a `⟦suite-repair⟧` step and no `⟦ci-repair⟧` step still gets its one CI
#      repair attempt.
#  36. SKILL.md's Draft PR step's full-run paragraph says the repair step's text lists every
#      suite the full run left red, each with its first `FAIL -` line, that the prompts take
#      that list from the step text through their templates, and that the conductor never
#      edits a built prompt.
#  37. SKILL.md's Draft PR step says the branch's own full run, and any `⟦suite-repair⟧` step
#      it adds, finishes green before `rebase-onto-default.sh` runs.
#  38. SKILL.md's Draft PR step never calls the branch's own full run the only full-suite run,
#      and names the rebased tip's run as the extra run a rebase owes, not a replacement for it.
#  39. SKILL.md's Draft PR step bails on a red rebased tip with cause `rebased-tip-red`, never
#      `suite-red`, after a clean rebase and after a verified conflict resolution alike.
#  40. SKILL.md's bail on a red rebased tip runs `git reset --hard <pre-rebase-sha>` before
#      *Bailing*'s push.
#  41. SKILL.md's bail on a red rebased tip after a verified conflict resolution also runs
#      `git reset --hard <pre-rebase-sha>` before *Bailing*'s push.
#  42. SKILL.md's Guardrails invariant about opening the PR says neither "exactly once" nor
#      "the only full-suite gate".
#  43. SKILL.md's Guardrails invariant about opening the PR names both runs at the Draft PR
#      step: the branch's own full run, again after each `⟦suite-repair⟧` step, and the extra
#      run on the rebased tip when sub-step 1 rebased the branch.
#  44. SKILL.md's `ci-red` bail names each failed CI check: every `cause=ci-red` bail line in the
#      Draft PR step carries a field read from the head's check runs, and `## Bailing`'s
#      `### ⛔ Bailed` comment says a `ci-red` bail names each check that failed.
#
# Run: scripts/tests/skill-draft-pr.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/first-record.sh"

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

section_lines() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path"
}

section_records() { section_lines "$1" "$2" | records_of; }

section_or_problem() {
  section_heading="$1" section_closer="$2"
  records="$(section_records "$1" "$2")"
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no $1 section to read — $3 could not be checked")
  return 1
}

step_or_problem() { section_or_problem "$1" '^## |^### ' "$2"; }

name="$skill_md's Draft PR step readies the PR against the already-pushed branch, with no push of its own"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step still pushes"; then
  pushes="$(first_record "$records" -F 'git push')"
  [[ -z "$pushes" ]] ||
    problems+=("$skill_md's Draft PR step still pushes the branch itself, so the procedure reads as though the branch reaches the remote only once the run is review-ready: $(printf '%.120s' "$pushes")")
fi
report "$name"

pass_or_problem() {
  record="$(first_record "$(section_records "$1" '^#')" -E '^ *- \*\*pass')"
  [[ -n "$record" ]] && return 0
  problems+=("$skill_md has no PASS branch under '$1' to read — $2 could not be checked")
  return 1
}

name="$skill_md's Green PASS and verify-refactor PASS both push the branch, at the two points that write the ledger"
problems=()

for heading in '#### Green' '#### Refactor loop'; do
  if pass_or_problem "$heading" "whether the branch is pushed where the ledger is written"; then
    grep -qF 'push-branch.sh' <<< "$record" ||
      problems+=("$skill_md's '$heading' PASS branch never runs push-branch.sh, so the commits it ticks and commits stay on one disk until the run is review-ready: $(printf '%.120s' "$record")")
  fi
done
report "$name"

names_the_full_gate() {
  grep -qE 'detect-test-command\.sh --tier all' <<< "$1" &&
    grep -qF 'exactly once' <<< "$1" &&
    grep -qwF 'only' <<< "$1"
}

name="$skill_md's Draft PR step runs detect-test-command.sh --tier all's command exactly once, as the only full-suite gate"
problems=()

if step_or_problem '### 4. Draft PR' "which command its full-suite gate runs"; then
  names_the_full_gate "$records" ||
    problems+=("$skill_md's Draft PR step never runs detect-test-command.sh --tier all's command exactly once as the only full-suite gate, so where the full command still runs is unstated")
fi
report "$name"

name="$skill_md's Draft PR step adds a repair step to the ledger on a red full run, rather than bailing"
problems=()

if step_or_problem '### 4. Draft PR' "what a red full run does"; then
  repair="$(first_record "$records" -F 'repair step' -wF 'red' -F 'ledger')"
  if [[ -z "$repair" ]]; then
    problems+=("$skill_md's Draft PR step has no record adding a repair step to the ledger on a red full run, so a suite only the full command reaches still ends the run in a bail")
  else
    grep -qF 'unit-tier test' <<< "$records" && grep -qwF 'gap' <<< "$records" ||
      problems+=("$skill_md's Draft PR step never says a unit-tier test is added when the red full run exposes a gap the fast tier missed")
    grep -qE 'verifier[^.]*full command' <<< "$records" ||
      problems+=("$skill_md's Draft PR step never says the repair step's verifier judges the fix against the full command")
  fi
fi
report "$name"

name="$skill_md's Draft PR step bails on a second red full run after a repair step, naming every suite still red"
problems=()

if step_or_problem '### 4. Draft PR' "what a second red full run does"; then
  second="$(first_record "$records" -wF 'bail' -E 'second red|red again' -F 'repair step')"
  if [[ -z "$second" ]]; then
    problems+=("$skill_md's Draft PR step has no record bailing on a second red full run after a repair step, so a repair that does not take can loop instead of ending the run")
  elif ! grep -qE 'every (suite still red|red suite|failing suite|still-red suite)' <<< "$second"; then
    problems+=("$skill_md's Draft PR step bails on a second red full run without naming every suite still red: $(printf '%.120s' "$second")")
  fi
fi
report "$name"

name="$skill_md's Draft PR step puts refactor-owed.sh render's output in the PR body, and omits the section on exit 3"
problems=()

if step_or_problem '### 4. Draft PR' "whether the run's refactor leftovers reach the PR body"; then
  render="$(first_record "$records" -F 'refactor-owed.sh render')"
  if [[ -z "$render" ]]; then
    problems+=("$skill_md's Draft PR step never runs refactor-owed.sh render, so every step's structural leftovers stay in a committed file nobody reading the PR is pointed at")
  else
    grep -qE 'issue-[^ ]*refactor-owed\.md' <<< "$render" ||
      problems+=("$skill_md's Draft PR step runs refactor-owed.sh render without naming the run's .tdd/issue-<n>-refactor-owed.md file, so which file the PR body is rendered from is left to judgement: $(printf '%.120s' "$render")")
    grep -qF 'body' <<< "$render" ||
      problems+=("$skill_md's Draft PR step renders the owed section without putting it in the PR body, so the leftovers are printed where only the conductor sees them: $(printf '%.120s' "$render")")
    grep -F 'refactor-owed' <<< "$records" |
      grep -E 'exits? 3' |
      grep -E 'omit|left out|leaves it out|no section|nothing' > /dev/null ||
      problems+=("$skill_md's Draft PR step never says an exit 3 from refactor-owed.sh render leaves the section out, so a run whose every refactor finished clean gets a ## Refactor owed heading promising leftovers nobody left")
  fi
fi
report "$name"

name="$skill_md's Draft PR step copies the ledger's ## Owed steps bullets into the PR body under ## Owed steps"
problems=()

if step_or_problem '### 4. Draft PR' "whether the ledger's owed steps reach the PR body"; then
  owed="$(grep -F 'owed steps' <<< "$records")"
  if [[ -z "$owed" ]]; then
    problems+=("$skill_md's Draft PR step never mentions the ledger's ## Owed steps section, so a step the growth budget refused is left in a committed file no reader of the PR is pointed at")
  else
    grep -qF '.tdd/issue-<n>.md' <<< "$owed" ||
      problems+=("$skill_md's Draft PR step speaks of ## Owed steps without naming the run's .tdd/issue-<n>.md ledger as where the bullets are read from, so the run's other owed file could be copied instead: $(printf '%.120s' "$owed")")
    grep -qF 'body' <<< "$owed" ||
      problems+=("$skill_md's Draft PR step never puts the ## Owed steps bullets in the PR body, so they stay where only the conductor sees them: $(printf '%.120s' "$owed")")
  fi
fi
report "$name"

name="$skill_md's Scope & plan step pushes and opens the draft PR after the plan commit, before the Plan comment"
problems=()

if step_or_problem '### 2. Scope & plan' "where the run's draft PR is opened"; then
  pr_at="$(record_number "$records" -F 'gh api repos/{owner}/{repo}/pulls -f draft=true')"
  if [[ -z "$pr_at" ]]; then
    problems+=("$skill_md's Scope & plan step never runs gh pr create, so a multi-step run puts no claim on origin until its last step and a second machine reads the issue as free for the whole of it")
  else
    pr_record="$(sed -n "${pr_at}p" <<< "$records")"
    grep -qF -- 'draft=true' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without --draft, so a run one step in reads as a branch offered for review: $(printf '%.120s' "$pr_record")")
    grep -qF 'closes #<n>' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without Closes #<n> in its body, so nothing on the PR names the issue it claims: $(printf '%.120s' "$pr_record")")
    grep -qE 'wip|work in progress' <<< "$pr_record" ||
      problems+=("$skill_md's Scope & plan step opens the PR without a title marking the work in progress, so a reader of origin cannot tell a run mid-flight from a finished branch: $(printf '%.120s' "$pr_record")")
    grep -qF 'push-branch.sh' <<< "$records" ||
      problems+=("$skill_md's Scope & plan step never runs push-branch.sh, so the branch the PR is opened against has never reached the remote")

    commit_at="$(record_number "$records" -F 'plan: scope #<n> into')"
    comment_at="$(record_number "$records" -F 'mirror the plan')"
    if [[ -z "$commit_at" || -z "$comment_at" ]]; then
      problems+=("$skill_md's Scope & plan step no longer has both the plan commit and the Plan comment to place the PR between — where it is opened could not be checked")
    else
      [[ "$commit_at" -lt "$pr_at" ]] ||
        problems+=("$skill_md's Scope & plan step opens the PR at record $pr_at, before the plan commit at record $commit_at — there is no commit ahead of the base for a PR to be opened against yet")
      [[ "$pr_at" -lt "$comment_at" ]] ||
        problems+=("$skill_md's Scope & plan step opens the PR at record $pr_at, after the Plan comment at record $comment_at — the comment is meant to name the PR url, and the claim is meant to be the first act after the plan commit")
    fi
  fi
fi
report "$name"

name="$skill_md's Green PASS branch updates the PR body with the ledger's done-of-total step count"
problems=()

if pass_or_problem '#### Green' "whether the step tick updates the PR body"; then
  if ! grep -qF 'gh api -x patch' <<< "$record"; then
    problems+=("$skill_md's Green PASS branch never runs gh pr edit, so the draft PR opened at the plan commit still reads as step 0 for the whole of a multi-step run")
  else
    grep -qF -- '-f body=' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR without --body, so nothing a reader of the PR sees carries the run's progress: $(printf '%.120s' "$record")")
    grep -qF '.tdd/issue-<n>.md' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR body without naming the run's .tdd/issue-<n>.md ledger as where the count is read from, so which file answers how far the run has got is left to judgement: $(printf '%.120s' "$record")")
    grep -qE '<done> of <total>|[0-9]+ of [0-9]+|done of|of how many' <<< "$record" ||
      problems+=("$skill_md's Green PASS branch edits the PR body without a done-of-total step count, so a reader learns the run moved but not how far it has left to go: $(printf '%.120s' "$record")")
  fi
fi
report "$name"

section_commands() {
  section_lines "$section_heading" "$section_closer" |
  awk '{ sub(/^[[:space:]]+/, "")
         buf = (cont ? buf " " $0 : $0)
         if (buf ~ /\\$/) { sub(/\\$/, "", buf); cont = 1; next }
         cont = 0; print buf }
       END { if (cont) print buf }' | tr '[:upper:]' '[:lower:]'
}

line_of() { awk -v re="$1" '$0 ~ ("^" re) { print NR; exit }' <<< "$commands"; }
done_mark='veri_issue=[^ ]* veri_actor=conductor [$]s/event[.]sh done'
metrics_commit='git commit -m "metrics:'
rollup_read='gh api [^#]*/check-runs'
wait_ci_run='[^#]*[$]s/wait-ci[.]sh '
push_run='[^#]*([$]s/push-branch[.]sh|git push)'
log_failed_read='[^#]*gh run view [^#]*--log-failed'
ready_run='[^#]*gh_pr_ready'
body_edit='gh api -x patch .*-f body='

unmarked_records() { tr -d '*`' <<< "$records"; }

name="$skill_md's Draft PR step creates no PR: it retitles and rewrites the open one and marks it ready for review"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step creates a second PR"; then
  commands="$(section_commands)"
  grep -qE '^gh api -x patch .*-f title=' <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit with --title, so the PR keeps the work-in-progress title it was opened with at the plan commit and a reader of origin cannot tell the finished branch from a run mid-flight")
  grep -qE "^$body_edit" <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit with --body, so the body a human reads at the merge is still the one-line claim the plan commit opened")
  grep -qE "^$ready_run" <<< "$commands" ||
    problems+=("$skill_md's Draft PR step never runs gh pr ready, so a finished run leaves a draft nobody is asked to review")
  creates="$(first_record "$commands" -E '^gh api repos/[{]owner[}]/[{]repo[}]/pulls -f')"
  [[ -z "$creates" ]] ||
    problems+=("$skill_md's Draft PR step still runs gh pr create, so a run whose draft PR has been open since its plan commit either fails at its last step or opens a second PR for the same branch: $(printf '%.120s' "$creates")")
fi
report "$name"

name="$skill_md's Resume reuses the open PR already on its branch and opens no second one"
problems=()

if section_or_problem '## Resume' '^## ' "what a resumed run does with the PR its branch already carries"; then
  grep -qE '^gh api [^#]*pulls[?]head=' <<< "$(section_commands)" ||
    problems+=("$skill_md's Resume section never runs gh pr view, so a resumed run never reads the open PR its branch already carries and has no url for the tick's gh pr edit or step 4's rewrite")
  creates="$(first_record "$records" -F 'pr-creating `gh api`')"
  if [[ -n "$creates" ]]; then
    grep -qE 'no open pr|no pr|none|no such pr' <<< "$creates" ||
      problems+=("$skill_md's Resume section runs gh pr create without conditioning it on there being no open PR to reuse, so a resume of a run that already opened one leaves the issue claimed by two pages: $(printf '%.120s' "$creates")")
  fi
fi
report "$name"

name="$skill_md's Bailing section leaves the draft PR open carrying the bail diagnostic, and opens no PR"
problems=()

if section_or_problem '## Bailing' '^## ' "what a bailed run does with the draft PR its branch already carries"; then
  commands="$(section_commands)"
  grep -qE "^gh api [^#]*/issues/<pr-number>/comments|^$body_edit" <<< "$commands" ||
    problems+=("$skill_md's Bailing section runs neither gh pr comment nor gh pr edit --body, so the bail diagnostic reaches the issue thread and never the draft PR a human is pointed at, which still reads as a run in progress")
  closes="$(first_record "$commands" -E '^gh pr close')"
  [[ -z "$closes" ]] ||
    problems+=("$skill_md's Bailing section closes the PR, so the issue goes back into solvable-issues.sh's pool for the next machine to re-take and re-bail, and the visible record of the bail is gone: $(printf '%.120s' "$closes")")
  opens_none="$(first_record "$records" -F 'open no pr')"
  [[ -z "$opens_none" ]] ||
    problems+=("$skill_md's Bailing section still tells the run to open no PR, an instruction whose premise went with #195: the PR has been open since the plan commit, so there is nothing here to withhold: $(printf '%.120s' "$opens_none")")
fi
report "$name"

name="$skill_md's worktree step no longer says the draft PR is opened once every step is green"
problems=()

if step_or_problem '### 1. Read the issue' "what step 1.2 says the claim is before the PR exists"; then
  stale="$(first_record "$records" -F 'every step is green')"
  [[ -z "$stale" ]] ||
    problems+=("$skill_md's worktree step still says the draft PR is opened once every step is green, the order #195 reversed — the PR now opens at the plan commit, so the window this passage gives as the reason for the pid lock no longer exists: $(printf '%.120s' "$stale")")
fi
report "$name"

name="$skill_md's Draft PR step runs rebase-onto-default.sh after its dirty-tree and pending-refactor check and before the done mark, the metrics commit and gh pr ready; exit 3 continues unchanged, exit 2 bails with no-verdict"
problems=()

if step_or_problem '### 4. Draft PR' "where the step rebases onto the default branch"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  if [[ -z "$rebase" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/rebase-onto-default.sh, so a branch behind the default one is still readied for review un-rebased")
  else
    rebase_runs() {
      local at
      at="$(line_of "$2")"
      if [[ -z "$at" ]]; then
        problems+=("$skill_md's Draft PR step runs no $2, so the rebase's order against it could not be checked")
      elif { [[ "$1" == after ]] && [[ "$at" -ge "$rebase" ]]; } ||
           { [[ "$1" == before ]] && [[ "$at" -le "$rebase" ]]; }; then
        problems+=("$skill_md's Draft PR step runs rebase-onto-default.sh (command line $rebase) not $1 $2 (command line $at)")
      fi
    }
    for before in 'git status --porcelain' '[$]s/next-pending-refactor[.]sh'; do
      rebase_runs after "$before"
    done
    for after in "$done_mark" '[$]s/metrics[.]sh' "$metrics_commit" "$ready_run"; do
      rebase_runs before "$after"
    done
    plain="$(unmarked_records)"
    said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 3' -E 'continu')"
    [[ -n "$said" ]] ||
      problems+=("no instruction of $skill_md's Draft PR step naming rebase-onto-default.sh says its exit 3 continues unchanged")
    said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 2' -E 'bail' -F 'no-verdict')"
    [[ -n "$said" ]] ||
      problems+=("no instruction of $skill_md's Draft PR step naming rebase-onto-default.sh says its exit 2 bails with no-verdict")
  fi
fi
report "$name"

name="$skill_md's Draft PR step runs the full test command once on a rebased tip, bails on red without readying the PR, and on green pushes with push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does after a rebase that changed the tree"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  leased="$(line_of '[$]s/push-branch[.]sh --force-with-lease=[^ :]+:[^ ]*pre-rebase')"
  if [[ -z "$leased" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, so a rebased branch's rewritten history has no push pinned to the sha its remote copy held before the rebase")
  elif [[ -z "$rebase" ]] || [[ "$leased" -le "$rebase" ]]; then
    problems+=("$skill_md's Draft PR step runs push-branch.sh --force-with-lease (command line $leased) not after rebase-onto-default.sh (command line ${rebase:-none})")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebased tip' -E 'full (test )?command|full suite|--tier all' -wF 'once')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step runs the full test command once on the rebased tip, so a rebase that combined two green branches into a red one reaches review unrun")
  said="$(first_record "$plain" -F 'rebased tip' -wF 'red' -wF 'bail' -F 'draft')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step bails on a red rebased tip with the PR left a draft, so a red rebase can still be readied for review")
  bare="$(first_record "$commands" -E '(^git push|^[$]s/push-branch[.]sh).*( --force( |$)| -f( |$)| \+)')"
  [[ -z "$bare" ]] ||
    problems+=("$skill_md's Draft PR step pushes with a bare force, which replaces the branch's remote copy whatever another writer left there: $(printf '%.120s' "$bare")")
fi
report "$name"

name="$skill_md's Draft PR step, on rebase-onto-default.sh exit 1, launches a develop-rebase leaf through supervise.sh, then a blind verify-rebase through run-verdict.sh, revises on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a conflicted rebase"; then
  commands="$(section_commands)"
  rebase="$(line_of '[$]s/rebase-onto-default[.]sh')"
  develop="$(line_of '.*[$]s/supervise[.]sh develop-rebase ')"
  verdict="$(line_of '.*[$]s/supervise[.]sh verdict-rebase [$]s/run-verdict[.]sh .* rebase ')"
  ready="$(line_of "$ready_run")"
  if [[ -z "$develop" ]]; then
    problems+=("$skill_md's Draft PR step launches no develop-rebase leaf through \$S/supervise.sh, so a conflicted rebase has nothing to resolve it")
  fi
  if [[ -z "$verdict" ]]; then
    problems+=("$skill_md's Draft PR step launches no verdict-rebase through \$S/supervise.sh \$S/run-verdict.sh … rebase, so a conflict's resolution reaches review seen by no blind verifier")
  fi
  if [[ -n "$develop" ]] && [[ -n "$verdict" ]]; then
    { [[ -n "$rebase" ]] && [[ "$rebase" -lt "$develop" ]] && [[ "$develop" -lt "$verdict" ]] &&
      [[ -n "$ready" ]] && [[ "$verdict" -lt "$ready" ]]; } ||
      problems+=("$skill_md's Draft PR step does not run rebase-onto-default.sh (command line ${rebase:-none}), the develop-rebase leaf ($develop), the verdict-rebase ($verdict) and gh pr ready (${ready:-none}) in that order")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebase-onto-default.sh' -E 'exit 1' -F 'develop-rebase')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says rebase-onto-default.sh's exit 1 launches the develop-rebase leaf")
  said="$(first_record "$plain" -wF 'reject' -F 'revise_budget')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step sends a verify-rebase REJECT round the revise loop within REVISE_BUDGET")
  said="$(first_record "$plain" -F 'verify-rebase' -wF 'pass' -E 'ready|readie')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step readies the PR only after a verify-rebase PASS")
fi
report "$name"

name="$skill_md's Draft PR step, on a rebase not resolved within budget (REBASE: FAILED, REVISE_BUDGET exhausted or a killed leaf), resets the branch to <pre-rebase-sha>, leaves the PR a draft and bails naming every conflicting file"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a rebase it could not resolve"; then
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rebase: failed' -F 'revise_budget' -wE 'killed|kill')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step names REBASE: FAILED, an exhausted REVISE_BUDGET and a killed leaf together as a rebase not resolved within budget")
  said="$(first_record "$plain" -E 'git reset --hard <pre-rebase-sha>')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step resets the branch with git reset --hard <pre-rebase-sha>, so a rebase it could not resolve leaves a half-made resolution on the branch")
  said="$(first_record "$plain" -wF 'bail' -E '(every|each|all) (of the )?conflicting file' -F 'draft')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step bails on an unresolved rebase with the PR left a draft and a comment naming every conflicting file")
fi
report "$name"

name="$skill_md's Draft PR step, after gh pr ready, waits on wait-ci.sh and reads the readied PR's statusCheckRollup fail-closed: an empty rollup is never a pass and a conclusion other than SUCCESS, NEUTRAL or SKIPPED counts as failed (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step reads the readied PR's CI"; then
  commands="$(section_commands)"
  ready="$(line_of "$ready_run")"
  watch="$(line_of "$wait_ci_run")"
  rollup="$(line_of "$rollup_read")"
  [[ -n "$ready" && -n "$watch" && "$watch" -gt "$ready" ]] ||
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh after gh pr ready, so nothing waits for the readied PR's CI to finish")
  [[ -n "$watch" && -n "$rollup" && "$rollup" -gt "$watch" ]] ||
    problems+=("$skill_md's Draft PR step runs no gh pr view --json statusCheckRollup after its \$S/wait-ci.sh, so the run reads CI before it has answered")
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'rollup' -wF 'empty' -E 'never[a-z ]* pass')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says an empty rollup is never a pass")
  said="$(first_record "$plain" -F 'conclusion' -F 'success' -F 'neutral' -F 'skipped' -E 'fail')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step counts a completed check whose conclusion is not SUCCESS, NEUTRAL or SKIPPED as failed")
fi
report "$name"

name="$skill_md's Draft PR step never counts a pending check as green, and a check still pending when its bounded CI wait runs out bails with a cause classify-bail.sh classifies (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does with a check still pending"; then
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -E 'pending check|check[a-z ]* pending' -wF 'never' -E 'green|pass')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says a pending check never counts as green")
  bail="$(first_record "$records" -E 'pending check|check[a-z ]* pending' -E 'bound|timeout|time out|runs out' -wF 'bail')"
  if [[ -z "$bail" ]]; then
    problems+=("no instruction of $skill_md's Draft PR step bounds the CI wait and bails on a check still pending when the bound runs out, so a hung CI job waits forever")
  else
    classified=""
    while IFS= read -r cause; do
      [[ -n "$cause" ]] || continue
      "$ROOT/skills/tdd/scripts/classify-bail.sh" "$cause" > /dev/null 2>&1 && classified="$cause"
    done < <(grep -o '`[^`]*`' <<< "$bail" | tr -d '`')
    [[ -n "$classified" ]] ||
      problems+=("$skill_md's Draft PR step bails on a check still pending past its bound with no cause classify-bail.sh classifies: $(printf '%.120s' "$bail")")
  fi
fi
report "$name"

name="$skill_md's Draft PR step bounds the command that waits on the readied PR's checks itself: wait-ci.sh with no max-seconds or one under 600, and no gh pr checks after gh pr ready (#542, #544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step's CI wait is bounded by its own command"; then
  commands="$(section_commands)"
  ready="$(line_of "$ready_run")"
  waits="$(line_of "$wait_ci_run")"
  if [[ -z "$ready" || -z "$waits" || "$waits" -le "$ready" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh after gh pr ready, so there is no CI wait to bound")
  else
    slice="$(awk -v at="$waits" -v re="$wait_ci_run" 'NR == at { sub("^" re " *[^ ]+", ""); print $1 }' <<< "$commands")"
    [[ ! "$slice" =~ ^[0-9]+$ || "$slice" -lt 600 ]] ||
      problems+=("$skill_md's Draft PR step gives wait-ci.sh a slice of $slice seconds, longer than one Bash call lives")
  fi
  checks="$(awk -v a="${ready:-0}" 'NR > a && /^[^#]*gh pr checks/ { print; exit }' <<< "$commands")"
  [[ -z "$checks" ]] ||
    problems+=("$skill_md's Draft PR step still waits with gh pr checks after gh pr ready: $(printf '%.120s' "$checks")")
fi
report "$name"

name="$skill_md's Draft PR step waits on the readied PR's checks and reads their rollup before the done mark and the metrics commit (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step reads CI before recording the run done"; then
  commands="$(section_commands)"
  for ci in "$wait_ci_run" "$rollup_read"; do
    ci_at="$(line_of "$ci")"
    if [[ -z "$ci_at" ]]; then
      problems+=("$skill_md's Draft PR step runs no $ci, so its order against the done mark could not be checked")
      continue
    fi
    for recorded in "$done_mark" "$metrics_commit"; do
      at="$(line_of "$recorded")"
      if [[ -z "$at" ]]; then
        problems+=("$skill_md's Draft PR step runs no $recorded, so the CI read's order against it could not be checked")
      elif [[ "$at" -le "$ci_at" ]]; then
        problems+=("$skill_md's Draft PR step runs $ci (command line $ci_at) after $recorded (command line $at)")
      fi
    done
  done
fi
report "$name"

name="$skill_md's Draft PR command block bails with cause ci-timeout on wait-ci.sh's exit 2, before the done mark (#542, #544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step's command block bails on a check still pending"; then
  commands="$(section_commands)"
  waits="$(line_of "$wait_ci_run")"
  done_at="$(line_of "$done_mark")"
  timeout="$(line_of '[^#]*ci-timeout')"
  if [[ -z "$waits" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh or no done mark, so where it bails on a pending check could not be checked")
  else
    [[ -n "$timeout" && "$timeout" -ge "$waits" && "$timeout" -lt "$done_at" ]] ||
      problems+=("no command line of $skill_md's Draft PR step bails with cause ci-timeout between \$S/wait-ci.sh and the done mark")
  fi
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'wait-ci.sh' -wF '2' -F 'ci-timeout')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says wait-ci.sh's exit 2 bails with cause ci-timeout")
fi
report "$name"

name="$skill_md's Draft PR step answers a failed CI check with a repair step quoting the gh run view --log-failed FAIL line, committed, resuming the cycle loop (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step repairs a failed CI check"; then
  commands="$(section_commands)"
  rollup="$(line_of "$rollup_read")"
  done_at="$(line_of "$done_mark")"
  log="$(line_of "$log_failed_read")"
  if [[ -z "$rollup" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step reads no statusCheckRollup or runs no done mark, so where it repairs a failed check could not be checked")
  elif [[ -z "$log" || "$log" -le "$rollup" || "$log" -ge "$done_at" ]]; then
    problems+=("no command line of $skill_md's Draft PR step runs gh run view --log-failed between the rollup read and the done mark, so a failed check's log is never read")
  else
    added="$(awk -v from="$log" -v to="$done_at" 'NR > from && NR < to && /^[$]s\/add-ledger-step[.]sh [.]tdd\/issue-<n>[.]md / { print NR; exit }' <<< "$commands")"
    [[ -n "$added" ]] ||
      problems+=("no command line of $skill_md's Draft PR step appends a repair step with add-ledger-step.sh between the --log-failed read and the done mark")
    [[ -n "$added" ]] && ! awk -v from="$added" -v to="$done_at" 'NR > from && NR < to && /^git commit / { found = 1 } END { exit !found }' <<< "$commands" &&
      problems+=("no command line of $skill_md's Draft PR step commits the ledger after appending the repair step and before the done mark")
    plain="$(unmarked_records)"
    record="$(first_record "$plain" -F 'log-failed' -F 'repair step')"
    if [[ -z "$record" ]]; then
      problems+=("no record of $skill_md's Draft PR step says what the repair step a failed check appends carries from --log-failed")
    else
      grep -F 'fail -' > /dev/null <<< "$record" ||
        problems+=("$skill_md's Draft PR step never says the CI repair step quotes the failing suite's FAIL - line: $(printf '%.120s' "$record")")
      grep -E 'step 3|cycle loop' > /dev/null <<< "$record" ||
        problems+=("$skill_md's Draft PR step never says the run returns to the cycle loop after appending the CI repair step: $(printf '%.120s' "$record")")
    fi
  fi
fi
report "$name"

name="$skill_md's Draft PR step bails on a second red CI result after a CI repair step with a cause classify-bail.sh maps to system or process (#542)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the step bails on a second red CI result"; then
  commands="$(section_commands)"
  log="$(line_of "$log_failed_read")"
  done_at="$(line_of "$done_mark")"
  if [[ -z "$log" || -z "$done_at" ]]; then
    problems+=("$skill_md's Draft PR step reads no --log-failed or runs no done mark, so where it bails on a second red CI result could not be checked")
  else
    cause="$(awk -v from="$log" -v to="$done_at" \
      'NR > from && NR < to && sub(/^[^#]*[$]s\/event[.]sh bail cause=/, "") && $1 != "ci-timeout" { print $1; exit }' <<< "$commands")"
    if [[ -z "$cause" ]]; then
      problems+=("no command line of $skill_md's Draft PR step bails (event.sh bail cause=…) between the --log-failed read and the done mark, so a second red CI result stops silently")
    else
      label="$("$ROOT/skills/tdd/scripts/classify-bail.sh" "$cause" 2> /dev/null)"
      [[ "$label" == system || "$label" == process ]] ||
        problems+=("$skill_md's Draft PR step bails on a second red CI result with cause $cause, which classify-bail.sh maps to no system or process label")
    fi
  fi
  plain="$(unmarked_records)"
  record="$(first_record "$plain" -F 'second red' -E 'red ci|ci (check|result)')"
  if [[ -z "$record" ]]; then
    problems+=("no record of $skill_md's Draft PR step says what a second red CI result after a repair step does")
  else
    grep -F 'bail' > /dev/null <<< "$record" ||
      problems+=("$skill_md's Draft PR step never says a second red CI result bails: $(printf '%.120s' "$record")")
  fi
fi
report "$name"

name="$skill_md's Draft PR step waits on CI by calling wait-ci.sh again on its exit 3, with no wait loop inside one Bash call and no pending test that reads .status alone (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "how the step waits on the readied PR's CI"; then
  commands="$(section_commands)"
  ready="$(line_of "$ready_run")"
  wait_ci="$(line_of "$wait_ci_run")"
  done_at="$(line_of "$done_mark")"
  [[ -n "$ready" && -n "$wait_ci" && -n "$done_at" && "$wait_ci" -gt "$ready" && "$wait_ci" -lt "$done_at" ]] ||
    problems+=("no command line of $skill_md's Draft PR step runs \$S/wait-ci.sh between gh pr ready and the done mark")
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -F 'wait-ci.sh' -wF '3' -E 'again')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says to call wait-ci.sh again on its exit 3")
  loop="$(first_record "$commands" -E '^(while|until) .*; *do( |$)|^sleep [0-9]|^gh pr checks .*--watch')"
  [[ -z "$loop" ]] ||
    problems+=("$skill_md's Draft PR command block waits inside one Bash call: $(printf '%.120s' "$loop")")
  status_only="$(first_record "$commands" -E '[.]status *==')"
  [[ -z "$status_only" ]] || grep -F '__typename' > /dev/null <<< "$status_only" ||
    problems+=("$skill_md's Draft PR command block tests a check pending by .status alone, so a legacy StatusContext row is never pending: $(printf '%.120s' "$status_only")")
fi
report "$name"

name="$skill_md's Draft PR step stops at a ci-timeout or ci-red bail: no done mark and no metrics commit follow it in its command block, and it goes to Bailing (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether a CI bail stops the step"; then
  commands="$(section_commands)"
  followed="$(awk -v done_re="$done_mark" -v metrics_re="$metrics_commit" '
      /^```/ { block++; fenced = !fenced; next }
      !fenced { next }
      /^[^#]*[$]s\/event[.]sh bail cause=ci-(timeout|red)/ {
        match($0, /cause=ci-(timeout|red)/); bails[block] = bails[block] " " substr($0, RSTART + 6, RLENGTH - 6); next }
      bails[block] != "" && ($0 ~ ("^" done_re) || $0 ~ ("^" metrics_re)) {
        print "after" bails[block] ": " $0 }' <<< "$commands")"
  bailed="$(grep -F 'event.sh bail cause=ci-' <<< "$commands")"
  [[ -n "$bailed" ]] ||
    problems+=("$skill_md's Draft PR step runs no event.sh bail cause=ci-timeout or cause=ci-red, so whether a CI bail stops the step could not be checked")
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    problems+=("$skill_md's Draft PR command block records the run finished after a CI bail — $(printf '%.160s' "$line")")
  done <<< "$followed"
  plain="$(unmarked_records)"
  said="$(first_record "$plain" -E 'ci-timeout|ci-red' -F 'bailing')"
  [[ -n "$said" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step sends a ci-timeout or ci-red bail to Bailing")
fi
report "$name"

name="$skill_md's Draft PR step appends its CI repair step with a ⟦ci-repair⟧ text and recognises a second red by that mark, not by the repair step's prose (#544)"
problems=()
ci_repair_mark='⟦ci-repair⟧'

if step_or_problem '### 4. Draft PR' "how the step marks and recognises a CI repair step"; then
  commands="$(section_commands)"
  appended="$(first_record "$commands" -E '^[^#]*[$]s/add-ledger-step[.]sh ' -F 'ci failure')"
  if [[ -z "$appended" ]]; then
    problems+=("no command line of $skill_md's Draft PR step appends a CI repair step through add-ledger-step.sh")
  else
    grep -F "$ci_repair_mark" > /dev/null <<< "$appended" ||
      problems+=("$skill_md's Draft PR step appends its CI repair step without the $ci_repair_mark mark: $(printf '%.160s' "$appended")")
  fi
  red="$(first_record "$commands" -E '^[^#]*[$]s/event[.]sh bail cause=ci-red')"
  if [[ -z "$red" ]]; then
    problems+=("no command line of $skill_md's Draft PR step bails with cause ci-red, so how it recognises a second red could not be checked")
  else
    grep -F "$ci_repair_mark" > /dev/null <<< "$red" ||
      problems+=("$skill_md's Draft PR step recognises a second red CI result without the $ci_repair_mark mark: $(printf '%.160s' "$red")")
    grep -F 'fix the ci failure' > /dev/null <<< "$red" &&
      problems+=("$skill_md's Draft PR step recognises a second red CI result by the repair step's prose: $(printf '%.160s' "$red")")
  fi
fi
report "$name"

name="$skill_md's Draft PR step leaves no CI run on the readied PR that nothing reads: every push after the CI read is followed by a wait-ci.sh call (#544)"
problems=()

if step_or_problem '### 4. Draft PR' "whether a push after the CI read has its run read"; then
  commands="$(section_commands)"
  read_at="$(line_of "$wait_ci_run")"
  if [[ -z "$read_at" ]]; then
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh, so whether a later push has its CI run read could not be checked")
  else
    unread="$(awk -v from="$read_at" -v wait_re="^$wait_ci_run" -v push_re="^$push_run" '
        NR <= from { next }
        $0 ~ push_re { pushed = $0; next }
        pushed != "" && $0 ~ wait_re { pushed = "" }
        END { print pushed }' <<< "$commands")"
    [[ -z "$unread" ]] ||
      problems+=("$skill_md's Draft PR step pushes after the CI read with no wait-ci.sh after it, leaving that push's CI run unread: $(printf '%.120s' "$unread")")
  fi
fi
report "$name"

name="$skill_md's Draft PR step passes every wait-ci.sh call the sha it just pushed, from git rev-parse HEAD, as the head it waits for (#550)"
problems=()

if step_or_problem '### 4. Draft PR' "which head sha the step's CI waits are given"; then
  commands="$(section_commands)"
  unpinned="$(awk -v wait_re="^$wait_ci_run" -v push_re="^$push_run" '
      $0 ~ push_re { delete sha }
      match($0, /^[a-z_][a-z0-9_]*="?[$][(]git rev-parse head[)]"?/) {
        split($0, lhs, "="); sha[lhs[1]] = 1 }
      $0 ~ wait_re {
        call = $0; sub(/#.*/, "", call); sub(/;.*/, "", call)
        gsub(/"?[$][(]git rev-parse head[)]"?/, "@head@", call)
        n = split(call, w, " ")
        arg = (n >= 5 ? w[5] : "")
        v = arg; gsub(/["${}]/, "", v)
        if (arg != "@head@" && !(arg ~ /^"?[$]/ && (v in sha))) print $0 }' <<< "$commands")"
  [[ -n "$(line_of "$wait_ci_run")" ]] ||
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh, so which head its CI waits are given could not be checked")
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    problems+=("$skill_md's Draft PR step calls wait-ci.sh with no head sha from git rev-parse HEAD after its last push: $(printf '%.120s' "$line")")
  done <<< "$unpinned"
fi
report "$name"

name="$skill_md's Draft PR step bails on the metrics: push's CI wait with a command in its block, ci-red on exit 1 and ci-timeout on exit 2 (#550)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the metrics: push's CI wait bails"; then
  commands="$(section_commands)"
  metrics_at="$(line_of "$metrics_commit")"
  if [[ -z "$metrics_at" ]]; then
    problems+=("$skill_md's Draft PR step makes no metrics: commit, so whether its push's CI wait bails could not be checked")
  else
    bails="$(awk -v from="$metrics_at" -v wait_re="^$wait_ci_run" '
        NR <= from { next }
        /^```/ { if (waited) exit; next }
        $0 ~ wait_re { waited = 1; next }
        waited && match($0, /[$]s\/event[.]sh bail cause=ci-(red|timeout)/) {
          cause = substr($0, RSTART + 23, RLENGTH - 23)
          print cause " " substr($0, 1, RSTART - 1) }' <<< "$commands")"
    for want in 'ci-red 1' 'ci-timeout 2'; do
      cause="${want% *}" code="${want#* }"
      keyed="$(awk -v c="$cause" -v k="$code" '$1 == c && (" " $0 " ") ~ ("[^0-9]" k "[^0-9]")' <<< "$bails")"
      [[ -n "$keyed" ]] ||
        problems+=("no command line of $skill_md's Draft PR step bails with cause $cause on the metrics: push's wait-ci.sh exit $code, in the block after that wait")
    done
  fi
fi
report "$name"

name="$skill_md's Green PASS branch counts the PR body's done-of-total from ledger-steps.sh's records (#495)"
problems=()

if pass_or_problem '#### Green' "where the PR body's step count is read from"; then
  grep -F 'ledger-steps.sh' <<< "$record" > /dev/null ||
    problems+=("$skill_md's Green PASS branch never runs ledger-steps.sh, so the PR body's done-of-total is not read off the ledger's step records: $(printf '%.120s' "$record")")
  spelled="$(grep -oF "grep -c '^- \\[" <<< "$record" || true)"
  [[ -z "$spelled" ]] ||
    problems+=("$skill_md's Green PASS branch still counts steps with its own box pattern: $(head -1 <<< "$spelled")")
fi
report "$name"

name="$skill_md reaches the default branch, the issue and the PR through the helper or gh api, never gh repo/issue/pr"
problems=()

while IFS= read -r hit; do
  problems+=("$skill_md:$hit")
done < <(grep -nE '\bgh (repo view|issue (view|comment)|pr (create|view|edit|ready|comment))\b' "$skill_path")
for route in 'gh_pr_ready' 'lib/github.sh' 'gh api ' 'default_branch'; do
  grep -F -- "$route" "$skill_path" > /dev/null ||
    problems+=("$skill_md never names $route")
done
report "$name"

name="$skill_md's Draft PR step calls wait-ci.sh with no fixed total and states the bound's rule: twice the mean of the last 5 CI runs, capped at 10 minutes, 540 s fallback (#549)"
problems=()

if step_or_problem '### 4. Draft PR' "how the step bounds its CI wait"; then
  commands="$(section_commands)"
  fixed="$(awk -v wait_re="^$wait_ci_run" '
      $0 ~ wait_re {
        call = $0; sub(/#.*/, "", call); sub(/;.*/, "", call)
        n = split(call, w, " ")
        if (n >= 4 && w[4] ~ /^[0-9]+$/) print $0 }' <<< "$commands")"
  [[ -n "$(line_of "$wait_ci_run")" ]] ||
    problems+=("$skill_md's Draft PR step runs no \$S/wait-ci.sh, so how its CI wait is bounded could not be checked")
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    problems+=("$skill_md's Draft PR step calls wait-ci.sh with a fixed total-seconds, overriding the bound computed from recent CI runs: $(printf '%.120s' "$line")")
  done <<< "$fixed"
  plain="$(unmarked_records)"
  rule="$(first_record "$plain" -F 'wait-ci.sh' -E '(twice|2 ?[x×]) the mean' -E '(last|most recent) (5|five)' -E '(10 minutes|600 s)' -F '540')"
  [[ -n "$rule" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step states wait-ci.sh's bound as twice the mean of the last 5 completed CI runs, capped at 10 minutes, falling back to 540 s")
fi
report "$name"

name="$skill_md's Draft PR step appends a ⟦suite-repair⟧ repair step naming the failing suite and its FAIL - line on a red full run, and commits the ledger (#590)"
problems=()
suite_repair_mark='⟦suite-repair⟧'

if step_or_problem '### 4. Draft PR' "how the step appends a full-suite repair step"; then
  commands="$(section_commands)"
  appended="$(awk -v mark="$suite_repair_mark" '/^[^#]*[$]s\/add-ledger-step[.]sh [.]tdd\/issue-<n>[.]md / && index($0, mark) { print NR "\t" $0; exit }' <<< "$commands")"
  if [[ -z "$appended" ]]; then
    problems+=("no command line of $skill_md's Draft PR step appends a full-suite repair step carrying $suite_repair_mark through add-ledger-step.sh")
  else
    at="${appended%%$'\t'*}"
    appended="${appended#*$'\t'}"
    grep -F '<suite>' > /dev/null <<< "$appended" && grep -F 'fail -' > /dev/null <<< "$appended" ||
      problems+=("$skill_md's Draft PR step appends its $suite_repair_mark step without naming the failing suite and its FAIL - line: $(printf '%.160s' "$appended")")
    awk -v from="$at" 'NR > from && /^git add [.]tdd\/issue-<n>[.]md/ { added = 1 } NR > from && /^git commit / { found = added; exit } END { exit !found }' <<< "$commands" ||
      problems+=("no command line of $skill_md's Draft PR step adds and commits the ledger after appending the $suite_repair_mark step")
  fi
fi
report "$name"

name="$skill_md's Draft PR step bails on a second red full run keyed on a ⟦suite-repair⟧ line already in the ledger, naming every suite still red (#590)"
problems=()

if step_or_problem '### 4. Draft PR' "how the step recognises a second red full run"; then
  commands="$(section_commands)"
  keyed="$(awk -v mark="$suite_repair_mark" '/^[^#]*[$]s\/event[.]sh bail / && index($0, mark) && index($0, ".tdd/issue-<n>.md") { print; exit }' <<< "$commands")"
  [[ -n "$keyed" ]] ||
    problems+=("no command line of $skill_md's Draft PR step bails on a $suite_repair_mark line already in .tdd/issue-<n>.md, so a second red full run is recognised only in prose")
  second="$(first_record "$records" -wF 'bail' -E 'second red|red again' -F 'repair step')"
  grep -E 'every (suite still red|red suite|failing suite|still-red suite)' > /dev/null <<< "$second" ||
    problems+=("$skill_md's Draft PR step's second-red bail no longer names every suite still red: $(printf '%.120s' "$second")")
fi
report "$name"

name="$skill_md's Draft PR step keys its ci-red bail on ⟦ci-repair⟧ only, and states a ⟦suite-repair⟧ step leaves the run its one CI repair attempt (#590)"
problems=()

if step_or_problem '### 4. Draft PR' "what the ci-red bail is keyed on"; then
  commands="$(section_commands)"
  keyed="$(first_record "$commands" -E '^[^#]*[$]s/event[.]sh bail cause=ci-red' -F '.tdd/issue-<n>.md')"
  if [[ -z "$keyed" ]]; then
    problems+=("no command line of $skill_md's Draft PR step bails with cause ci-red keyed on .tdd/issue-<n>.md")
  else
    grep -F "$ci_repair_mark" > /dev/null <<< "$keyed" ||
      problems+=("$skill_md's Draft PR step keys its ci-red bail without the $ci_repair_mark mark: $(printf '%.160s' "$keyed")")
    grep -F "$suite_repair_mark" > /dev/null <<< "$keyed" &&
      problems+=("$skill_md's Draft PR step keys its ci-red bail on $suite_repair_mark too, so a local full-suite repair spends the run's one CI repair attempt: $(printf '%.160s' "$keyed")")
  fi
  stated="$(first_record "$records" -F "$suite_repair_mark" -F "$ci_repair_mark" -E 'one ci repair attempt')"
  [[ -n "$stated" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step states that a ledger holding a $suite_repair_mark step and no $ci_repair_mark step still gets its one CI repair attempt")
fi
report "$name"

name="$skill_md's full-run paragraph says the repair step's text lists every red suite with its first FAIL - line, the prompts take it through their templates, and the conductor never edits a built prompt (#690)"
problems=()

if step_or_problem '### 4. Draft PR' "where the repair step's list of red suites comes from"; then
  paragraph="$(first_record "$records" -F 'repair step' -wF 'red' -F 'ledger')"
  if [[ -z "$paragraph" ]]; then
    problems+=("$skill_md's Draft PR step has no full-run paragraph adding a repair step to read")
  else
    grep -E 'every suite[^.]*red[^.]*first .?fail -' > /dev/null <<< "$paragraph" ||
      problems+=("$skill_md's full-run paragraph never says the repair step's text lists every suite the full run left red, each with its first FAIL - line: $(printf '%.160s' "$paragraph")")
    grep -E 'prompts[^.]*step.s text[^.]*templates?' > /dev/null <<< "$paragraph" ||
      problems+=("$skill_md's full-run paragraph never says the prompts take that list from the step text through their templates")
    grep -E 'never edits a built prompt' > /dev/null <<< "$paragraph" ||
      problems+=("$skill_md's full-run paragraph never says the conductor never edits a built prompt")
  fi
fi
report "$name"

name="$skill_md's Draft PR step readies the PR with gh_pr_ready <pr-number> \"\$(git rev-parse HEAD)\", so the ready_for_review CI run starts on the head just pushed (#879)"
problems=()

if step_or_problem '### 4. Draft PR' "which head the step readies the PR on"; then
  commands="$(section_commands)"
  readies="$(grep -E '(^|&& |; )gh_pr_ready( |$)' <<< "$commands" || true)"
  [[ -n "$readies" ]] ||
    problems+=("$skill_md's Draft PR step never runs gh_pr_ready, so which head it readies the PR on could not be checked")
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    grep -E 'gh_pr_ready <pr-number> "?[$][(]git rev-parse head[)]"?' > /dev/null <<< "$line" ||
      problems+=("$skill_md's Draft PR step readies the PR without the head sha it just pushed, so the ready_for_review run can start on the pre-rebase sha: $(printf '%.120s' "$line")")
  done <<< "$readies"
fi
report "$name"

name="$skill_md's Draft PR step says the branch's own full run, and any ⟦suite-repair⟧ step it adds, finishes green before rebase-onto-default.sh runs (#975)"
problems=()

if step_or_problem '### 4. Draft PR' "what has to be green before the step rebases"; then
  order="$(first_record "$(unmarked_records)" -E "own full(-suite)? run" -F "$suite_repair_mark" -wF 'green' -E 'before[^.]*rebase-onto-default[.]sh')"
  [[ -n "$order" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says the branch's own full run, and any $suite_repair_mark step it adds, finishes green before rebase-onto-default.sh runs, so the rebased tip's run can be read as replacing it")
fi
report "$name"

name="$skill_md's Draft PR step no longer calls the branch's own full run the only full-suite run, and names the rebased tip's run as the extra run a rebase owes (#975)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the branch's own full run is still called the only one"; then
  only="$(first_record "$(unmarked_records)" -E 'only full(-suite)? (gate|run)')"
  [[ -z "$only" ]] ||
    problems+=("$skill_md's Draft PR step still calls the branch's own full run the only full-suite run, which the rebased tip's run then contradicts: $(printf '%.160s' "$only")")
  extra="$(first_record "$(unmarked_records)" -E 'rebased tip.s run' -F 'extra run a rebase owes' -F 'replacement')"
  [[ -n "$extra" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step names the rebased tip's run as the extra run a rebase owes, not a replacement for the branch's own")
fi
report "$name"

name="$skill_md's Draft PR step bails on a red rebased tip with cause rebased-tip-red, not suite-red, after a clean rebase and after a verified conflict resolution alike (#975)"
problems=()

if step_or_problem '### 4. Draft PR' "which cause a red rebased tip bails with"; then
  plain="$(unmarked_records)"
  clean="$(first_record "$plain" -F 'an exit 0' -F 'rebased tip' -wF 'bail')"
  resolved="$(first_record "$plain" -F 'verify-rebase pass' -F 'rebased tip' -wF 'bail')"
  for path in clean resolved; do
    record="${!path}"
    if [[ -z "$record" ]]; then
      problems+=("no instruction of $skill_md's Draft PR step bails on a red rebased tip after a $path rebase")
      continue
    fi
    grep -F 'rebased-tip-red' > /dev/null <<< "$record" ||
      problems+=("$skill_md's Draft PR step bails on a red rebased tip after a $path rebase without naming cause rebased-tip-red: $(printf '%.160s' "$record")")
    grep -F 'suite-red' > /dev/null <<< "$record" &&
      problems+=("$skill_md's Draft PR step bails on a red rebased tip after a $path rebase with cause suite-red, which names a red run after a ⟦suite-repair⟧ step: $(printf '%.160s' "$record")")
  done
fi
report "$name"

name="$skill_md's bail on a red rebased tip runs git reset --hard <pre-rebase-sha> before Bailing's push (#975)"
problems=()

if step_or_problem '### 4. Draft PR' "what a red rebased tip's bail does to the branch before Bailing's push"; then
  reset="$(first_record "$(unmarked_records)" -F 'rebased-tip-red' -F 'git reset --hard <pre-rebase-sha>' -E 'bailing[^.]*push')"
  [[ -n "$reset" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step that bails with rebased-tip-red runs git reset --hard <pre-rebase-sha> before Bailing's push, so that push of the rebased branch is not a fast-forward and is rejected")
fi
report "$name"

name="$skill_md's bail on a red rebased tip after a verify-rebase PASS also runs git reset --hard <pre-rebase-sha> before Bailing's push (#975)"
problems=()

if step_or_problem '### 4. Draft PR' "what a red rebased tip's bail after a verified conflict resolution does to the branch before Bailing's push"; then
  record="$(first_record "$(unmarked_records)" -F 'only on a verify-rebase pass' -F 'rebased-tip-red')"
  resolved=""
  [[ "$record" =~ only\ on\ a\ verify-rebase\ pass.* ]] && resolved="${BASH_REMATCH[0]}"
  if [[ "$resolved" != *rebased-tip-red* ]]; then
    problems+=("no instruction of $skill_md's Draft PR step bails with rebased-tip-red after a verify-rebase PASS")
  else
    reset="$(first_record "$resolved" -F 'git reset --hard <pre-rebase-sha>' -E 'bailing[^.]*push')"
    [[ -n "$reset" ]] ||
      problems+=("$skill_md's bail on a red rebased tip after a verify-rebase PASS does not run git reset --hard <pre-rebase-sha> before Bailing's push, so that push of the rebased branch is not a fast-forward and is rejected: $(printf '%.160s' "$resolved")")
  fi
fi
report "$name"

name="$skill_md's Bailing cause-token list names rebased-tip-red and classifies it as a process failure (#975)"
problems=()

if section_or_problem '## Bailing' '^## ' "whether its cause-token list names rebased-tip-red"; then
  token="$(first_record "$records" -E '^ *- `rebased-tip-red`')"
  if [[ -z "$token" ]]; then
    problems+=("$skill_md's Bailing cause-token list has no rebased-tip-red entry, so a red rebased tip's bail names a cause the list never defines")
  elif ! grep -F '**process** failure' > /dev/null <<< "$token"; then
    problems+=("$skill_md's Bailing cause-token list names rebased-tip-red without classifying it as a **process** failure: $(printf '%.160s' "$token")")
  fi
fi
report "$name"

name="$skill_md's Guardrails invariant about opening the PR says neither \"exactly once\" nor \"the only full-suite gate\" (#1026)"
problems=()

invariant="$(first_record "$(section_records '## Guardrails' '^## ')" -F 'before you open the pr')"
if [[ -z "$invariant" ]]; then
  problems+=("$skill_md's Guardrails has no invariant about opening the PR to read — what it says of the full suite could not be checked")
else
  for phrase in 'exactly once' 'the only full-suite gate'; do
    grep -F "$phrase" > /dev/null <<< "$invariant" &&
      problems+=("$skill_md's Guardrails invariant still says \"$phrase\", so a conductor reading it as its checklist skips the rebased tip's run: $(printf '%.160s' "$invariant")")
  done
fi
report "$name"

name="$skill_md's Guardrails invariant about opening the PR names the branch's own full run, again after each suite-repair step, and the extra run on the rebased tip when sub-step 1 rebased the branch (#1026)"
problems=()

invariant="$(first_record "$(section_records '## Guardrails' '^## ')" -F 'before you open the pr')"
if [[ -z "$invariant" ]]; then
  problems+=("$skill_md's Guardrails has no invariant about opening the PR to read — which runs it names could not be checked")
else
  [[ -n "$(first_record "$invariant" -E 'own full(-suite)? (run|gate)')" ]] ||
    problems+=("$skill_md's Guardrails invariant never names the branch's own full run: $(printf '%.160s' "$invariant")")
  [[ -n "$(first_record "$invariant" -F "$suite_repair_mark")" ]] ||
    problems+=("$skill_md's Guardrails invariant never says the branch's own full run runs again after each $suite_repair_mark step: $(printf '%.160s' "$invariant")")
  [[ -n "$(first_record "$invariant" -F 'rebased tip' -wF 'rebased the branch')" ]] ||
    problems+=("$skill_md's Guardrails invariant never names the extra run on the rebased tip when sub-step 1 rebased the branch: $(printf '%.160s' "$invariant")")
fi
report "$name"

name="$skill_md's Draft PR step says a conductor never re-runs a failed CI job: a red check goes to the repair step or the ci-red bail, and re-running a flake is the operator's decision (#1282)"
problems=()

if step_or_problem '### 4. Draft PR' "whether a conductor may re-run a failed CI job"; then
  rule="$(first_record "$records" -F 'gh run rerun' -E 'never re-?runs?')"
  if [[ -z "$rule" ]]; then
    problems+=("$skill_md's Draft PR step never says a conductor does not re-run a failed CI job with gh run rerun, so a red check can be retried until a real failure reads as a flake")
  else
    [[ -n "$(first_record "$rule" -F 'repair step')" && -n "$(first_record "$rule" -F 'ci-red')" ]] ||
      problems+=("$skill_md's rule against re-running a failed CI job does not name the repair step and the ci-red bail as the only answer to a red check: $(printf '%.160s' "$rule")")
    [[ -n "$(first_record "$rule" -F 'operator')" ]] ||
      problems+=("$skill_md's rule against re-running a failed CI job does not leave re-running a known flake to the operator, outside a run: $(printf '%.160s' "$rule")")
  fi
fi
report "$name"

name="$skill_md's ci-red bail names each failed CI check: every ci-red bail mark in the Draft PR step carries the failed checks' names read from the head's check runs, and Bailing's ### ⛔ Bailed comment names them (#1282)"
problems=()

if step_or_problem '### 4. Draft PR' "whether its ci-red bail names the failed checks"; then
  bails="$(section_lines '### 4. Draft PR' '^## |^### ' | grep -F 'cause=ci-red')"
  [[ -n "$bails" ]] || problems+=("$skill_md's Draft PR step runs no ci-red bail at all")
  while IFS= read -r bail; do
    [[ -z "$bail" ]] && continue
    fields="$(printf '%s\n' "$bail" | grep -oE ' [a-z_]+=' | grep -vE '^ (cause|classification)=$')"
    [[ -n "$fields" && "$bail" == *check-runs* ]] ||
      problems+=("$skill_md's ci-red bail mark carries no field naming the failed checks read from the head's check runs: $(printf '%.200s' "$bail")")
  done <<< "$bails"
fi
if section_or_problem '## Bailing' '^## ' "whether its Bailed comment names the failed checks of a ci-red bail"; then
  comment="$(first_record "$records" -F '### ⛔ bailed' -F 'ci-red')"
  [[ -n "$comment" && -n "$(first_record "$comment" -F 'check')" ]] ||
    problems+=("$skill_md's ### ⛔ Bailed comment never says that a ci-red bail names each CI check that failed")
fi
report "$name"

finish
