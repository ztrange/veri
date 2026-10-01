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
preflight='### 0. Preflight'


source "$HERE/lib/harness.sh"

sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  local next
  next="$(head -1 < <(tail -n "+$((sec_start + 1))" "$md" | grep -nE '^#') | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    sec_end=$((sec_start + next - 1))
  else
    sec_end=$(($(wc -l < "$md")))
  fi
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

finish
