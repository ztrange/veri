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

item_around() {
  local at="$1" start end next
  start="$(awk -v s="$sec_start" -v at="$at" 'NR >= s && NR <= at && /^[0-9]+\./ { n = NR } END { print n + 0 }' "$md")"
  [[ "$start" -gt 0 ]] || start="$sec_start"
  next="$(awk -v s="$((at + 1))" -v e="$sec_end" 'NR >= s && NR <= e && /^[0-9]+\./ { print NR; exit }' "$md")"
  if [[ -n "$next" ]]; then end=$((next - 1)); else end="$sec_end"; fi
  sed -n "${start},${end}p" "$md"
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

name="$skill_md's preflight runs $launchable before the baseline suite"
problems=()

if preflight_or_problem "a launchability check"; then
  launch_at="$(call_at "$launchable")"
  baseline_at="$(call_at "$detector")"
  [[ -n "$launch_at" ]] ||
    problems+=("$skill_md's '$preflight' section never names $launchable, so a run performs no launchability check and still dies at its first leaf")
  if [[ -z "$baseline_at" ]]; then
    problems+=("$skill_md's '$preflight' section has no item naming $detector, so which check runs the baseline — the one a launchability check has to precede — could not be read")
  elif [[ -n "$launch_at" ]] && [[ "$launch_at" -gt "$baseline_at" ]]; then
    problems+=("$skill_md:$launch_at calls $launchable after the baseline's $detector call at line $baseline_at, so a run that cannot launch a leaf still pays the whole baseline suite first")
  fi
fi

report "$name"

name="$skill_md's preflight refuses to start on a bad $growth"
problems=()

if preflight_or_problem "a $growth check"; then
  growth_at="$(call_at "$growth")"
  if [[ -z "$growth_at" ]]; then
    problems+=("$skill_md's '$preflight' section never names $growth, so a run whose plan-growth budget cannot be read starts anyway and only finds out when a leaf first tries to grow the plan")
  elif ! grep -qiE "$refusal" < <(item_around "$growth_at"); then
    problems+=("$skill_md:$growth_at names $growth in a preflight item that spells no exit 2, so the document mentions the budget without refusing a run that cannot read it — the way item 5 refuses a bad VERI_REFACTOR_BUDGET")
  fi
fi

report "$name"

name="$skill_md's preflight calls $step_budget beside $refactor_budget and stops on its exit 2"
problems=()

if preflight_or_problem "a $step_budget check"; then
  sb_at="$(call_at "$step_budget")"
  if [[ -z "$sb_at" ]]; then
    problems+=("$skill_md's '$preflight' section never names $step_budget, so a run whose step or run budget cannot be read starts anyway and launches leaves it cannot price")
  else
    grep -F -- "$refactor_budget" > /dev/null < <(item_around "$sb_at") ||
      problems+=("$skill_md:$sb_at calls $step_budget outside the preflight item that runs $refactor_budget")
    grep -iE "$refusal" > /dev/null < <(paragraph_around "$sb_at") ||
      problems+=("$skill_md:$sb_at calls $step_budget in a paragraph that spells no exit 2, so nothing says a budget it cannot read stops the run before a leaf launches")
  fi
fi

report "$name"

name="$skill_md's preflight checks GitHub with $gh_check and stops the run on its non-zero exit (#864)"
problems=()

if preflight_or_problem "the GitHub check"; then
  auth_at="$(call_at "$claude_auth")"
  if [[ -z "$auth_at" ]]; then
    problems+=("$skill_md's '$preflight' section never names $claude_auth, so the item that checks authentication — the one the GitHub check belongs in — could not be read")
  elif ! grep -F -- "$gh_check" > /dev/null < <(item_around "$auth_at"); then
    problems+=("$skill_md:$auth_at checks $claude_auth in a preflight item that never names $gh_check, so GitHub is checked by a call other than the REST one every other GitHub read uses")
  else
    gh_at="$(call_at "$gh_check")"
    para="$(paragraph_around "$gh_at")"
    grep -iF -- "$nonzero" > /dev/null <<< "$para" && grep -iF -- "preflight" > /dev/null <<< "$para" ||
      problems+=("$skill_md:$gh_at names $gh_check in a paragraph that does not say its $nonzero exit stops the run as a preflight failure, so a conductor can carry on past a failed GitHub check")
  fi
fi

report "$name"

name="$skill_md runs the fast-tier baseline inside the issue's worktree, after $worktree_call cut the branch (#955)"
problems=()

enter_at="$(awk -v w="$worktree_call" -v c="$enter_call" 'index($0, w) && index($0, c) { print NR; exit }' "$md")"
fast_at="$(awk -v f="$fast_call" 'index($0, f) { print NR; exit }' "$md")"

if [[ -z "$enter_at" ]]; then
  problems+=("$skill_md has no line that runs $worktree_call and then $enter_call, so where the run enters the issue's worktree could not be read")
elif [[ -z "$fast_at" ]]; then
  problems+=("$skill_md never names $fast_call, so no baseline suite runs at all")
elif [[ "$fast_at" -lt "$enter_at" ]]; then
  problems+=("$skill_md:$fast_at runs the baseline ($fast_call) before line $enter_at enters the worktree $worktree_call cuts from origin/<default>, so the baseline proves the caller's checkout, not the commit the branch is cut from")
fi

report "$name"

name="$skill_md stops the run on a red baseline in the worktree as a preflight failure, whatever state the caller's checkout is in (#955)"
problems=()

if preflight_or_problem "the red-baseline stop"; then
  fast_in="$(call_at "$fast_call")"
  plan_at="$(heading_at "$plan_heading")"
  if [[ -z "$fast_in" ]]; then
    problems+=("$skill_md's '$preflight' section never names $fast_call, so the item that stops on a red baseline could not be read")
  else
    [[ -n "$plan_at" && "$fast_in" -lt "$plan_at" ]] ||
      problems+=("$skill_md:$fast_in runs the baseline after '$plan_heading' (line ${plan_at:-none}), so a red baseline cannot stop the run before the plan")
    stops="$(item_around "$fast_in" | tr '\n' ' ' | sed 's/  */ /g' | awk -v p="$red_phrase" 'BEGIN { RS = "[.] " } index(tolower($0), p)')"
    if ! grep -iF -- "preflight" <<< "$stops" | grep -F -- "$callers" > /dev/null; then
      problems+=("$skill_md:$fast_in's item has no sentence that stops on a $red_phrase as a preflight-class stop whatever the $callers holds — it says only: ${stops:-nothing}")
    fi
  fi
fi

report "$name"

name="$skill_md takes the full-tier measurement in the worktree, on the fast-tier baseline's commit, and sizes $timeout_call $timeout_flag only after it (#955)"
problems=()

if preflight_or_problem "the full-tier measurement"; then
  fast_in="$(call_at "$fast_call")"
  full_in="$(call_at "$full_call")"
  timeout_in="$(awk -v s="$sec_start" -v e="$sec_end" -v t="$timeout_call" -v f="$timeout_flag" \
    'NR >= s && NR <= e && index($0, t) && index($0, f) { print NR; exit }' "$md")"
  if [[ -z "$fast_in" || -z "$full_in" ]]; then
    problems+=("$skill_md's '$preflight' section does not name both $fast_call (${fast_in:-none}) and $full_call (${full_in:-none}), so where the full tier is measured could not be read")
  elif [[ "$full_in" -lt "$fast_in" ]]; then
    problems+=("$skill_md:$full_in measures the full tier ($full_call) before line $fast_in runs the fast-tier baseline in the worktree, so it times a different tree than the leaves run on")
  else
    moves="$(sed -n "${fast_in},${full_in}p" "$md" | grep -nE '(^|[^[:alnum:]_-])cd |git (checkout|switch|pull|fetch|reset|rebase)|issue-worktree\.sh')"
    [[ -z "$moves" ]] ||
      problems+=("$skill_md between line $fast_in ($fast_call) and line $full_in ($full_call) leaves the worktree or moves its commit: $moves")
  fi
  if [[ -z "$timeout_in" ]]; then
    problems+=("$skill_md's '$preflight' section has no $timeout_call call with $timeout_flag, so what sizes the timeout could not be read")
  elif [[ -n "$full_in" && "$timeout_in" -lt "$full_in" ]]; then
    problems+=("$skill_md:$timeout_in sizes the timeout ($timeout_call $timeout_flag) before line $full_in takes the full-tier measurement it is sized from")
  fi
fi

report "$name"

name="$skill_md says a resumed run's baseline runs on the $branch_head in its existing worktree, before any cycle (#955)"
problems=()

if section "$resume_heading"; then
  says="$(sed -n "${sec_start},${sec_end}p" "$md" | tr '\n' ' ' | sed 's/  */ /g' |
    awk -v b="baseline" -v h="$branch_head" 'BEGIN { RS = "[.] " } { l = tolower($0) } index(l, b) && index(l, h) && index(l, "worktree") && index(l, "cycle")')"
  [[ -n "$says" ]] ||
    problems+=("$skill_md's '$resume_heading' section has no sentence saying the baseline runs on the $branch_head in its existing worktree before any cycle of the resumed run")
