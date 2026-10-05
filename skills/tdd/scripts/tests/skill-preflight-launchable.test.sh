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
worktree_call='issue-worktree.sh'
enter_call='cd "$wt"'
plan_heading='### 2. Scope & plan'
red_phrase='red baseline'
callers="caller's checkout"


source "$HERE/lib/harness.sh"
source "$HERE/lib/section-end.sh"

sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
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
  plan_at="$(awk -v h="$plan_heading" 'index($0, h) == 1 { print NR; exit }' "$md")"
  if [[ -z "$fast_in" ]]; then
    problems+=("$skill_md's '$preflight' section never names $fast_call, so the item that stops on a red baseline could not be read")
  else
    [[ -n "$plan_at" && "$fast_in" -lt "$plan_at" ]] ||
      problems+=("$skill_md:$fast_in runs the baseline after '$plan_heading' (line ${plan_at:-none}), so a red baseline cannot stop the run before the plan")
    stops="$(item_around "$fast_in" | tr '\n' ' ' | sed 's/  */ /g' | awk 'BEGIN { RS = "[.] " } tolower($0) ~ /red baseline/')"
    if ! grep -iF -- "preflight" <<< "$stops" | grep -F -- "$callers" > /dev/null; then
      problems+=("$skill_md:$fast_in's item has no sentence that stops on a $red_phrase as a preflight-class stop whatever the $callers holds — it says only: ${stops:-nothing}")
    fi
  fi
fi

report "$name"

finish
