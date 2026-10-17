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
    grep -F -e "$ci_repair_mark" -e 'ledger-steps.sh has-mark ci-repair' > /dev/null <<< "$red" ||
      problems+=("$skill_md's Draft PR step recognises a second red CI result without the $ci_repair_mark mark or ledger-steps.sh has-mark ci-repair: $(printf '%.160s' "$red")")
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

name="$skill_md's Draft PR step bails on the metrics: push's CI wait with a command in its block, ci-timeout on exit 2 (#550)"
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
    for want in 'ci-timeout 2'; do
      cause="${want% *}" code="${want#* }"
      keyed="$(awk -v c="$cause" -v k="$code" '$1 == c && (" " $0 " ") ~ ("[^0-9]" k "[^0-9]")' <<< "$bails")"
      [[ -n "$keyed" ]] ||
        problems+=("no command line of $skill_md's Draft PR step bails with cause $cause on the metrics: push's wait-ci.sh exit $code, in the block after that wait")
    done
  fi
fi
report "$name"

name="#1431 $skill_md's Draft PR step says a red CI on the metrics: cost-report push appends one ⟦ci-repair⟧ step with the step-added event and returns to the cycle loop, bailing ci-red only when the ledger already holds a ⟦ci-repair⟧ step"
problems=()

if step_or_problem '### 4. Draft PR' "what a red CI on the metrics: push does"; then
  plain="$(unmarked_records)"
  said="$(grep -oE 'the metrics: push .*' <<< "$plain")"
  if [[ -z "$said" ]]; then
    problems+=("no instruction of $skill_md's Draft PR step describes the metrics: push's CI wait, so what its red does could not be checked")
  else
    repairs="$(first_record "$said" -E 'exit 1|red' -F '⟦ci-repair⟧' -F 'step-added' -F 'cycle loop' -E 'bails?[^.]*ci-red[^.]*only[^.]*already[^.]*⟦ci-repair⟧|only[^.]*already[^.]*⟦ci-repair⟧[^.]*bails?[^.]*ci-red')"
    [[ -n "$repairs" ]] ||
      problems+=("$skill_md's Draft PR step does not say a red CI on the metrics: push appends one ⟦ci-repair⟧ step with the step-added event and returns to the cycle loop, bailing ci-red only when the ledger already holds a ⟦ci-repair⟧ step, so a CI-only flake on the cost-report push still sends a finished run to a human: $(printf '%.160s' "$said")")
    reversed="$(first_record "$said" -F 'not a repair step')"
    [[ -z "$reversed" ]] ||
      problems+=("$skill_md's Draft PR step still says the metrics: push's red is not a repair step: $(printf '%.160s' "$reversed")")
  fi
fi
report "$name"

name="#1431 $skill_md's Draft PR step's metrics: push block bails ci-red on a red CI only when the ledger already holds a ⟦ci-repair⟧ step, then itself appends the ⟦ci-repair⟧ step and records its step-added event"
problems=()

