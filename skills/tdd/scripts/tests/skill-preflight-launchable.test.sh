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

name="#1297 $skill_md has a resumed run, one whose worktree and ledger already exist, run $rebase_call before its preflight baseline, and a new branch's run not rebase there"
problems=()

if rebase_span; then
  resumed="$(grep -F -- "$rebase_call" <<< "$between" | grep -iF 'resum' | grep -iF 'ledger')"
  [[ -n "$resumed" ]] ||
    problems+=("$skill_md between line $enter_at ($enter_call) and line $base_at (the fast-tier baseline) has no sentence saying a resumed run, whose worktree and ledger already exist, runs $rebase_call, so a resumed run's baseline runs on its old base")
  fresh="$(grep -iF 'new branch' <<< "$between" | grep -iF 'rebase' | negated)"
  [[ -n "$fresh" ]] ||
    problems+=("$skill_md between line $enter_at ($enter_call) and line $base_at (the fast-tier baseline) has no sentence saying a new branch's run does not rebase there")
fi

report "$name"

name="#1297 $skill_md says the resume $rebase_call's exit 3 goes on unchanged, its exit 1 goes on from the old base and leaves the conflict to the Draft PR step, and its exit 2 bails no-verdict"
problems=()

if rebase_span; then
  nothing="$(grep -iE 'exits? 3' <<< "$between" | grep -iF 'unchanged')"
  [[ -n "$nothing" ]] ||
    problems+=("$skill_md between line $enter_at ($enter_call) and line $base_at (the fast-tier baseline) has no sentence saying the resume rebase's exit 3 goes on unchanged")
  conflict="$(grep -iE 'exits? 1' <<< "$between" | grep -iF 'old base' | grep -iF 'Draft PR')"
  [[ -n "$conflict" ]] ||
    problems+=("$skill_md between line $enter_at ($enter_call) and line $base_at (the fast-tier baseline) has no sentence saying the resume rebase's exit 1 goes on from the old base and leaves the conflict to the Draft PR step")
  noanswer="$(grep -iE 'exits? 2' <<< "$between" | grep -iF 'bail' | grep -F 'no-verdict')"
  [[ -n "$noanswer" ]] ||
    problems+=("$skill_md between line $enter_at ($enter_call) and line $base_at (the fast-tier baseline) has no sentence saying the resume rebase's exit 2 bails no-verdict")
fi

report "$name"

resume_step3() {
  rebase_span && preflight_or_problem "$1" || return 1
  step3="$(item_around "$enter_at")"
  item_end="$(item_last_line "$enter_at")"
}

step3_line_of() {
  awk -v s="$enter_at" -v e="$item_end" -v n="$1" 'NR >= s && NR <= e && index($0, n) { print NR; exit }' "$md"
}

name="#1297 $skill_md publishes a resume rebase that moved the branch, once the baseline is green, with $lease_push, never a bare force"
problems=()