else
  problems+=("$skill_md has no '$resume_heading' section — where a resumed run's baseline is stated could not be read")
fi

report "$name"

name="$skill_md takes the worktree's .tdd/conductor.pid lock in preflight step 3, after $enter_call and before the fast-tier baseline (#987)"
problems=()

enter_at="$(awk -v w="$worktree_call" -v c="$enter_call" 'index($0, w) && index($0, c) { print NR; exit }' "$md")"
pid_at="$(awk -v w="$pid_write" -v v="$pid_value" 'index($0, w) && index($0, v) { print NR; exit }' "$md")"

if [[ -z "$enter_at" ]]; then
  problems+=("$skill_md has no line that runs $worktree_call and then $enter_call, so where the run enters the issue's worktree could not be read")
elif [[ -z "$pid_at" ]]; then
  problems+=("$skill_md has no line writing $pid_value $pid_write, so nothing locks the issue's worktree against a second conductor")
else
  base_at="$(awk -v s="$((enter_at + 1))" -v f="$fast_call" -v d="$detach_start" \
    'NR >= s && (index($0, f) || index($0, d)) { print NR; exit }' "$md")"
  if [[ -z "$base_at" ]]; then
    problems+=("$skill_md names neither $fast_call nor $detach_start after line $enter_at enters the worktree, so where the baseline starts could not be read")
  elif [[ "$pid_at" -lt "$enter_at" ]]; then
    problems+=("$skill_md:$pid_at writes $pid_write before line $enter_at enters the worktree, so the lock lands in the caller's checkout")
  elif [[ "$pid_at" -gt "$base_at" ]]; then
    problems+=("$skill_md:$pid_at writes $pid_write after line $base_at starts the fast-tier baseline, so for the whole baseline issue-worktree.sh hands the worktree to a second conductor")
  fi
fi

report "$name"

finish
