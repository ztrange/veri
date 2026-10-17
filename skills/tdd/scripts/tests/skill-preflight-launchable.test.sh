#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md's preflight checks before its baseline run, read
# as text.
#
# Contract under test:
#   1. Some preflight check names `leaf-launchable.sh`, and it comes before the check that
#      runs the baseline suite (the one calling `detect-test-command.sh`).
#   2. The same section refuses a bad `VERI_STEP_GROWTH` where it refuses a bad
#      `VERI_REFACTOR_BUDGET`.
#   3. The same item calls `step-budget.sh` beside `refactor-budget.sh 0`, and spells its
#      exit 2 in the paragraph that makes the call.
#   4. The item that checks `claude auth status` checks GitHub with `gh api user`, and the
#      paragraph that names it says a non-zero exit stops the run as a preflight failure.
#   5. The fast-tier baseline call (`detect-test-command.sh --tier fast`) comes after the line
#      that has `issue-worktree.sh` cut the branch and `cd`s into its worktree.
#   6. The baseline item sits before the plan section, and a sentence of it that stops on a red
#      baseline calls the stop preflight-class and says the caller's checkout does not change it.
#   7. The full-tier call (`detect-test-command.sh --tier all`) comes after the fast-tier one with
#      no line between them that leaves the worktree or moves its commit, and the
#      `leaf-timeout.sh ... --full` call comes after it.
#   8. The Resume section has a sentence saying the baseline runs on the branch head, in its
#      existing worktree, before any cycle of the resumed run.
#   9. The line that writes `$PPID` to `.tdd/conductor.pid` comes after the `issue-worktree.sh`
#      line that `cd`s into the worktree and before the first fast-tier baseline command
#      (`detect-test-command.sh --tier fast` or `detach-command.sh start`) after it.
#  10. The paragraph naming the **worktree guard** has a sentence naming the lock,
#      `preflight step 3` and `before the baseline`; no sentence of step 1.2's item pairs a
#      take/write verb with the word `here`, and no sentence anywhere says `step 1.2 takes`
#      (or writes, locks) or `taken in step 1.2` (or written, took, wrote).
#  11. Between the line that `cd`s into the worktree and the first fast-tier baseline command
#      after it, a sentence names `rebase-onto-default.sh` for a resumed run whose ledger
#      exists, and a sentence says a new branch's run does not rebase there.
#  12. In that same span, a sentence says the resume rebase's exit 3 goes on unchanged, one
#      says its exit 1 goes on from the old base and leaves the conflict to the Draft PR step,
#      and one says its exit 2 bails `no-verdict`.
#  13. Preflight step 3's item names `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`
#      after the fast-tier baseline command, in a sentence that says `green`, and has a sentence
#      saying never a bare force.
#  14. Preflight step 3's item has a sentence saying a red baseline on the rebased tip resets
#      to `<pre-rebase-sha>` before the run bails.
#  15. Preflight step 3's item, after its `rebase-onto-default.sh` call, has an `event.sh <name>`
#      line whose arguments carry `<pre-rebase-sha>` and the rebased sha (`rebased` or
#      `rev-parse HEAD`), and the Draft PR section has no `event.sh <name>` of that name.
#  16. Preflight step 3's item captures `git status --porcelain` into a variable, then runs
#      `git reset --hard HEAD`, both before its first line naming `rebase-onto-default.sh`; and
#      its first sentence naming `<pre-rebase-sha>` says it is that script's first stdout line.
#  17. Preflight step 3's item has a sentence in which `not`, `never` or `no` comes at most three
#      words before `bare force`, so another negative word elsewhere in it does not count.
#  17. Preflight step 3's item has a sentence in which `not`, `never` or `no` comes at most three
#      words before `bare force`, so another negative word elsewhere in it does not count.
#  18. Preflight step 3's fenced capture-and-discard block, run in a resumed worktree holding an
#      untracked file at a path the default branch has since added, leaves a tree that
#      `rebase-onto-default.sh` rebases with exit 0.
#  19. Preflight step 3's fenced capture-and-discard block, run in a resumed worktree holding a
#      killed leaf's untracked file, leaves that file listed in `$stray`.
#  20. Preflight step 3's fenced capture-and-discard block, run in a resumed worktree whose
#      `.gitignore` names `.tdd/`, leaves a `.tdd/` leaf log in place.
#  21. Preflight step 3's fenced capture-and-discard block, run in a resumed worktree under the
#      repository's own `.tdd/*` / `!.tdd/issue-*.md` patterns, keeps an untracked
#      `.tdd/issue-1-refactor-owed.md` out of `$stray` and on disk.
#
# Run: scripts/tests/skill-preflight-launchable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