if step_or_problem '### 4. Draft PR' "what the metrics: push's command block does on a red CI"; then
  commands="$(section_commands)"
  metrics_at="$(line_of "$metrics_commit")"
  if [[ -z "$metrics_at" ]]; then
    problems+=("$skill_md's Draft PR step makes no metrics: commit, so what its push's command block does on a red CI could not be checked")
  else
    after_wait="$(WAIT_RE="^$wait_ci_run" awk -v from="$metrics_at" '
        NR <= from { next }
        /^```/ { if (waited) exit; next }
        $0 ~ ENVIRON["WAIT_RE"] { waited = 1; next }
        waited' <<< "$commands")"
    guard_at="$(awk '/[$]s\/event[.]sh bail cause=ci-red/ && /! (grep -f .⟦ci-repair⟧.|[$]s\/ledger-steps[.]sh has-mark ci-repair) [^|]*[|][|] [^|]*[$]s\/event[.]sh bail cause=ci-red/ { print NR; exit }' <<< "$after_wait")"
    if [[ -z "$guard_at" ]]; then
      problems+=("no command line after the metrics: push's wait-ci.sh bails ci-red behind a ! grep -F '⟦ci-repair⟧' or ! \$S/ledger-steps.sh has-mark ci-repair guard, so a red CI there either bails on its first red with no repair step or appends a second ⟦ci-repair⟧ step instead of bailing: $(printf '%.200s' "$(grep -F 'cause=ci-red' <<< "$after_wait")")")
    else
      added="$(awk -v from="$guard_at" 'NR > from && /[$]s\/event[.]sh step-added/' <<< "$after_wait")"
      [[ -n "$added" ]] ||
        problems+=("no command line after the metrics: push's ci-red guard records a step-added event, so the ⟦ci-repair⟧ step a red CI there appends is missing from the run's metrics")
      appended="$(awk -v from="$guard_at" 'NR > from && /[$]s\/add-ledger-step[.]sh/ && /⟦ci-repair⟧/' <<< "$after_wait")"
      [[ -n "$appended" ]] ||
        problems+=("no command line after the metrics: push's ci-red guard runs add-ledger-step.sh with a ⟦ci-repair⟧ step, so a conductor running the block top to bottom never reaches the repair")
      awk -v from="$guard_at" 'NR > from && /[$]s\/add-ledger-step[.]sh/ && /⟦ci-repair⟧/ { added = 1; next } added && /git add [.]tdd\/issue-<n>[.]md/ && /git commit / { found = 1; exit } END { exit !found }' <<< "$after_wait" ||
        problems+=("no command line after the metrics: push's add-ledger-step.sh commits .tdd/issue-<n>.md, so the ⟦ci-repair⟧ step it appends is left out of the committed ledger a resumed run reads")
    fi
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

name="$skill_md's Draft PR step bails on a second red full run of this run with a suite-red command line that reads nothing from the ledger, naming every suite still red (#590, #1607)"
problems=()

if step_or_problem '### 4. Draft PR' "how the step recognises a second red full run"; then
  commands="$(section_commands)"
  keyed="$(awk '/^[^#]*[$]s\/event[.]sh bail / && index($0, "cause=suite-red") && index($0, "suites=") { print; exit }' <<< "$commands")"
  if [[ -z "$keyed" ]]; then
    problems+=("no command line of $skill_md's Draft PR step bails with cause=suite-red and the suites still red, so a second red full run is recognised only in prose")
  elif grep -F '.tdd/issue-<n>.md' > /dev/null <<< "$keyed"; then
    problems+=("$skill_md's Draft PR step's suite-red bail still names .tdd/issue-<n>.md, though add-ledger-step.sh's per-run refusal, not the ledger, says the red run is the second: $(printf '%.160s' "$keyed")")
  fi
  second="$(first_record "$records" -wF 'bail' -E 'second red|red again' -F 'repair step')"
  grep -E 'every (suite still red|red suite|failing suite|still-red suite)' > /dev/null <<< "$second" ||
    problems+=("$skill_md's Draft PR step's second-red bail no longer names every suite still red: $(printf '%.120s' "$second")")
fi
report "$name"

name="#1607 $skill_md's Draft PR step bails suite-red, naming every suite still red, when add-ledger-step.sh exits 1 on the ⟦suite-repair⟧ insertion"
problems=()

if step_or_problem '### 4. Draft PR' "what the step does when add-ledger-step.sh refuses the repair step"; then
  refusal="$(first_record "$(tr -d '*`' <<< "$records")" -F 'add-ledger-step.sh' -E 'exit(s|ing)? 1' -F 'suite-red' -E 'every (suite still red|red suite|failing suite|still-red suite)')"
  [[ -n "$refusal" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says that add-ledger-step.sh exiting 1 on the ⟦suite-repair⟧ insertion bails with cause suite-red, naming every suite still red")
fi
report "$name"

name="#1607 $skill_md's Draft PR step states the cap is one ⟦suite-repair⟧ step per run, that add-ledger-step.sh and not the conductor's judgement decides it, and no longer greps the whole ledger for the mark"
problems=()

if step_or_problem '### 4. Draft PR' "what decides the suite-repair cap"; then
  rule="$(first_record "$(tr -d '*`' <<< "$records")" -F 'add-ledger-step.sh' -E 'one [^.]*suite-repair[^.]* per run|per run[^.]*suite-repair' -F 'resume' -E 'not the conductor|conductor.s judgement')"
  [[ -n "$rule" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says the cap is one ⟦suite-repair⟧ step per run, a resume starting a new run, and that add-ledger-step.sh rather than the conductor's judgement decides it")
  grep -E '^[^#]*grep .*suite-repair.*[.]tdd/issue-<n>[.]md' > /dev/null <<< "$(section_commands)" &&
    problems+=("$skill_md's Draft PR step still greps .tdd/issue-<n>.md for ⟦suite-repair⟧, counting repair steps across the whole ledger")
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
    grep -F -e "$ci_repair_mark" -e 'ledger-steps.sh has-mark ci-repair' > /dev/null <<< "$keyed" ||
      problems+=("$skill_md's Draft PR step keys its ci-red bail without the $ci_repair_mark mark or ledger-steps.sh has-mark ci-repair: $(printf '%.160s' "$keyed")")
    grep -F -e "$suite_repair_mark" -e 'has-mark suite-repair' > /dev/null <<< "$keyed" &&
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

name="$skill_md's Draft PR step says rebase-onto-default.sh's exit code decides the next action, so nothing after it, the rebased tip's full run included, starts until it has returned, and never in the same message (#1287)"
problems=()

if step_or_problem '### 4. Draft PR' "whether the rebase's exit code gates the next action"; then
  gate="$(first_record "$(unmarked_records)" -F 'rebase-onto-default.sh' -F 'exit code' -E 'decides?[^.]*next action' -F 'full' -E 'until[^.]*returned' -F 'same message')"
  [[ -n "$gate" ]] ||
    problems+=("no instruction of $skill_md's Draft PR step says rebase-onto-default.sh's exit code decides the next action, so nothing after it — the rebased tip's full run in particular — is started until it has returned, and never in the same message as the rebase; a conductor batching tool calls starts the full run beside a rebase that exits 3")
fi
report "$name"

name="#1287 $skill_md's Draft PR sub-step 1, the one that asks the two questions, says on its own that rebase-onto-default.sh's exit code decides the next action, so nothing after it, the rebased tip's full run included, starts until it has returned, and never in the same message"
problems=()

if step_or_problem '### 4. Draft PR' "whether sub-step 1's rebase exit code gates the next action"; then
  sub_step_1="$(section_lines '### 4. Draft PR' '^## |^### ' | awk '/^ *1\. \*\*/ { inside = 1 } /^ *2\. \*\*/ { inside = 0 } inside' | records_of | tr -d '*`')"
  if [[ -z "$sub_step_1" ]]; then
    problems+=("$skill_md's Draft PR step has no sub-step 1 (1. **Ask the two questions …) to read — nothing could be checked")
  else
    gate="$(first_record "$sub_step_1" -F 'rebase-onto-default.sh' -F 'exit code' -E 'decides?[^.]*next action' -F 'full' -E 'until[^.]*returned' -F 'same message')"
    [[ -n "$gate" ]] ||
      problems+=("no instruction of $skill_md's Draft PR sub-step 1 says rebase-onto-default.sh's exit code decides the next action, so nothing after it — the rebased tip's full run in particular — is started until it has returned, and never in the same message as the rebase; the CI conflict-rebase copy later in the step does not stand in for it")
  fi
fi
report "$name"

name="#1613 $skill_md's Draft PR step decides whether the ledger already holds a CI repair step with ledger-steps.sh has-mark ci-repair, never a whole-ledger grep -F of the ⟦ci-repair⟧ mark"
problems=()

if step_or_problem '### 4. Draft PR' "how the ci-red bail lines find an existing CI repair step"; then
  bails="$(section_commands | grep -F -e 'cause=ci-red' -e 'no_repair=$?' || true)"
  if [[ -z "$bails" ]]; then
    problems+=("$skill_md's Draft PR step has no command line bailing with cause ci-red, so how it finds an existing CI repair step could not be checked")
  else
    while IFS= read -r line; do
      grep -F 'ledger-steps.sh has-mark ci-repair' > /dev/null <<< "$line" ||
        problems+=("a ci-red bail line of $skill_md's Draft PR step never asks ledger-steps.sh has-mark ci-repair, so a step that only quotes ⟦ci-repair⟧ in its prose counts as a CI repair: $(printf '%.160s' "$line")")
      if grep -iF "grep -F '⟦ci-repair⟧'" > /dev/null <<< "$line"; then
        problems+=("a ci-red bail line of $skill_md's Draft PR step still greps the whole ledger for ⟦ci-repair⟧: $(printf '%.160s' "$line")")
      fi
    done <<< "$bails"
  fi
  prose="$(tr -d '*`' <<< "$records")"
  grep -iF 'greps for ⟦ci-repair⟧' > /dev/null <<< "$prose" &&
    problems+=("$skill_md's Draft PR step still says the ci-red bail greps for ⟦ci-repair⟧, though it asks ledger-steps.sh has-mark ci-repair")
  grep -iF 'keys on ⟦ci-repair⟧ only' > /dev/null <<< "$prose" ||
    problems+=("$skill_md's Draft PR step no longer says the ci-red bail keys on ⟦ci-repair⟧ only")
fi
report "$name"

finish