if resume_step3 "the resume rebase's push"; then
  push_at="$(step3_line_of "$lease_push")"
  if [[ -z "$push_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) never names $lease_push, so a resume rebase that moved the branch is left unpublished or pushed without a pinned lease")
  else
    [[ "$push_at" -gt "$base_at" ]] ||
      problems+=("$skill_md:$push_at names $lease_push before line $base_at starts the fast-tier baseline, so the rebased tip is published before any suite proved it green")
    green="$(sentences <<< "$step3" | grep -F -- "$lease_push" | grep -iF 'green')"
    [[ -n "$green" ]] ||
      problems+=("$skill_md:$push_at's sentence naming $lease_push does not say it runs once the baseline is green")
  fi
  bare="$(sentences <<< "$step3" | grep -iF 'bare force' | negated)"
  [[ -n "$bare" ]] ||
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no sentence saying the resume rebase is never published with a bare force")
fi

report "$name"

name="#1297 $skill_md resets a red baseline on the resume-rebased tip to <pre-rebase-sha> before the run bails"
problems=()

if resume_step3 "the resume rebase's reset"; then
  reset="$(sentences <<< "$step3" | grep -iwF 'red' | grep -iF 'reset' | grep -F '<pre-rebase-sha>' | grep -iF 'bail')"
  [[ -n "$reset" ]] ||
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no sentence saying a red baseline on the rebased tip resets to <pre-rebase-sha> before the run bails, so a bailed resume leaves the branch on a rebased tip no suite proved green")
fi

report "$name"

name="#1297 $skill_md marks a resume rebase that moved the branch in the run log as its own event, carrying the pre-rebase and rebased shas, named apart from the Draft PR step's rebase"
problems=()

if resume_step3 "the resume rebase's event"; then
  rebase_at="$(step3_line_of "$rebase_call")"
  mark="$(sed -n "${rebase_at:-$enter_at},${item_end}p" "$md" | grep -oE 'event\.sh [a-z][a-z-]*( [^`]*)?' | grep -F '<pre-rebase-sha>' | sed -n 1p)"
  event_name="$(awk '{ print $2 }' <<< "$mark")"
  if [[ -z "$event_name" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no event.sh mark after $rebase_call whose arguments carry <pre-rebase-sha>, so a resume rebase that moved the branch leaves nothing in the run log")
  else
    grep -E 'rebased|rev-parse HEAD' <<< "${mark#event.sh "$event_name"}" > /dev/null ||
      problems+=("$skill_md's event.sh $event_name mark carries <pre-rebase-sha> but not the rebased sha: $mark")
    if section "$draft_heading"; then
      sed -n "${sec_start},${sec_end}p" "$md" | grep -E "event\.sh $event_name( |\$|\`)" > /dev/null &&
        problems+=("$skill_md's $draft_heading section also writes event.sh $event_name, so a metrics reading cannot tell the resume rebase from the Draft PR step's")
    else
      problems+=("$skill_md has no '$draft_heading' section, so whether its rebase records the same event could not be read")
    fi
  fi
fi

report "$name"

name="#1297 $skill_md captures and resets a dirty resume worktree before the resume $rebase_call, and says <pre-rebase-sha> is its first stdout line before first using it"
problems=()

if resume_step3 "the resume rebase's capture-and-reset"; then
  rebase_at="$(step3_line_of "$rebase_call")"
  capture_at="$(awk -v s="$enter_at" -v e="$item_end" 'NR >= s && NR <= e && /="\$\(git status --porcelain\)"/ { print NR; exit }' "$md")"
  reset_at="$(step3_line_of "$reset_head")"
  if [[ -z "$capture_at" || -z "$reset_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) does not capture git status --porcelain into a variable and then run $reset_head, so a killed leaf's stray edit meets the resume rebase on a dirty tree")
  elif [[ -n "$rebase_at" ]] && ! [[ "$capture_at" -lt "$reset_at" && "$reset_at" -lt "$rebase_at" ]]; then
    problems+=("$skill_md's preflight step 3 has the capture at line $capture_at, $reset_head at line $reset_at and $rebase_call at line $rebase_at: the rebase must come after the capture-and-reset")
  fi
  first_use="$(sed -n "${enter_at},${item_end}p" "$md" | sentences | grep -F '<pre-rebase-sha>' | sed -n 1p)"
  grep -F -- "$rebase_call" <<< "$first_use" | grep -iE 'first (stdout )?line' > /dev/null ||
    problems+=("$skill_md's preflight step 3 first uses <pre-rebase-sha> without saying it is $rebase_call's first stdout line: $first_use")
fi

report "$name"

name="#1297 $skill_md's preflight step 3 says never a bare force with the negation on the bare force itself, not on another word of the sentence"
problems=()

if resume_step3 "the resume rebase's bare-force sentence"; then
  governed="$(sentences <<< "$step3" | grep -iE '(^|[^[:alpha:]])(not|never|no)([[:space:]]+[[:alpha:]]+){0,3}[[:space:]]+bare force')"
  [[ -n "$governed" ]] ||
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no sentence whose not, never or no governs 'bare force': $(sentences <<< "$step3" | grep -iF 'bare force' | sed -n 1p)")
fi

report "$name"

name="#1485 $skill_md's preflight step 6 reads an empty or whitespace-only model variable as unset and stops only on a value with internal whitespace"
problems=()

if preflight_or_problem "the leaf-model item"; then
  at="$(call_at '$S/leaf-model.sh develop-red')"
  if [[ -z "$at" ]]; then
    problems+=("$skill_md's '$preflight' section never calls leaf-model.sh develop-red, so the item on leaf models could not be read")
  else
    model_item="$(item_around "$at" | sentences)"
    grep -iE 'empty' <<< "$model_item" | grep -iF 'whitespace-only' | grep -iE 'unset' > /dev/null ||
      problems+=("$skill_md:$at: no sentence of the leaf-model item says an empty or whitespace-only variable is treated as unset")
    grep -iF 'internal whitespace' <<< "$model_item" | grep -iE 'exit 2|stops?' > /dev/null ||
      problems+=("$skill_md:$at: no sentence of the leaf-model item says a value with internal whitespace is what stops the run")
  fi
fi

report "$name"

name="#1420 $skill_md's preflight discard removes a killed leaf's untracked file at a path the default branch has since added, so the resume $rebase_call exits 0, not 2"
problems=()

if resume_step3 "the resume discard's untracked files"; then
  capture_at="$(awk -v s="$enter_at" -v e="$item_end" 'NR >= s && NR <= e && /="\$\(git status --porcelain\)"/ { print NR; exit }' "$md")"
  if [[ -z "$capture_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no line capturing git status --porcelain, so its discard block could not be found")
  else
    discard="$(awk -v c="$capture_at" '
      NR < c && /^[[:space:]]*```/ { body = ""; next }
      NR < c { body = body $0 "\n"; next }
      /^[[:space:]]*```/ { printf "%s", body; exit }
      { body = body $0 "\n" }' "$md")"
    dir="$(scratch_dir)"
    new_repo --bare -b main "$dir/origin.git" >/dev/null 2>&1
    new_repo -b main "$dir/seed" >/dev/null 2>&1
    echo "base" > "$dir/seed/file.txt"
    git -C "$dir/seed" add -A >/dev/null 2>&1
    git -C "$dir/seed" commit -q -m "initial" >/dev/null 2>&1
    git -C "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
    git clone -q "$dir/origin.git" "$dir/wt" >/dev/null 2>&1
    git -C "$dir/wt" config user.name veri
    git -C "$dir/wt" config user.email veri@example.test
    git -C "$dir/wt" checkout -q -b tdd/1-a-run >/dev/null 2>&1
    echo "the run's work" > "$dir/wt/work.txt"
    git -C "$dir/wt" add -A >/dev/null 2>&1
    git -C "$dir/wt" commit -q -m "feat: a step's green commit (#1)" >/dev/null 2>&1
    echo "another run's work" > "$dir/seed/other.txt"
    git -C "$dir/seed" add -A >/dev/null 2>&1
    git -C "$dir/seed" commit -q -m "feat: another run merged (#2)" >/dev/null 2>&1
    git -C "$dir/seed" push -q "$dir/origin.git" main >/dev/null 2>&1
    git -C "$dir/wt" fetch -q origin >/dev/null 2>&1
    echo "a killed leaf's half-written file" > "$dir/wt/other.txt"
    (cd "$dir/wt" && bash -c "$discard") >/dev/null 2>&1
    (cd "$dir/wt" && bash "$HERE/../$rebase_call") > "$dir/rebase.out" 2> "$dir/rebase.err"
    rc=$?
    [[ "$rc" -eq 0 ]] ||
      problems+=("$rebase_call after preflight step 3's discard block, exit: want 0, got $rc — stderr: $(cat "$dir/rebase.err")")
  fi
fi

report "$name"

name="#1420 $skill_md's preflight discard captures a killed leaf's untracked file in \$stray before removing it, so the ▶️ Resuming comment names it"
problems=()

if resume_step3 "the resume discard's stray capture"; then
  capture_at="$(awk -v s="$enter_at" -v e="$item_end" 'NR >= s && NR <= e && /="\$\(git status --porcelain\)"/ { print NR; exit }' "$md")"
  if [[ -z "$capture_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no line capturing git status --porcelain, so its discard block could not be found")
  else
    discard="$(awk -v c="$capture_at" '
      NR < c && /^[[:space:]]*```/ { body = ""; next }
      NR < c { body = body $0 "\n"; next }
      /^[[:space:]]*```/ { printf "%s", body; exit }
      { body = body $0 "\n" }' "$md")"
    dir="$(scratch_dir)"
    new_repo -b main "$dir/wt" >/dev/null 2>&1
    echo "base" > "$dir/wt/file.txt"
    git -C "$dir/wt" add -A >/dev/null 2>&1
    git -C "$dir/wt" commit -q -m "initial" >/dev/null 2>&1
    echo "a killed leaf's half-written file" > "$dir/wt/other.txt"
    (cd "$dir/wt" && STRAY_OUT="$dir/stray.out" bash -c "$discard"$'\nprintf \'%s\\n\' "$stray" > "$STRAY_OUT"') >/dev/null 2>&1
    grep -Fx -- '?? other.txt' "$dir/stray.out" > /dev/null 2>&1 ||
      problems+=("\$stray after preflight step 3's discard block does not list the untracked file: want a line '?? other.txt', got: $(cat "$dir/stray.out" 2>/dev/null)")
  fi
fi

report "$name"

name="#1420 $skill_md's preflight discard never removes a file .gitignore ignores, so a .tdd/ leaf log survives it"
problems=()

if resume_step3 "the resume discard's ignored files"; then
  capture_at="$(awk -v s="$enter_at" -v e="$item_end" 'NR >= s && NR <= e && /="\$\(git status --porcelain\)"/ { print NR; exit }' "$md")"
  if [[ -z "$capture_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no line capturing git status --porcelain, so its discard block could not be found")
  else
    discard="$(awk -v c="$capture_at" '
      NR < c && /^[[:space:]]*```/ { body = ""; next }
      NR < c { body = body $0 "\n"; next }
      /^[[:space:]]*```/ { printf "%s", body; exit }
      { body = body $0 "\n" }' "$md")"
    dir="$(scratch_dir)"
    new_repo -b main "$dir/wt" >/dev/null 2>&1
    echo ".tdd/" > "$dir/wt/.gitignore"
    git -C "$dir/wt" add -A >/dev/null 2>&1
    git -C "$dir/wt" commit -q -m "initial" >/dev/null 2>&1
    mkdir -p "$dir/wt/.tdd"
    echo "a leaf's log" > "$dir/wt/.tdd/issue-1-leaf.log"
    (cd "$dir/wt" && bash -c "$discard") >/dev/null 2>&1
    [[ -f "$dir/wt/.tdd/issue-1-leaf.log" ]] ||
      problems+=("preflight step 3's discard block removed the ignored run-state file .tdd/issue-1-leaf.log: want it kept, got: $(ls -A "$dir/wt" 2>&1 | tr '\n' ' ')")
  fi
fi

report "$name"

name="#1420 $skill_md's preflight discard never loses an untracked .tdd/ run-state file the real .gitignore un-ignores: the refactor-owed file survives, uncaptured"
problems=()

if resume_step3 "the resume discard's un-ignored run state"; then
  capture_at="$(awk -v s="$enter_at" -v e="$item_end" 'NR >= s && NR <= e && /="\$\(git status --porcelain\)"/ { print NR; exit }' "$md")"
  if [[ -z "$capture_at" ]]; then
    problems+=("$skill_md's preflight step 3 (lines $enter_at-$item_end) has no line capturing git status --porcelain, so its discard block could not be found")
  else
    discard="$(awk -v c="$capture_at" '
      NR < c && /^[[:space:]]*```/ { body = ""; next }
      NR < c { body = body $0 "\n"; next }
      /^[[:space:]]*```/ { printf "%s", body; exit }
      { body = body $0 "\n" }' "$md")"
    dir="$(scratch_dir)"
    new_repo -b main "$dir/wt" >/dev/null 2>&1
    printf '%s\n' '.tdd/*' '!.tdd/issue-*.md' '.tdd/issue-*-spec.md' > "$dir/wt/.gitignore"
    mkdir -p "$dir/wt/.tdd"
    echo "- [x] step one" > "$dir/wt/.tdd/issue-1.md"
    git -C "$dir/wt" add -A >/dev/null 2>&1
    git -C "$dir/wt" commit -q -m "initial" >/dev/null 2>&1
    echo "a refactor the run owes" > "$dir/wt/.tdd/issue-1-refactor-owed.md"
    (cd "$dir/wt" && STRAY_OUT="$dir/stray.out" bash -c "$discard"$'\nprintf \'%s\\n\' "$stray" > "$STRAY_OUT"') >/dev/null 2>&1
    [[ -f "$dir/wt/.tdd/issue-1-refactor-owed.md" ]] ||
      problems+=("preflight step 3's discard block removed the untracked run-state file .tdd/issue-1-refactor-owed.md: want it kept, got .tdd/ holding: $(ls -A "$dir/wt/.tdd" 2>&1 | tr '\n' ' ')")
    if grep -F -- 'issue-1-refactor-owed.md' "$dir/stray.out" > /dev/null 2>&1; then
      problems+=("\$stray after preflight step 3's discard block captures the run-state file .tdd/issue-1-refactor-owed.md as a stray: want it absent, got: $(cat "$dir/stray.out")")
    fi
  fi
fi

report "$name"

finish