launchable="leaf-launchable.sh"
detector="detect-test-command.sh"
growth='VERI_STEP_GROWTH'
step_budget='step-budget.sh'
refactor_budget='refactor-budget.sh 0'
refusal='exits? 2'
claude_auth='claude auth status'
gh_check='gh api user'
nonzero='non-zero'
preflight='### 0. Preflight'
fast_call='detect-test-command.sh --tier fast'
full_call='detect-test-command.sh --tier all'
timeout_call='leaf-timeout.sh'
timeout_flag='--full'
worktree_call='issue-worktree.sh'
enter_call='cd "$wt"'
plan_heading='### 2. Scope & plan'
red_phrase='red baseline'
callers="caller's checkout"
resume_heading='## Resume'
branch_head='branch head'
pid_write='> .tdd/conductor.pid'
pid_value='"$PPID"'
detach_start='detach-command.sh start'
guard_name='**worktree guard**'
step1_heading='### 1. Read the issue'
slug_item='**Derive the slug'
rebase_call='rebase-onto-default.sh'
lease_push='push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>'
draft_heading='### 4. Draft PR'
reset_head='git reset --hard HEAD'


source "$HERE/lib/harness.sh"
source "$HERE/lib/section-end.sh"

heading_at() {
  awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md"
}

sec_start=0 sec_end=0
section() {
  sec_start="$(heading_at "$1")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  sec_end="$(section_end "$md" "$sec_start")"
  return 0
}

call_at() {
  awk -v s="$sec_start" -v e="$sec_end" -v want="$1" \
    'NR >= s && NR <= e && index($0, want) { print NR; exit }' "$md"
}

item_last_line() {
  local next
  next="$(awk -v s="$(($1 + 1))" -v e="$sec_end" 'NR >= s && NR <= e && /^[0-9]+\./ { print NR; exit }' "$md")"
  if [[ -n "$next" ]]; then echo "$((next - 1))"; else echo "$sec_end"; fi
}

item_around() {
  local at="$1" start
  start="$(awk -v s="$sec_start" -v at="$at" 'NR >= s && NR <= at && /^[0-9]+\./ { n = NR } END { print n + 0 }' "$md")"
  [[ "$start" -gt 0 ]] || start="$sec_start"
  sed -n "${start},$(item_last_line "$at")p" "$md"
}

paragraph_around() {
  awk -v at="$1" '
    NR <= at { if ($0 ~ /^[[:space:]]*$/) buf = ""; else if ($0 ~ /^[0-9]+\./) buf = $0 "\n"; else buf = buf $0 "\n"; next }
    $0 ~ /^[[:space:]]*$/ || $0 ~ /^[0-9]+\./ { exit }
    { buf = buf $0 "\n" }
    END { printf "%s", buf }' "$md"
}

preflight_or_problem() {
  section "$preflight" && return 0
  problems+=("$skill_md has no '$preflight' section — where $1 would sit could not be read")
  return 1
}


sentences() {
  tr '\n' ' ' | awk '{ gsub(/  +/, " "); gsub(/[.] /, ".\n"); print }'
}

negated() {
  grep -iE '(^|[^[:alpha:]])(not|never|no)([^[:alpha:]]|$)'
}

rebase_span() {
  enter_at="$(awk -v w="$worktree_call" -v c="$enter_call" 'index($0, w) && index($0, c) { print NR; exit }' "$md")"
  if [[ -z "$enter_at" ]]; then
    problems+=("$skill_md has no line that runs $worktree_call and then $enter_call, so where the run enters the issue's worktree could not be read")
    return 1
  fi
  base_at="$(awk -v s="$((enter_at + 1))" -v f="$fast_call" -v d="$detach_start" \
    'NR >= s && (index($0, f) || index($0, d)) { print NR; exit }' "$md")"
  if [[ -z "$base_at" ]]; then
    problems+=("$skill_md names neither $fast_call nor $detach_start after line $enter_at enters the worktree, so where the baseline starts could not be read")
    return 1
  fi
  between="$(sed -n "${enter_at},${base_at}p" "$md" | sentences)"
}

resume_step3() {
  rebase_span && preflight_or_problem "$1" || return 1
  step3="$(item_around "$enter_at")"
  item_end="$(item_last_line "$enter_at")"
}

step3_line_of() {
  awk -v s="$enter_at" -v e="$item_end" -v n="$1" 'NR >= s && NR <= e && index($0, n) { print NR; exit }' "$md"
}

finish
