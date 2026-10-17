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
#      block — `ci-timeout` on exit 2 — not only in prose. Its red is case 47's.
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
#  45. SKILL.md's Draft PR step says `rebase-onto-default.sh`'s exit code decides the next
#      action, so nothing after it — the rebased tip's full run in particular — starts until it
#      has returned, and never in the same message as the rebase.
#  46. SKILL.md's Draft PR sub-step 1 alone carries that sentence: the CI conflict-rebase copy
#      later in the same step does not stand in for it.
#  47. SKILL.md's Draft PR step says a red CI on the `metrics:` cost-report push appends one
#      `⟦ci-repair⟧` step with the `step-added` event a conductor-added step gets and returns
#      to the cycle loop, and bails `ci-red` only when the ledger already holds one.
#  48. SKILL.md's Draft PR step's `metrics:` push block bails `ci-red` behind a
#      `! grep -F '⟦ci-repair⟧'` guard, then itself records the `step-added` event and runs
#      `add-ledger-step.sh` with a `⟦ci-repair⟧` step and commits the ledger.
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

pass_or_problem() {
  record="$(first_record "$(section_records "$1" '^#')" -E '^ *- \*\*pass')"
  [[ -n "$record" ]] && return 0
  problems+=("$skill_md has no PASS branch under '$1' to read — $2 could not be checked")
  return 1
}

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
suite_repair_mark='⟦suite-repair⟧'

finish
